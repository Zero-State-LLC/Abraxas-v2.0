"""Tests for TransportBaselinePromotionReview.v1 — SHADOW / BASELINE_PROMOTION_REVIEW_ONLY."""
from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.transport_baseline_promotion_review import (
    OPERATOR_ID,
    REVIEW_ID,
    REVIEW_STAGE,
    REVIEW_STATUS,
    SCHEMA_VERSION,
    SOURCE_CLOSURE_HASH,
    SOURCE_DECISION_HASH,
    SOURCE_DECISION_ID,
    TransportBaselinePromotionReviewError,
    build_transport_baseline_promotion_review,
    validate_transport_baseline_promotion_review,
)


# ── helpers ───────────────────────────────────────────────────────────────────


def _review() -> dict:
    return build_transport_baseline_promotion_review()


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


def test_source_decision_id():
    assert _review()["source_decision_id"] == SOURCE_DECISION_ID


def test_source_decision_hash():
    assert _review()["source_decision_hash"] == SOURCE_DECISION_HASH


def test_source_closure_hash():
    assert _review()["source_closure_hash"] == SOURCE_CLOSURE_HASH


def test_all_reviews_passed():
    assert _review()["all_reviews_passed"] is True


def test_recommended_next_step():
    rs = _review()["recommended_next_step"]
    assert isinstance(rs, str) and len(rs) > 0


def test_canonical_hash_64_chars():
    h = _review()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_stable():
    assert _review()["canonical_hash"] == _review()["canonical_hash"]


def test_canonical_hash_recomputable():
    r = _review()
    assert canonical_hash(_preimage(r)) == r["canonical_hash"]


# ── decision_presence_review ──────────────────────────────────────────────────


def test_decision_presence_review_passed():
    assert _review()["decision_presence_review"]["review_passed"] is True


def test_decision_presence_id_confirmed():
    dpr = _review()["decision_presence_review"]
    assert dpr["decision_id_observed"] == SOURCE_DECISION_ID


def test_decision_presence_value_confirmed():
    dpr = _review()["decision_presence_review"]
    assert dpr["decision_observed"] == "approve_transport_shadow_stub_baseline_promotion_review"


def test_decision_presence_authorized_confirmed():
    dpr = _review()["decision_presence_review"]
    assert dpr["baseline_promotion_review_authorized_observed"] is True


def test_decision_presence_scope_confirmed():
    dpr = _review()["decision_presence_review"]
    assert dpr["authorized_scope_observed"] == "BASELINE_PROMOTION_REVIEW_ONLY"


def test_decision_presence_phase_closed_acknowledged():
    dpr = _review()["decision_presence_review"]
    assert dpr["transport_computation_phase_closed_acknowledged"] is True


# ── decision_hash_review ──────────────────────────────────────────────────────


def test_decision_hash_review_passed():
    assert _review()["decision_hash_review"]["review_passed"] is True


def test_decision_hash_hashes_match():
    dhr = _review()["decision_hash_review"]
    assert dhr["hashes_match"] is True
    assert dhr["observed_hash"] == SOURCE_DECISION_HASH


# ── source_closure_binding ────────────────────────────────────────────────────


def test_source_closure_binding_passed():
    assert _review()["source_closure_binding"]["review_passed"] is True


def test_source_closure_binding_hash_matches():
    scb = _review()["source_closure_binding"]
    assert scb["hashes_match"] is True
    assert scb["observed_hash"] == SOURCE_CLOSURE_HASH


def test_source_closure_binding_status_confirmed():
    scb = _review()["source_closure_binding"]
    assert scb["closure_status_confirmed"] is True
    assert scb["closure_status_observed"] == "TRANSPORT_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"


def test_source_closure_binding_all_closure_passed():
    assert _review()["source_closure_binding"]["all_closure_passed_confirmed"] is True


# ── computation_chain_closure_review ──────────────────────────────────────────


def test_computation_chain_closure_review_passed():
    assert _review()["computation_chain_closure_review"]["review_passed"] is True


def test_computation_chain_closure_phase_complete():
    assert _review()["computation_chain_closure_review"]["computation_phase_complete_confirmed"] is True


def test_computation_chain_closure_all_sections():
    ccr = _review()["computation_chain_closure_review"]
    assert ccr["valid_fixture_closure_confirmed"] is True
    assert ccr["invalid_fixture_closure_confirmed"] is True
    assert ccr["nc_fixture_closure_confirmed"] is True
    assert ccr["solver_policy_closure_confirmed"] is True
    assert ccr["authority_lock_closure_confirmed"] is True


# ── current_pack_state_review ─────────────────────────────────────────────────


def test_current_pack_state_review_passed():
    assert _review()["current_pack_state_review"]["review_passed"] is True


def test_current_pack_state_has_transport_vector():
    cps = _review()["current_pack_state_review"]
    assert "transport" in cps["transport_vector_id_observed"].lower()


def test_current_pack_state_vector_type():
    cps = _review()["current_pack_state_review"]
    assert cps["transport_vector_type_observed"] == "VALID_METADATA_VECTOR"


def test_current_pack_state_computation_status():
    cps = _review()["current_pack_state_review"]
    assert cps["expected_computation_status_observed"] == "NOT_IMPLEMENTED"


# ── target_state_review ───────────────────────────────────────────────────────


def test_target_state_review_passed():
    assert _review()["target_state_review"]["review_passed"] is True


