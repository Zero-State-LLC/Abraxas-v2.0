from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportImplementationAuthorizationTemplate.v1"
TEMPLATE_TYPE = "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_TEMPLATE"
OPERATOR_ID = "TRANSPORT"
ALLOWED_TEMPLATE_STATUS = ("TEMPLATE_ONLY",)
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


class TransportImplementationAuthorizationTemplateValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_required_operator_decision_fields() -> list[dict[str, Any]]:
    return [
        {
            "decision_id": "tr-decision-001",
            "field_name": "lp_solver_variant_declaration",
            "description": (
                "Operator declares the exact LP solver variant to be used for "
                "general m*n balanced transport problems. Must be a deterministic "
                "solver with a fixed algorithm family. Stochastic variants excluded."
            ),
            "value_template": "<OPERATOR_DECLARED_LP_SOLVER_VARIANT>",
            "locked": False,
        },
        {
            "decision_id": "tr-decision-002",
            "field_name": "pivot_rule_declaration",
            "description": (
                "Operator declares the exact pivot rule for the LP solver. "
                "Randomized pivot rules excluded. Must be fixed before "
                "implementation to ensure deterministic results."
            ),
            "value_template": "<OPERATOR_DECLARED_PIVOT_RULE>",
            "locked": False,
        },
        {
            "decision_id": "tr-decision-003",
            "field_name": "tie_breaking_rule_declaration",
            "description": (
                "Operator declares the tie-breaking rule for degenerate transport "
                "problems with multiple optimal transport plans. Required so "
                "that test fixtures have unique expected values."
            ),
            "value_template": "<OPERATOR_DECLARED_TIE_BREAKING_RULE>",
            "locked": False,
        },
        {
            "decision_id": "tr-decision-004",
            "field_name": "balance_tolerance_declaration",
            "description": (
                "Operator declares the exact relative balance tolerance epsilon_rel "
                "used to check |sum(supply) - sum(demand)| <= epsilon_rel * "
                "max(sum(supply), sum(demand)). Planned default: 1e-9."
            ),
            "value_template": "<OPERATOR_DECLARED_FLOAT64_EPSILON>",
            "locked": False,
        },
        {
            "decision_id": "tr-decision-005",
            "field_name": "max_problem_size_declaration",
            "description": (
                "Operator declares the maximum allowed m*n (number of LP decision "
                "variables). Required to bound LP solve time and memory allocation."
            ),
            "value_template": "<OPERATOR_DECLARED_INTEGER_BOUND>",
            "locked": False,
        },
        {
            "decision_id": "tr-decision-006",
            "field_name": "cost_matrix_magnitude_bound_declaration",
            "description": (
                "Operator declares the maximum allowed cost matrix entry value. "
                "Required to bound float64 overflow risk in LP objective "
                "accumulation for large cost matrices."
            ),
            "value_template": "<OPERATOR_DECLARED_FLOAT64_BOUND>",
            "locked": False,
        },
        {
            "decision_id": "tr-decision-007",
            "field_name": "not_computable_branch_enumeration_confirmation",
            "description": (
                "Operator confirms the complete enumeration of NOT_COMPUTABLE "
                "conditions: empty supply (m=0) or demand (n=0), unbalanced "
                "transport (exceeds tolerance), negative supply/demand/cost "
                "element, non-finite value, cost_matrix shape mismatch."
            ),
            "value_template": "CONFIRMED",
            "locked": False,
        },
    ]


def default_locked_constants_required() -> list[str]:
    return [
        "lp_solver_variant_declaration",
        "pivot_rule_declaration",
        "tie_breaking_rule_declaration",
        "balance_tolerance_declaration",
        "max_problem_size_declaration",
        "cost_matrix_magnitude_bound_declaration",
        "not_computable_branch_enumeration_confirmation",
    ]


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_template": True,
        "authorization_granted": False,
    }


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportImplementationAuthorizationTemplateValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_transport_implementation_authorization_template(
    packet: dict[str, Any],
) -> None:
    req = {
        "schema_version", "template_id", "template_type", "operator_id",
        "template_status", "active", "valid_for_execution", "authorization_granted",
        "required_operator_decision_fields", "locked_constants_required",
        "activation_blocked_reason", "output_contract",
        "governance_flags", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise TransportImplementationAuthorizationTemplateValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise TransportImplementationAuthorizationTemplateValidationError(
            "invalid_schema_version"
        )
    if packet["template_type"] != TEMPLATE_TYPE:
        raise TransportImplementationAuthorizationTemplateValidationError(
            "invalid_template_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise TransportImplementationAuthorizationTemplateValidationError(
            "unknown_operator_id"
        )
    if packet["template_status"] not in ALLOWED_TEMPLATE_STATUS:
        raise TransportImplementationAuthorizationTemplateValidationError(
            "invalid_template_status"
        )
    if packet["active"] is not False:
        raise TransportImplementationAuthorizationTemplateValidationError(
            "active_must_be_false"
        )
    if packet["valid_for_execution"] is not False:
        raise TransportImplementationAuthorizationTemplateValidationError(
            "valid_for_execution_must_be_false"
        )
    if packet["authorization_granted"] is not False:
        raise TransportImplementationAuthorizationTemplateValidationError(
            "authorization_granted_must_be_false"
        )
    if not packet.get("required_operator_decision_fields"):
        raise TransportImplementationAuthorizationTemplateValidationError(
            "required_operator_decision_fields_must_be_non_empty"
        )
    if not packet.get("locked_constants_required"):
        raise TransportImplementationAuthorizationTemplateValidationError(
            "locked_constants_required_must_be_non_empty"
        )
    if packet["output_contract"] != default_output_contract():
        raise TransportImplementationAuthorizationTemplateValidationError(
            "invalid_output_contract"
        )
    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise TransportImplementationAuthorizationTemplateValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_transport_implementation_authorization_template_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_transport_implementation_authorization_template(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_transport_implementation_authorization_template(
    payload: dict[str, Any],
) -> dict[str, Any]:
    decision_fields = sorted(
        payload.get(
            "required_operator_decision_fields",
            default_required_operator_decision_fields(),
        ),
        key=lambda d: d["decision_id"],
    )
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "template_type": TEMPLATE_TYPE,
        "operator_id": OPERATOR_ID,
        "template_status": "TEMPLATE_ONLY",
        "active": False,
        "valid_for_execution": False,
        "authorization_granted": False,
        "required_operator_decision_fields": decision_fields,
        "locked_constants_required": sorted(
            payload.get("locked_constants_required", default_locked_constants_required())
        ),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_transport_implementation_authorization_template_hash(base)
    validate_transport_implementation_authorization_template(base)
    return _finalize(base)
