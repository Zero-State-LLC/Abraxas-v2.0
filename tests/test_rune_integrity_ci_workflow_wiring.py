from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.rune_integrity_ci_workflow_wiring import (
    BRIER_SCORE,
    DEFAULT_OUT_PATH,
    STATUS,
    build_rune_integrity_ci_workflow_wiring_receipt,
)
from scripts.operator.run_rune_integrity_ci_workflow_wiring_receipt import run


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_rune_integrity_ci_workflow_wiring_preserves_authority_locks() -> None:
    packet = build_rune_integrity_ci_workflow_wiring_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == BRIER_SCORE
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["workflow_wiring_posture"]["blocking_ci_enforcement"] is False
    assert packet["workflow_wiring_posture"]["workflow_mutation"] is False


def test_rune_integrity_ci_workflow_wiring_hash_is_canonical() -> None:
    packet = build_rune_integrity_ci_workflow_wiring_receipt(repo_root=REPO_ROOT)
    without_hash = {
        key: value for key, value in packet.items() if key != "canonical_hash"
    }

    assert packet["canonical_hash"] == canonical_hash(without_hash)


def test_rune_integrity_ci_workflow_wiring_records_report_only_step() -> None:
    packet = build_rune_integrity_ci_workflow_wiring_receipt(repo_root=REPO_ROOT)

    assert packet["workflow_wiring_posture"]["status"] == "WIRED_ADVISORY_ONLY"
    assert packet["workflow_wiring_posture"]["report_only_step_present"] is True
    assert packet["workflow_wiring_posture"]["runner_wired"] is True
    assert packet["workflow_wiring_posture"]["continue_on_error"] is True


def test_rune_integrity_ci_workflow_wiring_missing_sources_fail_closed(tmp_path: Path) -> None:
    packet = build_rune_integrity_ci_workflow_wiring_receipt(repo_root=tmp_path)

    assert packet["source_status"] == "NOT_COMPUTABLE"
    assert packet["workflow_wiring_posture"]["status"] == "NOT_COMPUTABLE"
    assert packet["scanner_receipt_status"] == "MISSING"
    assert all(value is False for value in packet["authority_locks"].values())


def test_rune_integrity_ci_workflow_wiring_runner_writes_receipt(tmp_path: Path) -> None:
    out_path = tmp_path / "receipt.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=out_path)
    written = json.loads(out_path.read_text(encoding="utf-8"))

    assert out_path.exists()
    assert written == packet
    assert written["status"] == STATUS
    assert written["canonical_hash"] == packet["canonical_hash"]
    assert DEFAULT_OUT_PATH.endswith(".latest.json")
