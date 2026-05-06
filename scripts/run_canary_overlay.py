from __future__ import annotations

from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canary.runtime import run_canary_overlay


def _load(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    return data if isinstance(data, list) else [data]


if __name__ == "__main__":
    run_canary_overlay(_load("out/drift/latest.json"), _load("out/forecast/latest.json"), _load("out/brier/latest.json"))
    print("run_canary_overlay complete")
