from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "AALVizGeometricRendererImplementationPlan.v1"
PLAN_TYPE = "AAL_VIZ_GEOMETRIC_RENDERER_IMPLEMENTATION_PLAN"

ALLOWED_TARGET_RENDERER_FAMILIES = (
    "STATIC_SVG_PLANNING",
    "PROJECTION_SPEC_TO_VIEWMODEL_PLANNING",
    "DASHBOARD_PANEL_PLANNING",
    "MANIFOLD_MAP_PLANNING",
    "ROUTE_OVERLAY_PLANNING",
    "MULTI_SURFACE_RENDERER_PLANNING",
)
ALLOWED_INTENDED_LANES = ("PROJECTION", "SHADOW", "OBSERVATION_ONLY")
ALLOWED_IMPLEMENTATION_STAGES = (
    "IMPLEMENTATION_PLAN_ONLY",
    "WORK_PACKAGE_DEFINITION_ONLY",
    "VALIDATION_PLAN_ONLY",
    "BLOCKED_PENDING_OPERATOR_REVIEW",
)
ALLOWED_PACKAGE_TYPES = (
    "VIEWMODEL_ADAPTER_PLAN",
    "STATIC_RENDERER_PLAN",
    "PANEL_LAYOUT_PLAN",
    "COLOR_ENCODING_PLAN",
    "INTERACTION_BOUNDARY_PLAN",
    "VALIDATION_PLAN",
    "NOT_COMPUTABLE_PLAN",
)
ALLOWED_IMPLEMENTATION_STATUSES = (
    "PLANNED_ONLY",
    "NOT_IMPLEMENTED",
    "BLOCKED_PENDING_REVIEW",
)
LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
    "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
)
FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast", "rendering", "ui", "svg", "webgl", "canvas", "metric-computation", "route-control",
)


class AALVizGeometricRendererImplementationPlanValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_renderer_work_packages() -> list[dict[str, Any]]:
    return [
        {
            "package_id": "wp-001-implementation-boundary",
            "package_name": "Implementation boundary and adapter planning",
            "package_type": "VIEWMODEL_ADAPTER_PLAN",
            "description": "Define projection-spec to viewmodel adaptation boundaries without renderer or metric implementation.",
            "source_surface_refs": ["AALVizGeometricRendererPlanning.v1:planning-001", "GeometricProjectionSpec.v1:projection-spec-001"],
            "deliverables": ["adapter_interface_plan", "source_ref_matrix", "deterministic_ordering_contract"],
            "blocked_operations": ["renderer_code", "svg_webgl_canvas_components", "metric_computation"],
            "validation_requirements": ["schema_validation", "governance_false_flag_scan", "no_runtime_mutation_scan"],
            "implementation_status": "PLANNED_ONLY",
        }
    ]


def default_dependency_map() -> dict[str, bool]:
    return {
        "requires_projection_spec": True,
        "requires_renderer_planning": True,
        "requires_test_vectors": True,
        "requires_no_authority_scan": True,
        "requires_replay_receipts": True,
    }


def default_implementation_constraints() -> dict[str, bool]:
    return {
        "renderer_code_added": False,
        "ui_component_added": False,
        "svg_code_added": False,
        "webgl_code_added": False,
        "canvas_code_added": False,
        "metric_computation_added": False,
        "runtime_controls_added": False,
        "route_controls_added": False,
        "forecast_controls_added": False,
        "scheduler_controls_added": False,
    }


