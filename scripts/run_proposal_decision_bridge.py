#!/usr/bin/env python3
"""Sole-writer for proposal decision bridge packets (WP-D4-C4)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.proposal_decision_bridge.runtime import run_proposal_decision_bridge


if __name__ == "__main__":
    packet = run_proposal_decision_bridge([], [], [], [])
    write_canonical_json("out/proposal_decision_bridge/latest.json", packet)
    write_canonical_json(
        "out/proposal_decision_bridge_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/proposal_decision_bridge_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/proposal_decision_bridge_diagnostics/latest.json", packet["diagnostics"]
    )
