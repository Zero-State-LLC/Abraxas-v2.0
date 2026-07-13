from __future__ import annotations

import importlib
import importlib.util
import inspect
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


def _artifact_name(relative_path: str) -> str:
    return Path(relative_path).stem.removeprefix("run_")


def _import_core_module(artifact_name: str) -> ModuleType:
    candidates = (
        f"core.{artifact_name}",
        f"core.ingest.{artifact_name}",
        f"core.sync.{artifact_name}",
    )
    errors: list[str] = []
    for module_name in candidates:
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            errors.append(f"{module_name}: {exc}")
    raise ImportError(
        f"Unable to resolve missing script runner for {artifact_name}; tried "
        + ", ".join(candidates)
        + ". Errors: "
        + " | ".join(errors)
    )


def _select_function(
    module: ModuleType,
    *,
    prefix: str,
    artifact_name: str,
    suffix: str = "",
) -> Callable[..., Any] | None:
    exact_name = f"{prefix}{artifact_name}{suffix}"
    exact = getattr(module, exact_name, None)
    if callable(exact):
        return exact

    matches: list[Callable[..., Any]] = []
    for name, value in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith(prefix):
            continue
        if name == "write_canonical_json":
            continue
        if suffix and not name.endswith(suffix):
            continue
        if artifact_name in name:
            matches.append(value)
    if matches:
        return sorted(matches, key=lambda fn: fn.__name__)[0]

    for name, value in inspect.getmembers(module, inspect.isfunction):
        if name.startswith(prefix) and name != "write_canonical_json":
            if not suffix or name.endswith(suffix):
                return value
    return None


def _call_builder(builder: Callable[..., dict[str, Any]], repo_root: str | Path) -> dict[str, Any]:
    signature = inspect.signature(builder)
    kwargs: dict[str, Any] = {}
    if "repo_root" in signature.parameters:
        kwargs["repo_root"] = repo_root
    if "source_root" in signature.parameters:
        kwargs["source_root"] = repo_root
    return builder(**kwargs)


def _call_writer_with_roots(
    writer: Callable[..., dict[str, Any]],
    *,
    repo_root: str | Path,
    out_root: str | Path | None,
) -> dict[str, Any]:
    signature = inspect.signature(writer)
    kwargs: dict[str, Any] = {}
    if "out_root" in signature.parameters:
        kwargs["out_root"] = out_root
    if "repo_root" in signature.parameters:
        kwargs["repo_root"] = repo_root
        return writer(**kwargs)
    if "source_root" in signature.parameters:
        kwargs["source_root"] = repo_root
        return writer(**kwargs)
    return writer(repo_root, **kwargs)


def _default_out_path(module: ModuleType, name: str, fallback: Path) -> Path:
    value = getattr(module, name, None)
    if value is None:
        return fallback
    return Path(value)


def _synthesized_runner(relative_path: str) -> ModuleType:
    artifact_name = _artifact_name(relative_path)
    core_module = _import_core_module(artifact_name)
    builder = _select_function(core_module, prefix="build_", artifact_name=artifact_name)
    writer = _select_function(core_module, prefix="write_", artifact_name=artifact_name)
    markdown_writer = _select_function(
        core_module,
        prefix="write_",
        artifact_name=artifact_name,
        suffix="_markdown",
    )
    if writer is None and builder is None:
        raise ImportError(f"No build_* or write_* function found in {core_module.__name__}")

    module = ModuleType(Path(relative_path).stem)

    def run(
        repo_root: str | Path = ".",
        *,
        out_root: str | Path | None = None,
        out_json: str | Path | None = None,
        out_md: str | Path | None = None,
    ) -> dict[str, Any]:
        if writer is not None:
            writer_signature = inspect.signature(writer)
            writer_params = list(writer_signature.parameters)
            if "out_root" in writer_signature.parameters:
                return _call_writer_with_roots(writer, repo_root=repo_root, out_root=out_root)
            if set(("json_path", "md_path")).issubset(writer_signature.parameters):
                json_path = Path(out_json) if out_json is not None else _default_out_path(
                    core_module,
                    "OUT_JSON",
                    Path("out") / f"{artifact_name}.json",
                )
                md_path = Path(out_md) if out_md is not None else json_path.with_suffix(".md")
                return writer(json_path, md_path)
            if len(writer_params) >= 2 and writer_params[1] not in {"packet", "value"}:
                json_path = Path(out_json) if out_json is not None else _default_out_path(
                    core_module,
                    "OUT_JSON",
                    Path("out") / f"{artifact_name}.json",
                )
                md_path = Path(out_md) if out_md is not None else json_path.with_suffix(".md")
                return writer(json_path, md_path)

        if builder is None or writer is None:
            raise ImportError(f"Cannot synthesize path-based runner for {core_module.__name__}")

        packet = _call_builder(builder, repo_root)
        json_path = Path(out_json) if out_json is not None else _default_out_path(
            core_module,
            "OUT_JSON",
            Path("out") / f"{artifact_name}.json",
        )
        md_path = Path(out_md) if out_md is not None else json_path.with_suffix(".md")
        writer(json_path, packet)
        if markdown_writer is not None:
            markdown_writer(md_path, packet)
        return packet

    def main() -> int:
        packet = run()
        for key in ("status", "plan_status", "receipt_status", "recommended_next_patch"):
            if key in packet:
                print(packet[key])
        return 0

    module.run = run  # type: ignore[attr-defined]
    module.main = main  # type: ignore[attr-defined]
    module.__dict__["CORE_MODULE"] = core_module.__name__
    return module


def load_script_runner(repo_root: Path, relative_path: str, module_name: str) -> ModuleType:
    runner_path = repo_root / relative_path
    if not runner_path.exists():
        return _synthesized_runner(relative_path)
    spec = importlib.util.spec_from_file_location(module_name, runner_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load script runner from {runner_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
