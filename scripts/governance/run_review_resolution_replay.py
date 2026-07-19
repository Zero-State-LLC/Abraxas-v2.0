#!/usr/bin/env python3
"""Print review resolution replay; ensure packet via sole-writer if missing."""

from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.review_resolution.runtime import run_review_resolution_spine


if __name__ == "__main__":
    p = Path("out/review_resolution/latest.json")
    if not p.exists():
        packet = run_review_resolution_spine([], [], [], [], [])
        write_canonical_json("out/review_resolution/latest.json", packet)
        write_canonical_json(
            "out/review_resolution_replay/latest.json", packet["replay"]
        )
        write_canonical_json(
            "out/review_resolution_lineage/latest.json", packet["lineage"]
        )
        write_canonical_json(
            "out/review_resolution_diagnostics/latest.json", packet["diagnostics"]
        )
    print(json.loads(p.read_text()).get("replay", {}))
