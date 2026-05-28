from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferValidFixtureImplementationPlan.v1"
PLAN_TYPE = "CHAMFER_VALID_FIXTURE_IMPLEMENTATION_PLAN"
OPERATOR_ID = "CHAMFER_DISTANCE"
ALLOWED_FIXTURE_FAMILY = ("IDENTICAL_POINT_SETS", "OFFSET_POINT_SETS", "PARTIAL_OVERLAP_POINT_SETS", "DUPLICATE_POINTS", "MULTI_DIMENSIONAL_POINTS", "BASELINE_COMPARATOR_CASE", "MIXED_VALID_FIXTURE_PLAN")
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("IMPLEMENTATION_PLAN_ONLY", "FIXTURE_LAYOUT_ONLY", "MANIFEST_PLAN_ONLY", "BLOCKED_PENDING_OPERATOR_REVIEW")
ALLOWED_CASE_TYPE = ("IDENTICAL_POINT_SETS_CASE", "OFFSET_POINT_SETS_CASE", "PARTIAL_OVERLAP_CASE", "DUPLICATE_POINTS_CASE", "TWO_DIMENSIONAL_CASE", "THREE_DIMENSIONAL_CASE", "BASELINE_COMPARATOR_CASE")
ALLOWED_COORDINATE_SPACE = ("EUCLIDEAN_DECLARED", "NORMALIZED_UNIT_SPACE", "ABSTRACT_POINT_SPACE", "NOT_COMPUTABLE_SPACE")
ALLOWED_IMPL_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
LOCKED_FALSE_FLAGS = ("production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation", "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted")
FORBIDDEN = ("runtime", "scheduler", "cache", "forecast", "scoring", "metric-value", "chamfer-distance", "expected-distance", "fixture-file", "manifest-file", "schema-file", "gpu-kernel")


class ChamferValidFixtureImplementationPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_valid_fixture_cases() -> list[dict[str, Any]]:
    return [{"case_id": "case-001", "case_type": "IDENTICAL_POINT_SETS_CASE", "description": "Plan-only identical point-set fixture case.", "planned_point_set_a_shape": "N x D", "planned_point_set_b_shape": "N x D", "coordinate_space": "EUCLIDEAN_DECLARED", "dimensionality": 2, "expected_semantics": "identical_case_declared_without_distance_values", "blocked_outputs": ["expected_distances"], "implementation_status": "PLANNED_ONLY"}]


def default_fixture_manifest_plan() -> dict[str, bool]:
    return {"manifest_declared": True, "manifest_file_added": False, "fixture_files_added": False, "fixture_ids_declared": True, "deterministic_sorting_declared": True, "expected_metric_values_declared": False}


def default_deterministic_ordering_plan() -> dict[str, bool]:
    return {"sort_by_case_id": True, "stable_serialization_required": True, "canonical_hash_required": True, "nondeterministic_ordering_allowed": False}


def default_validation_plan() -> dict[str, bool]:
    return {"requires_case_shape_tests": True, "requires_manifest_shape_tests": True, "requires_schema_validation": True, "requires_no_fixture_file_scan": True, "requires_no_expected_distance_scan": True, "requires_no_metric_value_scan": True, "requires_no_authority_scan": True}


def default_fixture_constraints() -> dict[str, bool]:
    return {"fixture_files_added": False, "manifest_file_added": False, "expected_distances_added": False, "metric_values_added": False, "chamfer_math_added": False, "scoring_added": False, "runtime_binding_added": False, "forecast_influence_added": False}


def default_output_contract() -> dict[str, bool]:
    return {"emits_fixture_files": False, "emits_manifest_file": False, "emits_expected_distances": False, "emits_metric_values": False, "emits_chamfer_outputs": False, "emits_scores": False, "emits_runtime_controls": False, "emits_authority_tokens": False, "emits_valid_fixture_plan": True, "emits_fixture_case_metadata": True}


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ChamferValidFixtureImplementationPlanValidationError("forbidden_provenance_reference_detected")


