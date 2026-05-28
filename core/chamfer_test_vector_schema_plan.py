from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferTestVectorSchemaPlan.v1"
PLAN_TYPE = "CHAMFER_TEST_VECTOR_SCHEMA_PLAN"
OPERATOR_ID = "CHAMFER_DISTANCE"

ALLOWED_SCHEMA_FAMILY = ("VALID_VECTOR_SCHEMA", "INVALID_VECTOR_SCHEMA", "NOT_COMPUTABLE_SCHEMA", "MIXED_SCHEMA_PLAN")
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_SCHEMA_STAGE = ("SCHEMA_PLAN_ONLY", "SCHEMA_REQUIREMENTS_ONLY", "SCHEMA_LAYOUT_ONLY", "BLOCKED_PENDING_OPERATOR_REVIEW")
ALLOWED_SCHEMA_TYPE = ("POINT_SET_SCHEMA", "MULTI_DIMENSIONAL_POINT_SCHEMA", "DUPLICATE_POINT_SCHEMA", "BASELINE_COMPARATOR_SCHEMA", "VALID_ALIGNMENT_SCHEMA")
ALLOWED_INVALID_REASON = ("MISSING_REQUIRED_FIELD", "EMPTY_POINT_SET", "INVALID_COORDINATE_TYPE", "DIMENSION_MISMATCH", "UNKNOWN_COORDINATE_SPACE", "EXECUTABLE_REFERENCE_PRESENT", "AUTHORITY_FLAG_TRUE")
ALLOWED_NC_REASON = ("EMPTY_INPUT", "MALFORMED_SCHEMA", "DIMENSIONALITY_UNDECLARED", "COORDINATE_SPACE_UNDECLARED", "NUMERICAL_POLICY_MISSING", "INPUT_CONTRACT_VIOLATION")
ALLOWED_NC_STATE = ("NOT_COMPUTABLE", "VALIDATION_ERROR", "REJECTED_INPUT")
ALLOWED_IMPL_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
LOCKED_FALSE_FLAGS = ("production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation", "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted")
FORBIDDEN = ("runtime", "scheduler", "cache", "forecast", "scoring", "metric-value", "chamfer-distance", "expected-distance", "fixture-file", "schema-file", "gpu-kernel")


class ChamferTestVectorSchemaPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_valid_schema_groups() -> list[dict[str, Any]]:
    return [{"group_id": "valid-001", "schema_type": "POINT_SET_SCHEMA", "description": "Point-set shape contract schema metadata.", "expected_input_contract": "point_set_fields_declared", "blocked_operations": ["distance_computation"], "implementation_status": "PLANNED_ONLY"}]


def default_invalid_schema_groups() -> list[dict[str, Any]]:
    return [{"group_id": "invalid-001", "invalid_reason": "MISSING_REQUIRED_FIELD", "target_field": "point_set_a", "expected_failure": "validation_error_missing_field", "implementation_status": "PLANNED_ONLY"}]


def default_not_computable_schema_groups() -> list[dict[str, Any]]:
    return [{"group_id": "nc-001", "not_computable_reason": "EMPTY_INPUT", "description": "Empty point-set branch metadata.", "expected_state": "NOT_COMPUTABLE", "implementation_status": "PLANNED_ONLY"}]


def default_schema_layout_plan() -> dict[str, bool]:
    return {"schema_files_added": False, "fixture_files_added": False, "schema_directory_declared": True, "validation_layout_declared": True, "expected_metric_values_declared": False}


def default_schema_constraints() -> dict[str, bool]:
    return {"schema_files_generated": False, "fixture_files_generated": False, "metric_values_added": False, "expected_distances_added": False, "chamfer_math_added": False, "scoring_added": False, "runtime_binding_added": False, "forecast_influence_added": False}


def default_validation_plan() -> dict[str, bool]:
    return {"requires_valid_schema_tests": True, "requires_invalid_schema_tests": True, "requires_not_computable_schema_tests": True, "requires_schema_validation": True, "requires_no_metric_value_scan": True, "requires_no_authority_scan": True, "requires_no_fixture_file_scan": True}


def default_output_contract() -> dict[str, bool]:
    return {"emits_schema_files": False, "emits_fixture_files": False, "emits_metric_values": False, "emits_expected_distances": False, "emits_chamfer_outputs": False, "emits_scores": False, "emits_runtime_controls": False, "emits_authority_tokens": False, "emits_schema_plan": True, "emits_schema_group_metadata": True}


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ChamferTestVectorSchemaPlanValidationError("forbidden_provenance_reference_detected")


def _assert_unique(items: list[dict[str, Any]], key: str, err: str) -> None:
    seen: set[str] = set()
    for item in items:
        ident = item.get(key)
        if ident in seen:
            raise ChamferTestVectorSchemaPlanValidationError(err)
        seen.add(ident)


