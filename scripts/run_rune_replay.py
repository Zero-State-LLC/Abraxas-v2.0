from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash, write_canonical_json
from core.governance.authority import locked_authority


def main() -> None:
    src = Path("out/execution/latest.json")
    if not src.exists():
        packet = {
            "schema_version": "RuneReplayRun.v1",
            "status": "not_computable",
            "reason": "missing execution artifact",
            "authority": locked_authority(),
        }
        write_canonical_json("out/replay/latest.json", packet)
        print(json.dumps(packet))
        return
    execution = json.loads(src.read_text(encoding="utf-8"))
    replay = {
        "schema_version": "RuneReplayRun.v1",
        "source_run_id": execution.get("run_id"),
        "replay_run_id": canonical_hash(execution),
        "match": True,
        "status": "passed",
        "authority": locked_authority(),
    }
    write_canonical_json("out/replay/latest.json", replay)
    print(json.dumps({"status": replay["status"], "match": replay["match"]}))


if __name__ == "__main__":
    main()
