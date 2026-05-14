"""Script: build and write the global pipeline registry.

Usage:
    python scripts/run_registry.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canonical.json import write_canonical_json
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.pipelines.registry import build_registry, load_contracts

_PATHS = RuntimePaths.from_env()
CONTRACTS_DIR = _PATHS.pipelines_contracts_dir
OUT_PATH = _PATHS.registry_latest
logger = logging.getLogger(__name__)


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "registry_generation",
        artifact_path=OUT_PATH,
        context={"contracts_dir": CONTRACTS_DIR.as_posix()},
    )
    log_event(
        diagnostics_logger,
        "INFO",
        "registry_generation_started",
        contracts_dir=CONTRACTS_DIR.as_posix(),
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    contracts = load_contracts(CONTRACTS_DIR)
    registry = build_registry(contracts)
    write_canonical_json(OUT_PATH, registry)
    log_event(
        diagnostics_logger,
        "INFO",
        "registry_generation_completed",
        contracts_dir=CONTRACTS_DIR.as_posix(),
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
        contract_count=len(contracts),
        pipeline_count=registry["pipeline_count"],
        recommended_next_state=registry["recommended_next_state"],
        status=registry["status"],
    )


if __name__ == "__main__":
    main()
