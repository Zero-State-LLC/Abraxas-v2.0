"""Script: emit deterministic ChamferBaselineImplementationPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chamfer_baseline_implementation_plan import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_baseline_implementation_plan,
    default_algorithm_plan,
    default_benchmark_plan,
    default_future_acceleration_seams,
    default_implementation_constraints,
    default_input_data_contract,
    default_memory_layout_plan,
    default_numerical_stability_plan,
    default_output_contract,
    default_output_data_contract,
    default_validation_plan,
    serialize_chamfer_baseline_implementation_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_BASELINE_IMPLEMENTATION_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_baseline_implementation_plan_latest

_PAYLOAD: dict = {
    "plan_id": "chamfer_baseline_implementation_plan_001",
    "source_readiness_dossier_refs": [
        "ChamferDistanceImplementationReadinessDossier.v1:"
        "chamfer_distance_implementation_readiness_dossier_001",
    ],
    "source_metric_registry_refs": [
        "MetricOperatorRegistry.v1:metric_operator_registry_001",
    ],
    "source_test_vector_pack_refs": [
        "MetricOperatorBaselineTestVectorPack.v1:"
        "metric_operator_baseline_test_vector_pack_001",
    ],
    "implementation_topology": {
        "implementation_mode": "CPU_REFERENCE_PLAN",
        "intended_lane": "SHADOW",
        "topology_stage": "BASELINE_PLAN_ONLY",
    },
    "algorithm_plan": default_algorithm_plan(),
    "numerical_stability_plan": default_numerical_stability_plan(),
    "input_data_contract": default_input_data_contract(),
    "output_data_contract": default_output_data_contract(),
    "memory_layout_plan": default_memory_layout_plan(),
    "benchmark_plan": default_benchmark_plan(),
    "future_acceleration_seams": default_future_acceleration_seams(),
    "implementation_constraints": default_implementation_constraints(),
    "validation_plan": default_validation_plan(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "CHAMFER_BASELINE_IMPLEMENTATION_PLAN_001",
        "evidence_refs": [
            "ChamferDistanceImplementationReadinessDossier.v1:"
            "chamfer_distance_implementation_readiness_dossier_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "chamfer_distance_implementation_readiness_dossier.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_baseline_implementation_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_baseline_implementation_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_chamfer_baseline_implementation_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_baseline_implementation_plan(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "chamfer_baseline_implementation_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print("plan_status=CHAMFER_BASELINE_IMPLEMENTATION_PLAN_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
