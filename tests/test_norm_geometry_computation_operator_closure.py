from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.norm_geometry_computation_operator_closure import (
    CLOSURE_ID,
    CLOSURE_STAGE,
    CLOSURE_STATUS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SOURCE_COMPLETE_REVIEW_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_CPU_BASELINE_PLAN_HASH,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    NormGeometryComputationOperatorClosureError,
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


def test_source_cpu_baseline_plan_hash():
    assert (
        build_computation_operator_closure()["source_cpu_baseline_plan_hash"]
        == SOURCE_CPU_BASELINE_PLAN_HASH
    )


def test_all_closure_passed():
    assert build_computation_operator_closure()["all_closure_passed"] is True


def test_canonical_hash_64_chars():
    h = build_computation_operator_closure()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    r = build_computation_operator_closure()
    pre = {k: v for k, v in r.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == r["canonical_hash"]


def test_validate_passes():
    validate_computation_operator_closure(build_computation_operator_closure())


def test_replay_stable():
    assert build_computation_operator_closure() == build_computation_operator_closure()


def test_recommended_next_step():
    assert (
        build_computation_operator_closure()["recommended_next_step"]
        == "NORM_GEOMETRY_BASELINE_PROMOTION_DECISION"
    )


# ── phase_completion_review ────────────────────────────────────────────────────


def test_phase_review_closure_passed():
    assert (
        build_computation_operator_closure()["phase_completion_review"]["closure_passed"]
        is True
    )


def test_phase_review_complete_review_present():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["complete_review_present_and_passed"] is True


def test_phase_review_computation_phase_complete():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["computation_phase_complete"] is True


def test_phase_review_valid_fixture_passed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["valid_fixture_review_passed"] is True


def test_phase_review_invalid_fixture_passed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["invalid_fixture_review_passed"] is True


def test_phase_review_nc_fixture_passed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["not_computable_fixture_review_passed"] is True


def test_phase_review_no_metric_emission():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["no_metric_emission_review_passed"] is True


def test_phase_review_no_forecast_influence():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["no_forecast_influence_review_passed"] is True


def test_phase_review_no_p43_lane():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["no_p43_surface_lane_review_passed"] is True


def test_phase_review_computation_stage_confirmed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["computation_stage_confirmed"] is True


def test_phase_review_intended_lane_confirmed():
    pr = build_computation_operator_closure()["phase_completion_review"]
    assert pr["intended_lane_confirmed"] is True


# ── valid_fixture_result_closure ───────────────────────────────────────────────


def test_valid_closure_passed():
    assert (
        build_computation_operator_closure()["valid_fixture_result_closure"]["closure_passed"]
        is True
    )


def test_valid_closure_total_6():
    vfc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert vfc["total_valid_fixtures_closed"] == 6


def test_valid_closure_all_match():
    vfc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert vfc["all_match_closed"] is True


def test_valid_closure_match_count_6():
    vfc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert vfc["match_count"] == 6


def test_valid_closure_mismatch_zero():
    vfc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert vfc["mismatch_count"] == 0


def test_valid_closure_per_fixture_ids_count():
    vfc = build_computation_operator_closure()["valid_fixture_result_closure"]
    assert len(vfc["per_fixture_ids_closed"]) == 6


def test_valid_closure_fixture_ids_contain_all():
    vfc = build_computation_operator_closure()["valid_fixture_result_closure"]
    ids = vfc["per_fixture_ids_closed"]
    assert any("v001" in fid for fid in ids)
    assert any("v002" in fid for fid in ids)
    assert any("v003" in fid for fid in ids)
    assert any("v004" in fid for fid in ids)
    assert any("v005" in fid for fid in ids)
    assert any("v006" in fid for fid in ids)


# ── rejection_fixture_closure ──────────────────────────────────────────────────


def test_rejection_closure_passed():
    assert (
        build_computation_operator_closure()["rejection_fixture_closure"]["closure_passed"]
        is True
    )


def test_rejection_closure_total_8():
    rfc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rfc["total_rejection_fixtures_closed"] == 8


def test_rejection_closure_invalid_count_4():
    rfc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rfc["invalid_fixture_count_closed"] == 4


def test_rejection_closure_nc_count_4():
    rfc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rfc["not_computable_fixture_count_closed"] == 4


def test_rejection_closure_no_computation_attempted():
    rfc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rfc["computation_attempted_on_any_rejected"] is False


def test_rejection_closure_invalid_ids_count():
    rfc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert len(rfc["per_invalid_fixture_ids_closed"]) == 4


def test_rejection_closure_nc_ids_count():
    rfc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert len(rfc["per_not_computable_fixture_ids_closed"]) == 4


def test_rejection_closure_all_invalid_closed():
    rfc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rfc["all_invalid_rejected_correctly_closed"] is True


def test_rejection_closure_all_nc_closed():
    rfc = build_computation_operator_closure()["rejection_fixture_closure"]
    assert rfc["all_not_computable_closed"] is True


# ── authority_lock_closure ─────────────────────────────────────────────────────


def test_lock_closure_passed():
    assert (
        build_computation_operator_closure()["authority_lock_closure"]["closure_passed"]
        is True
    )


def test_lock_closure_all_true_locks():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["all_true_locks_closed"] is True


def test_lock_closure_all_false_locks():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["all_false_locks_closed"] is True


def test_lock_closure_shadow_posture():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["shadow_lane_posture_closed"] is True


def test_lock_closure_test_vector_only():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["test_vector_only_posture_closed"] is True


def test_lock_closure_no_metric_emission():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["no_metric_emission_closed"] is True


def test_lock_closure_no_projection_lane_influence():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["no_projection_lane_influence_closed"] is True


def test_lock_closure_no_p43():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["no_p43_lanes_closed"] is True


def test_lock_closure_no_state_mutation():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["no_state_mutation_closed"] is True


def test_lock_closure_no_production():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["no_production_activation_closed"] is True


def test_lock_closure_no_canon():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["no_canon_promotion_closed"] is True


def test_lock_closure_no_execution_authority():
    alc = build_computation_operator_closure()["authority_lock_closure"]
    assert alc["no_execution_authority_closed"] is True


# ── authority_locks ────────────────────────────────────────────────────────────


def test_authority_locks_advisory_only():
    assert build_computation_operator_closure()["authority_locks"]["advisory_only"] is True


def test_authority_locks_shadow_lane_only():
    assert build_computation_operator_closure()["authority_locks"]["shadow_lane_only"] is True


def test_authority_locks_computation_operator_closure_only():
    assert (
        build_computation_operator_closure()["authority_locks"][
            "computation_operator_closure_only"
        ]
        is True
    )


def test_authority_locks_test_vector_computation_only():
    assert (
        build_computation_operator_closure()["authority_locks"]["test_vector_computation_only"]
        is True
    )


def test_authority_locks_norm_geometry_authorized():
    assert (
        build_computation_operator_closure()["authority_locks"][
            "norm_geometry_computation_implementation_authorized"
        ]
        is True
    )


def test_authority_locks_emits_metric_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["emits_metric_values"] is False
    )


def test_authority_locks_forecast_influence_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["forecast_influence"] is False
    )


