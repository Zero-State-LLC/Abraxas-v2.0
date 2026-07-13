from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.temporal_continuity_authorization_source_status_audit_receipt import (
    DEFAULT_OUT_PATH,
    STATUS,
    build_temporal_continuity_authorization_source_status_audit_receipt,
)
from scripts.temporal import run_temporal_continuity_authorization_source_status_audit_receipt


def test_slice50_receipt_wraps_existing_p81_source_status() -> None:
    packet = build_temporal_continuity_authorization_source_status_audit_receipt()
    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["source_chain_summary"]["source_chain_status"] in {
        "NOT_COMPUTABLE",
        "SOURCE_CHAIN_BLOCKED",
        "SOURCE_CHAIN_READY_FOR_P80_REGENERATION",
        "SOURCE_CHAIN_READY_FOR_P81_TEMPLATE",
    }


def test_slice50_authority_locks_are_false() -> None:
    packet = build_temporal_continuity_authorization_source_status_audit_receipt()
    assert packet["authority_locks"]
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False


def test_slice50_canonical_hash_is_stable() -> None:
    first = build_temporal_continuity_authorization_source_status_audit_receipt()
    second = build_temporal_continuity_authorization_source_status_audit_receipt()
    assert first["canonical_hash"] == second["canonical_hash"]
    without_hash = dict(first)
    without_hash.pop("canonical_hash")
    assert first["canonical_hash"] == canonical_hash(without_hash)


def test_slice50_runner_writes_receipt(tmp_path: Path) -> None:
    out_path = tmp_path / "slice50.latest.json"
    packet = run_temporal_continuity_authorization_source_status_audit_receipt.run(
        out_path=out_path
    )
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written == packet
    assert written["status"] == STATUS


def test_slice50_default_out_path_is_audit_receipt() -> None:
    assert DEFAULT_OUT_PATH == (
        "out/audit/temporal_continuity_authorization_source_status_audit_001.latest.json"
    )
