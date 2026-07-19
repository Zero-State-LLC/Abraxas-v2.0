#!/usr/bin/env python3
"""Emit WP-D consolidation receipt."""

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

from core.production_readiness.wp_d_receipt import build_wp_d_receipt  # noqa: E402


def main() -> int:
    receipt = build_wp_d_receipt(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "work_package": receipt.get("work_package"),
                "metrics": receipt.get("metrics"),
                "modules_still_writing": receipt["metrics"]["modules_still_writing"],
                "output": "out/production_readiness/ws2/wp_d_consolidation_receipt.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if receipt["metrics"]["modules_still_writing"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
