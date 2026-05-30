#!/usr/bin/env python3
"""Runner: emit NormGeometryComputationImplementationGate.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.norm_geometry_computation_implementation_gate import (
    NormGeometryComputationImplementationGateValidationError,
    build_computation_implementation_gate,
    validate_computation_implementation_gate,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.norm_geometry_computation_implementation_gate_latest

    log.info("Building NormGeometryComputationImplementationGate.v1 ...")
    gate = build_computation_implementation_gate()

    log.info("Validating ...")
    try:
        validate_computation_implementation_gate(gate)
    except NormGeometryComputationImplementationGateValidationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    lc = gate["authorized_implementation_scope"]["locked_constants_binding"]
    log.info(
        "Locked constants: count=%d  float64=%s  p_inf=%s  max_element=%s  max_p=%s",
        lc["constants_count"],
        lc["float64_precision_declaration"],
        lc["p_inf_sentinel_value_declaration"],
        lc["max_element_magnitude_declaration"],
        lc["max_p_value_declaration"],
    )

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
