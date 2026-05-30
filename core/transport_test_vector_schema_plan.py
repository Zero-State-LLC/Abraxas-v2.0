from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportTestVectorSchemaPlan.v1"
PLAN_TYPE = "TRANSPORT_TEST_VECTOR_SCHEMA_PLAN"
OPERATOR_ID = "TRANSPORT"
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
    "numpy", "scipy", "gpu-kernel",
)


class TransportTestVectorSchemaPlanValidationError(ValueError):
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
            "description": (
                "2x2 balanced transport: supply=[0.5, 0.5], demand=[0.5, 0.5], "
                "cost=[[0, 1],[1, 0]]; the unique optimal plan sends all mass "
                "along the diagonal and the expected transport distance is 0.0."
            ),
            "expected_input_contract": "balanced_2x2_diagonal_cost_zero",
            "blocked_operations": ["transport_computation", "lp_solver_invocation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-002",
            "description": (
                "2x2 balanced transport: supply=[1.0, 0.0], demand=[0.0, 1.0], "
                "cost=[[0, 2],[1, 0]]; degenerate single-active-source; "
                "expected transport distance is 2.0."
            ),
            "expected_input_contract": "balanced_2x2_off_diagonal_cost_two",
            "blocked_operations": ["transport_computation", "lp_solver_invocation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-003",
            "description": (
                "Single-source (m=1): supply=[1.0], demand=[0.25, 0.25, 0.25, 0.25], "
                "cost=[[1, 2, 3, 4]]; closed-form: transport distance = "
                "1*0.25 + 2*0.25 + 3*0.25 + 4*0.25 = 2.5."
            ),
            "expected_input_contract": "single_source_1x4_closed_form",
            "blocked_operations": ["transport_computation", "lp_solver_invocation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-004",
            "description": (
                "Single-target (n=1): supply=[0.25, 0.25, 0.25, 0.25], demand=[1.0], "
                "cost=[[1],[2],[3],[4]]; closed-form: transport distance = "
                "1*0.25 + 2*0.25 + 3*0.25 + 4*0.25 = 2.5."
            ),
            "expected_input_contract": "single_target_4x1_closed_form",
            "blocked_operations": ["transport_computation", "lp_solver_invocation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-005",
            "description": (
                "1x1 degenerate: supply=[1.0], demand=[1.0], cost=[[3.0]]; "
                "transport distance equals C[0][0] * s[0] = 3.0."
            ),
            "expected_input_contract": "degenerate_1x1_balanced",
            "blocked_operations": ["transport_computation", "lp_solver_invocation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-006",
            "description": (
                "3x3 balanced uniform: supply=[1/3, 1/3, 1/3], demand=[1/3, 1/3, 1/3], "
                "cost=[[0,1,2],[1,0,1],[2,1,0]]; unique optimal plan is the "
                "identity transport; expected transport distance is 0.0."
            ),
            "expected_input_contract": "balanced_3x3_metric_cost_uniform",
            "blocked_operations": ["transport_computation", "lp_solver_invocation"],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_invalid_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "invalid-001",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "supply",
            "expected_failure": "validation_error_missing_supply",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-002",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "demand",
            "expected_failure": "validation_error_missing_demand",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-003",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "cost_matrix",
            "expected_failure": "validation_error_missing_cost_matrix",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-004",
            "invalid_reason": "COST_MATRIX_SHAPE_MISMATCH",
            "target_field": "cost_matrix",
            "expected_failure": "validation_error_cost_matrix_shape_mismatch",
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_not_computable_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "nc-001",
            "not_computable_reason": "UNBALANCED_SUPPLY_DEMAND",
            "description": (
                "sum(supply) != sum(demand) beyond float64 tolerance; "
                "balanced transport requires equal totals; "
                "must yield NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-002",
            "not_computable_reason": "NEGATIVE_SUPPLY_VALUE",
            "description": (
                "One or more elements of the supply vector are negative; "
                "supply values must be non-negative; must yield NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-003",
            "not_computable_reason": "NEGATIVE_COST_VALUE",
            "description": (
                "One or more elements of the cost matrix are negative; "
                "transport costs must be non-negative; must yield NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-004",
            "not_computable_reason": "EMPTY_SUPPLY_VECTOR",
            "description": (
                "The supply vector has zero elements (m=0); "
                "transport distance is undefined for empty supply; "
                "must yield NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-005",
            "not_computable_reason": "NON_FINITE_SUPPLY_VALUE",
            "description": (
                "One or more elements of the supply or demand vector are non-finite "
                "(NaN or infinite); must yield NOT_COMPUTABLE."
            ),
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
        "expected_transport_distances_added": False,
        "fixture_artifacts_generated": False,
        "forecast_influence_added": False,
        "transport_distance_values_added": False,
        "lp_solver_invoked": False,
        "schema_definitions_generated": False,
        "scoring_added": False,
        "transport_computation_added": False,
    }


def default_validation_plan() -> dict[str, bool]:
    return {
        "requires_valid_schema_tests": True,
        "requires_invalid_schema_tests": True,
        "requires_not_computable_schema_tests": True,
        "requires_schema_validation": True,
        "requires_no_transport_distance_value_scan": True,
        "requires_no_fixture_artifact_scan": True,
        "requires_no_authority_scan": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_authority_tokens": False,
        "emits_expected_transport_distances": False,
        "emits_fixture_artifacts": False,
        "emits_metric_values": False,
        "emits_runtime_controls": False,
        "emits_schema_definitions": False,
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
        raise TransportTestVectorSchemaPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_transport_test_vector_schema_plan(packet: dict[str, Any]) -> None:
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
        raise TransportTestVectorSchemaPlanValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise TransportTestVectorSchemaPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise TransportTestVectorSchemaPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise TransportTestVectorSchemaPlanValidationError("unknown_operator_id")

    scope = packet["schema_scope"]
    if scope.get("schema_family") not in ALLOWED_SCHEMA_FAMILY:
        raise TransportTestVectorSchemaPlanValidationError("unknown_schema_family")
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANE:
        raise TransportTestVectorSchemaPlanValidationError("unknown_intended_lane")
    if scope.get("schema_stage") not in ALLOWED_SCHEMA_STAGE:
        raise TransportTestVectorSchemaPlanValidationError("unknown_schema_stage")

    if not packet.get("valid_schema_groups"):
        raise TransportTestVectorSchemaPlanValidationError(
            "valid_schema_groups_must_be_non_empty"
        )
    if not packet.get("invalid_schema_groups"):
        raise TransportTestVectorSchemaPlanValidationError(
            "invalid_schema_groups_must_be_non_empty"
        )
    if not packet.get("not_computable_schema_groups"):
        raise TransportTestVectorSchemaPlanValidationError(
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
                raise TransportTestVectorSchemaPlanValidationError("duplicate_group_id")
            seen_ids.add(gid)
            if g.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
                raise TransportTestVectorSchemaPlanValidationError(
                    "unknown_implementation_status"
                )

    if packet["schema_layout_plan"] != default_schema_layout_plan():
        raise TransportTestVectorSchemaPlanValidationError("invalid_schema_layout_plan")
    if packet["schema_constraints"] != default_schema_constraints():
        raise TransportTestVectorSchemaPlanValidationError("invalid_schema_constraints")
    if packet["validation_plan"] != default_validation_plan():
        raise TransportTestVectorSchemaPlanValidationError("invalid_validation_plan")
    if packet["output_contract"] != default_output_contract():
        raise TransportTestVectorSchemaPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise TransportTestVectorSchemaPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_transport_test_vector_schema_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_transport_test_vector_schema_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_transport_test_vector_schema_plan(payload: dict[str, Any]) -> dict[str, Any]:
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
    base["canonical_hash"] = compute_transport_test_vector_schema_plan_hash(base)
    validate_transport_test_vector_schema_plan(base)
    return _finalize(base)
