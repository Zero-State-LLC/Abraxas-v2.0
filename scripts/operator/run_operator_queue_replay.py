#!/usr/bin/env python3
"""Print operator queue replay slice; fail closed if packet is missing."""

from __future__ import annotations

import json
from pathlib import Path


if __name__ == "__main__":
    replay_path = Path("out/operator_queue_replay/latest.json")
    if not replay_path.exists():
        raise FileNotFoundError(
            "required artifact missing: out/operator_queue_replay/latest.json "
            "(refuse empty-list synthetic operator queue packet)"
        )
    print(json.loads(replay_path.read_text(encoding="utf-8")))
