from __future__ import annotations

from pathlib import Path

import json

from core.canonical.json import write_canonical_json
from core.sandbox.runtime import run_adaptive_sandbox


def _load(path: str, default: dict) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def main() -> None:
    state = _load("out/state/latest.json", {"state_hash": "root"})
    replay = _load("out/replay/latest.json", {"replay_hash": "none"})
    topology = _load("out/yggdrasil/runtime.latest.json", {"topology_hash": "unknown"})
    observability = _load("out/observability/latest.json", {"telemetry_hash": "unknown"})
    result = run_adaptive_sandbox(state, replay, topology, observability)
    write_canonical_json(Path("out/sandbox/latest.json"), result)
    print("sandbox artifacts emitted")


if __name__ == "__main__":
    main()
