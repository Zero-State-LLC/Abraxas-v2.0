#!/usr/bin/env python3
"""Check production readiness documentation crosslinks; emit receipts."""

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

from core.production_readiness.docs_crosslink_check import (  # noqa: E402
    build_docs_crosslink_check,
)


def main() -> int:
    report = build_docs_crosslink_check(REPO_ROOT, write=True)
    summary = report.get("summary") or {}
    print(
        json.dumps(
            {
                "summary": summary,
                "broken_links": report.get("broken_links"),
                "output": "out/production_readiness/ws8/docs_crosslink_check.v1.json",
                "receipt": (
                    "out/production_readiness/ws8/"
                    "documentation_overhaul_receipt.v1.json"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if summary.get("all_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
