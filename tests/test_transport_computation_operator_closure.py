"""Tests for TransportComputationOperatorClosure.v1 — SHADOW / CLOSURE_ONLY."""
from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.transport_computation_operator_closure import (
    CLOSURE_ID,
    CLOSURE_STAGE,
    CLOSURE_STATUS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SOURCE_COMPLETE_REVIEW_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    TransportComputationOperatorClosureError,
    build_computation_operator_closure,
    validate_computation_operator_closure,
)


# ── helpers ───────────────────────────────────────────────────────────────────


def _closure() -> dict:
    return build_computation_operator_closure()


def _preimage(doc: dict) -> dict:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


# ── build + identity ──────────────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(_closure(), dict)


def test_schema_version():
    assert _closure()["schema_version"] == SCHEMA_VERSION


def test_closure_id():
    assert _closure()["closure_id"] == CLOSURE_ID


def test_operator_id():
    assert _closure()["operator_id"] == OPERATOR_ID


def test_closure_status():
    assert _closure()["closure_status"] == CLOSURE_STATUS


def test_closure_stage():
    assert _closure()["closure_stage"] == CLOSURE_STAGE


def test_intended_lane():
    assert _closure()["intended_lane"] == "SHADOW"


def test_source_complete_review_hash():
    assert _closure()["source_complete_review_hash"] == SOURCE_COMPLETE_REVIEW_HASH


