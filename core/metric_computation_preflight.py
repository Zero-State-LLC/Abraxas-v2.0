"""Core builder for Metric Computation Preflight boundary artifact."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "MetricComputationPreflight.v1"
PREFLIGHT_TYPE = "METRIC_COMPUTATION_PREFLIGHT_BOUNDARY"
PREFLIGHT_ID = "metric_computation_preflight_001"
PREFLIGHT_STATUS = "METRIC_COMPUTATION_PREFLIGHT_DEFINED"

SOURCE_WEBGL_RENDERER_BOUNDARY_HASH = (
    "d4ac613bb547b50a2b424124b2b4d26fd4d647f9d039f6a73691ee406cab5393"
)
SOURCE_METRIC_REGISTRY_HASH = (
    "0493c034f1f270d31f23c211c0a938d75e0634299f1123db872b503ccb4bd0e3"
)
SOURCE_BASELINE_VECTOR_PACK_HASH = (
    "053988aac083e06cf727a42675ae6e3f025e884d521f584d5b631ff813c2f0db"
)

REGISTERED_OPERATOR_COUNT = 12

ALLOWED_VALIDATION_RULES = (
    "AUTHORITY_LOCK_SCAN",
    "GOVERNANCE_FALSE_FLAG_SCAN",
    "NO_RUNTIME_MUTATION_SCAN",
    "OUTPUT_DECLARATION_COMPLIANCE",
    "PREFLIGHT_GOVERNANCE_ACKNOWLEDGEMENT_CHECK",
    "PREFLIGHT_PROJECTION_COMPLIANCE",
    "RENDERER_BOUNDARY_CHAIN_CHECK",
    "SCHEMA_VALIDATION",
    "SOURCE_REF_PRESERVATION_CHECK",
)

REQUIRED_BLOCKED_SCOPES = (
    "canon_promotion",
    "forecast_authority",
    "inference_authority",
    "p43_surface_lanes",
    "production_activation",
    "renderer_code",
    "runtime_mutation",
)

LOCKED_FALSE_AUTHORITY_KEYS = (
    "baseline_mutation",
    "canon_promotion",
    "governance_authority_mutation",
    "p43_surface_lanes_authorized",
    "production_activation",
    "runtime_mutation",
    "scheduler_mutation",
    "work_package_definition_only",
)

LOCKED_TRUE_AUTHORITY_KEYS = (
    "advisory_only",
    "canvas_renderer_implementation_authorized",
    "metric_computation_authorized",
    "projection_only",
    "renderer_boundary_implementation",
    "svg_renderer_implementation_authorized",
    "webgl_renderer_implementation_authorized",
)

LOCKED_FALSE_GOVERNANCE_FLAGS = (
    "activation_approved",
    "authorization_granted",
    "canon_promotion",
    "execution_authority",
    "forecast_influence",
    "production_activation",
    "runtime_authority",
    "runtime_mutation",
    "scheduler_mutation",
    "token_minting_allowed",
    "valid_for_execution",
)

LOCKED_FALSE_OUTPUT_FLAGS = (
    "emits_canvas",
    "emits_forecast_inputs",
    "emits_metric_values",
    "emits_rendered_output",
    "emits_runtime_controls",
    "emits_svg",
    "emits_ui_controls",
    "emits_webgl",
)

REQUIRED_PREFLIGHT_ACKNOWLEDGEMENT_KEYS = (
    "all_twelve_operators_remain_not_implemented",
    "emits_metric_values_is_false",
    "metric_computation_authorized_does_not_grant_forecast_authority",
    "metric_computation_authorized_does_not_grant_inference_authority",
    "p43_surface_lanes_remain_blocked",
    "production_activation_remains_false",
)

FORBIDDEN_PROVENANCE_TOKENS = (
    "cache",
    "callable",
    "executable",
    "forecast",
    "inference",
    "metric-computation",
    "metric-value",
    "route-control",
    "runtime",
    "scheduler",
    "scoring",
    "ui",
)


class MetricComputationPreflightValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def _assert_provenance_safe(provenance: dict[str, Any]) -> None:
    lowered = json.dumps(provenance).lower()
    for token in FORBIDDEN_PROVENANCE_TOKENS:
        if token in lowered:
            raise MetricComputationPreflightValidationError(
                f"forbidden_provenance_reference_detected:{token}"
            )


def build_preflight_projection(viewmodel_ref: dict[str, Any]) -> dict[str, Any]:
    """Construct a deterministic, advisory-only metric preflight boundary projection."""
    return _finalize(
        {
            "advisory_only": True,
            "data_source_hash": str(viewmodel_ref.get("source_hash", "")),
            "emits_metric_values": False,
            "execution_authority": False,
            "forecast_influence": False,
            "metric_computation_status": "PREFLIGHT_BOUNDARY_ONLY",
            "preflight_only": True,
            "projection_only": True,
            "registered_operator_count": REGISTERED_OPERATOR_COUNT,
            "schema_version": str(viewmodel_ref.get("schema_version", "")),
            "title": str(viewmodel_ref.get("title", "")),
        }
    )


def default_preflight_governance_acknowledgements() -> dict[str, Any]:
    return {
        "all_twelve_operators_remain_not_implemented": True,
        "emits_metric_values_is_false": True,
        "metric_computation_authorized_does_not_grant_forecast_authority": True,
        "metric_computation_authorized_does_not_grant_inference_authority": True,
        "p43_surface_lanes_remain_blocked": True,
        "production_activation_remains_false": True,
    }


def default_metric_intake_record(viewmodel_ref: dict[str, Any] | None = None) -> dict[str, Any]:
    vr = viewmodel_ref or {}
    return {
        "execution_authority": False,
        "input_fields_accepted": sorted(
            ["metric_registry_ref", "preflight_boundary_id", "viewmodel_ref"]
        ),
        "metric_computation_status": "PREFLIGHT_BOUNDARY_ONLY",
        "ordering_applied": "CANONICAL_JSON_SORT",
        "projection_only": True,
        "registered_operator_count": REGISTERED_OPERATOR_COUNT,
        "viewmodel_schema_version": vr.get("schema_version", ""),
    }


def default_renderer_output_declaration() -> dict[str, Any]:
    return {
        "emits_canvas": False,
        "emits_forecast_inputs": False,
        "emits_metric_values": False,
        "emits_planning_metadata": True,
        "emits_rendered_output": False,
        "emits_runtime_controls": False,
        "emits_svg": False,
        "emits_ui_controls": False,
        "emits_webgl": False,
        "execution_authority": False,
        "forecast_influence": False,
    }


def default_blocked_scopes() -> list[str]:
    return sorted(REQUIRED_BLOCKED_SCOPES)


def default_validation_rules() -> list[str]:
    return sorted(ALLOWED_VALIDATION_RULES)


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "baseline_mutation": False,
        "canon_promotion": False,
        "canvas_renderer_implementation_authorized": True,
        "governance_authority_mutation": False,
        "metric_computation_authorized": True,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "projection_only": True,
        "renderer_boundary_implementation": True,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "svg_renderer_implementation_authorized": True,
        "webgl_renderer_implementation_authorized": True,
        "work_package_definition_only": False,
    }


def default_governance_flags() -> dict[str, Any]:
    return {
        "activation_approved": False,
        "authorization_granted": False,
        "canon_promotion": False,
        "execution_authority": False,
        "forecast_influence": False,
        "production_activation": False,
        "runtime_authority": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
    }


def validate_metric_computation_preflight(packet: dict[str, Any]) -> None:
    required = {
        "authority_locks",
        "blocked_scopes",
        "canonical_hash",
        "created_at_utc",
        "governance_flags",
        "metric_intake_record",
        "preflight_governance_acknowledgements",
        "preflight_projection",
        "provenance",
        "recommended_next_step",
        "renderer_output_declaration",
        "schema_version",
        "source_baseline_vector_pack_hash",
        "source_metric_registry_hash",
        "source_operator_decision_ref",
        "source_webgl_renderer_boundary_hash",
        "validation_rules",
        "preflight_id",
        "preflight_status",
        "preflight_type",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise MetricComputationPreflightValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise MetricComputationPreflightValidationError("invalid_schema_version")
    if packet["preflight_type"] != PREFLIGHT_TYPE:
        raise MetricComputationPreflightValidationError("invalid_preflight_type")
    if packet["preflight_status"] != PREFLIGHT_STATUS:
        raise MetricComputationPreflightValidationError("invalid_preflight_status")

    # RENDERER_BOUNDARY_CHAIN_CHECK
    if packet["source_webgl_renderer_boundary_hash"] != SOURCE_WEBGL_RENDERER_BOUNDARY_HASH:
        raise MetricComputationPreflightValidationError(
            "source_webgl_renderer_boundary_hash_mismatch"
        )
    if packet["source_metric_registry_hash"] != SOURCE_METRIC_REGISTRY_HASH:
        raise MetricComputationPreflightValidationError(
            "source_metric_registry_hash_mismatch"
        )
    if packet["source_baseline_vector_pack_hash"] != SOURCE_BASELINE_VECTOR_PACK_HASH:
        raise MetricComputationPreflightValidationError(
            "source_baseline_vector_pack_hash_mismatch"
        )

    # PREFLIGHT_PROJECTION_COMPLIANCE
    pp = packet.get("preflight_projection", {})
    if not isinstance(pp, dict):
        raise MetricComputationPreflightValidationError(
            "preflight_projection_must_be_dict"
        )
    if pp.get("advisory_only") is not True:
        raise MetricComputationPreflightValidationError(
            "preflight_projection_advisory_only_must_be_true"
        )
    if pp.get("execution_authority") is not False:
        raise MetricComputationPreflightValidationError(
            "preflight_projection_execution_authority_must_be_false"
        )
    if pp.get("emits_metric_values") is not False:
        raise MetricComputationPreflightValidationError(
            "preflight_projection_emits_metric_values_must_be_false"
        )
    if pp.get("forecast_influence") is not False:
        raise MetricComputationPreflightValidationError(
            "preflight_projection_forecast_influence_must_be_false"
        )
    if pp.get("metric_computation_status") != "PREFLIGHT_BOUNDARY_ONLY":
        raise MetricComputationPreflightValidationError(
            "preflight_projection_metric_computation_status_must_be_PREFLIGHT_BOUNDARY_ONLY"
        )
    if pp.get("projection_only") is not True:
        raise MetricComputationPreflightValidationError(
            "preflight_projection_projection_only_must_be_true"
        )
    if pp.get("preflight_only") is not True:
        raise MetricComputationPreflightValidationError(
            "preflight_projection_preflight_only_must_be_true"
        )

    # PREFLIGHT_GOVERNANCE_ACKNOWLEDGEMENT_CHECK
    ack = packet.get("preflight_governance_acknowledgements", {})
    for key in REQUIRED_PREFLIGHT_ACKNOWLEDGEMENT_KEYS:
        if ack.get(key) is not True:
            raise MetricComputationPreflightValidationError(
                f"preflight_governance_acknowledgement_must_be_true:{key}"
            )

    # OUTPUT_DECLARATION_COMPLIANCE
    od = packet["renderer_output_declaration"]
    for flag in LOCKED_FALSE_OUTPUT_FLAGS:
        if od.get(flag) is not False:
            raise MetricComputationPreflightValidationError(
                f"renderer_output_declaration_{flag}_must_be_false"
            )
    if od.get("emits_planning_metadata") is not True:
        raise MetricComputationPreflightValidationError(
            "renderer_output_declaration_emits_planning_metadata_must_be_true"
        )
    if od.get("execution_authority") is not False:
        raise MetricComputationPreflightValidationError(
            "renderer_output_declaration_execution_authority_must_be_false"
        )
    if od.get("forecast_influence") is not False:
        raise MetricComputationPreflightValidationError(
            "renderer_output_declaration_forecast_influence_must_be_false"
        )

    # SOURCE_REF_PRESERVATION_CHECK — blocked scopes
    present_scopes = set(packet["blocked_scopes"])
    for scope in REQUIRED_BLOCKED_SCOPES:
        if scope not in present_scopes:
            raise MetricComputationPreflightValidationError(
                f"missing_required_blocked_scope:{scope}"
            )

    # AUTHORITY_LOCK_SCAN
    locks = packet["authority_locks"]
    for key in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(key) is not False:
            raise MetricComputationPreflightValidationError(
                f"authority_lock_must_be_false:{key}"
            )
    for key in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(key) is not True:
            raise MetricComputationPreflightValidationError(
                f"authority_lock_must_be_true:{key}"
            )

    # GOVERNANCE_FALSE_FLAG_SCAN
    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise MetricComputationPreflightValidationError(
                f"governance_flag_must_be_false:{flag}"
            )

    if (
        not isinstance(packet.get("recommended_next_step"), str)
        or not packet["recommended_next_step"].strip()
    ):
        raise MetricComputationPreflightValidationError(
            "recommended_next_step_must_be_non_empty_string"
        )

    # NO_RUNTIME_MUTATION_SCAN
    _assert_provenance_safe(packet["provenance"])


def compute_metric_computation_preflight_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_metric_computation_preflight(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_metric_computation_preflight(payload: dict[str, Any]) -> dict[str, Any]:
    viewmodel_ref = payload.get("viewmodel_ref", {})
    preflight_projection = payload.get("preflight_projection") or build_preflight_projection(
        viewmodel_ref
    )
    blocked_scopes = sorted(payload.get("blocked_scopes", default_blocked_scopes()))
    validation_rules = sorted(payload.get("validation_rules", default_validation_rules()))
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "preflight_type": PREFLIGHT_TYPE,
        "preflight_id": payload.get("preflight_id", PREFLIGHT_ID),
        "preflight_status": PREFLIGHT_STATUS,
        "source_webgl_renderer_boundary_hash": SOURCE_WEBGL_RENDERER_BOUNDARY_HASH,
        "source_metric_registry_hash": SOURCE_METRIC_REGISTRY_HASH,
        "source_baseline_vector_pack_hash": SOURCE_BASELINE_VECTOR_PACK_HASH,
        "preflight_projection": preflight_projection,
        "blocked_scopes": blocked_scopes,
        "validation_rules": validation_rules,
    }
    base.pop("viewmodel_ref", None)
    base["canonical_hash"] = compute_metric_computation_preflight_hash(base)
    validate_metric_computation_preflight(base)
    return _finalize(base)
