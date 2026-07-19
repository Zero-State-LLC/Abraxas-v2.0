"""Runner: emit TransportComputationImplementationGate.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.transport_computation_implementation_gate import (
    TransportComputationImplementationGateValidationError,
    build_transport_computation_implementation_gate,
    validate_transport_computation_implementation_gate,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.transport_computation_implementation_gate_001_latest

    log.info("Building TransportComputationImplementationGate.v1 ...")
    gate = build_transport_computation_implementation_gate()

    log.info("Validating ...")
    try:
        validate_transport_computation_implementation_gate(gate)
    except TransportComputationImplementationGateValidationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    lc = gate["locked_constants_binding"]
    log.info(
        "Locked constants: count=%d  solver=%s  pivot=%s  tie_breaking=%s",
        lc["constants_count"],
        lc["lp_solver_variant_declaration"],
        lc["pivot_rule_declaration"],
        lc["tie_breaking_rule_declaration"],
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(gate, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        out_path,
        gate["canonical_hash"][:16] + "...",
        gate["gate_status"],
    )
    print(f"gate_status={gate['gate_status']}")
    print(f"canonical_hash={gate['canonical_hash']}")
    print(f"recommended_next_step={gate['recommended_next_step']}")
    print(f"wrote={out_path.as_posix()}")


if __name__ == "__main__":
    main()
