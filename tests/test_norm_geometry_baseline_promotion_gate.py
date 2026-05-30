from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.norm_geometry_baseline_promotion_gate import (
    GATE_ID,
    GATE_STAGE,
    GATE_STATUS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SOURCE_CLOSURE_HASH,
    SOURCE_DECISION_HASH,
    NormGeometryBaselinePromotionGateError,
    build_baseline_promotion_gate,
    validate_baseline_promotion_gate,
)


# ── build + round-trip ─────────────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_baseline_promotion_gate(), dict)


def test_schema_version():
    assert build_baseline_promotion_gate()["schema_version"] == SCHEMA_VERSION


def test_gate_id():
    assert build_baseline_promotion_gate()["gate_id"] == GATE_ID


def test_operator_id():
    assert build_baseline_promotion_gate()["operator_id"] == OPERATOR_ID


def test_gate_status():
    assert build_baseline_promotion_gate()["gate_status"] == GATE_STATUS


def test_gate_stage():
    assert build_baseline_promotion_gate()["gate_stage"] == GATE_STAGE


def test_intended_lane():
    assert build_baseline_promotion_gate()["intended_lane"] == "SHADOW"


def test_source_decision_hash():
    assert build_baseline_promotion_gate()["source_decision_hash"] == SOURCE_DECISION_HASH


def test_source_closure_hash():
    assert build_baseline_promotion_gate()["source_closure_hash"] == SOURCE_CLOSURE_HASH


def test_all_gate_passed():
    assert build_baseline_promotion_gate()["all_gate_passed"] is True


def test_canonical_hash_64_chars():
    h = build_baseline_promotion_gate()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    r = build_baseline_promotion_gate()
    pre = {k: v for k, v in r.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == r["canonical_hash"]


def test_validate_passes():
    validate_baseline_promotion_gate(build_baseline_promotion_gate())


def test_replay_stable():
    assert build_baseline_promotion_gate() == build_baseline_promotion_gate()


def test_recommended_next_step():
    assert (
        build_baseline_promotion_gate()["recommended_next_step"]
        == "NORM_GEOMETRY_BASELINE_PROMOTION_REVIEW"
    )


# ── decision_review ────────────────────────────────────────────────────────────


def test_decision_review_passed():
    assert (
        build_baseline_promotion_gate()["decision_review"]["decision_review_passed"]
        is True
    )


def test_decision_review_id():
    dr = build_baseline_promotion_gate()["decision_review"]
    assert dr["decision_id"] == "NORM_GEOMETRY_BASELINE_PROMOTION_DECISION_2026_05_29_001"


def test_decision_review_decision():
    dr = build_baseline_promotion_gate()["decision_review"]
    assert dr["decision"] == "approve_norm_geometry_shadow_stub_baseline_promotion"


def test_decision_review_authorized():
    dr = build_baseline_promotion_gate()["decision_review"]
    assert dr["baseline_promotion_authorized"] is True


def test_decision_review_target_vector_type():
    dr = build_baseline_promotion_gate()["decision_review"]
    assert dr["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_decision_review_target_status():
    dr = build_baseline_promotion_gate()["decision_review"]
    assert dr["target_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_decision_review_closure_hash_acknowledged():
    dr = build_baseline_promotion_gate()["decision_review"]
    assert dr["source_closure_hash_acknowledged"] is True


def test_decision_review_all_blocks_acknowledged():
    dr = build_baseline_promotion_gate()["decision_review"]
    assert dr["all_blocks_acknowledged"] is True


def test_decision_review_authority_locks_all_false():
    dr = build_baseline_promotion_gate()["decision_review"]
    assert dr["authority_locks_all_false"] is True


# ── closure_review ─────────────────────────────────────────────────────────────


def test_closure_review_passed():
    assert (
        build_baseline_promotion_gate()["closure_review"]["closure_review_passed"]
        is True
    )


def test_closure_review_all_closure_passed():
    cr = build_baseline_promotion_gate()["closure_review"]
    assert cr["all_closure_passed"] is True


def test_closure_review_valid_fixture_count():
    cr = build_baseline_promotion_gate()["closure_review"]
    assert cr["valid_fixture_count"] == 6


def test_closure_review_rejection_fixture_count():
    cr = build_baseline_promotion_gate()["closure_review"]
    assert cr["rejection_fixture_count"] == 8


def test_closure_review_phase_completion_passed():
    cr = build_baseline_promotion_gate()["closure_review"]
    assert cr["phase_completion_passed"] is True


def test_closure_review_authority_lock_passed():
    cr = build_baseline_promotion_gate()["closure_review"]
    assert cr["authority_lock_passed"] is True


# ── current_baseline_pack_review ───────────────────────────────────────────────


def test_current_pack_review_passed():
    assert (
        build_baseline_promotion_gate()["current_baseline_pack_review"][
            "current_pack_review_passed"
        ]
        is True
    )


def test_current_pack_norm_geometry_not_yet_promoted():
    pr = build_baseline_promotion_gate()["current_baseline_pack_review"]
    assert pr["norm_geometry_not_yet_promoted"] is True


def test_current_pack_vector_type():
    pr = build_baseline_promotion_gate()["current_baseline_pack_review"]
    assert pr["norm_geometry_current_vector_type"] == "VALID_METADATA_VECTOR"


def test_current_pack_computation_status():
    pr = build_baseline_promotion_gate()["current_baseline_pack_review"]
    assert pr["norm_geometry_current_expected_computation_status"] == "NOT_IMPLEMENTED"


def test_current_pack_promotion_guard():
    pr = build_baseline_promotion_gate()["current_baseline_pack_review"]
    assert pr["promotion_guard_confirmed"] is True


# ── authorized_pack_update_scope ───────────────────────────────────────────────


def test_pack_scope_passed():
    assert (
        build_baseline_promotion_gate()["authorized_pack_update_scope"][
            "pack_update_scope_passed"
        ]
        is True
    )


def test_pack_scope_norm_geometry_only():
    ps = build_baseline_promotion_gate()["authorized_pack_update_scope"]
    assert ps["pack_update_scope"] == "NORM_GEOMETRY_ONLY"


def test_pack_scope_authorized():
    ps = build_baseline_promotion_gate()["authorized_pack_update_scope"]
    assert ps["pack_update_authorized"] is True


def test_pack_scope_new_vector_type():
    ps = build_baseline_promotion_gate()["authorized_pack_update_scope"]
    assert ps["new_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_pack_scope_new_computation_status():
    ps = build_baseline_promotion_gate()["authorized_pack_update_scope"]
    assert ps["new_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_pack_scope_previous_vector_type():
    ps = build_baseline_promotion_gate()["authorized_pack_update_scope"]
    assert ps["previous_vector_type"] == "VALID_METADATA_VECTOR"


def test_pack_scope_unchanged_operators_count():
    ps = build_baseline_promotion_gate()["authorized_pack_update_scope"]
    assert len(ps["unchanged_operators"]) == 11


def test_pack_scope_unchanged_not_contain_norm_geometry():
    ps = build_baseline_promotion_gate()["authorized_pack_update_scope"]
    assert "NORM_GEOMETRY" not in ps["unchanged_operators"]


# ── authority_locks ────────────────────────────────────────────────────────────


def test_authority_locks_advisory_only():
    assert build_baseline_promotion_gate()["authority_locks"]["advisory_only"] is True


def test_authority_locks_shadow_lane_only():
    assert build_baseline_promotion_gate()["authority_locks"]["shadow_lane_only"] is True


def test_authority_locks_gate_only():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["baseline_promotion_gate_only"]
        is True
    )


def test_authority_locks_promotion_authorized():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["baseline_promotion_authorized"]
        is True
    )


def test_authority_locks_pack_update_authorized():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["baseline_pack_update_authorized"]
        is True
    )


def test_authority_locks_emits_metric_false():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["emits_metric_values"] is False
    )


def test_authority_locks_forecast_influence_false():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["forecast_influence"] is False
    )


