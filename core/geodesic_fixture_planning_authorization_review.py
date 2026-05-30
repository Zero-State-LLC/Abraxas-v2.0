from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicFixturePlanningAuthorizationReview.v1"
REVIEW_TYPE = "GEODESIC_FIXTURE_PLANNING_AUTHORIZATION_REVIEW"
OPERATOR_ID = "GEODESIC"
ALLOWED_REVIEW_STATUS = (
    "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
    "PLANS_INCOMPLETE",
    "BLOCKED",
)
ALLOWED_FIXTURE_PLANNING_RECOMMENDATION = (
    "ADVISORY_REVIEW_ONLY",
    "NOT_AUTHORIZED",
    "BLOCKED",
)
LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation",
    "runtime_authority", "runtime_mutation", "forecast_influence",
    "execution_authority", "token_minting_allowed", "valid_for_execution",
    "activation_approved", "authorization_granted",
)
FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast",
    "scoring", "metric-computation", "metric-value", "geodesic-distance",
    "dijkstra-execution", "numpy", "scipy", "gpu-kernel",
)


class GeodesicFixturePlanningAuthorizationReviewValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_gate_conditions() -> list[dict[str, Any]]:
    return [
        {
            "condition_id": "gate-cond-001",
            "condition_description": (
                "MetricOperatorRank3CandidateAudit.v1 must be present with "
                "audit_status=RANK3_CANDIDATE_SELECTED and recommended_rank3=GEODESIC."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-002",
            "condition_description": (
                "MetricOperatorRank3SelectionPlan.v1 must be present with "
                "selected_operator_id=GEODESIC, intended_lane=SHADOW, "
                "selection_stage=SELECTION_PLAN_ONLY, and all implementation_gates "
                "blocking."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-003",
            "condition_description": (
                "GeodesicDistanceImplementationReadinessDossier.v1 must be present with "
                "dossier_status=GEODESIC_READINESS_DOSSIER_DEFINED and all required "
                "blocked_scopes present."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-004",
            "condition_description": (
                "GeodesicTestVectorSchemaPlan.v1 must be present with 5 valid, 4 invalid, "
                "and 4 not-computable schema groups; schema_stage=SCHEMA_PLAN_ONLY; "
                "all output_contract emission flags false except emits_schema_plan and "
                "emits_schema_group_metadata."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-005",
            "condition_description": (
                "All governance_flags across all four GEODESIC tier artifacts must be "
                "false; no authority lock may be elevated in any tier artifact."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-006",
            "condition_description": (
                "Operator explicit authorization for GEODESIC fixture file creation must "
                "be present as a separate operator instruction before any fixture schema "
                "file or fixture data file may be created."
            ),
            "condition_met": False,
            "blocking_reason": (
                "No operator instruction authorizing GEODESIC fixture file creation has "
                "been received. This review is advisory only and does not constitute "
                "authorization."
            ),
        },
    ]


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_fixture_files": False,
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_gate_review": True,
    }


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_geodesic_fixture_planning_authorization_review(
    packet: dict[str, Any],
) -> None:
    req = {
        "schema_version", "review_id", "review_type", "operator_id",
        "tiers_reviewed", "gate_conditions", "review_status",
        "fixture_planning_recommendation", "required_operator_decision",
        "stop_boundary_reason", "output_contract", "governance_flags",
        "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            "invalid_schema_version"
        )
    if packet["review_type"] != REVIEW_TYPE:
        raise GeodesicFixturePlanningAuthorizationReviewValidationError("invalid_review_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise GeodesicFixturePlanningAuthorizationReviewValidationError("invalid_operator_id")
    if packet["review_status"] not in ALLOWED_REVIEW_STATUS:
        raise GeodesicFixturePlanningAuthorizationReviewValidationError("unknown_review_status")
    if packet["fixture_planning_recommendation"] not in ALLOWED_FIXTURE_PLANNING_RECOMMENDATION:
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            "unknown_fixture_planning_recommendation"
        )
    if packet["required_operator_decision"] is not True:
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            "required_operator_decision_must_be_true"
        )
    if not packet.get("tiers_reviewed"):
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            "tiers_reviewed_must_be_non_empty"
        )
    if not packet.get("gate_conditions"):
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            "gate_conditions_must_be_non_empty"
        )
    if not packet.get("stop_boundary_reason", "").strip():
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            "stop_boundary_reason_must_be_non_empty"
        )

    # gate-cond-006 must exist and must be False
    cond_ids = {c["condition_id"] for c in packet["gate_conditions"]}
    if "gate-cond-006" not in cond_ids:
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            "gate_cond_006_missing"
        )
    gate6 = next(c for c in packet["gate_conditions"] if c["condition_id"] == "gate-cond-006")
    if gate6.get("condition_met") is not False:
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            "gate_cond_006_must_be_unmet"
        )

    if packet["output_contract"] != default_output_contract():
        raise GeodesicFixturePlanningAuthorizationReviewValidationError(
            "invalid_output_contract"
        )
    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise GeodesicFixturePlanningAuthorizationReviewValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_geodesic_fixture_planning_authorization_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_geodesic_fixture_planning_authorization_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_geodesic_fixture_planning_authorization_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "tiers_reviewed": sorted(payload.get("tiers_reviewed", [])),
        "gate_conditions": sorted(
            payload.get("gate_conditions", default_gate_conditions()),
            key=lambda x: x["condition_id"],
        ),
        "required_operator_decision": True,
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_geodesic_fixture_planning_authorization_review_hash(
        base
    )
    validate_geodesic_fixture_planning_authorization_review(base)
    return _finalize(base)
