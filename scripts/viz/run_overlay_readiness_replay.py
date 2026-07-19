from __future__ import annotations
import json
from pathlib import Path
from core.canonical.json import write_canonical_json

if __name__ == "__main__":
    p = Path("out/overlay_readiness/latest.json")
    data = json.loads(p.read_text()) if p.exists() else {"status": "not_computable"}
    write_canonical_json("out/overlay_readiness_replay/latest.json", data.get("replay", {"status": "not_computable"}))
