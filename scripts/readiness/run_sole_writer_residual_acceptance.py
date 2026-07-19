#!/usr/bin/env python3
"""WP-Q: emit sole-writer residual acceptance record."""

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

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.production_readiness.sole_writer_residual_acceptance import (  # noqa: E402
    build_sole_writer_residual_acceptance,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator", required=True)
    parser.add_argument(
        "--decision",
        default="ACCEPT_KNOWN_RESIDUAL",
        choices=[
            "ACCEPT_KNOWN_RESIDUAL",
            "REJECT_THRESHOLD_EXCEEDED",
            "DEFER",
        ],
    )
    parser.add_argument("--notes", default="")
    args = parser.parse_args()
    packet = build_sole_writer_residual_acceptance(
        REPO_ROOT,
        operator_id_or_role=args.operator,
        decision=args.decision,
        notes=args.notes,
        write=True,
    )
    print(
        json.dumps(
            {
                "decision": packet.get("decision"),
                "acceptance_status": packet.get("acceptance_status"),
                "under_threshold": packet.get("under_threshold"),
                "gate_4_satisfied": packet.get("gate_4_satisfied"),
                "fail_closed_enabled": packet.get("fail_closed_enabled"),
                "observed_finding_count": packet.get("observed", {}).get("finding_count"),
                "output": "out/production_readiness/ws1/sole_writer_residual_acceptance.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
