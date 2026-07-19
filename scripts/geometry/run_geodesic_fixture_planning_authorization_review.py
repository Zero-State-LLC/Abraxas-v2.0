"""Script: emit deterministic GeodesicFixturePlanningAuthorizationReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.geodesic_fixture_planning_authorization_review import (
    LOCKED_FALSE_FLAGS,
    build_geodesic_fixture_planning_authorization_review,
    default_gate_conditions,
    default_output_contract,
    serialize_geodesic_fixture_planning_authorization_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_GEODESIC_FIXTURE_PLANNING_AUTHORIZATION_REVIEW_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.geodesic_fixture_planning_authorization_review_latest

_PAYLOAD: dict = {
    "review_id": "geodesic_fixture_planning_authorization_review_001",
    "tiers_reviewed": [
        "MetricOperatorRank3CandidateAudit.v1:"
        "metric_operator_rank3_candidate_audit_001",
        "MetricOperatorRank3SelectionPlan.v1:"
        "metric_operator_rank3_selection_plan_001",
        "GeodesicDistanceImplementationReadinessDossier.v1:"
        "geodesic_distance_implementation_readiness_dossier_001",
        "GeodesicTestVectorSchemaPlan.v1:"
        "geodesic_test_vector_schema_plan_001",
    ],
    "gate_conditions": default_gate_conditions(),
    "review_status": "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
    "fixture_planning_recommendation": "ADVISORY_REVIEW_ONLY",
    "stop_boundary_reason": (
        "This review is advisory only. All four GEODESIC tier artifacts are complete "
        "and sealed. gate-cond-006 is not met: no operator instruction authorizing "
        "GEODESIC fixture file creation has been received. No fixture PR may be opened "
        "without an explicit operator authorization instruction. "
        "fixture_creation_authorized=false; emits_fixture_files=false; "
        "emits_metric_values=false."
    ),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "GEODESIC_FIXTURE_PLANNING_AUTHORIZATION_REVIEW_001",
        "evidence_refs": [
            "MetricOperatorRank3CandidateAudit.v1:"
            "metric_operator_rank3_candidate_audit_001",
            "MetricOperatorRank3SelectionPlan.v1:"
            "metric_operator_rank3_selection_plan_001",
            "GeodesicDistanceImplementationReadinessDossier.v1:"
            "geodesic_distance_implementation_readiness_dossier_001",
            "GeodesicTestVectorSchemaPlan.v1:"
            "geodesic_test_vector_schema_plan_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "geodesic_fixture_planning_authorization_review.v1.schema.json",
            "contracts/canon/"
            "geodesic_test_vector_schema_plan.v1.schema.json",
            "contracts/canon/"
            "geodesic_distance_implementation_readiness_dossier.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "geodesic_fixture_planning_authorization_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "geodesic_fixture_planning_authorization_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_geodesic_fixture_planning_authorization_review(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_geodesic_fixture_planning_authorization_review(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "geodesic_fixture_planning_authorization_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"review_id={packet['review_id']}")
    print(f"review_type={packet['review_type']}")
    print(f"review_status={packet['review_status']}")
    print(f"fixture_planning_recommendation={packet['fixture_planning_recommendation']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
