"""Script: emit deterministic ChamferExpectedDistancePolicyPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chamfer_expected_distance_policy_plan import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_expected_distance_policy_plan,
    default_expected_distance_policy_groups,
    default_not_computable_distance_policy,
    default_output_contract,
    default_policy_constraints,
    default_review_gate_plan,
    default_tolerance_policy_plan,
    serialize_chamfer_expected_distance_policy_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_EXPECTED_DISTANCE_POLICY_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_expected_distance_policy_plan_latest

_PAYLOAD: dict = {
    "plan_id": "chamfer_expected_distance_policy_plan_001",
    "source_fixture_readiness_review_refs": [
        "ChamferFixtureImplementationReadinessReview.v1:"
        "chamfer_fixture_implementation_readiness_review_001",
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
    "source_baseline_implementation_plan_refs": [
        "ChamferBaselineImplementationPlan.v1:chamfer_baseline_implementation_plan_001",
    ],
    "policy_scope": {
        "policy_family": "EXPECTED_DISTANCE_POLICY",
        "intended_lane": "SHADOW",
        "policy_stage": "POLICY_PLAN_ONLY",
    },
    "expected_distance_policy_groups": default_expected_distance_policy_groups(),
    "tolerance_policy_plan": default_tolerance_policy_plan(),
    "not_computable_distance_policy": default_not_computable_distance_policy(),
    "review_gate_plan": default_review_gate_plan(),
    "policy_constraints": default_policy_constraints(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "CHAMFER_EXPECTED_DISTANCE_POLICY_PLAN_001",
        "evidence_refs": [
            "ChamferFixtureImplementationReadinessReview.v1:"
            "chamfer_fixture_implementation_readiness_review_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/chamfer_expected_distance_policy_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_expected_distance_policy_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_expected_distance_policy_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_chamfer_expected_distance_policy_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_expected_distance_policy_plan(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "chamfer_expected_distance_policy_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print("plan_status=CHAMFER_EXPECTED_DISTANCE_POLICY_PLAN_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
