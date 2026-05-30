#!/usr/bin/env python3
"""Runner: emit GeodesicExpectedValuesCompleteReview.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.geodesic_expected_values_complete_review import (
    GeodesicExpectedValuesCompleteReviewValidationError,
    build_complete_review,
    validate_complete_review,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.geodesic_expected_values_complete_review_latest

    log.info("Building GeodesicExpectedValuesCompleteReview.v1 ...")
    review = build_complete_review()

    log.info("Validating ...")
    try:
        validate_complete_review(review)
    except GeodesicExpectedValuesCompleteReviewValidationError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(review, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        out_path,
        review["canonical_hash"][:16] + "…",
        review["review_status"],
    )


if __name__ == "__main__":
    main()
