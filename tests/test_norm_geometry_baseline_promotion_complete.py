from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.norm_geometry_baseline_promotion_complete import (
    COMPLETE_ID,
    COMPLETE_STAGE,
    COMPLETE_STATUS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SOURCE_BASELINE_PACK_HASH,
    SOURCE_CLOSURE_HASH,
    SOURCE_DECISION_HASH,
    SOURCE_GATE_HASH,
    SOURCE_PROMOTION_REVIEW_HASH,
    NormGeometryBaselinePromotionCompleteError,
    build_norm_geometry_baseline_promotion_complete,
    validate_norm_geometry_baseline_promotion_complete,
)


# ── build + round-trip ─────────────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_norm_geometry_baseline_promotion_complete(), dict)


def test_schema_version():
    assert build_norm_geometry_baseline_promotion_complete()["schema_version"] == SCHEMA_VERSION


def test_complete_id():
    assert build_norm_geometry_baseline_promotion_complete()["complete_id"] == COMPLETE_ID


def test_operator_id():
    assert build_norm_geometry_baseline_promotion_complete()["operator_id"] == OPERATOR_ID


def test_complete_status():
    assert build_norm_geometry_baseline_promotion_complete()["complete_status"] == COMPLETE_STATUS


def test_complete_stage():
    assert build_norm_geometry_baseline_promotion_complete()["complete_stage"] == COMPLETE_STAGE


def test_intended_lane():
    assert build_norm_geometry_baseline_promotion_complete()["intended_lane"] == "SHADOW"


def test_source_promotion_review_hash():
    assert (
        build_norm_geometry_baseline_promotion_complete()["source_promotion_review_hash"]
        == SOURCE_PROMOTION_REVIEW_HASH
    )


def test_source_baseline_pack_hash():
    assert (
        build_norm_geometry_baseline_promotion_complete()["source_baseline_pack_hash"]
        == SOURCE_BASELINE_PACK_HASH
    )


def test_source_gate_hash():
    assert (
        build_norm_geometry_baseline_promotion_complete()["source_gate_hash"]
        == SOURCE_GATE_HASH
    )


def test_source_decision_hash():
    assert (
        build_norm_geometry_baseline_promotion_complete()["source_decision_hash"]
        == SOURCE_DECISION_HASH
    )


def test_source_closure_hash():
    assert (
        build_norm_geometry_baseline_promotion_complete()["source_closure_hash"]
        == SOURCE_CLOSURE_HASH
    )


