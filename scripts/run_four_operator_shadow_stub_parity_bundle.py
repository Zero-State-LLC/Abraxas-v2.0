"""Script: emit FOUR_OPERATOR_SHADOW_STUB_PARITY_BUNDLE — three advisory-only artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.metric_operator_cross_operator_parity_receipt import (
    build_metric_operator_cross_operator_parity_receipt,
    default_governance_flags,
    default_output_contract,
    four_operator_default_parity_dimensions,
    serialize_metric_operator_cross_operator_parity_receipt,
)
from core.metric_operator_registry_stabilization import (
    build_metric_operator_registry_stabilization,
    default_governance_flags as stab_default_governance_flags,
    default_output_contract as stab_default_output_contract,
    four_operator_default_operator_entries,
    serialize_metric_operator_registry_stabilization,
)
from core.metric_operator_frontier_recommendation import (
    build_metric_operator_frontier_recommendation,
    default_governance_flags as front_default_governance_flags,
    default_output_contract as front_default_output_contract,
    four_operator_post_norm_geometry_ranked_options,
    serialize_metric_operator_frontier_recommendation,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "FOUR_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_001"

_PATHS = RuntimePaths.from_env()

PARITY_OUT   = _PATHS.metric_operator_cross_operator_parity_receipt_003_latest
STAB_OUT     = _PATHS.metric_operator_registry_stabilization_003_latest
FRONTIER_OUT = _PATHS.metric_operator_frontier_recommendation_005_latest

_NORM_GEOMETRY_COMPLETE_HASH = (
    "c82a211cb6e8618bb78930327340df7abf0569e4b8e738f824ee98eb8f2f36d1"
)
_BASELINE_PACK_HASH = (
    "bd58de7fd9597729aa92b51471698be3af5eddb7dcff07ae230b014273611e59"
)

_PARITY_PAYLOAD: dict = {
    "receipt_id": "metric_operator_cross_operator_parity_receipt_003",
    "parity_status": "PARITY_CONFIRMED",
    "operators_compared": [
        "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "WASSERSTEIN",
    ],
    "parity_dimensions": four_operator_default_parity_dimensions(),
    "output_contract": default_output_contract(),
    "governance_flags": default_governance_flags(),
    "provenance": {
        "source": "FOUR_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_cross_operator_parity_receipt.v1.schema.json",
            "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
            "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
        ],
        "evidence_refs": [
            "NormGeometryBaselinePromotionComplete.v1:norm_geometry_baseline_promotion_complete_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
            "MetricOperatorCrossOperatorParityReceipt.v1:metric_operator_cross_operator_parity_receipt_002",
            "GeodesicBaselinePromotionComplete.v1:geodesic_baseline_promotion_complete_001",
            "WassersteinExpectedValuesCompleteReview.v1:wasserstein_expected_values_complete_review_001",
            "ChamferExpectedValuesCompleteReview.v1:chamfer_expected_values_complete_review_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_STAB_PAYLOAD: dict = {
    "stabilization_id": "metric_operator_registry_stabilization_003",
    "title": (
        "Metric Operator Registry Stabilization — "
        "Four-operator SHADOW_STUB_ONLY parity confirmed"
    ),
    "stabilization_status": "STABLE",
    "operator_entries": four_operator_default_operator_entries(),
    "source_refs": [
        "NormGeometryBaselinePromotionComplete.v1:norm_geometry_baseline_promotion_complete_001",
        "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
        "MetricOperatorRegistry.v1:metric_operator_registry_001",
        "GeodesicBaselinePromotionComplete.v1:geodesic_baseline_promotion_complete_001",
        "WassersteinExpectedValuesCompleteReview.v1:wasserstein_expected_values_complete_review_001",
        "ChamferExpectedValuesCompleteReview.v1:chamfer_expected_values_complete_review_001",
    ],
    "output_contract": stab_default_output_contract(),
    "governance_flags": stab_default_governance_flags(),
    "provenance": {
        "source": "FOUR_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
            "contracts/canon/metric_operator_registry.v1.schema.json",
            "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
        ],
        "evidence_refs": [
            "NormGeometryBaselinePromotionComplete.v1:norm_geometry_baseline_promotion_complete_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_FRONTIER_PAYLOAD: dict = {
    "recommendation_id": "metric_operator_frontier_recommendation_005",
    "recommendation_status": "ADVISORY_ONLY",
    "ranked_options": four_operator_post_norm_geometry_ranked_options(),
    "recommended_next_step": "G_SEALED_PAUSE",
    "required_operator_decision": True,
    "stop_boundary_reason": (
        "Four-operator SHADOW_STUB_ONLY parity achieved "
        "(WASSERSTEIN, CHAMFER_DISTANCE, GEODESIC, NORM_GEOMETRY). "
        "No self-authorizing next step exists from SHADOW_STUB_ONLY posture. "
        "All advancement requires explicit operator instruction. "
        "TRANSPORT CPU baseline planning complete; authorization gate path advisory-only. "
        "Rank-6 operator selection and registry hardening remain advisory-only."
    ),
    "output_contract": front_default_output_contract(),
    "governance_flags": front_default_governance_flags(),
    "provenance": {
        "source": "FOUR_OPERATOR_SHADOW_STUB_PARITY_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_frontier_recommendation.v1.schema.json",
            "contracts/canon/metric_operator_cross_operator_parity_receipt.v1.schema.json",
            "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
        ],
        "evidence_refs": [
            "NormGeometryBaselinePromotionComplete.v1:norm_geometry_baseline_promotion_complete_001",
            "MetricOperatorCrossOperatorParityReceipt.v1:metric_operator_cross_operator_parity_receipt_003",
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_003",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "MetricOperatorFrontierRecommendation.v1:metric_operator_frontier_recommendation_004",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "four_operator_shadow_stub_parity_bundle",
        artifact_path=PARITY_OUT,
        context={"patch_id": PATCH_ID},
    )
    log_event(logger, "INFO", "four_operator_shadow_stub_parity_bundle_started",
              correlation_id=correlation_id)

    PARITY_OUT.parent.mkdir(parents=True, exist_ok=True)

    parity = build_metric_operator_cross_operator_parity_receipt(_PARITY_PAYLOAD)
    PARITY_OUT.write_text(
        serialize_metric_operator_cross_operator_parity_receipt(parity), encoding="utf-8"
    )
    log_event(logger, "INFO", "parity_receipt_003_emitted",
              canonical_hash=parity.get("canonical_hash", "?"), correlation_id=correlation_id)
    print(f"parity_receipt_003  canonical_hash={parity.get('canonical_hash','?')}")
    print(f"  wrote={PARITY_OUT.as_posix()}")

    stab = build_metric_operator_registry_stabilization(_STAB_PAYLOAD)
    STAB_OUT.write_text(
        serialize_metric_operator_registry_stabilization(stab), encoding="utf-8"
    )
    log_event(logger, "INFO", "registry_stabilization_003_emitted",
              canonical_hash=stab.get("canonical_hash", "?"), correlation_id=correlation_id)
    print(f"registry_stabilization_003  canonical_hash={stab.get('canonical_hash','?')}")
    print(f"  wrote={STAB_OUT.as_posix()}")

    frontier = build_metric_operator_frontier_recommendation(_FRONTIER_PAYLOAD)
    FRONTIER_OUT.write_text(
        serialize_metric_operator_frontier_recommendation(frontier), encoding="utf-8"
    )
    log_event(logger, "INFO", "frontier_recommendation_005_emitted",
              canonical_hash=frontier.get("canonical_hash", "?"), correlation_id=correlation_id)
    print(f"frontier_recommendation_005  canonical_hash={frontier.get('canonical_hash','?')}")
    print(f"  wrote={FRONTIER_OUT.as_posix()}")

    log_event(logger, "INFO", "four_operator_shadow_stub_parity_bundle_completed",
              correlation_id=correlation_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
