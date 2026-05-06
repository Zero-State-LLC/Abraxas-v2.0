from __future__ import annotations

import json
from pathlib import Path

from core.overlay_governance.runtime import run_overlay_governance_ledger


def _load(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return [{}]
    return [json.loads(p.read_text())]


if __name__ == "__main__":
    run_overlay_governance_ledger(
        _load("out/canary/latest.json"),
        _load("out/overlay_observability/latest.json"),
        _load("out/canary_scheduler/latest.json"),
        _load("out/canary_promotion/latest.json"),
    )
