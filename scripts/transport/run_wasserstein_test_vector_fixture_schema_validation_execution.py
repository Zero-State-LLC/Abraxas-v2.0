"""Script: emit WassersteinTestVectorFixtureSchemaValidationExecution.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_test_vector_fixture_schema_validation_execution import (
    build_wasserstein_test_vector_fixture_schema_validation_execution,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_test_vector_fixture_schema_validation_execution,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = (
    "PATCH_P55_WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_EXECUTION_001"
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_test_vector_fixture_schema_validation_execution_latest

_PAYLOAD: dict = {
    "execution_id": (
        "wasserstein_test_vector_fixture_schema_validation_execution_001"
    ),
    "intended_lane": "SHADOW",
    "execution_stage": "FIXTURE_SCHEMA_VALIDATION_EXECUTION_ONLY",
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "recommended_next_step": (
        "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW"
    ),
    "provenance": {
        "source": (
            "P55_WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_EXECUTION"
        ),
        "evidence_refs": [
            "WassersteinTestVectorFixtureSchemaValidationPlan.v1:"
            "wasserstein_test_vector_fixture_schema_validation_plan_001",
            "WassersteinTestVectorFixtureFileCreationCompleteReview.v1:"
            "wasserstein_test_vector_fixture_file_creation_complete_review_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_test_vector_fixture_schema_validation_execution"
            ".v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_fixture_schema_validation_execution",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_schema_validation_execution_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _PAYLOAD
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_fixture_schema_validation_execution(packet),
        encoding="utf-8",
    )
    al = packet["authority_locks"]
    summary = packet["validation_summary"]
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_schema_validation_execution_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"execution_id={packet['execution_id']}")
    print(f"execution_type={packet['execution_type']}")
    print(f"execution_status={summary['execution_status']}")
    print(f"total_fixtures={summary['total_fixtures']}")
    print(f"passed={summary['passed']}")
    print(f"failed={summary['failed']}")
    print(f"valid_passed={summary['valid_passed']}")
    print(f"invalid_passed={summary['invalid_passed']}")
    print(f"not_computable_passed={summary['not_computable_passed']}")
    print(f"all_checks_passed={summary['all_checks_passed']}")
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
