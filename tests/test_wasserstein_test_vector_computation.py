from __future__ import annotations

import math

import pytest

from core.wasserstein_test_vector_computation import (
    SOURCE_ACTUAL_PR_GATE_HASH,
    SOURCE_SCHEMA_VALIDATION_EXECUTION_HASH,
    _euclidean,
    _transport_cost,
    _w1_from_support,
    build_wasserstein_test_vector_computation_receipt,
    compute_wasserstein_test_vector_computation_receipt_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_determinism_checks,
    default_fixture_computation_results,
    default_no_forecast_influence_scan,
    default_no_p43_surface_lane_scan,
    default_numerical_policy,
    run_fixture_computation,
    serialize_wasserstein_test_vector_computation_receipt,
)

# ---------------------------------------------------------------------------
# Fixture corpus (mirrors the 14 files on disk, hard-coded for unit tests)
# ---------------------------------------------------------------------------

_VALID_FIXTURES = [
    {
        "fixture_id": "valid-001",
        "fixture_type": "VALID",
        "fixture_group": "DISTRIBUTION_PAIR_SCHEMA",
        "input": {"p": [0.2, 0.5, 0.3], "q": [0.4, 0.1, 0.5], "support": [0, 1, 2]},
        "rejection_reason": None,
    },
    {
        "fixture_id": "valid-002",
        "fixture_type": "VALID",
        "fixture_group": "WEIGHTED_HISTOGRAM_SCHEMA",
        "input": {
            "bin_edges": [0.0, 1.0, 2.0, 3.0],
            "weights_p": [0.1, 0.6, 0.3],
            "weights_q": [0.4, 0.4, 0.2],
        },
        "rejection_reason": None,
    },
    {
        "fixture_id": "valid-003",
        "fixture_type": "VALID",
        "fixture_group": "REFERENCE_VECTOR_SCHEMA",
        "input": {
            "declared_ground_metric": "euclidean",
            "dimensionality": 3,
            "query_vector": [1.5, 2.5, 3.5],
            "reference_vector": [1.0, 2.0, 3.0],
        },
        "rejection_reason": None,
    },
    {
        "fixture_id": "valid-004",
        "fixture_type": "VALID",
        "fixture_group": "GROUND_METRIC_SCHEMA",
        "input": {
            "cost_matrix": [[0.0, 1.0, 2.0], [1.0, 0.0, 1.0], [2.0, 1.0, 0.0]],
            "p": [0.3, 0.4, 0.3],
            "q": [0.5, 0.2, 0.3],
        },
        "rejection_reason": None,
    },
    {
        "fixture_id": "valid-005",
        "fixture_type": "VALID",
        "fixture_group": "DEGENERATE_DISTRIBUTION_SCHEMA",
        "input": {"p": [1.0], "q": [1.0], "support": [0]},
        "rejection_reason": None,
    },
]

_INVALID_FIXTURES = [
    {
        "fixture_id": "invalid-001",
        "fixture_type": "INVALID",
        "fixture_group": "MISSING_REQUIRED_FIELD",
        "input": {"p": [0.2, 0.5, 0.3], "support": [0, 1, 2]},
        "rejection_reason": "missing_required_field: q absent from input",
    },
    {
        "fixture_id": "invalid-002",
        "fixture_type": "INVALID",
        "fixture_group": "EMPTY_DISTRIBUTION",
        "input": {"p": [], "q": [], "support": []},
        "rejection_reason": "empty_distribution: p and q must each contain at least one element",
    },
    {
        "fixture_id": "invalid-003",
        "fixture_type": "INVALID",
        "fixture_group": "INVALID_WEIGHT_SUM",
        "input": {"p": [0.2, 0.3, 0.3], "q": [0.4, 0.1, 0.5], "support": [0, 1, 2]},
        "rejection_reason": "invalid_weight_sum: sum(p)=0.8 violates unit-mass constraint",
    },
    {
        "fixture_id": "invalid-004",
        "fixture_type": "INVALID",
        "fixture_group": "DIMENSION_MISMATCH",
        "input": {"p": [0.2, 0.5, 0.3], "q": [0.4, 0.6], "support": [0, 1, 2]},
        "rejection_reason": "dimension_mismatch: len(p)=3 != len(q)=2",
    },
    {
        "fixture_id": "invalid-005",
        "fixture_type": "INVALID",
        "fixture_group": "GROUND_METRIC_UNDECLARED",
        "input": {"p": [0.2, 0.5, 0.3], "q": [0.4, 0.1, 0.5], "support": [0, 1, 2]},
        "rejection_reason": (
            "ground_metric_undeclared: cost structure required by schema but absent from input fields"
        ),
    },
]

