"""Script: emit deterministic MetricOperatorBaselineTestVectorPack.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.metric_operator_baseline_test_vector_pack import (
    build_metric_operator_baseline_test_vector_pack,
    default_governance_flags,
    default_invalid_vectors,
    default_operator_vectors,
    default_output_contract,
    default_validation_policy,
    serialize_metric_operator_baseline_test_vector_pack,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_NORM_GEOMETRY_SHADOW_STUB_BASELINE_PACK_UPDATE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.metric_operator_baseline_test_vector_pack_latest

_PAYLOAD: dict = {
    "pack_id": "metric_operator_baseline_test_vector_pack_001",
    "source_metric_registry_refs": [
        "MetricOperatorRegistry.v1:metric_operator_registry_001",
    ],
    "operator_vectors": default_operator_vectors(),
    "invalid_vectors": default_invalid_vectors(),
    "validation_policy": default_validation_policy(),
    "output_contract": default_output_contract(),
    "governance_flags": default_governance_flags(),
    "provenance": {
        "source": "NORM_GEOMETRY_SHADOW_STUB_BASELINE_PACK_UPDATE",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
            "contracts/canon/metric_operator_registry.v1.schema.json",
        ],
        "evidence_refs": [
            "ChamferExpectedValuesCompleteReview.v1:chamfer_expected_values_complete_review_001",
            "GeodesicBaselinePromotionDecision:GEODESIC_BASELINE_PROMOTION_DECISION_2026_05_29_001",
            "GeodesicComputationOperatorClosure.v1:geodesic_computation_operator_closure_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
            "NormGeometryBaselinePromotionDecision:NORM_GEOMETRY_BASELINE_PROMOTION_DECISION_2026_05_29_001",
            "NormGeometryBaselinePromotionGate.v1:norm_geometry_baseline_promotion_gate_001",
            "NormGeometryComputationOperatorClosure.v1:norm_geometry_computation_operator_closure_001",
            "WassersteinExpectedValuesCompleteReview.v1:wasserstein_expected_values_complete_review_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "metric_operator_baseline_test_vector_pack",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "metric_operator_baseline_test_vector_pack_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_metric_operator_baseline_test_vector_pack(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_metric_operator_baseline_test_vector_pack(packet), encoding="utf-8"
    )

    log_event(
        logger,
        "INFO",
        "metric_operator_baseline_test_vector_pack_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"pack_id={packet['pack_id']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
