"""Tests: WassersteinBaselinePromotionComplete.v1."""

from __future__ import annotations

import json
import pathlib

import pytest

from core.wasserstein_baseline_promotion_complete import (
    COMPLETION_ID,
    COMPLETION_STATUS,
    COMPLETION_TYPE,
    SCHEMA_VERSION,
    SOURCE_DECISION_HASH,
    SOURCE_PACK_VECTOR_UPDATE_HASH,
    SOURCE_REVIEW_HASH,
    WassersteinBaselinePromotionCompleteError,
    build_authority_lock_completion,
    build_baseline_state_completion,
    build_blocked_scope_completion,
    build_cpu_baseline_chain_completion,
    build_decision_binding,
    build_no_op_parity_completion,
    build_pack_vector_update_binding,
    build_review_binding,
    build_wasserstein_baseline_promotion_complete,
    compute_wasserstein_baseline_promotion_complete_hash,
    default_authority_locks,
    default_blocked_scopes,
    load_and_verify_decision,
    load_and_verify_pack_vector_update,
    load_and_verify_review,
    serialize_wasserstein_baseline_promotion_complete,
)

_REVIEW_PATH = (
    "out/metric_operator/wasserstein_baseline_promotion_review_001.latest.json"
)
_DECISION_PATH = "input/wasserstein_baseline_promotion_operator_decision.json"
_PVU_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_pack_vector_update_001.latest.json"
)


def _load(path: str) -> dict:
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


_REVIEW = _load(_REVIEW_PATH)
_DECISION = _load(_DECISION_PATH)
_PVU = _load(_PVU_PATH)


