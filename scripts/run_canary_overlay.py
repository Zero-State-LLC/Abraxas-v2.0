from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canary.runtime import build_canary_overlay
from core.canonical.json import write_canonical_json


def _load(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    return data if isinstance(data, list) else [data]


if __name__ == "__main__":
    packet = build_canary_overlay(
        _load("out/drift/latest.json"),
        _load("out/forecast/latest.json"),
        _load("out/brier/latest.json"),
    )
    write_canonical_json("out/canary/latest.json", packet)
    write_canonical_json("out/canary_replay/latest.json", packet["replay"])
    write_canonical_json("out/canary_lineage/latest.json", packet["lineage"])
    write_canonical_json("out/canary_rollback/latest.json", packet["rollback"])
    print("run_canary_overlay complete")
