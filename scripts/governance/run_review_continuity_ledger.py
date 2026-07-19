#!/usr/bin/env python3
"""Sole-writer for review continuity packets (WP-D4-C4)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.review_continuity.runtime import run_review_continuity_ledger


if __name__ == "__main__":
    packet = run_review_continuity_ledger([], [], [], [], [])
    write_canonical_json("out/review_continuity/latest.json", packet)
    write_canonical_json("out/review_continuity_replay/latest.json", packet["replay"])
    write_canonical_json("out/review_continuity_lineage/latest.json", packet["lineage"])
    write_canonical_json(
        "out/review_continuity_diagnostics/latest.json", packet["diagnostics"]
    )
