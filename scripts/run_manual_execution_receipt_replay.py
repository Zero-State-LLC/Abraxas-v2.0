#!/usr/bin/env python3
"""Print receipt replay slice; ensure packet via sole-writer if missing."""

from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.manual_execution_receipts.runtime import run_manual_execution_receipt_ledger


if __name__ == "__main__":
    if not Path("out/manual_execution_receipts/latest.json").exists():
        packet = run_manual_execution_receipt_ledger([], [], [], [], [])
        write_canonical_json("out/manual_execution_receipts/latest.json", packet)
        write_canonical_json(
            "out/manual_execution_receipts_replay/latest.json", packet["replay"]
        )
        write_canonical_json(
            "out/manual_execution_receipts_lineage/latest.json", packet["lineage"]
        )
        write_canonical_json(
            "out/manual_execution_receipts_diagnostics/latest.json",
            packet["diagnostics"],
        )
    print(
        json.loads(Path("out/manual_execution_receipts_replay/latest.json").read_text())
    )
