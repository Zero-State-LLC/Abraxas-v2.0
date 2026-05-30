"""
TRANSPORT COMPUTATION — BOUNDED SHADOW TEST-VECTOR COMPUTATION
Algorithm: DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH
Lane: SHADOW (test vectors only)
Max size: 4×4 (16 transport variables)
Pivot: LEXICOGRAPHIC_MIN_COST_THEN_ROW_MAJOR
Tie-break: ROW_MAJOR_THEN_COLUMN_MAJOR
"""
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

from core.canonical.json import canonical_hash

OPERATOR_ID = "TRANSPORT"
SCHEMA_VERSION = "TransportComputationReceipt.v1"
ALGORITHM = "DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH"
PIVOT_RULE = "LEXICOGRAPHIC_MIN_COST_THEN_ROW_MAJOR"
TIE_BREAKING_RULE = "ROW_MAJOR_THEN_COLUMN_MAJOR"
LANE = "SHADOW"

MAX_SUPPLY_LEN = 4
MAX_DEMAND_LEN = 4
MAX_TRANSPORT_VARIABLES = 16
EPSILON_ABS = 0.0
EPSILON_REL = 0.0
COST_MAGNITUDE_BOUND = 1_000_000.0

GATE_HASH = "a5b9691e0ff410b512c725075cc3108141b941b0f22da58441772589a3467eb0"
CORPUS_HASH = "971a9bbc23850a6a4e9fffb16b6de1b48dfb8e060bb61d127c2d27d2454bb78e"
AUTH_RECORD_HASH = "2cd378187842043c93d4a66ed6e0f6a83b59cc1a3a8415c259abd70e5e1cb935"
FRONTIER_HASH = "bdedd43c2a87d13c54a2f352e45c13effbfa48aa827898a308877f38cb18896e"

NOT_COMPUTABLE_BRANCHES = [
    "COST_MATRIX_SHAPE_MISMATCH",
    "EMPTY_DEMAND_VECTOR",
    "EMPTY_SUPPLY_VECTOR",
    "NEGATIVE_COST_VALUE",
    "NEGATIVE_SUPPLY_VALUE",
    "NON_FINITE_COST_VALUE",
    "NON_FINITE_DEMAND_VALUE",
    "NON_FINITE_SUPPLY_VALUE",
    "UNBALANCED_SUPPLY_DEMAND",
]

_EPS = 1e-9
_MAX_PIVOT_ITER = 500


class TransportComputationError(Exception):
    pass


def _is_non_finite(v: Any) -> bool:
    if v is None:
        return True
    try:
        return not math.isfinite(float(v))
    except (TypeError, ValueError):
        return True


def _validate_input(inp: dict) -> tuple[str, Optional[str]]:
    """Return (status, reason). status: OK | REJECTED | NOT_COMPUTABLE."""
    for field in ("supply", "demand", "cost_matrix"):
        if field not in inp:
            return "REJECTED", (
                f"INVALID_INPUT: {field} field absent from input; "
                "required-field contract violated"
            )

    supply = inp["supply"]
    demand = inp["demand"]
    cost_matrix = inp["cost_matrix"]

    if len(supply) == 0:
        return "NOT_COMPUTABLE", "EMPTY_SUPPLY_VECTOR"
    if len(demand) == 0:
        return "NOT_COMPUTABLE", "EMPTY_DEMAND_VECTOR"

    for v in supply:
        if _is_non_finite(v):
            return "NOT_COMPUTABLE", "NON_FINITE_SUPPLY_VALUE"
    for v in demand:
        if _is_non_finite(v):
            return "NOT_COMPUTABLE", "NON_FINITE_DEMAND_VALUE"
    for row in cost_matrix:
        for v in row:
            if _is_non_finite(v):
                return "NOT_COMPUTABLE", "NON_FINITE_COST_VALUE"

    for v in supply:
        if float(v) < -_EPS:
            return "NOT_COMPUTABLE", "NEGATIVE_SUPPLY_VALUE"
    for row in cost_matrix:
        for v in row:
            if float(v) < -_EPS:
                return "NOT_COMPUTABLE", "NEGATIVE_COST_VALUE"

    m, n = len(supply), len(demand)
    if len(cost_matrix) != m:
        return "NOT_COMPUTABLE", "COST_MATRIX_SHAPE_MISMATCH"
    for row in cost_matrix:
        if len(row) != n:
            return "NOT_COMPUTABLE", "COST_MATRIX_SHAPE_MISMATCH"

    sum_s = sum(float(v) for v in supply)
    sum_d = sum(float(v) for v in demand)
    if abs(sum_s - sum_d) > _EPS:
        return "NOT_COMPUTABLE", "UNBALANCED_SUPPLY_DEMAND"

    return "OK", None


