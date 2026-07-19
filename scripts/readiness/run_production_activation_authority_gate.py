#!/usr/bin/env python3
"""WP-AUTH: emit production activation authority gate (fail-closed DENIED)."""

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

from core.production_readiness.production_activation_authority_gate import (  # noqa: E402
    build_production_activation_authority_gate,
)


def main() -> int:
    gate = build_production_activation_authority_gate(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "status": gate.get("status"),
                "production_activation_authorized": gate.get(
                    "production_activation_authorized"
                ),
                "fail_closed": gate.get("fail_closed"),
                "authorization_token_present": gate.get("authorization_token_present"),
                "output": (
                    "out/production_readiness/ws8/"
                    "production_activation_authority_gate.v1.json"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    # Non-zero if somehow authorized (should not happen)
    return 0 if gate.get("status") == "DENIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
