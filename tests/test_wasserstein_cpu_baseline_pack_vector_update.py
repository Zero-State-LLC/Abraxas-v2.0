"""Tests: WassersteinCpuBaselinePackVectorUpdate.v1."""

from __future__ import annotations

import json
import pathlib

import pytest

from core.wasserstein_cpu_baseline_pack_vector_update import (
    BASELINE_PACK_ID,
    SCHEMA_VERSION,
    SOURCE_CLOSURE_HASH,
    SOURCE_CLOSURE_ID,
    UPDATE_ID,
    UPDATE_STATUS,
    UPDATE_TYPE,
    WASSERSTEIN_VECTOR_ID,
    WassersteinCpuBaselinePackVectorUpdateError,
    build_authority_lock_review,
    build_blocked_scope_review,
    build_closure_binding_review,
    build_cpu_baseline_phase_record,
    build_current_pack_vector_review,
    build_non_promotion_guard,
    build_update_scope_review,
    build_wasserstein_cpu_baseline_pack_vector_update,
    compute_wasserstein_cpu_baseline_pack_vector_update_hash,
    default_authority_locks,
    default_blocked_scopes,
    load_and_verify_operator_closure,
    serialize_wasserstein_cpu_baseline_pack_vector_update,
)

_CLOSURE_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_computation_operator_closure_001.latest.json"
)
_PACK_PATH = (
    "out/metric_operator/metric_operator_baseline_test_vector_pack_001.latest.json"
)


def _load_closure() -> dict:
    return json.loads(pathlib.Path(_CLOSURE_PATH).read_text(encoding="utf-8"))


def _load_pack() -> dict:
    return json.loads(pathlib.Path(_PACK_PATH).read_text(encoding="utf-8"))


_CLOSURE = _load_closure()
_PACK = _load_pack()