def default_validation_plan() -> dict[str, bool]:
    return {
        "requires_snapshot_tests": True,
        "requires_schema_tests": True,
        "requires_no_authority_scan": True,
        "requires_no_metric_computation_check": True,
        "requires_no_runtime_mutation_check": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_code": False,
        "emits_rendered_output": False,
        "emits_ui_controls": False,
        "emits_metric_values": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_implementation_plan": True,
        "emits_work_packages": True,
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
            raise AALVizGeometricRendererImplementationPlanValidationError("forbidden_provenance_reference_detected")


def validate_aal_viz_geometric_renderer_implementation_plan(packet: dict[str, Any]) -> None:
    required = {
        "schema_version", "plan_id", "plan_type", "source_renderer_planning_refs", "source_projection_spec_refs",
        "source_metric_registry_refs", "source_test_vector_pack_refs", "implementation_scope", "renderer_work_packages",
        "dependency_map", "implementation_constraints", "validation_plan", "output_contract", "governance_flags",
        "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise AALVizGeometricRendererImplementationPlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise AALVizGeometricRendererImplementationPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise AALVizGeometricRendererImplementationPlanValidationError("invalid_plan_type")

    scope = packet["implementation_scope"]
    if scope.get("target_renderer_family") not in ALLOWED_TARGET_RENDERER_FAMILIES:
        raise AALVizGeometricRendererImplementationPlanValidationError("unknown_target_renderer_family")
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANES:
        raise AALVizGeometricRendererImplementationPlanValidationError("unknown_intended_lane")
    if scope.get("implementation_stage") not in ALLOWED_IMPLEMENTATION_STAGES:
        raise AALVizGeometricRendererImplementationPlanValidationError("unknown_implementation_stage")

    work_packages = packet["renderer_work_packages"]
    if not work_packages:
        raise AALVizGeometricRendererImplementationPlanValidationError("renderer_work_packages_must_be_non_empty")
    seen: set[str] = set()
    for wp in sorted(work_packages, key=lambda x: x["package_id"]):
        pid = wp["package_id"]
        if pid in seen:
            raise AALVizGeometricRendererImplementationPlanValidationError("duplicate_package_id")
        seen.add(pid)
        if wp["package_type"] not in ALLOWED_PACKAGE_TYPES:
            raise AALVizGeometricRendererImplementationPlanValidationError("unknown_package_type")
        if wp["implementation_status"] not in ALLOWED_IMPLEMENTATION_STATUSES:
            raise AALVizGeometricRendererImplementationPlanValidationError("unknown_implementation_status")

    if packet["dependency_map"] != default_dependency_map():
        raise AALVizGeometricRendererImplementationPlanValidationError("invalid_dependency_map")
    if packet["implementation_constraints"] != default_implementation_constraints():
        raise AALVizGeometricRendererImplementationPlanValidationError("invalid_implementation_constraints")
    if packet["validation_plan"] != default_validation_plan():
        raise AALVizGeometricRendererImplementationPlanValidationError("invalid_validation_plan")
    if packet["output_contract"] != default_output_contract():
        raise AALVizGeometricRendererImplementationPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise AALVizGeometricRendererImplementationPlanValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(packet["provenance"])


def compute_aal_viz_geometric_renderer_implementation_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_aal_viz_geometric_renderer_implementation_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_aal_viz_geometric_renderer_implementation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    work_packages = sorted(payload.get("renderer_work_packages", default_renderer_work_packages()), key=lambda x: x["package_id"])
    for work_package in work_packages:
        for ref_field in ("source_surface_refs", "deliverables", "blocked_operations", "validation_requirements"):
            work_package[ref_field] = sorted(work_package.get(ref_field, []))
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "source_renderer_planning_refs": sorted(payload.get("source_renderer_planning_refs", [])),
        "source_projection_spec_refs": sorted(payload.get("source_projection_spec_refs", [])),
        "source_metric_registry_refs": sorted(payload.get("source_metric_registry_refs", [])),
        "source_test_vector_pack_refs": sorted(payload.get("source_test_vector_pack_refs", [])),
        "renderer_work_packages": work_packages,
        "dependency_map": payload.get("dependency_map", default_dependency_map()),
        "implementation_constraints": payload.get("implementation_constraints", default_implementation_constraints()),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_aal_viz_geometric_renderer_implementation_plan_hash(base)
    validate_aal_viz_geometric_renderer_implementation_plan(base)
    return _finalize(base)
