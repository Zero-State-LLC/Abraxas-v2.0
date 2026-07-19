"""Script: emit THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE — three advisory-only artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.metric_operator_cross_operator_parity_receipt import (
    build_metric_operator_cross_operator_parity_receipt,
    default_governance_flags,
    default_output_contract,
    serialize_metric_operator_cross_operator_parity_receipt,
    three_operator_default_parity_dimensions,
)
from core.metric_operator_registry_stabilization import (
    build_metric_operator_registry_stabilization,
    default_governance_flags as stab_default_governance_flags,
    default_output_contract as stab_default_output_contract,
    serialize_metric_operator_registry_stabilization,
    three_operator_default_operator_entries,
)
from core.metric_operator_frontier_recommendation import (
    build_metric_operator_frontier_recommendation,
    default_governance_flags as front_default_governance_flags,
    default_output_contract as front_default_output_contract,
    serialize_metric_operator_frontier_recommendation,
    three_operator_default_ranked_options,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_001"

_PATHS = RuntimePaths.from_env()

PARITY_OUT   = _PATHS.metric_operator_cross_operator_parity_receipt_002_latest
STAB_OUT     = _PATHS.metric_operator_registry_stabilization_002_latest
FRONTIER_OUT = _PATHS.metric_operator_frontier_recommendation_002_latest

_GEODESIC_COMPLETE_HASH = (
    "def407d0ca652423b1794aad76238b6aeb4c20bb25f5cd4fce11af6dedc4a62a"
)
_BASELINE_PACK_HASH = (
    "7fd7f4fb01ec2d7a5802dda978cd08a9e954a3da816512bd7e9dafffe1aca5b8"
)

_PARITY_PAYLOAD: dict = {
    "receipt_id": "metric_operator_cross_operator_parity_receipt_002",
    "parity_status": "PARITY_CONFIRMED",
    "operators_compared": ["CHAMFER_DISTANCE", "GEODESIC", "WASSERSTEIN"],
    "parity_dimensions": three_operator_default_parity_dimensions(),
    "output_contract": default_output_contract(),
    "governance_flags": default_governance_flags(),
    "provenance": {
        "source": "THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_cross_operator_parity_receipt.v1.schema.json",
            "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
            "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
        ],
        "evidence_refs": [
            "GeodesicBaselinePromotionComplete.v1:geodesic_baseline_promotion_complete_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_001",
            "WassersteinExpectedValuesCompleteReview.v1:wasserstein_expected_values_complete_review_001",
            "ChamferExpectedValuesCompleteReview.v1:chamfer_expected_values_complete_review_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_STAB_PAYLOAD: dict = {
    "stabilization_id": "metric_operator_registry_stabilization_002",
    "title": (
        "Metric Operator Registry Stabilization — "
        "Three-operator SHADOW_STUB_ONLY parity confirmed"
    ),
    "stabilization_status": "STABLE",
    "operator_entries": three_operator_default_operator_entries(),
    "source_refs": [
        "GeodesicBaselinePromotionComplete.v1:geodesic_baseline_promotion_complete_001",
        "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
        "MetricOperatorRegistry.v1:metric_operator_registry_001",
        "WassersteinExpectedValuesCompleteReview.v1:wasserstein_expected_values_complete_review_001",
        "ChamferExpectedValuesCompleteReview.v1:chamfer_expected_values_complete_review_001",
    ],
    "output_contract": stab_default_output_contract(),
    "governance_flags": stab_default_governance_flags(),
    "provenance": {
        "source": "THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
            "contracts/canon/metric_operator_registry.v1.schema.json",
            "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
        ],
        "evidence_refs": [
            "GeodesicBaselinePromotionComplete.v1:geodesic_baseline_promotion_complete_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_FRONTIER_PAYLOAD: dict = {
    "recommendation_id": "metric_operator_frontier_recommendation_002",
    "recommendation_status": "ADVISORY_ONLY",
    "ranked_options": three_operator_default_ranked_options(),
    "recommended_next_step": "G_SEALED_PAUSE",
    "required_operator_decision": True,
    "stop_boundary_reason": (
        "Three-operator SHADOW_STUB_ONLY parity achieved "
        "(WASSERSTEIN, CHAMFER_DISTANCE, GEODESIC). "
        "No self-authorizing next step exists from SHADOW_STUB_ONLY posture. "
        "All advancement requires explicit operator instruction. "
        "Rank-4 operator selection and CPU baseline planning remain advisory-only."
    ),
    "output_contract": front_default_output_contract(),
    "governance_flags": front_default_governance_flags(),
    "provenance": {
        "source": "THREE_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_frontier_recommendation.v1.schema.json",
            "contracts/canon/metric_operator_cross_operator_parity_receipt.v1.schema.json",
            "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
        ],
        "evidence_refs": [
            "GeodesicBaselinePromotionComplete.v1:geodesic_baseline_promotion_complete_001",
            "MetricOperatorCrossOperatorParityReceipt.v1:metric_operator_cross_operator_parity_receipt_002",
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "three_operator_shadow_stub_parity_bundle",
        artifact_path=PARITY_OUT,
        context={"patch_id": PATCH_ID},
    )
    log_event(logger, "INFO", "three_operator_shadow_stub_parity_bundle_started",
              correlation_id=correlation_id)

    PARITY_OUT.parent.mkdir(parents=True, exist_ok=True)

    parity = build_metric_operator_cross_operator_parity_receipt(_PARITY_PAYLOAD)
    PARITY_OUT.write_text(
        serialize_metric_operator_cross_operator_parity_receipt(parity), encoding="utf-8"
    )
    log_event(logger, "INFO", "parity_receipt_002_emitted",
              canonical_hash=parity.get("canonical_hash", "?"), correlation_id=correlation_id)
    print(f"parity_receipt_002  canonical_hash={parity.get('canonical_hash','?')}")
    print(f"  wrote={PARITY_OUT.as_posix()}")

    stab = build_metric_operator_registry_stabilization(_STAB_PAYLOAD)
    STAB_OUT.write_text(
        serialize_metric_operator_registry_stabilization(stab), encoding="utf-8"
    )
    log_event(logger, "INFO", "registry_stabilization_002_emitted",
              canonical_hash=stab.get("canonical_hash", "?"), correlation_id=correlation_id)
    print(f"registry_stabilization_002  canonical_hash={stab.get('canonical_hash','?')}")
    print(f"  wrote={STAB_OUT.as_posix()}")

    frontier = build_metric_operator_frontier_recommendation(_FRONTIER_PAYLOAD)
    FRONTIER_OUT.write_text(
        serialize_metric_operator_frontier_recommendation(frontier), encoding="utf-8"
    )
    log_event(logger, "INFO", "frontier_recommendation_002_emitted",
              canonical_hash=frontier.get("canonical_hash", "?"), correlation_id=correlation_id)
    print(f"frontier_recommendation_002  canonical_hash={frontier.get('canonical_hash','?')}")
    print(f"  wrote={FRONTIER_OUT.as_posix()}")

    log_event(logger, "INFO", "three_operator_shadow_stub_parity_bundle_completed",
              correlation_id=correlation_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