def _payload() -> dict:
    return {
        "update_id": UPDATE_ID,
        "intended_lane": "SHADOW",
        "update_stage": "PACK_VECTOR_UPDATE_ONLY",
        "closure_binding_review": build_closure_binding_review(_CLOSURE),
        "current_pack_vector_review": build_current_pack_vector_review(_PACK),
        "update_scope_review": build_update_scope_review(),
        "cpu_baseline_phase_record": build_cpu_baseline_phase_record(),
        "non_promotion_guard": build_non_promotion_guard(_CLOSURE, _PACK),
        "authority_lock_review": build_authority_lock_review(),
        "blocked_scope_review": build_blocked_scope_review(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_CPU_BASELINE_CHAIN_CLOSED",
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE",
            "evidence_refs": [
                "WassersteinCpuBaselineComputationOperatorClosure.v1:wasserstein_cpu_baseline_computation_operator_closure_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_cpu_baseline_pack_vector_update.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_schema_version() -> None:
    assert SCHEMA_VERSION == "WassersteinCpuBaselinePackVectorUpdate.v1"


def test_update_type() -> None:
    assert UPDATE_TYPE == "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE"


def test_update_status_constant() -> None:
    assert UPDATE_STATUS == "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE_COMPLETE"


def test_update_id_constant() -> None:
    assert UPDATE_ID == "wasserstein_cpu_baseline_pack_vector_update_001"


def test_source_closure_hash() -> None:
    assert SOURCE_CLOSURE_HASH == (
        "36fb4fb48974e3ba9eed93bf76584fae8f543ceeb41d05d3cb48a0a4bdffa7bd"
    )


def test_source_closure_id() -> None:
    assert SOURCE_CLOSURE_ID == "wasserstein_cpu_baseline_computation_operator_closure_001"


def test_baseline_pack_id_constant() -> None:
    assert BASELINE_PACK_ID == "metric_operator_baseline_test_vector_pack_001"


def test_wasserstein_vector_id_constant() -> None:
    assert WASSERSTEIN_VECTOR_ID == "vector-001-wasserstein"


# ---------------------------------------------------------------------------
# Source file loading
# ---------------------------------------------------------------------------

def test_closure_file_hash_matches_constant() -> None:
    assert _CLOSURE["canonical_hash"] == SOURCE_CLOSURE_HASH


def test_closure_file_status() -> None:
    assert _CLOSURE["closure_status"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"


def test_closure_file_closure_authorized_true() -> None:
    assert _CLOSURE["authority_locks"]["closure_authorized"] is True


def test_closure_file_baseline_promotion_false() -> None:
    assert _CLOSURE["authority_locks"]["baseline_promotion_authorized"] is False


def test_pack_file_loads() -> None:
    assert _PACK["pack_id"] == BASELINE_PACK_ID


def test_pack_file_has_wasserstein_vector() -> None:
    ids = [v["operator_id"] for v in _PACK.get("operator_vectors", [])]
    assert "WASSERSTEIN" in ids


def test_load_and_verify_operator_closure() -> None:
    closure = load_and_verify_operator_closure(_CLOSURE_PATH)
    assert closure["canonical_hash"] == SOURCE_CLOSURE_HASH


def test_load_and_verify_operator_closure_wrong_path_raises() -> None:
    with pytest.raises((FileNotFoundError, OSError)):
        load_and_verify_operator_closure("nonexistent/path.json")


# ---------------------------------------------------------------------------
# build_closure_binding_review
# ---------------------------------------------------------------------------

def test_closure_binding_review_status() -> None:
    r = build_closure_binding_review(_CLOSURE)
    assert r["review_status"] == "CLOSURE_BOUND"


def test_closure_binding_review_hashes_match() -> None:
    r = build_closure_binding_review(_CLOSURE)
    assert r["hashes_match"] is True
    assert r["expected_hash"] == SOURCE_CLOSURE_HASH
    assert r["observed_hash"] == SOURCE_CLOSURE_HASH


def test_closure_binding_review_closure_status_observed() -> None:
    r = build_closure_binding_review(_CLOSURE)
    assert r["closure_status_observed"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"


def test_closure_binding_review_closure_authorized() -> None:
    r = build_closure_binding_review(_CLOSURE)
    assert r["closure_authorized_observed"] is True


def test_closure_binding_review_baseline_promotion_false() -> None:
    r = build_closure_binding_review(_CLOSURE)
    assert r["baseline_promotion_authorized_observed"] is False


def test_closure_binding_review_wrong_hash_raises() -> None:
    bad = dict(_CLOSURE, canonical_hash="deadbeef")
    with pytest.raises(WassersteinCpuBaselinePackVectorUpdateError, match="closure_binding_hash_mismatch"):
        build_closure_binding_review(bad)


def test_closure_binding_review_wrong_status_raises() -> None:
    bad = dict(_CLOSURE, closure_status="WRONG_STATUS")
    with pytest.raises(WassersteinCpuBaselinePackVectorUpdateError, match="closure_status_unexpected"):
        build_closure_binding_review(bad)


def test_closure_binding_review_baseline_promotion_true_raises() -> None:
    bad = dict(_CLOSURE)
    bad["authority_locks"] = dict(_CLOSURE["authority_locks"], baseline_promotion_authorized=True)
    with pytest.raises(WassersteinCpuBaselinePackVectorUpdateError, match="baseline_promotion_authorized_not_false"):
        build_closure_binding_review(bad)


# ---------------------------------------------------------------------------
# build_current_pack_vector_review
# ---------------------------------------------------------------------------

def test_current_pack_vector_review_status() -> None:
    r = build_current_pack_vector_review(_PACK)
    assert r["review_status"] == "CURRENT_PACK_VECTOR_REVIEWED"


def test_current_pack_vector_review_pack_id() -> None:
    r = build_current_pack_vector_review(_PACK)
    assert r["pack_id_observed"] == BASELINE_PACK_ID


def test_current_pack_vector_review_wasserstein_vector_id() -> None:
    r = build_current_pack_vector_review(_PACK)
    assert r["wasserstein_vector_id_observed"] == WASSERSTEIN_VECTOR_ID


def test_current_pack_vector_review_vector_type_present() -> None:
    r = build_current_pack_vector_review(_PACK)
    assert r["vector_type_observed"] != ""


def test_current_pack_vector_review_authority_state_advisory_only() -> None:
    r = build_current_pack_vector_review(_PACK)
    assert r["expected_authority_state_observed"] == "ADVISORY_ONLY"


def test_current_pack_vector_review_vector_type_unchanged() -> None:
    r = build_current_pack_vector_review(_PACK)
    assert r["vector_type_unchanged"] is True


def test_current_pack_vector_review_no_wasserstein_raises() -> None:
    bad = dict(_PACK, operator_vectors=[])
    with pytest.raises(WassersteinCpuBaselinePackVectorUpdateError, match="wasserstein_vector_not_found"):
        build_current_pack_vector_review(bad)


# ---------------------------------------------------------------------------
# build_update_scope_review
# ---------------------------------------------------------------------------

def test_update_scope_review_status() -> None:
    r = build_update_scope_review()
    assert r["review_status"] == "UPDATE_SCOPE_VERIFIED"


def test_update_scope_review_scope() -> None:
    r = build_update_scope_review()
    assert r["update_scope"] == "COMPUTATION_PHASE_CLOSURE_RECORD_ONLY"


def test_update_scope_review_no_modifications() -> None:
    r = build_update_scope_review()
    assert r["vector_type_modified"] is False
    assert r["baseline_promoted"] is False
    assert r["runtime_surfaces_modified"] is False
    assert r["metric_emission_altered"] is False


# ---------------------------------------------------------------------------
# build_cpu_baseline_phase_record
# ---------------------------------------------------------------------------

def test_cpu_baseline_phase_record_status() -> None:
    r = build_cpu_baseline_phase_record()
    assert r["review_status"] == "CPU_BASELINE_PHASE_RECORDED"


def test_cpu_baseline_phase_record_phase_status() -> None:
    r = build_cpu_baseline_phase_record()
    assert r["cpu_baseline_computation_phase_status"] == "COMPUTATION_PHASE_CLOSED"


def test_cpu_baseline_phase_record_source_closure_id() -> None:
    r = build_cpu_baseline_phase_record()
    assert r["source_closure_id"] == SOURCE_CLOSURE_ID


def test_cpu_baseline_phase_record_fixture_counts() -> None:
    r = build_cpu_baseline_phase_record()
    assert r["valid_fixtures_closed"] == 5
    assert r["invalid_fixtures_closed"] == 5
    assert r["nc_fixtures_closed"] == 4


def test_cpu_baseline_phase_record_helper_kernels() -> None:
    r = build_cpu_baseline_phase_record()
    assert r["helper_kernels_scope"] == "TEST_VECTOR_FIXTURE_HELPER_KERNELS_ONLY"


# ---------------------------------------------------------------------------
# build_non_promotion_guard
# ---------------------------------------------------------------------------

def test_non_promotion_guard_status() -> None:
    r = build_non_promotion_guard(_CLOSURE, _PACK)
    assert r["guard_status"] == "NON_PROMOTION_GUARD_PASSED"


def test_non_promotion_guard_baseline_promotion_false() -> None:
    r = build_non_promotion_guard(_CLOSURE, _PACK)
    assert r["baseline_promotion_authorized"] is False


def test_non_promotion_guard_vector_type_unchanged() -> None:
    r = build_non_promotion_guard(_CLOSURE, _PACK)
    assert r["vector_type_unchanged"] is True


def test_non_promotion_guard_pack_id_unchanged() -> None:
    r = build_non_promotion_guard(_CLOSURE, _PACK)
    assert r["pack_id_unchanged"] is True


def test_non_promotion_guard_mutation_blocked() -> None:
    r = build_non_promotion_guard(_CLOSURE, _PACK)
    assert r["runtime_mutation_blocked"] is True
    assert r["metric_emission_blocked"] is True


def test_non_promotion_guard_baseline_promotion_true_raises() -> None:
    bad = dict(_CLOSURE)
    bad["authority_locks"] = dict(_CLOSURE["authority_locks"], baseline_promotion_authorized=True)
    with pytest.raises(WassersteinCpuBaselinePackVectorUpdateError, match="non_promotion_guard"):
        build_non_promotion_guard(bad, _PACK)


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
    assert r["pack_vector_update_only"] is True
    assert r["cpu_baseline_computation_phase_closed"] is True


def test_authority_lock_review_false_locks() -> None:
    r = build_authority_lock_review()
    assert r["baseline_promotion_authorized"] is False
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
    assert al["pack_vector_update_only"] is True
    assert al["cpu_baseline_computation_phase_closed"] is True


def test_default_authority_locks_false_keys() -> None:
    al = default_authority_locks()
    assert al["baseline_promotion_authorized"] is False
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False


def test_default_blocked_scopes_all_false() -> None:
    bs = default_blocked_scopes()
    for scope, value in bs.items():
        assert value is False, scope


# ---------------------------------------------------------------------------
# build_wasserstein_cpu_baseline_pack_vector_update (end-to-end)
# ---------------------------------------------------------------------------

def test_end_to_end_update_status() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    assert packet["update_status"] == "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE_COMPLETE"


def test_end_to_end_schema_version() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    assert packet["schema_version"] == "WassersteinCpuBaselinePackVectorUpdate.v1"


def test_end_to_end_update_type() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    assert packet["update_type"] == "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE"


def test_end_to_end_intended_lane() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    assert packet["intended_lane"] == "SHADOW"


def test_end_to_end_source_closure_hash() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    assert packet["source_closure_hash"] == SOURCE_CLOSURE_HASH


def test_end_to_end_canonical_hash_present() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    assert "canonical_hash" in packet
    assert len(packet["canonical_hash"]) == 64


def test_end_to_end_canonical_hash_deterministic() -> None:
    p1 = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    p2 = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_end_to_end_authority_locks_intact() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    al = packet["authority_locks"]
    assert al["cpu_baseline_computation_phase_closed"] is True
    assert al["baseline_promotion_authorized"] is False
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False


def test_end_to_end_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    for scope, value in packet["blocked_scopes"].items():
        assert value is False, scope


def test_end_to_end_all_sections_present() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    required = [
        "closure_binding_review", "current_pack_vector_review",
        "update_scope_review", "cpu_baseline_phase_record",
        "non_promotion_guard", "authority_lock_review", "blocked_scope_review",
    ]
    for section in required:
        assert section in packet, f"missing section: {section}"


def test_end_to_end_cpu_baseline_phase_closed() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    assert packet["cpu_baseline_phase_record"]["cpu_baseline_computation_phase_status"] == "COMPUTATION_PHASE_CLOSED"


def test_end_to_end_non_promotion_guard_passed() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    assert packet["non_promotion_guard"]["guard_status"] == "NON_PROMOTION_GUARD_PASSED"


def test_end_to_end_recommended_next_step() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    assert packet["recommended_next_step"] == "WASSERSTEIN_CPU_BASELINE_CHAIN_CLOSED"


# ---------------------------------------------------------------------------
# compute_hash
# ---------------------------------------------------------------------------

def test_compute_hash_excludes_canonical_hash() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    h1 = compute_wasserstein_cpu_baseline_pack_vector_update_hash(packet)
    packet_no_hash = dict(packet)
    packet_no_hash.pop("canonical_hash", None)
    h2 = compute_wasserstein_cpu_baseline_pack_vector_update_hash(packet_no_hash)
    assert h1 == h2


def test_compute_hash_is_64_hex_chars() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    h = compute_wasserstein_cpu_baseline_pack_vector_update_hash(packet)
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# serialize
# ---------------------------------------------------------------------------

def test_serialize_produces_valid_json() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    text = serialize_wasserstein_cpu_baseline_pack_vector_update(packet)
    parsed = json.loads(text)
    assert parsed["schema_version"] == SCHEMA_VERSION


def test_serialize_canonical_hash_survives_roundtrip() -> None:
    packet = build_wasserstein_cpu_baseline_pack_vector_update(_payload())
    text = serialize_wasserstein_cpu_baseline_pack_vector_update(packet)
    parsed = json.loads(text)
    assert parsed["canonical_hash"] == packet["canonical_hash"]
