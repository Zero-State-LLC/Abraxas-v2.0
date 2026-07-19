from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.canonical.json import write_canonical_json

if __name__ == "__main__":
    p = json.loads(Path("out/overlay_observability/latest.json").read_text())
    write_canonical_json("out/overlay_observability_replay/latest.json", p["replay"])
    print("run_overlay_observability_replay complete")
