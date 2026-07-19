#!/usr/bin/env python3
"""Emit Threat Model v0 (WP-F)."""

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

from core.production_readiness.threat_model import build_threat_model_v0  # noqa: E402


def main() -> int:
    model = build_threat_model_v0(REPO_ROOT, write=True)
    print(
        json.dumps(
            {
                "model_id": model.get("model_id"),
                "evidence_state": model.get("evidence_state"),
                "threat_count": len(model.get("threats", [])),
                "control_count": len(model.get("controls", [])),
                "residual_risk_count": len(model.get("residual_risks", [])),
                "output": "out/production_readiness/ws8/threat_model.v0.json",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
