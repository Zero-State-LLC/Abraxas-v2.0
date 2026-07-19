from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.overlay_containment.runtime import run_overlay_containment_policy


if __name__ == "__main__":
    packet = run_overlay_containment_policy([], [], [], [], [])
    write_canonical_json("out/overlay_containment/latest.json", packet)
    write_canonical_json(
        "out/overlay_containment_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/overlay_containment_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/overlay_containment_diagnostics/latest.json", packet["diagnostics"]
    )
