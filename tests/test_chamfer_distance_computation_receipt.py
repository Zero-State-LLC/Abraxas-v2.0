from __future__ import annotations

import pytest

from core.chamfer_distance_computation_receipt import (
    EXPECTED_SHADOW_DISTANCES,
    FORBIDDEN,
    INVALID_FIXTURE_IDS,
    NC_FIXTURE_IDS,
    SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH,
    SOURCE_FIXTURE_CREATION_GATE_HASH,
    VALID_FIXTURE_IDS,
    ChamferDistanceComputationReceiptError,
    _chamfer_shadow,
    _nearest_mean,
    _squared_distance,
    build_chamfer_distance_computation_receipt,
    compute_chamfer_distance_computation_receipt_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_determinism_checks,
    default_fixture_computation_results,
    default_no_forecast_influence_scan,
    default_no_p43_surface_lane_scan,
    default_numerical_policy,
    run_fixture_computation,
    serialize_chamfer_distance_computation_receipt,
)


# ---------------------------------------------------------------------------
# Fixture corpus (mirrors the 13 files, hard-coded for unit tests)
# ---------------------------------------------------------------------------

_VALID_FIXTURES = [
    {
        "fixture_id": "chamfer.valid.duplicate_points.v1",
        "fixture_type": "VALID",
        "case_family": "DUPLICATE_POINTS",
        "expected_distance": 0.0,
        "expected_status": "VALID_INPUT_WITH_EXPECTED_DISTANCE",
        "point_sets": {
            "point_set_a": [[0, 0], [0, 0], [1, 1]],
            "point_set_b": [[0, 0], [1, 1]],
        },
    },
    {
        "fixture_id": "chamfer.valid.identical_point_sets.v1",
        "fixture_type": "VALID",
        "case_family": "IDENTICAL_POINT_SETS",
        "expected_distance": 0.0,
        "expected_status": "VALID_INPUT_WITH_EXPECTED_DISTANCE",
        "point_sets": {
            "point_set_a": [[0, 0], [1, 1]],
            "point_set_b": [[0, 0], [1, 1]],
        },
    },
    {
        "fixture_id": "chamfer.valid.multidimensional_points.v1",
        "fixture_type": "VALID",
        "case_family": "MULTIDIMENSIONAL_POINTS",
        "expected_distance": 3.0,
        "expected_status": "VALID_INPUT_WITH_EXPECTED_DISTANCE",
        "point_sets": {
            "point_set_a": [[0, 0, 0], [1, 1, 1]],
            "point_set_b": [[0, 0, 0], [0, 3, 3]],
        },
    },
    {
        "fixture_id": "chamfer.valid.offset_point_sets.v1",
        "fixture_type": "VALID",
        "case_family": "OFFSET_POINT_SETS",
        "expected_distance": 1.0,
        "expected_status": "VALID_INPUT_WITH_EXPECTED_DISTANCE",
        "point_sets": {
            "point_set_a": [[0, 0], [1, 1]],
            "point_set_b": [[1, 1], [2, 2]],
        },
    },
    {
        "fixture_id": "chamfer.valid.partial_overlap_point_sets.v1",
        "fixture_type": "VALID",
        "case_family": "PARTIAL_OVERLAP_POINT_SETS",
        "expected_distance": 0.5,
        "expected_status": "VALID_INPUT_WITH_EXPECTED_DISTANCE",
        "point_sets": {
            "point_set_a": [[0, 0], [1, 0]],
            "point_set_b": [[1, 0], [2, 0]],
        },
    },
]

_INVALID_FIXTURES = [
    {"fixture_id": f"chamfer.invalid.{x}.v1", "fixture_type": "INVALID",
     "case_family": x.upper(), "expected_status": "INVALID_INPUT_NO_EXPECTED_DISTANCE"}
    for x in ["dimension_mismatch", "empty_point_set", "malformed_coordinates",
               "missing_point_set", "non_numeric_coordinate"]
]

