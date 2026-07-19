#!/usr/bin/env python3
"""WP-RUNBOOK: emit SUPPORTED surface operator runbook."""

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

from core.production_readiness.supported_surface_operator_runbook import (  # noqa: E402
    build_supported_surface_operator_runbook,
)


def main() -> int:
    runbook = build_supported_surface_operator_runbook(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "procedure_count": len(runbook.get("procedures") or []),
                "surface_summary": runbook.get("surface_summary"),
                "output_json": (
                    "out/production_readiness/ws8/"
                    "supported_surface_operator_runbook.v1.json"
                ),
                "output_md": (
                    "out/production_readiness/ws8/"
                    "supported_surface_operator_runbook.v1.md"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
