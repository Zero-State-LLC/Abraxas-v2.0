#!/usr/bin/env python3
"""WP-N: emit soft CI gate audit."""

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

from core.production_readiness.soft_ci_gate_audit import (  # noqa: E402
    build_soft_ci_gate_audit,
)


def main() -> int:
    audit = build_soft_ci_gate_audit(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "work_package": audit.get("work_package"),
                "summary": audit.get("summary"),
                "output": "out/production_readiness/ws6/soft_ci_gate_audit.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
