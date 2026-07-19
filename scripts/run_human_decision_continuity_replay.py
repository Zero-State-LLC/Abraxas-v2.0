#!/usr/bin/env python3
"""Ensure human decision continuity packet exists via sole-writer."""

from __future__ import annotations

from pathlib import Path

from core.canonical.json import write_canonical_json
from core.human_decision_continuity.runtime import run_human_decision_continuity


if __name__ == "__main__":
    if not Path("out/human_decision_continuity/latest.json").exists():
        packet = run_human_decision_continuity([], [], [], [])
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
