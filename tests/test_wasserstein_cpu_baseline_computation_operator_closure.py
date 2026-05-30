"""Tests: WassersteinCpuBaselineComputationOperatorClosure.v1."""

from __future__ import annotations

import json
import pathlib

import pytest

from core.wasserstein_cpu_baseline_computation_operator_closure import (
    CLOSURE_ID,
    CLOSURE_STATUS,
    CLOSURE_TYPE,
    EXPECTED_INVALID_COUNT,
    EXPECTED_NC_COUNT,
    EXPECTED_VALID_COUNT,
    INVALID_FIXTURE_CLOSURES,
    KERNEL_CLOSURES,
    NC_FIXTURE_CLOSURES,
    SCHEMA_VERSION,
    SOURCE_AUTHORIZATION_DECISION_HASH,
    SOURCE_AUTHORIZATION_DECISION_ID,
    SOURCE_COMPLETE_REVIEW_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    VALID_FIXTURE_CLOSURES,
    WassersteinCpuBaselineComputationOperatorClosureError,
    build_authority_lock_closure,
    build_blocked_scope_closure,
    build_complete_review_binding,
    build_computation_receipt_binding,
    build_decision_hash_review,
    build_decision_presence_review,
    build_helper_kernel_scope_closure,
    build_invalid_fixture_rejection_closure,
    build_not_computable_fixture_rejection_closure,
    build_phase_completion_review,
    build_valid_fixture_result_closure,
    build_wasserstein_cpu_baseline_computation_operator_closure,
    compute_wasserstein_cpu_baseline_computation_operator_closure_hash,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_cpu_baseline_computation_operator_closure,
)

_DECISION_PATH = (
    "input/wasserstein_cpu_baseline_computation_authorization_decision.json"
)
_REVIEW_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_computation_complete_review_001.latest.json"
)
_RECEIPT_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_computation_receipt_001.latest.json"
)


def _load_decision() -> dict:
    return json.loads(pathlib.Path(_DECISION_PATH).read_text(encoding="utf-8"))


def _load_review() -> dict:
    return json.loads(pathlib.Path(_REVIEW_PATH).read_text(encoding="utf-8"))


def _load_receipt() -> dict:
    return json.loads(pathlib.Path(_RECEIPT_PATH).read_text(encoding="utf-8"))


_DECISION = _load_decision()
_REVIEW = _load_review()
_RECEIPT = _load_receipt()


