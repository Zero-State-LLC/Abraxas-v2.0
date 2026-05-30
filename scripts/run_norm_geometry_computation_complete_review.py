#!/usr/bin/env python3
"""Runner: emit NormGeometryComputationCompleteReview.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.norm_geometry_computation_complete_review import (
    NormGeometryComputationCompleteReviewError,
    build_computation_complete_review,
    validate_computation_complete_review,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.norm_geometry_computation_complete_review_latest

    log.info("Building NormGeometryComputationCompleteReview.v1 ...")
    review = build_computation_complete_review()

    log.info("Validating ...")
    try:
        validate_computation_complete_review(review)
    except NormGeometryComputationCompleteReviewError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    log.info(
        "all_reviews_passed=%s  valid=%s  invalid=%s  nc=%s",
        review["all_reviews_passed"],
        review["valid_fixture_result_review"]["review_passed"],
        review["invalid_fixture_rejection_review"]["review_passed"],
        review["not_computable_fixture_rejection_review"]["review_passed"],
    )

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
