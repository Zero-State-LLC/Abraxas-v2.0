from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.geodesic_computation_authorization_review import (
    DECLARED_EXPECTED_VALUES,
    OPERATOR_ID,
    REVIEW_ID,
    REVIEW_STAGE,
    REVIEW_STATUS,
    SCHEMA_VERSION,
    SOURCE_ADDITION_RECEIPT_HASH,
    SOURCE_COMPLETE_REVIEW_HASH,
    SOURCE_GATE_HASH,
    GeodesicComputationAuthorizationReviewValidationError,
    build_computation_authorization_review,
    validate_computation_authorization_review,
)


# ── build + validate round-trip ────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_computation_authorization_review(), dict)


def test_schema_version():
    assert build_computation_authorization_review()["schema_version"] == SCHEMA_VERSION


def test_review_id():
    assert build_computation_authorization_review()["review_id"] == REVIEW_ID


def test_operator_id():
    assert build_computation_authorization_review()["operator_id"] == OPERATOR_ID


def test_review_status():
    assert build_computation_authorization_review()["review_status"] == REVIEW_STATUS


def test_review_stage():
    assert build_computation_authorization_review()["review_stage"] == REVIEW_STAGE


def test_intended_lane():
    assert build_computation_authorization_review()["intended_lane"] == "SHADOW"


def test_source_complete_review_hash():
    assert (
        build_computation_authorization_review()["source_expected_values_complete_review_hash"]
        == SOURCE_COMPLETE_REVIEW_HASH
    )


def test_source_addition_receipt_hash():
    assert (
        build_computation_authorization_review()["source_expected_values_addition_receipt_hash"]
        == SOURCE_ADDITION_RECEIPT_HASH
    )


def test_source_gate_hash():
    assert (
        build_computation_authorization_review()["source_expected_values_gate_hash"]
        == SOURCE_GATE_HASH
    )


