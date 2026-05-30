from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicTestVectorSchemaPlan.v1"
PLAN_TYPE = "GEODESIC_TEST_VECTOR_SCHEMA_PLAN"
OPERATOR_ID = "GEODESIC"
ALLOWED_SCHEMA_FAMILY = (
    "MIXED_SCHEMA_PLAN",
    "VALID_ONLY_SCHEMA_PLAN",
    "INVALID_ONLY_SCHEMA_PLAN",
)
ALLOWED_INTENDED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_SCHEMA_STAGE = ("SCHEMA_PLAN_ONLY", "SCHEMA_DEFINITION_READY", "FIXTURE_READY")
ALLOWED_IMPLEMENTATION_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation",
    "runtime_authority", "runtime_mutation", "forecast_influence",
    "execution_authority", "token_minting_allowed", "valid_for_execution",
    "activation_approved", "authorization_granted",
)
FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast",
    "scoring", "metric-computation", "metric-value", "geodesic-distance",
    "dijkstra-execution", "numpy", "scipy", "gpu-kernel",
)


class GeodesicTestVectorSchemaPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_valid_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "valid-001",
            "description": "Simple connected weighted graph (3 nodes, 3 edges); shortest path is the direct single-hop connection.",
            "expected_input_contract": "graph_fields_declared_with_direct_path",
            "blocked_operations": ["geodesic_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-002",
            "description": "Multi-hop graph (4 nodes, 5 edges); shortest path routes through an intermediate node (indirect path cheaper than direct edge).",
            "expected_input_contract": "graph_fields_declared_with_indirect_path",
            "blocked_operations": ["geodesic_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-003",
            "description": "Self-loop case: source_node equals target_node; expected geodesic distance is 0.0 by convention.",
            "expected_input_contract": "graph_fields_declared_source_equals_target",
            "blocked_operations": ["geodesic_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-004",
            "description": "Unweighted graph (all edge weights equal to 1.0); BFS-equivalent result; 3-hop shortest path.",
            "expected_input_contract": "graph_fields_declared_uniform_weights",
            "blocked_operations": ["geodesic_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-005",
            "description": "Complete graph (all pairs connected); shortest path is always the direct single-hop edge; 5 nodes, 10 directed edges.",
            "expected_input_contract": "graph_fields_declared_complete_graph",
            "blocked_operations": ["geodesic_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_invalid_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "invalid-001",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "source_node",
            "expected_failure": "validation_error_missing_source_node",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-002",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "target_node",
            "expected_failure": "validation_error_missing_target_node",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-003",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "edge_list",
            "expected_failure": "validation_error_missing_edge_list",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-004",
            "invalid_reason": "NEGATIVE_EDGE_WEIGHT",
            "target_field": "edge_list[*].weight",
            "expected_failure": "validation_error_negative_edge_weight",
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_not_computable_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "nc-001",
            "not_computable_reason": "EMPTY_INPUT",
            "description": "Empty graph (zero nodes); geodesic distance is undefined and must yield NOT_COMPUTABLE.",
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-002",
            "not_computable_reason": "DISCONNECTED_GRAPH",
            "description": "Graph is disconnected: no path exists from source_node to target_node; must yield NOT_COMPUTABLE without infinite traversal.",
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-003",
            "not_computable_reason": "SOURCE_NODE_NOT_IN_GRAPH",
            "description": "source_node identifier is not present in the graph node set; must yield NOT_COMPUTABLE.",
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-004",
            "not_computable_reason": "TARGET_NODE_NOT_IN_GRAPH",
            "description": "target_node identifier is not present in the graph node set; must yield NOT_COMPUTABLE.",
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_schema_layout_plan() -> dict[str, bool]:
    return {
        "schema_directory_declared": True,
        "validation_layout_declared": True,
        "fixture_files_added": False,
        "schema_files_added": False,
        "expected_metric_values_declared": False,
    }


def default_schema_constraints() -> dict[str, bool]:
    return {
        "expected_geodesic_distances_added": False,
        "fixture_files_generated": False,
        "forecast_influence_added": False,
        "metric_values_added": False,
        "runtime_binding_added": False,
        "schema_files_generated": False,
        "scoring_added": False,
        "geodesic_math_added": False,
    }


def default_validation_plan() -> dict[str, bool]:
    return {
        "requires_valid_schema_tests": True,
        "requires_invalid_schema_tests": True,
        "requires_not_computable_schema_tests": True,
        "requires_schema_validation": True,
        "requires_no_metric_value_scan": True,
        "requires_no_fixture_file_scan": True,
        "requires_no_authority_scan": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_authority_tokens": False,
        "emits_expected_geodesic_distances": False,
        "emits_fixture_files": False,
        "emits_metric_values": False,
        "emits_runtime_controls": False,
        "emits_schema_files": False,
        "emits_schema_group_metadata": True,
        "emits_schema_plan": True,
        "emits_scores": False,
    }


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicTestVectorSchemaPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_geodesic_test_vector_schema_plan(packet: dict[str, Any]) -> None:
    req = {
        "schema_version", "plan_id", "plan_type", "operator_id",
        "source_dossier_refs", "source_metric_registry_refs",
        "source_baseline_vector_pack_refs", "schema_scope",
        "valid_schema_groups", "invalid_schema_groups", "not_computable_schema_groups",
        "schema_layout_plan", "schema_constraints", "validation_plan",
        "output_contract", "governance_flags", "provenance", "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise GeodesicTestVectorSchemaPlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise GeodesicTestVectorSchemaPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise GeodesicTestVectorSchemaPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise GeodesicTestVectorSchemaPlanValidationError("unknown_operator_id")

    scope = packet["schema_scope"]
    if scope.get("schema_family") not in ALLOWED_SCHEMA_FAMILY:
        raise GeodesicTestVectorSchemaPlanValidationError("unknown_schema_family")
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANE:
        raise GeodesicTestVectorSchemaPlanValidationError("unknown_intended_lane")
    if scope.get("schema_stage") not in ALLOWED_SCHEMA_STAGE:
        raise GeodesicTestVectorSchemaPlanValidationError("unknown_schema_stage")

    if not packet.get("valid_schema_groups"):
        raise GeodesicTestVectorSchemaPlanValidationError(
            "valid_schema_groups_must_be_non_empty"
        )
    if not packet.get("invalid_schema_groups"):
        raise GeodesicTestVectorSchemaPlanValidationError(
            "invalid_schema_groups_must_be_non_empty"
        )
    if not packet.get("not_computable_schema_groups"):
        raise GeodesicTestVectorSchemaPlanValidationError(
            "not_computable_schema_groups_must_be_non_empty"
        )

    for group_list in (
        packet["valid_schema_groups"],
        packet["invalid_schema_groups"],
        packet["not_computable_schema_groups"],
    ):
        seen_ids: set[str] = set()
        for g in group_list:
            gid = g.get("group_id")
            if gid in seen_ids:
                raise GeodesicTestVectorSchemaPlanValidationError("duplicate_group_id")
            seen_ids.add(gid)
            if g.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
                raise GeodesicTestVectorSchemaPlanValidationError(
                    "unknown_implementation_status"
                )

    if packet["schema_layout_plan"] != default_schema_layout_plan():
        raise GeodesicTestVectorSchemaPlanValidationError("invalid_schema_layout_plan")
    if packet["schema_constraints"] != default_schema_constraints():
        raise GeodesicTestVectorSchemaPlanValidationError("invalid_schema_constraints")
    if packet["validation_plan"] != default_validation_plan():
        raise GeodesicTestVectorSchemaPlanValidationError("invalid_validation_plan")
    if packet["output_contract"] != default_output_contract():
        raise GeodesicTestVectorSchemaPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise GeodesicTestVectorSchemaPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_geodesic_test_vector_schema_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_geodesic_test_vector_schema_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_geodesic_test_vector_schema_plan(payload: dict[str, Any]) -> dict[str, Any]:
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_dossier_refs": sorted(payload.get("source_dossier_refs", [])),
        "source_metric_registry_refs": sorted(
            payload.get("source_metric_registry_refs", [])
        ),
        "source_baseline_vector_pack_refs": sorted(
            payload.get("source_baseline_vector_pack_refs", [])
        ),
        "valid_schema_groups": sorted(
            payload.get("valid_schema_groups", default_valid_schema_groups()),
            key=lambda x: x["group_id"],
        ),
        "invalid_schema_groups": sorted(
            payload.get("invalid_schema_groups", default_invalid_schema_groups()),
            key=lambda x: x["group_id"],
        ),
        "not_computable_schema_groups": sorted(
            payload.get(
                "not_computable_schema_groups", default_not_computable_schema_groups()
            ),
            key=lambda x: x["group_id"],
        ),
        "schema_layout_plan": payload.get(
            "schema_layout_plan", default_schema_layout_plan()
        ),
        "schema_constraints": payload.get(
            "schema_constraints", default_schema_constraints()
        ),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_geodesic_test_vector_schema_plan_hash(base)
    validate_geodesic_test_vector_schema_plan(base)
    return _finalize(base)
