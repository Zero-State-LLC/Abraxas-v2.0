from __future__ import annotations
import json
from pathlib import Path
from core.overlay_risk.runtime import run_overlay_risk_envelope

def _load(path: str) -> list[dict]:
    p = Path(path)
    return [json.loads(p.read_text())] if p.exists() else [{}]

if __name__ == '__main__':
    run_overlay_risk_envelope(_load('out/overlay_governance/latest.json'), _load('out/overlay_observability/latest.json'), _load('out/canary_scheduler/latest.json'), _load('out/canary_promotion/latest.json'))
