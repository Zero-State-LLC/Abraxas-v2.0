from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json
from core.config import RuntimePaths
from core.state.runtime import run_state_engine

logger = logging.getLogger(__name__)

_PATHS = RuntimePaths.from_env()
_EXECUTION_PATH = _PATHS.execution_latest
_REPLAY_PATH = _PATHS.replay_latest
_TELEMETRY_PATH = _PATHS.telemetry_latest
_TOPOLOGY_PATH = _PATHS.topology_latest
_STATE_RUNTIME_PATH = _PATHS.state_runtime_latest


def _load(path: str | Path, default: dict[str, Any]) -> dict[str, Any]:
    """Load JSON from *path*.

    - FileNotFoundError: file is absent → use *default* (input_missing).
    - OSError (other): unreadable → raise RuntimeError (input_unreadable).
    - JSONDecodeError: corrupt data → raise RuntimeError (input_malformed).
    """
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
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
    execution = _load(_EXECUTION_PATH, {"pipeline_id": "shadow", "execution_hash": "exec:latest", "prev_state_hash": "root"})
    replay = _load(_REPLAY_PATH, {"replay_hash": "replay:latest"})
    telemetry = _load(_TELEMETRY_PATH, {"telemetry_hash": "telemetry:latest"})
    topology = _load(_TOPOLOGY_PATH, {"topology_hash": "topology:latest"})
    result = run_state_engine(execution, replay, telemetry, topology)
    write_canonical_json(_STATE_RUNTIME_PATH, result)
    print(f"State engine complete: {_STATE_RUNTIME_PATH}")


if __name__ == "__main__":
    main()
