from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash
from core.chamfer_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS

SCHEMA_VERSION = "ChamferExpectedDistanceValuePlan.v1"
PLAN_TYPE = "CHAMFER_EXPECTED_DISTANCE_VALUE_PLAN"
OPERATOR_ID = "CHAMFER_DISTANCE"
FORBIDDEN = ("runtime", "authority", "execution", "forecast", "scheduler", "canon-active", "activated")


class ChamferExpectedDistanceValuePlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_planned_value_groups() -> list[dict[str, str]]:
    return [
        {"group_id": "group-001", "group_type": "valid_fixture_expected_value_group", "description": "Future valid fixture expected-distance group with values intentionally not added.", "fixture_family": "VALID_FIXTURES", "expected_value_status": "VALUES_HELD", "implementation_status": "PLANNED_ONLY"},
        {"group_id": "group-002", "group_type": "invalid_fixture_no_value_group", "description": "Invalid fixture group remains without expected distances.", "fixture_family": "INVALID_FIXTURES", "expected_value_status": "NO_VALUES_ADDED", "implementation_status": "PLANNED_ONLY"},
        {"group_id": "group-003", "group_type": "not_computable_no_value_group", "description": "Not-computable fixture group remains null-only.", "fixture_family": "NOT_COMPUTABLE_FIXTURES", "expected_value_status": "NOT_COMPUTABLE_NULL_ONLY", "implementation_status": "PLANNED_ONLY"},
    ]


def default_planned_tolerance_policy() -> dict[str, bool]:
    return {"tolerance_policy_declared": True, "tolerance_values_added": False, "absolute_tolerance_values_added": False, "relative_tolerance_values_added": False, "tolerance_execution_enabled": False}


def default_not_computable_value_policy() -> dict[str, bool]:
    return {"not_computable_cases_have_expected_distance": False, "not_computable_cases_remain_null": True, "runtime_not_computable_enabled": False}


def default_validation_plan() -> dict[str, bool]:
    return {"requires_fixture_manifest": True, "requires_all_fixture_hashes_valid": True, "requires_expected_distance_policy": True, "requires_no_expected_values_scan": True, "requires_no_tolerance_values_scan": True, "requires_no_chamfer_math_scan": True, "requires_no_metric_value_scan": True, "requires_no_authority_scan": True}


def default_value_constraints() -> dict[str, bool]:
    return {"expected_distances_added": False, "tolerance_values_added": False, "chamfer_math_added": False, "metric_values_emitted": False, "runtime_loading_enabled": False, "forecast_influence_added": False}


def default_output_contract() -> dict[str, bool]:
    return {"emits_expected_distances": False, "emits_tolerance_values": False, "emits_chamfer_outputs": False, "emits_metric_values": False, "emits_runtime_controls": False, "emits_authority_tokens": False, "emits_value_plan": True, "emits_fixture_value_mapping_metadata": True}


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ChamferExpectedDistanceValuePlanValidationError("forbidden_provenance_tokens_detected")


def validate_chamfer_expected_distance_value_plan(packet: dict[str, Any]) -> None:
    required = {"schema_version", "plan_id", "plan_type", "operator_id", "source_fixture_manifest_refs", "source_fixture_archive_receipt_refs", "source_expected_distance_policy_plan_refs", "source_fixture_files_refs", "value_plan_scope", "planned_value_groups", "planned_tolerance_policy", "fixture_value_mapping_plan", "not_computable_value_policy", "validation_plan", "value_constraints", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash"}
    missing = sorted(required - packet.keys())
    if missing:
        raise ChamferExpectedDistanceValuePlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferExpectedDistanceValuePlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise ChamferExpectedDistanceValuePlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferExpectedDistanceValuePlanValidationError("unknown_operator_id")

    for k in ("source_fixture_manifest_refs", "source_fixture_archive_receipt_refs", "source_expected_distance_policy_plan_refs", "source_fixture_files_refs"):
        if not packet[k]:
            raise ChamferExpectedDistanceValuePlanValidationError(f"{k}_must_be_non_empty")

    groups = packet["planned_value_groups"]
    if not groups:
        raise ChamferExpectedDistanceValuePlanValidationError("planned_value_groups_must_be_non_empty")
    seen = set()
    for g in groups:
        gid = g["group_id"]
        if gid in seen:
            raise ChamferExpectedDistanceValuePlanValidationError("duplicate_group_id")
        seen.add(gid)

    mapping = packet["fixture_value_mapping_plan"]
    if not mapping:
        raise ChamferExpectedDistanceValuePlanValidationError("fixture_value_mapping_plan_must_be_non_empty")
    seen_map = set()
    for m in mapping:
        mid = m["mapping_id"]
        if mid in seen_map:
            raise ChamferExpectedDistanceValuePlanValidationError("duplicate_mapping_id")
        seen_map.add(mid)

    if packet["planned_tolerance_policy"] != default_planned_tolerance_policy():
        raise ChamferExpectedDistanceValuePlanValidationError("invalid_planned_tolerance_policy")
    if packet["not_computable_value_policy"] != default_not_computable_value_policy():
        raise ChamferExpectedDistanceValuePlanValidationError("invalid_not_computable_value_policy")
    if packet["validation_plan"] != default_validation_plan():
        raise ChamferExpectedDistanceValuePlanValidationError("invalid_validation_plan")
    if packet["value_constraints"] != default_value_constraints():
        raise ChamferExpectedDistanceValuePlanValidationError("invalid_value_constraints")
    if packet["output_contract"] != default_output_contract():
        raise ChamferExpectedDistanceValuePlanValidationError("invalid_output_contract")

    for f in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(f) is not False:
            raise ChamferExpectedDistanceValuePlanValidationError(f"authority_lock_must_be_false:{f}")

    _assert_safe(packet["provenance"])


def compute_chamfer_expected_distance_value_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_expected_distance_value_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_expected_distance_value_plan(payload: dict[str, Any]) -> dict[str, Any]:
    groups = sorted(payload.get("planned_value_groups", default_planned_value_groups()), key=lambda x: x["group_id"])
    mapping = sorted(payload.get("fixture_value_mapping_plan", [{"mapping_id": "map-001", "fixture_ref": "fixture-001", "planned_group_id": "group-001", "expected_distance_value_added": False}]), key=lambda x: x["mapping_id"])
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_fixture_manifest_refs": sorted(payload.get("source_fixture_manifest_refs", [])),
        "source_fixture_archive_receipt_refs": sorted(payload.get("source_fixture_archive_receipt_refs", [])),
        "source_expected_distance_policy_plan_refs": sorted(payload.get("source_expected_distance_policy_plan_refs", [])),
        "source_fixture_files_refs": sorted(payload.get("source_fixture_files_refs", [])),
        "planned_value_groups": groups,
        "planned_tolerance_policy": payload.get("planned_tolerance_policy", default_planned_tolerance_policy()),
        "fixture_value_mapping_plan": mapping,
        "not_computable_value_policy": payload.get("not_computable_value_policy", default_not_computable_value_policy()),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "value_constraints": payload.get("value_constraints", default_value_constraints()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_expected_distance_value_plan_hash(base)
    validate_chamfer_expected_distance_value_plan(base)
    return _finalize(base)
