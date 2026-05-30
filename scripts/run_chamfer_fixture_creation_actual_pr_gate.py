"""Script: emit deterministic ChamferFixtureCreationActualPRGate.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chamfer_fixture_creation_actual_pr_gate import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_fixture_creation_actual_pr_gate,
    default_blockers,
    default_fixture_batches,
    default_gate_constraints,
    default_output_contract,
    default_proposed_fixture_directories,
    default_source_refs,
    default_validation_requirements,
    serialize_chamfer_fixture_creation_actual_pr_gate,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_FIXTURE_CREATION_ACTUAL_PR_GATE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_fixture_creation_actual_pr_gate_latest

_PAYLOAD: dict = {
    "gate_id": "chamfer_fixture_creation_actual_pr_gate_001",
    "gate_scope": {
        "intended_lane": "SHADOW",
        "gate_stage": "ACTUAL_PR_GATE_ONLY",
    },
    "proposed_manifest_path": (
        "input/fixtures/chamfer/chamfer_fixture_manifest.v1.json"
    ),
    "required_future_pr_name": "CHAMFER_FIXTURE_FILES_ACTUAL_PR_V1",
    "required_operator_approval_state": "EXPLICIT_OPERATOR_APPROVAL_REQUIRED",
    "stop_rule": (
        "Stop unless explicit operator approval is recorded for fixture creation."
    ),
    "authority_state": "ADVISORY_ONLY",
    "source_refs": default_source_refs(),
    "proposed_fixture_directories": default_proposed_fixture_directories(),
    "fixture_batches": default_fixture_batches(),
    "blockers": default_blockers(),
    "validation_requirements": default_validation_requirements(),
    "gate_constraints": default_gate_constraints(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "CHAMFER_FIXTURE_CREATION_ACTUAL_PR_GATE_001",
        "evidence_refs": [
            "ChamferFixtureCreationPRPlan.v1:"
            "chamfer_fixture_creation_pr_plan_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "chamfer_fixture_creation_actual_pr_gate.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_fixture_creation_actual_pr_gate",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_fixture_creation_actual_pr_gate_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_chamfer_fixture_creation_actual_pr_gate(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_fixture_creation_actual_pr_gate(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "chamfer_fixture_creation_actual_pr_gate_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"gate_id={packet['gate_id']}")
    print(f"gate_type={packet['gate_type']}")
    print("gate_status=CHAMFER_FIXTURE_CREATION_ACTUAL_PR_GATE_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
