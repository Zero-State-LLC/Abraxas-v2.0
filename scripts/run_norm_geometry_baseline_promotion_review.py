"""Script: emit deterministic NormGeometryBaselinePromotionReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.norm_geometry_baseline_promotion_review import (
    NormGeometryBaselinePromotionReviewError,
    build_norm_geometry_baseline_promotion_review,
    validate_norm_geometry_baseline_promotion_review,
)
from core.canonical.json import canonical_dumps
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_NORM_GEOMETRY_SHADOW_STUB_BASELINE_PROMOTION_REVIEW_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.norm_geometry_baseline_promotion_review_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "norm_geometry_baseline_promotion_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "norm_geometry_baseline_promotion_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    review = build_norm_geometry_baseline_promotion_review()

    try:
        validate_norm_geometry_baseline_promotion_review(review)
    except NormGeometryBaselinePromotionReviewError as exc:
        log_event(
            logger,
            "ERROR",
            "norm_geometry_baseline_promotion_review_validation_failed",
            error=str(exc),
            correlation_id=correlation_id,
        )
        raise SystemExit(1) from exc

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(canonical_dumps(review) + "\n", encoding="utf-8")

    log_event(
        logger,
        "INFO",
        "norm_geometry_baseline_promotion_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        review_status=review.get("review_status", "?"),
        canonical_hash=review.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"review_id={review['review_id']}")
    print(f"review_status={review['review_status']}")
    print(f"canonical_hash={review.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
