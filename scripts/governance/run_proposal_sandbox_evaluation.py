#!/usr/bin/env python3
"""Sole-writer for proposal sandbox evaluation packets (WP-D4-C3)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.proposal_sandbox_evaluation.runtime import run_proposal_sandbox_evaluation


if __name__ == "__main__":
    packet = run_proposal_sandbox_evaluation([], [], [], [])
    write_canonical_json("out/proposal_sandbox_evaluation/latest.json", packet)
    write_canonical_json(
        "out/proposal_sandbox_evaluation_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/proposal_sandbox_evaluation_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/proposal_sandbox_evaluation_diagnostics/latest.json",
        packet["diagnostics"],
    )
