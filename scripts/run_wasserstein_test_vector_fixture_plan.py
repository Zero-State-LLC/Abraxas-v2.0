"""Script: emit deterministic WassersteinTestVectorFixturePlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wasserstein_test_vector_fixture_plan import (
    build_wasserstein_test_vector_fixture_plan,
    default_authority_locks,
    default_blocked_scopes,
    default_determinism_requirements,
    default_invalid_fixture_plan,
    default_not_computable_fixture_plan,
    default_numerical_policy_requirements,
    default_valid_fixture_plan,
    serialize_wasserstein_test_vector_fixture_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_P47_WASSERSTEIN_TEST_VECTOR_FIXTURE_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_test_vector_fixture_plan_latest

_PAYLOAD: dict = {
    "fixture_plan_id": "wasserstein_test_vector_fixture_plan_001",
    "intended_lane": "SHADOW",
    "fixture_stage": "FIXTURE_PLAN_ONLY",
    "valid_fixture_plan": default_valid_fixture_plan(),
    "invalid_fixture_plan": default_invalid_fixture_plan(),
    "not_computable_fixture_plan": default_not_computable_fixture_plan(),
    "determinism_requirements": default_determinism_requirements(),
    "numerical_policy_requirements": default_numerical_policy_requirements(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "recommended_next_step": (
        "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_READINESS_REVIEW"
    ),
    "provenance": {
        "source": "P47_WASSERSTEIN_TEST_VECTOR_FIXTURE_PLAN",
        "evidence_refs": [
            "WassersteinTestVectorSchemaPlan.v1:"
            "wasserstein_test_vector_schema_plan_001",
            "WassersteinFixturePlanConsolidationReceipt.v1:"
            "wasserstein_fixture_plan_consolidation_receipt_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/wasserstein_test_vector_fixture_plan.v1.schema.json",
            "contracts/canon/wasserstein_test_vector_schema_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_fixture_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_test_vector_fixture_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_fixture_plan(packet), encoding="utf-8"
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"fixture_plan_id={packet['fixture_plan_id']}")
    print(f"fixture_plan_type={packet['fixture_plan_type']}")
    print("plan_status=WASSERSTEIN_TEST_VECTOR_FIXTURE_PLAN_DEFINED")
    print(f"source_schema_plan_hash={packet['source_schema_plan_hash']}")
    print(f"fixture_stage={packet['fixture_stage']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
