"""Tests for TRANSPORT COMPUTATION — BOUNDED SHADOW TEST-VECTOR COMPUTATION.

Algorithm: DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH
Lane: SHADOW | Scope: TEST_VECTOR_COMPUTATION_ONLY
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.transport_computation import (
    ALGORITHM,
    CORPUS_HASH,
    EPSILON_ABS,
    EPSILON_REL,
    GATE_HASH,
    MAX_DEMAND_LEN,
    MAX_SUPPLY_LEN,
    NOT_COMPUTABLE_BRANCHES,
    OPERATOR_ID,
    PIVOT_RULE,
    SCHEMA_VERSION,
    TIE_BREAKING_RULE,
    TransportComputationError,
    _northwest_corner,
    _solve_transport,
    _validate_input,
    build_transport_computation_receipt,
    process_fixture,
    validate_transport_computation_receipt,
)

FIXTURE_DIR = Path("input/fixtures/transport")
CORPUS_RECEIPT_PATH = Path(
    "out/metric_operator/transport_fixture_corpus_creation_receipt_001.latest.json"
)


def _load_manifest() -> list[dict]:
    return json.loads(CORPUS_RECEIPT_PATH.read_text())["fixture_manifest"]


def _load_fixture(fixture_id: str) -> dict:
    return json.loads((FIXTURE_DIR / f"{fixture_id}.json").read_text())


class TestConstants:
    def test_algorithm_name(self):
        assert ALGORITHM == "DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH"

    def test_pivot_rule(self):
        assert PIVOT_RULE == "LEXICOGRAPHIC_MIN_COST_THEN_ROW_MAJOR"

    def test_tie_breaking_rule(self):
        assert TIE_BREAKING_RULE == "ROW_MAJOR_THEN_COLUMN_MAJOR"

    def test_max_dimensions(self):
        assert MAX_SUPPLY_LEN == 4
        assert MAX_DEMAND_LEN == 4

    def test_balance_tolerance(self):
        assert EPSILON_ABS == 0.0
        assert EPSILON_REL == 0.0

    def test_not_computable_branches_count(self):
        assert len(NOT_COMPUTABLE_BRANCHES) == 9

    def test_not_computable_branches_content(self):
        expected = {
            "COST_MATRIX_SHAPE_MISMATCH",
            "EMPTY_DEMAND_VECTOR",
            "EMPTY_SUPPLY_VECTOR",
            "NEGATIVE_COST_VALUE",
            "NEGATIVE_SUPPLY_VALUE",
            "NON_FINITE_COST_VALUE",
            "NON_FINITE_DEMAND_VALUE",
            "NON_FINITE_SUPPLY_VALUE",
            "UNBALANCED_SUPPLY_DEMAND",
        }
        assert set(NOT_COMPUTABLE_BRANCHES) == expected

    def test_operator_id(self):
        assert OPERATOR_ID == "TRANSPORT"

    def test_schema_version(self):
        assert SCHEMA_VERSION == "TransportComputationReceipt.v1"

    def test_gate_hash_length(self):
        assert len(GATE_HASH) == 64

    def test_corpus_hash_length(self):
        assert len(CORPUS_HASH) == 64


class TestValidateInput:
    def test_missing_supply(self):
        status, reason = _validate_input({"demand": [1.0], "cost_matrix": [[1.0]]})
        assert status == "REJECTED"
        assert "supply" in reason

    def test_missing_demand(self):
        status, reason = _validate_input({"supply": [1.0], "cost_matrix": [[1.0]]})
        assert status == "REJECTED"
        assert "demand" in reason

    def test_missing_cost_matrix(self):
        status, reason = _validate_input({"supply": [1.0], "demand": [1.0]})
        assert status == "REJECTED"
        assert "cost_matrix" in reason

    def test_empty_supply(self):
        status, reason = _validate_input(
            {"supply": [], "demand": [1.0], "cost_matrix": []}
        )
        assert status == "NOT_COMPUTABLE"
        assert reason == "EMPTY_SUPPLY_VECTOR"

    def test_empty_demand(self):
        status, reason = _validate_input(
            {"supply": [1.0], "demand": [], "cost_matrix": [[1.0]]}
        )
        assert status == "NOT_COMPUTABLE"
        assert reason == "EMPTY_DEMAND_VECTOR"

    def test_non_finite_supply_none(self):
        status, reason = _validate_input(
            {"supply": [1.0, None], "demand": [1.0, 1.0], "cost_matrix": [[1.0, 0.0], [0.0, 1.0]]}
        )
        assert status == "NOT_COMPUTABLE"
        assert reason == "NON_FINITE_SUPPLY_VALUE"

    def test_negative_supply(self):
        status, reason = _validate_input(
            {"supply": [2.0, -1.0], "demand": [1.0], "cost_matrix": [[1.0], [1.0]]}
        )
        assert status == "NOT_COMPUTABLE"
        assert reason == "NEGATIVE_SUPPLY_VALUE"

    def test_negative_cost(self):
        status, reason = _validate_input(
            {"supply": [1.0], "demand": [1.0], "cost_matrix": [[-1.0]]}
        )
        assert status == "NOT_COMPUTABLE"
        assert reason == "NEGATIVE_COST_VALUE"

    def test_shape_mismatch_cols(self):
        status, reason = _validate_input(
            {
                "supply": [1.0, 1.0],
                "demand": [1.0, 1.0],
                "cost_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            }
        )
        assert status == "NOT_COMPUTABLE"
        assert reason == "COST_MATRIX_SHAPE_MISMATCH"

    def test_shape_mismatch_rows(self):
        status, reason = _validate_input(
            {
                "supply": [1.0],
                "demand": [1.0],
                "cost_matrix": [[1.0], [1.0]],
            }
        )
        assert status == "NOT_COMPUTABLE"
        assert reason == "COST_MATRIX_SHAPE_MISMATCH"

    def test_unbalanced(self):
        status, reason = _validate_input(
            {
                "supply": [1.0, 2.0],
                "demand": [1.0, 1.0],
                "cost_matrix": [[1.0, 1.0], [1.0, 1.0]],
            }
        )
        assert status == "NOT_COMPUTABLE"
        assert reason == "UNBALANCED_SUPPLY_DEMAND"

    def test_valid_input(self):
        status, reason = _validate_input(
            {
                "supply": [1.0, 1.0],
                "demand": [1.0, 1.0],
                "cost_matrix": [[1.0, 2.0], [2.0, 1.0]],
            }
        )
        assert status == "OK"
        assert reason is None


class TestNorthwestCorner:
    def test_2x2_returns_three_cells(self):
        alloc = _northwest_corner([1.0, 1.0], [1.0, 1.0])
        assert len(alloc) == 3  # m+n-1

    def test_1x1(self):
        alloc = _northwest_corner([5.0], [5.0])
        assert alloc == {(0, 0): 5.0}

    def test_1x4(self):
        alloc = _northwest_corner([1.0], [0.25, 0.25, 0.25, 0.25])
        assert len(alloc) == 4  # m+n-1=4
        assert abs(sum(alloc.values()) - 1.0) < 1e-9

    def test_supply_fully_allocated(self):
        supply = [3.0, 2.0]
        demand = [2.0, 3.0]
        alloc = _northwest_corner(supply, demand)
        for i, s in enumerate(supply):
            row_alloc = sum(v for (r, c), v in alloc.items() if r == i)
            assert abs(row_alloc - s) < 1e-9

    def test_demand_fully_allocated(self):
        supply = [3.0, 2.0]
        demand = [2.0, 3.0]
        alloc = _northwest_corner(supply, demand)
        for j, d in enumerate(demand):
            col_alloc = sum(v for (r, c), v in alloc.items() if c == j)
            assert abs(col_alloc - d) < 1e-9


class TestSolveTransport:
    def test_1x1_trivial(self):
        cost = [[3.0]]
        total = _solve_transport([1.0], [1.0], cost)
        assert abs(total - 3.0) < 1e-6

    def test_2x2_diagonal_zero(self):
        cost = [[0.0, 1.0], [1.0, 0.0]]
        total = _solve_transport([1.0, 1.0], [1.0, 1.0], cost)
        assert abs(total - 0.0) < 1e-6

    def test_2x2_off_diagonal(self):
        cost = [[1.0, 2.0], [2.0, 1.0]]
        total = _solve_transport([1.0, 1.0], [1.0, 1.0], cost)
        assert abs(total - 2.0) < 1e-6

    def test_1x4_closed_form(self):
        cost = [[1.0, 2.0, 3.0, 4.0]]
        total = _solve_transport([1.0], [0.25, 0.25, 0.25, 0.25], cost)
        assert abs(total - 2.5) < 1e-6

    def test_4x1_closed_form(self):
        cost = [[1.0], [2.0], [3.0], [4.0]]
        total = _solve_transport([0.25, 0.25, 0.25, 0.25], [1.0], cost)
        assert abs(total - 2.5) < 1e-6

    def test_3x3_metric_cost_uniform(self):
        cost = [[0.0, 1.0, 2.0], [1.0, 0.0, 1.0], [2.0, 1.0, 0.0]]
        total = _solve_transport([1.0, 1.0, 1.0], [1.0, 1.0, 1.0], cost)
        assert abs(total - 0.0) < 1e-6


class TestProcessFixture:
    def test_valid_001(self):
        f = _load_fixture("tv-valid-001")
        result = process_fixture(f)
        assert result["actual"] == "COMPUTED"
        assert result["matched"] is True
        assert abs(result["transport_distance"] - 0.0) < 1e-6

    def test_valid_002(self):
        f = _load_fixture("tv-valid-002")
        result = process_fixture(f)
        assert result["actual"] == "COMPUTED"
        assert result["matched"] is True
        assert abs(result["transport_distance"] - 2.0) < 1e-6

    def test_valid_003(self):
        f = _load_fixture("tv-valid-003")
        result = process_fixture(f)
        assert result["actual"] == "COMPUTED"
        assert result["matched"] is True
        assert abs(result["transport_distance"] - 2.5) < 1e-6

    def test_valid_004(self):
        f = _load_fixture("tv-valid-004")
        result = process_fixture(f)
        assert result["actual"] == "COMPUTED"
        assert result["matched"] is True
        assert abs(result["transport_distance"] - 2.5) < 1e-6

    def test_valid_005(self):
        f = _load_fixture("tv-valid-005")
        result = process_fixture(f)
        assert result["actual"] == "COMPUTED"
        assert result["matched"] is True
        assert abs(result["transport_distance"] - 3.0) < 1e-6

    def test_valid_006(self):
        f = _load_fixture("tv-valid-006")
        result = process_fixture(f)
        assert result["actual"] == "COMPUTED"
        assert result["matched"] is True
        assert abs(result["transport_distance"] - 0.0) < 1e-6

    def test_invalid_001_missing_supply(self):
        f = _load_fixture("tv-invalid-001")
        result = process_fixture(f)
        assert result["actual"] == "REJECTED"
        assert result["matched"] is True
        assert result["transport_distance"] is None

    def test_invalid_002_missing_demand(self):
        f = _load_fixture("tv-invalid-002")
        result = process_fixture(f)
        assert result["actual"] == "REJECTED"
        assert result["matched"] is True
        assert result["transport_distance"] is None

    def test_invalid_003_missing_cost_matrix(self):
        f = _load_fixture("tv-invalid-003")
        result = process_fixture(f)
        assert result["actual"] == "REJECTED"
        assert result["matched"] is True
        assert result["transport_distance"] is None

    def test_invalid_004_shape_mismatch(self):
        f = _load_fixture("tv-invalid-004")
        result = process_fixture(f)
        assert result["actual"] in ("REJECTED", "NOT_COMPUTABLE")
        assert result["matched"] is True
        assert result["transport_distance"] is None

    def test_nc_001_unbalanced(self):
        f = _load_fixture("tv-nc-001")
        result = process_fixture(f)
        assert result["actual"] == "NOT_COMPUTABLE"
        assert result["matched"] is True
        assert result["not_computable_reason"] == "UNBALANCED_SUPPLY_DEMAND"

    def test_nc_002_negative_supply(self):
        f = _load_fixture("tv-nc-002")
        result = process_fixture(f)
        assert result["actual"] == "NOT_COMPUTABLE"
        assert result["matched"] is True
        assert result["not_computable_reason"] == "NEGATIVE_SUPPLY_VALUE"

    def test_nc_003_negative_cost(self):
        f = _load_fixture("tv-nc-003")
        result = process_fixture(f)
        assert result["actual"] == "NOT_COMPUTABLE"
        assert result["matched"] is True
        assert result["not_computable_reason"] == "NEGATIVE_COST_VALUE"

    def test_nc_004_empty_supply(self):
        f = _load_fixture("tv-nc-004")
        result = process_fixture(f)
        assert result["actual"] == "NOT_COMPUTABLE"
        assert result["matched"] is True
        assert result["not_computable_reason"] == "EMPTY_SUPPLY_VECTOR"

    def test_nc_005_non_finite_supply(self):
        f = _load_fixture("tv-nc-005")
        result = process_fixture(f)
        assert result["actual"] == "NOT_COMPUTABLE"
        assert result["matched"] is True
        assert result["not_computable_reason"] == "NON_FINITE_SUPPLY_VALUE"


class TestBuildReceipt:
    @pytest.fixture(scope="class")
    def receipt(self):
        manifest = _load_manifest()
        return build_transport_computation_receipt(FIXTURE_DIR, manifest)

    def test_schema_version(self, receipt):
        assert receipt["schema_version"] == SCHEMA_VERSION

    def test_operator_id(self, receipt):
        assert receipt["operator_id"] == OPERATOR_ID

    def test_computation_executed(self, receipt):
        assert receipt["computation_executed"] is True

    def test_all_valid_passed(self, receipt):
        assert receipt["all_valid_passed"] is True

    def test_all_invalid_rejected(self, receipt):
        assert receipt["all_invalid_rejected"] is True

    def test_all_not_computable_routed(self, receipt):
        assert receipt["all_not_computable_routed"] is True

    def test_all_matched(self, receipt):
        assert receipt["all_matched"] is True

    def test_fixture_counts(self, receipt):
        assert receipt["fixture_count_total"] == 15
        assert receipt["fixture_count_valid"] == 6
        assert receipt["fixture_count_invalid"] == 4
        assert receipt["fixture_count_not_computable"] == 5

    def test_receipt_status(self, receipt):
        assert receipt["receipt_status"] == "TRANSPORT_COMPUTATION_RECEIPT_COMPLETE"

    def test_authority_locks_computation_executed(self, receipt):
        assert receipt["authority_locks"]["computation_executed"] is True

    def test_authority_locks_metric_emission_blocked(self, receipt):
        assert receipt["authority_locks"]["emits_metric_values"] is False

    def test_authority_locks_forecast_blocked(self, receipt):
        assert receipt["authority_locks"]["forecast_influence"] is False

    def test_authority_locks_p43_blocked(self, receipt):
        assert receipt["authority_locks"]["p43_surface_lanes_authorized"] is False

    def test_authority_locks_canon_blocked(self, receipt):
        assert receipt["authority_locks"]["canon_promotion"] is False

    def test_authority_locks_production_blocked(self, receipt):
        assert receipt["authority_locks"]["production_activation"] is False

    def test_canonical_hash_present(self, receipt):
        assert len(receipt.get("canonical_hash", "")) == 64

    def test_provenance_gate_ref(self, receipt):
        assert GATE_HASH in receipt["provenance"]["gate_ref"]

    def test_provenance_corpus_ref(self, receipt):
        assert CORPUS_HASH in receipt["provenance"]["corpus_ref"]

    def test_fixture_results_count(self, receipt):
        assert len(receipt["fixture_results"]) == 15

    def test_no_valid_fixture_has_null_distance(self, receipt):
        for r in receipt["fixture_results"]:
            if r["fixture_type"] == "VALID":
                assert r["transport_distance"] is not None

    def test_no_invalid_fixture_has_computed_distance(self, receipt):
        for r in receipt["fixture_results"]:
            if r["fixture_type"] == "INVALID":
                assert r["actual"] != "COMPUTED"


class TestValidateReceipt:
    @pytest.fixture(scope="class")
    def good_receipt(self):
        manifest = _load_manifest()
        return build_transport_computation_receipt(FIXTURE_DIR, manifest)

    def test_valid_receipt_passes(self, good_receipt):
        validate_transport_computation_receipt(good_receipt)

    def test_wrong_schema_raises(self, good_receipt):
        bad = dict(good_receipt, schema_version="WRONG")
        with pytest.raises(TransportComputationError):
            validate_transport_computation_receipt(bad)

    def test_false_computation_executed_raises(self, good_receipt):
        bad = dict(good_receipt, computation_executed=False)
        with pytest.raises(TransportComputationError):
            validate_transport_computation_receipt(bad)

    def test_false_all_matched_raises(self, good_receipt):
        bad = dict(good_receipt, all_matched=False)
        with pytest.raises(TransportComputationError):
            validate_transport_computation_receipt(bad)
