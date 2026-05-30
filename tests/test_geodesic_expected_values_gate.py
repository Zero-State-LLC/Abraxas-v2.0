from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.geodesic_expected_values_gate import (
    GATE_ID,
    GATE_STAGE,
    GATE_STATUS,
    INVALID_FIXTURE_IDS,
    NC_FIXTURE_IDS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SOURCE_FIXTURE_MANIFEST_HASH,
    SOURCE_FIXTURE_PLAN_HASH,
    VALID_FIXTURE_IDS,
    GeodesicExpectedValuesGateValidationError,
    build_expected_values_gate,
    validate_expected_values_gate,
)


# ── build + validate round-trip ────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_expected_values_gate(), dict)


def test_schema_version():
    assert build_expected_values_gate()["schema_version"] == SCHEMA_VERSION


def test_gate_id():
    assert build_expected_values_gate()["gate_id"] == GATE_ID


def test_operator_id():
    assert build_expected_values_gate()["operator_id"] == OPERATOR_ID


def test_gate_status():
    assert build_expected_values_gate()["gate_status"] == GATE_STATUS


def test_gate_stage():
    assert build_expected_values_gate()["gate_stage"] == GATE_STAGE


def test_intended_lane_shadow():
    assert build_expected_values_gate()["intended_lane"] == "SHADOW"


def test_source_fixture_plan_hash():
    assert build_expected_values_gate()["source_fixture_plan_hash"] == SOURCE_FIXTURE_PLAN_HASH


def test_source_fixture_manifest_hash():
    assert build_expected_values_gate()["source_fixture_manifest_hash"] == SOURCE_FIXTURE_MANIFEST_HASH


