from __future__ import annotations

import copy
from pathlib import Path

import pytest

from core.chamfer_expected_distance_values_actual_pr_gate import (
    build_chamfer_expected_distance_values_actual_pr_gate,
    compute_chamfer_expected_distance_values_actual_pr_gate_hash,
    default_eligible_value_fixture_refs,
    default_null_locked_fixture_refs,
    serialize_chamfer_expected_distance_values_actual_pr_gate,
    validate_chamfer_expected_distance_values_actual_pr_gate,
    ChamferExpectedDistanceValuesActualPRGateValidationError,
)


def _payload():
    return {
        "gate_id": "gate-001",
        "gate_scope": {"gate_family": "EXPECTED_DISTANCE_VALUE_ACTUAL_PR_GATE", "intended_lane": "SHADOW", "gate_stage": "GATE_ONLY"},
        "governance_flags": {k: False for k in ("production_activation","canon_promotion","scheduler_mutation","runtime_authority","runtime_mutation","forecast_influence","execution_authority","token_minting_allowed","valid_for_execution","activation_approved","authorization_granted")},
        "provenance": {"source": "CHAMFER_EXPECTED_DISTANCE_VALUES_ACTUAL_PR_GATE_V1"},
        "created_at_utc": "2026-05-28T00:00:00Z",
    }


def test_defaults_and_determinism_and_hash_preimage_exclusion():
    a = build_chamfer_expected_distance_values_actual_pr_gate(_payload())
    b = build_chamfer_expected_distance_values_actual_pr_gate(_payload())
    assert a == b
    assert serialize_chamfer_expected_distance_values_actual_pr_gate(a) == serialize_chamfer_expected_distance_values_actual_pr_gate(b)
    c = copy.deepcopy(a)
    c["canonical_hash"] = "0" * 64
    assert compute_chamfer_expected_distance_values_actual_pr_gate_hash(a) == compute_chamfer_expected_distance_values_actual_pr_gate_hash(c)


def test_non_empty_defaults_and_fixture_groups():
    p = build_chamfer_expected_distance_values_actual_pr_gate(_payload())
    for k in ("source_fixture_manifest_refs","source_fixture_archive_receipt_refs","source_expected_distance_value_plan_refs","source_expected_distance_value_plan_archive_refs","source_fixture_file_refs","eligible_value_fixture_refs","null_locked_fixture_refs","blocker_findings"):
        assert p[k]
    assert {x["fixture_id"] for x in p["eligible_value_fixture_refs"]} == {"identical_point_sets","offset_point_sets","partial_overlap_point_sets","duplicate_points","multidimensional_points"}
    assert {x["fixture_id"] for x in p["null_locked_fixture_refs"]} >= {"dimension_mismatch","missing_numerical_policy"}


def test_duplicate_and_invalid_eligible_rejected():
    p = _payload()
    d = default_eligible_value_fixture_refs()
    p["eligible_value_fixture_refs"] = [d[0], d[0]]
    with pytest.raises(ChamferExpectedDistanceValuesActualPRGateValidationError):
        build_chamfer_expected_distance_values_actual_pr_gate(p)
    p = _payload()
    d = default_eligible_value_fixture_refs()
    d[0]["fixture_id"] = "missing_numerical_policy"
    p["eligible_value_fixture_refs"] = d
    with pytest.raises(ChamferExpectedDistanceValuesActualPRGateValidationError):
        build_chamfer_expected_distance_values_actual_pr_gate(p)


def test_locked_map_mutation_and_true_flags_and_forbidden_provenance_rejected():
    p = _payload()
    p["null_locked_fixture_refs"] = default_null_locked_fixture_refs()[:-1]
    with pytest.raises(ChamferExpectedDistanceValuesActualPRGateValidationError):
        build_chamfer_expected_distance_values_actual_pr_gate(p)
    p = build_chamfer_expected_distance_values_actual_pr_gate(_payload())
    p["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ChamferExpectedDistanceValuesActualPRGateValidationError):
        validate_chamfer_expected_distance_values_actual_pr_gate(p)
    p = _payload()
    p["provenance"] = {"note": "authority granted"}
    with pytest.raises(ChamferExpectedDistanceValuesActualPRGateValidationError):
        build_chamfer_expected_distance_values_actual_pr_gate(p)


def test_schema_validation_importorskip():
    jsonschema = pytest.importorskip("jsonschema")
    import json
    schema = json.loads(Path("contracts/canon/chamfer_expected_distance_values_actual_pr_gate.v1.schema.json").read_text())
    packet = build_chamfer_expected_distance_values_actual_pr_gate(_payload())
    jsonschema.Draft202012Validator(schema).validate(packet)

