#!/usr/bin/env python3
"""WP-G: emit Neon Genie allowlist + run fail-closed capability probes (advisory)."""

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

from core.production_readiness.neon_genie_allowlist import (  # noqa: E402
    build_allowlist_check_report,
    check_capability,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print the report summary without rewriting tracked report files (fast CI)",
    )
    args = parser.parse_args(argv)
    report = build_allowlist_check_report(REPO_ROOT, write=not args.no_write)
    # Smoke: denied production activation
    assert check_capability("production.activate")["status"] == "DENIED"
    assert check_capability("venture_cycle.intake")["status"] == "ALLOWED"
    print(
        json.dumps(
            {
                "allowlist_id": report.get("allowlist_id"),
                "summary": report.get("summary"),
                "output_dir": "out/production_readiness/ws5/",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