def test_canonical_hash_present_and_64_chars():
    h = build_expected_values_gate()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    gate = build_expected_values_gate()
    pre = {k: v for k, v in gate.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == gate["canonical_hash"]


def test_validate_passes():
    validate_expected_values_gate(build_expected_values_gate())


def test_replay_stable():
    assert build_expected_values_gate() == build_expected_values_gate()


def test_recommended_next_step():
    gate = build_expected_values_gate()
    assert gate["recommended_next_step"] == "GEODESIC_EXPECTED_VALUES_ADDITION_RECEIPT"


# ── valid fixture review ───────────────────────────────────────────────────────


def test_valid_fixture_review_count():
    vfr = build_expected_values_gate()["valid_fixture_review"]
    assert vfr["fixture_count"] == 5


def test_valid_fixture_review_ids():
    vfr = build_expected_values_gate()["valid_fixture_review"]
    assert set(vfr["fixtures_reviewed"]) == set(VALID_FIXTURE_IDS)


def test_valid_fixture_review_addition_permitted():
    vfr = build_expected_values_gate()["valid_fixture_review"]
    assert vfr["addition_permitted"] is True


def test_valid_fixture_review_computation_blocked():
    vfr = build_expected_values_gate()["valid_fixture_review"]
    assert vfr["computation_blocked"] is True


def test_valid_fixture_review_current_state_no_expected_distance():
    vfr = build_expected_values_gate()["valid_fixture_review"]
    for fid in VALID_FIXTURE_IDS:
        assert vfr["current_state"][fid]["expected_geodesic_distance_included"] is False


def test_valid_fixture_review_current_state_no_metric_value():
    vfr = build_expected_values_gate()["valid_fixture_review"]
    for fid in VALID_FIXTURE_IDS:
        assert vfr["current_state"][fid]["metric_value_emitted"] is False


# ── expected value authorization scope ────────────────────────────────────────


def test_authorization_scope_fixture_count():
    scope = build_expected_values_gate()["expected_value_authorization_scope"]
    assert scope["authorized_fixture_count"] == 5


def test_authorization_scope_type():
    scope = build_expected_values_gate()["expected_value_authorization_scope"]
    assert scope["authorization_type"] == "STATIC_DECLARED_VALUES_ONLY"


def test_authorization_scope_computation_blocked():
    scope = build_expected_values_gate()["expected_value_authorization_scope"]
    assert scope["computation_blocked"] is True


def test_authorization_scope_runtime_math_blocked():
    scope = build_expected_values_gate()["expected_value_authorization_scope"]
    assert scope["runtime_math_blocked"] is True


def test_authorization_scope_metric_emission_blocked():
    scope = build_expected_values_gate()["expected_value_authorization_scope"]
    assert scope["metric_emission_blocked"] is True


def test_authorization_scope_files_not_modified_by_gate():
    scope = build_expected_values_gate()["expected_value_authorization_scope"]
    assert scope["fixture_files_not_modified_by_gate"] is True


# ── exclusion scopes ───────────────────────────────────────────────────────────


def test_invalid_exclusion_count():
    exc = build_expected_values_gate()["invalid_fixture_exclusion_scope"]
    assert exc["excluded_fixture_count"] == 4


def test_invalid_exclusion_ids():
    exc = build_expected_values_gate()["invalid_fixture_exclusion_scope"]
    assert set(exc["excluded_fixture_ids"]) == set(INVALID_FIXTURE_IDS)


def test_invalid_exclusion_distance_blocked():
    exc = build_expected_values_gate()["invalid_fixture_exclusion_scope"]
    assert exc["expected_geodesic_distance_blocked"] is True


def test_nc_exclusion_count():
    exc = build_expected_values_gate()["not_computable_fixture_exclusion_scope"]
    assert exc["excluded_fixture_count"] == 4


def test_nc_exclusion_ids():
    exc = build_expected_values_gate()["not_computable_fixture_exclusion_scope"]
    assert set(exc["excluded_fixture_ids"]) == set(NC_FIXTURE_IDS)


def test_nc_exclusion_distance_blocked():
    exc = build_expected_values_gate()["not_computable_fixture_exclusion_scope"]
    assert exc["expected_geodesic_distance_blocked"] is True


# ── blocks ─────────────────────────────────────────────────────────────────────


def test_metric_emission_block_false():
    blk = build_expected_values_gate()["metric_emission_block"]
    assert blk["emits_metric_values"] is False
    assert blk["metric_emission_blocked"] is True


def test_forecast_influence_block_false():
    blk = build_expected_values_gate()["forecast_influence_block"]
    assert blk["forecast_influence"] is False
    assert blk["forecast_blocked"] is True


def test_p43_surface_lane_block_false():
    blk = build_expected_values_gate()["p43_surface_lane_block"]
    assert blk["p43_surface_lanes_authorized"] is False
    assert blk["p43_blocked"] is True


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_expected_values_gate()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False"


# ── authority locks ────────────────────────────────────────────────────────────


def test_authority_lock_advisory_only():
    assert build_expected_values_gate()["authority_locks"]["advisory_only"] is True


def test_authority_lock_shadow_lane_only():
    assert build_expected_values_gate()["authority_locks"]["shadow_lane_only"] is True


def test_authority_lock_expected_values_gate_only():
    assert build_expected_values_gate()["authority_locks"]["expected_values_gate_only"] is True


def test_authority_lock_expected_geodesic_distances_authorized():
    assert build_expected_values_gate()["authority_locks"]["expected_geodesic_distances_authorized"] is True


def test_authority_lock_emits_metric_values_false():
    assert build_expected_values_gate()["authority_locks"]["emits_metric_values"] is False


def test_authority_lock_forecast_influence_false():
    assert build_expected_values_gate()["authority_locks"]["forecast_influence"] is False


def test_authority_lock_p43_surface_lanes_authorized_false():
    assert build_expected_values_gate()["authority_locks"]["p43_surface_lanes_authorized"] is False


def test_authority_lock_production_activation_false():
    assert build_expected_values_gate()["authority_locks"]["production_activation"] is False


def test_authority_lock_canon_promotion_false():
    assert build_expected_values_gate()["authority_locks"]["canon_promotion"] is False


def test_authority_lock_runtime_mutation_false():
    assert build_expected_values_gate()["authority_locks"]["runtime_mutation"] is False


def test_authority_lock_execution_authority_false():
    assert build_expected_values_gate()["authority_locks"]["execution_authority"] is False


def test_authority_lock_inference_authority_false():
    assert build_expected_values_gate()["authority_locks"]["inference_authority"] is False


# ── validate rejects bad inputs ────────────────────────────────────────────────


def test_validate_rejects_wrong_schema_version():
    gate = build_expected_values_gate()
    gate["schema_version"] = "Wrong.v1"
    with pytest.raises(GeodesicExpectedValuesGateValidationError):
        validate_expected_values_gate(gate)


def test_validate_rejects_wrong_operator_id():
    gate = build_expected_values_gate()
    gate["operator_id"] = "WASSERSTEIN"
    with pytest.raises(GeodesicExpectedValuesGateValidationError):
        validate_expected_values_gate(gate)


def test_validate_rejects_hash_mismatch():
    gate = build_expected_values_gate()
    gate["canonical_hash"] = "a" * 64
    with pytest.raises(GeodesicExpectedValuesGateValidationError):
        validate_expected_values_gate(gate)


def test_validate_rejects_emits_metric_values_true():
    gate = build_expected_values_gate()
    gate["authority_locks"]["emits_metric_values"] = True
    gate["canonical_hash"] = canonical_hash(
        {k: v for k, v in gate.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicExpectedValuesGateValidationError):
        validate_expected_values_gate(gate)


def test_validate_rejects_forecast_influence_true():
    gate = build_expected_values_gate()
    gate["authority_locks"]["forecast_influence"] = True
    gate["canonical_hash"] = canonical_hash(
        {k: v for k, v in gate.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicExpectedValuesGateValidationError):
        validate_expected_values_gate(gate)


def test_validate_rejects_wrong_plan_hash():
    gate = build_expected_values_gate()
    gate["source_fixture_plan_hash"] = "b" * 64
    gate["canonical_hash"] = canonical_hash(
        {k: v for k, v in gate.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicExpectedValuesGateValidationError):
        validate_expected_values_gate(gate)


def test_validate_rejects_wrong_manifest_hash():
    gate = build_expected_values_gate()
    gate["source_fixture_manifest_hash"] = "c" * 64
    gate["canonical_hash"] = canonical_hash(
        {k: v for k, v in gate.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicExpectedValuesGateValidationError):
        validate_expected_values_gate(gate)
