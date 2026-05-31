"""Tests for TransportComputationCompleteReview.v1 — SHADOW / REVIEW_ONLY."""
from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.transport_computation_complete_review import (
    OPERATOR_ID,
    REVIEW_ID,
    REVIEW_STAGE,
    REVIEW_STATUS,
    SCHEMA_VERSION,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    TransportComputationCompleteReviewError,
    build_computation_complete_review,
    validate_computation_complete_review,
)


# ── helpers ───────────────────────────────────────────────────────────────────


def _review() -> dict:
    return build_computation_complete_review()


def _preimage(doc: dict) -> dict:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


# ── build + identity ──────────────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(_review(), dict)


def test_schema_version():
    assert _review()["schema_version"] == SCHEMA_VERSION


def test_review_id():
    assert _review()["review_id"] == REVIEW_ID


def test_operator_id():
    assert _review()["operator_id"] == OPERATOR_ID


def test_review_status():
    assert _review()["review_status"] == REVIEW_STATUS


def test_review_stage():
    assert _review()["review_stage"] == REVIEW_STAGE


def test_intended_lane():
    assert _review()["intended_lane"] == "SHADOW"


def test_source_receipt_hash():
    assert _review()["source_computation_receipt_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH


def test_source_gate_hash():
    assert _review()["source_implementation_gate_hash"] == SOURCE_IMPLEMENTATION_GATE_HASH


def test_all_reviews_passed():
    assert _review()["all_reviews_passed"] is True


def test_recommended_next_step_present():
    assert isinstance(_review()["recommended_next_step"], str)
    assert len(_review()["recommended_next_step"]) > 0


def test_canonical_hash_64_chars():
    h = _review()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_stable():
    r1 = _review()
    r2 = _review()
    assert r1["canonical_hash"] == r2["canonical_hash"]


def test_canonical_hash_recomputable():
    r = _review()
    assert canonical_hash(_preimage(r)) == r["canonical_hash"]


# ── receipt_presence_review ───────────────────────────────────────────────────


def test_receipt_presence_review_passed():
    assert _review()["receipt_presence_review"]["review_passed"] is True


def test_receipt_presence_id_confirmed():
    assert _review()["receipt_presence_review"]["receipt_id_confirmed"] is True


def test_receipt_presence_status_confirmed():
    assert _review()["receipt_presence_review"]["receipt_status_confirmed"] is True


def test_receipt_presence_computation_executed_confirmed():
    assert _review()["receipt_presence_review"]["computation_executed_confirmed"] is True


# ── source_receipt_hash_review ────────────────────────────────────────────────


def test_source_receipt_hash_review_passed():
    assert _review()["source_receipt_hash_review"]["review_passed"] is True


def test_source_receipt_hash_review_matches():
    r = _review()["source_receipt_hash_review"]
    assert r["hash_matches_confirmed"] is True
    assert r["stored_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH


# ── implementation_gate_binding ───────────────────────────────────────────────


def test_gate_binding_review_passed():
    assert _review()["implementation_gate_binding"]["review_passed"] is True


def test_gate_binding_hash_in_provenance():
    gb = _review()["implementation_gate_binding"]
    assert gb["gate_hash_in_provenance_confirmed"] is True
    assert SOURCE_IMPLEMENTATION_GATE_HASH in gb["gate_ref_from_provenance"]


# ── valid_fixture_result_review ───────────────────────────────────────────────


def test_valid_fixture_review_passed():
    assert _review()["valid_fixture_result_review"]["review_passed"] is True


def test_valid_fixture_count():
    assert _review()["valid_fixture_result_review"]["total_valid_fixtures"] == 6


def test_valid_fixtures_all_match():
    assert _review()["valid_fixture_result_review"]["all_match_confirmed"] is True


def test_valid_per_fixture_all_passed():
    for entry in _review()["valid_fixture_result_review"]["per_fixture"]:
        assert entry["review_passed"] is True, f"{entry['fixture_id']} failed"


def test_valid_per_fixture_distances_confirmed():
    for entry in _review()["valid_fixture_result_review"]["per_fixture"]:
        assert entry["distance_matched_confirmed"] is True
        assert entry["corpus_distance_confirmed"] is True


# ── invalid_fixture_rejection_review ─────────────────────────────────────────


def test_invalid_rejection_review_passed():
    assert _review()["invalid_fixture_rejection_review"]["review_passed"] is True


def test_invalid_rejected_fixture_count():
    assert _review()["invalid_fixture_rejection_review"]["total_invalid_rejected_fixtures"] == 3


def test_invalid_all_rejected_correctly():
    assert _review()["invalid_fixture_rejection_review"]["all_rejected_correctly_confirmed"] is True


def test_invalid_per_fixture_all_passed():
    for entry in _review()["invalid_fixture_rejection_review"]["per_fixture"]:
        assert entry["review_passed"] is True, f"{entry['fixture_id']} failed"
        assert entry["rejection_outcome_confirmed"] is True
        assert entry["computation_attempted_confirmed_false"] is True


# ── not_computable_fixture_rejection_review ───────────────────────────────────


def test_nc_review_passed():
    assert _review()["not_computable_fixture_rejection_review"]["review_passed"] is True


def test_nc_routed_count():
    assert _review()["not_computable_fixture_rejection_review"]["total_not_computable_routed"] == 6


def test_nc_invalid_004_routed():
    r = _review()["not_computable_fixture_rejection_review"]
    assert r["invalid_004_routed_not_computable"] is True
    assert r["invalid_004_reason_confirmed"] is True


def test_nc_type_fixtures_count():
    assert _review()["not_computable_fixture_rejection_review"]["nc_type_fixtures_count"] == 5


def test_nc_all_correct():
    assert _review()["not_computable_fixture_rejection_review"]["all_not_computable_correctly_confirmed"] is True


def test_nc_per_fixture_all_passed():
    for entry in _review()["not_computable_fixture_rejection_review"]["per_fixture"]:
        assert entry["review_passed"] is True, f"{entry['fixture_id']} failed"
        assert entry["reason_confirmed"] is True


# ── comparison_summary_review ─────────────────────────────────────────────────


def test_comparison_summary_review_passed():
    assert _review()["comparison_summary_review"]["review_passed"] is True


def test_comparison_summary_totals_confirmed():
    cs = _review()["comparison_summary_review"]
    assert cs["total_fixture_count_confirmed"] is True
    assert cs["valid_fixture_count_confirmed"] is True
    assert cs["invalid_fixture_count_confirmed"] is True
    assert cs["not_computable_fixture_count_confirmed"] is True
    assert cs["all_matched_confirmed_true"] is True


# ── solver_policy_review ──────────────────────────────────────────────────────


def test_solver_policy_review_passed():
    assert _review()["solver_policy_review"]["review_passed"] is True


def test_solver_policy_algorithm_confirmed():
    assert _review()["solver_policy_review"]["algorithm_confirmed"] is True


def test_solver_policy_pivot_rule_confirmed():
    assert _review()["solver_policy_review"]["pivot_rule_confirmed"] is True


def test_solver_policy_tie_breaking_confirmed():
    assert _review()["solver_policy_review"]["tie_breaking_rule_confirmed"] is True


def test_solver_policy_nc_branches_confirmed():
    sp = _review()["solver_policy_review"]
    assert sp["not_computable_branches_sealed_count"] == 9
    assert sp["not_computable_branches_confirmed"] is True


# ── authority reviews ─────────────────────────────────────────────────────────


def test_no_metric_emission_review_passed():
    assert _review()["no_metric_emission_review"]["review_passed"] is True


def test_no_metric_emission_value_false():
    assert _review()["no_metric_emission_review"]["emits_metric_values"] is False


def test_no_forecast_influence_review_passed():
    assert _review()["no_forecast_influence_review"]["review_passed"] is True


def test_no_forecast_influence_value_false():
    assert _review()["no_forecast_influence_review"]["forecast_influence"] is False


def test_no_p43_review_passed():
    assert _review()["no_p43_surface_lane_review"]["review_passed"] is True


def test_no_p43_value_false():
    assert _review()["no_p43_surface_lane_review"]["p43_surface_lanes_authorized"] is False


def test_authority_lock_review_passed():
    assert _review()["authority_lock_review"]["review_passed"] is True


def test_authority_lock_review_true_flags():
    r = _review()["authority_lock_review"]
    assert r["all_true_locks_confirmed"] is True
    assert r["lane_confirmed_shadow"] is True
    assert r["algorithm_confirmed"] is True


def test_authority_lock_review_false_flags():
    assert _review()["authority_lock_review"]["all_false_locks_confirmed"] is True


def test_blocked_scope_review_passed():
    assert _review()["blocked_scope_review"]["review_passed"] is True


# ── authority_locks (artifact-level) ─────────────────────────────────────────


def test_authority_locks_true_flags():
    locks = _review()["authority_locks"]
    for flag in (
        "advisory_only", "shadow_lane_only", "computation_complete_review_only",
        "test_vector_computation_only", "transport_computation_implementation_authorized",
        "lp_solver_invocation_authorized_for_test_vectors",
    ):
        assert locks[flag] is True, f"authority_locks.{flag} must be True"


def test_authority_locks_false_flags():
    locks = _review()["authority_locks"]
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert locks[flag] is False, f"authority_locks.{flag} must be False"


def test_blocked_scopes_all_false():
    bs = _review()["blocked_scopes"]
    for flag in (
        "emits_metric_values", "p43_surface_lanes_authorized", "production_activation",
        "canon_promotion", "runtime_mutation", "execution_authority", "inference_authority",
    ):
        assert bs[flag] is False, f"blocked_scopes.{flag} must be False"


# ── validate round-trip ───────────────────────────────────────────────────────


def test_validate_passes_on_valid_review():
    validate_computation_complete_review(_review())


def test_validate_rejects_wrong_schema_version():
    r = _review()
    r["schema_version"] = "WRONG"
    with pytest.raises(TransportComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_wrong_status():
    r = _review()
    r["review_status"] = "WRONG"
    with pytest.raises(TransportComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_wrong_operator():
    r = _review()
    r["operator_id"] = "GEODESIC"
    with pytest.raises(TransportComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_wrong_lane():
    r = _review()
    r["intended_lane"] = "PRODUCTION"
    with pytest.raises(TransportComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_wrong_receipt_hash():
    r = _review()
    r["source_computation_receipt_hash"] = "a" * 64
    with pytest.raises(TransportComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_wrong_gate_hash():
    r = _review()
    r["source_implementation_gate_hash"] = "b" * 64
    with pytest.raises(TransportComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_tampered_canonical_hash():
    r = _review()
    r["canonical_hash"] = "c" * 64
    with pytest.raises(TransportComputationCompleteReviewError):
        validate_computation_complete_review(r)
