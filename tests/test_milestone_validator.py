from __future__ import annotations

from pathlib import Path

from core.spine.milestone_registry import MILESTONE_EVIDENCE_MAP, build_milestone_registry
from core.spine.milestone_validator import validate_active_milestone


def _touch(root: Path, paths: list[str]) -> None:
    for path in paths:
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(path)


def test_stale_v205_report_fails(tmp_path: Path) -> None:
    for item in MILESTONE_EVIDENCE_MAP:
        _touch(tmp_path, item["code"] + item["scripts"])
    registry = build_milestone_registry(tmp_path)
    packet = validate_active_milestone("v2.0.5-governed-adaptive-sandbox", registry)
    assert packet.status == "failed"


def test_validation_passes_on_derived_v209(tmp_path: Path) -> None:
    for item in MILESTONE_EVIDENCE_MAP:
        _touch(tmp_path, item["code"] + item["scripts"])
    registry = build_milestone_registry(tmp_path)
    packet = validate_active_milestone("v2.0.9-governed-weight-drift-simulation", registry)
    assert packet.status == "passed"


def test_partial_highest_blocks_seal(tmp_path: Path) -> None:
    for item in MILESTONE_EVIDENCE_MAP[:-1]:
        _touch(tmp_path, item["code"] + item["scripts"])
    _touch(tmp_path, MILESTONE_EVIDENCE_MAP[-1]["code"][:1])
    registry = build_milestone_registry(tmp_path)
    packet = validate_active_milestone(registry.active_milestone, registry)
    assert registry.partial_milestones
    assert packet.status == "failed" or registry.status == "partial"
