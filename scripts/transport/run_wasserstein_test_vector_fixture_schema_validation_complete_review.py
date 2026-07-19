"""Script: emit WassersteinTestVectorFixtureSchemaValidationCompleteReview.v1."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_test_vector_fixture_schema_validation_complete_review import (
    build_wasserstein_test_vector_fixture_schema_validation_complete_review,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_test_vector_fixture_schema_validation_complete_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = (
    "PATCH_P56_WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW_001"
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = (
    _PATHS.wasserstein_test_vector_fixture_schema_validation_complete_review_latest
)

_PAYLOAD: dict = {
    "review_id": (
        "wasserstein_test_vector_fixture_schema_validation_complete_review_001"
    ),
    "intended_lane": "SHADOW",
    "review_stage": "FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW_ONLY",
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "recommended_next_step": (
        "WASSERSTEIN_TEST_VECTOR_COMPUTATION_AUTHORIZATION_REVIEW"
    ),
    "provenance": {
        "source": (
            "P56_WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW"
        ),
        "evidence_refs": [
            "WassersteinTestVectorFixtureSchemaValidationExecution.v1:"
            "wasserstein_test_vector_fixture_schema_validation_execution_001",
            "WassersteinTestVectorFixtureSchemaValidationPlan.v1:"
            "wasserstein_test_vector_fixture_schema_validation_plan_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_test_vector_fixture_schema_validation_complete_review"
            ".v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_fixture_schema_validation_complete_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_schema_validation_complete_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _PAYLOAD
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_fixture_schema_validation_complete_review(
            packet
        ),
        encoding="utf-8",
    )
    al = packet["authority_locks"]
    vcs = packet["validation_completion_summary"]
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_schema_validation_complete_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"review_id={packet['review_id']}")
    print(f"review_type={packet['review_type']}")
    print(f"review_status={vcs['review_status']}")
    print(f"total_fixtures={vcs['total_fixtures']}")
    print(f"total_passed={vcs['total_passed']}")
    print(f"all_obligations_satisfied={vcs['all_obligations_satisfied']}")
    print(f"schema_validation_complete={vcs['schema_validation_complete']}")
    print(
        f"fixture_schema_validation_executed={al['fixture_schema_validation_executed']}"
    )
    print(
        f"wasserstein_computation_authorized={al['wasserstein_computation_authorized']}"
    )
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
