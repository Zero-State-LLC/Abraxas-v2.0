from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash
from core.chamfer_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS

SCHEMA_VERSION = "ChamferNotComputableFixtureImplementationPlan.v1"
PLAN_TYPE = "CHAMFER_NOT_COMPUTABLE_FIXTURE_IMPLEMENTATION_PLAN"
OPERATOR_ID = "CHAMFER_DISTANCE"
ALLOWED_FIXTURE_FAMILY = (
    "EMPTY_INPUT_FIXTURES",
    "MALFORMED_COORDINATE_FIXTURES",
    "UNDECLARED_DIMENSIONALITY_FIXTURES",
    "UNDECLARED_COORDINATE_SPACE_FIXTURES",
    "MISSING_NUMERICAL_POLICY_FIXTURES",
    "INPUT_CONTRACT_VIOLATION_FIXTURES",
    "MIXED_NOT_COMPUTABLE_FIXTURE_PLAN",
)
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("IMPLEMENTATION_PLAN_ONLY", "FIXTURE_LAYOUT_ONLY", "NOT_COMPUTABLE_POLICY_ONLY", "BLOCKED_PENDING_OPERATOR_REVIEW")
ALLOWED_CASE_TYPE = (
    "EMPTY_INPUT_CASE",
    "MALFORMED_COORDINATE_CASE",
    "DIMENSIONALITY_UNDECLARED_CASE",
    "COORDINATE_SPACE_UNDECLARED_CASE",
    "NUMERICAL_POLICY_MISSING_CASE",
    "INPUT_CONTRACT_VIOLATION_CASE",
)
ALLOWED_REASON = (
    "EMPTY_INPUT",
    "MALFORMED_COORDINATES",
    "DIMENSIONALITY_UNDECLARED",
    "COORDINATE_SPACE_UNDECLARED",
    "NUMERICAL_POLICY_MISSING",
    "INPUT_CONTRACT_VIOLATION",
)
ALLOWED_EXPECTED_STATE = ("NOT_COMPUTABLE", "VALIDATION_ERROR", "REJECTED_INPUT")
ALLOWED_IMPL_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
FORBIDDEN = (
    "runtime", "scheduler", "cache", "forecast", "scoring", "metric-value", "chamfer-distance", "expected-distance",
    "fixture-file", "manifest-file", "schema-file", "gpu-kernel", "not-computable-runtime", "authority-flag"
)


class ChamferNotComputableFixtureImplementationPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_not_computable_fixture_cases() -> list[dict[str, Any]]:
    return [{
        "case_id": "not-computable-case-001",
        "case_type": "EMPTY_INPUT_CASE",
        "description": "Plan-only NOT_COMPUTABLE fixture for empty input routing.",
        "target_field": "point_set_a",
        "not_computable_reason": "EMPTY_INPUT",
        "expected_state": "NOT_COMPUTABLE",
        "blocked_outputs": ["expected_distances", "metric_values"],
        "implementation_status": "PLANNED_ONLY",
    }]


def default_not_computable_policy_plan() -> dict[str, bool]:
    return {
        "not_computable_policy_declared": True,
        "emits_not_computable_state_planned": True,
        "rejects_empty_input": True,
        "rejects_malformed_coordinates": True,
        "rejects_undeclared_dimensionality": True,
        "rejects_undeclared_coordinate_space": True,
        "rejects_missing_numerical_policy": True,
        "rejects_input_contract_violation": True,
        "runtime_not_computable_enabled": False,
    }


def default_deterministic_ordering_plan() -> dict[str, bool]:
    return {"sort_by_case_id": True, "stable_serialization_required": True, "canonical_hash_required": True, "nondeterministic_ordering_allowed": False}


def default_validation_plan() -> dict[str, bool]:
    return {
        "requires_not_computable_case_shape_tests": True,
        "requires_not_computable_policy_tests": True,
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
        "emits_not_computable_fixture_plan": True,
        "emits_not_computable_case_metadata": True,
        "emits_not_computable_policy_metadata": True,
    }


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ChamferNotComputableFixtureImplementationPlanValidationError("forbidden_provenance_reference_detected")


