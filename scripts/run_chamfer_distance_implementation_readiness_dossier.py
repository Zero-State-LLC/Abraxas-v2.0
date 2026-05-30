"""Script: emit deterministic ChamferDistanceImplementationReadinessDossier.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chamfer_distance_implementation_readiness_dossier import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_distance_implementation_readiness_dossier,
    default_output_contract,
    serialize_chamfer_distance_implementation_readiness_dossier,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_distance_implementation_readiness_dossier_latest

_PAYLOAD: dict = {
    "dossier_id": "chamfer_distance_implementation_readiness_dossier_001",
    "implementation_scope": {
        "mode": "CPU_REFERENCE_ONLY",
        "planning_lane": "BATCH_F1",
        "readiness_status": "PLANNING_ONLY",
    },
    "implementation_prerequisites": [
        {
            "prerequisite_id": "prereq-001",
            "status": "REQUIRED",
            "description": "Reference vectors and deterministic fixtures established.",
            "evidence_refs": [
                "MetricOperatorBaselineTestVectorPack.v1:"
                "metric_operator_baseline_test_vector_pack_001",
            ],
        }
    ],
    "dependency_inventory": [
        {
            "dependency_id": "dep-001",
            "dependency_type": "TEST_VECTOR",
            "description": "CHAMFER_DISTANCE baseline vector packet references.",
            "required": True,
            "evidence_refs": [
                "MetricOperatorBaselineTestVectorPack.v1:"
                "metric_operator_baseline_test_vector_pack_001",
            ],
        }
    ],
    "numerical_constraints": [
        "No floating-point kernel execution in this lane.",
        "Hash and serialization determinism required.",
    ],
    "validation_strategy": [
        {
            "strategy_id": "val-001",
            "validation_type": "DETERMINISTIC_REPLAY",
            "description": "Replay dossier generation with stable hash equivalence.",
            "evidence_refs": [
                "tests/test_chamfer_distance_implementation_readiness_dossier.py",
            ],
        }
    ],
    "implementation_risks": [
        {
            "risk_id": "risk-001",
            "risk_level": "MEDIUM",
            "description": (
                "Future kernel implementation could drift from planning constraints."
            ),
            "mitigation": "Keep advisory lock checks fail-closed.",
            "evidence_refs": [
                "contracts/canon/"
                "chamfer_distance_implementation_readiness_dossier.v1.schema.json",
            ],
        }
    ],
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "CHAMFER_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER_001",
        "evidence_refs": [
            "MetricOperatorImplementationSelectionPlan.v1:"
            "metric_operator_implementation_selection_plan_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "metric_operator_implementation_selection_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_distance_implementation_readiness_dossier",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_distance_implementation_readiness_dossier_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_chamfer_distance_implementation_readiness_dossier(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_distance_implementation_readiness_dossier(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "chamfer_distance_implementation_readiness_dossier_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"dossier_id={packet['dossier_id']}")
    print(f"dossier_type={packet['dossier_type']}")
    print("dossier_status=CHAMFER_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
