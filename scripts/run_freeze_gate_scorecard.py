#!/usr/bin/env python3
"""WP-GATE: emit freeze gate scorecard."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPT_DIR_KEY = _SCRIPT_DIR.casefold()
sys.path = [
    path
    for path in sys.path
    if os.path.abspath(path or os.curdir).casefold() != _SCRIPT_DIR_KEY
]

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.production_readiness.freeze_gate_scorecard import (  # noqa: E402
    build_freeze_gate_scorecard,
)


def main() -> int:
    card = build_freeze_gate_scorecard(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "summary": card.get("summary"),
                "recommended_release_code": card.get("recommended_release_code"),
                "gates": [
                    {"id": g["gate_id"], "status": g["status"], "name": g["name"]}
                    for g in card.get("gates", [])
                ],
                "output": "out/production_readiness/ws8/freeze_gate_scorecard.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
