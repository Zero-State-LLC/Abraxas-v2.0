from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json
from core.state.runtime import run_state_engine

logger = logging.getLogger(__name__)


def _load(path: str, default: dict[str, Any]) -> dict[str, Any]:
    """Load JSON from *path*.

    - FileNotFoundError: file is absent → use *default* (input_missing).
    - OSError (other): unreadable → raise RuntimeError (input_unreadable).
    - JSONDecodeError: corrupt data → raise RuntimeError (input_malformed).
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("input_missing: %s — using default", path)
        return default
    except OSError as exc:
        logger.error("input_unreadable: %s — %s", path, exc)
        raise RuntimeError(f"input_unreadable: {path}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error("input_malformed: %s — %s", path, exc)
        raise RuntimeError(f"input_malformed: {path}") from exc


def main() -> None:
    execution = _load("out/execution/latest.json", {"pipeline_id": "shadow", "execution_hash": "exec:latest", "prev_state_hash": "root"})
    replay = _load("out/replay/latest.json", {"replay_hash": "replay:latest"})
    telemetry = _load("out/telemetry/latest.json", {"telemetry_hash": "telemetry:latest"})
    topology = _load("out/topology/latest.json", {"topology_hash": "topology:latest"})
    result = run_state_engine(execution, replay, telemetry, topology)
    write_canonical_json("out/state/runtime.latest.json", result)
    print("State engine complete: out/state/runtime.latest.json")


if __name__ == "__main__":
    main()