def test_canonical_hash_64_chars():
    h = build_norm_geometry_baseline_promotion_complete()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    r = build_norm_geometry_baseline_promotion_complete()
    pre = {k: v for k, v in r.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == r["canonical_hash"]


def test_validate_passes():
    validate_norm_geometry_baseline_promotion_complete(
        build_norm_geometry_baseline_promotion_complete()
    )


def test_replay_stable():
    assert (
        build_norm_geometry_baseline_promotion_complete()
        == build_norm_geometry_baseline_promotion_complete()
    )


def test_recommended_next_step():
    assert (
        build_norm_geometry_baseline_promotion_complete()["recommended_next_step"]
        == "NORM_GEOMETRY_SHADOW_STUB_PHASE_CLOSED"
    )


# ── phase_summary ──────────────────────────────────────────────────────────────


def test_phase_summary_all_checks_passed():
    ps = build_norm_geometry_baseline_promotion_complete()["phase_summary"]
    assert ps["all_promotion_checks_passed"] is True


def test_phase_summary_norm_geometry_at_shadow_stub():
    ps = build_norm_geometry_baseline_promotion_complete()["phase_summary"]
    assert ps["norm_geometry_at_shadow_stub"] is True


def test_phase_summary_parity_achieved():
    ps = build_norm_geometry_baseline_promotion_complete()["phase_summary"]
    assert ps["parity_achieved"] is True


def test_phase_summary_promotion_review_on_main():
    ps = build_norm_geometry_baseline_promotion_complete()["phase_summary"]
    assert ps["promotion_review_on_main"] is True


def test_phase_summary_promotion_gate_on_main():
    ps = build_norm_geometry_baseline_promotion_complete()["phase_summary"]
    assert ps["promotion_gate_on_main"] is True


def test_phase_summary_baseline_pack_updated_on_main():
    ps = build_norm_geometry_baseline_promotion_complete()["phase_summary"]
    assert ps["baseline_pack_updated_on_main"] is True


def test_phase_summary_promotion_review_passed():
    ps = build_norm_geometry_baseline_promotion_complete()["phase_summary"]
    assert ps["promotion_review_passed"] is True


def test_phase_summary_review_status():
    ps = build_norm_geometry_baseline_promotion_complete()["phase_summary"]
    assert ps["promotion_review_status"] == "NORM_GEOMETRY_BASELINE_PROMOTION_REVIEW_COMPLETE"


# ── parity_confirmation ────────────────────────────────────────────────────────


def test_parity_confirmation_passed():
    pc = build_norm_geometry_baseline_promotion_complete()["parity_confirmation"]
    assert pc["parity_confirmation_passed"] is True


def test_parity_norm_geometry_shadow_stub():
    pc = build_norm_geometry_baseline_promotion_complete()["parity_confirmation"]
    assert pc["NORM_GEOMETRY"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert pc["NORM_GEOMETRY"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_parity_wasserstein_shadow_stub():
    pc = build_norm_geometry_baseline_promotion_complete()["parity_confirmation"]
    assert pc["WASSERSTEIN"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert pc["WASSERSTEIN"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_parity_chamfer_shadow_stub():
    pc = build_norm_geometry_baseline_promotion_complete()["parity_confirmation"]
    assert pc["CHAMFER_DISTANCE"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert pc["CHAMFER_DISTANCE"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_parity_geodesic_shadow_stub():
    pc = build_norm_geometry_baseline_promotion_complete()["parity_confirmation"]
    assert pc["GEODESIC"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert pc["GEODESIC"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_parity_transport_shadow_stub():
    pc = build_norm_geometry_baseline_promotion_complete()["parity_confirmation"]
    assert pc["TRANSPORT"]["expected_computation_status"] == "SHADOW_STUB_ONLY"
    assert pc["TRANSPORT"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_parity_shadow_stub_operators_five():
    pc = build_norm_geometry_baseline_promotion_complete()["parity_confirmation"]
    assert len(pc["shadow_stub_operators"]) == 5


def test_parity_shadow_stub_operators_contents():
    pc = build_norm_geometry_baseline_promotion_complete()["parity_confirmation"]
    assert sorted(pc["shadow_stub_operators"]) == sorted(
        ["WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "TRANSPORT"]
    )


# ── provenance_chain ───────────────────────────────────────────────────────────


def test_provenance_all_sources_verified():
    prov = build_norm_geometry_baseline_promotion_complete()["provenance_chain"]
    assert prov["all_sources_verified"] is True


def test_provenance_closure_hash():
    prov = build_norm_geometry_baseline_promotion_complete()["provenance_chain"]
    assert prov["norm_geometry_computation_operator_closure_hash"] == SOURCE_CLOSURE_HASH


def test_provenance_decision_hash():
    prov = build_norm_geometry_baseline_promotion_complete()["provenance_chain"]
    assert prov["norm_geometry_baseline_promotion_decision_hash"] == SOURCE_DECISION_HASH


def test_provenance_gate_hash():
    prov = build_norm_geometry_baseline_promotion_complete()["provenance_chain"]
    assert prov["norm_geometry_baseline_promotion_gate_hash"] == SOURCE_GATE_HASH


def test_provenance_review_hash():
    prov = build_norm_geometry_baseline_promotion_complete()["provenance_chain"]
    assert prov["norm_geometry_baseline_promotion_review_hash"] == SOURCE_PROMOTION_REVIEW_HASH


def test_provenance_pack_hash():
    prov = build_norm_geometry_baseline_promotion_complete()["provenance_chain"]
    assert prov["metric_operator_baseline_test_vector_pack_hash"] == SOURCE_BASELINE_PACK_HASH


# ── authority_locks ────────────────────────────────────────────────────────────


def test_authority_locks_advisory_only():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"]["advisory_only"]
        is True
    )


def test_authority_locks_shadow_lane_only():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"]["shadow_lane_only"]
        is True
    )


def test_authority_locks_complete_only():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"][
            "baseline_promotion_complete_only"
        ]
        is True
    )


def test_authority_locks_promotion_authorized():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"][
            "baseline_promotion_authorized"
        ]
        is True
    )


def test_authority_locks_pack_update_authorized():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"][
            "baseline_pack_update_authorized"
        ]
        is True
    )


def test_authority_locks_emits_metric_false():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"]["emits_metric_values"]
        is False
    )


def test_authority_locks_forecast_influence_false():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"]["forecast_influence"]
        is False
    )


def test_authority_locks_p43_false():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"][
            "p43_surface_lanes_authorized"
        ]
        is False
    )


