"""Phase 7 production-convergence recovery drill."""

from __future__ import annotations

import json
from pathlib import Path

from core.production_convergence.recovery_drill import run_recovery_drill

REPO = Path(__file__).resolve().parents[1]


def test_recovery_drill_analyze_persist_replay(tmp_path: Path) -> None:
    task = json.loads(
        (REPO / "fixtures/alembic/example_task.json").read_text(encoding="utf-8")
    )
    report = run_recovery_drill(
        repo_root=REPO,
        work_dir=tmp_path,
        alembic_task=task,
        run_id="unit-recovery-drill",
    )
    assert report["analyze_status"] == "OK"
    assert report["replay_status"] == "OK"
    assert report["receipt_hash_stable"] is True
    assert report["on_disk_hash_matches"] is True
    assert report["candidate_status"] == "NOT_READY"
    assert report["provider_id"] == "denied"
    assert (tmp_path / report["receipt_path"]).is_file()
