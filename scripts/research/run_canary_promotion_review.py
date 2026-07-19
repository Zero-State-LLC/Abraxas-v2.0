from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.canary_promotion.runtime import run_canary_promotion_review
from core.canonical.json import write_canonical_json


def _load(p: str) -> list[dict]:
    path = Path(p)
    if not path.exists():
        return []
    d = json.loads(path.read_text())
    return d if isinstance(d, list) else [d]


if __name__ == "__main__":
    packet = run_canary_promotion_review(
        _load("out/canary_scheduler/latest.json"),
        _load("out/overlay_observability/latest.json"),
    )
    write_canonical_json("out/canary_promotion/latest.json", packet)
    write_canonical_json("out/canary_promotion_replay/latest.json", packet["replay"])
    write_canonical_json("out/canary_promotion_lineage/latest.json", packet["lineage"])
    write_canonical_json(
        "out/canary_promotion_review/latest.json", packet["operator_review"]
    )
    print("run_canary_promotion_review complete")
