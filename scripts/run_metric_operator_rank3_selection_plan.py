"""Script: emit deterministic MetricOperatorRank3SelectionPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.metric_operator_rank3_selection_plan import (
    LOCKED_FALSE_FLAGS,
    build_metric_operator_rank3_selection_plan,
    default_implementation_gates,
    default_output_contract,
    serialize_metric_operator_rank3_selection_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_METRIC_OPERATOR_RANK3_SELECTION_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.metric_operator_rank3_selection_plan_latest

_PAYLOAD: dict = {
    "plan_id": "metric_operator_rank3_selection_plan_001",
    "selection_scope": {
        "intended_lane": "SHADOW",
        "selection_family": "RANK3_OPERATOR_SELECTION",
        "selection_stage": "SELECTION_PLAN_ONLY",
    },
    "source_audit_refs": [
        "MetricOperatorRank3CandidateAudit.v1:"
        "metric_operator_rank3_candidate_audit_001",
    ],
    "source_registry_stabilization_refs": [
        "MetricOperatorRegistryStabilization.v1:"
        "metric_operator_registry_stabilization_001",
    ],
    "source_frontier_recommendation_refs": [
        "MetricOperatorFrontierRecommendation.v1:"
        "metric_operator_frontier_recommendation_001",
    ],
    "implementation_gates": default_implementation_gates(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "METRIC_OPERATOR_RANK3_SELECTION_PLAN_001",
        "evidence_refs": [
            "MetricOperatorRank3CandidateAudit.v1:"
            "metric_operator_rank3_candidate_audit_001",
            "MetricOperatorRegistryStabilization.v1:"
            "metric_operator_registry_stabilization_001",
            "MetricOperatorFrontierRecommendation.v1:"
            "metric_operator_frontier_recommendation_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "metric_operator_rank3_selection_plan.v1.schema.json",
            "contracts/canon/"
            "metric_operator_rank3_candidate_audit.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "metric_operator_rank3_selection_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "metric_operator_rank3_selection_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_metric_operator_rank3_selection_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_metric_operator_rank3_selection_plan(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "metric_operator_rank3_selection_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print(f"selected_operator_id={packet['selected_operator_id']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