def _payload() -> dict:
    return {
        "closure_id": CLOSURE_ID,
        "intended_lane": "SHADOW",
        "closure_stage": "COMPUTATION_OPERATOR_CLOSURE_ONLY",
        "decision_presence_review": build_decision_presence_review(_DECISION),
        "decision_hash_review": build_decision_hash_review(_DECISION),
        "complete_review_binding": build_complete_review_binding(_REVIEW),
        "computation_receipt_binding": build_computation_receipt_binding(_RECEIPT),
        "phase_completion_review": build_phase_completion_review(_DECISION),
        "valid_fixture_result_closure": build_valid_fixture_result_closure(),
        "invalid_fixture_rejection_closure": build_invalid_fixture_rejection_closure(),
        "not_computable_fixture_rejection_closure": build_not_computable_fixture_rejection_closure(),
        "helper_kernel_scope_closure": build_helper_kernel_scope_closure(),
        "authority_lock_closure": build_authority_lock_closure(),
        "blocked_scope_closure": build_blocked_scope_closure(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE",
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE",
            "evidence_refs": [
                "WassersteinCpuBaselineComputationCompleteReview.v1:wasserstein_cpu_baseline_computation_complete_review_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_cpu_baseline_computation_operator_closure.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_schema_version() -> None:
    assert SCHEMA_VERSION == "WassersteinCpuBaselineComputationOperatorClosure.v1"


def test_closure_type() -> None:
    assert CLOSURE_TYPE == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE"


def test_closure_status_constant() -> None:
    assert CLOSURE_STATUS == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"


def test_closure_id_constant() -> None:
    assert CLOSURE_ID == "wasserstein_cpu_baseline_computation_operator_closure_001"


def test_source_authorization_decision_id() -> None:
    assert SOURCE_AUTHORIZATION_DECISION_ID == (
        "WASSERSTEIN_CPU_BASELINE_COMPUTATION_AUTHORIZATION_DECISION_2026_05_30_001"
    )


def test_source_authorization_decision_hash() -> None:
    assert SOURCE_AUTHORIZATION_DECISION_HASH == (
        "5e717d8da9d1d8e61b2acaef132ac77e6ecec1a79d7e15ba15a79af866a59653"
    )


def test_source_complete_review_hash() -> None:
    assert SOURCE_COMPLETE_REVIEW_HASH == (
        "43524e976b01ce2666820f0d821bb58a0cd8b6b51da925eec60e0d07645bf7a0"
    )


def test_source_computation_receipt_hash() -> None:
    assert SOURCE_COMPUTATION_RECEIPT_HASH == (
        "8c03e94b23efb32b6901117fab1cefdb134ea0ca4bf883b218711d46e57c336c"
    )


def test_expected_counts() -> None:
    assert EXPECTED_VALID_COUNT == 5
    assert EXPECTED_INVALID_COUNT == 5
    assert EXPECTED_NC_COUNT == 4


def test_fixture_closure_list_counts() -> None:
    assert len(VALID_FIXTURE_CLOSURES) == 5
    assert len(INVALID_FIXTURE_CLOSURES) == 5
    assert len(NC_FIXTURE_CLOSURES) == 4


def test_kernel_closures_count() -> None:
    assert len(KERNEL_CLOSURES) == 3


def test_kernel_closures_all_test_vector_helpers() -> None:
    for k in KERNEL_CLOSURES:
        assert k["classification"] == "TEST_VECTOR_FIXTURE_HELPER_KERNEL"
        assert k["runtime_authority_expansion"] is False


# ---------------------------------------------------------------------------
# Source file loading
# ---------------------------------------------------------------------------

def test_decision_file_loads() -> None:
    assert _DECISION["decision_id"] == SOURCE_AUTHORIZATION_DECISION_ID


def test_decision_file_closure_authorized_true() -> None:
    assert _DECISION["closure_authorized"] is True


def test_decision_file_baseline_promotion_false() -> None:
    assert _DECISION["baseline_promotion_authorized"] is False


def test_review_file_hash_matches_constant() -> None:
    assert _REVIEW["canonical_hash"] == SOURCE_COMPLETE_REVIEW_HASH


def test_receipt_file_hash_matches_constant() -> None:
    assert _RECEIPT["canonical_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH


# ---------------------------------------------------------------------------
# build_decision_presence_review
# ---------------------------------------------------------------------------

def test_decision_presence_review_status() -> None:
    r = build_decision_presence_review(_DECISION)
    assert r["closure_status"] == "DECISION_PRESENT_VERIFIED"


def test_decision_presence_review_all_true() -> None:
    r = build_decision_presence_review(_DECISION)
    assert r["decision_file_found"] is True
    assert r["decision_id_present"] is True
    assert r["closure_authorized_present"] is True
    assert r["decision_value_present"] is True


def test_decision_presence_review_missing_decision_id_raises() -> None:
    bad = dict(_DECISION)
    bad.pop("decision_id")
    with pytest.raises(WassersteinCpuBaselineComputationOperatorClosureError, match="decision_id_absent"):
        build_decision_presence_review(bad)


def test_decision_presence_review_missing_closure_authorized_raises() -> None:
    bad = dict(_DECISION)
    bad.pop("closure_authorized")
    with pytest.raises(WassersteinCpuBaselineComputationOperatorClosureError, match="closure_authorized_absent"):
        build_decision_presence_review(bad)


# ---------------------------------------------------------------------------
# build_decision_hash_review
# ---------------------------------------------------------------------------

def test_decision_hash_review_status() -> None:
    r = build_decision_hash_review(_DECISION)
    assert r["closure_status"] == "DECISION_HASH_VERIFIED"


def test_decision_hash_review_hashes_match() -> None:
    r = build_decision_hash_review(_DECISION)
    assert r["hashes_match"] is True
    assert r["expected_hash"] == SOURCE_AUTHORIZATION_DECISION_HASH
    assert r["observed_hash"] == SOURCE_AUTHORIZATION_DECISION_HASH


def test_decision_hash_review_wrong_content_raises() -> None:
    bad = dict(_DECISION, decision_id="TAMPERED")
    with pytest.raises(WassersteinCpuBaselineComputationOperatorClosureError, match="decision_hash_mismatch"):
        build_decision_hash_review(bad)


# ---------------------------------------------------------------------------
# build_complete_review_binding
# ---------------------------------------------------------------------------

def test_complete_review_binding_status() -> None:
    r = build_complete_review_binding(_REVIEW)
    assert r["closure_status"] == "COMPLETE_REVIEW_BOUND"


def test_complete_review_binding_hashes_match() -> None:
    r = build_complete_review_binding(_REVIEW)
    assert r["hashes_match"] is True
    assert r["expected_hash"] == SOURCE_COMPLETE_REVIEW_HASH


def test_complete_review_binding_review_status_present() -> None:
    r = build_complete_review_binding(_REVIEW)
    assert r["review_status_observed"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE_REVIEW_READY"


def test_complete_review_binding_wrong_hash_raises() -> None:
    bad = dict(_REVIEW, canonical_hash="deadbeef")
    with pytest.raises(WassersteinCpuBaselineComputationOperatorClosureError, match="complete_review_binding_hash_mismatch"):
        build_complete_review_binding(bad)


# ---------------------------------------------------------------------------
# build_computation_receipt_binding
# ---------------------------------------------------------------------------

def test_computation_receipt_binding_status() -> None:
    r = build_computation_receipt_binding(_RECEIPT)
    assert r["closure_status"] == "COMPUTATION_RECEIPT_BOUND"


def test_computation_receipt_binding_hashes_match() -> None:
    r = build_computation_receipt_binding(_RECEIPT)
    assert r["hashes_match"] is True
    assert r["expected_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH


def test_computation_receipt_binding_computation_status_present() -> None:
    r = build_computation_receipt_binding(_RECEIPT)
    assert r["computation_status_observed"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE"


def test_computation_receipt_binding_wrong_hash_raises() -> None:
    bad = dict(_RECEIPT, canonical_hash="deadbeef")
    with pytest.raises(WassersteinCpuBaselineComputationOperatorClosureError, match="computation_receipt_binding_hash_mismatch"):
        build_computation_receipt_binding(bad)


# ---------------------------------------------------------------------------
# build_phase_completion_review
# ---------------------------------------------------------------------------

def test_phase_completion_review_status() -> None:
    r = build_phase_completion_review(_DECISION)
    assert r["closure_status"] == "PHASE_COMPLETION_VERIFIED"


def test_phase_completion_review_closure_authorized() -> None:
    r = build_phase_completion_review(_DECISION)
    assert r["closure_authorized"] is True


def test_phase_completion_review_baseline_promotion_false() -> None:
    r = build_phase_completion_review(_DECISION)
    assert r["baseline_promotion_authorized"] is False


def test_phase_completion_review_authorized_scope() -> None:
    r = build_phase_completion_review(_DECISION)
    assert r["authorized_scope"] == "COMPUTATION_PHASE_CLOSURE_ONLY"


def test_phase_completion_review_decision_value() -> None:
    r = build_phase_completion_review(_DECISION)
    assert r["decision_value"] == "approve_wasserstein_cpu_baseline_computation_phase_closure"


def test_phase_completion_review_all_fixtures_closed() -> None:
    r = build_phase_completion_review(_DECISION)
    assert r["all_fixtures_closed"] is True


def test_phase_completion_review_closure_not_authorized_raises() -> None:
    bad = dict(_DECISION, closure_authorized=False)
    with pytest.raises(WassersteinCpuBaselineComputationOperatorClosureError, match="closure_authorized_not_true"):
        build_phase_completion_review(bad)


def test_phase_completion_review_baseline_promotion_true_raises() -> None:
    bad = dict(_DECISION, baseline_promotion_authorized=True)
    with pytest.raises(WassersteinCpuBaselineComputationOperatorClosureError, match="baseline_promotion_authorized_not_false"):
        build_phase_completion_review(bad)


def test_phase_completion_review_wrong_scope_raises() -> None:
    bad = dict(_DECISION, authorized_scope="FULL_BASELINE_PROMOTION")
    with pytest.raises(WassersteinCpuBaselineComputationOperatorClosureError, match="authorized_scope_mismatch"):
        build_phase_completion_review(bad)


# ---------------------------------------------------------------------------
# build_valid_fixture_result_closure
# ---------------------------------------------------------------------------

def test_valid_fixture_result_closure_status() -> None:
    r = build_valid_fixture_result_closure()
    assert r["closure_status"] == "VALID_FIXTURES_CLOSED"


def test_valid_fixture_result_closure_total() -> None:
    r = build_valid_fixture_result_closure()
    assert r["total_closed"] == 5


def test_valid_fixture_result_closure_all_matched() -> None:
    r = build_valid_fixture_result_closure()
    assert r["all_matched"] is True


def test_valid_fixture_result_closure_no_metric_values() -> None:
    r = build_valid_fixture_result_closure()
    assert r["no_metric_values_emitted"] is True


def test_valid_fixture_result_closure_fixture_count() -> None:
    r = build_valid_fixture_result_closure()
    assert len(r["fixture_closures"]) == 5


def test_valid_fixture_result_closure_all_closed() -> None:
    r = build_valid_fixture_result_closure()
    for fc in r["fixture_closures"]:
        assert fc["closure_status"] == "CLOSED"
        assert fc["outcome"] == "MATCHED"
        assert fc["metric_value_emitted"] is False


# ---------------------------------------------------------------------------
# build_invalid_fixture_rejection_closure
# ---------------------------------------------------------------------------

def test_invalid_fixture_rejection_closure_status() -> None:
    r = build_invalid_fixture_rejection_closure()
    assert r["closure_status"] == "INVALID_FIXTURES_CLOSED"


def test_invalid_fixture_rejection_closure_total() -> None:
    r = build_invalid_fixture_rejection_closure()
    assert r["total_closed"] == 5


def test_invalid_fixture_rejection_closure_all_invalid_input() -> None:
    r = build_invalid_fixture_rejection_closure()
    assert r["all_invalid_input_status"] is True
    assert r["all_computation_not_attempted"] is True


def test_invalid_fixture_rejection_closure_fixture_count() -> None:
    r = build_invalid_fixture_rejection_closure()
    assert len(r["fixture_closures"]) == 5


def test_invalid_fixture_rejection_closure_all_closed() -> None:
    r = build_invalid_fixture_rejection_closure()
    for fc in r["fixture_closures"]:
        assert fc["closure_status"] == "CLOSED"
        assert fc["outcome"] == "INVALID_INPUT"
        assert fc["computation_attempted"] is False
        assert fc["metric_value_emitted"] is False


# ---------------------------------------------------------------------------
# build_not_computable_fixture_rejection_closure
# ---------------------------------------------------------------------------

def test_nc_fixture_rejection_closure_status() -> None:
    r = build_not_computable_fixture_rejection_closure()
    assert r["closure_status"] == "NOT_COMPUTABLE_FIXTURES_CLOSED"


def test_nc_fixture_rejection_closure_total() -> None:
    r = build_not_computable_fixture_rejection_closure()
    assert r["total_closed"] == 4


def test_nc_fixture_rejection_closure_all_not_computable() -> None:
    r = build_not_computable_fixture_rejection_closure()
    assert r["all_not_computable_status"] is True
    assert r["all_computation_not_attempted"] is True


def test_nc_fixture_rejection_closure_fixture_count() -> None:
    r = build_not_computable_fixture_rejection_closure()
    assert len(r["fixture_closures"]) == 4


def test_nc_fixture_rejection_closure_all_closed() -> None:
    r = build_not_computable_fixture_rejection_closure()
    for fc in r["fixture_closures"]:
        assert fc["closure_status"] == "CLOSED"
        assert fc["outcome"] == "NOT_COMPUTABLE"
        assert fc["computation_attempted"] is False
        assert fc["metric_value_emitted"] is False


# ---------------------------------------------------------------------------
# build_helper_kernel_scope_closure
# ---------------------------------------------------------------------------

def test_helper_kernel_scope_closure_status() -> None:
    r = build_helper_kernel_scope_closure()
    assert r["closure_status"] == "HELPER_KERNELS_CLOSED_TEST_VECTOR_FIXTURE_HELPERS_ONLY"


def test_helper_kernel_scope_closure_all_helpers_only() -> None:
    r = build_helper_kernel_scope_closure()
    assert r["all_test_vector_fixture_helpers_only"] is True


def test_helper_kernel_scope_closure_no_runtime_expansion() -> None:
    r = build_helper_kernel_scope_closure()
    assert r["no_runtime_authority_expansion"] is True


def test_helper_kernel_scope_closure_kernel_count() -> None:
    r = build_helper_kernel_scope_closure()
    assert len(r["kernels_closed"]) == 3


def test_helper_kernel_scope_closure_kernel_names() -> None:
    r = build_helper_kernel_scope_closure()
    names = {k["kernel_name"] for k in r["kernels_closed"]}
    assert names == {"_w1_sorted_cdf", "_euclidean_distance", "_greedy_min_cost_transport"}


def test_helper_kernel_scope_closure_all_closed() -> None:
    r = build_helper_kernel_scope_closure()
    for k in r["kernels_closed"]:
        assert k["closure_status"] == "CLOSED"
        assert k["runtime_authority_expansion"] is False


# ---------------------------------------------------------------------------
# build_authority_lock_closure
# ---------------------------------------------------------------------------

def test_authority_lock_closure_status() -> None:
    r = build_authority_lock_closure()
    assert r["closure_status"] == "AUTHORITY_LOCKS_CLOSED"


def test_authority_lock_closure_all_locks_intact() -> None:
    r = build_authority_lock_closure()
    assert r["all_locks_intact"] is True


def test_authority_lock_closure_true_locks() -> None:
    r = build_authority_lock_closure()
    assert r["advisory_only"] is True
    assert r["shadow_lane_only"] is True
    assert r["computation_operator_closure_only"] is True
    assert r["test_vector_computation_only"] is True
    assert r["wasserstein_cpu_baseline_implementation_authorized"] is True
    assert r["closure_authorized"] is True


def test_authority_lock_closure_false_locks() -> None:
    r = build_authority_lock_closure()
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
# build_blocked_scope_closure
# ---------------------------------------------------------------------------

def test_blocked_scope_closure_status() -> None:
    r = build_blocked_scope_closure()
    assert r["closure_status"] == "BLOCKED_SCOPES_CLOSED"


def test_blocked_scope_closure_all_false() -> None:
    r = build_blocked_scope_closure()
    assert r["all_blocked_scopes_false"] is True


def test_blocked_scope_closure_scopes_count() -> None:
    r = build_blocked_scope_closure()
    assert len(r["scopes_verified"]) == 8


def test_blocked_scope_closure_all_scopes_closed() -> None:
    r = build_blocked_scope_closure()
    for s in r["scopes_verified"]:
        assert s["closure_status"] == "CLOSED"
        assert s["blocked"] is False


# ---------------------------------------------------------------------------
# default_authority_locks / default_blocked_scopes
# ---------------------------------------------------------------------------

def test_default_authority_locks_true_keys() -> None:
    al = default_authority_locks()
    assert al["advisory_only"] is True
    assert al["shadow_lane_only"] is True
    assert al["computation_operator_closure_only"] is True
    assert al["test_vector_computation_only"] is True
    assert al["wasserstein_cpu_baseline_implementation_authorized"] is True
    assert al["closure_authorized"] is True


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
# build_wasserstein_cpu_baseline_computation_operator_closure (end-to-end)
# ---------------------------------------------------------------------------

def test_end_to_end_closure_status() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    assert packet["closure_status"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"


def test_end_to_end_schema_version() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    assert packet["schema_version"] == "WassersteinCpuBaselineComputationOperatorClosure.v1"


def test_end_to_end_closure_type() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    assert packet["closure_type"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE"


def test_end_to_end_intended_lane() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    assert packet["intended_lane"] == "SHADOW"


def test_end_to_end_source_hashes() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    assert packet["source_authorization_decision_hash"] == SOURCE_AUTHORIZATION_DECISION_HASH
    assert packet["source_complete_review_hash"] == SOURCE_COMPLETE_REVIEW_HASH
    assert packet["source_computation_receipt_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH


def test_end_to_end_canonical_hash_present() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    assert "canonical_hash" in packet
    assert len(packet["canonical_hash"]) == 64


def test_end_to_end_canonical_hash_deterministic() -> None:
    p1 = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    p2 = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_end_to_end_authority_locks_intact() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    al = packet["authority_locks"]
    assert al["closure_authorized"] is True
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
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    for scope, value in packet["blocked_scopes"].items():
        assert value is False, scope


def test_end_to_end_all_closure_sections_present() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    required = [
        "decision_presence_review", "decision_hash_review",
        "complete_review_binding", "computation_receipt_binding",
        "phase_completion_review", "valid_fixture_result_closure",
        "invalid_fixture_rejection_closure", "not_computable_fixture_rejection_closure",
        "helper_kernel_scope_closure", "authority_lock_closure", "blocked_scope_closure",
    ]
    for section in required:
        assert section in packet, f"missing section: {section}"


def test_end_to_end_recommended_next_step() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    assert packet["recommended_next_step"] == "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE"


# ---------------------------------------------------------------------------
# compute_hash
# ---------------------------------------------------------------------------

def test_compute_hash_excludes_canonical_hash() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    h1 = compute_wasserstein_cpu_baseline_computation_operator_closure_hash(packet)
    packet_no_hash = dict(packet)
    packet_no_hash.pop("canonical_hash", None)
    h2 = compute_wasserstein_cpu_baseline_computation_operator_closure_hash(packet_no_hash)
    assert h1 == h2


def test_compute_hash_is_64_hex_chars() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    h = compute_wasserstein_cpu_baseline_computation_operator_closure_hash(packet)
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# serialize
# ---------------------------------------------------------------------------

def test_serialize_produces_valid_json() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    text = serialize_wasserstein_cpu_baseline_computation_operator_closure(packet)
    parsed = json.loads(text)
    assert parsed["schema_version"] == SCHEMA_VERSION


def test_serialize_canonical_hash_survives_roundtrip() -> None:
    packet = build_wasserstein_cpu_baseline_computation_operator_closure(_payload())
    text = serialize_wasserstein_cpu_baseline_computation_operator_closure(packet)
    parsed = json.loads(text)
    assert parsed["canonical_hash"] == packet["canonical_hash"]