def test_authority_locks_production_false():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"]["production_activation"]
        is False
    )


def test_authority_locks_canon_false():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"]["canon_promotion"]
        is False
    )


def test_authority_locks_runtime_mutation_false():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"]["runtime_mutation"]
        is False
    )


def test_authority_locks_execution_false():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"]["execution_authority"]
        is False
    )


def test_authority_locks_inference_false():
    assert (
        build_norm_geometry_baseline_promotion_complete()["authority_locks"]["inference_authority"]
        is False
    )


# ── blocked_scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_norm_geometry_baseline_promotion_complete()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False, got {val!r}"


# ── validate: wrong values ─────────────────────────────────────────────────────


def test_validate_wrong_schema_version():
    r = build_norm_geometry_baseline_promotion_complete()
    r["schema_version"] = "WRONG"
    with pytest.raises(NormGeometryBaselinePromotionCompleteError, match="schema_version"):
        validate_norm_geometry_baseline_promotion_complete(r)


def test_validate_wrong_complete_status():
    r = build_norm_geometry_baseline_promotion_complete()
    r["complete_status"] = "WRONG"
    with pytest.raises(NormGeometryBaselinePromotionCompleteError, match="complete_status"):
        validate_norm_geometry_baseline_promotion_complete(r)


def test_validate_wrong_operator_id():
    r = build_norm_geometry_baseline_promotion_complete()
    r["operator_id"] = "WRONG"
    with pytest.raises(NormGeometryBaselinePromotionCompleteError, match="operator_id"):
        validate_norm_geometry_baseline_promotion_complete(r)


def test_validate_wrong_intended_lane():
    r = build_norm_geometry_baseline_promotion_complete()
    r["intended_lane"] = "PRODUCTION"
    with pytest.raises(NormGeometryBaselinePromotionCompleteError, match="intended_lane"):
        validate_norm_geometry_baseline_promotion_complete(r)


def test_validate_wrong_review_hash():
    r = build_norm_geometry_baseline_promotion_complete()
    r["source_promotion_review_hash"] = "a" * 64
    with pytest.raises(
        NormGeometryBaselinePromotionCompleteError, match="source_promotion_review_hash"
    ):
        validate_norm_geometry_baseline_promotion_complete(r)


def test_validate_wrong_pack_hash():
    r = build_norm_geometry_baseline_promotion_complete()
    r["source_baseline_pack_hash"] = "b" * 64
    with pytest.raises(
        NormGeometryBaselinePromotionCompleteError, match="source_baseline_pack_hash"
    ):
        validate_norm_geometry_baseline_promotion_complete(r)


def test_validate_wrong_gate_hash():
    r = build_norm_geometry_baseline_promotion_complete()
    r["source_gate_hash"] = "c" * 64
    with pytest.raises(NormGeometryBaselinePromotionCompleteError, match="source_gate_hash"):
        validate_norm_geometry_baseline_promotion_complete(r)


def test_validate_canonical_hash_mismatch():
    r = build_norm_geometry_baseline_promotion_complete()
    r["canonical_hash"] = "d" * 64
    with pytest.raises(NormGeometryBaselinePromotionCompleteError, match="canonical_hash"):
        validate_norm_geometry_baseline_promotion_complete(r)


def test_validate_authority_lock_emits_true_fails():
    r = build_norm_geometry_baseline_promotion_complete()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["emits_metric_values"] = True
    with pytest.raises(
        NormGeometryBaselinePromotionCompleteError, match="emits_metric_values"
    ):
        validate_norm_geometry_baseline_promotion_complete(r)


def test_validate_advisory_only_false_fails():
    r = build_norm_geometry_baseline_promotion_complete()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["advisory_only"] = False
    with pytest.raises(NormGeometryBaselinePromotionCompleteError, match="advisory_only"):
        validate_norm_geometry_baseline_promotion_complete(r)


def test_validate_complete_only_false_fails():
    r = build_norm_geometry_baseline_promotion_complete()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["baseline_promotion_complete_only"] = False
    with pytest.raises(
        NormGeometryBaselinePromotionCompleteError, match="baseline_promotion_complete_only"
    ):
        validate_norm_geometry_baseline_promotion_complete(r)