def test_source_receipt_hash():
    assert _closure()["source_computation_receipt_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH


def test_source_gate_hash():
    assert _closure()["source_implementation_gate_hash"] == SOURCE_IMPLEMENTATION_GATE_HASH


def test_all_closure_passed():
    assert _closure()["all_closure_passed"] is True


def test_recommended_next_step_present():
    rs = _closure()["recommended_next_step"]
    assert isinstance(rs, str) and len(rs) > 0


def test_canonical_hash_64_chars():
    h = _closure()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_stable():
    assert _closure()["canonical_hash"] == _closure()["canonical_hash"]


def test_canonical_hash_recomputable():
    c = _closure()
    assert canonical_hash(_preimage(c)) == c["canonical_hash"]


# ── complete_review_binding ───────────────────────────────────────────────────


def test_complete_review_binding_passed():
    assert _closure()["complete_review_binding"]["closure_passed"] is True


def test_complete_review_binding_hash_matches():
    rb = _closure()["complete_review_binding"]
    assert rb["hash_matches_confirmed"] is True
    assert rb["stored_hash"] == SOURCE_COMPLETE_REVIEW_HASH


def test_complete_review_binding_status_confirmed():
    assert _closure()["complete_review_binding"]["review_status_confirmed"] is True


def test_complete_review_binding_all_reviews_passed():
    assert _closure()["complete_review_binding"]["all_reviews_passed_confirmed"] is True


# ── computation_receipt_binding ───────────────────────────────────────────────


def test_computation_receipt_binding_passed():
    assert _closure()["computation_receipt_binding"]["closure_passed"] is True


def test_computation_receipt_binding_hash_matches():
    rb = _closure()["computation_receipt_binding"]
    assert rb["hash_matches_confirmed"] is True
    assert rb["review_bound_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH


def test_computation_receipt_binding_review_passed():
    assert _closure()["computation_receipt_binding"]["receipt_hash_review_passed_in_complete_review"] is True


# ── implementation_gate_binding ───────────────────────────────────────────────


def test_implementation_gate_binding_passed():
    assert _closure()["implementation_gate_binding"]["closure_passed"] is True


def test_implementation_gate_binding_hash_matches():
    gb = _closure()["implementation_gate_binding"]
    assert gb["hash_matches_confirmed"] is True
    assert gb["review_bound_hash"] == SOURCE_IMPLEMENTATION_GATE_HASH


def test_implementation_gate_binding_review_passed():
    assert _closure()["implementation_gate_binding"]["gate_binding_review_passed_in_complete_review"] is True


# ── phase_completion_review ───────────────────────────────────────────────────


def test_phase_completion_review_passed():
    assert _closure()["phase_completion_review"]["closure_passed"] is True


def test_phase_completion_review_all_sections():
    pc = _closure()["phase_completion_review"]
    assert pc["complete_review_present_and_passed"] is True
    assert pc["valid_fixture_review_passed"] is True
    assert pc["invalid_fixture_review_passed"] is True
    assert pc["not_computable_fixture_review_passed"] is True
    assert pc["comparison_summary_review_passed"] is True
    assert pc["authority_lock_review_passed"] is True
    assert pc["solver_policy_review_passed"] is True
    assert pc["no_metric_emission_review_passed"] is True
    assert pc["no_forecast_influence_review_passed"] is True
    assert pc["no_p43_surface_lane_review_passed"] is True
    assert pc["lane_confirmed_shadow"] is True
    assert pc["algorithm_confirmed"] is True
    assert pc["computation_phase_complete"] is True


# ── valid_fixture_result_closure ──────────────────────────────────────────────


def test_valid_fixture_closure_passed():
    assert _closure()["valid_fixture_result_closure"]["closure_passed"] is True


def test_valid_fixture_closure_count():
    assert _closure()["valid_fixture_result_closure"]["total_valid_fixtures_closed"] == 6


def test_valid_fixture_closure_all_match():
    assert _closure()["valid_fixture_result_closure"]["all_match_closed"] is True


def test_valid_fixture_closure_mismatch_zero():
    assert _closure()["valid_fixture_result_closure"]["mismatch_count"] == 0


def test_valid_fixture_closure_ids():
    ids = _closure()["valid_fixture_result_closure"]["per_fixture_ids_closed"]
    assert set(ids) == {
        "tv-valid-001", "tv-valid-002", "tv-valid-003",
        "tv-valid-004", "tv-valid-005", "tv-valid-006",
    }


# ── invalid_fixture_rejection_closure ────────────────────────────────────────


def test_invalid_rejection_closure_passed():
    assert _closure()["invalid_fixture_rejection_closure"]["closure_passed"] is True


def test_invalid_rejected_closure_count():
    assert _closure()["invalid_fixture_rejection_closure"]["total_invalid_rejected_closed"] == 3


def test_invalid_all_rejected_correctly_closed():
    assert _closure()["invalid_fixture_rejection_closure"]["all_rejected_correctly_closed"] is True


def test_invalid_computation_not_attempted():
    assert _closure()["invalid_fixture_rejection_closure"]["computation_attempted_on_any_rejected"] is False


def test_invalid_closure_ids():
    ids = _closure()["invalid_fixture_rejection_closure"]["per_fixture_ids_closed"]
    assert set(ids) == {"tv-invalid-001", "tv-invalid-002", "tv-invalid-003"}


# ── not_computable_fixture_rejection_closure ──────────────────────────────────


def test_nc_closure_passed():
    assert _closure()["not_computable_fixture_rejection_closure"]["closure_passed"] is True


def test_nc_routed_closed_count():
    assert _closure()["not_computable_fixture_rejection_closure"]["total_not_computable_routed_closed"] == 6


def test_nc_invalid_004_closed():
    assert _closure()["not_computable_fixture_rejection_closure"]["invalid_004_routed_not_computable_closed"] is True


def test_nc_type_count_closed():
    assert _closure()["not_computable_fixture_rejection_closure"]["nc_type_fixtures_count_closed"] == 5


def test_nc_all_correctly_closed():
    assert _closure()["not_computable_fixture_rejection_closure"]["all_not_computable_correctly_closed"] is True


def test_nc_closure_ids():
    ids = set(_closure()["not_computable_fixture_rejection_closure"]["per_fixture_ids_closed"])
    assert "tv-invalid-004" in ids
    for i in range(1, 6):
        assert f"tv-nc-00{i}" in ids


# ── solver_policy_closure ─────────────────────────────────────────────────────


def test_solver_policy_closure_passed():
    assert _closure()["solver_policy_closure"]["closure_passed"] is True


def test_solver_policy_deterministic_confirmed():
    assert _closure()["solver_policy_closure"]["deterministic_bounded_test_vector_policy_confirmed"] is True


def test_solver_policy_all_constants_closed():
    sp = _closure()["solver_policy_closure"]
    assert sp["algorithm_closed"] is True
    assert sp["pivot_rule_closed"] is True
    assert sp["tie_breaking_rule_closed"] is True
    assert sp["max_supply_length_closed"] is True
    assert sp["max_demand_length_closed"] is True
    assert sp["max_transport_variables_closed"] is True
    assert sp["cost_magnitude_bound_closed"] is True
    assert sp["epsilon_abs_closed"] is True
    assert sp["epsilon_rel_closed"] is True
    assert sp["not_computable_branches_closed"] is True


def test_solver_policy_nc_branches_count():
    assert _closure()["solver_policy_closure"]["not_computable_branches_sealed_count_closed"] == 9


# ── authority_lock_closure ────────────────────────────────────────────────────


def test_authority_lock_closure_passed():
    assert _closure()["authority_lock_closure"]["closure_passed"] is True


def test_authority_lock_true_locks_closed():
    assert _closure()["authority_lock_closure"]["all_true_locks_closed"] is True


def test_authority_lock_false_locks_closed():
    assert _closure()["authority_lock_closure"]["all_false_locks_closed"] is True


def test_authority_lock_postures_closed():
    alc = _closure()["authority_lock_closure"]
    assert alc["shadow_lane_posture_closed"] is True
    assert alc["test_vector_only_posture_closed"] is True
    assert alc["no_metric_emission_closed"] is True
    assert alc["no_forecast_influence_closed"] is True
    assert alc["no_p43_lanes_closed"] is True
    assert alc["no_runtime_mutation_closed"] is True
    assert alc["no_production_activation_closed"] is True
    assert alc["no_canon_promotion_closed"] is True
    assert alc["no_execution_authority_closed"] is True


# ── blocked_scope_closure ─────────────────────────────────────────────────────


def test_blocked_scope_closure_passed():
    assert _closure()["blocked_scope_closure"]["closure_passed"] is True


def test_blocked_scope_closure_all_confirmed():
    bsc = _closure()["blocked_scope_closure"]
    for key in (
        "emits_metric_values_blocked_closed",
        "p43_surface_lanes_blocked_closed",
        "production_activation_blocked_closed",
        "canon_promotion_blocked_closed",
        "runtime_mutation_blocked_closed",
        "execution_authority_blocked_closed",
        "inference_authority_blocked_closed",
        "blocked_scope_review_passed_in_complete_review",
    ):
        assert bsc[key] is True, f"blocked_scope_closure.{key} must be True"


# ── authority_locks (artifact-level) ─────────────────────────────────────────


def test_authority_locks_true_flags():
    locks = _closure()["authority_locks"]
    for flag in (
        "advisory_only", "shadow_lane_only", "computation_operator_closure_only",
        "test_vector_computation_only", "transport_computation_implementation_authorized",
        "lp_solver_invocation_authorized_for_test_vectors",
    ):
        assert locks[flag] is True, f"authority_locks.{flag} must be True"


def test_authority_locks_false_flags():
    locks = _closure()["authority_locks"]
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert locks[flag] is False, f"authority_locks.{flag} must be False"


def test_blocked_scopes_all_false():
    bs = _closure()["blocked_scopes"]
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert bs[flag] is False, f"blocked_scopes.{flag} must be False"


# ── validate round-trip ───────────────────────────────────────────────────────


def test_validate_passes_on_valid_closure():
    validate_computation_operator_closure(_closure())


def test_validate_rejects_wrong_schema_version():
    c = _closure()
    c["schema_version"] = "WRONG"
    with pytest.raises(TransportComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_wrong_status():
    c = _closure()
    c["closure_status"] = "WRONG"
    with pytest.raises(TransportComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_wrong_operator():
    c = _closure()
    c["operator_id"] = "GEODESIC"
    with pytest.raises(TransportComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_wrong_lane():
    c = _closure()
    c["intended_lane"] = "PRODUCTION"
    with pytest.raises(TransportComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_wrong_complete_review_hash():
    c = _closure()
    c["source_complete_review_hash"] = "a" * 64
    with pytest.raises(TransportComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_wrong_receipt_hash():
    c = _closure()
    c["source_computation_receipt_hash"] = "b" * 64
    with pytest.raises(TransportComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_wrong_gate_hash():
    c = _closure()
    c["source_implementation_gate_hash"] = "c" * 64
    with pytest.raises(TransportComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_tampered_canonical_hash():
    c = _closure()
    c["canonical_hash"] = "d" * 64
    with pytest.raises(TransportComputationOperatorClosureError):
        validate_computation_operator_closure(c)
