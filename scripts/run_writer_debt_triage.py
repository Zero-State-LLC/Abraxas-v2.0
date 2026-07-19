#!/usr/bin/env python3
"""Generate writer debt triage report (WP-A)."""

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

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.production_readiness.writer_debt_triage import (  # noqa: E402
    build_writer_debt_triage,
)


def main() -> int:
    report = build_writer_debt_triage(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "work_package": report.get("work_package"),
                "repository_sha": report.get("repository_sha"),
                "summary": report.get("summary"),
                "output": "out/production_readiness/ws2/writer_debt_triage.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
