from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.geodesic_computation_operator_closure import (
    CLOSURE_ID,
    CLOSURE_STAGE,
    CLOSURE_STATUS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SOURCE_COMPLETE_REVIEW_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    SOURCE_IMPLEMENTATION_PLAN_HASH,
    GeodesicComputationOperatorClosureError,
    build_computation_operator_closure,
    validate_computation_operator_closure,
)


# ── build + round-trip ─────────────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_computation_operator_closure(), dict)


def test_schema_version():
    assert build_computation_operator_closure()["schema_version"] == SCHEMA_VERSION


def test_closure_id():
    assert build_computation_operator_closure()["closure_id"] == CLOSURE_ID


def test_operator_id():
    assert build_computation_operator_closure()["operator_id"] == OPERATOR_ID


def test_closure_status():
    assert build_computation_operator_closure()["closure_status"] == CLOSURE_STATUS


def test_closure_stage():
    assert build_computation_operator_closure()["closure_stage"] == CLOSURE_STAGE


def test_intended_lane():
    assert build_computation_operator_closure()["intended_lane"] == "SHADOW"


def test_source_complete_review_hash():
    assert (
        build_computation_operator_closure()["source_complete_review_hash"]
        == SOURCE_COMPLETE_REVIEW_HASH
    )


def test_source_computation_receipt_hash():
    assert (
        build_computation_operator_closure()["source_computation_receipt_hash"]
        == SOURCE_COMPUTATION_RECEIPT_HASH
    )


def test_source_implementation_gate_hash():
    assert (
        build_computation_operator_closure()["source_implementation_gate_hash"]
        == SOURCE_IMPLEMENTATION_GATE_HASH
    )


def test_source_implementation_plan_hash():
    assert (
        build_computation_operator_closure()["source_implementation_plan_hash"]
        == SOURCE_IMPLEMENTATION_PLAN_HASH
    )


def test_all_closure_passed():
    assert build_computation_operator_closure()["all_closure_passed"] is True


