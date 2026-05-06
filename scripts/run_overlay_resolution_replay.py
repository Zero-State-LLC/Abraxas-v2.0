from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json


if __name__ == "__main__":
    src = Path("out/overlay_resolution/latest.json")
    packet = json.loads(src.read_text()) if src.exists() else {"status": "not_computable"}
    write_canonical_json("out/overlay_resolution_replay/latest.json", packet.get("replay", {"status": "not_computable"}))