_NC_FIXTURES = [
    {
        "fixture_id": "nc-001",
        "fixture_type": "NOT_COMPUTABLE",
        "fixture_group": "EMPTY_INPUT",
        "input": {"p": None, "q": None},
        "rejection_reason": "not_computable: empty_input \u2014 no distribution data present to operate on",
    },
    {
        "fixture_id": "nc-002",
        "fixture_type": "NOT_COMPUTABLE",
        "fixture_group": "GROUND_METRIC_UNDECLARED",
        "input": {"declared_ground_metric": None, "p": [0.2, 0.5, 0.3], "q": [0.4, 0.1, 0.5], "support": [0, 1, 2]},
        "rejection_reason": (
            "not_computable: ground_metric_policy_undeclared \u2014 system-level cost policy absent; cannot determine transport plan"
        ),
    },
    {
        "fixture_id": "nc-003",
        "fixture_type": "NOT_COMPUTABLE",
        "fixture_group": "NUMERICAL_POLICY_MISSING",
        "input": {"declared_ground_metric": "euclidean", "numerical_policy": None, "p": [0.2, 0.5, 0.3], "q": [0.4, 0.1, 0.5], "support": [0, 1, 2]},
        "rejection_reason": (
            "not_computable: numerical_policy_missing \u2014 precision and regularization policy not declared; solver cannot proceed safely"
        ),
    },
    {
        "fixture_id": "nc-004",
        "fixture_type": "NOT_COMPUTABLE",
        "fixture_group": "DIMENSIONALITY_UNDECLARED",
        "input": {"declared_ground_metric": "euclidean", "dimensionality": None, "p": [0.3, 0.7], "q": [0.5, 0.5]},
        "rejection_reason": (
            "not_computable: dimensionality_undeclared \u2014 ambient space dimension absent; transport geometry indeterminate"
        ),
    },
]


