"""Script: emit deterministic ChamferNotComputableFixtureImplementationPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.chamfer_not_computable_fixture_implementation_plan import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_not_computable_fixture_implementation_plan,
    default_deterministic_ordering_plan,
    default_fixture_constraints,
    default_not_computable_fixture_cases,
    default_not_computable_policy_plan,
    default_output_contract,
    default_validation_plan,
    serialize_chamfer_not_computable_fixture_implementation_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_NOT_COMPUTABLE_FIXTURE_IMPLEMENTATION_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_not_computable_fixture_implementation_plan_latest

_PAYLOAD: dict = {
    "plan_id": "chamfer_not_computable_fixture_implementation_plan_001",
    "source_fixture_plan_refs": [
        "ChamferBaselineImplementationPlan.v1:chamfer_baseline_implementation_plan_001",
    ],
    "source_schema_plan_refs": [
        "ChamferTestVectorSchemaPlan.v1:chamfer_test_vector_schema_plan_001",
    ],
    "source_valid_fixture_plan_refs": [
        "ChamferValidFixtureImplementationPlan.v1:"
        "chamfer_valid_fixture_implementation_plan_001",
    ],
    "source_invalid_fixture_plan_refs": [
        "ChamferInvalidFixtureImplementationPlan.v1:"
        "chamfer_invalid_fixture_implementation_plan_001",
    ],
    "source_baseline_implementation_plan_refs": [
        "ChamferBaselineImplementationPlan.v1:chamfer_baseline_implementation_plan_001",
    ],
    "not_computable_fixture_scope": {
        "fixture_family": "MIXED_NOT_COMPUTABLE_FIXTURE_PLAN",
        "intended_lane": "SHADOW",
        "implementation_stage": "IMPLEMENTATION_PLAN_ONLY",
    },
    "not_computable_fixture_cases": default_not_computable_fixture_cases(),
    "not_computable_policy_plan": default_not_computable_policy_plan(),
    "deterministic_ordering_plan": default_deterministic_ordering_plan(),
    "validation_plan": default_validation_plan(),
    "fixture_constraints": default_fixture_constraints(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "CHAMFER_NOT_COMPUTABLE_FIXTURE_IMPLEMENTATION_PLAN_001",
        "evidence_refs": [
            "ChamferInvalidFixtureImplementationPlan.v1:"
            "chamfer_invalid_fixture_implementation_plan_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "chamfer_not_computable_fixture_implementation_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_not_computable_fixture_implementation_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_not_computable_fixture_implementation_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_chamfer_not_computable_fixture_implementation_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_not_computable_fixture_implementation_plan(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "chamfer_not_computable_fixture_implementation_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print("plan_status=CHAMFER_NOT_COMPUTABLE_FIXTURE_IMPLEMENTATION_PLAN_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
