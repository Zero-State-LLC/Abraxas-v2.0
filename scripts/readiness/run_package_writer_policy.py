#!/usr/bin/env python3
"""TD Wave 2: emit package writer policy."""

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

from core.production_readiness.package_writer_policy import (  # noqa: E402
    build_package_writer_policy,
)


def main() -> int:
    p = build_package_writer_policy(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "policy_id": p.get("policy_id"),
                "prefixes": [x["prefix"] for x in p.get("authorized_prefixes", [])],
                "output": "out/production_readiness/ws2/package_writer_policy.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