def test_authority_locks_p43_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["p43_surface_lanes_authorized"]
        is False
    )


def test_authority_locks_production_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["production_activation"] is False
    )


def test_authority_locks_canon_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["canon_promotion"] is False
    )


def test_authority_locks_runtime_mutation_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["runtime_mutation"] is False
    )


def test_authority_locks_execution_authority_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["execution_authority"] is False
    )


def test_authority_locks_inference_authority_false():
    assert (
        build_computation_operator_closure()["authority_locks"]["inference_authority"] is False
    )


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_computation_operator_closure()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False, got {val!r}"


# ── validate: wrong values ─────────────────────────────────────────────────────


def test_validate_wrong_schema_version():
    r = build_computation_operator_closure()
    r["schema_version"] = "WRONG"
    with pytest.raises(NormGeometryComputationOperatorClosureError, match="schema_version"):
        validate_computation_operator_closure(r)


def test_validate_wrong_closure_status():
    r = build_computation_operator_closure()
    r["closure_status"] = "WRONG"
    with pytest.raises(NormGeometryComputationOperatorClosureError, match="closure_status"):
        validate_computation_operator_closure(r)


def test_validate_wrong_operator_id():
    r = build_computation_operator_closure()
    r["operator_id"] = "WRONG"
    with pytest.raises(NormGeometryComputationOperatorClosureError, match="operator_id"):
        validate_computation_operator_closure(r)


def test_validate_wrong_intended_lane():
    r = build_computation_operator_closure()
    r["intended_lane"] = "PRODUCTION"
    with pytest.raises(NormGeometryComputationOperatorClosureError, match="intended_lane"):
        validate_computation_operator_closure(r)


def test_validate_wrong_review_hash():
    r = build_computation_operator_closure()
    r["source_complete_review_hash"] = "a" * 64
    with pytest.raises(
        NormGeometryComputationOperatorClosureError, match="source_complete_review_hash"
    ):
        validate_computation_operator_closure(r)


def test_validate_wrong_receipt_hash():
    r = build_computation_operator_closure()
    r["source_computation_receipt_hash"] = "b" * 64
    with pytest.raises(
        NormGeometryComputationOperatorClosureError, match="source_computation_receipt_hash"
    ):
        validate_computation_operator_closure(r)


def test_validate_wrong_gate_hash():
    r = build_computation_operator_closure()
    r["source_implementation_gate_hash"] = "c" * 64
    with pytest.raises(
        NormGeometryComputationOperatorClosureError, match="source_implementation_gate_hash"
    ):
        validate_computation_operator_closure(r)


def test_validate_wrong_cpu_baseline_hash():
    r = build_computation_operator_closure()
    r["source_cpu_baseline_plan_hash"] = "d" * 64
    with pytest.raises(
        NormGeometryComputationOperatorClosureError, match="source_cpu_baseline_plan_hash"
    ):
        validate_computation_operator_closure(r)


def test_validate_canonical_hash_mismatch():
    r = build_computation_operator_closure()
    r["canonical_hash"] = "e" * 64
    with pytest.raises(NormGeometryComputationOperatorClosureError, match="canonical_hash"):
        validate_computation_operator_closure(r)


def test_validate_authority_lock_emits_true_fails():
    r = build_computation_operator_closure()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["emits_metric_values"] = True
    with pytest.raises(
        NormGeometryComputationOperatorClosureError, match="emits_metric_values"
    ):
        validate_computation_operator_closure(r)


def test_validate_authority_lock_advisory_false_fails():
    r = build_computation_operator_closure()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["advisory_only"] = False
    with pytest.raises(NormGeometryComputationOperatorClosureError, match="advisory_only"):
        validate_computation_operator_closure(r)
