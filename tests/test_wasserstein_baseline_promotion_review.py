"""Tests: WassersteinBaselinePromotionReview.v1."""

from __future__ import annotations

import json
import pathlib

import pytest

from core.wasserstein_baseline_promotion_review import (
    REVIEW_ID,
    REVIEW_STATUS,
    REVIEW_TYPE,
    SCHEMA_VERSION,
    SOURCE_CLOSURE_HASH,
    SOURCE_DECISION_HASH,
    SOURCE_DECISION_ID,
    SOURCE_PACK_VECTOR_UPDATE_HASH,
    WassersteinBaselinePromotionReviewError,
    build_authority_lock_review,
    build_blocked_scope_review,
    build_cpu_baseline_chain_closure_review,
    build_current_pack_state_review,
    build_decision_hash_review,
    build_decision_presence_review,
    build_no_op_parity_review,
    build_promotion_scope_review,
    build_source_pack_vector_update_binding,
    build_target_state_review,
    build_wasserstein_baseline_promotion_review,
    compute_wasserstein_baseline_promotion_review_hash,
    default_authority_locks,
    default_blocked_scopes,
    load_and_verify_decision,
    load_and_verify_operator_closure,
    load_and_verify_pack_vector_update,
    serialize_wasserstein_baseline_promotion_review,
)

_DECISION_PATH = "input/wasserstein_baseline_promotion_operator_decision.json"
_PVU_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_pack_vector_update_001.latest.json"
)
_CLOSURE_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_computation_operator_closure_001.latest.json"
)
_PACK_PATH = (
    "out/metric_operator/metric_operator_baseline_test_vector_pack_001.latest.json"
)


def _load(path: str) -> dict:
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


_DECISION = _load(_DECISION_PATH)
_PVU = _load(_PVU_PATH)
_CLOSURE = _load(_CLOSURE_PATH)
_PACK = _load(_PACK_PATH)


