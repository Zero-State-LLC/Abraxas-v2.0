from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.geodesic_computation_implementation_gate import (
    GATE_ID,
    GATE_STAGE,
    GATE_STATUS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SOURCE_AUTHORIZATION_REVIEW_HASH,
    SOURCE_IMPLEMENTATION_PLAN_HASH,
    SOURCE_OPERATOR_DECISION_HASH,
    GeodesicComputationImplementationGateValidationError,
    build_computation_implementation_gate,
    validate_computation_implementation_gate,
)


# ── build + validate round-trip ────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_computation_implementation_gate(), dict)


def test_schema_version():
    assert build_computation_implementation_gate()["schema_version"] == SCHEMA_VERSION


def test_gate_id():
    assert build_computation_implementation_gate()["gate_id"] == GATE_ID


def test_operator_id():
    assert build_computation_implementation_gate()["operator_id"] == OPERATOR_ID


def test_gate_status():
    assert build_computation_implementation_gate()["gate_status"] == GATE_STATUS


def test_gate_stage():
    assert build_computation_implementation_gate()["gate_stage"] == GATE_STAGE


def test_intended_lane():
    assert build_computation_implementation_gate()["intended_lane"] == "SHADOW"


def test_source_implementation_plan_hash():
    assert (
        build_computation_implementation_gate()["source_implementation_plan_hash"]
        == SOURCE_IMPLEMENTATION_PLAN_HASH
    )


def test_source_operator_decision_hash():
    assert (
        build_computation_implementation_gate()["source_operator_decision_hash"]
        == SOURCE_OPERATOR_DECISION_HASH
    )


def test_source_authorization_review_hash():
    assert (
        build_computation_implementation_gate()["source_computation_authorization_review_hash"]
        == SOURCE_AUTHORIZATION_REVIEW_HASH
    )


