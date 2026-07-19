#!/usr/bin/env python3
"""WP-H: emit Notion readiness mapping (repo-side; no Notion writeback)."""

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

from core.production_readiness.notion_readiness_mapping import (  # noqa: E402
    build_notion_readiness_mapping,
)


def main() -> int:
    mapping = build_notion_readiness_mapping(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "mapping_id": mapping.get("mapping_id"),
                "evidence_state": mapping.get("evidence_state"),
                "risk_012": mapping.get("risk_012", {}).get("status"),
                "writeback_performed": mapping.get("writeback_performed"),
                "summary": mapping.get("summary"),
                "output": "out/production_readiness/ws8/notion_readiness_mapping.v1.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
