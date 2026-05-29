"""Core builder for AAL-Viz Geometric Renderer Canvas Boundary artifact."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "AALVizGeometricRendererCanvas.v1"
RENDERER_CANVAS_TYPE = "AAL_VIZ_GEOMETRIC_RENDERER_CANVAS_BOUNDARY"
RENDERER_CANVAS_ID = "aal_viz_geometric_renderer_canvas_001"
RENDERER_CANVAS_STATUS = "RENDERER_CANVAS_BOUNDARY_DEFINED"

SOURCE_SVG_RENDERER_BOUNDARY_HASH = (
    "8ed1cc538d8743c24f3c4eb79b0ed66dc4bc6324b43900ca207603dacf289bff"
)

ALLOWED_VALIDATION_RULES = (
    "AUTHORITY_LOCK_SCAN",
    "CANVAS_PROJECTION_COMPLIANCE",
    "GOVERNANCE_FALSE_FLAG_SCAN",
    "NO_RUNTIME_MUTATION_SCAN",
    "OUTPUT_DECLARATION_COMPLIANCE",
    "RENDERER_BOUNDARY_CHAIN_CHECK",
    "SCHEMA_VALIDATION",
    "SOURCE_REF_PRESERVATION_CHECK",
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
    "webgl_renderer_implementation",
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
    "webgl_renderer_implementation_authorized",
    "work_package_definition_only",
)

LOCKED_TRUE_AUTHORITY_KEYS = (
    "advisory_only",
    "canvas_renderer_implementation_authorized",
    "projection_only",
    "renderer_boundary_implementation",
    "svg_renderer_implementation_authorized",
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
    "emits_forecast_inputs",
    "emits_metric_values",
    "emits_rendered_output",
    "emits_runtime_controls",
    "emits_svg",
    "emits_ui_controls",
    "emits_webgl",
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


class AALVizGeometricRendererCanvasValidationError(ValueError):
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
            raise AALVizGeometricRendererCanvasValidationError(
                f"forbidden_provenance_reference_detected:{token}"
            )


def build_canvas_projection(viewmodel_ref: dict[str, Any]) -> dict[str, Any]:
    """Construct a deterministic, advisory-only Canvas boundary projection."""
    return _finalize(
        {
            "advisory_only": True,
            "canvas_generation_status": "BOUNDARY_PROJECTION_ONLY",
            "data_source_hash": str(viewmodel_ref.get("source_hash", "")),
            "execution_authority": False,
            "projection_only": True,
            "schema_version": str(viewmodel_ref.get("schema_version", "")),
            "surface_type": "CANVAS_BOUNDARY",
            "title": str(viewmodel_ref.get("title", "")),
        }
    )


def default_canvas_intake_record(viewmodel_ref: dict[str, Any] | None = None) -> dict[str, Any]:
    vr = viewmodel_ref or {}
    return {
        "canvas_generation_status": "BOUNDARY_PROJECTION_ONLY",
        "execution_authority": False,
        "input_fields_accepted": sorted(
            ["adapter_status", "projection_boundary_id", "viewmodel_ref"]
        ),
        "ordering_applied": "CANONICAL_JSON_SORT",
        "projection_only": True,
        "viewmodel_schema_version": vr.get("schema_version", ""),
    }


def default_renderer_output_declaration() -> dict[str, Any]:
    return {
        "emits_canvas": True,
        "emits_forecast_inputs": False,
        "emits_metric_values": False,
        "emits_planning_metadata": True,
        "emits_rendered_output": False,
        "emits_runtime_controls": False,
        "emits_svg": False,
        "emits_ui_controls": False,
        "emits_webgl": False,
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
        "webgl_renderer_implementation_authorized": False,
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


def validate_aal_viz_geometric_renderer_canvas(packet: dict[str, Any]) -> None:
    required = {
        "authority_locks",
        "blocked_scopes",
        "canonical_hash",
        "canvas_intake_record",
        "canvas_projection",
        "created_at_utc",
        "governance_flags",
        "provenance",
        "recommended_next_step",
        "renderer_canvas_id",
        "renderer_canvas_status",
        "renderer_canvas_type",
        "renderer_output_declaration",
        "schema_version",
        "source_operator_decision_ref",
        "source_svg_renderer_boundary_hash",
        "validation_rules",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise AALVizGeometricRendererCanvasValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise AALVizGeometricRendererCanvasValidationError("invalid_schema_version")
    if packet["renderer_canvas_type"] != RENDERER_CANVAS_TYPE:
        raise AALVizGeometricRendererCanvasValidationError("invalid_renderer_canvas_type")
    if packet["renderer_canvas_status"] != RENDERER_CANVAS_STATUS:
        raise AALVizGeometricRendererCanvasValidationError("invalid_renderer_canvas_status")

    # RENDERER_BOUNDARY_CHAIN_CHECK
    if packet["source_svg_renderer_boundary_hash"] != SOURCE_SVG_RENDERER_BOUNDARY_HASH:
        raise AALVizGeometricRendererCanvasValidationError(
            "source_svg_renderer_boundary_hash_mismatch"
        )

    # CANVAS_PROJECTION_COMPLIANCE
    cp = packet.get("canvas_projection", {})
    if not isinstance(cp, dict):
        raise AALVizGeometricRendererCanvasValidationError(
            "canvas_projection_must_be_dict"
        )
    if cp.get("advisory_only") is not True:
        raise AALVizGeometricRendererCanvasValidationError(
            "canvas_projection_advisory_only_must_be_true"
        )
    if cp.get("execution_authority") is not False:
        raise AALVizGeometricRendererCanvasValidationError(
            "canvas_projection_execution_authority_must_be_false"
        )
    if cp.get("canvas_generation_status") != "BOUNDARY_PROJECTION_ONLY":
        raise AALVizGeometricRendererCanvasValidationError(
            "canvas_projection_canvas_generation_status_must_be_BOUNDARY_PROJECTION_ONLY"
        )
    if cp.get("surface_type") != "CANVAS_BOUNDARY":
        raise AALVizGeometricRendererCanvasValidationError(
            "canvas_projection_surface_type_must_be_CANVAS_BOUNDARY"
        )
    if cp.get("projection_only") is not True:
        raise AALVizGeometricRendererCanvasValidationError(
            "canvas_projection_projection_only_must_be_true"
        )

    # OUTPUT_DECLARATION_COMPLIANCE
    od = packet["renderer_output_declaration"]
    for flag in LOCKED_FALSE_OUTPUT_FLAGS:
        if od.get(flag) is not False:
            raise AALVizGeometricRendererCanvasValidationError(
                f"renderer_output_declaration_{flag}_must_be_false"
            )
    if od.get("emits_canvas") is not True:
        raise AALVizGeometricRendererCanvasValidationError(
            "renderer_output_declaration_emits_canvas_must_be_true"
        )
    if od.get("emits_planning_metadata") is not True:
        raise AALVizGeometricRendererCanvasValidationError(
            "renderer_output_declaration_emits_planning_metadata_must_be_true"
        )
    if od.get("execution_authority") is not False:
        raise AALVizGeometricRendererCanvasValidationError(
            "renderer_output_declaration_execution_authority_must_be_false"
        )

    # SOURCE_REF_PRESERVATION_CHECK — blocked scopes
    present_scopes = set(packet["blocked_scopes"])
    for scope in REQUIRED_BLOCKED_SCOPES:
        if scope not in present_scopes:
            raise AALVizGeometricRendererCanvasValidationError(
                f"missing_required_blocked_scope:{scope}"
            )

    # AUTHORITY_LOCK_SCAN
    locks = packet["authority_locks"]
    for key in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(key) is not False:
            raise AALVizGeometricRendererCanvasValidationError(
                f"authority_lock_must_be_false:{key}"
            )
    for key in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(key) is not True:
            raise AALVizGeometricRendererCanvasValidationError(
                f"authority_lock_must_be_true:{key}"
            )

    # GOVERNANCE_FALSE_FLAG_SCAN
    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise AALVizGeometricRendererCanvasValidationError(
                f"governance_flag_must_be_false:{flag}"
            )

    if (
        not isinstance(packet.get("recommended_next_step"), str)
        or not packet["recommended_next_step"].strip()
    ):
        raise AALVizGeometricRendererCanvasValidationError(
            "recommended_next_step_must_be_non_empty_string"
        )

    # NO_RUNTIME_MUTATION_SCAN
    _assert_provenance_safe(packet["provenance"])


def compute_aal_viz_geometric_renderer_canvas_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_aal_viz_geometric_renderer_canvas(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_aal_viz_geometric_renderer_canvas(payload: dict[str, Any]) -> dict[str, Any]:
    viewmodel_ref = payload.get("viewmodel_ref", {})
    canvas_projection = payload.get("canvas_projection") or build_canvas_projection(
        viewmodel_ref
    )
    blocked_scopes = sorted(payload.get("blocked_scopes", default_blocked_scopes()))
    validation_rules = sorted(payload.get("validation_rules", default_validation_rules()))
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "renderer_canvas_type": RENDERER_CANVAS_TYPE,
        "renderer_canvas_id": payload.get("renderer_canvas_id", RENDERER_CANVAS_ID),
        "renderer_canvas_status": RENDERER_CANVAS_STATUS,
        "source_svg_renderer_boundary_hash": SOURCE_SVG_RENDERER_BOUNDARY_HASH,
        "canvas_projection": canvas_projection,
        "blocked_scopes": blocked_scopes,
        "validation_rules": validation_rules,
    }
    base.pop("viewmodel_ref", None)
    base["canonical_hash"] = compute_aal_viz_geometric_renderer_canvas_hash(base)
    validate_aal_viz_geometric_renderer_canvas(base)
    return _finalize(base)
