"""Runner: emit WassersteinCpuBaselineImplementationGate.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.wasserstein_cpu_baseline_implementation_gate import (
    WassersteinCpuBaselineImplementationGateValidationError,
    build_wasserstein_cpu_baseline_implementation_gate,
    validate_wasserstein_cpu_baseline_implementation_gate,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.wasserstein_cpu_baseline_implementation_gate_001_latest

    log.info("Building WassersteinCpuBaselineImplementationGate.v1 ...")
    gate = build_wasserstein_cpu_baseline_implementation_gate()

    log.info("Validating ...")
    try:
        validate_wasserstein_cpu_baseline_implementation_gate(gate)
    except WassersteinCpuBaselineImplementationGateValidationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    lc = gate["locked_constants_binding"]
    log.info(
        "Locked constants: count=%d  solver=%s  fixture_scope=%s",
        lc["constants_count"],
        lc["solver_policy"],
        lc["supported_fixture_scope"],
    )

    fsr = gate["fixture_scope_review"]
    log.info(
        "Fixture scope: valid=%d  invalid=%d  not_computable=%d  total=%d",
        fsr["valid_fixture_count"],
        fsr["invalid_fixture_count"],
        fsr["not_computable_fixture_count"],
        fsr["total_fixture_count"],
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
