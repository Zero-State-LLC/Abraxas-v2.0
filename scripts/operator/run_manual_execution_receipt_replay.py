#!/usr/bin/env python3
"""Print receipt replay slice; fail closed if packet is missing."""

from __future__ import annotations

import json
from pathlib import Path

if __name__ == "__main__":
    replay_path = Path("out/manual_execution_receipts_replay/latest.json")
    if not replay_path.exists():
        raise FileNotFoundError(
            "required artifact missing: "
            "out/manual_execution_receipts_replay/latest.json "
            "(refuse empty-list synthetic receipt packet)"
        )
    print(json.loads(replay_path.read_text(encoding="utf-8")))
