from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "MetricOperatorRank5SelectionPlan.v1"
PLAN_TYPE = "METRIC_OPERATOR_RANK5_SELECTION_PLAN"
SELECTED_OPERATOR_ID = "TRANSPORT"
ALLOWED_INTENDED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_SELECTION_FAMILY = (
    "RANK5_OPERATOR_SELECTION",
    "BASELINE_OPERATOR_SELECTION",
    "LOW_RISK_OPERATOR_SELECTION",
)
ALLOWED_SELECTION_STAGE = (
    "SELECTION_PLAN_ONLY",
    "READINESS_REVIEW",
    "SCHEMA_PLAN_READY",
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
    "numpy", "scipy", "gpu-kernel",
)


class MetricOperatorRank5SelectionPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_implementation_gates() -> dict[str, bool]:
    return {
        "implementation_blocked": True,
        "fixture_creation_blocked": True,
        "planning_only": True,
        "requires_dedicated_tests": True,
        "requires_new_operator_plan": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_selection_metadata": True,
    }


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise MetricOperatorRank5SelectionPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_metric_operator_rank5_selection_plan(packet: dict[str, Any]) -> None:
    req = {
        "schema_version", "plan_id", "plan_type", "selected_operator_id",
        "selection_scope", "source_audit_refs", "source_registry_stabilization_refs",
        "source_frontier_recommendation_refs", "implementation_gates",
        "output_contract", "governance_flags", "provenance", "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise MetricOperatorRank5SelectionPlanValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise MetricOperatorRank5SelectionPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise MetricOperatorRank5SelectionPlanValidationError("invalid_plan_type")
    if packet["selected_operator_id"] != SELECTED_OPERATOR_ID:
        raise MetricOperatorRank5SelectionPlanValidationError("unknown_selected_operator_id")

    scope = packet["selection_scope"]
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANE:
        raise MetricOperatorRank5SelectionPlanValidationError("unknown_intended_lane")
    if scope.get("selection_family") not in ALLOWED_SELECTION_FAMILY:
        raise MetricOperatorRank5SelectionPlanValidationError("unknown_selection_family")
    if scope.get("selection_stage") not in ALLOWED_SELECTION_STAGE:
        raise MetricOperatorRank5SelectionPlanValidationError("unknown_selection_stage")

    if not packet.get("source_audit_refs"):
        raise MetricOperatorRank5SelectionPlanValidationError(
            "source_audit_refs_must_be_non_empty"
        )

    gates = packet["implementation_gates"]
    if gates != default_implementation_gates():
        raise MetricOperatorRank5SelectionPlanValidationError("invalid_implementation_gates")

    if packet["output_contract"] != default_output_contract():
        raise MetricOperatorRank5SelectionPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise MetricOperatorRank5SelectionPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_metric_operator_rank5_selection_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_metric_operator_rank5_selection_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_metric_operator_rank5_selection_plan(payload: dict[str, Any]) -> dict[str, Any]:
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "selected_operator_id": SELECTED_OPERATOR_ID,
        "source_audit_refs": sorted(payload.get("source_audit_refs", [])),
        "source_registry_stabilization_refs": sorted(
            payload.get("source_registry_stabilization_refs", [])
        ),
        "source_frontier_recommendation_refs": sorted(
            payload.get("source_frontier_recommendation_refs", [])
        ),
        "implementation_gates": payload.get(
            "implementation_gates", default_implementation_gates()
        ),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_metric_operator_rank5_selection_plan_hash(base)
    validate_metric_operator_rank5_selection_plan(base)
    return _finalize(base)
