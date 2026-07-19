#!/usr/bin/env python3
"""WP-O: emit recovery drill v0 (dry-run, no worktree mutation)."""

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

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.production_readiness.recovery_drill import build_recovery_drill_v0  # noqa: E402


def main() -> int:
    drill = build_recovery_drill_v0(REPO_ROOT, write=True)
    summary = drill.get("summary", {})
    print(
        json.dumps(
            {
                "work_package": drill.get("work_package"),
                "summary": summary,
                "output": "out/production_readiness/ws8/recovery_drill.v0.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if summary.get("all_critical_restorable") else 1


if __name__ == "__main__":
    raise SystemExit(main())
