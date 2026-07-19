#!/usr/bin/env python3
"""Sole-writer for proposal sandbox routing packets (WP-D4-C3)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.proposal_sandbox_routing.runtime import run_proposal_sandbox_routing


if __name__ == "__main__":
    packet = run_proposal_sandbox_routing([], [], [], [])
    write_canonical_json("out/proposal_sandbox_routing/latest.json", packet)
    write_canonical_json(
        "out/proposal_sandbox_routing_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/proposal_sandbox_routing_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/proposal_sandbox_routing_diagnostics/latest.json", packet["diagnostics"]
    )
