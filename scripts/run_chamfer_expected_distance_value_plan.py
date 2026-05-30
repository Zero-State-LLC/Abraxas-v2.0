"""Script: emit deterministic ChamferExpectedDistanceValuePlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chamfer_expected_distance_value_plan import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_expected_distance_value_plan,
    default_not_computable_value_policy,
    default_output_contract,
    default_planned_tolerance_policy,
    default_planned_value_groups,
    default_validation_plan,
    default_value_constraints,
    serialize_chamfer_expected_distance_value_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_EXPECTED_DISTANCE_VALUE_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_expected_distance_value_plan_latest

_PAYLOAD: dict = {
    "plan_id": "chamfer_expected_distance_value_plan_001",
    "source_fixture_manifest_refs": [
        "ChamferFixtureManifest.v1:chamfer_fixture_manifest_v1",
    ],
    "source_fixture_archive_receipt_refs": [
        "ChamferFixtureCreationActualPRGate.v1:"
        "chamfer_fixture_creation_actual_pr_gate_001",
    ],
    "source_expected_distance_policy_plan_refs": [
        "ChamferExpectedDistancePolicyPlan.v1:"
        "chamfer_expected_distance_policy_plan_001",
    ],
    "source_fixture_files_refs": [
        "input/fixtures/chamfer/chamfer_fixture_manifest.v1.json",
    ],
    "value_plan_scope": {
        "plan_family": "EXPECTED_DISTANCE_VALUE_PLAN",
        "intended_lane": "SHADOW",
        "plan_stage": "IMPLEMENTATION_PLAN_ONLY",
    },
    "planned_value_groups": default_planned_value_groups(),
    "planned_tolerance_policy": default_planned_tolerance_policy(),
    "not_computable_value_policy": default_not_computable_value_policy(),
    "validation_plan": default_validation_plan(),
    "value_constraints": default_value_constraints(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "CHAMFER_EXPECTED_DISTANCE_VALUE_PLAN_001",
        "evidence_refs": [
            "ChamferFixtureCreationActualPRGate.v1:"
            "chamfer_fixture_creation_actual_pr_gate_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/chamfer_expected_distance_value_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_expected_distance_value_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_expected_distance_value_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_chamfer_expected_distance_value_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_expected_distance_value_plan(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "chamfer_expected_distance_value_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print("plan_status=CHAMFER_EXPECTED_DISTANCE_VALUE_PLAN_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
