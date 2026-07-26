from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.sandbox.runtime import run_adaptive_sandbox


def _load(path: str, default: dict | None = None) -> dict:
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    if default is not None:
        return default
    raise FileNotFoundError(
        f"required artifact missing: {path} (refuse unknown telemetry fallback)"
    )


def main() -> None:
    state = _load("out/state/latest.json", {"state_hash": "root"})
    replay = _load("out/replay/latest.json", {"replay_hash": "none"})
    topology = _load("out/yggdrasil/runtime.latest.json", {"topology_hash": "unknown"})
    # Require real ObservabilityAggregation — nested telemetry_hash must be present.
    observability = _load("out/observability/latest.json")
    packet = run_adaptive_sandbox(state, replay, topology, observability)
    write_canonical_json(Path("out/sandbox/latest.json"), packet)
    write_canonical_json(Path("out/sandbox_lineage/latest.json"), packet["lineage"])
    write_canonical_json(
        Path("out/sandbox_convergence/latest.json"), packet["convergence"]
    )
    write_canonical_json(Path("out/sandbox_replay/latest.json"), packet["replay"])
    print("sandbox artifacts emitted")


if __name__ == "__main__":
    main()
