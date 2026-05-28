from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash
from core.chamfer_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS

SCHEMA_VERSION = "ChamferExpectedDistancePolicyPlan.v1"
PLAN_TYPE = "CHAMFER_EXPECTED_DISTANCE_POLICY_PLAN"
OPERATOR_ID = "CHAMFER_DISTANCE"
ALLOWED_FAMILY = (
    "EXPECTED_DISTANCE_POLICY",
    "FLOAT_TOLERANCE_POLICY",
    "NOT_COMPUTABLE_DISTANCE_POLICY",
    "REVIEW_GATE_POLICY",
    "MIXED_DISTANCE_POLICY_PLAN",
)
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("POLICY_PLAN_ONLY", "EXPECTED_VALUE_HELD", "BLOCKED_PENDING_OPERATOR_REVIEW")
ALLOWED_GROUP_TYPE = (
    "EXACT_DISTANCE_POLICY_GROUP",
    "APPROXIMATE_DISTANCE_POLICY_GROUP",
    "TOLERANCE_BOUND_POLICY_GROUP",
    "NOT_COMPUTABLE_POLICY_GROUP",
    "MANUAL_REVIEW_POLICY_GROUP",
)
ALLOWED_FIXTURE_FAMILY = ("VALID_FIXTURES", "INVALID_FIXTURES", "NOT_COMPUTABLE_FIXTURES", "MIXED_FIXTURES")
ALLOWED_DISTANCE_VALUE_STATUS = ("NOT_ADDED", "HELD_PENDING_IMPLEMENTATION", "HELD_PENDING_OPERATOR_REVIEW", "NOT_COMPUTABLE_ONLY")
ALLOWED_IMPL_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
FORBIDDEN = (
    "runtime", "scheduler", "cache", "forecast", "scoring", "metric-value", "chamfer-distance", "expected-distance",
    "tolerance-value", "fixture-file", "manifest-file", "schema-file", "gpu-kernel", "authority-flag", "implementation-allowed"
)


class ChamferExpectedDistancePolicyPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_expected_distance_policy_groups() -> list[dict[str, Any]]:
    return [{
        "group_id": "group-001",
        "group_type": "TOLERANCE_BOUND_POLICY_GROUP",
        "description": "Tolerance policy metadata for future valid fixture expected-distance introduction.",
        "applicable_fixture_family": "VALID_FIXTURES",
        "distance_value_status": "HELD_PENDING_OPERATOR_REVIEW",
        "tolerance_required": True,
        "review_required": True,
        "implementation_status": "PLANNED_ONLY",
    }]


def default_tolerance_policy_plan() -> dict[str, bool]:
    return {
        "tolerance_policy_declared": True,
        "absolute_tolerance_declared": True,
        "relative_tolerance_declared": True,
        "floating_point_policy_declared": True,
        "tolerance_values_added": False,
        "tolerance_execution_enabled": False,
    }


def default_not_computable_distance_policy() -> dict[str, bool]:
    return {
        "not_computable_policy_declared": True,
        "expected_not_computable_state_declared": True,
        "expected_distance_value_allowed_for_not_computable": False,
        "runtime_not_computable_enabled": False,
    }


def default_review_gate_plan() -> dict[str, bool]:
    return {
        "operator_review_required": True,
        "expected_values_require_new_pr": True,
        "fixture_files_require_new_pr": True,
        "baseline_implementation_required_before_values": True,
        "no_authority_scan_required": True,
        "policy_only_no_values": True,
    }


def default_policy_constraints() -> dict[str, bool]:
    return {
        "expected_distances_added": False,
        "tolerance_values_added": False,
        "fixture_files_added": False,
        "metric_values_added": False,
        "chamfer_math_added": False,
        "scoring_added": False,
        "runtime_binding_added": False,
        "forecast_influence_added": False,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_expected_distances": False,
        "emits_tolerance_values": False,
        "emits_fixture_files": False,
        "emits_metric_values": False,
        "emits_chamfer_outputs": False,
        "emits_scores": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_policy_plan": True,
        "emits_review_gate_metadata": True,
    }


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ChamferExpectedDistancePolicyPlanValidationError("forbidden_provenance_reference_detected")