def test_target_state_vector_type():
    tsr = _review()["target_state_review"]
    assert tsr["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_target_state_computation_status():
    tsr = _review()["target_state_review"]
    assert tsr["target_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_target_state_matches_decision():
    assert _review()["target_state_review"]["target_matches_decision"] is True


# ── promotion_scope_review ────────────────────────────────────────────────────


def test_promotion_scope_review_passed():
    assert _review()["promotion_scope_review"]["review_passed"] is True


def test_promotion_scope_pack_not_modified():
    assert _review()["promotion_scope_review"]["pack_vector_modified"] is False


def test_promotion_scope_vector_not_promoted():
    assert _review()["promotion_scope_review"]["vector_type_promoted"] is False


def test_promotion_scope_runtime_not_mutated():
    assert _review()["promotion_scope_review"]["runtime_mutated"] is False


def test_promotion_scope_no_metric_emission():
    assert _review()["promotion_scope_review"]["metric_emission_enabled"] is False


def test_promotion_scope_no_p43():
    assert _review()["promotion_scope_review"]["p43_lanes_opened"] is False


def test_promotion_scope_authorized_scope():
    assert _review()["promotion_scope_review"]["authorized_scope"] == "BASELINE_PROMOTION_REVIEW_ONLY"


# ── no_op_parity_review ───────────────────────────────────────────────────────


def test_no_op_parity_review_passed():
    assert _review()["no_op_parity_review"]["review_passed"] is True


def test_no_op_parity_confirmed():
    assert _review()["no_op_parity_review"]["no_op_parity_confirmed"] is True


def test_no_op_parity_pack_unchanged():
    assert _review()["no_op_parity_review"]["pack_vector_unchanged_through_review"] is True


def test_no_op_parity_advisory_only_preserved():
    assert _review()["no_op_parity_review"]["advisory_only_posture_preserved"] is True


def test_no_op_parity_no_metric_emission():
    assert _review()["no_op_parity_review"]["no_metric_emission_through_review"] is True


def test_no_op_parity_no_runtime_mutation():
    assert _review()["no_op_parity_review"]["no_runtime_mutation_through_review"] is True


# ── authority_lock_review ─────────────────────────────────────────────────────


def test_authority_lock_review_passed():
    assert _review()["authority_lock_review"]["review_passed"] is True


def test_authority_lock_review_true_flags():
    alr = _review()["authority_lock_review"]
    assert alr["advisory_only"] is True
    assert alr["shadow_lane_only"] is True
    assert alr["baseline_promotion_review_only"] is True
    assert alr["baseline_promotion_review_authorized"] is True
    assert alr["all_locks_intact"] is True


def test_authority_lock_review_target_vector_type():
    assert _review()["authority_lock_review"]["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_authority_lock_review_target_computation_status():
    assert _review()["authority_lock_review"]["target_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_authority_lock_review_false_flags():
    alr = _review()["authority_lock_review"]
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert alr[flag] is False, f"authority_lock_review.{flag} must be False"


# ── blocked_scope_review ──────────────────────────────────────────────────────


def test_blocked_scope_review_passed():
    assert _review()["blocked_scope_review"]["review_passed"] is True


def test_blocked_scope_review_all_false():
    assert _review()["blocked_scope_review"]["all_blocked_scopes_false"] is True


# ── authority_locks (artifact-level) ─────────────────────────────────────────


def test_authority_locks_true_flags():
    locks = _review()["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["baseline_promotion_review_only"] is True
    assert locks["baseline_promotion_review_authorized"] is True
    assert locks["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert locks["target_expected_computation_status"] == "SHADOW_STUB_ONLY"


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
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert bs[flag] is False, f"blocked_scopes.{flag} must be False"


# ── validate round-trip ───────────────────────────────────────────────────────


def test_validate_passes_on_valid_review():
    validate_transport_baseline_promotion_review(_review())


def test_validate_rejects_wrong_schema_version():
    r = _review()
    r["schema_version"] = "WRONG"
    with pytest.raises(TransportBaselinePromotionReviewError):
        validate_transport_baseline_promotion_review(r)


def test_validate_rejects_wrong_status():
    r = _review()
    r["review_status"] = "WRONG"
    with pytest.raises(TransportBaselinePromotionReviewError):
        validate_transport_baseline_promotion_review(r)


def test_validate_rejects_wrong_operator():
    r = _review()
    r["operator_id"] = "GEODESIC"
    with pytest.raises(TransportBaselinePromotionReviewError):
        validate_transport_baseline_promotion_review(r)


def test_validate_rejects_wrong_lane():
    r = _review()
    r["intended_lane"] = "PRODUCTION"
    with pytest.raises(TransportBaselinePromotionReviewError):
        validate_transport_baseline_promotion_review(r)


def test_validate_rejects_wrong_decision_hash():
    r = _review()
    r["source_decision_hash"] = "a" * 64
    with pytest.raises(TransportBaselinePromotionReviewError):
        validate_transport_baseline_promotion_review(r)


def test_validate_rejects_wrong_closure_hash():
    r = _review()
    r["source_closure_hash"] = "b" * 64
    with pytest.raises(TransportBaselinePromotionReviewError):
        validate_transport_baseline_promotion_review(r)


def test_validate_rejects_tampered_canonical_hash():
    r = _review()
    r["canonical_hash"] = "c" * 64
    with pytest.raises(TransportBaselinePromotionReviewError):
        validate_transport_baseline_promotion_review(r)
