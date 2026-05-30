from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.norm_geometry_baseline_promotion_review import (
    OPERATOR_ID,
    REVIEW_ID,
    REVIEW_STAGE,
    REVIEW_STATUS,
    SCHEMA_VERSION,
    SOURCE_CLOSURE_HASH,
    SOURCE_DECISION_HASH,
    SOURCE_GATE_HASH,
    NormGeometryBaselinePromotionReviewError,
    build_norm_geometry_baseline_promotion_review,
    validate_norm_geometry_baseline_promotion_review,
)


# ── build + round-trip ─────────────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_norm_geometry_baseline_promotion_review(), dict)


def test_schema_version():
    assert build_norm_geometry_baseline_promotion_review()["schema_version"] == SCHEMA_VERSION


def test_review_id():
    assert build_norm_geometry_baseline_promotion_review()["review_id"] == REVIEW_ID


def test_operator_id():
    assert build_norm_geometry_baseline_promotion_review()["operator_id"] == OPERATOR_ID


def test_review_status():
    assert build_norm_geometry_baseline_promotion_review()["review_status"] == REVIEW_STATUS


def test_review_stage():
    assert build_norm_geometry_baseline_promotion_review()["review_stage"] == REVIEW_STAGE


def test_intended_lane():
    assert build_norm_geometry_baseline_promotion_review()["intended_lane"] == "SHADOW"


def test_source_gate_hash():
    assert build_norm_geometry_baseline_promotion_review()["source_gate_hash"] == SOURCE_GATE_HASH


def test_source_decision_hash():
    assert build_norm_geometry_baseline_promotion_review()["source_decision_hash"] == SOURCE_DECISION_HASH


def test_source_closure_hash():
    assert build_norm_geometry_baseline_promotion_review()["source_closure_hash"] == SOURCE_CLOSURE_HASH


