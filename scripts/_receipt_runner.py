from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any, Callable


def _select_function(module_name: str, prefix: str) -> Callable[..., Any]:
    module = importlib.import_module(module_name)
    module_stem = module_name.rsplit(".", 1)[-1]
    candidates: list[Callable[..., Any]] = []
    for name, value in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith(prefix):
            continue
        if name == "write_canonical_json":
            continue
        if module_stem in name or name.endswith("_receipt") or name.endswith("_harness"):
            candidates.append(value)
    if not candidates:
        raise ImportError(f"No {prefix} function found in {module_name}")
    return sorted(candidates, key=lambda fn: fn.__name__)[0]


def run_receipt(
    core_module: str,
    *,
    repo_root: str | Path = ".",
    out_path: str | Path | None = None,
) -> dict[str, Any]:
    module = importlib.import_module(core_module)
    builder = _select_function(core_module, "build_")
    writer = _select_function(core_module, "write_")
    root = Path(repo_root)

    build_signature = inspect.signature(builder)
    build_kwargs: dict[str, Any] = {}
    if "repo_root" in build_signature.parameters:
        build_kwargs["repo_root"] = root
    if "source_root" in build_signature.parameters:
        build_kwargs["source_root"] = root
    packet = builder(**build_kwargs)

    target = Path(
        out_path
        if out_path is not None
        else getattr(module, "DEFAULT_OUT_PATH", Path("out") / f"{core_module.rsplit('.', 1)[-1]}.json")
    )
    writer(target, packet)
    return packet
