"""Script: emit deterministic ChamferExpectedDistanceValuesActualPRGate.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.chamfer_expected_distance_values_actual_pr_gate import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_expected_distance_values_actual_pr_gate,
    default_blocker_findings,
    default_eligible_value_fixture_refs,
    default_expected_value_authorization_state,
    default_null_locked_fixture_refs,
    default_output_contract,
    default_tolerance_authorization_state,
    default_value_creation_constraints,
    default_validation_plan,
    serialize_chamfer_expected_distance_values_actual_pr_gate,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_EXPECTED_DISTANCE_VALUES_ACTUAL_PR_GATE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_expected_distance_values_actual_pr_gate_latest

_PAYLOAD: dict = {
    "gate_id": "chamfer_expected_distance_values_actual_pr_gate_001",
    "gate_scope": {
        "gate_family": "EXPECTED_DISTANCE_VALUE_ACTUAL_PR_GATE",
        "intended_lane": "SHADOW",
        "gate_stage": "GATE_ONLY",
    },
    "expected_value_authorization_state": default_expected_value_authorization_state(),
    "tolerance_authorization_state": default_tolerance_authorization_state(),
    "value_creation_constraints": default_value_creation_constraints(),
    "validation_plan": default_validation_plan(),
    "output_contract": default_output_contract(),
    "eligible_value_fixture_refs": default_eligible_value_fixture_refs(),
    "null_locked_fixture_refs": default_null_locked_fixture_refs(),
    "blocker_findings": default_blocker_findings(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "CHAMFER_EXPECTED_DISTANCE_VALUES_ACTUAL_PR_GATE_001",
        "evidence_refs": [
            "ChamferExpectedDistanceValuePlan.v1:"
            "chamfer_expected_distance_value_plan_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "chamfer_expected_distance_values_actual_pr_gate.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_expected_distance_values_actual_pr_gate",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_expected_distance_values_actual_pr_gate_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_chamfer_expected_distance_values_actual_pr_gate(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_expected_distance_values_actual_pr_gate(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "chamfer_expected_distance_values_actual_pr_gate_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"gate_id={packet['gate_id']}")
    print(f"gate_type={packet['gate_type']}")
    print("gate_status=CHAMFER_EXPECTED_DISTANCE_VALUES_ACTUAL_PR_GATE_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
