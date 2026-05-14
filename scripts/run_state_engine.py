from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json
from core.config import RuntimePaths
from core.diagnostics import (
    get_structured_logger,
    log_event,
    stable_correlation_id,
)
from core.state.runtime import run_state_engine

logger = logging.getLogger(__name__)

_PATHS = RuntimePaths.from_env()
_EXECUTION_PATH = _PATHS.execution_latest
_REPLAY_PATH = _PATHS.replay_latest
_TELEMETRY_PATH = _PATHS.telemetry_latest
_TOPOLOGY_PATH = _PATHS.topology_latest
_STATE_RUNTIME_PATH = _PATHS.state_runtime_latest


def _load(
    path: str | Path,
    default: dict[str, Any],
    *,
    diagnostics_logger: logging.Logger | None = None,
) -> dict[str, Any]:
    """Load JSON from *path*.

    - FileNotFoundError: file is absent → use *default* (input_missing).
    - OSError (other): unreadable → raise RuntimeError (input_unreadable).
    - JSONDecodeError: corrupt data → raise RuntimeError (input_malformed).
    """
    path = Path(path)
    active_logger = diagnostics_logger or logger
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        log_event(
            active_logger,
            "WARNING",
            "state_engine_input_missing",
            reason="input_missing",
            artifact_path=str(path),
            correlation_id=stable_correlation_id(
                "state_engine_input",
                artifact_path=path,
                context={"reason": "input_missing"},
            ),
        )
        return default
    except OSError as exc:
        log_event(
            active_logger,
            "ERROR",
            "state_engine_input_unreadable",
            reason="input_unreadable",
            artifact_path=str(path),
            correlation_id=stable_correlation_id(
                "state_engine_input",
                artifact_path=path,
                context={"reason": "input_unreadable"},
            ),
            error_type=type(exc).__name__,
        )
        raise RuntimeError(f"input_unreadable: {path}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        log_event(
            active_logger,
            "ERROR",
            "state_engine_input_malformed",
            reason="input_malformed",
            artifact_path=str(path),
            correlation_id=stable_correlation_id(
                "state_engine_input",
                artifact_path=path,
                context={"reason": "input_malformed"},
            ),
            line=exc.lineno,
            column=exc.colno,
        )
        raise RuntimeError(f"input_malformed: {path}") from exc


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)
    input_artifacts = [
        _EXECUTION_PATH.as_posix(),
        _REPLAY_PATH.as_posix(),
        _TELEMETRY_PATH.as_posix(),
        _TOPOLOGY_PATH.as_posix(),
    ]
    execution = _load(
        _EXECUTION_PATH,
        {
            "pipeline_id": "shadow",
            "execution_hash": "exec:latest",
            "prev_state_hash": "root",
        },
        diagnostics_logger=diagnostics_logger,
    )
    replay = _load(
        _REPLAY_PATH,
        {"replay_hash": "replay:latest"},
        diagnostics_logger=diagnostics_logger,
    )
    telemetry = _load(
        _TELEMETRY_PATH,
        {"telemetry_hash": "telemetry:latest"},
        diagnostics_logger=diagnostics_logger,
    )
    topology = _load(
        _TOPOLOGY_PATH,
        {"topology_hash": "topology:latest"},
        diagnostics_logger=diagnostics_logger,
    )
    result = run_state_engine(execution, replay, telemetry, topology)
    write_canonical_json(_STATE_RUNTIME_PATH, result)
    log_event(
        diagnostics_logger,
        "INFO",
        "state_engine_completed",
        artifact_path=_STATE_RUNTIME_PATH.as_posix(),
        correlation_id=stable_correlation_id(
            "state_runtime_write",
            artifact_path=_STATE_RUNTIME_PATH,
            context={"inputs": input_artifacts},
        ),
        input_artifacts=input_artifacts,
    )


if __name__ == "__main__":
    main()
