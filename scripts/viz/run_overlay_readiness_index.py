from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.overlay_readiness.runtime import run_overlay_readiness_index


if __name__ == "__main__":
    packet = run_overlay_readiness_index([], [], [], [], [])
    write_canonical_json("out/overlay_readiness/latest.json", packet)
    write_canonical_json("out/overlay_readiness_replay/latest.json", packet["replay"])
    write_canonical_json("out/overlay_readiness_lineage/latest.json", packet["lineage"])
    write_canonical_json(
        "out/overlay_readiness_diagnostics/latest.json", packet["diagnostics"]
    )
