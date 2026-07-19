#!/usr/bin/env python3
"""Ensure evaluation packet exists via sole-writer."""

from __future__ import annotations

from pathlib import Path

from core.canonical.json import write_canonical_json
from core.proposal_sandbox_evaluation.runtime import run_proposal_sandbox_evaluation


if __name__ == "__main__":
    if not Path("out/proposal_sandbox_evaluation/latest.json").exists():
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
