#!/usr/bin/env python3
"""Sole-writer for manual execution receipt ledger packets (WP-D4-C1)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.manual_execution_receipts.runtime import run_manual_execution_receipt_ledger


if __name__ == "__main__":
    packet = run_manual_execution_receipt_ledger([], [], [], [], [])
    write_canonical_json("out/manual_execution_receipts/latest.json", packet)
    write_canonical_json(
        "out/manual_execution_receipts_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/manual_execution_receipts_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/manual_execution_receipts_diagnostics/latest.json", packet["diagnostics"]
    )
