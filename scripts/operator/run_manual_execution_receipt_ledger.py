#!/usr/bin/env python3
"""Sole-writer for manual execution receipt ledger packets (WP-D4-C1)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.governance.upstream_evidence import load_required_upstream_packet
from core.manual_execution_receipts.runtime import run_manual_execution_receipt_ledger

if __name__ == "__main__":
    manual = load_required_upstream_packet("out/manual_execution/latest.json")
    manual_packet = manual[0]
    authorization = manual_packet.get("authorization")
    acknowledgement = manual_packet.get("acknowledgement")
    rollback = manual_packet.get("rollback")
    if not isinstance(authorization, dict) or not authorization:
        raise ValueError(
            "manual_execution_receipt_ledger: missing authorization on "
            "out/manual_execution/latest.json; refuse synthetic receipt"
        )
    if not isinstance(acknowledgement, dict) or not acknowledgement:
        raise ValueError(
            "manual_execution_receipt_ledger: missing acknowledgement on "
            "out/manual_execution/latest.json; refuse synthetic receipt"
        )
    if not isinstance(rollback, dict) or not rollback:
        raise ValueError(
            "manual_execution_receipt_ledger: missing rollback on "
            "out/manual_execution/latest.json; refuse synthetic receipt"
        )
    packet = run_manual_execution_receipt_ledger(
        manual,
        [authorization],
        [acknowledgement],
        load_required_upstream_packet("out/manual_execution_replay/latest.json"),
        [rollback],
    )
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