def validate_chamfer_test_vector_schema_plan(packet: dict[str, Any]) -> None:
    required = {"schema_version", "plan_id", "plan_type", "operator_id", "source_fixture_plan_refs", "source_metric_registry_refs", "source_baseline_vector_pack_refs", "schema_scope", "valid_schema_groups", "invalid_schema_groups", "not_computable_schema_groups", "schema_layout_plan", "schema_constraints", "validation_plan", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash"}
    missing = sorted(required - packet.keys())
    if missing:
        raise ChamferTestVectorSchemaPlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferTestVectorSchemaPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise ChamferTestVectorSchemaPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferTestVectorSchemaPlanValidationError("unknown_operator_id")

    scope = packet["schema_scope"]
    if scope.get("schema_family") not in ALLOWED_SCHEMA_FAMILY:
        raise ChamferTestVectorSchemaPlanValidationError("unknown_schema_family")
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferTestVectorSchemaPlanValidationError("unknown_intended_lane")
    if scope.get("schema_stage") not in ALLOWED_SCHEMA_STAGE:
        raise ChamferTestVectorSchemaPlanValidationError("unknown_schema_stage")

    valid = packet["valid_schema_groups"]
    invalid = packet["invalid_schema_groups"]
    nc = packet["not_computable_schema_groups"]
    if not valid:
        raise ChamferTestVectorSchemaPlanValidationError("valid_schema_groups_must_be_non_empty")
    if not invalid:
        raise ChamferTestVectorSchemaPlanValidationError("invalid_schema_groups_must_be_non_empty")
    if not nc:
        raise ChamferTestVectorSchemaPlanValidationError("not_computable_schema_groups_must_be_non_empty")

    _assert_unique(valid, "group_id", "duplicate_group_id")
    _assert_unique(invalid, "group_id", "duplicate_group_id")
    _assert_unique(nc, "group_id", "duplicate_group_id")

    for entry in valid:
        if entry.get("schema_type") not in ALLOWED_SCHEMA_TYPE:
            raise ChamferTestVectorSchemaPlanValidationError("unknown_schema_type")
        if entry.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise ChamferTestVectorSchemaPlanValidationError("unknown_implementation_status")
    for entry in invalid:
        if entry.get("invalid_reason") not in ALLOWED_INVALID_REASON:
            raise ChamferTestVectorSchemaPlanValidationError("unknown_invalid_reason")
        if entry.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise ChamferTestVectorSchemaPlanValidationError("unknown_implementation_status")
    for entry in nc:
        if entry.get("not_computable_reason") not in ALLOWED_NC_REASON:
            raise ChamferTestVectorSchemaPlanValidationError("unknown_not_computable_reason")
        if entry.get("expected_state") not in ALLOWED_NC_STATE:
            raise ChamferTestVectorSchemaPlanValidationError("unknown_expected_state")
        if entry.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise ChamferTestVectorSchemaPlanValidationError("unknown_implementation_status")

    if packet["schema_layout_plan"] != default_schema_layout_plan():
        raise ChamferTestVectorSchemaPlanValidationError("invalid_schema_layout_plan")
    if packet["schema_constraints"] != default_schema_constraints():
        raise ChamferTestVectorSchemaPlanValidationError("invalid_schema_constraints")
    if packet["validation_plan"] != default_validation_plan():
        raise ChamferTestVectorSchemaPlanValidationError("invalid_validation_plan")
    if packet["output_contract"] != default_output_contract():
        raise ChamferTestVectorSchemaPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferTestVectorSchemaPlanValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_safe(packet["provenance"])


def compute_chamfer_test_vector_schema_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_test_vector_schema_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_test_vector_schema_plan(payload: dict[str, Any]) -> dict[str, Any]:
    valid = sorted(payload.get("valid_schema_groups", default_valid_schema_groups()), key=lambda x: x["group_id"])
    invalid = sorted(payload.get("invalid_schema_groups", default_invalid_schema_groups()), key=lambda x: x["group_id"])
    nc = sorted(payload.get("not_computable_schema_groups", default_not_computable_schema_groups()), key=lambda x: x["group_id"])
    for item in valid:
        item["blocked_operations"] = sorted(item.get("blocked_operations", []))

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_fixture_plan_refs": sorted(payload.get("source_fixture_plan_refs", [])),
        "source_metric_registry_refs": sorted(payload.get("source_metric_registry_refs", [])),
        "source_baseline_vector_pack_refs": sorted(payload.get("source_baseline_vector_pack_refs", [])),
        "valid_schema_groups": valid,
        "invalid_schema_groups": invalid,
        "not_computable_schema_groups": nc,
        "schema_layout_plan": payload.get("schema_layout_plan", default_schema_layout_plan()),
        "schema_constraints": payload.get("schema_constraints", default_schema_constraints()),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_test_vector_schema_plan_hash(base)
    validate_chamfer_test_vector_schema_plan(base)
    return _finalize(base)
