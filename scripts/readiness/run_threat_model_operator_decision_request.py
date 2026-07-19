#!/usr/bin/env python3
"""WP-P: emit threat model operator decision request (PENDING only)."""

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

from core.production_readiness.threat_model_operator_decision_request import (  # noqa: E402
    build_threat_model_operator_decision_request,
)


def main() -> int:
    req = build_threat_model_operator_decision_request(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "request_id": req.get("request_id"),
                "decision_status": req.get("decision_status"),
                "auto_accepted": req.get("auto_accepted"),
                "evidence_state": req.get("evidence_state"),
                "output": (
                    "out/production_readiness/ws8/"
                    "threat_model_operator_decision_request.v0.json"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
