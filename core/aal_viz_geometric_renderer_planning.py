from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "AALVizGeometricRendererPlanning.v1"
PLANNING_TYPE = "AAL_VIZ_GEOMETRIC_RENDERER_PLANNING"

ALLOWED_SURFACE_FAMILIES = (
    "MANIFOLD_TRANSPORT",
    "METRIC_DISTANCE_PANEL",
    "HYSTERESIS_MEMORY",
    "COUNTERFACTUAL_BRANCHING",
    "HEAVY_TAIL_ANOMALY",
    "RESERVOIR_STATE_SPACE",
    "HYPERVECTOR_TOPOLOGY",
    "TRUST_GEOMETRY",
    "PHASE_STATE_TRANSITION",
    "YGGDRASIL_ROUTE_OVERLAY",
    "MULTI_SURFACE_PLANNING",
)
ALLOWED_INTENDED_LANES = ("PROJECTION", "SHADOW", "OBSERVATION_ONLY")
ALLOWED_PLANNING_STAGES = (
    "REQUIREMENTS_ONLY",
    "CONTRACT_ONLY",
    "RENDERER_NOT_IMPLEMENTED",
    "IMPLEMENTATION_PLANNING_ONLY",
)
ALLOWED_IMPLEMENTATION_STATUS = (
    "PLANNED_ONLY",
    "CONTRACT_DECLARED",
    "RENDERER_NOT_IMPLEMENTED",
    "BLOCKED_PENDING_OPERATOR_REVIEW",
)
ALLOWED_EVIDENCE_REQUIRED = (
    "PROJECTION_SPEC_REF_REQUIRED",
    "METRIC_REGISTRY_REF_REQUIRED",
    "TEST_VECTOR_REF_REQUIRED",
    "REPLAY_RECEIPT_REF_REQUIRED",
    "PROVENANCE_REF_REQUIRED",
    "NO_RUNTIME_EFFECT_REQUIRED",
)
LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
    "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
)
FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast", "rendering", "ui", "svg", "webgl", "canvas", "metric-computation", "route-control",
)


class AALVizGeometricRendererPlanningValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_planned_surfaces() -> list[dict[str, Any]]:
    return [
        {
            "surface_id": "surface-001-multi-surface-plan",
            "surface_family": "MULTI_SURFACE_PLANNING",
            "description": "Planning-only aggregate surface for future geometric renderer tracks.",
            "source_placeholder_refs": ["GeometricProjectionSpec.v1:projection-spec-001"],
            "visual_requirements": ["deterministic_layer_ordering", "projection_only_advisory_posture"],
            "implementation_status": "RENDERER_NOT_IMPLEMENTED",
            "evidence_required": "PROJECTION_SPEC_REF_REQUIRED",
        }
    ]


def default_renderer_constraints() -> dict[str, bool]:
    return {
        "renderer_implemented": False,
        "ui_component_added": False,
        "svg_renderer_added": False,
        "webgl_renderer_added": False,
        "canvas_renderer_added": False,
        "metric_computation_added": False,
        "runtime_controls_added": False,
        "forecast_controls_added": False,
        "route_controls_added": False,
        "scheduler_controls_added": False,
    }


def default_implementation_gates() -> dict[str, bool]:
    return {
        "requires_operator_review": True,
        "requires_projection_spec": True,
        "requires_test_vectors": True,
        "requires_replay_receipts": True,
        "requires_no_authority_scan": True,
        "renderer_implementation_blocked": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_rendered_output": False,
        "emits_ui_controls": False,
        "emits_metric_values": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_planning_metadata": True,
        "emits_observation_notes": True,
    }


def _assert_provenance_safe(value: Any) -> None:
    if isinstance(value, dict):
        for v in value.values():
            _assert_provenance_safe(v)
    elif isinstance(value, list):
        for v in value:
            _assert_provenance_safe(v)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(token in lowered for token in FORBIDDEN_PROVENANCE_TOKENS):
            raise AALVizGeometricRendererPlanningValidationError("forbidden_provenance_reference_detected")