def test_canonical_hash_64_chars():
    h = build_computation_implementation_gate()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    gate = build_computation_implementation_gate()
    pre = {k: v for k, v in gate.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == gate["canonical_hash"]


def test_validate_passes():
    validate_computation_implementation_gate(build_computation_implementation_gate())


def test_replay_stable():
    assert build_computation_implementation_gate() == build_computation_implementation_gate()


def test_recommended_next_step():
    assert (
        build_computation_implementation_gate()["recommended_next_step"]
        == "GEODESIC_COMPUTATION_IMPLEMENTATION"
    )


# ── implementation plan review ─────────────────────────────────────────────────


def test_plan_review_passed():
    pr = build_computation_implementation_gate()["implementation_plan_review"]
    assert pr["plan_review_passed"] is True


def test_plan_review_cpu_only():
    pr = build_computation_implementation_gate()["implementation_plan_review"]
    assert pr["cpu_only_confirmed"] is True


def test_plan_review_no_gpu():
    pr = build_computation_implementation_gate()["implementation_plan_review"]
    assert pr["no_gpu_confirmed"] is True


def test_plan_review_no_external_library():
    pr = build_computation_implementation_gate()["implementation_plan_review"]
    assert pr["no_external_library_confirmed"] is True


def test_plan_review_no_metric_emission():
    pr = build_computation_implementation_gate()["implementation_plan_review"]
    assert pr["no_runtime_metric_emission_confirmed"] is True


def test_plan_review_negative_weight_rejection():
    pr = build_computation_implementation_gate()["implementation_plan_review"]
    assert pr["negative_weight_rejection_confirmed"] is True


def test_plan_review_self_loop():
    pr = build_computation_implementation_gate()["implementation_plan_review"]
    assert pr["self_loop_zero_distance_confirmed"] is True


def test_plan_review_determinism():
    pr = build_computation_implementation_gate()["implementation_plan_review"]
    assert pr["determinism_guaranteed_confirmed"] is True


def test_plan_review_fixture_counts():
    pr = build_computation_implementation_gate()["implementation_plan_review"]
    assert pr["total_fixture_count_confirmed"] is True
    assert pr["valid_fixture_count_confirmed"] is True


# ── authorized implementation scope ───────────────────────────────────────────


def test_auth_scope_implementation_authorized():
    auth = build_computation_implementation_gate()["authorized_implementation_scope"]
    assert auth["geodesic_computation_implementation_authorized"] is True


def test_auth_scope_lane():
    auth = build_computation_implementation_gate()["authorized_implementation_scope"]
    assert auth["authorized_lane"] == "SHADOW"


def test_auth_scope_computation_type():
    auth = build_computation_implementation_gate()["authorized_implementation_scope"]
    assert auth["authorized_computation_type"] == "TEST_VECTOR_COMPUTATION_ONLY"


def test_auth_scope_bounded():
    auth = build_computation_implementation_gate()["authorized_implementation_scope"]
    assert auth["bounded_scope_only"] is True


# ── valid fixture scope ────────────────────────────────────────────────────────


def test_valid_scope_count():
    assert build_computation_implementation_gate()["valid_fixture_scope"]["fixture_count"] == 5


def test_valid_scope_computation_authorized():
    assert (
        build_computation_implementation_gate()["valid_fixture_scope"]["computation_authorized"]
        is True
    )


def test_valid_scope_no_metric_emission():
    assert (
        build_computation_implementation_gate()["valid_fixture_scope"]["metric_emission_authorized"]
        is False
    )


def test_valid_scope_no_forecast_influence():
    assert (
        build_computation_implementation_gate()["valid_fixture_scope"]["forecast_influence_authorized"]
        is False
    )


def test_valid_scope_fixture_ids_count():
    ids = build_computation_implementation_gate()["valid_fixture_scope"]["fixture_ids"]
    assert len(ids) == 5


# ── rejection fixture scope ────────────────────────────────────────────────────


def test_rejection_invalid_count():
    rs = build_computation_implementation_gate()["rejection_fixture_scope"]
    assert rs["invalid_fixture_count"] == 4


def test_rejection_nc_count():
    rs = build_computation_implementation_gate()["rejection_fixture_scope"]
    assert rs["not_computable_fixture_count"] == 4


def test_rejection_not_computed():
    rs = build_computation_implementation_gate()["rejection_fixture_scope"]
    assert rs["computation_attempted_on_rejected"] is False


def test_rejection_invalid_outcome():
    rs = build_computation_implementation_gate()["rejection_fixture_scope"]
    assert rs["invalid_rejection_outcome"] == "INVALID_INPUT"


def test_rejection_nc_outcome():
    rs = build_computation_implementation_gate()["rejection_fixture_scope"]
    assert rs["not_computable_rejection_outcome"] == "NOT_COMPUTABLE"


# ── block sections ─────────────────────────────────────────────────────────────


def test_no_metric_emission_blocked():
    b = build_computation_implementation_gate()["no_metric_emission_block"]
    assert b["emits_metric_values"] is False
    assert b["metric_emission_blocked"] is True
    assert b["block_confirmed"] is True


def test_no_forecast_influence_blocked():
    b = build_computation_implementation_gate()["no_forecast_influence_block"]
    assert b["forecast_influence"] is False
    assert b["forecast_influence_blocked"] is True
    assert b["block_confirmed"] is True


def test_no_p43_blocked():
    b = build_computation_implementation_gate()["no_p43_surface_lane_block"]
    assert b["p43_surface_lanes_authorized"] is False
    assert b["p43_blocked"] is True
    assert b["block_confirmed"] is True


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_computation_implementation_gate()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False"


# ── authority locks ────────────────────────────────────────────────────────────


def test_lock_advisory_only():
    assert build_computation_implementation_gate()["authority_locks"]["advisory_only"] is True


def test_lock_shadow_lane_only():
    assert build_computation_implementation_gate()["authority_locks"]["shadow_lane_only"] is True


def test_lock_implementation_gate_only():
    assert (
        build_computation_implementation_gate()["authority_locks"]["implementation_gate_only"] is True
    )


def test_lock_geodesic_computation_implementation_authorized_true():
    assert (
        build_computation_implementation_gate()["authority_locks"][
            "geodesic_computation_implementation_authorized"
        ]
        is True
    )


def test_lock_emits_metric_values_false():
    assert (
        build_computation_implementation_gate()["authority_locks"]["emits_metric_values"] is False
    )


def test_lock_execution_authority_false():
    assert (
        build_computation_implementation_gate()["authority_locks"]["execution_authority"] is False
    )


def test_lock_production_activation_false():
    assert (
        build_computation_implementation_gate()["authority_locks"]["production_activation"] is False
    )


# ── validate rejects bad inputs ────────────────────────────────────────────────


def test_validate_rejects_wrong_schema_version():
    gate = build_computation_implementation_gate()
    gate["schema_version"] = "Wrong.v1"
    with pytest.raises(GeodesicComputationImplementationGateValidationError):
        validate_computation_implementation_gate(gate)


def test_validate_rejects_wrong_status():
    gate = build_computation_implementation_gate()
    gate["gate_status"] = "WRONG"
    with pytest.raises(GeodesicComputationImplementationGateValidationError):
        validate_computation_implementation_gate(gate)


def test_validate_rejects_hash_mismatch():
    gate = build_computation_implementation_gate()
    gate["canonical_hash"] = "a" * 64
    with pytest.raises(GeodesicComputationImplementationGateValidationError):
        validate_computation_implementation_gate(gate)


def test_validate_rejects_wrong_plan_hash():
    gate = build_computation_implementation_gate()
    gate["source_implementation_plan_hash"] = "b" * 64
    gate["canonical_hash"] = canonical_hash(
        {k: v for k, v in gate.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationImplementationGateValidationError):
        validate_computation_implementation_gate(gate)


def test_validate_rejects_emits_metric_values_true():
    gate = build_computation_implementation_gate()
    gate["authority_locks"]["emits_metric_values"] = True
    gate["canonical_hash"] = canonical_hash(
        {k: v for k, v in gate.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationImplementationGateValidationError):
        validate_computation_implementation_gate(gate)


def test_validate_rejects_plan_review_failed():
    gate = build_computation_implementation_gate()
    gate["implementation_plan_review"]["plan_review_passed"] = False
    gate["canonical_hash"] = canonical_hash(
        {k: v for k, v in gate.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationImplementationGateValidationError):
        validate_computation_implementation_gate(gate)


def test_validate_rejects_impl_not_authorized():
    gate = build_computation_implementation_gate()
    gate["authorized_implementation_scope"]["geodesic_computation_implementation_authorized"] = False
    gate["canonical_hash"] = canonical_hash(
        {k: v for k, v in gate.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationImplementationGateValidationError):
        validate_computation_implementation_gate(gate)
