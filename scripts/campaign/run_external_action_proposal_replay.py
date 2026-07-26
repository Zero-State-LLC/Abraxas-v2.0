#!/usr/bin/env python3
"""Print external action proposal replay; fail closed if packet is missing."""

from __future__ import annotations

import json
from pathlib import Path


if __name__ == "__main__":
    replay_path = Path("out/external_action_proposals_replay/latest.json")
    if not replay_path.exists():
        raise FileNotFoundError(
            "required artifact missing: "
            "out/external_action_proposals_replay/latest.json "
            "(refuse empty-list synthetic external action proposal packet)"
        )
    print(json.loads(replay_path.read_text(encoding="utf-8")))
