#!/usr/bin/env python3
"""Runner: emit TransportComputationCompleteReview.v1 artifact.

Lane:  SHADOW
Scope: COMPUTATION_COMPLETE_REVIEW_ONLY
Output: out/metric_operator/transport_computation_complete_review_001.latest.json
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from core.transport_computation_complete_review import (
    TransportComputationCompleteReviewError,
    build_computation_complete_review,
    validate_computation_complete_review,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_PATH = Path(
    "out/metric_operator/transport_computation_complete_review_001.latest.json"
)


def main() -> None:
    log.info("TRANSPORT COMPUTATION COMPLETE REVIEW — SHADOW / REVIEW_ONLY")
    log.info("Building TransportComputationCompleteReview.v1 ...")

    try:
        review = build_computation_complete_review()
    except TransportComputationCompleteReviewError as exc:
        log.error("Build failed: %s", exc)
        sys.exit(1)

    log.info("Validating ...")
    try:
        validate_computation_complete_review(review)
    except TransportComputationCompleteReviewError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    log.info(
        "all_reviews_passed=%s  valid=%s  invalid=%s  nc=%s  solver=%s",
        review["all_reviews_passed"],
        review["valid_fixture_result_review"]["review_passed"],
        review["invalid_fixture_rejection_review"]["review_passed"],
        review["not_computable_fixture_rejection_review"]["review_passed"],
        review["solver_policy_review"]["review_passed"],
    )
    log.info(
        "receipt_presence=%s  gate_binding=%s  lock_review=%s",
        review["receipt_presence_review"]["review_passed"],
        review["implementation_gate_binding"]["review_passed"],
        review["authority_lock_review"]["review_passed"],
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(review, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        OUT_PATH,
        review["canonical_hash"][:16] + "…",
        review["review_status"],
    )

    print(f"review_status={review['review_status']}")
    print(f"all_reviews_passed={review['all_reviews_passed']}")
    print(f"canonical_hash={review['canonical_hash']}")
    print(f"recommended_next_step={review['recommended_next_step']}")
    print(f"wrote={OUT_PATH.as_posix()}")


if __name__ == "__main__":
    main()
