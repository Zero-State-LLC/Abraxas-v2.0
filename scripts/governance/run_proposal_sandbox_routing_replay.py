#!/usr/bin/env python3
"""Ensure routing packet exists via sole-writer, then no-op for replay helper."""

from __future__ import annotations

from pathlib import Path

from core.canonical.json import write_canonical_json
from core.proposal_sandbox_routing.runtime import run_proposal_sandbox_routing


if __name__ == "__main__":
    if not Path("out/proposal_sandbox_routing/latest.json").exists():
        packet = run_proposal_sandbox_routing([], [], [], [])
        write_canonical_json("out/proposal_sandbox_routing/latest.json", packet)
        write_canonical_json(
            "out/proposal_sandbox_routing_replay/latest.json", packet["replay"]
        )
        write_canonical_json(
            "out/proposal_sandbox_routing_lineage/latest.json", packet["lineage"]
        )
        write_canonical_json(
            "out/proposal_sandbox_routing_diagnostics/latest.json",
            packet["diagnostics"],
        )
