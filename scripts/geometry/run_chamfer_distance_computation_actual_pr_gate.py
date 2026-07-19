"""Script: emit ChamferDistanceComputationActualPrGate.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.chamfer_distance_computation_actual_pr_gate import (
    SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_FIXTURE_CREATION_GATE_HASH,
    SOURCE_OPERATOR_DECISION_HASH,
    SOURCE_OPERATOR_DECISION_ID,
    build_chamfer_distance_computation_actual_pr_gate,
    default_authority_locks,
    default_authorized_computation_scope,
    default_authorized_fixture_manifest,
    default_blocked_scopes,
    default_computation_constraints,
    default_operator_decision_verification,
    serialize_chamfer_distance_computation_actual_pr_gate,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_DISTANCE_COMPUTATION_ACTUAL_PR_GATE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_distance_computation_actual_pr_gate_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_distance_computation_actual_pr_gate",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_distance_computation_actual_pr_gate_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    payload: dict = {
        "gate_id": "chamfer_distance_computation_actual_pr_gate_001",
        "intended_lane": "SHADOW",
        "gate_stage": "COMPUTATION_ACTUAL_PR_GATE_ONLY",
        "operator_decision_verification": default_operator_decision_verification(),
        "authorized_computation_scope": default_authorized_computation_scope(),
        "authorized_fixture_manifest": default_authorized_fixture_manifest(),
        "computation_constraints": default_computation_constraints(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": (
            "CHAMFER_DISTANCE_COMPUTATION_COMPLETE_REVIEW"
        ),
        "provenance": {
            "source": "CHAMFER_DISTANCE_COMPUTATION_ACTUAL_PR_GATE",
            "evidence_refs": [
                f"ChamferDistanceComputationAuthorizationReview.v1:{SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH}",
                f"ChamferDistanceComputationReceipt.v1:{SOURCE_COMPUTATION_RECEIPT_HASH}",
                f"OperatorDecision:{SOURCE_OPERATOR_DECISION_ID}:{SOURCE_OPERATOR_DECISION_HASH}",
                f"ChamferFixtureCreationActualPrGate.v1:{SOURCE_FIXTURE_CREATION_GATE_HASH}",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/"
                "chamfer_distance_computation_actual_pr_gate.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }

    packet = build_chamfer_distance_computation_actual_pr_gate(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_distance_computation_actual_pr_gate(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "chamfer_distance_computation_actual_pr_gate_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"gate_id={packet['gate_id']}")
    print(f"gate_type={packet['gate_type']}")
    print(f"gate_stage={packet['gate_stage']}")
    print(f"chamfer_distance_computation_authorized={al['chamfer_distance_computation_authorized']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
