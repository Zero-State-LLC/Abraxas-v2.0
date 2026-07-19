"""Script: emit WassersteinTestVectorFixtureCreationReadinessReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_test_vector_fixture_creation_readiness_review import (
    build_wasserstein_test_vector_fixture_creation_readiness_review,
    default_authority_lock_check,
    default_authority_locks,
    default_blocked_scopes,
    default_fixture_coverage_check,
    default_operator_review_requirement,
    default_plan_triad_presence_check,
    serialize_wasserstein_test_vector_fixture_creation_readiness_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = (
    "PATCH_P48_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_READINESS_REVIEW_001"
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_test_vector_fixture_creation_readiness_review_latest

_PAYLOAD: dict = {
    "review_id": "wasserstein_test_vector_fixture_creation_readiness_review_001",
    "intended_lane": "SHADOW",
    "review_stage": "FIXTURE_CREATION_READINESS_REVIEW_ONLY",
    "plan_triad_presence_check": default_plan_triad_presence_check(),
    "fixture_coverage_check": default_fixture_coverage_check(),
    "authority_lock_check": default_authority_lock_check(),
    "operator_review_requirement": default_operator_review_requirement(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "recommended_next_step": "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_PR_PLAN",
    "provenance": {
        "source": "P48_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_READINESS_REVIEW",
        "evidence_refs": [
            "WassersteinTestVectorFixturePlan.v1:"
            "wasserstein_test_vector_fixture_plan_001",
            "WassersteinTestVectorSchemaPlan.v1:"
            "wasserstein_test_vector_schema_plan_001",
            "WassersteinDistanceImplementationReadinessDossier.v1:"
            "wasserstein_distance_implementation_readiness_dossier_001",
            "WassersteinFixturePlanConsolidationReceipt.v1:"
            "wasserstein_fixture_plan_consolidation_receipt_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_test_vector_fixture_creation_readiness_review.v1.schema.json",
            "contracts/canon/wasserstein_test_vector_fixture_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_fixture_creation_readiness_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_creation_readiness_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_test_vector_fixture_creation_readiness_review(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_fixture_creation_readiness_review(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_creation_readiness_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"review_id={packet['review_id']}")
    print(f"review_type={packet['review_type']}")
    print(
        "review_status="
        "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_READINESS_REVIEW_READY"
    )
    print(f"source_fixture_plan_hash={packet['source_fixture_plan_hash']}")
    print(f"review_stage={packet['review_stage']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