def _payload() -> dict:
    valid_r, invalid_r, nc_r = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    return {
        "computation_receipt_id": "wasserstein_test_vector_computation_receipt_001",
        "intended_lane": "SHADOW",
        "computation_stage": "TEST_VECTOR_COMPUTATION_ONLY",
        "fixture_computation_results": default_fixture_computation_results(
            valid_r, invalid_r, nc_r
        ),
        "valid_fixture_results": valid_r,
        "invalid_fixture_results": invalid_r,
        "not_computable_fixture_results": nc_r,
        "numerical_policy": default_numerical_policy(),
        "determinism_checks": default_determinism_checks(),
        "no_forecast_influence_scan": default_no_forecast_influence_scan(),
        "no_p43_surface_lane_scan": default_no_p43_surface_lane_scan(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW"
        ),
        "provenance": {
            "source": "P57_WASSERSTEIN_TEST_VECTOR_COMPUTATION",
            "evidence_refs": [
                "WassersteinTestVectorComputationActualPrGate.v1:"
                "wasserstein_test_vector_computation_actual_pr_gate_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_test_vector_computation_receipt.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Computation kernels
# ---------------------------------------------------------------------------


def test_w1_distribution_pair() -> None:
    result = _w1_from_support([0.2, 0.5, 0.3], [0.4, 0.1, 0.5], [0.0, 1.0, 2.0])
    assert abs(result - 0.4) < 1e-12


def test_w1_degenerate_same_support() -> None:
    result = _w1_from_support([1.0], [1.0], [0.0])
    assert result == 0.0


def test_w1_weighted_histogram() -> None:
    edges = [0.0, 1.0, 2.0, 3.0]
    midpoints = [(edges[k] + edges[k + 1]) / 2.0 for k in range(len(edges) - 1)]
    result = _w1_from_support([0.1, 0.6, 0.3], [0.4, 0.4, 0.2], midpoints)
    assert abs(result - 0.4) < 1e-12


def test_euclidean_reference_vector() -> None:
    result = _euclidean([1.0, 2.0, 3.0], [1.5, 2.5, 3.5])
    assert abs(result - math.sqrt(0.75)) < 1e-12


def test_euclidean_identical_vectors() -> None:
    assert _euclidean([1.0, 2.0], [1.0, 2.0]) == 0.0


def test_transport_cost_ground_metric() -> None:
    cost = [[0.0, 1.0, 2.0], [1.0, 0.0, 1.0], [2.0, 1.0, 0.0]]
    result = _transport_cost([0.3, 0.4, 0.3], [0.5, 0.2, 0.3], cost)
    assert abs(result - 0.2) < 1e-12


def test_transport_cost_identity() -> None:
    cost = [[0.0, 1.0], [1.0, 0.0]]
    result = _transport_cost([0.5, 0.5], [0.5, 0.5], cost)
    assert abs(result) < 1e-12


# ---------------------------------------------------------------------------
# run_fixture_computation
# ---------------------------------------------------------------------------


def test_run_fixture_computation_counts() -> None:
    valid_r, invalid_r, nc_r = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    assert len(valid_r) == 5
    assert len(invalid_r) == 5
    assert len(nc_r) == 4


def test_valid_results_shadow_computation_complete() -> None:
    valid_r, _, _ = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    for r in valid_r:
        assert r["computation_status"] == "SHADOW_COMPUTATION_COMPLETE"
        assert r["shadow_lane"] == "SHADOW"
        assert r["metric_value_emitted"] is False
        assert r["expected_distance_included"] is False
        assert r["deterministic"] is True
        assert "shadow_transport_value" in r


def test_invalid_results_validation_error() -> None:
    _, invalid_r, _ = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    for r in invalid_r:
        assert r["computation_status"] == "VALIDATION_ERROR"
        assert r["metric_value_emitted"] is False


def test_nc_results_not_computable() -> None:
    _, _, nc_r = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    for r in nc_r:
        assert r["computation_status"] == "NOT_COMPUTABLE"
        assert r["metric_value_emitted"] is False


def test_valid_001_shadow_transport_value() -> None:
    valid_r, _, _ = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    r = next(x for x in valid_r if x["fixture_id"] == "valid-001")
    assert abs(r["shadow_transport_value"] - 0.4) < 1e-12


def test_valid_002_shadow_transport_value() -> None:
    valid_r, _, _ = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    r = next(x for x in valid_r if x["fixture_id"] == "valid-002")
    assert abs(r["shadow_transport_value"] - 0.4) < 1e-12


def test_valid_003_shadow_transport_value() -> None:
    valid_r, _, _ = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    r = next(x for x in valid_r if x["fixture_id"] == "valid-003")
    assert abs(r["shadow_transport_value"] - math.sqrt(0.75)) < 1e-12


def test_valid_004_shadow_transport_value() -> None:
    valid_r, _, _ = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    r = next(x for x in valid_r if x["fixture_id"] == "valid-004")
    assert abs(r["shadow_transport_value"] - 0.2) < 1e-12


def test_valid_005_shadow_transport_value() -> None:
    valid_r, _, _ = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    r = next(x for x in valid_r if x["fixture_id"] == "valid-005")
    assert abs(r["shadow_transport_value"]) < 1e-12


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash() -> None:
    a = build_wasserstein_test_vector_computation_receipt(_payload())
    b = build_wasserstein_test_vector_computation_receipt(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_deterministic_serialization() -> None:
    a = build_wasserstein_test_vector_computation_receipt(_payload())
    b = build_wasserstein_test_vector_computation_receipt(_payload())
    assert serialize_wasserstein_test_vector_computation_receipt(
        a
    ) == serialize_wasserstein_test_vector_computation_receipt(b)


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    assert packet["schema_version"] == "WassersteinTestVectorComputationReceipt.v1"
    assert packet["receipt_type"] == "WASSERSTEIN_TEST_VECTOR_COMPUTATION_RECEIPT"
    assert packet["operator_id"] == "WASSERSTEIN"
    assert packet["source_actual_pr_gate_hash"] == SOURCE_ACTUAL_PR_GATE_HASH
    assert (
        packet["source_schema_validation_execution_hash"]
        == SOURCE_SCHEMA_VALIDATION_EXECUTION_HASH
    )
    assert packet["intended_lane"] == "SHADOW"
    assert packet["computation_stage"] == "TEST_VECTOR_COMPUTATION_ONLY"


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_computation_authorized_true() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    assert packet["authority_locks"]["wasserstein_computation_authorized"] is True


def test_test_vector_computation_only_true() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    assert packet["authority_locks"]["test_vector_computation_only"] is True


def test_emits_metric_values_false() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    assert packet["authority_locks"]["emits_metric_values"] is False


def test_execution_authority_false() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    assert packet["authority_locks"]["execution_authority"] is False


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="emits_metric_values_must_be_false"):
        build_wasserstein_test_vector_computation_receipt(p)


def test_computation_authorized_false_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["wasserstein_computation_authorized"] = False
    p["authority_locks"] = al
    with pytest.raises(
        ValueError, match="wasserstein_computation_authorized_must_be_true"
    ):
        build_wasserstein_test_vector_computation_receipt(p)


# ---------------------------------------------------------------------------
# Blocked scopes
# ---------------------------------------------------------------------------


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    bs = default_blocked_scopes()
    bs["forecast_influence"] = True
    p["blocked_scopes"] = bs
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_computation_receipt(p)


# ---------------------------------------------------------------------------
# fixture_computation_results
# ---------------------------------------------------------------------------


def test_fixture_computation_results_summary() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    fcr = packet["fixture_computation_results"]
    assert fcr["total_fixtures"] == 14
    assert fcr["valid_computed"] == 5
    assert fcr["invalid_rejected"] == 5
    assert fcr["not_computable_rejected"] == 4
    assert fcr["all_shadow_lane"] is True
    assert fcr["no_metric_values_emitted"] is True
    assert (
        fcr["computation_status"]
        == "WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE"
    )


def test_fixture_total_mismatch_raises() -> None:
    p = _payload()
    fcr = dict(p["fixture_computation_results"])
    fcr["total_fixtures"] = 10
    p["fixture_computation_results"] = fcr
    with pytest.raises(ValueError, match="fixture_computation_total_mismatch"):
        build_wasserstein_test_vector_computation_receipt(p)


def test_not_all_shadow_raises() -> None:
    p = _payload()
    fcr = dict(p["fixture_computation_results"])
    fcr["all_shadow_lane"] = False
    p["fixture_computation_results"] = fcr
    with pytest.raises(ValueError, match="not_all_results_shadow_lane"):
        build_wasserstein_test_vector_computation_receipt(p)


# ---------------------------------------------------------------------------
# Numerical policy + determinism
# ---------------------------------------------------------------------------


def test_numerical_policy_deterministic() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    np_ = packet["numerical_policy"]
    assert np_["deterministic"] is True
    assert np_["shadow_only"] is True
    assert np_["no_stochastic_elements"] is True


def test_determinism_checks_pass() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    dc = packet["determinism_checks"]
    assert dc["all_results_deterministic"] is True
    assert dc["determinism_status"] == "PASS"


# ---------------------------------------------------------------------------
# Scan sections
# ---------------------------------------------------------------------------


def test_no_forecast_influence_scan_clean() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    scan = packet["no_forecast_influence_scan"]
    assert scan["scan_status"] == "CLEAN"
    assert scan["violations"] == []
    assert scan["total_checked"] == 14


def test_no_p43_scan_clean() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    scan = packet["no_p43_surface_lane_scan"]
    assert scan["scan_status"] == "CLEAN"
    assert scan["violations"] == []
    assert scan["total_checked"] == 14


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_computation_receipt(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_test_vector_computation_receipt_hash(packet)
        == compute_wasserstein_test_vector_computation_receipt_hash(altered)
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_computation_receipt(_payload())
    b = build_wasserstein_test_vector_computation_receipt(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring metric-value authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_computation_receipt(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["computation_receipt_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_computation_receipt(p)


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("computation_stage", "ACTIVE", "unknown_computation_stage"),
    ],
)
def test_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_computation_receipt(p)
