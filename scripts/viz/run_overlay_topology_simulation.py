from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.overlay_topology.runtime import run_overlay_topology_simulation


def _load(path: str) -> list[dict]:
    p = Path(path)
    return [json.loads(p.read_text())] if p.exists() else [{}]


if __name__ == "__main__":
    packet = run_overlay_topology_simulation(
        _load("out/overlay_risk/latest.json"),
        _load("out/overlay_governance/latest.json"),
        _load("out/canary_scheduler/latest.json"),
        _load("out/canary_promotion/latest.json"),
    )
    write_canonical_json("out/overlay_topology/latest.json", packet)
    write_canonical_json("out/overlay_topology_replay/latest.json", packet["replay"])
    write_canonical_json("out/overlay_topology_lineage/latest.json", packet["lineage"])
    write_canonical_json(
        "out/overlay_topology_diagnostics/latest.json", packet["diagnostics"]
    )
