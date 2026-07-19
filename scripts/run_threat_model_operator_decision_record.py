#!/usr/bin/env python3
"""WP-P+: emit threat model operator decision record (explicit decision only)."""

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

from core.production_readiness.threat_model_operator_decision_record import (  # noqa: E402
    ALLOWED_CODES,
    build_threat_model_operator_decision_record,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--decision-code",
        required=True,
        choices=sorted(ALLOWED_CODES),
        help="Operator decision (required; never defaulted).",
    )
    parser.add_argument(
        "--operator",
        required=True,
        help="Operator id or role for the audit trail.",
    )
    parser.add_argument(
        "--notes",
        required=True,
        help="Human notes explaining the decision.",
    )
    parser.add_argument(
        "--residuals",
        default="RR-01,RR-02,RR-03,RR-04,RR-05",
        help="Comma-separated residual risk IDs acknowledged.",
    )
    args = parser.parse_args()
    residuals = [r.strip() for r in args.residuals.split(",") if r.strip()]
    record = build_threat_model_operator_decision_record(
        REPO_ROOT,
        decision_code=args.decision_code,
        operator_id_or_role=args.operator,
        notes=args.notes,
        acknowledged_residual_risk_ids=residuals,
        write=True,
    )
    print(
        json.dumps(
            {
                "record_id": record.get("record_id"),
                "decision_code": record.get("decision_code"),
                "operator_review_state": record.get("operator_review_state"),
                "production_activation_authorized": record.get(
                    "production_activation_authorized"
                ),
                "readiness_state": record.get("readiness_state"),
                "output": (
                    "out/production_readiness/ws8/"
                    "threat_model_operator_decision_record.v0.json"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
