"""Tests for WassersteinCpuBaselineComputationReceipt.v1."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from core.wasserstein_cpu_baseline_computation import (
    COMPUTATION_STATUS,
    EPSILON_ABS,
    EPSILON_REL,
    FIXTURE_COMPARISON_ABS_TOL,
    FLOAT64_DECLARATION,
    FIXTURE_DIR,
    INTENDED_LANE,
    MAX_COORDINATE_MAGNITUDE,
    MAX_DISTRIBUTION_LENGTH,
    NOT_COMPUTABLE_BRANCHES,
    OPERATOR_ID,
    RECEIPT_ID,
    RECEIPT_TYPE,
    SCHEMA_VERSION,
    SOLVER_POLICY,
    SOURCE_GATE_HASH,
    WassersteinCpuBaselineComputationError,
    _dispatch_invalid,
    _dispatch_nc,
    _dispatch_valid,
    _euclidean_distance,
    _greedy_min_cost_transport,
    _w1_sorted_cdf,
    build_authority_locks,
    build_blocked_scopes,
    build_comparison_summary,
    build_solver_policy_summary,
    build_wasserstein_cpu_baseline_computation_receipt,
    run_computation,
    serialize_wasserstein_cpu_baseline_computation_receipt,
    validate_wasserstein_cpu_baseline_computation_receipt,
)
from core.canonical.json import canonical_hash


# ── constant invariants ────────────────────────────────────────────────────────


def test_schema_version() -> None:
    assert SCHEMA_VERSION == "WassersteinCpuBaselineComputationReceipt.v1"


def test_receipt_type() -> None:
    assert RECEIPT_TYPE == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_RECEIPT"


def test_operator_id() -> None:
    assert OPERATOR_ID == "WASSERSTEIN"


def test_computation_status() -> None:
    assert COMPUTATION_STATUS == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE"


def test_intended_lane() -> None:
    assert INTENDED_LANE == "SHADOW"


def test_solver_policy() -> None:
    assert SOLVER_POLICY == "DETERMINISTIC_1D_SORTED_CDF_TRANSPORT_ONLY"


def test_float64_declaration() -> None:
    assert FLOAT64_DECLARATION == "IEEE_754_BINARY64_REQUIRED"


def test_epsilon_rel() -> None:
    assert EPSILON_REL == 1e-9


def test_epsilon_abs() -> None:
    assert EPSILON_ABS == 1e-12


def test_max_distribution_length() -> None:
    assert MAX_DISTRIBUTION_LENGTH == 16


def test_max_coordinate_magnitude() -> None:
    assert MAX_COORDINATE_MAGNITUDE == 1_000_000.0


def test_not_computable_branches_count() -> None:
    assert len(NOT_COMPUTABLE_BRANCHES) == 7


def test_not_computable_branches_content() -> None:
    expected = {
        "EMPTY_DISTRIBUTION",
        "UNBALANCED_MASS",
        "NEGATIVE_MASS",
        "NON_FINITE_WEIGHT",
        "NON_FINITE_COORDINATE",
        "MISSING_REQUIRED_FIELD",
        "MISMATCHED_SUPPORT_WEIGHT_LENGTH",
    }
    assert NOT_COMPUTABLE_BRANCHES == expected


def test_source_gate_hash_length() -> None:
    assert isinstance(SOURCE_GATE_HASH, str)
    assert len(SOURCE_GATE_HASH) == 64


def test_receipt_id() -> None:
    assert RECEIPT_ID == "wasserstein_cpu_baseline_computation_receipt_001"


# ── solver kernels ─────────────────────────────────────────────────────────────


def test_w1_sorted_cdf_valid001() -> None:
    """valid-001: p=[0.2,0.5,0.3] q=[0.4,0.1,0.5] support=[0,1,2] → 0.4"""
    result = _w1_sorted_cdf([0.2, 0.5, 0.3], [0.4, 0.1, 0.5], [0.0, 1.0, 2.0])
    assert abs(result - 0.4) < FIXTURE_COMPARISON_ABS_TOL


def test_w1_sorted_cdf_degenerate() -> None:
    """valid-005: identical mass on single support → 0.0"""
    result = _w1_sorted_cdf([1.0], [1.0], [0.0])
    assert result == 0.0


def test_euclidean_distance_valid003() -> None:
    """valid-003: sqrt(0.25+0.25+0.25) = sqrt(0.75) ≈ 0.866025"""
    result = _euclidean_distance([1.0, 2.0, 3.0], [1.5, 2.5, 3.5])
    assert abs(result - math.sqrt(0.75)) < 1e-12


def test_greedy_transport_valid004() -> None:
    """valid-004: 3×3 cost matrix → expected 0.2"""
    cost = [[0.0, 1.0, 2.0], [1.0, 0.0, 1.0], [2.0, 1.0, 0.0]]
    result = _greedy_min_cost_transport([0.3, 0.4, 0.3], [0.5, 0.2, 0.3], cost)
    assert abs(result - 0.2) < FIXTURE_COMPARISON_ABS_TOL


def test_w1_histogram_valid002() -> None:
    """valid-002: weighted histogram, edges=[0,1,2,3], midpoints=[0.5,1.5,2.5] → 0.4"""
    edges = [0.0, 1.0, 2.0, 3.0]
    midpoints = [(edges[k] + edges[k + 1]) / 2.0 for k in range(len(edges) - 1)]
    result = _w1_sorted_cdf([0.1, 0.6, 0.3], [0.4, 0.4, 0.2], midpoints)
    assert abs(result - 0.4) < FIXTURE_COMPARISON_ABS_TOL


# ── fixture dispatch ───────────────────────────────────────────────────────────


def test_dispatch_valid_distribution_pair() -> None:
    f = {
        "fixture_id": "valid-001",
        "fixture_group": "DISTRIBUTION_PAIR_SCHEMA",
        "fixture_type": "VALID",
        "expected_wasserstein_distance": 0.4,
        "input": {"p": [0.2, 0.5, 0.3], "q": [0.4, 0.1, 0.5], "support": [0, 1, 2]},
    }
    r = _dispatch_valid(f)
    assert r["computation_status"] == "SHADOW_COMPUTATION_COMPLETE"
    assert r["computation_attempted"] is True
    assert r["distance_matched"] is True
    assert r["metric_value_emitted"] is False
    assert r["emits_metric_values"] is False
    assert r["shadow_lane"] == "SHADOW"
    assert abs(r["shadow_transport_value"] - 0.4) < FIXTURE_COMPARISON_ABS_TOL


def test_dispatch_valid_reference_vector() -> None:
    f = {
        "fixture_id": "valid-003",
        "fixture_group": "REFERENCE_VECTOR_SCHEMA",
        "fixture_type": "VALID",
        "expected_wasserstein_distance": 0.866025,
        "input": {
            "reference_vector": [1.0, 2.0, 3.0],
            "query_vector": [1.5, 2.5, 3.5],
            "declared_ground_metric": "euclidean",
            "dimensionality": 3,
        },
    }
    r = _dispatch_valid(f)
    assert r["distance_matched"] is True
    assert abs(r["shadow_transport_value"] - math.sqrt(0.75)) < 1e-12


def test_dispatch_valid_degenerate() -> None:
    f = {
        "fixture_id": "valid-005",
        "fixture_group": "DEGENERATE_DISTRIBUTION_SCHEMA",
        "fixture_type": "VALID",
        "expected_wasserstein_distance": 0.0,
        "input": {"p": [1.0], "q": [1.0], "support": [0]},
    }
    r = _dispatch_valid(f)
    assert r["distance_matched"] is True
    assert r["shadow_transport_value"] == 0.0


def test_dispatch_invalid() -> None:
    f = {
        "fixture_id": "invalid-001",
        "fixture_group": "MISSING_REQUIRED_FIELD",
        "fixture_type": "INVALID",
        "rejection_reason": "missing_required_field: q absent from input",
        "input": {},
    }
    r = _dispatch_invalid(f)
    assert r["computation_status"] == "INVALID_INPUT"
    assert r["computation_attempted"] is False
    assert r["metric_value_emitted"] is False
    assert r["emits_metric_values"] is False


def test_dispatch_nc() -> None:
    f = {
        "fixture_id": "nc-001",
        "fixture_group": "EMPTY_INPUT",
        "fixture_type": "NOT_COMPUTABLE",
        "rejection_reason": "not_computable: empty_input",
        "input": {},
    }
    r = _dispatch_nc(f)
    assert r["computation_status"] == "NOT_COMPUTABLE"
    assert r["computation_attempted"] is False
    assert r["metric_value_emitted"] is False
    assert r["emits_metric_values"] is False


def test_dispatch_valid_unknown_group_raises() -> None:
    f = {
        "fixture_id": "x-001",
        "fixture_group": "UNKNOWN_GROUP",
        "fixture_type": "VALID",
        "expected_wasserstein_distance": 0.0,
        "input": {},
    }
    with pytest.raises(WassersteinCpuBaselineComputationError):
        _dispatch_valid(f)


# ── fixture files exist on disk ───────────────────────────────────────────────


def test_fixture_dir_valid_exists() -> None:
    assert (FIXTURE_DIR / "valid").is_dir()


def test_fixture_dir_invalid_exists() -> None:
    assert (FIXTURE_DIR / "invalid").is_dir()


def test_fixture_dir_nc_exists() -> None:
    assert (FIXTURE_DIR / "not_computable").is_dir()


def test_valid_fixture_count() -> None:
    files = sorted((FIXTURE_DIR / "valid").glob("*.json"))
    assert len(files) == 5


def test_invalid_fixture_count() -> None:
    files = sorted((FIXTURE_DIR / "invalid").glob("*.json"))
    assert len(files) == 5


def test_nc_fixture_count() -> None:
    files = sorted((FIXTURE_DIR / "not_computable").glob("*.json"))
    assert len(files) == 4


# ── comparison summary ─────────────────────────────────────────────────────────

_VALID_R = [
    {"computation_status": "SHADOW_COMPUTATION_COMPLETE", "distance_matched": True},
    {"computation_status": "SHADOW_COMPUTATION_COMPLETE", "distance_matched": True},
    {"computation_status": "SHADOW_COMPUTATION_COMPLETE", "distance_matched": True},
    {"computation_status": "SHADOW_COMPUTATION_COMPLETE", "distance_matched": True},
    {"computation_status": "SHADOW_COMPUTATION_COMPLETE", "distance_matched": True},
]
_INVALID_R = [
    {"computation_status": "INVALID_INPUT"},
    {"computation_status": "INVALID_INPUT"},
    {"computation_status": "INVALID_INPUT"},
    {"computation_status": "INVALID_INPUT"},
    {"computation_status": "INVALID_INPUT"},
]
_NC_R = [
    {"computation_status": "NOT_COMPUTABLE"},
    {"computation_status": "NOT_COMPUTABLE"},
    {"computation_status": "NOT_COMPUTABLE"},
    {"computation_status": "NOT_COMPUTABLE"},
]


def test_comparison_summary_all_matched() -> None:
    cs = build_comparison_summary(_VALID_R, _INVALID_R, _NC_R)
    assert cs["all_matched"] is True
    assert cs["valid_matched"] == 5
    assert cs["invalid_routed_as_invalid_input"] == 5
    assert cs["nc_routed_as_not_computable"] == 4


def test_comparison_summary_not_all_matched_if_distance_fail() -> None:
    bad_valid = copy.deepcopy(_VALID_R)
    bad_valid[0]["distance_matched"] = False
    cs = build_comparison_summary(bad_valid, _INVALID_R, _NC_R)
    assert cs["all_matched"] is False


# ── solver_policy_summary ─────────────────────────────────────────────────────


def test_solver_policy_summary_fields() -> None:
    sps = build_solver_policy_summary()
    assert sps["solver_policy"] == SOLVER_POLICY
    assert sps["float64_precision_declaration"] == FLOAT64_DECLARATION
    assert sps["epsilon_rel"] == EPSILON_REL
    assert sps["epsilon_abs"] == EPSILON_ABS
    assert sps["max_distribution_length"] == MAX_DISTRIBUTION_LENGTH
    assert sps["max_coordinate_magnitude"] == MAX_COORDINATE_MAGNITUDE
    assert sps["deterministic"] is True
    assert sps["shadow_only"] is True
    assert sps["no_external_solver"] is True


# ── authority locks & blocked scopes ─────────────────────────────────────────


def test_authority_locks_structure() -> None:
    al = build_authority_locks()
    assert al["wasserstein_cpu_baseline_computation_authorized"] is True
    assert al["shadow_lane_only"] is True
    assert al["test_vector_computation_only"] is True
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False


def test_blocked_scopes_all_false() -> None:
    bs = build_blocked_scopes()
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        assert bs[flag] is False, f"blocked_scopes.{flag} must be False"


# ── full end-to-end receipt build from disk fixtures ─────────────────────────


def _load_dir(directory: Path) -> list[dict]:
    return [
        json.loads(f.read_text(encoding="utf-8"))
        for f in sorted(directory.glob("*.json"))
    ]


def _build_full_packet() -> dict:
    valid_fixtures = _load_dir(FIXTURE_DIR / "valid")
    invalid_fixtures = _load_dir(FIXTURE_DIR / "invalid")
    nc_fixtures = _load_dir(FIXTURE_DIR / "not_computable")
    valid_results, invalid_results, nc_results = run_computation(
        valid_fixtures, invalid_fixtures, nc_fixtures
    )
    comparison_summary = build_comparison_summary(valid_results, invalid_results, nc_results)
    payload = {
        "valid_fixture_results": valid_results,
        "invalid_fixture_results": invalid_results,
        "not_computable_fixture_results": nc_results,
        "comparison_summary": comparison_summary,
        "solver_policy_summary": build_solver_policy_summary(),
        "blocked_scopes": build_blocked_scopes(),
        "authority_locks": build_authority_locks(),
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_COMPUTATION",
            "generated_by": "WASSERSTEIN_CPU_BASELINE_COMPUTATION_001",
            "source_gate_hash": SOURCE_GATE_HASH,
            "evidence_refs": [
                (
                    "WassersteinCpuBaselineImplementationGate.v1:"
                    "wasserstein_cpu_baseline_implementation_gate_001"
                ),
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }
    return build_wasserstein_cpu_baseline_computation_receipt(payload)


def test_full_receipt_builds_without_error() -> None:
    packet = _build_full_packet()
    assert packet is not None


def test_full_receipt_schema_version() -> None:
    packet = _build_full_packet()
    assert packet["schema_version"] == SCHEMA_VERSION


def test_full_receipt_computation_status() -> None:
    packet = _build_full_packet()
    assert packet["computation_status"] == COMPUTATION_STATUS


def test_full_receipt_all_matched() -> None:
    packet = _build_full_packet()
    assert packet["comparison_summary"]["all_matched"] is True


def test_full_receipt_valid_count() -> None:
    packet = _build_full_packet()
    assert len(packet["valid_fixture_results"]) == 5


def test_full_receipt_invalid_count() -> None:
    packet = _build_full_packet()
    assert len(packet["invalid_fixture_results"]) == 5


def test_full_receipt_nc_count() -> None:
    packet = _build_full_packet()
    assert len(packet["not_computable_fixture_results"]) == 4


def test_full_receipt_all_valid_matched() -> None:
    packet = _build_full_packet()
    for r in packet["valid_fixture_results"]:
        assert r["distance_matched"] is True, f"{r['fixture_id']} did not match"


def test_full_receipt_all_invalid_routed() -> None:
    packet = _build_full_packet()
    for r in packet["invalid_fixture_results"]:
        assert r["computation_status"] == "INVALID_INPUT"


def test_full_receipt_all_nc_routed() -> None:
    packet = _build_full_packet()
    for r in packet["not_computable_fixture_results"]:
        assert r["computation_status"] == "NOT_COMPUTABLE"


def test_full_receipt_no_metric_values_emitted() -> None:
    packet = _build_full_packet()
    for r in packet["valid_fixture_results"]:
        assert r["metric_value_emitted"] is False
    for r in packet["invalid_fixture_results"]:
        assert r["metric_value_emitted"] is False
    for r in packet["not_computable_fixture_results"]:
        assert r["metric_value_emitted"] is False


def test_full_receipt_canonical_hash_stable() -> None:
    p1 = _build_full_packet()
    p2 = _build_full_packet()
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_full_receipt_canonical_hash_valid() -> None:
    packet = _build_full_packet()
    preimage = {k: v for k, v in packet.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == packet["canonical_hash"]


def test_full_receipt_authority_locks() -> None:
    packet = _build_full_packet()
    al = packet["authority_locks"]
    assert al["wasserstein_cpu_baseline_computation_authorized"] is True
    assert al["emits_metric_values"] is False
    assert al["execution_authority"] is False
    assert al["shadow_lane_only"] is True


def test_full_receipt_blocked_scopes() -> None:
    packet = _build_full_packet()
    bs = packet["blocked_scopes"]
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        assert bs[flag] is False


def test_full_receipt_validate_passes() -> None:
    packet = _build_full_packet()
    validate_wasserstein_cpu_baseline_computation_receipt(packet)


def test_full_receipt_source_gate_hash() -> None:
    packet = _build_full_packet()
    assert packet["source_gate_hash"] == SOURCE_GATE_HASH


def test_validate_raises_on_wrong_schema() -> None:
    packet = _build_full_packet()
    bad = copy.deepcopy(packet)
    bad["schema_version"] = "WrongSchema.v1"
    bad.pop("canonical_hash")
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items()})
    with pytest.raises(WassersteinCpuBaselineComputationError):
        validate_wasserstein_cpu_baseline_computation_receipt(bad)


def test_validate_raises_on_metric_emitted() -> None:
    packet = _build_full_packet()
    bad = copy.deepcopy(packet)
    bad["authority_locks"]["emits_metric_values"] = True
    bad.pop("canonical_hash")
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items()})
    with pytest.raises(WassersteinCpuBaselineComputationError):
        validate_wasserstein_cpu_baseline_computation_receipt(bad)


def test_validate_raises_on_missing_fields() -> None:
    with pytest.raises(WassersteinCpuBaselineComputationError):
        validate_wasserstein_cpu_baseline_computation_receipt({"schema_version": SCHEMA_VERSION})


def test_serialize_roundtrip() -> None:
    packet = _build_full_packet()
    serialized = serialize_wasserstein_cpu_baseline_computation_receipt(packet)
    reloaded = json.loads(serialized)
    assert reloaded["canonical_hash"] == packet["canonical_hash"]
    assert reloaded["computation_status"] == COMPUTATION_STATUS
