"""Tests for WP-O recovery drill v0."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.recovery_drill import build_recovery_drill_v0


REPO = Path(__file__).resolve().parents[1]


def test_recovery_drill_runs() -> None:
    drill = build_recovery_drill_v0(REPO, write=False)
    assert drill["schema_version"] == "recovery_drill.v0"
    assert drill["mode"] == "DRY_RUN_NO_WORKTREE_MUTATION"
    assert drill["summary"]["paths_checked"] >= 5
    # VERSION and COMPATIBILITY.md must be restorable
    by_path = {c["path"]: c for c in drill["checks"]}
    assert by_path["VERSION"]["status"] == "PASS"
    assert by_path["COMPATIBILITY.md"]["status"] == "PASS"
