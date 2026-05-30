from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryImplementationAuthorizationTemplate.v1"
TEMPLATE_TYPE = "NORM_GEOMETRY_IMPLEMENTATION_AUTHORIZATION_TEMPLATE"
OPERATOR_ID = "NORM_GEOMETRY"
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


class NormGeometryImplementationAuthorizationTemplateValidationError(ValueError):
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
            "decision_id": "ng-decision-001",
            "field_name": "float64_precision_declaration",
            "description": (
                "Operator confirms float64 required for all element-wise "
                "differences, power operations, summation accumulation, and "
                "root extraction. Float32 excluded."
            ),
            "value_template": "FLOAT64_REQUIRED",
            "locked": False,
        },
        {
            "decision_id": "ng-decision-002",
            "field_name": "p_inf_sentinel_value_declaration",
            "description": (
                "Operator declares the exact sentinel value used to represent "
                "p=inf in input data. Required for deterministic branch selection."
            ),
            "value_template": "<OPERATOR_DECLARED_SENTINEL>",
            "locked": False,
        },
        {
            "decision_id": "ng-decision-003",
            "field_name": "max_element_magnitude_declaration",
            "description": (
                "Operator declares the maximum allowed element magnitude in "
                "input vectors. Required to bound power overflow risk."
            ),
            "value_template": "<OPERATOR_DECLARED_FLOAT64_BOUND>",
            "locked": False,
        },
        {
            "decision_id": "ng-decision-004",
            "field_name": "max_p_value_declaration",
            "description": (
                "Operator declares the maximum allowed finite p value. "
                "Required to bound power overflow risk for finite p."
            ),
            "value_template": "<OPERATOR_DECLARED_FLOAT64_BOUND>",
            "locked": False,
        },
        {
            "decision_id": "ng-decision-005",
            "field_name": "not_computable_branch_enumeration_confirmation",
            "description": (
                "Operator confirms the complete enumeration of NOT_COMPUTABLE "
                "conditions: empty vector (n=0), p < 1.0, mismatched lengths, "
                "non-finite element value, power overflow."
            ),
            "value_template": "CONFIRMED",
            "locked": False,
        },
    ]


def default_locked_constants_required() -> list[str]:
    return [
        "float64_precision_declaration",
        "p_inf_sentinel_value_declaration",
        "max_element_magnitude_declaration",
        "max_p_value_declaration",
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
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_norm_geometry_implementation_authorization_template(
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
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "invalid_schema_version"
        )
    if packet["template_type"] != TEMPLATE_TYPE:
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "invalid_template_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "unknown_operator_id"
        )
    if packet["template_status"] not in ALLOWED_TEMPLATE_STATUS:
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "invalid_template_status"
        )
    if packet["active"] is not False:
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "active_must_be_false"
        )
    if packet["valid_for_execution"] is not False:
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "valid_for_execution_must_be_false"
        )
    if packet["authorization_granted"] is not False:
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "authorization_granted_must_be_false"
        )
    if not packet.get("required_operator_decision_fields"):
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "required_operator_decision_fields_must_be_non_empty"
        )
    if not packet.get("locked_constants_required"):
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "locked_constants_required_must_be_non_empty"
        )
    if packet["output_contract"] != default_output_contract():
        raise NormGeometryImplementationAuthorizationTemplateValidationError(
            "invalid_output_contract"
        )
    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise NormGeometryImplementationAuthorizationTemplateValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_norm_geometry_implementation_authorization_template_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_norm_geometry_implementation_authorization_template(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_norm_geometry_implementation_authorization_template(
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
    base["canonical_hash"] = compute_norm_geometry_implementation_authorization_template_hash(
        base
    )
    validate_norm_geometry_implementation_authorization_template(base)
    return _finalize(base)
