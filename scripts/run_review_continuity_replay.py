#!/usr/bin/env python3
"""Ensure review continuity packet exists via sole-writer."""

from __future__ import annotations

from pathlib import Path

from core.canonical.json import write_canonical_json
from core.review_continuity.runtime import run_review_continuity_ledger


if __name__ == "__main__":
    if not Path("out/review_continuity/latest.json").exists():
        packet = run_review_continuity_ledger([], [], [], [], [])
        write_canonical_json("out/review_continuity/latest.json", packet)
        write_canonical_json(
            "out/review_continuity_replay/latest.json", packet["replay"]
        )
        write_canonical_json(
            "out/review_continuity_lineage/latest.json", packet["lineage"]
        )
        write_canonical_json(
            "out/review_continuity_diagnostics/latest.json", packet["diagnostics"]
        )
