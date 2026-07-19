#!/usr/bin/env python3
"""Advisory sole-writer / write-path check for Abraxas (WS1.7).

Report-only and always exits 0 unless --fail-closed is passed.
Wired into run_fast_ci as a fail-open advisory gate.
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

from core.production_readiness.sole_writer_check import (  # noqa: E402
    build_sole_writer_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-closed",
        action="store_true",
        help="Exit 1 when findings exist (default: always 0)",
    )
    args = parser.parse_args()

    report = build_sole_writer_report(REPO_ROOT, write=True)
    count = int(report.get("finding_count", 0))
    by_pkg = report.get("by_package", {})
    print(
        json.dumps(
            {
                "finding_count": count,
                "by_package": by_pkg,
                "truncated": report.get("truncated"),
                "repository_sha": report.get("repository_sha"),
                "output": "out/production_readiness/ws1/sole_writer_advisory_report.v1.json",
                "mode": "fail_closed" if args.fail_closed else "advisory",
            },
            indent=2,
            sort_keys=True,
        )
    )
    if args.fail_closed and count > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
