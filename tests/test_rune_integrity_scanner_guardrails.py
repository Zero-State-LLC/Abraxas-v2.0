from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.rune_integrity_scanner_guardrails import (
    BRIER_SCORE,
    DEFAULT_OUT_PATH,
    STATUS,
    build_rune_integrity_scanner_guardrails_receipt,
)
from Scripts.run_rune_integrity_scanner_guardrails_receipt import run


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_rune_integrity_scanner_preserves_authority_locks() -> None:
    packet = build_rune_integrity_scanner_guardrails_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == BRIER_SCORE
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["blocking_ci_enforcement"] is False
    assert packet["workflow_visibility"]["blocking_ci_enforcement"] is False


def test_rune_integrity_scanner_hash_is_canonical() -> None:
    packet = build_rune_integrity_scanner_guardrails_receipt(repo_root=REPO_ROOT)
    without_hash = {
        key: value for key, value in packet.items() if key != "canonical_hash"
    }

    assert packet["canonical_hash"] == canonical_hash(without_hash)


def test_rune_integrity_scanner_records_repo_real_runes() -> None:
    packet = build_rune_integrity_scanner_guardrails_receipt(repo_root=REPO_ROOT)
    rows = {row["path"]: row for row in packet["rune_integrity_rows"]}

    assert "abraxas/v2/hygiene/runes/hyperstition_tag.py" in rows
    assert "RUNE.HYPERSTITION_TAG" in rows[
        "abraxas/v2/hygiene/runes/hyperstition_tag.py"
    ]["rune_ids"]
    assert packet["guardrail_summary"]["rune_file_count"] >= 5
    assert packet["guardrail_summary"]["enforcement_action"] == "REPORT_ONLY"
    assert packet["workflow_visibility"]["status"] == "WIRED_ADVISORY_ONLY"


def test_rune_integrity_scanner_missing_sources_fail_closed(tmp_path: Path) -> None:
    packet = build_rune_integrity_scanner_guardrails_receipt(repo_root=tmp_path)

    assert packet["source_status"] == "NOT_COMPUTABLE"
    assert packet["guardrail_summary"]["rune_file_count"] == 0
    assert packet["workflow_visibility"]["status"] == "NOT_WIRED_ADVISORY_ONLY"
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["canonical_hash"] == canonical_hash(
        {key: value for key, value in packet.items() if key != "canonical_hash"}
    )


def test_rune_integrity_scanner_runner_writes_receipt(tmp_path: Path) -> None:
    out_path = tmp_path / "receipt.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=out_path)
    written = json.loads(out_path.read_text(encoding="utf-8"))

    assert out_path.exists()
    assert written == packet
    assert written["status"] == STATUS
    assert written["canonical_hash"] == packet["canonical_hash"]
    assert DEFAULT_OUT_PATH.endswith(".latest.json")
