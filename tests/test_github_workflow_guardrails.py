from __future__ import annotations

from collections.abc import Iterator, Mapping
from pathlib import Path, PurePosixPath
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_ROOT = ROOT / ".github" / "workflows"
LOCAL_WORKFLOW_PREFIX = "./.github/workflows/"


def _workflow_files() -> list[Path]:
    return sorted(WORKFLOW_ROOT.rglob("*.yml")) + sorted(WORKFLOW_ROOT.rglob("*.yaml"))


def _load_workflow(path: Path) -> Mapping[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(payload, Mapping), f"{path} must contain a YAML mapping"
    return payload


def _uses_values(payload: Any) -> Iterator[str]:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if key == "uses" and isinstance(value, str):
                yield value
            else:
                yield from _uses_values(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _uses_values(item)


def _validate_local_reusable_workflow_ref(ref: str) -> None:
    if not ref.startswith(LOCAL_WORKFLOW_PREFIX):
        return

    workflow_path = PurePosixPath(ref.removeprefix("./"))
    if workflow_path.parent != PurePosixPath(".github/workflows"):
        raise AssertionError(
            "local reusable workflow references must point directly under "
            f".github/workflows: {ref}"
        )
    if workflow_path.suffix not in {".yml", ".yaml"}:
        raise AssertionError(f"local reusable workflow reference must be YAML: {ref}")
    if not (ROOT / workflow_path).is_file():
        raise AssertionError(f"local reusable workflow reference is missing: {ref}")


@pytest.mark.parametrize("path", _workflow_files(), ids=lambda path: str(path.relative_to(ROOT)))
def test_github_workflow_yaml_is_parseable(path: Path) -> None:
    _load_workflow(path)


@pytest.mark.parametrize("path", _workflow_files(), ids=lambda path: str(path.relative_to(ROOT)))
def test_local_reusable_workflow_refs_are_top_level(path: Path) -> None:
    workflow = _load_workflow(path)

    for ref in _uses_values(workflow):
        _validate_local_reusable_workflow_ref(ref)


def test_nested_local_reusable_workflow_ref_is_rejected() -> None:
    with pytest.raises(AssertionError, match="must point directly under"):
        _validate_local_reusable_workflow_ref("./.github/workflows/reusable/python-setup.yml")
