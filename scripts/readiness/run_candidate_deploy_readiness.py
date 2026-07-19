#!/usr/bin/env python3
"""WP-DEPLOY: emit candidate deploy readiness packet (default NO_GO)."""

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

from core.production_readiness.candidate_deploy_readiness import (  # noqa: E402
    build_candidate_deploy_readiness,
)


def main() -> int:
    packet = build_candidate_deploy_readiness(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "go_no_go": packet.get("go_no_go"),
                "deploy_authorized": packet.get("deploy_authorized"),
                "production_activation_authorized": packet.get(
                    "production_activation_authorized"
                ),
                "summary": packet.get("summary"),
                "blocked_reasons": packet.get("blocked_reasons"),
                "output": "out/production_readiness/ws8/candidate_deploy_readiness.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
