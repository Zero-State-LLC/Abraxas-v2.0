from __future__ import annotations

from pathlib import Path

from core.spine.milestone_registry import MILESTONE_EVIDENCE_MAP, build_milestone_registry


def _touch(root: Path, paths: list[str]) -> None:
    for path in paths:
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(path)


def test_artifact_only_discovery(tmp_path: Path) -> None:
    for item in MILESTONE_EVIDENCE_MAP:
        _touch(tmp_path, item["artifact"])
    registry = build_milestone_registry(tmp_path)
    assert registry.active_milestone == "v2.0.9-governed-weight-drift-simulation"


def test_code_script_discovery(tmp_path: Path) -> None:
    for item in MILESTONE_EVIDENCE_MAP:
        _touch(tmp_path, item["code"] + item["scripts"])
    registry = build_milestone_registry(tmp_path)
    assert registry.active_milestone == "v2.0.9-governed-weight-drift-simulation"
    assert registry.status == "passed"


def test_missing_older_artifacts_do_not_force_unknown_when_code_script_present(tmp_path: Path) -> None:
    for item in MILESTONE_EVIDENCE_MAP[4:]:
        _touch(tmp_path, item["code"] + item["scripts"])
    registry = build_milestone_registry(tmp_path)
    assert registry.active_milestone == "v2.0.9-governed-weight-drift-simulation"


def test_no_evidence_not_computable(tmp_path: Path) -> None:
    registry = build_milestone_registry(tmp_path)
    assert registry.status == "not_computable"
    assert registry.active_milestone == "unknown"