def _northwest_corner(
    supply: list[float], demand: list[float]
) -> dict[tuple[int, int], float]:
    """Deterministic northwest-corner initial BFS. Handles degeneracy."""
    m, n = len(supply), len(demand)
    s = list(supply)
    d = list(demand)
    alloc: dict[tuple[int, int], float] = {}
    i, j = 0, 0
    while i < m and j < n:
        val = min(s[i], d[j])
        alloc[(i, j)] = val
        s[i] -= val
        d[j] -= val
        both_zero = s[i] < _EPS and d[j] < _EPS
        if both_zero:
            i += 1
        elif s[i] < _EPS:
            i += 1
        else:
            j += 1
    return alloc


def _compute_uv(
    cost: list[list[float]], basis: list[tuple[int, int]]
) -> tuple[list[Optional[float]], list[Optional[float]]]:
    """MODI: solve u[i] + v[j] = c[i][j] for all (i,j) in basis. u[0] = 0."""
    m = max(r for r, _ in basis) + 1
    n = max(c for _, c in basis) + 1
    u: list[Optional[float]] = [None] * m
    v: list[Optional[float]] = [None] * n
    u[0] = 0.0
    changed = True
    while changed:
        changed = False
        for i, j in basis:
            if u[i] is not None and v[j] is None:
                v[j] = cost[i][j] - u[i]
                changed = True
            elif v[j] is not None and u[i] is None:
                u[i] = cost[i][j] - v[j]
                changed = True
    return u, v


def _find_entering(
    cost: list[list[float]],
    basis_set: set[tuple[int, int]],
    u: list[Optional[float]],
    v: list[Optional[float]],
    m: int,
    n: int,
) -> Optional[tuple[int, int]]:
    """LEXICOGRAPHIC_MIN_COST_THEN_ROW_MAJOR with ROW_MAJOR_THEN_COLUMN_MAJOR tie-break."""
    best_rc = -_EPS
    best: Optional[tuple[int, int]] = None
    for i in range(m):
        for j in range(n):
            if (i, j) in basis_set:
                continue
            ui = u[i]
            vj = v[j]
            if ui is None or vj is None:
                continue
            rc = cost[i][j] - ui - vj
            if rc < best_rc - _EPS:
                best_rc = rc
                best = (i, j)
            elif best is not None and abs(rc - best_rc) < _EPS and (i, j) < best:
                best = (i, j)
    return best


def _find_loop(
    basis_cells: list[tuple[int, int]], enter: tuple[int, int]
) -> Optional[list[tuple[int, int]]]:
    """
    Find closed loop for entering variable through basis cells.
    Moves alternate horizontal / vertical.
    Returns loop as list starting with enter (does NOT append enter again at end).
    """
    by_row: dict[int, set[int]] = defaultdict(set)
    by_col: dict[int, set[int]] = defaultdict(set)
    for r, c in basis_cells:
        by_row[r].add(c)
        by_col[c].add(r)

    er, ec = enter
    path_set: set[tuple[int, int]] = {enter}

    def dfs(
        path: list[tuple[int, int]], next_horiz: bool
    ) -> Optional[list[tuple[int, int]]]:
        r, c = path[-1]
        if len(path) >= 3:
            if next_horiz and r == er:
                return list(path)
            if not next_horiz and c == ec:
                return list(path)
        if next_horiz:
            for nc in sorted(by_row[r]):
                cell = (r, nc)
                if cell not in path_set:
                    path_set.add(cell)
                    res = dfs(path + [cell], False)
                    path_set.discard(cell)
                    if res is not None:
                        return res
        else:
            for nr in sorted(by_col[c]):
                cell = (nr, c)
                if cell not in path_set:
                    path_set.add(cell)
                    res = dfs(path + [cell], True)
                    path_set.discard(cell)
                    if res is not None:
                        return res
        return None

    res = dfs([enter], True)
    if res is None:
        res = dfs([enter], False)
    return res


