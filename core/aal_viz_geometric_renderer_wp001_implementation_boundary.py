"""Core builder for AAL-Viz Geometric Renderer WP-001 Implementation Boundary artifact."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "AALVizGeometricRendererWP001ImplementationBoundary.v1"
WORK_PACKAGE_TYPE = "AAL_VIZ_GEOMETRIC_RENDERER_WP001_IMPLEMENTATION_BOUNDARY"
WORK_PACKAGE_ID = "wp-001-implementation-boundary"
IMPLEMENTATION_STAGE = "WORK_PACKAGE_DEFINITION_ONLY"
WP001_STATUS = "WP001_IMPLEMENTATION_BOUNDARY_DEFINED"

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
    "renderer_code_authorized",
    "runtime_mutation",
    "scheduler_mutation",
)

LOCKED_TRUE_AUTHORITY_KEYS = (
    "advisory_only",
    "projection_only",
    "work_package_definition_only",
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

FORBIDDEN_PROVENANCE_TOKENS = (
    "cache",
    "callable",
    "canvas",
    "executable",
    "forecast",
    "inference",
    "metric-computation",
    "rendering",
    "route-control",
    "runtime",
    "scheduler",
    "svg",
    "ui",
    "webgl",
)


class AALVizGeometricRendererWP001ValidationError(ValueError):
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
            raise AALVizGeometricRendererWP001ValidationError(
                f"forbidden_provenance_reference_detected:{token}"
            )


def default_adapter_interface_plan() -> dict[str, Any]:
    return {
        "adapter_status": "BOUNDARY_DECLARED_ONLY",
        "adaptation_boundary": "PROJECTION_SPEC_FIELD_BOUNDARY",
        "declared_input_fields": [
            "canonical_hash",
            "created_at_utc",
            "governance_flags",
            "item_id",
            "observed_summary",
            "provenance",
            "schema_version",
            "title",
        ],
        "declared_output_fields": [
            "adapter_status",
            "projection_boundary_id",
            "viewmodel_ref",
        ],
        "description": (
            "Defines the interface boundary between GeometricProjectionSpec.v1 fields "
            "and the MULTI_SURFACE_RENDERER_PLANNING surface. "
            "No field is mapped to executable renderer logic. "
            "All fields are declared-only advisory references. "
            "Metric computation, renderer code, and SVG/WebGL/canvas components are blocked."
        ),
        "execution_authority": False,
        "field_mapping_policy": "DECLARED_ONLY",
        "interface_id": "adapter-001-projection-spec-to-viewmodel",
        "interface_type": "VIEWMODEL_ADAPTER_PLAN",
        "metric_computation": False,
        "renderer_code": False,
        "source_surface": "GeometricProjectionSpec.v1",
        "target_surface": "MULTI_SURFACE_RENDERER_PLANNING",
    }


def default_deterministic_ordering_contract() -> dict[str, Any]:
    return {
        "contract_id": "ordering-001-projection-spec-canonical",
        "description": (
            "All projection spec fields entering the viewmodel adapter boundary "
            "are ordered by lexicographic field-name sort before hashing. "
            "canonical_hash is excluded from the preimage. "
            "Output is byte-stable across identical inputs and Python versions."
        ),
        "determinism_guarantee": "BYTE_STABLE_ACROSS_RUNS",
        "execution_authority": False,
        "hash_algorithm": "SHA-256",
        "hash_input": "canonical_preimage_excluding_canonical_hash",
        "ordering_basis": "CANONICAL_JSON_SORT",
        "ordering_status": "CONTRACT_DECLARED_ONLY",
        "sort_key": "field_name_lexicographic",
    }


def default_source_reference_matrix() -> list[dict[str, Any]]:
    return [
        {
            "adapter_contribution": "SURFACE_FAMILY_CONSTRAINTS_AND_PLANNING_STAGE",
            "execution_authority": False,
            "ref_id": "ref-001-p43-planning",
            "role": "UPSTREAM_PLANNING_SOURCE",
            "schema_ref": "AALVizGeometricRendererPlanning.v1:aal_viz_geometric_renderer_planning_001",
        },
        {
            "adapter_contribution": "PROJECTION_SPEC_FIELD_DECLARATIONS",
            "execution_authority": False,
            "ref_id": "ref-002-projection-spec",
            "role": "ADAPTER_INPUT_SPEC",
            "schema_ref": "GeometricProjectionSpec.v1:geometric_projection_spec_001",
        },
        {
            "adapter_contribution": "METRIC_OPERATOR_IDENTIFIER_SCOPE",
            "execution_authority": False,
            "ref_id": "ref-003-metric-operator-registry",
            "role": "OPERATOR_SCOPE_BOUNDARY",
            "schema_ref": "MetricOperatorRegistry.v1:metric_operator_registry_001",
        },
        {
            "adapter_contribution": "BASELINE_TEST_VECTOR_BOUNDARY_DECLARATIONS",
            "execution_authority": False,
            "ref_id": "ref-004-test-vector-pack",
            "role": "VALIDATION_BOUNDARY_SOURCE",
            "schema_ref": "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
        },
        {
            "adapter_contribution": "ORACLE_REPLAY_EVIDENCE",
            "execution_authority": False,
            "ref_id": "ref-005-oracle-receipt",
            "role": "REPLAY_EVIDENCE",
            "schema_ref": "OracleGeometricAttachmentReplayReceipt.v1:oracle_geometric_attachment_replay_receipt_001",
        },
        {
            "adapter_contribution": "YGGDRASIL_ROUTE_REPLAY_EVIDENCE",
            "execution_authority": False,
            "ref_id": "ref-006-yggdrasil-receipt",
            "role": "REPLAY_EVIDENCE",
            "schema_ref": "YggdrasilGeometricRouteReplayReceipt.v1:yggdrasil_geometric_route_replay_receipt_001",
        },
    ]


def default_blocked_scopes() -> list[str]:
    return sorted(REQUIRED_BLOCKED_SCOPES)


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "baseline_mutation": False,
        "canon_promotion": False,
        "governance_authority_mutation": False,
        "metric_computation_authorized": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "projection_only": True,
        "renderer_code_authorized": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "work_package_definition_only": True,
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


def validate_aal_viz_geometric_renderer_wp001_implementation_boundary(
    packet: dict[str, Any],
) -> None:
    required = {
        "adapter_interface_plan",
        "authority_locks",
        "blocked_scopes",
        "canonical_hash",
        "created_at_utc",
        "deterministic_ordering_contract",
        "governance_flags",
        "implementation_stage",
        "provenance",
        "recommended_next_step",
        "schema_version",
        "source_operator_decision_ref",
        "source_p44_plan_hash",
        "source_reference_matrix",
        "work_package_id",
        "work_package_type",
        "wp_status",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise AALVizGeometricRendererWP001ValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise AALVizGeometricRendererWP001ValidationError("invalid_schema_version")
    if packet["work_package_type"] != WORK_PACKAGE_TYPE:
        raise AALVizGeometricRendererWP001ValidationError("invalid_work_package_type")
    if packet["work_package_id"] != WORK_PACKAGE_ID:
        raise AALVizGeometricRendererWP001ValidationError("invalid_work_package_id")
    if packet["implementation_stage"] != IMPLEMENTATION_STAGE:
        raise AALVizGeometricRendererWP001ValidationError("invalid_implementation_stage")
    if packet["wp_status"] != WP001_STATUS:
        raise AALVizGeometricRendererWP001ValidationError("invalid_wp_status")

    present_scopes = set(packet["blocked_scopes"])
    for scope in REQUIRED_BLOCKED_SCOPES:
        if scope not in present_scopes:
            raise AALVizGeometricRendererWP001ValidationError(
                f"missing_required_blocked_scope:{scope}"
            )

    locks = packet["authority_locks"]
    for key in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(key) is not False:
            raise AALVizGeometricRendererWP001ValidationError(f"authority_lock_must_be_false:{key}")
    for key in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(key) is not True:
            raise AALVizGeometricRendererWP001ValidationError(f"authority_lock_must_be_true:{key}")

    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise AALVizGeometricRendererWP001ValidationError(f"governance_flag_must_be_false:{flag}")

    if not isinstance(packet["adapter_interface_plan"], dict) or not packet["adapter_interface_plan"]:
        raise AALVizGeometricRendererWP001ValidationError(
            "adapter_interface_plan_must_be_non_empty_dict"
        )
    if (
        not isinstance(packet["deterministic_ordering_contract"], dict)
        or not packet["deterministic_ordering_contract"]
    ):
        raise AALVizGeometricRendererWP001ValidationError(
            "deterministic_ordering_contract_must_be_non_empty_dict"
        )
    if not isinstance(packet["source_reference_matrix"], list) or not packet["source_reference_matrix"]:
        raise AALVizGeometricRendererWP001ValidationError(
            "source_reference_matrix_must_be_non_empty_list"
        )
    if not isinstance(packet.get("recommended_next_step"), str) or not packet["recommended_next_step"].strip():
        raise AALVizGeometricRendererWP001ValidationError(
            "recommended_next_step_must_be_non_empty_string"
        )

    _assert_provenance_safe(packet["provenance"])


def compute_aal_viz_geometric_renderer_wp001_implementation_boundary_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_aal_viz_geometric_renderer_wp001_implementation_boundary(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_aal_viz_geometric_renderer_wp001_implementation_boundary(
    payload: dict[str, Any],
) -> dict[str, Any]:
    blocked_scopes = sorted(payload.get("blocked_scopes", default_blocked_scopes()))
    source_ref_matrix = sorted(
        payload.get("source_reference_matrix", default_source_reference_matrix()),
        key=lambda x: x["ref_id"],
    )
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "work_package_type": WORK_PACKAGE_TYPE,
        "work_package_id": WORK_PACKAGE_ID,
        "implementation_stage": IMPLEMENTATION_STAGE,
        "wp_status": WP001_STATUS,
        "blocked_scopes": blocked_scopes,
        "source_reference_matrix": source_ref_matrix,
    }
    base["canonical_hash"] = compute_aal_viz_geometric_renderer_wp001_implementation_boundary_hash(
        base
    )
    validate_aal_viz_geometric_renderer_wp001_implementation_boundary(base)
    return _finalize(base)
