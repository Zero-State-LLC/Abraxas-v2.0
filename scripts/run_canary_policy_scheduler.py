from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canary_scheduler.runtime import run_canary_policy_scheduler


def _load(p: str) -> list[dict]:
    path = Path(p)
    if not path.exists():
        return []
    d = json.loads(path.read_text())
    return d if isinstance(d, list) else [d]


if __name__ == "__main__":
    run_canary_policy_scheduler(_load("out/canary/latest.json"), _load("out/overlay_observability/latest.json"))
    print("run_canary_policy_scheduler complete")
