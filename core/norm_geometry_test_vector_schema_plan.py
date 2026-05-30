from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryTestVectorSchemaPlan.v1"
PLAN_TYPE = "NORM_GEOMETRY_TEST_VECTOR_SCHEMA_PLAN"
OPERATOR_ID = "NORM_GEOMETRY"
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


class NormGeometryTestVectorSchemaPlanValidationError(ValueError):
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
                "L1 (Manhattan) norm: two 3-element float64 vectors, p=1; "
                "expected distance is the sum of absolute differences."
            ),
            "expected_input_contract": "paired_float64_vectors_p1",
            "blocked_operations": ["norm_geometry_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-002",
            "description": (
                "L2 (Euclidean) norm: two 4-element float64 vectors, p=2; "
                "expected distance is the square root of the sum of squared differences."
            ),
            "expected_input_contract": "paired_float64_vectors_p2",
            "blocked_operations": ["norm_geometry_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-003",
            "description": (
                "L-infinity (Chebyshev) norm: two 4-element float64 vectors, p=inf; "
                "expected distance is the maximum absolute difference across all elements."
            ),
            "expected_input_contract": "paired_float64_vectors_p_inf",
            "blocked_operations": ["norm_geometry_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-004",
            "description": (
                "Identical vectors: x == y, p=2; expected Lp distance is 0.0 by "
                "definition regardless of p."
            ),
            "expected_input_contract": "paired_identical_float64_vectors",
            "blocked_operations": ["norm_geometry_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-005",
            "description": (
                "General Lp norm: two 5-element float64 vectors, p=3; "
                "expected distance uses the cubic root of the sum of cubed absolute differences."
            ),
            "expected_input_contract": "paired_float64_vectors_p3",
            "blocked_operations": ["norm_geometry_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-006",
            "description": (
                "Single-element vectors (n=1): scalar absolute difference, p=2; "
                "expected distance is |x_0 - y_0|."
            ),
            "expected_input_contract": "paired_single_element_float64_vectors",
            "blocked_operations": ["norm_geometry_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_invalid_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "invalid-001",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "vector_x",
            "expected_failure": "validation_error_missing_vector_x",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-002",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "vector_y",
            "expected_failure": "validation_error_missing_vector_y",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-003",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "p_parameter",
            "expected_failure": "validation_error_missing_p_parameter",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-004",
            "invalid_reason": "MISMATCHED_VECTOR_LENGTHS",
            "target_field": "vector_x,vector_y",
            "expected_failure": "validation_error_mismatched_vector_lengths",
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_not_computable_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "nc-001",
            "not_computable_reason": "EMPTY_VECTOR_INPUT",
            "description": (
                "Both vector_x and vector_y have zero elements (n=0); "
                "Lp norm distance is undefined and must yield NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-002",
            "not_computable_reason": "P_BELOW_MINIMUM",
            "description": (
                "The p parameter is less than 1.0; values below 1.0 do not define "
                "a proper norm; must yield NOT_COMPUTABLE without distance computation."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-003",
            "not_computable_reason": "NON_FINITE_ELEMENT_VALUE",
            "description": (
                "One or more elements of vector_x or vector_y are non-finite "
                "(NaN or infinite); must yield NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-004",
            "not_computable_reason": "MISMATCHED_VECTOR_LENGTHS",
            "description": (
                "len(vector_x) != len(vector_y); Lp norm requires equal-length "
                "vectors; must yield NOT_COMPUTABLE."
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
        "expected_lp_distances_added": False,
        "fixture_artifacts_generated": False,
        "forecast_influence_added": False,
        "lp_distance_values_added": False,
        "runtime_binding_added": False,
        "schema_definitions_generated": False,
        "scoring_added": False,
        "norm_geometry_computation_added": False,
    }


def default_validation_plan() -> dict[str, bool]:
    return {
        "requires_valid_schema_tests": True,
        "requires_invalid_schema_tests": True,
        "requires_not_computable_schema_tests": True,
        "requires_schema_validation": True,
        "requires_no_lp_distance_value_scan": True,
        "requires_no_fixture_artifact_scan": True,
        "requires_no_authority_scan": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_authority_tokens": False,
        "emits_expected_lp_distances": False,
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
        raise NormGeometryTestVectorSchemaPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_norm_geometry_test_vector_schema_plan(packet: dict[str, Any]) -> None:
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
        raise NormGeometryTestVectorSchemaPlanValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise NormGeometryTestVectorSchemaPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise NormGeometryTestVectorSchemaPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise NormGeometryTestVectorSchemaPlanValidationError("unknown_operator_id")

    scope = packet["schema_scope"]
    if scope.get("schema_family") not in ALLOWED_SCHEMA_FAMILY:
        raise NormGeometryTestVectorSchemaPlanValidationError("unknown_schema_family")
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANE:
        raise NormGeometryTestVectorSchemaPlanValidationError("unknown_intended_lane")
    if scope.get("schema_stage") not in ALLOWED_SCHEMA_STAGE:
        raise NormGeometryTestVectorSchemaPlanValidationError("unknown_schema_stage")

    if not packet.get("valid_schema_groups"):
        raise NormGeometryTestVectorSchemaPlanValidationError(
            "valid_schema_groups_must_be_non_empty"
        )
    if not packet.get("invalid_schema_groups"):
        raise NormGeometryTestVectorSchemaPlanValidationError(
            "invalid_schema_groups_must_be_non_empty"
        )
    if not packet.get("not_computable_schema_groups"):
        raise NormGeometryTestVectorSchemaPlanValidationError(
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
                raise NormGeometryTestVectorSchemaPlanValidationError("duplicate_group_id")
            seen_ids.add(gid)
            if g.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
                raise NormGeometryTestVectorSchemaPlanValidationError(
                    "unknown_implementation_status"
                )

    if packet["schema_layout_plan"] != default_schema_layout_plan():
        raise NormGeometryTestVectorSchemaPlanValidationError("invalid_schema_layout_plan")
    if packet["schema_constraints"] != default_schema_constraints():
        raise NormGeometryTestVectorSchemaPlanValidationError("invalid_schema_constraints")
    if packet["validation_plan"] != default_validation_plan():
        raise NormGeometryTestVectorSchemaPlanValidationError("invalid_validation_plan")
    if packet["output_contract"] != default_output_contract():
        raise NormGeometryTestVectorSchemaPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise NormGeometryTestVectorSchemaPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_norm_geometry_test_vector_schema_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_norm_geometry_test_vector_schema_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_norm_geometry_test_vector_schema_plan(payload: dict[str, Any]) -> dict[str, Any]:
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
    base["canonical_hash"] = compute_norm_geometry_test_vector_schema_plan_hash(base)
    validate_norm_geometry_test_vector_schema_plan(base)
    return _finalize(base)