def validate_aal_viz_geometric_renderer_planning(packet: dict[str, Any]) -> None:
    required = {"schema_version", "planning_id", "planning_type", "source_projection_spec_refs", "source_metric_registry_refs", "source_test_vector_pack_refs", "source_oracle_replay_receipt_refs", "source_yggdrasil_replay_receipt_refs", "renderer_scope", "planned_surfaces", "renderer_constraints", "implementation_gates", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash"}
    missing = sorted(required - packet.keys())
    if missing:
        raise AALVizGeometricRendererPlanningValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise AALVizGeometricRendererPlanningValidationError("invalid_schema_version")
    if packet["planning_type"] != PLANNING_TYPE:
        raise AALVizGeometricRendererPlanningValidationError("invalid_planning_type")

    scope = packet["renderer_scope"]
    if scope.get("target_surface_family") not in ALLOWED_SURFACE_FAMILIES:
        raise AALVizGeometricRendererPlanningValidationError("unknown_target_surface_family")
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANES:
        raise AALVizGeometricRendererPlanningValidationError("unknown_intended_lane")
    if scope.get("planning_stage") not in ALLOWED_PLANNING_STAGES:
        raise AALVizGeometricRendererPlanningValidationError("unknown_planning_stage")

    surfaces = packet["planned_surfaces"]
    if not surfaces:
        raise AALVizGeometricRendererPlanningValidationError("planned_surfaces_must_be_non_empty")
    seen: set[str] = set()
    for s in sorted(surfaces, key=lambda x: x["surface_id"]):
        sid = s["surface_id"]
        if sid in seen:
            raise AALVizGeometricRendererPlanningValidationError("duplicate_surface_id")
        seen.add(sid)
        if s["surface_family"] not in ALLOWED_SURFACE_FAMILIES:
            raise AALVizGeometricRendererPlanningValidationError("unknown_surface_family")
        if s["implementation_status"] not in ALLOWED_IMPLEMENTATION_STATUS:
            raise AALVizGeometricRendererPlanningValidationError("unknown_implementation_status")
        if s["evidence_required"] not in ALLOWED_EVIDENCE_REQUIRED:
            raise AALVizGeometricRendererPlanningValidationError("unknown_evidence_required")

    if packet["renderer_constraints"] != default_renderer_constraints():
        raise AALVizGeometricRendererPlanningValidationError("invalid_renderer_constraints")
    if packet["implementation_gates"] != default_implementation_gates():
        raise AALVizGeometricRendererPlanningValidationError("invalid_implementation_gates")
    if packet["output_contract"] != default_output_contract():
        raise AALVizGeometricRendererPlanningValidationError("invalid_output_contract")
    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise AALVizGeometricRendererPlanningValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(packet["provenance"])


def compute_aal_viz_geometric_renderer_planning_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_aal_viz_geometric_renderer_planning(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_aal_viz_geometric_renderer_planning(payload: dict[str, Any]) -> dict[str, Any]:
    planned_surfaces = sorted(payload.get("planned_surfaces", default_planned_surfaces()), key=lambda x: x["surface_id"])
    for surface in planned_surfaces:
        surface["source_placeholder_refs"] = sorted(surface.get("source_placeholder_refs", []))
        surface["visual_requirements"] = sorted(surface.get("visual_requirements", []))
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "planning_type": PLANNING_TYPE,
        "source_projection_spec_refs": sorted(payload.get("source_projection_spec_refs", [])),
        "source_metric_registry_refs": sorted(payload.get("source_metric_registry_refs", [])),
        "source_test_vector_pack_refs": sorted(payload.get("source_test_vector_pack_refs", [])),
        "source_oracle_replay_receipt_refs": sorted(payload.get("source_oracle_replay_receipt_refs", [])),
        "source_yggdrasil_replay_receipt_refs": sorted(payload.get("source_yggdrasil_replay_receipt_refs", [])),
        "planned_surfaces": planned_surfaces,
        "renderer_constraints": payload.get("renderer_constraints", default_renderer_constraints()),
        "implementation_gates": payload.get("implementation_gates", default_implementation_gates()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_aal_viz_geometric_renderer_planning_hash(base)
    validate_aal_viz_geometric_renderer_planning(base)
    return _finalize(base)
