#!/usr/bin/env python3
"""Runner: emit GeodesicComputationOperatorClosure.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.geodesic_computation_operator_closure import (
    GeodesicComputationOperatorClosureError,
    build_computation_operator_closure,
    validate_computation_operator_closure,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.geodesic_computation_operator_closure_latest

    log.info("Building GeodesicComputationOperatorClosure.v1 ...")
    closure = build_computation_operator_closure()

    log.info("Validating ...")
    try:
        validate_computation_operator_closure(closure)
    except GeodesicComputationOperatorClosureError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    log.info(
        "all_closure_passed=%s  phase=%s  valid=%s  rejection=%s  locks=%s",
        closure["all_closure_passed"],
        closure["phase_completion_review"]["closure_passed"],
        closure["valid_fixture_result_closure"]["closure_passed"],
        closure["rejection_fixture_closure"]["closure_passed"],
        closure["authority_lock_closure"]["closure_passed"],
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(closure, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        out_path,
        closure["canonical_hash"][:16] + "…",
        closure["closure_status"],
    )


if __name__ == "__main__":
    main()
