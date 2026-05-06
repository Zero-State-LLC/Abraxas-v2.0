from __future__ import annotations

from core.canonical.json import write_canonical_json
import json
from pathlib import Path
from core.state.runtime import run_state_engine


def _load(path: str, default: dict) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def main() -> None:
    execution = _load("out/execution/latest.json", {"pipeline_id": "shadow", "execution_hash": "exec:latest", "prev_state_hash": "root"})
    replay = _load("out/replay/latest.json", {"replay_hash": "replay:latest"})
    telemetry = _load("out/telemetry/latest.json", {"telemetry_hash": "telemetry:latest"})
    topology = _load("out/topology/latest.json", {"topology_hash": "topology:latest"})
    result = run_state_engine(execution, replay, telemetry, topology)
    write_canonical_json("out/state/runtime.latest.json", result)
    print("State engine complete: out/state/latest.json")


if __name__ == "__main__":
    main()
