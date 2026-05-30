"""Script: emit deterministic MetricOperatorRank3CandidateAudit.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.metric_operator_rank3_candidate_audit import (
    LOCKED_FALSE_FLAGS,
    build_metric_operator_rank3_candidate_audit,
    default_candidate_entries,
    default_output_contract,
    serialize_metric_operator_rank3_candidate_audit,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_METRIC_OPERATOR_RANK3_CANDIDATE_AUDIT_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.metric_operator_rank3_candidate_audit_latest

_PAYLOAD: dict = {
    "audit_id": "metric_operator_rank3_candidate_audit_001",
    "completed_operators": ["CHAMFER_DISTANCE", "WASSERSTEIN"],
    "candidate_entries": default_candidate_entries(),
    "recommended_rank3": "GEODESIC",
    "audit_status": "RANK3_CANDIDATE_SELECTED",
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "METRIC_OPERATOR_RANK3_CANDIDATE_AUDIT_001",
        "evidence_refs": [
            "MetricOperatorRegistryStabilization.v1:"
            "metric_operator_registry_stabilization_001",
            "MetricOperatorFrontierRecommendation.v1:"
            "metric_operator_frontier_recommendation_001",
            "MetricOperatorCrossOperatorParityReceipt.v1:"
            "metric_operator_cross_operator_parity_receipt_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "metric_operator_rank3_candidate_audit.v1.schema.json",
            "contracts/canon/"
            "metric_operator_registry_stabilization.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "metric_operator_rank3_candidate_audit",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "metric_operator_rank3_candidate_audit_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_metric_operator_rank3_candidate_audit(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_metric_operator_rank3_candidate_audit(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "metric_operator_rank3_candidate_audit_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"audit_id={packet['audit_id']}")
    print(f"audit_type={packet['audit_type']}")
    print(f"audit_status={packet['audit_status']}")
    print(f"recommended_rank3={packet['recommended_rank3']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