def validate_chamfer_not_computable_fixture_implementation_plan(packet: dict[str, Any]) -> None:
    req = {
        "schema_version", "plan_id", "plan_type", "operator_id", "source_fixture_plan_refs", "source_schema_plan_refs",
        "source_valid_fixture_plan_refs", "source_invalid_fixture_plan_refs", "source_baseline_implementation_plan_refs",
        "not_computable_fixture_scope", "not_computable_fixture_cases", "not_computable_policy_plan", "deterministic_ordering_plan",
        "validation_plan", "fixture_constraints", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash"
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise ChamferNotComputableFixtureImplementationPlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferNotComputableFixtureImplementationPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise ChamferNotComputableFixtureImplementationPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferNotComputableFixtureImplementationPlanValidationError("unknown_operator_id")

    scope = packet["not_computable_fixture_scope"]
    if scope.get("fixture_family") not in ALLOWED_FIXTURE_FAMILY:
        raise ChamferNotComputableFixtureImplementationPlanValidationError("unknown_fixture_family")
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferNotComputableFixtureImplementationPlanValidationError("unknown_intended_lane")
    if scope.get("implementation_stage") not in ALLOWED_STAGE:
        raise ChamferNotComputableFixtureImplementationPlanValidationError("unknown_implementation_stage")

    cases = packet["not_computable_fixture_cases"]
    if not cases:
        raise ChamferNotComputableFixtureImplementationPlanValidationError("not_computable_fixture_cases_must_be_non_empty")
    seen: set[str] = set()
    for case in cases:
        cid = case.get("case_id")
        if cid in seen:
            raise ChamferNotComputableFixtureImplementationPlanValidationError("duplicate_case_id")
        seen.add(cid)
        if case.get("case_type") not in ALLOWED_CASE_TYPE:
            raise ChamferNotComputableFixtureImplementationPlanValidationError("unknown_case_type")
        if case.get("not_computable_reason") not in ALLOWED_REASON:
            raise ChamferNotComputableFixtureImplementationPlanValidationError("unknown_not_computable_reason")
        if case.get("expected_state") not in ALLOWED_EXPECTED_STATE:
            raise ChamferNotComputableFixtureImplementationPlanValidationError("unknown_expected_state")
        if case.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise ChamferNotComputableFixtureImplementationPlanValidationError("unknown_implementation_status")

    if packet["not_computable_policy_plan"] != default_not_computable_policy_plan():
        raise ChamferNotComputableFixtureImplementationPlanValidationError("invalid_not_computable_policy_plan")
    if packet["deterministic_ordering_plan"] != default_deterministic_ordering_plan():
        raise ChamferNotComputableFixtureImplementationPlanValidationError("invalid_deterministic_ordering_plan")
    if packet["validation_plan"] != default_validation_plan():
        raise ChamferNotComputableFixtureImplementationPlanValidationError("invalid_validation_plan")
    if packet["fixture_constraints"] != default_fixture_constraints():
        raise ChamferNotComputableFixtureImplementationPlanValidationError("invalid_fixture_constraints")
    if packet["output_contract"] != default_output_contract():
        raise ChamferNotComputableFixtureImplementationPlanValidationError("invalid_output_contract")
    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferNotComputableFixtureImplementationPlanValidationError(f"authority_lock_must_be_false:{flag}")
    _assert_safe(packet["provenance"])


def compute_chamfer_not_computable_fixture_implementation_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_not_computable_fixture_implementation_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_not_computable_fixture_implementation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    cases = sorted(payload.get("not_computable_fixture_cases", default_not_computable_fixture_cases()), key=lambda x: x["case_id"])
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
        "source_invalid_fixture_plan_refs": sorted(payload.get("source_invalid_fixture_plan_refs", [])),
        "source_baseline_implementation_plan_refs": sorted(payload.get("source_baseline_implementation_plan_refs", [])),
        "not_computable_fixture_cases": cases,
        "not_computable_policy_plan": payload.get("not_computable_policy_plan", default_not_computable_policy_plan()),
        "deterministic_ordering_plan": payload.get("deterministic_ordering_plan", default_deterministic_ordering_plan()),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "fixture_constraints": payload.get("fixture_constraints", default_fixture_constraints()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_not_computable_fixture_implementation_plan_hash(base)
    validate_chamfer_not_computable_fixture_implementation_plan(base)
    return _finalize(base)