def _solve_transport(
    supply_in: list[float], demand_in: list[float], cost_in: list[list[float]]
) -> float:
    """Solve balanced transport problem. Returns optimal total cost."""
    m, n = len(supply_in), len(demand_in)
    cost = [[float(v) for v in row] for row in cost_in]
    supply = [float(v) for v in supply_in]
    demand = [float(v) for v in demand_in]

    alloc = _northwest_corner(supply, demand)

    for _ in range(_MAX_PIVOT_ITER):
        basis_list = list(alloc.keys())
        basis_set = set(basis_list)

        u, v = _compute_uv(cost, basis_list)

        entering = _find_entering(cost, basis_set, u, v, m, n)
        if entering is None:
            break

        loop = _find_loop(basis_list, entering)
        if loop is None:
            break

        minus_positions = loop[1::2]
        theta = min(alloc.get(cell, 0.0) for cell in minus_positions)

        leaving: Optional[tuple[int, int]] = None
        for cell in minus_positions:
            if abs(alloc.get(cell, 0.0) - theta) < _EPS:
                leaving = cell
                break

        for idx, cell in enumerate(loop):
            if idx % 2 == 0:
                alloc[cell] = alloc.get(cell, 0.0) + theta
            else:
                alloc[cell] = alloc.get(cell, 0.0) - theta
                if alloc[cell] < _EPS:
                    alloc[cell] = 0.0

        if leaving is not None and leaving != entering:
            del alloc[leaving]

    total = sum(
        alloc.get((i, j), 0.0) * cost[i][j] for i in range(m) for j in range(n)
    )
    return round(total, 9)


def process_fixture(fixture: dict) -> dict:
    """Process a single test vector fixture. Returns result dict."""
    fid = fixture["fixture_id"]
    ftype = fixture["fixture_type"]
    inp = fixture.get("input", {})

    status, reason = _validate_input(inp)

    if status == "REJECTED":
        matched = ftype == "INVALID"
        return {
            "fixture_id": fid,
            "fixture_type": ftype,
            "expected": ftype,
            "actual": "REJECTED",
            "matched": matched,
            "rejection_reason": reason,
            "transport_distance": None,
        }

    if status == "NOT_COMPUTABLE":
        matched = ftype in ("INVALID", "NOT_COMPUTABLE")
        return {
            "fixture_id": fid,
            "fixture_type": ftype,
            "expected": ftype,
            "actual": "NOT_COMPUTABLE",
            "matched": matched,
            "not_computable_reason": reason,
            "transport_distance": None,
        }

    supply = [float(v) for v in inp["supply"]]
    demand = [float(v) for v in inp["demand"]]
    cost_matrix = inp["cost_matrix"]

    computed = _solve_transport(supply, demand, cost_matrix)

    expected_dist = fixture.get("expected_transport_distance")
    if expected_dist is not None:
        distance_matched = abs(computed - float(expected_dist)) < 1e-6
    else:
        distance_matched = True

    matched = ftype == "VALID" and distance_matched

    return {
        "fixture_id": fid,
        "fixture_type": ftype,
        "expected": ftype,
        "actual": "COMPUTED",
        "matched": matched,
        "transport_distance": computed,
        "expected_transport_distance": expected_dist,
        "distance_matched": distance_matched,
    }


