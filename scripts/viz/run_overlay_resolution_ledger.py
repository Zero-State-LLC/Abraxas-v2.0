from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.overlay_resolution.runtime import run_overlay_resolution_ledger


if __name__ == "__main__":
    packet = run_overlay_resolution_ledger([], [], [], [], [])
    write_canonical_json("out/overlay_resolution/latest.json", packet)
    write_canonical_json(
        "out/overlay_resolution_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/overlay_resolution_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/overlay_resolution_diagnostics/latest.json", packet["diagnostics"]
    )
