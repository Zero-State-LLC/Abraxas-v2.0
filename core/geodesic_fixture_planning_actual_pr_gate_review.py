from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicFixturePlanningActualPrGateReview.v1"
REVIEW_TYPE = "GEODESIC_FIXTURE_PLANNING_ACTUAL_PR_GATE_REVIEW"
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


class GeodesicFixturePlanningActualPrGateReviewValidationError(ValueError):
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
                "GeodesicFixturePlanningAuthorizationReview.v1 must be present with "
                "review_status=PLANS_COMPLETE_PENDING_OPERATOR_DECISION and "
                "fixture_planning_recommendation=ADVISORY_REVIEW_ONLY."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-002",
            "condition_description": (
                "All four GEODESIC tier artifacts (CandidateAudit, SelectionPlan, "
                "ReadinessDossier, TestVectorSchemaPlan) must be present and sealed "
                "with valid canonical hashes and all governance_flags false."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-003",
            "condition_description": (
                "gate-cond-006 from GeodesicFixturePlanningAuthorizationReview.v1 must "
                "remain unmet: no operator authorization for fixture file creation has "
                "been issued."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-004",
            "condition_description": (
                "This PR gate review must not itself authorize fixture file creation, "
                "computation, metric emission, or any authority escalation."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-005",
            "condition_description": (
                "Operator explicit authorization for GEODESIC fixture file creation must "
                "be received as a new operator instruction before a fixture PR may be "
                "opened."
            ),
            "condition_met": False,
            "blocking_reason": (
                "No operator instruction authorizing GEODESIC fixture file creation has "
                "been received. This PR gate review is advisory only."
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
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_geodesic_fixture_planning_actual_pr_gate_review(
    packet: dict[str, Any],
) -> None:
    req = {
        "schema_version", "review_id", "review_type", "operator_id",
        "authorization_reviews_referenced", "gate_conditions", "review_status",
        "fixture_planning_recommendation", "required_operator_decision",
        "stop_boundary_reason", "output_contract", "governance_flags",
        "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            "invalid_schema_version"
        )
    if packet["review_type"] != REVIEW_TYPE:
        raise GeodesicFixturePlanningActualPrGateReviewValidationError("invalid_review_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise GeodesicFixturePlanningActualPrGateReviewValidationError("invalid_operator_id")
    if packet["review_status"] not in ALLOWED_REVIEW_STATUS:
        raise GeodesicFixturePlanningActualPrGateReviewValidationError("unknown_review_status")
    if packet["fixture_planning_recommendation"] not in ALLOWED_FIXTURE_PLANNING_RECOMMENDATION:
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            "unknown_fixture_planning_recommendation"
        )
    if packet["required_operator_decision"] is not True:
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            "required_operator_decision_must_be_true"
        )
    if not packet.get("authorization_reviews_referenced"):
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            "authorization_reviews_referenced_must_be_non_empty"
        )
    if not packet.get("gate_conditions"):
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            "gate_conditions_must_be_non_empty"
        )
    if not packet.get("stop_boundary_reason", "").strip():
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            "stop_boundary_reason_must_be_non_empty"
        )

    # gate-cond-005 must exist and must be False (operator auth still unmet)
    cond_ids = {c["condition_id"] for c in packet["gate_conditions"]}
    if "gate-cond-005" not in cond_ids:
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            "gate_cond_005_missing"
        )
    gate5 = next(c for c in packet["gate_conditions"] if c["condition_id"] == "gate-cond-005")
    if gate5.get("condition_met") is not False:
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            "gate_cond_005_must_be_unmet"
        )

    if packet["output_contract"] != default_output_contract():
        raise GeodesicFixturePlanningActualPrGateReviewValidationError(
            "invalid_output_contract"
        )
    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise GeodesicFixturePlanningActualPrGateReviewValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_geodesic_fixture_planning_actual_pr_gate_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_geodesic_fixture_planning_actual_pr_gate_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_geodesic_fixture_planning_actual_pr_gate_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "authorization_reviews_referenced": sorted(
            payload.get("authorization_reviews_referenced", [])
        ),
        "gate_conditions": sorted(
            payload.get("gate_conditions", default_gate_conditions()),
            key=lambda x: x["condition_id"],
        ),
        "required_operator_decision": True,
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_geodesic_fixture_planning_actual_pr_gate_review_hash(
        base
    )
    validate_geodesic_fixture_planning_actual_pr_gate_review(base)
    return _finalize(base)