def test_canonical_hash_64_chars():
    h = build_computation_authorization_review()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    review = build_computation_authorization_review()
    pre = {k: v for k, v in review.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == review["canonical_hash"]


def test_validate_passes():
    validate_computation_authorization_review(build_computation_authorization_review())


def test_replay_stable():
    assert build_computation_authorization_review() == build_computation_authorization_review()


def test_recommended_next_step():
    assert (
        build_computation_authorization_review()["recommended_next_step"]
        == "GEODESIC_COMPUTATION_OPERATOR_DECISION"
    )


# ── fixture corpus readiness review ───────────────────────────────────────────


def test_corpus_total_fixture_count():
    cr = build_computation_authorization_review()["fixture_corpus_readiness_review"]
    assert cr["total_fixture_count"] == 13


def test_corpus_valid_fixture_count():
    cr = build_computation_authorization_review()["fixture_corpus_readiness_review"]
    assert cr["valid_fixture_count"] == 5


def test_corpus_invalid_fixture_count():
    cr = build_computation_authorization_review()["fixture_corpus_readiness_review"]
    assert cr["invalid_fixture_count"] == 4


def test_corpus_nc_fixture_count():
    cr = build_computation_authorization_review()["fixture_corpus_readiness_review"]
    assert cr["not_computable_fixture_count"] == 4


def test_corpus_all_valid_have_expected_distance():
    cr = build_computation_authorization_review()["fixture_corpus_readiness_review"]
    assert cr["all_valid_fixtures_have_expected_distance"] is True


def test_corpus_invalid_excluded():
    cr = build_computation_authorization_review()["fixture_corpus_readiness_review"]
    assert cr["invalid_fixtures_excluded"] is True


def test_corpus_nc_excluded():
    cr = build_computation_authorization_review()["fixture_corpus_readiness_review"]
    assert cr["not_computable_fixtures_excluded"] is True


def test_corpus_consistent():
    cr = build_computation_authorization_review()["fixture_corpus_readiness_review"]
    assert cr["corpus_consistent"] is True


def test_corpus_gate_hashes_consistent():
    cr = build_computation_authorization_review()["fixture_corpus_readiness_review"]
    assert cr["all_gate_hashes_consistent"] is True


def test_corpus_ready_for_authorization():
    cr = build_computation_authorization_review()["fixture_corpus_readiness_review"]
    assert cr["corpus_ready_for_computation_authorization"] is True


# ── expected values readiness review ──────────────────────────────────────────


def test_values_declared_count():
    vr = build_computation_authorization_review()["expected_values_readiness_review"]
    assert vr["declared_fixture_count"] == 5


def test_values_all_match_declared():
    vr = build_computation_authorization_review()["expected_values_readiness_review"]
    assert vr["all_values_match_declared"] is True


def test_values_gate_consistent():
    vr = build_computation_authorization_review()["expected_values_readiness_review"]
    assert vr["all_fixtures_gate_consistent"] is True


def test_values_entry_count_confirmed():
    vr = build_computation_authorization_review()["expected_values_readiness_review"]
    assert vr["fixture_entry_count_confirmed"] is True


def test_values_ready_for_authorization():
    vr = build_computation_authorization_review()["expected_values_readiness_review"]
    assert vr["expected_values_ready_for_computation_authorization"] is True


def test_values_declared_map():
    vr = build_computation_authorization_review()["expected_values_readiness_review"]
    for fid, ev in DECLARED_EXPECTED_VALUES.items():
        assert vr["declared_values"][fid] == ev


# ── computation scope review ───────────────────────────────────────────────────


def test_scope_computation_not_authorized():
    csr = build_computation_authorization_review()["computation_scope_review"]
    assert csr["computation_implementation_authorized"] is False


def test_scope_emits_metric_values_false():
    csr = build_computation_authorization_review()["computation_scope_review"]
    assert csr["emits_metric_values"] is False


def test_scope_forecast_influence_false():
    csr = build_computation_authorization_review()["computation_scope_review"]
    assert csr["forecast_influence"] is False


def test_scope_execution_authority_false():
    csr = build_computation_authorization_review()["computation_scope_review"]
    assert csr["execution_authority"] is False


def test_scope_intended_scope():
    csr = build_computation_authorization_review()["computation_scope_review"]
    assert csr["intended_computation_scope"] == "SHADOW_STUB_ONLY"


# ── authority lock review ──────────────────────────────────────────────────────


def test_lock_review_advisory_confirmed():
    alr = build_computation_authorization_review()["authority_lock_review"]
    assert alr["advisory_only_confirmed"] is True


def test_lock_review_shadow_confirmed():
    alr = build_computation_authorization_review()["authority_lock_review"]
    assert alr["shadow_lane_only_confirmed"] is True


def test_lock_review_no_metric_emission():
    alr = build_computation_authorization_review()["authority_lock_review"]
    assert alr["no_metric_emission_confirmed"] is True


def test_lock_review_no_execution_authority():
    alr = build_computation_authorization_review()["authority_lock_review"]
    assert alr["no_execution_authority_confirmed"] is True


# ── operator authorization requirement ────────────────────────────────────────


def test_op_requirement_separate_decision_required():
    op = build_computation_authorization_review()["operator_authorization_requirement"]
    assert op["separate_operator_decision_required"] is True


def test_op_requirement_decision_artifact_absent():
    op = build_computation_authorization_review()["operator_authorization_requirement"]
    assert op["operator_decision_artifact_present"] is False


def test_op_requirement_computation_blocked():
    op = build_computation_authorization_review()["operator_authorization_requirement"]
    assert op["computation_blocked_pending_operator_decision"] is True


# ── authorization recommendation ──────────────────────────────────────────────


def test_auth_recommendation_positive():
    ar = build_computation_authorization_review()["authorization_recommendation"]
    assert ar["recommend_geodesic_computation_authorization"] is True


def test_auth_computation_not_granted():
    ar = build_computation_authorization_review()["authorization_recommendation"]
    assert ar["geodesic_computation_authorized"] is False


def test_auth_emits_metric_values_false():
    ar = build_computation_authorization_review()["authorization_recommendation"]
    assert ar["emits_metric_values"] is False


def test_auth_forecast_influence_false():
    ar = build_computation_authorization_review()["authorization_recommendation"]
    assert ar["forecast_influence"] is False


def test_auth_p43_false():
    ar = build_computation_authorization_review()["authorization_recommendation"]
    assert ar["p43_surface_lanes_authorized"] is False


def test_auth_advisory_only():
    ar = build_computation_authorization_review()["authorization_recommendation"]
    assert ar["authorization_advisory_only"] is True


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_computation_authorization_review()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False"


# ── authority locks ────────────────────────────────────────────────────────────


def test_lock_advisory_only():
    assert build_computation_authorization_review()["authority_locks"]["advisory_only"] is True


def test_lock_shadow_lane_only():
    assert build_computation_authorization_review()["authority_locks"]["shadow_lane_only"] is True


def test_lock_emits_metric_values_false():
    assert build_computation_authorization_review()["authority_locks"]["emits_metric_values"] is False


def test_lock_execution_authority_false():
    assert build_computation_authorization_review()["authority_locks"]["execution_authority"] is False


def test_lock_geodesic_computation_authorized_false():
    assert (
        build_computation_authorization_review()["authority_locks"]["geodesic_computation_authorized"]
        is False
    )


# ── validate rejects bad inputs ────────────────────────────────────────────────


def test_validate_rejects_wrong_schema_version():
    review = build_computation_authorization_review()
    review["schema_version"] = "Wrong.v1"
    with pytest.raises(GeodesicComputationAuthorizationReviewValidationError):
        validate_computation_authorization_review(review)


def test_validate_rejects_wrong_status():
    review = build_computation_authorization_review()
    review["review_status"] = "WRONG"
    with pytest.raises(GeodesicComputationAuthorizationReviewValidationError):
        validate_computation_authorization_review(review)


def test_validate_rejects_hash_mismatch():
    review = build_computation_authorization_review()
    review["canonical_hash"] = "a" * 64
    with pytest.raises(GeodesicComputationAuthorizationReviewValidationError):
        validate_computation_authorization_review(review)


def test_validate_rejects_computation_authorized_true():
    review = build_computation_authorization_review()
    review["authority_locks"]["geodesic_computation_authorized"] = True
    review["canonical_hash"] = canonical_hash(
        {k: v for k, v in review.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationAuthorizationReviewValidationError):
        validate_computation_authorization_review(review)


def test_validate_rejects_wrong_complete_review_hash():
    review = build_computation_authorization_review()
    review["source_expected_values_complete_review_hash"] = "b" * 64
    review["canonical_hash"] = canonical_hash(
        {k: v for k, v in review.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationAuthorizationReviewValidationError):
        validate_computation_authorization_review(review)


def test_validate_rejects_operator_decision_present():
    review = build_computation_authorization_review()
    review["operator_authorization_requirement"]["operator_decision_artifact_present"] = True
    review["canonical_hash"] = canonical_hash(
        {k: v for k, v in review.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationAuthorizationReviewValidationError):
        validate_computation_authorization_review(review)
