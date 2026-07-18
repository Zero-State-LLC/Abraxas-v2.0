#!/usr/bin/env python3
"""Advisory architecture-boundary check (prohibited imports + unregistered surfaces).

Default: always exit 0 (fail-open).
Pass --fail-closed to exit 1 when findings exist (not wired into fast CI yet).
"""

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

from core.production_readiness.boundary_check import (  # noqa: E402
    build_boundary_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-closed",
        action="store_true",
        help="Exit non-zero when findings exist (default: advisory / exit 0)",
    )
    args = parser.parse_args()

    report, exit_code = build_boundary_report(
        REPO_ROOT,
        write=True,
        fail_closed=args.fail_closed,
    )
    summary = report.get("summary", {})
    print(
        json.dumps(
            {
                "mode": report.get("mode"),
                "repository_sha": report.get("repository_sha"),
                "finding_count": summary.get("finding_count"),
                "sensitive_import_findings": summary.get("sensitive_import_findings"),
                "unregistered_surface_findings": summary.get(
                    "unregistered_surface_findings"
                ),
                "output": "out/production_readiness/ws1/boundary_advisory_report.v1.json",
                "exit_code": exit_code,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
