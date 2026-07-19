"""Script: emit WassersteinTestVectorFixtureCreationPRPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_test_vector_fixture_creation_pr_plan import (
    build_wasserstein_test_vector_fixture_creation_pr_plan,
    default_authority_locks,
    default_blocked_scopes,
    default_fixture_creation_batches,
    default_proposed_fixture_file_manifest,
    default_review_requirements,
    default_validation_plan,
    serialize_wasserstein_test_vector_fixture_creation_pr_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_P49_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_PR_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_test_vector_fixture_creation_pr_plan_latest

_PAYLOAD: dict = {
    "pr_plan_id": "wasserstein_test_vector_fixture_creation_pr_plan_001",
    "intended_lane": "SHADOW",
    "pr_plan_stage": "FIXTURE_CREATION_PR_PLAN_ONLY",
    "proposed_fixture_file_manifest": default_proposed_fixture_file_manifest(),
    "fixture_creation_batches": default_fixture_creation_batches(),
    "validation_plan": default_validation_plan(),
    "review_requirements": default_review_requirements(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "recommended_next_step": (
        "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_AUTHORIZATION_REVIEW"
    ),
    "provenance": {
        "source": "P49_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_PR_PLAN",
        "evidence_refs": [
            "WassersteinTestVectorFixtureCreationReadinessReview.v1:"
            "wasserstein_test_vector_fixture_creation_readiness_review_001",
            "WassersteinTestVectorFixturePlan.v1:"
            "wasserstein_test_vector_fixture_plan_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_test_vector_fixture_creation_pr_plan.v1.schema.json",
            "contracts/canon/"
            "wasserstein_test_vector_fixture_creation_readiness_review.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_fixture_creation_pr_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_creation_pr_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_fixture_creation_pr_plan(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_creation_pr_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"pr_plan_id={packet['pr_plan_id']}")
    print(f"pr_plan_type={packet['pr_plan_type']}")
    print("pr_plan_status=WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_PR_PLAN_DEFINED")
    print(f"source_readiness_review_hash={packet['source_readiness_review_hash']}")
    print(f"pr_plan_stage={packet['pr_plan_stage']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
