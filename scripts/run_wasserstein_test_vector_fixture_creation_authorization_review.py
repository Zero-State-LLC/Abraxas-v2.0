"""Script: emit WassersteinTestVectorFixtureCreationAuthorizationReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wasserstein_test_vector_fixture_creation_authorization_review import (
    build_wasserstein_test_vector_fixture_creation_authorization_review,
    default_authority_lock_review,
    default_authority_locks,
    default_authorization_recommendation,
    default_batch_review,
    default_blocked_scopes,
    default_manifest_review,
    default_operator_authorization_requirement,
    serialize_wasserstein_test_vector_fixture_creation_authorization_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = (
    "PATCH_P50_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_AUTHORIZATION_REVIEW_001"
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = (
    _PATHS.wasserstein_test_vector_fixture_creation_authorization_review_latest
)

_PAYLOAD: dict = {
    "authorization_review_id": (
        "wasserstein_test_vector_fixture_creation_authorization_review_001"
    ),
    "intended_lane": "SHADOW",
    "review_stage": "FIXTURE_CREATION_AUTHORIZATION_REVIEW_ONLY",
    "manifest_review": default_manifest_review(),
    "batch_review": default_batch_review(),
    "authority_lock_review": default_authority_lock_review(),
    "operator_authorization_requirement": default_operator_authorization_requirement(),
    "authorization_recommendation": default_authorization_recommendation(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "recommended_next_step": (
        "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_OPERATOR_DECISION"
    ),
    "provenance": {
        "source": "P50_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_AUTHORIZATION_REVIEW",
        "evidence_refs": [
            "WassersteinTestVectorFixtureCreationPRPlan.v1:"
            "wasserstein_test_vector_fixture_creation_pr_plan_001",
            "WassersteinTestVectorFixtureCreationReadinessReview.v1:"
            "wasserstein_test_vector_fixture_creation_readiness_review_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_test_vector_fixture_creation_authorization_review"
            ".v1.schema.json",
            "contracts/canon/"
            "wasserstein_test_vector_fixture_creation_pr_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_fixture_creation_authorization_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_creation_authorization_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_test_vector_fixture_creation_authorization_review(
        _PAYLOAD
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_fixture_creation_authorization_review(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_creation_authorization_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"authorization_review_id={packet['authorization_review_id']}")
    print(f"review_type={packet['review_type']}")
    print(
        "review_status="
        "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_AUTHORIZATION_REVIEW_READY"
    )
    print(f"source_pr_plan_hash={packet['source_pr_plan_hash']}")
    print(f"review_stage={packet['review_stage']}")
    rec = packet["authorization_recommendation"]
    print(
        f"authorization_recommendation="
        f"authorize={rec['authorize_fixture_file_creation']},"
        f"authorized={rec['fixture_file_creation_authorized']},"
        f"status={rec['recommendation_status']}"
    )
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
