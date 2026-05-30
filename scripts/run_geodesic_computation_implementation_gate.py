#!/usr/bin/env python3
"""Runner: emit GeodesicComputationImplementationGate.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.geodesic_computation_implementation_gate import (
    GeodesicComputationImplementationGateValidationError,
    build_computation_implementation_gate,
    validate_computation_implementation_gate,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.geodesic_computation_implementation_gate_latest

    log.info("Building GeodesicComputationImplementationGate.v1 ...")
    gate = build_computation_implementation_gate()

    log.info("Validating ...")
    try:
        validate_computation_implementation_gate(gate)
    except GeodesicComputationImplementationGateValidationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(gate, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        out_path,
        gate["canonical_hash"][:16] + "…",
        gate["gate_status"],
    )


if __name__ == "__main__":
    main()
