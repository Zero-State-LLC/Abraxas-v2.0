#!/usr/bin/env python3
"""TD Wave 3: emit soft CI gate acceptance."""

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

from core.production_readiness.soft_ci_gate_acceptance import (  # noqa: E402
    build_soft_ci_gate_acceptance,
)


def main() -> int:
    p = build_soft_ci_gate_acceptance(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "status": p.get("status"),
                "summary": p.get("summary"),
                "output": "out/production_readiness/ws6/soft_ci_gate_acceptance.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
