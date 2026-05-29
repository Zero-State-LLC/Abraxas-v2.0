"""Core builder for AAL-Viz Geometric Renderer SVG Boundary artifact."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "AALVizGeometricRendererSVG.v1"
RENDERER_SVG_TYPE = "AAL_VIZ_GEOMETRIC_RENDERER_SVG_BOUNDARY"
RENDERER_SVG_ID = "aal_viz_geometric_renderer_svg_001"
RENDERER_SVG_STATUS = "RENDERER_SVG_BOUNDARY_DEFINED"

SOURCE_RENDERER_BOUNDARY_HASH = (
    "7b9fb8dc6d03e339b78a28aac83ba3be4a6c6cd6ac7848fadba1262a34572e1b"
)

ALLOWED_VALIDATION_RULES = (
    "AUTHORITY_LOCK_SCAN",
    "GOVERNANCE_FALSE_FLAG_SCAN",
    "NO_RUNTIME_MUTATION_SCAN",
    "OUTPUT_DECLARATION_COMPLIANCE",
    "RENDERER_BOUNDARY_CHAIN_CHECK",
    "SCHEMA_VALIDATION",
    "SOURCE_REF_PRESERVATION_CHECK",
    "SVG_WELLFORMEDNESS_CHECK",
)

REQUIRED_BLOCKED_SCOPES = (
    "canvas_renderer_implementation",
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
    "canvas_renderer_implementation_authorized",
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
    "emits_canvas",
    "emits_forecast_inputs",
    "emits_metric_values",
    "emits_rendered_output",
    "emits_runtime_controls",
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


class AALVizGeometricRendererSVGValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _assert_provenance_safe(provenance: dict[str, Any]) -> None:
    lowered = json.dumps(provenance).lower()
    for token in FORBIDDEN_PROVENANCE_TOKENS:
        if token in lowered:
            raise AALVizGeometricRendererSVGValidationError(
                f"forbidden_provenance_reference_detected:{token}"
            )


def build_svg_projection(viewmodel_ref: dict[str, Any]) -> str:
    """Construct a deterministic, advisory-only SVG projection string."""
    schema_version = _xml_escape(str(viewmodel_ref.get("schema_version", "")))
    title = _xml_escape(str(viewmodel_ref.get("title", "")))
    source_hash = _xml_escape(str(viewmodel_ref.get("source_hash", "")))
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<!-- advisory-only projection surface: no display rendering authorized -->",
        '<svg xmlns="http://www.w3.org/2000/svg" version="1.1"',
        '     data-advisory-only="true"',
        '     data-projection-only="true"',
        f'     data-schema-version="{schema_version}"',
        f'     data-source-hash="{source_hash}">',
        f"  <title>{title}</title>",
        "  <desc>projection-only | advisory-only | no display rendering authorized</desc>",
        '  <g id="boundary-projection">',
        f'    <text id="schema-version-label">{schema_version}</text>',
        "  </g>",
        "</svg>",
    ]
    return "\n".join(lines)


def validate_svg_wellformedness(svg_string: str) -> None:
    try:
        ET.fromstring(svg_string.split("?>", 1)[-1].strip())
    except ET.ParseError as exc:
        raise AALVizGeometricRendererSVGValidationError(
            f"svg_wellformedness_check_failed:{exc}"
        ) from exc


def default_svg_intake_record(viewmodel_ref: dict[str, Any] | None = None) -> dict[str, Any]:
    vr = viewmodel_ref or {}
    return {
        "execution_authority": False,
        "input_fields_accepted": sorted(
            ["adapter_status", "projection_boundary_id", "viewmodel_ref"]
        ),
        "ordering_applied": "CANONICAL_JSON_SORT",
        "projection_only": True,
        "svg_generation_status": "BOUNDARY_PROJECTION_ONLY",
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
        "emits_svg": True,
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
        "canvas_renderer_implementation_authorized": False,
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


def validate_aal_viz_geometric_renderer_svg(packet: dict[str, Any]) -> None:
    required = {
        "authority_locks",
        "blocked_scopes",
        "canonical_hash",
        "created_at_utc",
        "governance_flags",
        "provenance",
        "recommended_next_step",
        "renderer_output_declaration",
        "renderer_svg_id",
        "renderer_svg_status",
        "renderer_svg_type",
        "schema_version",
        "source_operator_decision_ref",
        "source_renderer_boundary_hash",
        "svg_intake_record",
        "svg_projection",
        "validation_rules",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise AALVizGeometricRendererSVGValidationError(f"missing_required_fields:{missing}")

    if packet["schema_version"] != SCHEMA_VERSION:
        raise AALVizGeometricRendererSVGValidationError("invalid_schema_version")
    if packet["renderer_svg_type"] != RENDERER_SVG_TYPE:
        raise AALVizGeometricRendererSVGValidationError("invalid_renderer_svg_type")
    if packet["renderer_svg_status"] != RENDERER_SVG_STATUS:
        raise AALVizGeometricRendererSVGValidationError("invalid_renderer_svg_status")

    # RENDERER_BOUNDARY_CHAIN_CHECK
    if packet["source_renderer_boundary_hash"] != SOURCE_RENDERER_BOUNDARY_HASH:
        raise AALVizGeometricRendererSVGValidationError(
            "source_renderer_boundary_hash_mismatch"
        )

    # SVG_WELLFORMEDNESS_CHECK
    svg_str = packet.get("svg_projection", "")
    if not svg_str:
        raise AALVizGeometricRendererSVGValidationError("svg_projection_must_be_non_empty")
    validate_svg_wellformedness(svg_str)

    # OUTPUT_DECLARATION_COMPLIANCE
    od = packet["renderer_output_declaration"]
    for flag in LOCKED_FALSE_OUTPUT_FLAGS:
        if od.get(flag) is not False:
            raise AALVizGeometricRendererSVGValidationError(
                f"renderer_output_declaration_{flag}_must_be_false"
            )
    if od.get("emits_svg") is not True:
        raise AALVizGeometricRendererSVGValidationError(
            "renderer_output_declaration_emits_svg_must_be_true"
        )
    if od.get("emits_planning_metadata") is not True:
        raise AALVizGeometricRendererSVGValidationError(
            "renderer_output_declaration_emits_planning_metadata_must_be_true"
        )
    if od.get("execution_authority") is not False:
        raise AALVizGeometricRendererSVGValidationError(
            "renderer_output_declaration_execution_authority_must_be_false"
        )

    # SOURCE_REF_PRESERVATION_CHECK — blocked scopes
    present_scopes = set(packet["blocked_scopes"])
    for scope in REQUIRED_BLOCKED_SCOPES:
        if scope not in present_scopes:
            raise AALVizGeometricRendererSVGValidationError(
                f"missing_required_blocked_scope:{scope}"
            )

    # AUTHORITY_LOCK_SCAN
    locks = packet["authority_locks"]
    for key in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(key) is not False:
            raise AALVizGeometricRendererSVGValidationError(
                f"authority_lock_must_be_false:{key}"
            )
    for key in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(key) is not True:
            raise AALVizGeometricRendererSVGValidationError(
                f"authority_lock_must_be_true:{key}"
            )

    # GOVERNANCE_FALSE_FLAG_SCAN
    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise AALVizGeometricRendererSVGValidationError(
                f"governance_flag_must_be_false:{flag}"
            )

    if (
        not isinstance(packet.get("recommended_next_step"), str)
        or not packet["recommended_next_step"].strip()
    ):
        raise AALVizGeometricRendererSVGValidationError(
            "recommended_next_step_must_be_non_empty_string"
        )

    # NO_RUNTIME_MUTATION_SCAN
    _assert_provenance_safe(packet["provenance"])


def compute_aal_viz_geometric_renderer_svg_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_aal_viz_geometric_renderer_svg(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_aal_viz_geometric_renderer_svg(payload: dict[str, Any]) -> dict[str, Any]:
    viewmodel_ref = payload.get("viewmodel_ref", {})
    svg_projection = payload.get("svg_projection") or build_svg_projection(viewmodel_ref)
    blocked_scopes = sorted(payload.get("blocked_scopes", default_blocked_scopes()))
    validation_rules = sorted(payload.get("validation_rules", default_validation_rules()))
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "renderer_svg_type": RENDERER_SVG_TYPE,
        "renderer_svg_id": payload.get("renderer_svg_id", RENDERER_SVG_ID),
        "renderer_svg_status": RENDERER_SVG_STATUS,
        "source_renderer_boundary_hash": SOURCE_RENDERER_BOUNDARY_HASH,
        "svg_projection": svg_projection,
        "blocked_scopes": blocked_scopes,
        "validation_rules": validation_rules,
    }
    base.pop("viewmodel_ref", None)
    base["canonical_hash"] = compute_aal_viz_geometric_renderer_svg_hash(base)
    validate_aal_viz_geometric_renderer_svg(base)
    return _finalize(base)
