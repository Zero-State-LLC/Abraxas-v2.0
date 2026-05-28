from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferInvalidFixtureImplementationPlan.v1"
PLAN_TYPE = "CHAMFER_INVALID_FIXTURE_IMPLEMENTATION_PLAN"
OPERATOR_ID = "CHAMFER_DISTANCE"
ALLOWED_FIXTURE_FAMILY = (
    "MISSING_POINT_SET_FIXTURES",
    "EMPTY_POINT_SET_FIXTURES",
    "DIMENSION_MISMATCH_FIXTURES",
    "NON_NUMERIC_COORDINATE_FIXTURES",
    "UNKNOWN_COORDINATE_SPACE_FIXTURES",
    "EXECUTABLE_REFERENCE_FIXTURES",
    "AUTHORITY_FLAG_FIXTURES",
    "MIXED_INVALID_FIXTURE_PLAN",
)
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("IMPLEMENTATION_PLAN_ONLY", "FIXTURE_LAYOUT_ONLY", "REJECTION_POLICY_ONLY", "BLOCKED_PENDING_OPERATOR_REVIEW")
ALLOWED_CASE_TYPE = (
    "MISSING_POINT_SET_A_CASE",
    "MISSING_POINT_SET_B_CASE",
    "EMPTY_POINT_SET_CASE",
    "DIMENSION_MISMATCH_CASE",
    "NON_NUMERIC_COORDINATE_CASE",
    "UNKNOWN_COORDINATE_SPACE_CASE",
    "EXECUTABLE_REFERENCE_CASE",
    "AUTHORITY_FLAG_TRUE_CASE",
)
ALLOWED_INVALID_REASON = (
    "MISSING_REQUIRED_FIELD",
    "EMPTY_POINT_SET",
    "DIMENSION_MISMATCH",
    "NON_NUMERIC_COORDINATE",
    "UNKNOWN_COORDINATE_SPACE",
    "EXECUTABLE_REFERENCE_PRESENT",
    "AUTHORITY_FLAG_TRUE",
)
ALLOWED_EXPECTED_FAILURE = ("VALIDATION_ERROR", "REJECTED_INPUT", "NOT_COMPUTABLE")
ALLOWED_IMPL_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
LOCKED_FALSE_FLAGS = (
    "production_activation","canon_promotion","scheduler_mutation","runtime_authority","runtime_mutation",
    "forecast_influence","execution_authority","token_minting_allowed","valid_for_execution","activation_approved","authorization_granted"
)
FORBIDDEN = (
    "runtime", "scheduler", "cache", "forecast", "scoring", "metric-value", "chamfer-distance", "expected-distance",
    "fixture-file", "manifest-file", "schema-file", "gpu-kernel", "executable-reference", "authority-flag"
)


class ChamferInvalidFixtureImplementationPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_invalid_fixture_cases() -> list[dict[str, Any]]:
    return [{
        "case_id": "invalid-case-001",
        "case_type": "MISSING_POINT_SET_A_CASE",
        "description": "Plan-only invalid fixture case for missing point_set_a.",
        "target_field": "point_set_a",
        "invalid_reason": "MISSING_REQUIRED_FIELD",
        "expected_failure": "VALIDATION_ERROR",
        "blocked_outputs": ["expected_distances", "metric_values"],
        "implementation_status": "PLANNED_ONLY",
    }]


def default_rejection_policy_plan() -> dict[str, bool]:
    return {
        "rejection_policy_declared": True,
        "rejects_missing_required_fields": True,
        "rejects_empty_point_sets": True,
        "rejects_dimension_mismatch": True,
        "rejects_non_numeric_coordinates": True,
        "rejects_unknown_coordinate_space": True,
        "rejects_executable_references": True,
        "rejects_authority_flags": True,
        "runtime_rejection_enabled": False,
    }


def default_deterministic_ordering_plan() -> dict[str, bool]:
    return {"sort_by_case_id": True, "stable_serialization_required": True, "canonical_hash_required": True, "nondeterministic_ordering_allowed": False}


def default_validation_plan() -> dict[str, bool]:
    return {
        "requires_invalid_case_shape_tests": True,
        "requires_rejection_policy_tests": True,
        "requires_schema_validation": True,
        "requires_no_fixture_file_scan": True,
        "requires_no_expected_distance_scan": True,
        "requires_no_metric_value_scan": True,
        "requires_no_authority_scan": True,
    }


def default_fixture_constraints() -> dict[str, bool]:
    return {
        "fixture_files_added": False,
        "expected_distances_added": False,
        "metric_values_added": False,
        "chamfer_math_added": False,
        "scoring_added": False,
        "runtime_binding_added": False,
        "forecast_influence_added": False,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_fixture_files": False,
        "emits_expected_distances": False,
        "emits_metric_values": False,
        "emits_chamfer_outputs": False,
        "emits_scores": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_invalid_fixture_plan": True,
        "emits_invalid_case_metadata": True,
        "emits_rejection_policy_metadata": True,
    }


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ChamferInvalidFixtureImplementationPlanValidationError("forbidden_provenance_reference_detected")


