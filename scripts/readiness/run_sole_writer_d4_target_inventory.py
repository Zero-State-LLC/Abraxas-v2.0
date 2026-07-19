#!/usr/bin/env python3
"""WP-D4-prep: emit sole-writer D4 target inventory (no rewrites)."""

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

from core.production_readiness.sole_writer_d4_target_inventory import (  # noqa: E402
    build_sole_writer_d4_target_inventory,
)


def main() -> int:
    inv = build_sole_writer_d4_target_inventory(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "finding_count": inv.get("finding_count"),
                "cluster_count": len(inv.get("clusters") or []),
                "implementation_executed": inv.get("implementation_executed"),
                "next_pr_suggestion": inv.get("next_pr_suggestion"),
                "output": "out/production_readiness/ws2/sole_writer_d4_target_inventory.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
