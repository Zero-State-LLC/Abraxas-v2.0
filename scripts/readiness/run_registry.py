"""Script: build and write the global pipeline registry.

Usage:
    python scripts/readiness/run_registry.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.performance import RuntimeProfiler
from core.pipelines.registry import build_registry, load_contracts

_PATHS = RuntimePaths.from_env()
CONTRACTS_DIR = _PATHS.pipelines_contracts_dir
OUT_PATH = _PATHS.registry_latest
GLOBAL_OUT_PATH = _PATHS.global_pipeline_registry_latest
logger = logging.getLogger(__name__)


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)
    profiler = RuntimeProfiler(_PATHS.runtime_performance_profile_latest)
    profiler.record_artifact("contracts_dir", CONTRACTS_DIR)
    profiler.record_artifact("registry_output", OUT_PATH)
    profiler.record_artifact("global_registry_output", GLOBAL_OUT_PATH)
    correlation_id = stable_correlation_id(
        "registry_generation",
        artifact_path=OUT_PATH,
        context={"contracts_dir": CONTRACTS_DIR.as_posix()},
    )
    profiler.record_correlation("registry_generation", correlation_id)
    log_event(
        diagnostics_logger,
        "INFO",
        "registry_generation_started",
        contracts_dir=CONTRACTS_DIR.as_posix(),
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    with profiler.measure("registry_generation", "load_contracts"):
        contracts = load_contracts(CONTRACTS_DIR)
    with profiler.measure("registry_generation", "build_registry"):
        registry = build_registry(contracts, root=Path("."))
    with profiler.measure("registry_generation", "write_registry"):
        out_root = _PATHS.out_dir
        write_classified_json(
            OUT_PATH,
            registry,
            artifact_class=ArtifactClass.BUILD_EVIDENCE,
            out_root=out_root,
        )
        write_classified_json(
            GLOBAL_OUT_PATH,
            registry,
            artifact_class=ArtifactClass.BUILD_EVIDENCE,
            out_root=out_root,
        )
    log_event(
        diagnostics_logger,
        "INFO",
        "registry_generation_completed",
        contracts_dir=CONTRACTS_DIR.as_posix(),
        artifact_path=OUT_PATH.as_posix(),
        global_artifact_path=GLOBAL_OUT_PATH.as_posix(),
        correlation_id=correlation_id,
        contract_count=len(contracts),
        pipeline_count=registry["pipeline_count"],
        recommended_next_state=registry["recommended_next_state"],
        status=registry["status"],
    )
    profiler.write()


if __name__ == "__main__":
    main()