def test_canonical_hash_64_chars():
    h = build_norm_geometry_baseline_promotion_review()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    r = build_norm_geometry_baseline_promotion_review()
    pre = {k: v for k, v in r.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == r["canonical_hash"]


def test_validate_passes():
    validate_norm_geometry_baseline_promotion_review(
        build_norm_geometry_baseline_promotion_review()
    )


def test_replay_stable():
    assert (
        build_norm_geometry_baseline_promotion_review()
        == build_norm_geometry_baseline_promotion_review()
    )


def test_recommended_next_step():
    assert (
        build_norm_geometry_baseline_promotion_review()["recommended_next_step"]
        == "NORM_GEOMETRY_BASELINE_PROMOTION_COMPLETE"
    )


# ── gate_review ────────────────────────────────────────────────────────────────


def test_gate_review_passed():
    assert (
        build_norm_geometry_baseline_promotion_review()["gate_review"]["gate_review_passed"]
        is True
    )


def test_gate_review_all_gate_passed():
    gr = build_norm_geometry_baseline_promotion_review()["gate_review"]
    assert gr["all_gate_passed"] is True


def test_gate_review_gate_id():
    gr = build_norm_geometry_baseline_promotion_review()["gate_review"]
    assert gr["gate_id"] == "norm_geometry_baseline_promotion_gate_001"


def test_gate_review_gate_status():
    gr = build_norm_geometry_baseline_promotion_review()["gate_review"]
    assert gr["gate_status"] == "NORM_GEOMETRY_BASELINE_PROMOTION_GATE_READY"


def test_gate_review_pack_authorized():
    gr = build_norm_geometry_baseline_promotion_review()["gate_review"]
    assert gr["baseline_pack_update_authorized"] is True


def test_gate_review_subsections_passed():
    gr = build_norm_geometry_baseline_promotion_review()["gate_review"]
    assert gr["decision_review_passed"] is True
    assert gr["closure_review_passed"] is True
    assert gr["current_pack_review_passed"] is True
    assert gr["pack_scope_passed"] is True


# ── decision_review ────────────────────────────────────────────────────────────


def test_decision_review_passed():
    assert (
        build_norm_geometry_baseline_promotion_review()["decision_review"]["decision_review_passed"]
        is True
    )


def test_decision_review_id():
    dr = build_norm_geometry_baseline_promotion_review()["decision_review"]
    assert dr["decision_id"] == "NORM_GEOMETRY_BASELINE_PROMOTION_DECISION_2026_05_29_001"


def test_decision_review_decision():
    dr = build_norm_geometry_baseline_promotion_review()["decision_review"]
    assert dr["decision"] == "approve_norm_geometry_shadow_stub_baseline_promotion"


def test_decision_review_authorized():
    dr = build_norm_geometry_baseline_promotion_review()["decision_review"]
    assert dr["baseline_promotion_authorized"] is True


def test_decision_review_target_vector_type():
    dr = build_norm_geometry_baseline_promotion_review()["decision_review"]
    assert dr["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_decision_review_target_status():
    dr = build_norm_geometry_baseline_promotion_review()["decision_review"]
    assert dr["target_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_decision_review_all_blocks_acknowledged():
    dr = build_norm_geometry_baseline_promotion_review()["decision_review"]
    assert dr["all_blocks_acknowledged"] is True


def test_decision_review_authority_locks_all_false():
    dr = build_norm_geometry_baseline_promotion_review()["decision_review"]
    assert dr["authority_locks_all_false"] is True


# ── closure_review ─────────────────────────────────────────────────────────────


def test_closure_review_passed():
    assert (
        build_norm_geometry_baseline_promotion_review()["closure_review"]["closure_review_passed"]
        is True
    )


def test_closure_review_all_closure_passed():
    cr = build_norm_geometry_baseline_promotion_review()["closure_review"]
    assert cr["all_closure_passed"] is True


def test_closure_review_valid_fixture_count():
    cr = build_norm_geometry_baseline_promotion_review()["closure_review"]
    assert cr["valid_fixture_count"] == 6


def test_closure_review_rejection_fixture_count():
    cr = build_norm_geometry_baseline_promotion_review()["closure_review"]
    assert cr["rejection_fixture_count"] == 8


# ── baseline_pack_update_review ────────────────────────────────────────────────


def test_pack_update_review_passed():
    assert (
        build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"][
            "pack_update_review_passed"
        ]
        is True
    )


def test_pack_update_scope():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert pu["pack_update_scope"] == "NORM_GEOMETRY_ONLY"


def test_pack_update_authorized():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert pu["pack_update_authorized"] is True


def test_pack_update_previous_vector_type():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert pu["previous_vector_type"] == "VALID_METADATA_VECTOR"


def test_pack_update_new_vector_type():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert pu["new_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_pack_update_previous_status():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert pu["previous_expected_computation_status"] == "NOT_IMPLEMENTED"


def test_pack_update_new_status():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert pu["new_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_pack_update_evidence_refs_count():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert len(pu["evidence_refs"]) == 4


def test_pack_update_evidence_refs_contains_closure():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert any("norm_geometry_computation_operator_closure" in r for r in pu["evidence_refs"])


def test_pack_update_evidence_refs_contains_decision():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert any("NORM_GEOMETRY_BASELINE_PROMOTION_DECISION" in r for r in pu["evidence_refs"])


def test_pack_update_evidence_refs_contains_gate():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert any("norm_geometry_baseline_promotion_gate" in r for r in pu["evidence_refs"])


def test_pack_update_unchanged_operators_count():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert len(pu["unchanged_operators"]) == 11


def test_pack_update_unchanged_not_contain_norm_geometry():
    pu = build_norm_geometry_baseline_promotion_review()["baseline_pack_update_review"]
    assert "NORM_GEOMETRY" not in pu["unchanged_operators"]


# ── operator_state_after_update ────────────────────────────────────────────────


def test_operator_state_norm_geometry_shadow_stub():
    os_ = build_norm_geometry_baseline_promotion_review()["operator_state_after_update"]
    assert os_["NORM_GEOMETRY"]["expected_computation_status"] == "SHADOW_STUB_ONLY"
    assert os_["NORM_GEOMETRY"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_operator_state_wasserstein_shadow_stub():
    os_ = build_norm_geometry_baseline_promotion_review()["operator_state_after_update"]
    assert os_["WASSERSTEIN"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_operator_state_chamfer_shadow_stub():
    os_ = build_norm_geometry_baseline_promotion_review()["operator_state_after_update"]
    assert os_["CHAMFER_DISTANCE"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_operator_state_geodesic_shadow_stub():
    os_ = build_norm_geometry_baseline_promotion_review()["operator_state_after_update"]
    assert os_["GEODESIC"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_operator_state_transport_not_implemented():
    os_ = build_norm_geometry_baseline_promotion_review()["operator_state_after_update"]
    assert os_["TRANSPORT"]["expected_computation_status"] == "NOT_IMPLEMENTED"


def test_operator_state_count():
    os_ = build_norm_geometry_baseline_promotion_review()["operator_state_after_update"]
    assert len(os_) == 12


# ── parity_review ──────────────────────────────────────────────────────────────


def test_parity_review_passed():
    assert (
        build_norm_geometry_baseline_promotion_review()["parity_review"]["parity_review_passed"]
        is True
    )


def test_parity_review_achieved():
    pr = build_norm_geometry_baseline_promotion_review()["parity_review"]
    assert pr["parity_achieved"] is True


def test_parity_shadow_stub_operators():
    pr = build_norm_geometry_baseline_promotion_review()["parity_review"]
    assert sorted(pr["shadow_stub_operators_after_update"]) == sorted(
        ["CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "WASSERSTEIN"]
    )


def test_parity_norm_geometry_at_shadow_stub():
    pr = build_norm_geometry_baseline_promotion_review()["parity_review"]
    assert pr["norm_geometry_at_shadow_stub_after_promotion"] is True


def test_parity_wasserstein():
    pr = build_norm_geometry_baseline_promotion_review()["parity_review"]
    assert pr["wasserstein_at_shadow_stub"] is True


def test_parity_chamfer():
    pr = build_norm_geometry_baseline_promotion_review()["parity_review"]
    assert pr["chamfer_distance_at_shadow_stub"] is True


def test_parity_geodesic():
    pr = build_norm_geometry_baseline_promotion_review()["parity_review"]
    assert pr["geodesic_at_shadow_stub"] is True


# ── no_metric_emission_review ──────────────────────────────────────────────────


def test_no_metric_emission_passed():
    assert (
        build_norm_geometry_baseline_promotion_review()["no_metric_emission_review"][
            "no_metric_emission_review_passed"
        ]
        is True
    )


def test_no_metric_emission_false():
    nm = build_norm_geometry_baseline_promotion_review()["no_metric_emission_review"]
    assert nm["emits_metric_values"] is False


# ── no_forecast_influence_review ───────────────────────────────────────────────


def test_no_forecast_influence_passed():
    assert (
        build_norm_geometry_baseline_promotion_review()["no_forecast_influence_review"][
            "no_forecast_influence_review_passed"
        ]
        is True
    )


def test_no_forecast_influence_false():
    nf = build_norm_geometry_baseline_promotion_review()["no_forecast_influence_review"]
    assert nf["forecast_influence"] is False


# ── no_p43_surface_lane_review ─────────────────────────────────────────────────


def test_no_p43_passed():
    assert (
        build_norm_geometry_baseline_promotion_review()["no_p43_surface_lane_review"][
            "no_p43_surface_lane_review_passed"
        ]
        is True
    )


def test_no_p43_false():
    np43 = build_norm_geometry_baseline_promotion_review()["no_p43_surface_lane_review"]
    assert np43["p43_surface_lanes_authorized"] is False


# ── authority_locks ────────────────────────────────────────────────────────────


def test_authority_locks_advisory_only():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"]["advisory_only"]
        is True
    )


def test_authority_locks_shadow_lane_only():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"]["shadow_lane_only"]
        is True
    )


def test_authority_locks_review_only():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"][
            "baseline_promotion_review_only"
        ]
        is True
    )


def test_authority_locks_promotion_authorized():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"][
            "baseline_promotion_authorized"
        ]
        is True
    )


def test_authority_locks_pack_update_authorized():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"][
            "baseline_pack_update_authorized"
        ]
        is True
    )


def test_authority_locks_emits_metric_false():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"]["emits_metric_values"]
        is False
    )