def test_authority_locks_p43_false():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["p43_surface_lanes_authorized"]
        is False
    )


def test_authority_locks_production_false():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["production_activation"] is False
    )


def test_authority_locks_canon_false():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["canon_promotion"] is False
    )


def test_authority_locks_runtime_mutation_false():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["runtime_mutation"] is False
    )


def test_authority_locks_execution_false():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["execution_authority"] is False
    )


def test_authority_locks_inference_false():
    assert (
        build_baseline_promotion_gate()["authority_locks"]["inference_authority"] is False
    )


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_baseline_promotion_gate()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False, got {val!r}"


# ── validate: wrong values ─────────────────────────────────────────────────────


def test_validate_wrong_schema_version():
    r = build_baseline_promotion_gate()
    r["schema_version"] = "WRONG"
    with pytest.raises(NormGeometryBaselinePromotionGateError, match="schema_version"):
        validate_baseline_promotion_gate(r)


def test_validate_wrong_gate_status():
    r = build_baseline_promotion_gate()
    r["gate_status"] = "WRONG"
    with pytest.raises(NormGeometryBaselinePromotionGateError, match="gate_status"):
        validate_baseline_promotion_gate(r)


def test_validate_wrong_operator_id():
    r = build_baseline_promotion_gate()
    r["operator_id"] = "WRONG"
    with pytest.raises(NormGeometryBaselinePromotionGateError, match="operator_id"):
        validate_baseline_promotion_gate(r)


def test_validate_wrong_intended_lane():
    r = build_baseline_promotion_gate()
    r["intended_lane"] = "PRODUCTION"
    with pytest.raises(NormGeometryBaselinePromotionGateError, match="intended_lane"):
        validate_baseline_promotion_gate(r)


def test_validate_wrong_decision_hash():
    r = build_baseline_promotion_gate()
    r["source_decision_hash"] = "a" * 64
    with pytest.raises(NormGeometryBaselinePromotionGateError, match="source_decision_hash"):
        validate_baseline_promotion_gate(r)


def test_validate_wrong_closure_hash():
    r = build_baseline_promotion_gate()
    r["source_closure_hash"] = "b" * 64
    with pytest.raises(NormGeometryBaselinePromotionGateError, match="source_closure_hash"):
        validate_baseline_promotion_gate(r)


def test_validate_canonical_hash_mismatch():
    r = build_baseline_promotion_gate()
    r["canonical_hash"] = "c" * 64
    with pytest.raises(NormGeometryBaselinePromotionGateError, match="canonical_hash"):
        validate_baseline_promotion_gate(r)


def test_validate_authority_lock_emits_true_fails():
    r = build_baseline_promotion_gate()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["emits_metric_values"] = True
    with pytest.raises(
        NormGeometryBaselinePromotionGateError, match="emits_metric_values"
    ):
        validate_baseline_promotion_gate(r)


def test_validate_authority_lock_advisory_false_fails():
    r = build_baseline_promotion_gate()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["advisory_only"] = False
    with pytest.raises(NormGeometryBaselinePromotionGateError, match="advisory_only"):
        validate_baseline_promotion_gate(r)
