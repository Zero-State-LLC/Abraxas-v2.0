"""Script: emit WassersteinTestVectorFixtureSchemaValidationPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_test_vector_fixture_schema_validation_plan import (
    build_wasserstein_test_vector_fixture_schema_validation_plan,
    default_authority_lock_scan_plan,
    default_authority_locks,
    default_blocked_scopes,
    default_fixture_schema_validation_scope,
    default_invalid_fixture_validation_plan,
    default_no_expected_distance_scan_plan,
    default_no_metric_value_scan_plan,
    default_not_computable_fixture_validation_plan,
    default_valid_fixture_validation_plan,
    serialize_wasserstein_test_vector_fixture_schema_validation_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = (
    "PATCH_P54_WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_PLAN_001"
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_test_vector_fixture_schema_validation_plan_latest

_PAYLOAD: dict = {
    "validation_plan_id": (
        "wasserstein_test_vector_fixture_schema_validation_plan_001"
    ),
    "intended_lane": "SHADOW",
    "validation_stage": "FIXTURE_SCHEMA_VALIDATION_PLAN_ONLY",
    "fixture_schema_validation_scope": default_fixture_schema_validation_scope(),
    "valid_fixture_validation_plan": default_valid_fixture_validation_plan(),
    "invalid_fixture_validation_plan": default_invalid_fixture_validation_plan(),
    "not_computable_fixture_validation_plan": (
        default_not_computable_fixture_validation_plan()
    ),
    "no_metric_value_scan_plan": default_no_metric_value_scan_plan(),
    "no_expected_distance_scan_plan": default_no_expected_distance_scan_plan(),
    "authority_lock_scan_plan": default_authority_lock_scan_plan(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "recommended_next_step": (
        "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_EXECUTION"
    ),
    "provenance": {
        "source": (
            "P54_WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_PLAN"
        ),
        "evidence_refs": [
            "WassersteinTestVectorFixtureFileCreationCompleteReview.v1:"
            "wasserstein_test_vector_fixture_file_creation_complete_review_001",
            "WassersteinTestVectorFixtureFileCreationReceipt.v1:"
            "wasserstein_test_vector_fixture_file_creation_receipt_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_test_vector_fixture_schema_validation_plan"
            ".v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_fixture_schema_validation_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_schema_validation_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_fixture_schema_validation_plan(packet),
        encoding="utf-8",
    )
    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_schema_validation_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"validation_plan_id={packet['validation_plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print(
        "plan_status="
        "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_PLAN_DEFINED"
    )
    scope = packet["fixture_schema_validation_scope"]
    print(f"total_fixtures_in_scope={scope['total_fixtures']}")
    print(f"valid_plan_entries={len(packet['valid_fixture_validation_plan'])}")
    print(f"invalid_plan_entries={len(packet['invalid_fixture_validation_plan'])}")
    print(
        "not_computable_plan_entries="
        f"{len(packet['not_computable_fixture_validation_plan'])}"
    )
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
