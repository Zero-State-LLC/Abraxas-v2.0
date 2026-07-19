#!/usr/bin/env python3
"""Generate merged Workstream 1 Interface Registry snapshot."""

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

from core.production_readiness.interface_registry import (  # noqa: E402
    build_interface_registry,
)


def main() -> int:
    registry = build_interface_registry(REPO_ROOT, write=True)
    summary = registry.get("summary", {})
    print(
        json.dumps(
            {
                "registry_id": registry.get("registry_id"),
                "repository_sha": registry.get("repository_sha"),
                "evidence_state": registry.get("evidence_state"),
                "entry_count": summary.get("entry_count"),
                "by_stability_class": summary.get("by_stability_class"),
                "supported_count": summary.get("supported_count"),
                "output": "out/production_readiness/ws1/interface_registry_snapshot.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