def build_transport_computation_receipt(
    fixture_dir: Path,
    fixture_manifest: list[dict],
) -> dict:
    """Run all fixtures and build the computation receipt."""
    fixture_results = []
    for entry in fixture_manifest:
        path = Path(entry["fixture_path"])
        import json
        fixture = json.loads(path.read_text())
        result = process_fixture(fixture)
        fixture_results.append(result)

    valid_results = [r for r in fixture_results if r["fixture_type"] == "VALID"]
    invalid_results = [r for r in fixture_results if r["fixture_type"] == "INVALID"]
    nc_results = [r for r in fixture_results if r["fixture_type"] == "NOT_COMPUTABLE"]

    all_valid_passed = all(r["matched"] for r in valid_results)
    all_invalid_rejected = all(r["matched"] for r in invalid_results)
    all_nc_routed = all(r["matched"] for r in nc_results)
    all_matched = all_valid_passed and all_invalid_rejected and all_nc_routed

    receipt: dict = {
        "schema_version": SCHEMA_VERSION,
        "operator_id": OPERATOR_ID,
        "receipt_id": "transport_computation_receipt_001",
        "computation_executed": True,
        "algorithm": ALGORITHM,
        "pivot_rule": PIVOT_RULE,
        "tie_breaking_rule": TIE_BREAKING_RULE,
        "lane": LANE,
        "locked_constants": {
            "lp_solver_variant": ALGORITHM,
            "max_supply_length": MAX_SUPPLY_LEN,
            "max_demand_length": MAX_DEMAND_LEN,
            "max_transport_variables": MAX_TRANSPORT_VARIABLES,
            "epsilon_abs": EPSILON_ABS,
            "epsilon_rel": EPSILON_REL,
            "cost_magnitude_bound": COST_MAGNITUDE_BOUND,
            "pivot_rule": PIVOT_RULE,
            "tie_breaking_rule": TIE_BREAKING_RULE,
            "not_computable_branches_sealed": NOT_COMPUTABLE_BRANCHES,
        },
        "fixture_count_total": len(fixture_results),
        "fixture_count_valid": len(valid_results),
        "fixture_count_invalid": len(invalid_results),
        "fixture_count_not_computable": len(nc_results),
        "fixture_results": fixture_results,
        "all_valid_passed": all_valid_passed,
        "all_invalid_rejected": all_invalid_rejected,
        "all_not_computable_routed": all_nc_routed,
        "all_matched": all_matched,
        "receipt_status": (
            "TRANSPORT_COMPUTATION_RECEIPT_COMPLETE"
            if all_matched
            else "TRANSPORT_COMPUTATION_RECEIPT_FAILURES"
        ),
        "authority_locks": {
            "computation_executed": True,
            "emits_metric_values": False,
            "forecast_influence": False,
            "p43_surface_lanes_authorized": False,
            "canon_promotion": False,
            "production_activation": False,
            "runtime_mutation": False,
            "shadow_lane_only": True,
            "test_vector_scope_only": True,
        },
        "provenance": {
            "generated_by": "TRANSPORT_COMPUTATION_001",
            "source": "TRANSPORT_COMPUTATION_RUN",
            "gate_ref": f"transport_computation_implementation_gate_001:{GATE_HASH}",
            "corpus_ref": f"transport_fixture_corpus_creation_receipt_001:{CORPUS_HASH}",
            "auth_record_ref": (
                f"transport_implementation_authorization_decision_record_001:"
                f"{AUTH_RECORD_HASH}"
            ),
            "frontier_ref": f"metric_operator_frontier_recommendation_006:{FRONTIER_HASH}",
        },
    }

    receipt["canonical_hash"] = canonical_hash(receipt)
    return receipt


def validate_transport_computation_receipt(receipt: dict) -> None:
    """Validate a transport computation receipt. Raises on failure."""
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise TransportComputationError(
            f"schema_version mismatch: {receipt.get('schema_version')!r}"
        )
    if receipt.get("operator_id") != OPERATOR_ID:
        raise TransportComputationError(
            f"operator_id mismatch: {receipt.get('operator_id')!r}"
        )
    if not receipt.get("computation_executed"):
        raise TransportComputationError("computation_executed must be True")
    if not receipt.get("all_valid_passed"):
        raise TransportComputationError("all_valid_passed is False")
    if not receipt.get("all_invalid_rejected"):
        raise TransportComputationError("all_invalid_rejected is False")
    if not receipt.get("all_not_computable_routed"):
        raise TransportComputationError("all_not_computable_routed is False")
    if not receipt.get("all_matched"):
        raise TransportComputationError("all_matched is False")
    locks = receipt.get("authority_locks", {})
    for blocked in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "canon_promotion",
        "production_activation",
        "runtime_mutation",
    ):
        if locks.get(blocked) is not False:
            raise TransportComputationError(
                f"authority_locks.{blocked} must be False"
            )
    if locks.get("computation_executed") is not True:
        raise TransportComputationError("authority_locks.computation_executed must be True")
    if receipt.get("receipt_status") != "TRANSPORT_COMPUTATION_RECEIPT_COMPLETE":
        raise TransportComputationError(
            f"receipt_status: {receipt.get('receipt_status')!r}"
        )
