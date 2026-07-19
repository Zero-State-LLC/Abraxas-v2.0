#!/usr/bin/env python3
"""Runner: emit TransportBaselinePromotionReview.v1 artifact.

Lane:  SHADOW
Scope: BASELINE_PROMOTION_REVIEW_ONLY
Output: out/metric_operator/transport_baseline_promotion_review_001.latest.json
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from core.transport_baseline_promotion_review import (
    TransportBaselinePromotionReviewError,
    build_transport_baseline_promotion_review,
    validate_transport_baseline_promotion_review,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_PATH = Path(
    "out/metric_operator/transport_baseline_promotion_review_001.latest.json"
)


def main() -> None:
    log.info("TRANSPORT BASELINE PROMOTION REVIEW — SHADOW / BASELINE_PROMOTION_REVIEW_ONLY")
    log.info("Building TransportBaselinePromotionReview.v1 ...")

    try:
        review = build_transport_baseline_promotion_review()
    except TransportBaselinePromotionReviewError as exc:
        log.error("Build failed: %s", exc)
        sys.exit(1)

    log.info("Validating ...")
    try:
        validate_transport_baseline_promotion_review(review)
    except TransportBaselinePromotionReviewError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    log.info(
        "all_reviews_passed=%s  decision=%s  closure=%s  chain=%s",
        review["all_reviews_passed"],
        review["decision_presence_review"]["review_passed"],
        review["source_closure_binding"]["review_passed"],
        review["computation_chain_closure_review"]["review_passed"],
    )
    log.info(
        "target=%s  no_op=%s  scope=%s  locks=%s",
        review["target_state_review"]["review_passed"],
        review["no_op_parity_review"]["review_passed"],
        review["promotion_scope_review"]["review_passed"],
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