def _payload() -> dict:
    return {
        "review_id": REVIEW_ID,
        "intended_lane": "SHADOW",
        "review_stage": "BASELINE_PROMOTION_REVIEW_ONLY",
        "decision_presence_review": build_decision_presence_review(_DECISION),
        "decision_hash_review": build_decision_hash_review(_DECISION),
        "source_pack_vector_update_binding": build_source_pack_vector_update_binding(_PVU),
        "cpu_baseline_chain_closure_review": build_cpu_baseline_chain_closure_review(_CLOSURE),
        "current_pack_state_review": build_current_pack_state_review(_PACK),
        "target_state_review": build_target_state_review(_PACK, _DECISION),
        "promotion_scope_review": build_promotion_scope_review(),
        "no_op_parity_review": build_no_op_parity_review(_PACK),
        "authority_lock_review": build_authority_lock_review(),
        "blocked_scope_review": build_blocked_scope_review(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE",
        "provenance": {
            "source": "WASSERSTEIN_BASELINE_PROMOTION_REVIEW",
            "evidence_refs": ["unit_test"],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_baseline_promotion_review.v1.schema.json"
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_schema_version() -> None:
    assert SCHEMA_VERSION == "WassersteinBaselinePromotionReview.v1"


def test_review_type() -> None:
    assert REVIEW_TYPE == "WASSERSTEIN_BASELINE_PROMOTION_REVIEW"


def test_review_status_constant() -> None:
    assert REVIEW_STATUS == "WASSERSTEIN_BASELINE_PROMOTION_REVIEW_COMPLETE"


def test_review_id_constant() -> None:
    assert REVIEW_ID == "wasserstein_baseline_promotion_review_001"


def test_source_decision_id() -> None:
    assert SOURCE_DECISION_ID == "WASSERSTEIN_BASELINE_PROMOTION_DECISION_2026_05_30_001"


def test_source_decision_hash() -> None:
    assert SOURCE_DECISION_HASH == (
        "a3f470fe0d1986ddbffddfbe997a25480977c0436f651b7bdbfe2f0d9bfab080"
    )


def test_source_pack_vector_update_hash() -> None:
    assert SOURCE_PACK_VECTOR_UPDATE_HASH == (
        "b18caaea2d2cd7a06f6958350a23de7c4337cf3cd82c34345b6b7519d1b39134"
    )


def test_source_closure_hash() -> None:
    assert SOURCE_CLOSURE_HASH == (
        "36fb4fb48974e3ba9eed93bf76584fae8f543ceeb41d05d3cb48a0a4bdffa7bd"
    )


# ---------------------------------------------------------------------------
# Source file loading
# ---------------------------------------------------------------------------

def test_decision_file_hash_matches() -> None:
    decision = load_and_verify_decision(_DECISION_PATH)
    from core.canonical.json import canonical_hash
    assert canonical_hash(decision) == SOURCE_DECISION_HASH


def test_decision_file_decision_value() -> None:
    assert _DECISION["decision"] == "approve_wasserstein_shadow_stub_baseline_promotion_review"


def test_decision_file_baseline_promotion_review_authorized() -> None:
    assert _DECISION["baseline_promotion_review_authorized"] is True


def test_decision_file_authorized_scope() -> None:
    assert _DECISION["authorized_scope"] == "BASELINE_PROMOTION_REVIEW_ONLY"


def test_pvu_file_hash_matches() -> None:
    pvu = load_and_verify_pack_vector_update(_PVU_PATH)
    assert pvu["canonical_hash"] == SOURCE_PACK_VECTOR_UPDATE_HASH


def test_pvu_file_update_status() -> None:
    assert _PVU["update_status"] == "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE_COMPLETE"


def test_pvu_file_cpu_baseline_phase_closed() -> None:
    assert _PVU["cpu_baseline_phase_record"]["cpu_baseline_computation_phase_status"] == "COMPUTATION_PHASE_CLOSED"


def test_closure_file_hash_matches() -> None:
    closure = load_and_verify_operator_closure(_CLOSURE_PATH)
    assert closure["canonical_hash"] == SOURCE_CLOSURE_HASH


def test_closure_file_status() -> None:
    assert _CLOSURE["closure_status"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"


def test_load_decision_wrong_path_raises() -> None:
    with pytest.raises((FileNotFoundError, OSError)):
        load_and_verify_decision("nonexistent/path.json")


def test_load_pvu_wrong_path_raises() -> None:
    with pytest.raises((FileNotFoundError, OSError)):
        load_and_verify_pack_vector_update("nonexistent/path.json")


def test_load_closure_wrong_path_raises() -> None:
    with pytest.raises((FileNotFoundError, OSError)):
        load_and_verify_operator_closure("nonexistent/path.json")


# ---------------------------------------------------------------------------
# build_decision_presence_review
# ---------------------------------------------------------------------------

def test_decision_presence_review_status() -> None:
    r = build_decision_presence_review(_DECISION)
    assert r["review_status"] == "DECISION_PRESENT_VERIFIED"


def test_decision_presence_review_decision_observed() -> None:
    r = build_decision_presence_review(_DECISION)
    assert r["decision_observed"] == "approve_wasserstein_shadow_stub_baseline_promotion_review"


def test_decision_presence_review_authorized_true() -> None:
    r = build_decision_presence_review(_DECISION)
    assert r["baseline_promotion_review_authorized_observed"] is True


def test_decision_presence_review_scope() -> None:
    r = build_decision_presence_review(_DECISION)
    assert r["authorized_scope_observed"] == "BASELINE_PROMOTION_REVIEW_ONLY"


def test_decision_presence_review_wrong_decision_raises() -> None:
    bad = dict(_DECISION, decision="WRONG_DECISION")
    with pytest.raises(WassersteinBaselinePromotionReviewError, match="decision_value_unexpected"):
        build_decision_presence_review(bad)


def test_decision_presence_review_authorized_false_raises() -> None:
    bad = dict(_DECISION, baseline_promotion_review_authorized=False)
    with pytest.raises(WassersteinBaselinePromotionReviewError, match="baseline_promotion_review_authorized_not_true"):
        build_decision_presence_review(bad)


def test_decision_presence_review_wrong_scope_raises() -> None:
    bad = dict(_DECISION, authorized_scope="WRONG_SCOPE")
    with pytest.raises(WassersteinBaselinePromotionReviewError, match="authorized_scope_unexpected"):
        build_decision_presence_review(bad)


# ---------------------------------------------------------------------------
# build_decision_hash_review
# ---------------------------------------------------------------------------

def test_decision_hash_review_status() -> None:
    r = build_decision_hash_review(_DECISION)
    assert r["review_status"] == "DECISION_HASH_VERIFIED"


def test_decision_hash_review_hashes_match() -> None:
    r = build_decision_hash_review(_DECISION)
    assert r["hashes_match"] is True
    assert r["expected_hash"] == SOURCE_DECISION_HASH
    assert r["observed_hash"] == SOURCE_DECISION_HASH


def test_decision_hash_review_wrong_hash_raises() -> None:
    bad = dict(_DECISION, decision="tampered_value")
    with pytest.raises(WassersteinBaselinePromotionReviewError, match="decision_hash_mismatch"):
        build_decision_hash_review(bad)


# ---------------------------------------------------------------------------
# build_source_pack_vector_update_binding
# ---------------------------------------------------------------------------

def test_source_pvu_binding_status() -> None:
    r = build_source_pack_vector_update_binding(_PVU)
    assert r["review_status"] == "SOURCE_PACK_VECTOR_UPDATE_BOUND"


def test_source_pvu_binding_hashes_match() -> None:
    r = build_source_pack_vector_update_binding(_PVU)
    assert r["hashes_match"] is True
    assert r["observed_hash"] == SOURCE_PACK_VECTOR_UPDATE_HASH


def test_source_pvu_binding_update_status() -> None:
    r = build_source_pack_vector_update_binding(_PVU)
    assert r["update_status_observed"] == "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE_COMPLETE"


def test_source_pvu_binding_phase_status() -> None:
    r = build_source_pack_vector_update_binding(_PVU)
    assert r["cpu_baseline_phase_status_observed"] == "COMPUTATION_PHASE_CLOSED"


def test_source_pvu_binding_wrong_hash_raises() -> None:
    bad = dict(_PVU, canonical_hash="deadbeef")
    with pytest.raises(WassersteinBaselinePromotionReviewError, match="pack_vector_update_hash_mismatch"):
        build_source_pack_vector_update_binding(bad)


def test_source_pvu_binding_wrong_status_raises() -> None:
    bad = dict(_PVU, update_status="WRONG_STATUS")
    with pytest.raises(WassersteinBaselinePromotionReviewError, match="pack_vector_update_status_unexpected"):
        build_source_pack_vector_update_binding(bad)


# ---------------------------------------------------------------------------
# build_cpu_baseline_chain_closure_review
# ---------------------------------------------------------------------------

def test_cpu_baseline_chain_closure_review_status() -> None:
    r = build_cpu_baseline_chain_closure_review(_CLOSURE)
    assert r["review_status"] == "CPU_BASELINE_CHAIN_CLOSURE_CONFIRMED"


def test_cpu_baseline_chain_closure_review_closure_status() -> None:
    r = build_cpu_baseline_chain_closure_review(_CLOSURE)
    assert r["closure_status_observed"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"


def test_cpu_baseline_chain_closure_review_closure_authorized() -> None:
    r = build_cpu_baseline_chain_closure_review(_CLOSURE)
    assert r["closure_authorized_observed"] is True


def test_cpu_baseline_chain_closure_review_baseline_promotion_false() -> None:
    r = build_cpu_baseline_chain_closure_review(_CLOSURE)
    assert r["baseline_promotion_authorized_in_closure"] is False


def test_cpu_baseline_chain_closure_review_wrong_hash_raises() -> None:
    bad = dict(_CLOSURE, canonical_hash="deadbeef")
    with pytest.raises(WassersteinBaselinePromotionReviewError, match="closure_hash_mismatch"):
        build_cpu_baseline_chain_closure_review(bad)


# ---------------------------------------------------------------------------
# build_current_pack_state_review
# ---------------------------------------------------------------------------

def test_current_pack_state_review_status() -> None:
    r = build_current_pack_state_review(_PACK)
    assert r["review_status"] == "CURRENT_PACK_STATE_REVIEWED"


def test_current_pack_state_review_authority_state_advisory_only() -> None:
    r = build_current_pack_state_review(_PACK)
    assert r["expected_authority_state_observed"] == "ADVISORY_ONLY"


def test_current_pack_state_review_vector_type_present() -> None:
    r = build_current_pack_state_review(_PACK)
    assert r["wasserstein_vector_type_observed"] != ""


# ---------------------------------------------------------------------------
# build_target_state_review
# ---------------------------------------------------------------------------

def test_target_state_review_status() -> None:
    r = build_target_state_review(_PACK, _DECISION)
    assert r["review_status"] == "TARGET_STATE_VERIFIED"


def test_target_state_review_target_vector_type() -> None:
    r = build_target_state_review(_PACK, _DECISION)
    assert r["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_target_state_review_target_computation_status() -> None:
    r = build_target_state_review(_PACK, _DECISION)
    assert r["target_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_target_state_review_matches_decision() -> None:
    r = build_target_state_review(_PACK, _DECISION)
    assert r["target_matches_decision"] is True


def test_target_state_review_matches_current_state() -> None:
    r = build_target_state_review(_PACK, _DECISION)
    assert r["target_matches_current_state"] is True


def test_target_state_review_wrong_vector_type_raises() -> None:
    bad = dict(_DECISION, target_vector_type="WRONG_TYPE")
    with pytest.raises(WassersteinBaselinePromotionReviewError, match="target_vector_type_unexpected"):
        build_target_state_review(_PACK, bad)


def test_target_state_review_wrong_computation_status_raises() -> None:
    bad = dict(_DECISION, target_expected_computation_status="WRONG_STATUS")
    with pytest.raises(WassersteinBaselinePromotionReviewError, match="target_expected_computation_status_unexpected"):
        build_target_state_review(_PACK, bad)


# ---------------------------------------------------------------------------
# build_promotion_scope_review
# ---------------------------------------------------------------------------

def test_promotion_scope_review_status() -> None:
    r = build_promotion_scope_review()
    assert r["review_status"] == "PROMOTION_SCOPE_VERIFIED"


def test_promotion_scope_review_authorized_scope() -> None:
    r = build_promotion_scope_review()
    assert r["authorized_scope"] == "BASELINE_PROMOTION_REVIEW_ONLY"


def test_promotion_scope_review_no_modifications() -> None:
    r = build_promotion_scope_review()
    assert r["pack_vector_modified"] is False
    assert r["vector_type_promoted"] is False
    assert r["metric_emission_enabled"] is False
    assert r["forecast_influence_enabled"] is False
    assert r["p43_lanes_opened"] is False
    assert r["runtime_mutated"] is False


# ---------------------------------------------------------------------------
# build_no_op_parity_review
# ---------------------------------------------------------------------------

def test_no_op_parity_review_status() -> None:
    r = build_no_op_parity_review(_PACK)
    assert r["review_status"] == "NO_OP_PARITY_CONFIRMED"


def test_no_op_parity_review_confirmed() -> None:
    r = build_no_op_parity_review(_PACK)
    assert r["no_op_parity_confirmed"] is True


def test_no_op_parity_review_vector_type_unchanged() -> None:
    r = build_no_op_parity_review(_PACK)
    assert r["wasserstein_vector_type_unchanged"] is True


def test_no_op_parity_review_shadow_stub_preserved() -> None:
    r = build_no_op_parity_review(_PACK)
    assert r["shadow_stub_posture_preserved"] is True


def test_no_op_parity_review_advisory_only_preserved() -> None:
    r = build_no_op_parity_review(_PACK)
    assert r["advisory_only_posture_preserved"] is True


def test_no_op_parity_review_pack_id_unchanged() -> None:
    r = build_no_op_parity_review(_PACK)
    assert r["pack_id_unchanged"] is True


# ---------------------------------------------------------------------------
# build_authority_lock_review
# ---------------------------------------------------------------------------

def test_authority_lock_review_status() -> None:
    r = build_authority_lock_review()
    assert r["review_status"] == "AUTHORITY_LOCKS_VERIFIED"


def test_authority_lock_review_all_locks_intact() -> None:
    r = build_authority_lock_review()
    assert r["all_locks_intact"] is True


def test_authority_lock_review_true_locks() -> None:
    r = build_authority_lock_review()
    assert r["advisory_only"] is True
    assert r["shadow_lane_only"] is True
    assert r["baseline_promotion_review_only"] is True
    assert r["baseline_promotion_review_authorized"] is True


def test_authority_lock_review_target_fields() -> None:
    r = build_authority_lock_review()
    assert r["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert r["target_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_authority_lock_review_false_locks() -> None:
    r = build_authority_lock_review()
    assert r["emits_metric_values"] is False
    assert r["forecast_influence"] is False
    assert r["p43_surface_lanes_authorized"] is False
    assert r["production_activation"] is False
    assert r["canon_promotion"] is False
    assert r["runtime_mutation"] is False
    assert r["execution_authority"] is False
    assert r["inference_authority"] is False


# ---------------------------------------------------------------------------
# build_blocked_scope_review
# ---------------------------------------------------------------------------

def test_blocked_scope_review_status() -> None:
    r = build_blocked_scope_review()
    assert r["review_status"] == "BLOCKED_SCOPES_VERIFIED"


def test_blocked_scope_review_all_false() -> None:
    r = build_blocked_scope_review()
    assert r["all_blocked_scopes_false"] is True


def test_blocked_scope_review_scopes_count() -> None:
    r = build_blocked_scope_review()
    assert len(r["scopes_verified"]) == 8


def test_blocked_scope_review_all_verified() -> None:
    r = build_blocked_scope_review()
    for s in r["scopes_verified"]:
        assert s["blocked"] is False
        assert s["review_status"] == "VERIFIED"


# ---------------------------------------------------------------------------
# default_authority_locks / default_blocked_scopes
# ---------------------------------------------------------------------------

def test_default_authority_locks_true_keys() -> None:
    al = default_authority_locks()
    assert al["advisory_only"] is True
    assert al["shadow_lane_only"] is True
    assert al["baseline_promotion_review_only"] is True
    assert al["baseline_promotion_review_authorized"] is True


def test_default_authority_locks_target_fields() -> None:
    al = default_authority_locks()
    assert al["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert al["target_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_default_authority_locks_false_keys() -> None:
    al = default_authority_locks()
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False


def test_default_blocked_scopes_all_false() -> None:
    for scope, value in default_blocked_scopes().items():
        assert value is False, scope


# ---------------------------------------------------------------------------
# build_wasserstein_baseline_promotion_review (end-to-end)
# ---------------------------------------------------------------------------

def test_end_to_end_review_status() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    assert packet["review_status"] == "WASSERSTEIN_BASELINE_PROMOTION_REVIEW_COMPLETE"


def test_end_to_end_schema_version() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    assert packet["schema_version"] == "WassersteinBaselinePromotionReview.v1"


def test_end_to_end_review_type() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    assert packet["review_type"] == "WASSERSTEIN_BASELINE_PROMOTION_REVIEW"


def test_end_to_end_intended_lane() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    assert packet["intended_lane"] == "SHADOW"


def test_end_to_end_source_decision_hash() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    assert packet["source_decision_hash"] == SOURCE_DECISION_HASH


def test_end_to_end_source_pack_vector_update_hash() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    assert packet["source_pack_vector_update_hash"] == SOURCE_PACK_VECTOR_UPDATE_HASH


def test_end_to_end_canonical_hash_present() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    assert "canonical_hash" in packet
    assert len(packet["canonical_hash"]) == 64


def test_end_to_end_canonical_hash_deterministic() -> None:
    p1 = build_wasserstein_baseline_promotion_review(_payload())
    p2 = build_wasserstein_baseline_promotion_review(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_end_to_end_all_sections_present() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    required = [
        "decision_presence_review", "decision_hash_review",
        "source_pack_vector_update_binding", "cpu_baseline_chain_closure_review",
        "current_pack_state_review", "target_state_review",
        "promotion_scope_review", "no_op_parity_review",
        "authority_lock_review", "blocked_scope_review",
    ]
    for section in required:
        assert section in packet, f"missing section: {section}"


def test_end_to_end_no_op_parity_confirmed() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    assert packet["no_op_parity_review"]["no_op_parity_confirmed"] is True


def test_end_to_end_authority_locks_intact() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    al = packet["authority_locks"]
    assert al["advisory_only"] is True
    assert al["baseline_promotion_review_authorized"] is True
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False


def test_end_to_end_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    for scope, value in packet["blocked_scopes"].items():
        assert value is False, scope


def test_end_to_end_recommended_next_step() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    assert packet["recommended_next_step"] == "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE"


# ---------------------------------------------------------------------------
# compute_hash
# ---------------------------------------------------------------------------

def test_compute_hash_excludes_canonical_hash() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    h1 = compute_wasserstein_baseline_promotion_review_hash(packet)
    packet_no_hash = dict(packet)
    packet_no_hash.pop("canonical_hash", None)
    h2 = compute_wasserstein_baseline_promotion_review_hash(packet_no_hash)
    assert h1 == h2


def test_compute_hash_is_64_hex_chars() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    h = compute_wasserstein_baseline_promotion_review_hash(packet)
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# serialize
# ---------------------------------------------------------------------------

def test_serialize_produces_valid_json() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    text = serialize_wasserstein_baseline_promotion_review(packet)
    parsed = json.loads(text)
    assert parsed["schema_version"] == SCHEMA_VERSION


def test_serialize_canonical_hash_survives_roundtrip() -> None:
    packet = build_wasserstein_baseline_promotion_review(_payload())
    text = serialize_wasserstein_baseline_promotion_review(packet)
    parsed = json.loads(text)
    assert parsed["canonical_hash"] == packet["canonical_hash"]
