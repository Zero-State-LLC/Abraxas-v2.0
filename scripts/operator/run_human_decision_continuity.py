#!/usr/bin/env python3
"""Sole-writer for human decision continuity packets (WP-D4-C4)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.governance.upstream_evidence import load_required_upstream_packet
from core.human_decision_continuity.runtime import run_human_decision_continuity

if __name__ == "__main__":
    packet = run_human_decision_continuity(
        load_required_upstream_packet("out/human_decision_ledger/latest.json"),
        load_required_upstream_packet("out/proposal_decision_bridge/latest.json"),
        load_required_upstream_packet("out/operator_queue/latest.json"),
        load_required_upstream_packet("out/human_decision_ledger_replay/latest.json"),
    )
    write_canonical_json("out/human_decision_continuity/latest.json", packet)
    write_canonical_json(
        "out/human_decision_continuity_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/human_decision_continuity_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/human_decision_continuity_diagnostics/latest.json",
        packet["diagnostics"],
    )
