#!/usr/bin/env python3
"""Runner: emit NormGeometryComputationReceipt.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.norm_geometry_computation import (
    NormGeometryComputationError,
    build_computation_receipt,
    validate_computation_receipt,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.norm_geometry_computation_receipt_latest

    log.info("Building NormGeometryComputationReceipt.v1 ...")
    receipt = build_computation_receipt()

    log.info("Validating ...")
    try:
        validate_computation_receipt(receipt)
    except NormGeometryComputationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    cs = receipt["comparison_summary"]
    log.info(
        "Comparison summary: total=%d match=%d mismatch=%d all_match=%s",
        cs["total_valid_fixtures"],
        cs["match_count"],
        cs["mismatch_count"],
        cs["all_valid_match"],
    )
    log.info(
        "Invalid fixtures: %d  NOT_COMPUTABLE fixtures: %d",
        len(receipt["invalid_fixture_results"]),
        len(receipt["not_computable_fixture_results"]),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(receipt, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        out_path,
        receipt["canonical_hash"][:16] + "…",
        receipt["computation_status"],
    )


if __name__ == "__main__":
    main()
