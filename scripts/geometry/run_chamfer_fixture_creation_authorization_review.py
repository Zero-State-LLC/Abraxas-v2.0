"""Script: emit deterministic ChamferFixtureCreationAuthorizationReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.chamfer_fixture_creation_authorization_review import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_fixture_creation_authorization_review,
    default_authorization_decision,
    default_authorization_findings,
    default_blocker_findings,
    default_creation_constraints,
    default_output_contract,
    serialize_chamfer_fixture_creation_authorization_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_FIXTURE_CREATION_AUTHORIZATION_REVIEW_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_fixture_creation_authorization_review_latest

_PAYLOAD: dict = {
    "review_id": "chamfer_fixture_creation_authorization_review_001",
    "source_fixture_readiness_review_refs": [
        "ChamferFixtureImplementationReadinessReview.v1:"
        "chamfer_fixture_implementation_readiness_review_001",
    ],
    "source_expected_distance_policy_plan_refs": [
        "ChamferExpectedDistancePolicyPlan.v1:"
        "chamfer_expected_distance_policy_plan_001",
    ],
    "source_fixture_consolidation_receipt_refs": [
        "ChamferFixturePlanConsolidationReceipt.v1:"
        "chamfer_fixture_plan_consolidation_receipt_001",
    ],
    "source_valid_fixture_plan_refs": [
        "ChamferValidFixtureImplementationPlan.v1:"
        "chamfer_valid_fixture_implementation_plan_001",
    ],
    "source_invalid_fixture_plan_refs": [
        "ChamferInvalidFixtureImplementationPlan.v1:"
        "chamfer_invalid_fixture_implementation_plan_001",
    ],
    "source_not_computable_fixture_plan_refs": [
        "ChamferNotComputableFixtureImplementationPlan.v1:"
        "chamfer_not_computable_fixture_implementation_plan_001",
    ],
    "source_schema_plan_refs": [
        "ChamferTestVectorSchemaPlan.v1:chamfer_test_vector_schema_plan_001",
    ],
    "source_baseline_implementation_plan_refs": [
        "ChamferBaselineImplementationPlan.v1:chamfer_baseline_implementation_plan_001",
    ],
    "authorization_scope": {
        "authorization_family": "FIXTURE_CREATION_AUTHORIZATION_REVIEW",
        "intended_lane": "SHADOW",
        "authorization_stage": "AUTHORIZATION_REVIEW_ONLY",
    },
    "authorization_findings": default_authorization_findings(),
    "blocker_findings": default_blocker_findings(),
    "authorization_decision": default_authorization_decision(),
    "creation_constraints": default_creation_constraints(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "CHAMFER_FIXTURE_CREATION_AUTHORIZATION_REVIEW_001",
        "evidence_refs": [
            "ChamferExpectedDistancePolicyPlan.v1:"
            "chamfer_expected_distance_policy_plan_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "chamfer_fixture_creation_authorization_review.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_fixture_creation_authorization_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_fixture_creation_authorization_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_chamfer_fixture_creation_authorization_review(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_fixture_creation_authorization_review(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "chamfer_fixture_creation_authorization_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"review_id={packet['review_id']}")
    print(f"review_type={packet['review_type']}")
    print("review_status=CHAMFER_FIXTURE_CREATION_AUTHORIZATION_REVIEW_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
