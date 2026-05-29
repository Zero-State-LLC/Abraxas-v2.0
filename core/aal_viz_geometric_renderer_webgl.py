"""Core builder for AAL-Viz Geometric Renderer WebGL Boundary artifact."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "AALVizGeometricRendererWebGL.v1"
RENDERER_WEBGL_TYPE = "AAL_VIZ_GEOMETRIC_RENDERER_WEBGL_BOUNDARY"
RENDERER_WEBGL_ID = "aal_viz_geometric_renderer_webgl_001"
RENDERER_WEBGL_STATUS = "RENDERER_WEBGL_BOUNDARY_DEFINED"

SOURCE_CANVAS_RENDERER_BOUNDARY_HASH = (
    "f22a540c6fab6b45fe301339d6b28471489be3725078e4c8942d64afa2550d1d"
)

ALLOWED_VALIDATION_RULES = (
    "AUTHORITY_LOCK_SCAN",
    "GOVERNANCE_FALSE_FLAG_SCAN",
    "NO_RUNTIME_MUTATION_SCAN",
    "OUTPUT_DECLARATION_COMPLIANCE",
    "RENDERER_BOUNDARY_CHAIN_CHECK",
    "SCHEMA_VALIDATION",
    "SOURCE_REF_PRESERVATION_CHECK",
    "WEBGL_PROJECTION_COMPLIANCE",
)

REQUIRED_BLOCKED_SCOPES = (
    "canon_promotion",
    "forecast_authority",
    "inference_authority",
    "metric_computation",
    "p43_surface_lanes",
    "production_activation",
    "renderer_code",
    "runtime_mutation",
)

LOCKED_FALSE_AUTHORITY_KEYS = (
    "baseline_mutation",
    "canon_promotion",
    "governance_authority_mutation",
    "metric_computation_authorized",
    "p43_surface_lanes_authorized",
    "production_activation",
    "runtime_mutation",
    "scheduler_mutation",
    "work_package_definition_only",
)

LOCKED_TRUE_AUTHORITY_KEYS = (
    "advisory_only",
    "canvas_renderer_implementation_authorized",
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
)

FORBIDDEN_PROVENANCE_TOKENS = (
    "cache",
    "callable",
    "executable",
    "forecast",
    "inference",
    "metric-computation",
    "route-control",
    "runtime",
    "scheduler",
    "ui",
)


class AALVizGeometricRendererWebGLValidationError(ValueError):
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
            raise AALVizGeometricRendererWebGLValidationError(
                f"forbidden_provenance_reference_detected:{token}"
            )


def build_webgl_projection(viewmodel_ref: dict[str, Any]) -> dict[str, Any]:
    """Construct a deterministic, advisory-only WebGL boundary projection."""
    return _finalize(
        {
            "advisory_only": True,
            "data_source_hash": str(viewmodel_ref.get("source_hash", "")),
            "execution_authority": False,
            "projection_only": True,
            "schema_version": str(viewmodel_ref.get("schema_version", "")),
            "surface_type": "WEBGL_BOUNDARY",
            "title": str(viewmodel_ref.get("title", "")),
            "webgl_generation_status": "BOUNDARY_PROJECTION_ONLY",
        }
    )


def default_webgl_intake_record(viewmodel_ref: dict[str, Any] | None = None) -> dict[str, Any]:
    vr = viewmodel_ref or {}
    return {
        "execution_authority": False,
        "input_fields_accepted": sorted(
            ["adapter_status", "projection_boundary_id", "viewmodel_ref"]
        ),
        "ordering_applied": "CANONICAL_JSON_SORT",
        "projection_only": True,
        "viewmodel_schema_version": vr.get("schema_version", ""),
        "webgl_generation_status": "BOUNDARY_PROJECTION_ONLY",
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
        "emits_webgl": True,
        "execution_authority": False,
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
        "metric_computation_authorized": False,
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


def validate_aal_viz_geometric_renderer_webgl(packet: dict[str, Any]) -> None:
    required = {
        "authority_locks",
        "blocked_scopes",
        "canonical_hash",
        "created_at_utc",
        "governance_flags",
        "provenance",
        "recommended_next_step",
        "renderer_output_declaration",
        "renderer_webgl_id",
        "renderer_webgl_status",
        "renderer_webgl_type",
        "schema_version",
        "source_canvas_renderer_boundary_hash",
        "source_operator_decision_ref",
        "validation_rules",
        "webgl_intake_record",
        "webgl_projection",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise AALVizGeometricRendererWebGLValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise AALVizGeometricRendererWebGLValidationError("invalid_schema_version")
    if packet["renderer_webgl_type"] != RENDERER_WEBGL_TYPE:
        raise AALVizGeometricRendererWebGLValidationError("invalid_renderer_webgl_type")
    if packet["renderer_webgl_status"] != RENDERER_WEBGL_STATUS:
        raise AALVizGeometricRendererWebGLValidationError("invalid_renderer_webgl_status")

    # RENDERER_BOUNDARY_CHAIN_CHECK
    if packet["source_canvas_renderer_boundary_hash"] != SOURCE_CANVAS_RENDERER_BOUNDARY_HASH:
        raise AALVizGeometricRendererWebGLValidationError(
            "source_canvas_renderer_boundary_hash_mismatch"
        )

    # WEBGL_PROJECTION_COMPLIANCE
    wp = packet.get("webgl_projection", {})
    if not isinstance(wp, dict):
        raise AALVizGeometricRendererWebGLValidationError(
            "webgl_projection_must_be_dict"
        )
    if wp.get("advisory_only") is not True:
        raise AALVizGeometricRendererWebGLValidationError(
            "webgl_projection_advisory_only_must_be_true"
        )
    if wp.get("execution_authority") is not False:
        raise AALVizGeometricRendererWebGLValidationError(
            "webgl_projection_execution_authority_must_be_false"
        )
    if wp.get("webgl_generation_status") != "BOUNDARY_PROJECTION_ONLY":
        raise AALVizGeometricRendererWebGLValidationError(
            "webgl_projection_webgl_generation_status_must_be_BOUNDARY_PROJECTION_ONLY"
        )
    if wp.get("surface_type") != "WEBGL_BOUNDARY":
        raise AALVizGeometricRendererWebGLValidationError(
            "webgl_projection_surface_type_must_be_WEBGL_BOUNDARY"
        )
    if wp.get("projection_only") is not True:
        raise AALVizGeometricRendererWebGLValidationError(
            "webgl_projection_projection_only_must_be_true"
        )

    # OUTPUT_DECLARATION_COMPLIANCE
    od = packet["renderer_output_declaration"]
    for flag in LOCKED_FALSE_OUTPUT_FLAGS:
        if od.get(flag) is not False:
            raise AALVizGeometricRendererWebGLValidationError(
                f"renderer_output_declaration_{flag}_must_be_false"
            )
    if od.get("emits_webgl") is not True:
        raise AALVizGeometricRendererWebGLValidationError(
            "renderer_output_declaration_emits_webgl_must_be_true"
        )
    if od.get("emits_planning_metadata") is not True:
        raise AALVizGeometricRendererWebGLValidationError(
            "renderer_output_declaration_emits_planning_metadata_must_be_true"
        )
    if od.get("execution_authority") is not False:
        raise AALVizGeometricRendererWebGLValidationError(
            "renderer_output_declaration_execution_authority_must_be_false"
        )

    # SOURCE_REF_PRESERVATION_CHECK — blocked scopes
    present_scopes = set(packet["blocked_scopes"])
    for scope in REQUIRED_BLOCKED_SCOPES:
        if scope not in present_scopes:
            raise AALVizGeometricRendererWebGLValidationError(
                f"missing_required_blocked_scope:{scope}"
            )

    # AUTHORITY_LOCK_SCAN
    locks = packet["authority_locks"]
    for key in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(key) is not False:
            raise AALVizGeometricRendererWebGLValidationError(
                f"authority_lock_must_be_false:{key}"
            )
    for key in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(key) is not True:
            raise AALVizGeometricRendererWebGLValidationError(
                f"authority_lock_must_be_true:{key}"
            )

    # GOVERNANCE_FALSE_FLAG_SCAN
    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise AALVizGeometricRendererWebGLValidationError(
                f"governance_flag_must_be_false:{flag}"
            )

    if (
        not isinstance(packet.get("recommended_next_step"), str)
        or not packet["recommended_next_step"].strip()
    ):
        raise AALVizGeometricRendererWebGLValidationError(
            "recommended_next_step_must_be_non_empty_string"
        )

    # NO_RUNTIME_MUTATION_SCAN
    _assert_provenance_safe(packet["provenance"])


def compute_aal_viz_geometric_renderer_webgl_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_aal_viz_geometric_renderer_webgl(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_aal_viz_geometric_renderer_webgl(payload: dict[str, Any]) -> dict[str, Any]:
    viewmodel_ref = payload.get("viewmodel_ref", {})
    webgl_projection = payload.get("webgl_projection") or build_webgl_projection(
        viewmodel_ref
    )
    blocked_scopes = sorted(payload.get("blocked_scopes", default_blocked_scopes()))
    validation_rules = sorted(payload.get("validation_rules", default_validation_rules()))
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "renderer_webgl_type": RENDERER_WEBGL_TYPE,
        "renderer_webgl_id": payload.get("renderer_webgl_id", RENDERER_WEBGL_ID),
        "renderer_webgl_status": RENDERER_WEBGL_STATUS,
        "source_canvas_renderer_boundary_hash": SOURCE_CANVAS_RENDERER_BOUNDARY_HASH,
        "webgl_projection": webgl_projection,
        "blocked_scopes": blocked_scopes,
        "validation_rules": validation_rules,
    }
    base.pop("viewmodel_ref", None)
    base["canonical_hash"] = compute_aal_viz_geometric_renderer_webgl_hash(base)
    validate_aal_viz_geometric_renderer_webgl(base)
    return _finalize(base)