def validate_chamfer_valid_fixture_implementation_plan(packet: dict[str, Any]) -> None:
    req = {"schema_version","plan_id","plan_type","operator_id","source_fixture_plan_refs","source_schema_plan_refs","source_baseline_implementation_plan_refs","valid_fixture_scope","valid_fixture_cases","fixture_manifest_plan","deterministic_ordering_plan","validation_plan","fixture_constraints","output_contract","governance_flags","provenance","created_at_utc","canonical_hash"}
    missing = sorted(req - packet.keys())
    if missing:
        raise ChamferValidFixtureImplementationPlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferValidFixtureImplementationPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise ChamferValidFixtureImplementationPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferValidFixtureImplementationPlanValidationError("unknown_operator_id")

    scope = packet["valid_fixture_scope"]
    if scope.get("fixture_family") not in ALLOWED_FIXTURE_FAMILY:
        raise ChamferValidFixtureImplementationPlanValidationError("unknown_fixture_family")
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferValidFixtureImplementationPlanValidationError("unknown_intended_lane")
    if scope.get("implementation_stage") not in ALLOWED_STAGE:
        raise ChamferValidFixtureImplementationPlanValidationError("unknown_implementation_stage")

    cases = packet["valid_fixture_cases"]
    if not cases:
        raise ChamferValidFixtureImplementationPlanValidationError("valid_fixture_cases_must_be_non_empty")
    seen: set[str] = set()
    for case in cases:
        cid = case.get("case_id")
        if cid in seen:
            raise ChamferValidFixtureImplementationPlanValidationError("duplicate_case_id")
        seen.add(cid)
        if case.get("case_type") not in ALLOWED_CASE_TYPE:
            raise ChamferValidFixtureImplementationPlanValidationError("unknown_case_type")
        if case.get("coordinate_space") not in ALLOWED_COORDINATE_SPACE:
            raise ChamferValidFixtureImplementationPlanValidationError("unknown_coordinate_space")
        if case.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise ChamferValidFixtureImplementationPlanValidationError("unknown_implementation_status")
        if not isinstance(case.get("dimensionality"), int) or case["dimensionality"] <= 0:
            raise ChamferValidFixtureImplementationPlanValidationError("invalid_dimensionality")

    if packet["fixture_manifest_plan"] != default_fixture_manifest_plan():
        raise ChamferValidFixtureImplementationPlanValidationError("invalid_fixture_manifest_plan")
    if packet["deterministic_ordering_plan"] != default_deterministic_ordering_plan():
        raise ChamferValidFixtureImplementationPlanValidationError("invalid_deterministic_ordering_plan")
    if packet["validation_plan"] != default_validation_plan():
        raise ChamferValidFixtureImplementationPlanValidationError("invalid_validation_plan")
    if packet["fixture_constraints"] != default_fixture_constraints():
        raise ChamferValidFixtureImplementationPlanValidationError("invalid_fixture_constraints")
    if packet["output_contract"] != default_output_contract():
        raise ChamferValidFixtureImplementationPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferValidFixtureImplementationPlanValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_safe(packet["provenance"])


def compute_chamfer_valid_fixture_implementation_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_valid_fixture_implementation_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_valid_fixture_implementation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    cases = sorted(payload.get("valid_fixture_cases", default_valid_fixture_cases()), key=lambda x: x["case_id"])
    for case in cases:
        case["blocked_outputs"] = sorted(case.get("blocked_outputs", []))

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_fixture_plan_refs": sorted(payload.get("source_fixture_plan_refs", [])),
        "source_schema_plan_refs": sorted(payload.get("source_schema_plan_refs", [])),
        "source_baseline_implementation_plan_refs": sorted(payload.get("source_baseline_implementation_plan_refs", [])),
        "valid_fixture_cases": cases,
        "fixture_manifest_plan": payload.get("fixture_manifest_plan", default_fixture_manifest_plan()),
        "deterministic_ordering_plan": payload.get("deterministic_ordering_plan", default_deterministic_ordering_plan()),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "fixture_constraints": payload.get("fixture_constraints", default_fixture_constraints()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_valid_fixture_implementation_plan_hash(base)
    validate_chamfer_valid_fixture_implementation_plan(base)
    return _finalize(base)
