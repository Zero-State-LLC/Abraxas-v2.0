from __future__ import annotations

import json
from pathlib import Path

from core.observability.validators import validate_lineage_replay


def main() -> None:
    trace = json.loads(Path("out/lineage/latest.json").read_text(encoding="utf-8"))
    replay = json.loads(Path("out/graph_replay/latest.json").read_text(encoding="utf-8"))
    result = validate_lineage_replay(trace, replay)
    Path("out/lineage/validation.latest.json").write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])


if __name__ == "__main__":
    main()