def test_authority_locks_forecast_influence_false():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"]["forecast_influence"]
        is False
    )


def test_authority_locks_p43_false():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"][
            "p43_surface_lanes_authorized"
        ]
        is False
    )


def test_authority_locks_production_false():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"]["production_activation"]
        is False
    )


def test_authority_locks_canon_false():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"]["canon_promotion"]
        is False
    )


def test_authority_locks_runtime_mutation_false():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"]["runtime_mutation"]
        is False
    )


def test_authority_locks_execution_false():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"]["execution_authority"]
        is False
    )


def test_authority_locks_inference_false():
    assert (
        build_norm_geometry_baseline_promotion_review()["authority_locks"]["inference_authority"]
        is False
    )


# ── blocked_scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_norm_geometry_baseline_promotion_review()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False, got {val!r}"


# ── validate: wrong values ─────────────────────────────────────────────────────


def test_validate_wrong_schema_version():
    r = build_norm_geometry_baseline_promotion_review()
    r["schema_version"] = "WRONG"
    with pytest.raises(NormGeometryBaselinePromotionReviewError, match="schema_version"):
        validate_norm_geometry_baseline_promotion_review(r)


def test_validate_wrong_review_status():
    r = build_norm_geometry_baseline_promotion_review()
    r["review_status"] = "WRONG"
    with pytest.raises(NormGeometryBaselinePromotionReviewError, match="review_status"):
        validate_norm_geometry_baseline_promotion_review(r)


