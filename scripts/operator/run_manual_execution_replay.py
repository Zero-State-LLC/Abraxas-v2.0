#!/usr/bin/env python3
"""Print manual execution replay slice; ensure packet via sole-writer if missing."""

from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.manual_execution.runtime import run_manual_execution_authorization


if __name__ == "__main__":
    p = Path("out/manual_execution/latest.json")
    if not p.exists():
        packet = run_manual_execution_authorization([], [], [], [], [])
        write_canonical_json("out/manual_execution/latest.json", packet)
        write_canonical_json("out/manual_execution_replay/latest.json", packet["replay"])
        write_canonical_json(
            "out/manual_execution_lineage/latest.json", packet["lineage"]
        )
        write_canonical_json(
            "out/manual_execution_diagnostics/latest.json", packet["diagnostics"]
        )
    print(json.loads(Path("out/manual_execution_replay/latest.json").read_text()))
