from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryCpuBaselineActualPrGateReview.v1"
REVIEW_TYPE = "NORM_GEOMETRY_CPU_BASELINE_ACTUAL_PR_GATE_REVIEW"
OPERATOR_ID = "NORM_GEOMETRY"
ALLOWED_REVIEW_STATUS = (
    "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
    "PLANS_INCOMPLETE",
    "BLOCKED",
)
ALLOWED_IMPLEMENTATION_RECOMMENDATION = (
    "ADVISORY_REVIEW_ONLY",
    "NOT_AUTHORIZED",
    "BLOCKED",
)
LOCKED_FALSE_FLAGS = (
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "runtime_authority",
    "runtime_mutation",
    "forecast_influence",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "activation_approved",
    "authorization_granted",
)
FORBIDDEN = (
    "executable",
    "callable",
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-computation",
    "metric-value",
    "geodesic-distance",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class NormGeometryCpuBaselineActualPrGateReviewValidationError(ValueError):
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
                "NormGeometryCpuBaselineImplementationPlan.v1 must be present "
                "and sealed with all 8 algorithm steps and 6 numerical "
                "stability entries."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-002",
            "condition_description": (
                "NormGeometryCpuBaselineValidationPlan.v1 must be present and "
                "sealed covering all 6 valid fixtures, 4 invalid fixture "
                "rejections, and 4 not-computable fixture rejections."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-003",
            "condition_description": (
                "NormGeometryDistanceImplementationReadinessDossier.v1 must be "
                "present and sealed with "
                "NORM_GEOMETRY_READINESS_DOSSIER_DEFINED status."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-004",
            "condition_description": (
                "All governance_flags in both plan artifacts must be false; "
                "no authority lock may be elevated."
            ),
            "condition_met": True,
        },
        {
            "condition_id": "gate-cond-005",
            "condition_description": (
                "Operator explicit authorization instruction required before "
                "any implementation PR may be opened; this review does not "
                "constitute authorization."
            ),
            "condition_met": False,
        },
    ]


def default_output_contract() -> dict[str, bool]:
    return {
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
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_norm_geometry_cpu_baseline_actual_pr_gate_review(
    packet: dict[str, Any],
) -> None:
    req = {
        "schema_version", "review_id", "review_type", "operator_id",
        "review_status", "plans_reviewed", "gate_conditions",
        "implementation_recommendation", "required_operator_decision",
        "stop_boundary_reason", "output_contract",
        "governance_flags", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError(
            "invalid_schema_version"
        )
    if packet["review_type"] != REVIEW_TYPE:
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError("invalid_review_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError("unknown_operator_id")
    if packet["review_status"] not in ALLOWED_REVIEW_STATUS:
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError("unknown_review_status")
    if packet["implementation_recommendation"] not in ALLOWED_IMPLEMENTATION_RECOMMENDATION:
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError(
            "unknown_implementation_recommendation"
        )
    if packet["required_operator_decision"] is not True:
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError(
            "required_operator_decision_must_be_true"
        )
    if not packet.get("plans_reviewed"):
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError(
            "plans_reviewed_must_be_non_empty"
        )
    if not packet.get("gate_conditions"):
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError(
            "gate_conditions_must_be_non_empty"
        )

    seen_condition_ids: set[str] = set()
    for cond in packet["gate_conditions"]:
        cid = cond.get("condition_id")
        if cid in seen_condition_ids:
            raise NormGeometryCpuBaselineActualPrGateReviewValidationError(
                "duplicate_condition_id"
            )
        seen_condition_ids.add(cid)
        if not isinstance(cond.get("condition_met"), bool):
            raise NormGeometryCpuBaselineActualPrGateReviewValidationError(
                "condition_met_must_be_bool"
            )

    if packet["output_contract"] != default_output_contract():
        raise NormGeometryCpuBaselineActualPrGateReviewValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise NormGeometryCpuBaselineActualPrGateReviewValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_norm_geometry_cpu_baseline_actual_pr_gate_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_norm_geometry_cpu_baseline_actual_pr_gate_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_norm_geometry_cpu_baseline_actual_pr_gate_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    gate_conditions = sorted(
        payload.get("gate_conditions", default_gate_conditions()),
        key=lambda x: x["condition_id"],
    )
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "plans_reviewed": sorted(payload.get("plans_reviewed", [])),
        "gate_conditions": gate_conditions,
        "required_operator_decision": True,
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_norm_geometry_cpu_baseline_actual_pr_gate_review_hash(base)
    validate_norm_geometry_cpu_baseline_actual_pr_gate_review(base)
    return _finalize(base)