def _payload() -> dict:
    return {
        "completion_id": COMPLETION_ID,
        "intended_lane": "SHADOW",
        "completion_stage": "BASELINE_PROMOTION_COMPLETE_ONLY",
        "review_binding": build_review_binding(_REVIEW),
        "decision_binding": build_decision_binding(_DECISION),
        "pack_vector_update_binding": build_pack_vector_update_binding(_PVU),
        "no_op_parity_completion": build_no_op_parity_completion(_REVIEW),
        "baseline_state_completion": build_baseline_state_completion(_REVIEW),
        "cpu_baseline_chain_completion": build_cpu_baseline_chain_completion(_REVIEW),
        "authority_lock_completion": build_authority_lock_completion(),
        "blocked_scope_completion": build_blocked_scope_completion(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_BASELINE_PROMOTION_PHASE_CLOSED",
        "provenance": {
            "source": "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE",
            "evidence_refs": ["unit_test"],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_baseline_promotion_complete.v1.schema.json"
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_schema_version() -> None:
    assert SCHEMA_VERSION == "WassersteinBaselinePromotionComplete.v1"


def test_completion_type() -> None:
    assert COMPLETION_TYPE == "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE"


def test_completion_status_constant() -> None:
    assert COMPLETION_STATUS == "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE"


def test_completion_id_constant() -> None:
    assert COMPLETION_ID == "wasserstein_baseline_promotion_complete_001"


def test_source_review_hash() -> None:
    assert SOURCE_REVIEW_HASH == (
        "a5adc285aa2dc51ba999e5a402aa0126eb0eb2a91e9cbd5f9cb78680ebe9336f"
    )


def test_source_decision_hash() -> None:
    assert SOURCE_DECISION_HASH == (
        "a3f470fe0d1986ddbffddfbe997a25480977c0436f651b7bdbfe2f0d9bfab080"
    )


def test_source_pack_vector_update_hash() -> None:
    assert SOURCE_PACK_VECTOR_UPDATE_HASH == (
        "b18caaea2d2cd7a06f6958350a23de7c4337cf3cd82c34345b6b7519d1b39134"
    )


# ---------------------------------------------------------------------------
# Source file loading
# ---------------------------------------------------------------------------

def test_review_file_hash_matches() -> None:
    review = load_and_verify_review(_REVIEW_PATH)
    assert review["canonical_hash"] == SOURCE_REVIEW_HASH


def test_review_file_status() -> None:
    assert _REVIEW["review_status"] == "WASSERSTEIN_BASELINE_PROMOTION_REVIEW_COMPLETE"


def test_decision_file_hash_matches() -> None:
    from core.canonical.json import canonical_hash
    decision = load_and_verify_decision(_DECISION_PATH)
    assert canonical_hash(decision) == SOURCE_DECISION_HASH


def test_pvu_file_hash_matches() -> None:
    pvu = load_and_verify_pack_vector_update(_PVU_PATH)
    assert pvu["canonical_hash"] == SOURCE_PACK_VECTOR_UPDATE_HASH


def test_load_review_wrong_path_raises() -> None:
    with pytest.raises((FileNotFoundError, OSError)):
        load_and_verify_review("nonexistent/path.json")


def test_load_decision_wrong_path_raises() -> None:
    with pytest.raises((FileNotFoundError, OSError)):
        load_and_verify_decision("nonexistent/path.json")


def test_load_pvu_wrong_path_raises() -> None:
    with pytest.raises((FileNotFoundError, OSError)):
        load_and_verify_pack_vector_update("nonexistent/path.json")


def test_load_review_wrong_hash_raises() -> None:
    import os
    import tempfile

    bad = dict(_REVIEW, canonical_hash="deadbeef")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(bad, f)
        fname = f.name
    try:
        with pytest.raises(WassersteinBaselinePromotionCompleteError, match="review_hash_mismatch"):
            load_and_verify_review(fname)
    finally:
        os.unlink(fname)


# ---------------------------------------------------------------------------
# build_review_binding
# ---------------------------------------------------------------------------

def test_review_binding_status() -> None:
    r = build_review_binding(_REVIEW)
    assert r["binding_status"] == "REVIEW_BOUND"


def test_review_binding_hash_match() -> None:
    r = build_review_binding(_REVIEW)
    assert r["hash_match"] is True
    assert r["review_hash"] == SOURCE_REVIEW_HASH


def test_review_binding_status_observed() -> None:
    r = build_review_binding(_REVIEW)
    assert r["review_status_observed"] == "WASSERSTEIN_BASELINE_PROMOTION_REVIEW_COMPLETE"


def test_review_binding_wrong_hash_raises() -> None:
    bad = dict(_REVIEW, canonical_hash="deadbeef")
    with pytest.raises(WassersteinBaselinePromotionCompleteError, match="review_hash_mismatch"):
        build_review_binding(bad)


def test_review_binding_wrong_status_raises() -> None:
    bad = dict(_REVIEW, review_status="WRONG_STATUS")
    with pytest.raises(WassersteinBaselinePromotionCompleteError, match="review_status_unexpected"):
        build_review_binding(bad)


# ---------------------------------------------------------------------------
# build_decision_binding
# ---------------------------------------------------------------------------

def test_decision_binding_status() -> None:
    r = build_decision_binding(_DECISION)
    assert r["binding_status"] == "DECISION_BOUND"


def test_decision_binding_hash_match() -> None:
    r = build_decision_binding(_DECISION)
    assert r["hash_match"] is True
    assert r["decision_hash"] == SOURCE_DECISION_HASH


def test_decision_binding_decision_observed() -> None:
    r = build_decision_binding(_DECISION)
    assert r["decision_observed"] == "approve_wasserstein_shadow_stub_baseline_promotion_review"


def test_decision_binding_authorized_scope() -> None:
    r = build_decision_binding(_DECISION)
    assert r["authorized_scope_observed"] == "BASELINE_PROMOTION_REVIEW_ONLY"


def test_decision_binding_authorized_true() -> None:
    r = build_decision_binding(_DECISION)
    assert r["baseline_promotion_review_authorized_observed"] is True


def test_decision_binding_wrong_hash_raises() -> None:
    bad = dict(_DECISION, some_field="tampered")
    with pytest.raises(WassersteinBaselinePromotionCompleteError, match="decision_hash_mismatch"):
        build_decision_binding(bad)


def test_decision_binding_wrong_decision_raises() -> None:
    bad = dict(_DECISION, decision="WRONG")
    with pytest.raises(WassersteinBaselinePromotionCompleteError):
        build_decision_binding(bad)


# ---------------------------------------------------------------------------
# build_pack_vector_update_binding
# ---------------------------------------------------------------------------

def test_pvu_binding_status() -> None:
    r = build_pack_vector_update_binding(_PVU)
    assert r["binding_status"] == "PACK_VECTOR_UPDATE_BOUND"


def test_pvu_binding_hash_match() -> None:
    r = build_pack_vector_update_binding(_PVU)
    assert r["hash_match"] is True
    assert r["pack_vector_update_hash"] == SOURCE_PACK_VECTOR_UPDATE_HASH


def test_pvu_binding_update_status() -> None:
    r = build_pack_vector_update_binding(_PVU)
    assert r["update_status_observed"] == "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE_COMPLETE"


def test_pvu_binding_phase_status() -> None:
    r = build_pack_vector_update_binding(_PVU)
    assert r["cpu_baseline_phase_status_observed"] == "COMPUTATION_PHASE_CLOSED"


def test_pvu_binding_wrong_hash_raises() -> None:
    bad = dict(_PVU, canonical_hash="deadbeef")
    with pytest.raises(WassersteinBaselinePromotionCompleteError, match="pack_vector_update_hash_mismatch"):
        build_pack_vector_update_binding(bad)


def test_pvu_binding_wrong_status_raises() -> None:
    bad = dict(_PVU, update_status="WRONG")
    with pytest.raises(WassersteinBaselinePromotionCompleteError, match="pack_vector_update_status_unexpected"):
        build_pack_vector_update_binding(bad)


# ---------------------------------------------------------------------------
# build_no_op_parity_completion
# ---------------------------------------------------------------------------

def test_no_op_parity_completion_status() -> None:
    r = build_no_op_parity_completion(_REVIEW)
    assert r["completion_status"] == "NO_OP_PARITY_COMPLETE"


def test_no_op_parity_completion_confirmed() -> None:
    r = build_no_op_parity_completion(_REVIEW)
    assert r["no_op_parity_confirmed"] is True


def test_no_op_parity_completion_pack_not_modified() -> None:
    r = build_no_op_parity_completion(_REVIEW)
    assert r["pack_vector_modified"] is False


def test_no_op_parity_completion_vector_not_promoted() -> None:
    r = build_no_op_parity_completion(_REVIEW)
    assert r["vector_type_promoted"] is False


def test_no_op_parity_completion_runtime_not_mutated() -> None:
    r = build_no_op_parity_completion(_REVIEW)
    assert r["runtime_mutated"] is False


def test_no_op_parity_completion_shadow_stub_preserved() -> None:
    r = build_no_op_parity_completion(_REVIEW)
    assert r["shadow_stub_posture_preserved"] is True


def test_no_op_parity_completion_advisory_only_preserved() -> None:
    r = build_no_op_parity_completion(_REVIEW)
    assert r["advisory_only_posture_preserved"] is True


def test_no_op_parity_completion_parity_not_confirmed_raises() -> None:
    bad = dict(_REVIEW, no_op_parity_review={"no_op_parity_confirmed": False})
    with pytest.raises(WassersteinBaselinePromotionCompleteError, match="no_op_parity_not_confirmed_in_review"):
        build_no_op_parity_completion(bad)


# ---------------------------------------------------------------------------
# build_baseline_state_completion
# ---------------------------------------------------------------------------

def test_baseline_state_completion_status() -> None:
    r = build_baseline_state_completion(_REVIEW)
    assert r["completion_status"] == "BASELINE_STATE_COMPLETE"


def test_baseline_state_completion_vector_type() -> None:
    r = build_baseline_state_completion(_REVIEW)
    assert r["current_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_baseline_state_completion_computation_status() -> None:
    r = build_baseline_state_completion(_REVIEW)
    assert r["current_computation_status"] == "SHADOW_STUB_ONLY"


def test_baseline_state_completion_authority_state() -> None:
    r = build_baseline_state_completion(_REVIEW)
    assert r["current_authority_state"] == "ADVISORY_ONLY"


def test_baseline_state_completion_phase_complete() -> None:
    r = build_baseline_state_completion(_REVIEW)
    assert r["baseline_promotion_phase_complete"] is True


def test_baseline_state_completion_wrong_vector_type_raises() -> None:
    bad = dict(_REVIEW, current_pack_state_review=dict(
        _REVIEW["current_pack_state_review"],
        wasserstein_vector_type_observed="WRONG"
    ))
    with pytest.raises(WassersteinBaselinePromotionCompleteError, match="current_vector_type_unexpected"):
        build_baseline_state_completion(bad)


# ---------------------------------------------------------------------------
# build_cpu_baseline_chain_completion
# ---------------------------------------------------------------------------

def test_cpu_baseline_chain_completion_status() -> None:
    r = build_cpu_baseline_chain_completion(_REVIEW)
    assert r["completion_status"] == "CPU_BASELINE_CHAIN_COMPLETE"


def test_cpu_baseline_chain_completion_all_true() -> None:
    r = build_cpu_baseline_chain_completion(_REVIEW)
    assert r["cpu_baseline_computation_phase_closed"] is True
    assert r["cpu_baseline_pack_vector_update_complete"] is True
    assert r["cpu_baseline_operator_closure_complete"] is True
    assert r["baseline_promotion_review_complete"] is True


def test_cpu_baseline_chain_completion_wrong_closure_status_raises() -> None:
    bad = dict(_REVIEW, cpu_baseline_chain_closure_review=dict(
        _REVIEW["cpu_baseline_chain_closure_review"],
        closure_status_observed="WRONG"
    ))
    with pytest.raises(WassersteinBaselinePromotionCompleteError, match="cpu_baseline_closure_status_unexpected"):
        build_cpu_baseline_chain_completion(bad)


# ---------------------------------------------------------------------------
# build_authority_lock_completion
# ---------------------------------------------------------------------------

def test_authority_lock_completion_status() -> None:
    r = build_authority_lock_completion()
    assert r["completion_status"] == "AUTHORITY_LOCKS_COMPLETE"


def test_authority_lock_completion_all_intact() -> None:
    r = build_authority_lock_completion()
    assert r["all_locks_intact"] is True


def test_authority_lock_completion_true_locks() -> None:
    r = build_authority_lock_completion()
    assert r["advisory_only"] is True
    assert r["shadow_lane_only"] is True
    assert r["baseline_promotion_complete_only"] is True
    assert r["no_op_parity_confirmed"] is True
    assert r["baseline_promotion_phase_complete"] is True


def test_authority_lock_completion_false_locks() -> None:
    r = build_authority_lock_completion()
    assert r["emits_metric_values"] is False
    assert r["forecast_influence"] is False
    assert r["p43_surface_lanes_authorized"] is False
    assert r["production_activation"] is False
    assert r["canon_promotion"] is False
    assert r["runtime_mutation"] is False
    assert r["execution_authority"] is False
    assert r["inference_authority"] is False


# ---------------------------------------------------------------------------
# build_blocked_scope_completion
# ---------------------------------------------------------------------------

def test_blocked_scope_completion_status() -> None:
    r = build_blocked_scope_completion()
    assert r["completion_status"] == "BLOCKED_SCOPES_COMPLETE"


def test_blocked_scope_completion_all_false() -> None:
    r = build_blocked_scope_completion()
    assert r["all_blocked_scopes_false"] is True


def test_blocked_scope_completion_scopes_count() -> None:
    r = build_blocked_scope_completion()
    assert len(r["scopes_verified"]) == 8


def test_blocked_scope_completion_all_verified() -> None:
    r = build_blocked_scope_completion()
    for s in r["scopes_verified"]:
        assert s["blocked"] is False
        assert s["completion_status"] == "VERIFIED"


# ---------------------------------------------------------------------------
# default_authority_locks / default_blocked_scopes
# ---------------------------------------------------------------------------

def test_default_authority_locks_true_keys() -> None:
    al = default_authority_locks()
    assert al["advisory_only"] is True
    assert al["shadow_lane_only"] is True
    assert al["baseline_promotion_complete_only"] is True
    assert al["no_op_parity_confirmed"] is True
    assert al["baseline_promotion_phase_complete"] is True


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
# build_wasserstein_baseline_promotion_complete (end-to-end)
# ---------------------------------------------------------------------------

def test_end_to_end_completion_status() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["completion_status"] == "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE"


def test_end_to_end_schema_version() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["schema_version"] == "WassersteinBaselinePromotionComplete.v1"


def test_end_to_end_completion_type() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["completion_type"] == "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE"


def test_end_to_end_intended_lane() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["intended_lane"] == "SHADOW"


def test_end_to_end_completion_stage() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["completion_stage"] == "BASELINE_PROMOTION_COMPLETE_ONLY"


def test_end_to_end_source_review_hash() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["source_review_hash"] == SOURCE_REVIEW_HASH


def test_end_to_end_source_decision_hash() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["source_decision_hash"] == SOURCE_DECISION_HASH


def test_end_to_end_source_pack_vector_update_hash() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["source_pack_vector_update_hash"] == SOURCE_PACK_VECTOR_UPDATE_HASH


def test_end_to_end_canonical_hash_present() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert "canonical_hash" in packet
    assert len(packet["canonical_hash"]) == 64


def test_end_to_end_canonical_hash_deterministic() -> None:
    p1 = build_wasserstein_baseline_promotion_complete(_payload())
    p2 = build_wasserstein_baseline_promotion_complete(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_end_to_end_all_sections_present() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    required = [
        "review_binding", "decision_binding", "pack_vector_update_binding",
        "no_op_parity_completion", "baseline_state_completion",
        "cpu_baseline_chain_completion", "authority_lock_completion",
        "blocked_scope_completion",
    ]
    for section in required:
        assert section in packet, f"missing section: {section}"


def test_end_to_end_no_op_parity_confirmed() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["no_op_parity_completion"]["no_op_parity_confirmed"] is True


def test_end_to_end_baseline_promotion_phase_complete() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["baseline_state_completion"]["baseline_promotion_phase_complete"] is True


def test_end_to_end_authority_locks() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    al = packet["authority_locks"]
    assert al["advisory_only"] is True
    assert al["no_op_parity_confirmed"] is True
    assert al["baseline_promotion_phase_complete"] is True
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False


def test_end_to_end_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    for scope, value in packet["blocked_scopes"].items():
        assert value is False, scope


def test_end_to_end_recommended_next_step() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    assert packet["recommended_next_step"] == "WASSERSTEIN_BASELINE_PROMOTION_PHASE_CLOSED"


# ---------------------------------------------------------------------------
# compute_hash
# ---------------------------------------------------------------------------

def test_compute_hash_excludes_canonical_hash() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    h1 = compute_wasserstein_baseline_promotion_complete_hash(packet)
    packet_no_hash = dict(packet)
    packet_no_hash.pop("canonical_hash", None)
    h2 = compute_wasserstein_baseline_promotion_complete_hash(packet_no_hash)
    assert h1 == h2


def test_compute_hash_is_64_hex_chars() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    h = compute_wasserstein_baseline_promotion_complete_hash(packet)
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# serialize
# ---------------------------------------------------------------------------

def test_serialize_produces_valid_json() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    text = serialize_wasserstein_baseline_promotion_complete(packet)
    parsed = json.loads(text)
    assert parsed["schema_version"] == SCHEMA_VERSION


def test_serialize_canonical_hash_survives_roundtrip() -> None:
    packet = build_wasserstein_baseline_promotion_complete(_payload())
    text = serialize_wasserstein_baseline_promotion_complete(packet)
    parsed = json.loads(text)
    assert parsed["canonical_hash"] == packet["canonical_hash"]
