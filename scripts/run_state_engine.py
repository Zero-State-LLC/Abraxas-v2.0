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
from core.performance import RuntimeProfiler
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
    diag_logger = get_structured_logger(__name__)
    profiler = RuntimeProfiler(_PATHS.runtime_performance_profile_latest)
    input_artifacts = [
        _EXECUTION_PATH.as_posix(),
        _REPLAY_PATH.as_posix(),
        _TELEMETRY_PATH.as_posix(),
        _TOPOLOGY_PATH.as_posix(),
    ]
    profiler.record_artifact("execution_input", _EXECUTION_PATH)
    profiler.record_artifact("replay_input", _REPLAY_PATH)
    profiler.record_artifact("telemetry_input", _TELEMETRY_PATH)
    profiler.record_artifact("topology_input", _TOPOLOGY_PATH)
    profiler.record_artifact("state_runtime_output", _STATE_RUNTIME_PATH)
    with profiler.measure("state_engine_runtime_write", "load_execution"):
        execution = _load(
            _EXECUTION_PATH,
            {
                "pipeline_id": "shadow",
                "execution_hash": "exec:latest",
                "prev_state_hash": "root",
            },
            diagnostics_logger=diag_logger,
        )
    with profiler.measure("state_engine_runtime_write", "load_replay"):
        replay = _load(
            _REPLAY_PATH,
            {"replay_hash": "replay:latest"},
            diagnostics_logger=diag_logger,
        )
    with profiler.measure("state_engine_runtime_write", "load_telemetry"):
        telemetry = _load(
            _TELEMETRY_PATH,
            {"telemetry_hash": "telemetry:latest"},
            diagnostics_logger=diag_logger,
        )
    with profiler.measure("state_engine_runtime_write", "load_topology"):
        topology = _load(
            _TOPOLOGY_PATH,
            {"topology_hash": "topology:latest"},
            diagnostics_logger=diag_logger,
        )
    with profiler.measure("state_engine_runtime_write", "run_state_engine"):
        result = run_state_engine(execution, replay, telemetry, topology)
    with profiler.measure("state_engine_runtime_write", "write_state_runtime"):
        # Sole-writer publication (WP-D batch2): core/state/runtime is pure builder
        write_canonical_json(_STATE_RUNTIME_PATH, result)
        write_canonical_json(Path("out/state/latest.json"), result["snapshot"])
        write_canonical_json(Path("out/state_lineage/latest.json"), result["lineage"])
        write_canonical_json(
            Path("out/stabilization/latest.json"), result["stabilization"]
        )

    correlation_namespace = "state_runtime_write"
    correlation_id = stable_correlation_id(
        correlation_namespace,
        artifact_path=_STATE_RUNTIME_PATH,
        context={"inputs": input_artifacts},
    )
    profiler.record_correlation(correlation_namespace, correlation_id)
    log_event(
        diag_logger,
        "INFO",
        "state_engine_completed",
        artifact_path=_STATE_RUNTIME_PATH.as_posix(),
        correlation_id=correlation_id,
        input_artifacts=input_artifacts,
    )
    profiler.write()


if __name__ == "__main__":
    main()
