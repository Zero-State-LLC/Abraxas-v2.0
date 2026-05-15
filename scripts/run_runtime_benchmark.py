"""Script: execute runtime benchmark and emit drift report.

PATCH-P10-RUNTIME-BENCHMARK-AND-DRIFT-GUARD-001

Usage:
    python scripts/run_runtime_benchmark.py

Output:
    out/audit/runtime_benchmark_001.latest.json

Observational-only.  No authority or mutation side effects.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.benchmark import (
    BenchmarkRunner,
    build_benchmark_artifact,
    write_benchmark_artifact,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.pipelines.registry import build_registry, load_contracts

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.runtime_benchmark_latest
CONTRACTS_DIR = _PATHS.pipelines_contracts_dir

logger = logging.getLogger(__name__)

_BASELINE_RUN_COUNT = 3
_OPTIMIZED_RUN_COUNT = 3


def _registry_surface() -> object:
    """Execute one registry load pass and return the registry object."""
    contracts = load_contracts(CONTRACTS_DIR)
    return build_registry(contracts)


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)

    correlation_id = stable_correlation_id(
        "runtime_benchmark",
        artifact_path=OUT_PATH,
        context={"contracts_dir": CONTRACTS_DIR.as_posix()},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "runtime_benchmark_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    # --- baseline suite ---
    baseline_runner = BenchmarkRunner(
        surface="registry_generation.baseline",
        run_count=_BASELINE_RUN_COUNT,
    )
    baseline_runner.run(
        _registry_surface,
        registry_loads=1,
        serialization_counts=1,
        artifact_writes=1,
    )
    baseline_suite = baseline_runner.build_suite("baseline_registry_001")

    # --- optimized suite (same workload; placeholder for future optimization layer) ---
    optimized_runner = BenchmarkRunner(
        surface="registry_generation.optimized",
        run_count=_OPTIMIZED_RUN_COUNT,
    )
    optimized_runner.run(
        _registry_surface,
        registry_loads=1,
        serialization_counts=1,
        artifact_writes=1,
    )
    optimized_suite = optimized_runner.build_suite("optimized_registry_001")

    artifact = build_benchmark_artifact(
        artifact_id="runtime_benchmark_001",
        baseline_suite=baseline_suite,
        optimized_suite=optimized_suite,
        output_path=OUT_PATH,
    )

    written_path = write_benchmark_artifact(OUT_PATH, artifact)

    log_event(
        diagnostics_logger,
        "INFO",
        "runtime_benchmark_completed",
        artifact_path=written_path.as_posix(),
        correlation_id=correlation_id,
        drift_detected=artifact["drift_report"]["drift_detected"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
