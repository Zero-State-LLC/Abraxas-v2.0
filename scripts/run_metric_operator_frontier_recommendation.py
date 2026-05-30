"""Script: emit deterministic MetricOperatorFrontierRecommendation.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.metric_operator_frontier_recommendation import (
    build_metric_operator_frontier_recommendation,
    default_governance_flags,
    default_output_contract,
    default_ranked_options,
    serialize_metric_operator_frontier_recommendation,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "METRIC_OPERATOR_FRONTIER_RECOMMENDATION_BUNDLE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.metric_operator_frontier_recommendation_latest

_PAYLOAD: dict = {
    "recommendation_id": "metric_operator_frontier_recommendation_001",
    "recommendation_status": "ADVISORY_ONLY",
    "ranked_options": default_ranked_options(),
    "recommended_next_step": "G_SEALED_PAUSE",
    "required_operator_decision": True,
    "stop_boundary_reason": (
        "Selection plan declares implementation_blocked=True and "
        "requires_new_operator_plan=True. No self-authorizing next step exists "
        "from SHADOW_STUB_ONLY posture. All advancement requires explicit "
        "operator instruction."
    ),
    "output_contract": default_output_contract(),
    "governance_flags": default_governance_flags(),
    "provenance": {
        "source": "METRIC_OPERATOR_FRONTIER_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_frontier_recommendation.v1.schema.json",
            "contracts/canon/metric_operator_cross_operator_parity_receipt.v1.schema.json",
            "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
        ],
        "evidence_refs": [
            "MetricOperatorCrossOperatorParityReceipt.v1:metric_operator_cross_operator_parity_receipt_001",
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_001",
            "MetricOperatorImplementationSelectionPlan.v1:metric_operator_implementation_selection_plan_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "metric_operator_frontier_recommendation",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "metric_operator_frontier_recommendation_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_metric_operator_frontier_recommendation(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_metric_operator_frontier_recommendation(packet), encoding="utf-8"
    )

    log_event(
        logger,
        "INFO",
        "metric_operator_frontier_recommendation_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"recommendation_id={packet['recommendation_id']}")
    print(f"recommendation_status={packet['recommendation_status']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