def test_validate_wrong_operator_id():
    r = build_norm_geometry_baseline_promotion_review()
    r["operator_id"] = "WRONG"
    with pytest.raises(NormGeometryBaselinePromotionReviewError, match="operator_id"):
        validate_norm_geometry_baseline_promotion_review(r)


def test_validate_wrong_intended_lane():
    r = build_norm_geometry_baseline_promotion_review()
    r["intended_lane"] = "PRODUCTION"
    with pytest.raises(NormGeometryBaselinePromotionReviewError, match="intended_lane"):
        validate_norm_geometry_baseline_promotion_review(r)


def test_validate_wrong_gate_hash():
    r = build_norm_geometry_baseline_promotion_review()
    r["source_gate_hash"] = "a" * 64
    with pytest.raises(NormGeometryBaselinePromotionReviewError, match="source_gate_hash"):
        validate_norm_geometry_baseline_promotion_review(r)


def test_validate_wrong_decision_hash():
    r = build_norm_geometry_baseline_promotion_review()
    r["source_decision_hash"] = "b" * 64
    with pytest.raises(NormGeometryBaselinePromotionReviewError, match="source_decision_hash"):
        validate_norm_geometry_baseline_promotion_review(r)


def test_validate_wrong_closure_hash():
    r = build_norm_geometry_baseline_promotion_review()
    r["source_closure_hash"] = "c" * 64
    with pytest.raises(NormGeometryBaselinePromotionReviewError, match="source_closure_hash"):
        validate_norm_geometry_baseline_promotion_review(r)


def test_validate_canonical_hash_mismatch():
    r = build_norm_geometry_baseline_promotion_review()
    r["canonical_hash"] = "d" * 64
    with pytest.raises(NormGeometryBaselinePromotionReviewError, match="canonical_hash"):
        validate_norm_geometry_baseline_promotion_review(r)


def test_validate_authority_lock_emits_true_fails():
    r = build_norm_geometry_baseline_promotion_review()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["emits_metric_values"] = True
    with pytest.raises(
        NormGeometryBaselinePromotionReviewError, match="emits_metric_values"
    ):
        validate_norm_geometry_baseline_promotion_review(r)


def test_validate_authority_lock_advisory_false_fails():
    r = build_norm_geometry_baseline_promotion_review()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["advisory_only"] = False
    with pytest.raises(NormGeometryBaselinePromotionReviewError, match="advisory_only"):
        validate_norm_geometry_baseline_promotion_review(r)


def test_validate_review_only_false_fails():
    r = build_norm_geometry_baseline_promotion_review()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["baseline_promotion_review_only"] = False
    with pytest.raises(
        NormGeometryBaselinePromotionReviewError, match="baseline_promotion_review_only"
    ):
        validate_norm_geometry_baseline_promotion_review(r)
