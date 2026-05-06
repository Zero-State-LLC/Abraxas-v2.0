from __future__ import annotations
import json
from pathlib import Path
from core.overlay_topology.runtime import run_overlay_topology_simulation


def _load(path:str)->list[dict]:
    p=Path(path)
    return [json.loads(p.read_text())] if p.exists() else [{}]

if __name__=='__main__':
    run_overlay_topology_simulation(_load('out/overlay_risk/latest.json'),_load('out/overlay_governance/latest.json'),_load('out/canary_scheduler/latest.json'),_load('out/canary_promotion/latest.json'))
