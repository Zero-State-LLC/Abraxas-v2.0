from __future__ import annotations

from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.canonical.json import write_canonical_json

if __name__ == "__main__":
    data = json.loads(Path("out/canary/latest.json").read_text())
    write_canonical_json("out/canary_replay/latest.json", data["replay"])
    print("run_canary_replay complete")