def validate_chamfer_expected_distance_policy_plan(packet: dict[str, Any]) -> None:
    required = {
        "schema_version", "plan_id", "plan_type", "operator_id", "source_fixture_readiness_review_refs",
        "source_fixture_consolidation_receipt_refs", "source_valid_fixture_plan_refs", "source_invalid_fixture_plan_refs",
        "source_not_computable_fixture_plan_refs", "source_baseline_implementation_plan_refs", "policy_scope",
        "expected_distance_policy_groups", "tolerance_policy_plan", "not_computable_distance_policy", "review_gate_plan",
        "policy_constraints", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash"
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise ChamferExpectedDistancePolicyPlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferExpectedDistancePolicyPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise ChamferExpectedDistancePolicyPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferExpectedDistancePolicyPlanValidationError("unknown_operator_id")

    scope = packet["policy_scope"]
    if scope.get("policy_family") not in ALLOWED_FAMILY:
        raise ChamferExpectedDistancePolicyPlanValidationError("unknown_policy_family")
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferExpectedDistancePolicyPlanValidationError("unknown_intended_lane")
    if scope.get("policy_stage") not in ALLOWED_STAGE:
        raise ChamferExpectedDistancePolicyPlanValidationError("unknown_policy_stage")

    groups = packet["expected_distance_policy_groups"]
    if not groups:
        raise ChamferExpectedDistancePolicyPlanValidationError("expected_distance_policy_groups_must_be_non_empty")
    seen: set[str] = set()
    for group in groups:
        gid = group.get("group_id")
        if gid in seen:
            raise ChamferExpectedDistancePolicyPlanValidationError("duplicate_group_id")
        seen.add(gid)
        if group.get("group_type") not in ALLOWED_GROUP_TYPE:
            raise ChamferExpectedDistancePolicyPlanValidationError("unknown_group_type")
        if group.get("applicable_fixture_family") not in ALLOWED_FIXTURE_FAMILY:
            raise ChamferExpectedDistancePolicyPlanValidationError("unknown_applicable_fixture_family")
        if group.get("distance_value_status") not in ALLOWED_DISTANCE_VALUE_STATUS:
            raise ChamferExpectedDistancePolicyPlanValidationError("unknown_distance_value_status")
        if group.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise ChamferExpectedDistancePolicyPlanValidationError("unknown_implementation_status")

    if packet["tolerance_policy_plan"] != default_tolerance_policy_plan():
        raise ChamferExpectedDistancePolicyPlanValidationError("invalid_tolerance_policy_plan")
    if packet["not_computable_distance_policy"] != default_not_computable_distance_policy():
        raise ChamferExpectedDistancePolicyPlanValidationError("invalid_not_computable_distance_policy")
    if packet["review_gate_plan"] != default_review_gate_plan():
        raise ChamferExpectedDistancePolicyPlanValidationError("invalid_review_gate_plan")
    if packet["policy_constraints"] != default_policy_constraints():
        raise ChamferExpectedDistancePolicyPlanValidationError("invalid_policy_constraints")
    if packet["output_contract"] != default_output_contract():
        raise ChamferExpectedDistancePolicyPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferExpectedDistancePolicyPlanValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_safe(packet["provenance"])


def compute_chamfer_expected_distance_policy_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_expected_distance_policy_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_expected_distance_policy_plan(payload: dict[str, Any]) -> dict[str, Any]:
    groups = sorted(payload.get("expected_distance_policy_groups", default_expected_distance_policy_groups()), key=lambda x: x["group_id"])

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_fixture_readiness_review_refs": sorted(payload.get("source_fixture_readiness_review_refs", [])),
        "source_fixture_consolidation_receipt_refs": sorted(payload.get("source_fixture_consolidation_receipt_refs", [])),
        "source_valid_fixture_plan_refs": sorted(payload.get("source_valid_fixture_plan_refs", [])),
        "source_invalid_fixture_plan_refs": sorted(payload.get("source_invalid_fixture_plan_refs", [])),
        "source_not_computable_fixture_plan_refs": sorted(payload.get("source_not_computable_fixture_plan_refs", [])),
        "source_baseline_implementation_plan_refs": sorted(payload.get("source_baseline_implementation_plan_refs", [])),
        "expected_distance_policy_groups": groups,
        "tolerance_policy_plan": payload.get("tolerance_policy_plan", default_tolerance_policy_plan()),
        "not_computable_distance_policy": payload.get("not_computable_distance_policy", default_not_computable_distance_policy()),
        "review_gate_plan": payload.get("review_gate_plan", default_review_gate_plan()),
        "policy_constraints": payload.get("policy_constraints", default_policy_constraints()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_expected_distance_policy_plan_hash(base)
    validate_chamfer_expected_distance_policy_plan(base)
    return _finalize(base)
