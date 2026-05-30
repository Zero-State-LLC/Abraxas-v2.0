#!/usr/bin/env python3
"""Runner: emit GeodesicTestVectorFixturePlan.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.geodesic_test_vector_fixture_plan import (
    GeodesicTestVectorFixturePlanValidationError,
    build_fixture_plan,
    validate_fixture_plan,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.geodesic_test_vector_fixture_plan_latest

    log.info("Building GeodesicTestVectorFixturePlan.v1 ...")
    plan = build_fixture_plan()

    log.info("Validating ...")
    try:
        validate_fixture_plan(plan)
    except GeodesicTestVectorFixturePlanValidationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(plan, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s",
        out_path,
        plan["canonical_hash"][:16] + "…",
    )


if __name__ == "__main__":
    main()