def validate_chamfer_invalid_fixture_implementation_plan(packet: dict[str, Any]) -> None:
    req = {
        "schema_version","plan_id","plan_type","operator_id","source_fixture_plan_refs","source_schema_plan_refs",
        "source_valid_fixture_plan_refs","source_baseline_implementation_plan_refs","invalid_fixture_scope","invalid_fixture_cases",
        "rejection_policy_plan","deterministic_ordering_plan","validation_plan","fixture_constraints","output_contract",
        "governance_flags","provenance","created_at_utc","canonical_hash"
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise ChamferInvalidFixtureImplementationPlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferInvalidFixtureImplementationPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise ChamferInvalidFixtureImplementationPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferInvalidFixtureImplementationPlanValidationError("unknown_operator_id")

    scope = packet["invalid_fixture_scope"]
    if scope.get("fixture_family") not in ALLOWED_FIXTURE_FAMILY:
        raise ChamferInvalidFixtureImplementationPlanValidationError("unknown_fixture_family")
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferInvalidFixtureImplementationPlanValidationError("unknown_intended_lane")
    if scope.get("implementation_stage") not in ALLOWED_STAGE:
        raise ChamferInvalidFixtureImplementationPlanValidationError("unknown_implementation_stage")

    cases = packet["invalid_fixture_cases"]
    if not cases:
        raise ChamferInvalidFixtureImplementationPlanValidationError("invalid_fixture_cases_must_be_non_empty")
    seen: set[str] = set()
    for case in cases:
        cid = case.get("case_id")
        if cid in seen:
            raise ChamferInvalidFixtureImplementationPlanValidationError("duplicate_case_id")
        seen.add(cid)
        if case.get("case_type") not in ALLOWED_CASE_TYPE:
            raise ChamferInvalidFixtureImplementationPlanValidationError("unknown_case_type")
        if case.get("invalid_reason") not in ALLOWED_INVALID_REASON:
            raise ChamferInvalidFixtureImplementationPlanValidationError("unknown_invalid_reason")
        if case.get("expected_failure") not in ALLOWED_EXPECTED_FAILURE:
            raise ChamferInvalidFixtureImplementationPlanValidationError("unknown_expected_failure")
        if case.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise ChamferInvalidFixtureImplementationPlanValidationError("unknown_implementation_status")

    if packet["rejection_policy_plan"] != default_rejection_policy_plan():
        raise ChamferInvalidFixtureImplementationPlanValidationError("invalid_rejection_policy_plan")
    if packet["deterministic_ordering_plan"] != default_deterministic_ordering_plan():
        raise ChamferInvalidFixtureImplementationPlanValidationError("invalid_deterministic_ordering_plan")
    if packet["validation_plan"] != default_validation_plan():
        raise ChamferInvalidFixtureImplementationPlanValidationError("invalid_validation_plan")
    if packet["fixture_constraints"] != default_fixture_constraints():
        raise ChamferInvalidFixtureImplementationPlanValidationError("invalid_fixture_constraints")
    if packet["output_contract"] != default_output_contract():
        raise ChamferInvalidFixtureImplementationPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferInvalidFixtureImplementationPlanValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_safe(packet["provenance"])


def compute_chamfer_invalid_fixture_implementation_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_invalid_fixture_implementation_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_invalid_fixture_implementation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    cases = sorted(payload.get("invalid_fixture_cases", default_invalid_fixture_cases()), key=lambda x: x["case_id"])
    for case in cases:
        case["blocked_outputs"] = sorted(case.get("blocked_outputs", []))

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_fixture_plan_refs": sorted(payload.get("source_fixture_plan_refs", [])),
        "source_schema_plan_refs": sorted(payload.get("source_schema_plan_refs", [])),
        "source_valid_fixture_plan_refs": sorted(payload.get("source_valid_fixture_plan_refs", [])),
        "source_baseline_implementation_plan_refs": sorted(payload.get("source_baseline_implementation_plan_refs", [])),
        "invalid_fixture_cases": cases,
        "rejection_policy_plan": payload.get("rejection_policy_plan", default_rejection_policy_plan()),
        "deterministic_ordering_plan": payload.get("deterministic_ordering_plan", default_deterministic_ordering_plan()),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "fixture_constraints": payload.get("fixture_constraints", default_fixture_constraints()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_invalid_fixture_implementation_plan_hash(base)
    validate_chamfer_invalid_fixture_implementation_plan(base)
    return _finalize(base)
