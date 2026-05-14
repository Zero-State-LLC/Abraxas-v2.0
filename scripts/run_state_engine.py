from __future__ import annotations

import json
import logging
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.state.runtime import run_state_engine

logger = logging.getLogger(__name__)

_STATE_OUTPUT_PATH = "out/state/runtime.latest.json"


def _load_optional(path: str, default: dict) -> dict:
    """Load JSON from path, returning default only if the file is missing.

    Raises on malformed/corrupt JSON or other read errors so that
    upstream artifacts are never silently discarded.

    Reason codes:
      input_missing   – file does not exist; default used (optional input)
      input_malformed – file exists but is not valid JSON
      input_unreadable – file exists but could not be read
    """
    p = Path(path)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning("input_missing: %s – using default", path)
        return default
    except json.JSONDecodeError as exc:
        logger.error("input_malformed: %s – %s", path, exc)
        raise RuntimeError(f"input_malformed: {path}") from exc
    except OSError as exc:
        logger.error("input_unreadable: %s – %s", path, exc)
        raise RuntimeError(f"input_unreadable: {path}") from exc


def main() -> None:
    execution = _load_optional("out/execution/latest.json", {"pipeline_id": "shadow", "execution_hash": "exec:latest", "prev_state_hash": "root"})
    replay = _load_optional("out/replay/latest.json", {"replay_hash": "replay:latest"})
    telemetry = _load_optional("out/telemetry/latest.json", {"telemetry_hash": "telemetry:latest"})
    topology = _load_optional("out/topology/latest.json", {"topology_hash": "topology:latest"})
    result = run_state_engine(execution, replay, telemetry, topology)
    write_canonical_json(_STATE_OUTPUT_PATH, result)
    print(f"State engine complete: {_STATE_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
