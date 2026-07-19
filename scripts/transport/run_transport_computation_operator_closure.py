#!/usr/bin/env python3
"""Runner: emit TransportComputationOperatorClosure.v1 artifact.

Lane:  SHADOW
Scope: COMPUTATION_OPERATOR_CLOSURE_ONLY
Output: out/metric_operator/transport_computation_operator_closure_001.latest.json
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from core.transport_computation_operator_closure import (
    TransportComputationOperatorClosureError,
    build_computation_operator_closure,
    validate_computation_operator_closure,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_PATH = Path(
    "out/metric_operator/transport_computation_operator_closure_001.latest.json"
)


def main() -> None:
    log.info("TRANSPORT COMPUTATION OPERATOR CLOSURE — SHADOW / CLOSURE_ONLY")
    log.info("Building TransportComputationOperatorClosure.v1 ...")

    try:
        closure = build_computation_operator_closure()
    except TransportComputationOperatorClosureError as exc:
        log.error("Build failed: %s", exc)
        sys.exit(1)

    log.info("Validating ...")
    try:
        validate_computation_operator_closure(closure)
    except TransportComputationOperatorClosureError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    log.info(
        "all_closure_passed=%s  review_binding=%s  receipt_binding=%s  gate_binding=%s",
        closure["all_closure_passed"],
        closure["complete_review_binding"]["closure_passed"],
        closure["computation_receipt_binding"]["closure_passed"],
        closure["implementation_gate_binding"]["closure_passed"],
    )
    log.info(
        "valid=%s  invalid=%s  nc=%s  solver=%s  lock=%s",
        closure["valid_fixture_result_closure"]["closure_passed"],
        closure["invalid_fixture_rejection_closure"]["closure_passed"],
        closure["not_computable_fixture_rejection_closure"]["closure_passed"],
        closure["solver_policy_closure"]["closure_passed"],
        closure["authority_lock_closure"]["closure_passed"],
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(closure, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        OUT_PATH,
        closure["canonical_hash"][:16] + "…",
        closure["closure_status"],
    )

    print(f"closure_status={closure['closure_status']}")
    print(f"all_closure_passed={closure['all_closure_passed']}")
    print(f"canonical_hash={closure['canonical_hash']}")
    print(f"recommended_next_step={closure['recommended_next_step']}")
    print(f"wrote={OUT_PATH.as_posix()}")


if __name__ == "__main__":
    main()
