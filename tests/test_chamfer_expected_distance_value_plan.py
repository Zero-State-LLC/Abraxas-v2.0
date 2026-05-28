from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_expected_distance_value_plan import (
    ChamferExpectedDistanceValuePlanValidationError,
    build_chamfer_expected_distance_value_plan,
    compute_chamfer_expected_distance_value_plan_hash,
    default_output_contract,
    default_planned_tolerance_policy,
    default_planned_value_groups,
    default_validation_plan,
    default_value_constraints,
    serialize_chamfer_expected_distance_value_plan,
)


def _payload() -> dict:
    return {
        "plan_id": "value-plan-001",
        "source_fixture_manifest_refs": ["ChamferFixtureManifest.v1:manifest-001"],
        "source_fixture_archive_receipt_refs": ["ChamferFixtureArchiveReceipt.v1:receipt-001"],
        "source_expected_distance_policy_plan_refs": ["ChamferExpectedDistancePolicyPlan.v1:plan-001"],
        "source_fixture_files_refs": ["ChamferFixtureFile.v1:fixture-001"],
        "value_plan_scope": {"plan_family": "EXPECTED_DISTANCE_VALUE_PLAN", "intended_lane": "SHADOW", "plan_stage": "IMPLEMENTATION_PLAN_ONLY"},
        "provenance": {"source": "CHAMFER_EXPECTED_DISTANCE_VALUE_PLAN_V1", "evidence_refs": ["evidence-001"], "generated_by": "agent", "upstream_schema_refs": ["contracts/canon/chamfer_expected_distance_value_plan.v1.schema.json"]},
        "created_at_utc": "2026-05-28T00:00:00Z",
        "governance_flags": {k: False for k in (
            "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
            "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution",
            "activation_approved", "authorization_granted"
        )},
    }


def test_deterministic_hash_and_serialization_stability() -> None:
    a = build_chamfer_expected_distance_value_plan(_payload())
    b = build_chamfer_expected_distance_value_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_expected_distance_value_plan(a) == serialize_chamfer_expected_distance_value_plan(b)


def test_non_empty_defaults() -> None:
    packet = build_chamfer_expected_distance_value_plan(_payload())
    assert packet["source_fixture_manifest_refs"]
    assert packet["source_fixture_archive_receipt_refs"]
    assert packet["source_expected_distance_policy_plan_refs"]
    assert packet["source_fixture_files_refs"]
    assert packet["planned_value_groups"]
    assert packet["fixture_value_mapping_plan"]
    assert packet["validation_plan"] == default_validation_plan()


def test_duplicate_rejection_and_locked_map_mutation_fails() -> None:
    p = _payload()
    g = default_planned_value_groups()[0]
    p["planned_value_groups"] = [g, dict(g)]
    with pytest.raises(ChamferExpectedDistanceValuePlanValidationError, match="duplicate_group_id"):
        build_chamfer_expected_distance_value_plan(p)

    p = _payload()
    p["planned_tolerance_policy"] = dict(default_planned_tolerance_policy(), tolerance_values_added=True)
    with pytest.raises(ChamferExpectedDistanceValuePlanValidationError, match="invalid_planned_tolerance_policy"):
        build_chamfer_expected_distance_value_plan(p)


def test_governance_true_and_expected_or_tolerance_or_runtime_flags_fail() -> None:
    p = _payload()
    p["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ChamferExpectedDistanceValuePlanValidationError, match="authority_lock_must_be_false"):
        build_chamfer_expected_distance_value_plan(p)

    p = _payload()
    p["value_constraints"] = dict(default_value_constraints(), expected_distances_added=True)
    with pytest.raises(ChamferExpectedDistanceValuePlanValidationError, match="invalid_value_constraints"):
        build_chamfer_expected_distance_value_plan(p)

    p = _payload()
    p["value_constraints"] = dict(default_value_constraints(), tolerance_values_added=True)
    with pytest.raises(ChamferExpectedDistanceValuePlanValidationError, match="invalid_value_constraints"):
        build_chamfer_expected_distance_value_plan(p)

    p = _payload()
    p["value_constraints"] = dict(default_value_constraints(), chamfer_math_added=True)
    with pytest.raises(ChamferExpectedDistanceValuePlanValidationError, match="invalid_value_constraints"):
        build_chamfer_expected_distance_value_plan(p)

    p = _payload()
    p["value_constraints"] = dict(default_value_constraints(), metric_values_emitted=True)
    with pytest.raises(ChamferExpectedDistanceValuePlanValidationError, match="invalid_value_constraints"):
        build_chamfer_expected_distance_value_plan(p)

    p = _payload()
    p["value_constraints"] = dict(default_value_constraints(), runtime_loading_enabled=True)
    with pytest.raises(ChamferExpectedDistanceValuePlanValidationError, match="invalid_value_constraints"):
        build_chamfer_expected_distance_value_plan(p)


def test_hash_excludes_canonical_hash_and_changes_on_meaningful_metadata() -> None:
    packet = build_chamfer_expected_distance_value_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_expected_distance_value_plan_hash(packet) == compute_chamfer_expected_distance_value_plan_hash(altered)

    p = _payload()
    p["value_plan_scope"] = {"plan_family": "EXPECTED_DISTANCE_VALUE_PLAN", "intended_lane": "PROJECTION", "plan_stage": "IMPLEMENTATION_PLAN_ONLY"}
    changed = build_chamfer_expected_distance_value_plan(p)
    assert packet["canonical_hash"] != changed["canonical_hash"]


def test_schema_validation_and_source_refs_id_only() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_expected_distance_value_plan.v1.schema.json").read_text(encoding="utf-8"))
    packet = build_chamfer_expected_distance_value_plan(_payload())
    jsonschema.validate(packet, schema)
    assert all(isinstance(ref, str) and ":" in ref for ref in packet["source_fixture_manifest_refs"])


def test_forbidden_provenance_and_output_contract_mutation_fails() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime execution authority"
    with pytest.raises(ChamferExpectedDistanceValuePlanValidationError, match="forbidden_provenance_tokens_detected"):
        build_chamfer_expected_distance_value_plan(p)

    p = _payload()
    p["output_contract"] = dict(default_output_contract(), emits_metric_values=True)
    with pytest.raises(ChamferExpectedDistanceValuePlanValidationError, match="invalid_output_contract"):
        build_chamfer_expected_distance_value_plan(p)
