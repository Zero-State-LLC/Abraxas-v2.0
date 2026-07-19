#!/usr/bin/env python3
"""WP-D4-R: emit residual package disposition (skills/afe/core)."""

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

from core.production_readiness.residual_package_disposition import (  # noqa: E402
    build_residual_package_disposition,
)


def main() -> int:
    packet = build_residual_package_disposition(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "finding_count": packet.get("finding_count"),
                "by_package": packet.get("by_package"),
                "dispositions": [
                    d.get("package") + ":" + d.get("disposition", "")
                    for d in packet.get("dispositions", [])
                ],
                "fail_closed_enabled": packet.get("fail_closed_enabled"),
                "output": "out/production_readiness/ws2/residual_package_disposition.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
