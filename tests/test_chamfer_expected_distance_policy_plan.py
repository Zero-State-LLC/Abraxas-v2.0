from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_expected_distance_policy_plan import (
    ChamferExpectedDistancePolicyPlanValidationError,
    build_chamfer_expected_distance_policy_plan,
    compute_chamfer_expected_distance_policy_plan_hash,
    default_expected_distance_policy_groups,
    default_not_computable_distance_policy,
    default_output_contract,
    default_policy_constraints,
    default_review_gate_plan,
    default_tolerance_policy_plan,
    serialize_chamfer_expected_distance_policy_plan,
)


def _payload() -> dict:
    return {
        "plan_id": "policy-001",
        "source_fixture_readiness_review_refs": ["ChamferFixtureImplementationReadinessReview.v1:review-001"],
        "source_fixture_consolidation_receipt_refs": ["ChamferFixturePlanConsolidationReceipt.v1:receipt-001"],
        "source_valid_fixture_plan_refs": ["ChamferValidFixtureImplementationPlan.v1:plan-valid-001"],
        "source_invalid_fixture_plan_refs": ["ChamferInvalidFixtureImplementationPlan.v1:plan-invalid-001"],
        "source_not_computable_fixture_plan_refs": ["ChamferNotComputableFixtureImplementationPlan.v1:plan-nc-001"],
        "source_baseline_implementation_plan_refs": ["ChamferBaselineImplementationPlan.v1:plan-001"],
        "policy_scope": {"policy_family": "EXPECTED_DISTANCE_POLICY", "intended_lane": "SHADOW", "policy_stage": "POLICY_PLAN_ONLY"},
        "provenance": {
            "source": "CHAMFER_EXPECTED_DISTANCE_POLICY_PLAN_V1",
            "evidence_refs": ["evidence-001"],
            "generated_by": "agent",
            "upstream_schema_refs": ["contracts/canon/chamfer_expected_distance_policy_plan.v1.schema.json"],
        },
        "created_at_utc": "2026-05-28T00:00:00Z",
        "governance_flags": {k: False for k in (
            "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
            "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution",
            "activation_approved", "authorization_granted"
        )},
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_chamfer_expected_distance_policy_plan(_payload())
    b = build_chamfer_expected_distance_policy_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_expected_distance_policy_plan(a) == serialize_chamfer_expected_distance_policy_plan(b)


def test_default_groups_non_empty_and_deterministic() -> None:
    assert default_expected_distance_policy_groups() == default_expected_distance_policy_groups()
    assert default_expected_distance_policy_groups()


@pytest.mark.parametrize(
    ("path", "value", "err"),
    [
        (("policy_scope", "policy_family"), "BAD", "unknown_policy_family"),
        (("policy_scope", "intended_lane"), "BAD", "unknown_intended_lane"),
        (("policy_scope", "policy_stage"), "BAD", "unknown_policy_stage"),
        (("expected_distance_policy_groups", 0, "group_type"), "BAD", "unknown_group_type"),
        (("expected_distance_policy_groups", 0, "applicable_fixture_family"), "BAD", "unknown_applicable_fixture_family"),
        (("expected_distance_policy_groups", 0, "distance_value_status"), "BAD", "unknown_distance_value_status"),
        (("expected_distance_policy_groups", 0, "implementation_status"), "BAD", "unknown_implementation_status"),
    ],
)
def test_enum_failures(path: tuple, value: str, err: str) -> None:
    payload = _payload()
    payload["expected_distance_policy_groups"] = default_expected_distance_policy_groups()
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ChamferExpectedDistancePolicyPlanValidationError, match=err):
        build_chamfer_expected_distance_policy_plan(payload)


def test_duplicate_group_id_fails() -> None:
    payload = _payload()
    g = default_expected_distance_policy_groups()[0]
    payload["expected_distance_policy_groups"] = [g, dict(g)]
    with pytest.raises(ChamferExpectedDistancePolicyPlanValidationError, match="duplicate_group_id"):
        build_chamfer_expected_distance_policy_plan(payload)


def test_locked_maps_and_provenance_rules() -> None:
    p = _payload()
    p["tolerance_policy_plan"] = dict(default_tolerance_policy_plan(), tolerance_values_added=True)
    with pytest.raises(ChamferExpectedDistancePolicyPlanValidationError, match="invalid_tolerance_policy_plan"):
        build_chamfer_expected_distance_policy_plan(p)

    p = _payload()
    p["not_computable_distance_policy"] = dict(default_not_computable_distance_policy(), expected_distance_value_allowed_for_not_computable=True)
    with pytest.raises(ChamferExpectedDistancePolicyPlanValidationError, match="invalid_not_computable_distance_policy"):
        build_chamfer_expected_distance_policy_plan(p)

    p = _payload()
    p["review_gate_plan"] = dict(default_review_gate_plan(), operator_review_required=False)
    with pytest.raises(ChamferExpectedDistancePolicyPlanValidationError, match="invalid_review_gate_plan"):
        build_chamfer_expected_distance_policy_plan(p)

    p = _payload()
    p["policy_constraints"] = dict(default_policy_constraints(), expected_distances_added=True)
    with pytest.raises(ChamferExpectedDistancePolicyPlanValidationError, match="invalid_policy_constraints"):
        build_chamfer_expected_distance_policy_plan(p)

    p = _payload()
    p["output_contract"] = dict(default_output_contract(), emits_expected_distances=True)
    with pytest.raises(ChamferExpectedDistancePolicyPlanValidationError, match="invalid_output_contract"):
        build_chamfer_expected_distance_policy_plan(p)

    p = _payload()
    p["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ChamferExpectedDistancePolicyPlanValidationError, match="authority_lock_must_be_false"):
        build_chamfer_expected_distance_policy_plan(p)

    p = _payload()
    p["provenance"]["source"] = "runtime authority-flag"
    with pytest.raises(ChamferExpectedDistancePolicyPlanValidationError, match="forbidden_provenance_reference_detected"):
        build_chamfer_expected_distance_policy_plan(p)


def test_hash_excludes_hash_and_changes_meaningfully() -> None:
    packet = build_chamfer_expected_distance_policy_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_expected_distance_policy_plan_hash(packet) == compute_chamfer_expected_distance_policy_plan_hash(altered)

    changed_payload = _payload()
    changed_payload["expected_distance_policy_groups"] = [{**default_expected_distance_policy_groups()[0], "description": "changed"}]
    changed = build_chamfer_expected_distance_policy_plan(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]


def test_schema_validation_and_id_only_refs() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_expected_distance_policy_plan.v1.schema.json").read_text(encoding="utf-8"))
    packet = build_chamfer_expected_distance_policy_plan(_payload())
    jsonschema.validate(packet, schema)
    assert all(isinstance(ref, str) and ":" in ref for ref in packet["source_fixture_readiness_review_refs"])


def test_operator_id_mismatch_fails() -> None:
    packet = build_chamfer_expected_distance_policy_plan(_payload())
    packet["operator_id"] = "NOT_CHAMFER"
    with pytest.raises(ChamferExpectedDistancePolicyPlanValidationError, match="unknown_operator_id"):
        from core.chamfer_expected_distance_policy_plan import validate_chamfer_expected_distance_policy_plan
        validate_chamfer_expected_distance_policy_plan(packet)
