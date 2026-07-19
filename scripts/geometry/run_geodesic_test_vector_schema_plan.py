"""Script: emit deterministic GeodesicTestVectorSchemaPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.geodesic_test_vector_schema_plan import (
    LOCKED_FALSE_FLAGS,
    build_geodesic_test_vector_schema_plan,
    default_invalid_schema_groups,
    default_not_computable_schema_groups,
    default_output_contract,
    default_schema_constraints,
    default_schema_layout_plan,
    default_valid_schema_groups,
    default_validation_plan,
    serialize_geodesic_test_vector_schema_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_GEODESIC_TEST_VECTOR_SCHEMA_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.geodesic_test_vector_schema_plan_latest

_PAYLOAD: dict = {
    "plan_id": "geodesic_test_vector_schema_plan_001",
    "source_dossier_refs": [
        "GeodesicDistanceImplementationReadinessDossier.v1:"
        "geodesic_distance_implementation_readiness_dossier_001",
    ],
    "source_metric_registry_refs": [
        "MetricOperatorRegistry.v1:metric_operator_registry_001",
    ],
    "source_baseline_vector_pack_refs": [
        "MetricOperatorBaselineTestVectorPack.v1:"
        "metric_operator_baseline_test_vector_pack_001",
    ],
    "schema_scope": {
        "schema_family": "MIXED_SCHEMA_PLAN",
        "intended_lane": "SHADOW",
        "schema_stage": "SCHEMA_PLAN_ONLY",
    },
    "valid_schema_groups": default_valid_schema_groups(),
    "invalid_schema_groups": default_invalid_schema_groups(),
    "not_computable_schema_groups": default_not_computable_schema_groups(),
    "schema_layout_plan": default_schema_layout_plan(),
    "schema_constraints": default_schema_constraints(),
    "validation_plan": default_validation_plan(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "GEODESIC_TEST_VECTOR_SCHEMA_PLAN_001",
        "evidence_refs": [
            "GeodesicDistanceImplementationReadinessDossier.v1:"
            "geodesic_distance_implementation_readiness_dossier_001",
            "MetricOperatorRank3SelectionPlan.v1:"
            "metric_operator_rank3_selection_plan_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
            "MetricOperatorBaselineTestVectorPack.v1:"
            "metric_operator_baseline_test_vector_pack_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "geodesic_test_vector_schema_plan.v1.schema.json",
            "contracts/canon/"
            "geodesic_distance_implementation_readiness_dossier.v1.schema.json",
            "contracts/canon/"
            "metric_operator_rank3_selection_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "geodesic_test_vector_schema_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "geodesic_test_vector_schema_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_geodesic_test_vector_schema_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_geodesic_test_vector_schema_plan(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "geodesic_test_vector_schema_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print(f"operator_id={packet['operator_id']}")
    print(f"valid_groups={len(packet['valid_schema_groups'])}")
    print(f"invalid_groups={len(packet['invalid_schema_groups'])}")
    print(f"not_computable_groups={len(packet['not_computable_schema_groups'])}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
