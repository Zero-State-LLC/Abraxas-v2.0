#!/usr/bin/env python3
"""Runner: emit GeodesicComputationImplementationPlan.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.geodesic_computation_implementation_plan import (
    GeodesicComputationImplementationPlanValidationError,
    build_computation_implementation_plan,
    validate_computation_implementation_plan,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.geodesic_computation_implementation_plan_latest

    log.info("Building GeodesicComputationImplementationPlan.v1 ...")
    plan = build_computation_implementation_plan()

    log.info("Validating ...")
    try:
        validate_computation_implementation_plan(plan)
    except GeodesicComputationImplementationPlanValidationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(plan, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        out_path,
        plan["canonical_hash"][:16] + "…",
        plan["plan_status"],
    )


if __name__ == "__main__":
    main()
