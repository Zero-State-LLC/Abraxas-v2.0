#!/usr/bin/env python3
"""WP-I: emit release decision + supported surface freeze inventory."""

from __future__ import annotations

import argparse
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

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.production_readiness.release_decision import (  # noqa: E402
    ALLOWED_CODES,
    build_release_decision,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--decision-code",
        required=True,
        choices=sorted(ALLOWED_CODES),
    )
    parser.add_argument("--operator", required=True)
    parser.add_argument("--notes", required=True)
    args = parser.parse_args()
    decision = build_release_decision(
        REPO_ROOT,
        decision_code=args.decision_code,
        operator_id_or_role=args.operator,
        notes=args.notes,
        write=True,
    )
    print(
        json.dumps(
            {
                "decision_code": decision.get("decision_code"),
                "readiness_state": decision.get("readiness_state"),
                "production_activation_authorized": decision.get(
                    "production_activation_authorized"
                ),
                "scorecard_summary": decision.get("scorecard_summary"),
                "surface_summary": decision.get("surface_summary"),
                "output": "out/production_readiness/ws8/release_decision.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
