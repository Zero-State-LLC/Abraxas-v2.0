from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.overlay_observability.runtime import run_overlay_observability


def _load(p: str) -> list[dict]:
    path = Path(p)
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return data if isinstance(data, list) else [data]


if __name__ == "__main__":
    run_overlay_observability(_load("out/canary/latest.json"), _load("out/drift/latest.json"), _load("out/forecast/latest.json"), _load("out/brier/latest.json"))
    print("run_overlay_observability complete")