_NC_FIXTURES = [
    {"fixture_id": f"chamfer.not_computable.{x}.v1", "fixture_type": "NOT_COMPUTABLE",
     "case_family": x.upper(), "expected_status": "NOT_COMPUTABLE_NO_EXPECTED_DISTANCE"}
    for x in ["missing_numerical_policy", "undeclared_dimensionality", "unknown_coordinate_space"]
]


def _base_payload() -> dict:
    valid_r, invalid_r, nc_r = run_fixture_computation(
        _VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES
    )
    return {
        "computation_receipt_id": "chamfer_distance_computation_receipt_001",
        "intended_lane": "SHADOW",
        "computation_stage": "COMPUTATION_RECEIPT_ONLY",
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
        "recommended_next_step": "CHAMFER_DISTANCE_COMPUTATION_AUTHORIZATION_REVIEW",
        "provenance": {
            "source": "CHAMFER_DISTANCE_COMPUTATION_RECEIPT",
            "evidence_refs": [
                "ChamferFixtureCreationActualPrGate.v1:chamfer_fixture_creation_actual_pr_gate_001",
            ],
            "generated_by": "PATCH_CHAMFER_DISTANCE_COMPUTATION_RECEIPT_001",
            "upstream_schema_refs": [],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Kernel unit tests
# ---------------------------------------------------------------------------


def test_squared_distance_zero() -> None:
    assert _squared_distance([0.0, 0.0], [0.0, 0.0]) == 0.0


def test_squared_distance_known() -> None:
    import math
    v = _squared_distance([1.0, 0.0], [0.0, 0.0])
    assert math.isclose(v, 1.0)


def test_nearest_mean_identical() -> None:
    a = [[0.0, 0.0], [1.0, 1.0]]
    assert _nearest_mean(a, a) == 0.0


def test_chamfer_shadow_identical() -> None:
    a = [[0.0, 0.0], [1.0, 1.0]]
    assert _chamfer_shadow(a, a) == 0.0


def test_chamfer_shadow_offset() -> None:
    import math
    a = [[0.0, 0.0], [1.0, 1.0]]
    b = [[1.0, 1.0], [2.0, 2.0]]
    result = _chamfer_shadow(a, b)
    assert math.isclose(result, 1.0, abs_tol=1e-9)


# ---------------------------------------------------------------------------
# Fixture computation
# ---------------------------------------------------------------------------


def test_run_fixture_computation_counts() -> None:
    vr, ir, nr = run_fixture_computation(_VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES)
    assert len(vr) == 5
    assert len(ir) == 5
    assert len(nr) == 3


def test_valid_fixture_values_match_static() -> None:
    vr, _, _ = run_fixture_computation(_VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES)
    for r in vr:
        assert r["values_match"] is True, f"mismatch for {r['fixture_id']}"


def test_valid_fixture_no_metric_emission() -> None:
    vr, _, _ = run_fixture_computation(_VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES)
    for r in vr:
        assert r["metric_value_emitted"] is False


def test_invalid_fixture_status() -> None:
    _, ir, _ = run_fixture_computation(_VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES)
    for r in ir:
        assert r["computation_status"] == "VALIDATION_ERROR"
        assert r["metric_value_emitted"] is False


def test_nc_fixture_status() -> None:
    _, _, nr = run_fixture_computation(_VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES)
    for r in nr:
        assert r["computation_status"] == "NOT_COMPUTABLE"
        assert r["metric_value_emitted"] is False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_expected_shadow_distances() -> None:
    assert EXPECTED_SHADOW_DISTANCES["chamfer.valid.duplicate_points.v1"] == 0.0
    assert EXPECTED_SHADOW_DISTANCES["chamfer.valid.identical_point_sets.v1"] == 0.0
    assert EXPECTED_SHADOW_DISTANCES["chamfer.valid.multidimensional_points.v1"] == 3.0
    assert EXPECTED_SHADOW_DISTANCES["chamfer.valid.offset_point_sets.v1"] == 1.0
    assert EXPECTED_SHADOW_DISTANCES["chamfer.valid.partial_overlap_point_sets.v1"] == 0.5


def test_valid_fixture_ids_count() -> None:
    assert len(VALID_FIXTURE_IDS) == 5


def test_invalid_fixture_ids_count() -> None:
    assert len(INVALID_FIXTURE_IDS) == 5


def test_nc_fixture_ids_count() -> None:
    assert len(NC_FIXTURE_IDS) == 3


def test_source_hashes_present() -> None:
    assert len(SOURCE_FIXTURE_CREATION_GATE_HASH) == 64
    assert len(SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH) == 64


# ---------------------------------------------------------------------------
# Build / validate / hash / serialize
# ---------------------------------------------------------------------------


def test_build_valid_receipt() -> None:
    packet = build_chamfer_distance_computation_receipt(_base_payload())
    assert packet["schema_version"] == "ChamferDistanceComputationReceipt.v1"
    assert packet["receipt_type"] == "CHAMFER_DISTANCE_COMPUTATION_RECEIPT"
    assert packet["operator_id"] == "CHAMFER_DISTANCE"
    assert "canonical_hash" in packet


def test_hash_is_deterministic() -> None:
    p1 = build_chamfer_distance_computation_receipt(_base_payload())
    p2 = build_chamfer_distance_computation_receipt(_base_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_hash_function() -> None:
    packet = build_chamfer_distance_computation_receipt(_base_payload())
    h = compute_chamfer_distance_computation_receipt_hash(packet)
    assert h == packet["canonical_hash"]


def test_serialize_produces_string() -> None:
    packet = build_chamfer_distance_computation_receipt(_base_payload())
    s = serialize_chamfer_distance_computation_receipt(packet)
    assert isinstance(s, str)
    assert "CHAMFER_DISTANCE_COMPUTATION_RECEIPT" in s


def test_invalid_schema_version_raises() -> None:
    payload = _base_payload()
    payload["_override_schema"] = True
    packet = build_chamfer_distance_computation_receipt(payload)
    packet2 = dict(packet)
    packet2["schema_version"] = "Wrong.v1"
    with pytest.raises(ChamferDistanceComputationReceiptError, match="invalid_schema_version"):
        from core.chamfer_distance_computation_receipt import (
            validate_chamfer_distance_computation_receipt,
        )
        validate_chamfer_distance_computation_receipt(packet2)


def test_invalid_lane_raises() -> None:
    payload = _base_payload()
    payload["intended_lane"] = "PRODUCTION"
    with pytest.raises(ChamferDistanceComputationReceiptError, match="invalid_lane"):
        build_chamfer_distance_computation_receipt(payload)


def test_authority_lock_violation_raises() -> None:
    payload = _base_payload()
    al = dict(default_authority_locks())
    al["emits_metric_values"] = True
    payload["authority_locks"] = al
    with pytest.raises(ChamferDistanceComputationReceiptError):
        build_chamfer_distance_computation_receipt(payload)


def test_forbidden_provenance_token_raises() -> None:
    payload = _base_payload()
    payload["provenance"]["source"] = "runtime_mutation_source"
    with pytest.raises(ChamferDistanceComputationReceiptError, match="forbidden"):
        build_chamfer_distance_computation_receipt(payload)


def test_authority_locks_defaults() -> None:
    al = default_authority_locks()
    assert al["emits_metric_values"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["chamfer_distance_computation_authorized"] is True


def test_blocked_scopes_all_false() -> None:
    bs = default_blocked_scopes()
    assert all(v is False for v in bs.values())


def test_numerical_policy_shadow_only() -> None:
    np_ = default_numerical_policy()
    assert np_["shadow_only"] is True
    assert np_["deterministic"] is True


def test_fixture_computation_results_totals() -> None:
    vr, ir, nr = run_fixture_computation(_VALID_FIXTURES, _INVALID_FIXTURES, _NC_FIXTURES)
    fcr = default_fixture_computation_results(vr, ir, nr)
    assert fcr["total_fixtures"] == 13
    assert fcr["valid_computed"] == 5
    assert fcr["invalid_rejected"] == 5
    assert fcr["not_computable_rejected"] == 3
    assert fcr["all_values_match_static_fixtures"] is True


def test_forbidden_tokens_list_nonempty() -> None:
    assert len(FORBIDDEN) > 0
    assert "runtime" in FORBIDDEN
