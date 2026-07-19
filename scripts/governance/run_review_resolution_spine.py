#!/usr/bin/env python3
"""Sole-writer for review resolution packets (WP-D4-C4)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.review_resolution.runtime import run_review_resolution_spine


if __name__ == "__main__":
    packet = run_review_resolution_spine([], [], [], [], [])
    write_canonical_json("out/review_resolution/latest.json", packet)
    write_canonical_json("out/review_resolution_replay/latest.json", packet["replay"])
    write_canonical_json("out/review_resolution_lineage/latest.json", packet["lineage"])
    write_canonical_json(
        "out/review_resolution_diagnostics/latest.json", packet["diagnostics"]
    )