def test_canonical_hash_64_chars():
    h = build_computation_operator_closure()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    c = build_computation_operator_closure()
    pre = {k: v for k, v in c.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == c["canonical_hash"]


def test_validate_passes():
    validate_computation_operator_closure(build_computation_operator_closure())


def test_replay_stable():
    assert build_computation_operator_closure() == build_computation_operator_closure()


def test_recommended_next_step():
    assert (
        build_computation_operator_closure()["recommended_next_step"]
        == "GEODESIC_BASELINE_PROMOTION_DECISION"
    )


# ── phase completion review ────────────────────────────────────────────────────


def test_phase_review_closure_passed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["closure_passed"] is True


def test_phase_review_complete_review_present():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["complete_review_present_and_passed"] is True


def test_phase_review_valid_fixture_review_passed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["valid_fixture_review_passed"] is True


def test_phase_review_invalid_fixture_review_passed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["invalid_fixture_review_passed"] is True


def test_phase_review_nc_fixture_review_passed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["not_computable_fixture_review_passed"] is True


def test_phase_review_no_metric_emission():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["no_metric_emission_review_passed"] is True


def test_phase_review_no_forecast_influence():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["no_forecast_influence_review_passed"] is True


def test_phase_review_no_p43():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["no_p43_surface_lane_review_passed"] is True


def test_phase_review_computation_phase_complete():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["computation_phase_complete"] is True


def test_phase_review_stage_confirmed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["computation_stage_confirmed"] is True


def test_phase_review_lane_confirmed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["intended_lane_confirmed"] is True


# ── valid fixture result closure ───────────────────────────────────────────────


def test_valid_closure_passed():
    vc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert vc["closure_passed"] is True


def test_valid_closure_total_5():
    vc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert vc["total_valid_fixtures_closed"] == 5


def test_valid_closure_all_match():
    vc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert vc["all_match_closed"] is True


def test_valid_closure_match_count():
    vc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert vc["match_count"] == 5


def test_valid_closure_mismatch_zero():
    vc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert vc["mismatch_count"] == 0


def test_valid_closure_fixture_ids_count():
    vc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert len(vc["per_fixture_ids_closed"]) == 5


# ── rejection fixture closure ──────────────────────────────────────────────────


def test_rejection_closure_passed():
    rc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rc["closure_passed"] is True


def test_rejection_closure_total_8():
    rc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rc["total_rejection_fixtures_closed"] == 8


def test_rejection_closure_invalid_count():
    rc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rc["invalid_fixture_count_closed"] == 4


def test_rejection_closure_nc_count():
    rc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rc["not_computable_fixture_count_closed"] == 4


def test_rejection_closure_all_invalid_correctly():
    rc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rc["all_invalid_rejected_correctly_closed"] is True


def test_rejection_closure_all_nc_correctly():
    rc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rc["all_not_computable_closed"] is True


def test_rejection_closure_no_computation_attempted():
    rc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rc["computation_attempted_on_any_rejected"] is False


def test_rejection_closure_invalid_ids_count():
    rc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert len(rc["per_invalid_fixture_ids_closed"]) == 4


def test_rejection_closure_nc_ids_count():
    rc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert len(rc["per_not_computable_fixture_ids_closed"]) == 4


# ── authority lock closure ─────────────────────────────────────────────────────


def test_lock_closure_passed():
    lc = build_computation_operator_closure()["authority_lock_closure"]
    assert lc["closure_passed"] is True


def test_lock_closure_all_true_closed():
    lc = build_computation_operator_closure()["authority_lock_closure"]
    assert lc["all_true_locks_closed"] is True


def test_lock_closure_all_false_closed():
    lc = build_computation_operator_closure()["authority_lock_closure"]
    assert lc["all_false_locks_closed"] is True


def test_lock_closure_shadow_posture():
    lc = build_computation_operator_closure()["authority_lock_closure"]
    assert lc["shadow_lane_posture_closed"] is True


def test_lock_closure_no_metric():
    lc = build_computation_operator_closure()["authority_lock_closure"]
    assert lc["no_metric_emission_closed"] is True


def test_lock_closure_no_forecast():
    lc = build_computation_operator_closure()["authority_lock_closure"]
    assert lc["no_forecast_influence_closed"] is True


def test_lock_closure_no_p43():
    lc = build_computation_operator_closure()["authority_lock_closure"]
    assert lc["no_p43_lanes_closed"] is True


def test_lock_closure_no_production():
    lc = build_computation_operator_closure()["authority_lock_closure"]
    assert lc["no_production_activation_closed"] is True


def test_lock_closure_no_canon():
    lc = build_computation_operator_closure()["authority_lock_closure"]
    assert lc["no_canon_promotion_closed"] is True


def test_lock_closure_no_execution():
    lc = build_computation_operator_closure()["authority_lock_closure"]
    assert lc["no_execution_authority_closed"] is True


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_computation_operator_closure()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False"


# ── authority locks ────────────────────────────────────────────────────────────


def test_lock_advisory_only():
    assert build_computation_operator_closure()["authority_locks"]["advisory_only"] is True


def test_lock_shadow_lane_only():
    assert build_computation_operator_closure()["authority_locks"]["shadow_lane_only"] is True


def test_lock_computation_operator_closure_only():
    assert (
        build_computation_operator_closure()["authority_locks"][
            "computation_operator_closure_only"
        ]
        is True
    )


def test_lock_test_vector_computation_only():
    assert (
        build_computation_operator_closure()["authority_locks"]["test_vector_computation_only"]
        is True
    )


def test_lock_geodesic_authorized():
    assert (
        build_computation_operator_closure()["authority_locks"][
            "geodesic_computation_implementation_authorized"
        ]
        is True
    )


def test_lock_emits_metric_values_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["emits_metric_values"] is False
    )


def test_lock_execution_authority_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["execution_authority"] is False
    )


def test_lock_production_activation_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["production_activation"] is False
    )


def test_lock_canon_promotion_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["canon_promotion"] is False
    )


# ── validate rejects bad inputs ────────────────────────────────────────────────


def test_validate_rejects_wrong_schema():
    c = build_computation_operator_closure()
    c["schema_version"] = "Wrong.v1"
    with pytest.raises(GeodesicComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_wrong_status():
    c = build_computation_operator_closure()
    c["closure_status"] = "WRONG"
    with pytest.raises(GeodesicComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_hash_mismatch():
    c = build_computation_operator_closure()
    c["canonical_hash"] = "a" * 64
    with pytest.raises(GeodesicComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_wrong_review_hash():
    c = build_computation_operator_closure()
    c["source_complete_review_hash"] = "b" * 64
    c["canonical_hash"] = canonical_hash(
        {k: v for k, v in c.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_all_closure_not_passed():
    c = build_computation_operator_closure()
    c["all_closure_passed"] = False
    c["canonical_hash"] = canonical_hash(
        {k: v for k, v in c.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_execution_authority_true():
    c = build_computation_operator_closure()
    c["authority_locks"]["execution_authority"] = True
    c["canonical_hash"] = canonical_hash(
        {k: v for k, v in c.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationOperatorClosureError):
        validate_computation_operator_closure(c)


def test_validate_rejects_wrong_rejection_total():
    c = build_computation_operator_closure()
    c["rejection_fixture_closure"]["total_rejection_fixtures_closed"] = 7
    c["canonical_hash"] = canonical_hash(
        {k: v for k, v in c.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationOperatorClosureError):
        validate_computation_operator_closure(c)
