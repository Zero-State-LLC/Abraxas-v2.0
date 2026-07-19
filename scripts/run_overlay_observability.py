from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canonical.json import write_canonical_json
from core.overlay_observability.runtime import run_overlay_observability


def _load(p: str) -> list[dict]:
    path = Path(p)
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return data if isinstance(data, list) else [data]


if __name__ == "__main__":
    packet = run_overlay_observability(
        _load("out/canary/latest.json"),
        _load("out/drift/latest.json"),
        _load("out/forecast/latest.json"),
        _load("out/brier/latest.json"),
    )
    write_canonical_json("out/overlay_observability/latest.json", packet)
    write_canonical_json(
        "out/overlay_observability_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/overlay_observability_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/overlay_observability_diagnostics/latest.json", packet["diagnostics"]
    )
    print("run_overlay_observability complete")
