"""WP-D4-C1: manual_execution runtimes are pure builders (no disk writes)."""

from __future__ import annotations

from pathlib import Path

from core.manual_execution.runtime import run_manual_execution_authorization
from core.manual_execution_receipts.runtime import run_manual_execution_receipt_ledger


REPO = Path(__file__).resolve().parents[1]


def test_manual_execution_runtime_has_no_write_canonical() -> None:
    text = (REPO / "core/manual_execution/runtime.py").read_text(encoding="utf-8")
    assert "write_canonical_json(" not in text
    assert "from core.canonical.json import" not in text
    packet = run_manual_execution_authorization([], [], [], [], [])
    assert packet["schema_version"] == "ManualExecutionRuntimePacket.v1"
    assert "authorization" in packet
    assert "replay" in packet


def test_manual_execution_receipts_runtime_has_no_write_canonical() -> None:
    text = (
        REPO / "core/manual_execution_receipts/runtime.py"
    ).read_text(encoding="utf-8")
    assert "write_canonical_json(" not in text
    assert "from core.canonical.json import" not in text
    packet = run_manual_execution_receipt_ledger([], [], [], [], [])
    assert packet["schema_version"] == "ManualExecutionReceiptRuntimePacket.v1"
    assert "ledger" in packet
    assert "replay" in packet
