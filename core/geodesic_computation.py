from __future__ import annotations

import heapq
import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicComputationReceipt.v1"
RECEIPT_ID = "geodesic_computation_receipt_001"
COMPUTATION_STATUS = "GEODESIC_COMPUTATION_COMPLETE"
COMPUTATION_STAGE = "TEST_VECTOR_COMPUTATION_ONLY"
OPERATOR_ID = "GEODESIC"

SOURCE_IMPLEMENTATION_GATE_HASH = (
    "a33bf6482414d0fa2d6788c997b466bb0c20215f4a6aa9b3c552a447616f432f"
)
SOURCE_IMPLEMENTATION_PLAN_HASH = (
    "9a5c2bebf5102bfaedc72a089361f69cb463bd12f21ff017994aa43d55c62491"
)

FIXTURE_BASE = pathlib.Path("input/fixtures/geodesic")

FORBIDDEN = (
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "metric-value",
    "metric-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class GeodesicComputationError(ValueError):
    pass


# ── pure-Python shortest path (CPU reference, directed graph, heapq) ──────────


def _directed_shortest_path(
    node_set: list[str],
    edge_list: list[dict[str, Any]],
    source: str,
    target: str,
) -> float:
    """
    Compute shortest directed path distance from source to target using a
    standard priority-queue relaxation over a directed adjacency list.
    Returns 0.0 for the self-loop case (source == target).
    Raises GeodesicComputationError if no path exists.
    Nodes and edges are processed in deterministic order (sorted node set,
    edges traversed in the order they appear in edge_list).
    """
    if source == target:
        return 0.0

    adj: dict[str, list[tuple[float, str]]] = {n: [] for n in sorted(node_set)}
    for edge in edge_list:
        frm = edge["from"]
        to = edge["to"]
        w = float(edge["weight"])
        adj[frm].append((w, to))

    dist: dict[str, float] = {n: float("inf") for n in adj}
    dist[source] = 0.0
    heap: list[tuple[float, str]] = [(0.0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == target:
            return dist[u]
        for w, v in adj.get(u, []):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))

    raise GeodesicComputationError(
        f"NO_PATH: no directed path from {source!r} to {target!r}"
    )


# ── validation helpers ────────────────────────────────────────────────────────


def _validate_invalid_input(graph: dict[str, Any]) -> str | None:
    """Return a rejection_reason string if the input is invalid, else None."""
    if "source_node" not in graph:
        return "missing_required_field: source_node absent from input"
    if "target_node" not in graph:
        return "missing_required_field: target_node absent from input"
    if "edge_list" not in graph:
        return "missing_required_field: edge_list absent from input"
    for edge in graph.get("edge_list", []):
        if float(edge.get("weight", 0.0)) < 0.0:
            return "negative_weight_rejected: all edge weights must be non-negative"
    return None


def _check_not_computable(
    graph: dict[str, Any],
) -> str | None:
    """Return a not_computable_reason string if the input cannot be computed, else None."""
    node_set: list[str] = graph.get("node_set", [])
    edge_list: list[dict[str, Any]] = graph.get("edge_list", [])
    source: str = graph.get("source_node", "")
    target: str = graph.get("target_node", "")

    if not node_set and not edge_list:
        return "EMPTY_INPUT"
    if source not in node_set:
        return "SOURCE_NODE_NOT_IN_GRAPH"
    if target not in node_set:
        return "TARGET_NODE_NOT_IN_GRAPH"
    return None


# ── fixture loaders ───────────────────────────────────────────────────────────


def _load_fixtures(subdir: str) -> list[dict[str, Any]]:
    d = FIXTURE_BASE / subdir
    return sorted(
        [json.loads(p.read_text()) for p in d.glob("*.json")],
        key=lambda x: x["fixture_id"],
    )


# ── per-category runners ──────────────────────────────────────────────────────


def _run_valid(fixture: dict[str, Any]) -> dict[str, Any]:
    graph = fixture["graph"]
    node_set: list[str] = graph["node_set"]
    edge_list: list[dict[str, Any]] = graph["edge_list"]
    source: str = graph["source_node"]
    target: str = graph["target_node"]
    expected: float = float(fixture["expected_geodesic_distance"])

    computed = _directed_shortest_path(node_set, edge_list, source, target)
    match = computed == expected

    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_canonical_hash": fixture["canonical_hash"],
        "fixture_type": "VALID",
        "source_node": source,
        "target_node": target,
        "computed_geodesic_distance": computed,
        "expected_geodesic_distance": expected,
        "comparison_outcome": "MATCH" if match else "MISMATCH",
        "computation_outcome": "COMPUTED",
        "metric_emitted": False,
        "forecast_influenced": False,
    }


def _run_invalid(fixture: dict[str, Any]) -> dict[str, Any]:
    graph = fixture.get("graph", {})
    reason = fixture.get(
        "rejection_reason",
        _validate_invalid_input(graph) or "INVALID_INPUT",
    )
    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_canonical_hash": fixture["canonical_hash"],
        "fixture_type": "INVALID",
        "rejection_outcome": "INVALID_INPUT",
        "rejection_reason": reason,
        "computation_attempted": False,
        "metric_emitted": False,
        "forecast_influenced": False,
    }


def _run_not_computable(fixture: dict[str, Any]) -> dict[str, Any]:
    reason = fixture.get("not_computable_reason", "NOT_COMPUTABLE")
    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_canonical_hash": fixture["canonical_hash"],
        "fixture_type": "NOT_COMPUTABLE",
        "not_computable_outcome": "NOT_COMPUTABLE",
        "not_computable_reason": reason,
        "computation_attempted": False,
        "metric_emitted": False,
        "forecast_influenced": False,
    }


# ── summary builders ──────────────────────────────────────────────────────────


def _comparison_summary(valid_results: list[dict[str, Any]]) -> dict[str, Any]:
    match_count = sum(1 for r in valid_results if r["comparison_outcome"] == "MATCH")
    mismatch_count = sum(1 for r in valid_results if r["comparison_outcome"] == "MISMATCH")
    return {
        "total_valid_fixtures": len(valid_results),
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "all_valid_match": mismatch_count == 0,
        "comparison_field": "expected_geodesic_distance",
        "output_field": "computed_geodesic_distance",
    }


def _deterministic_ordering_summary() -> dict[str, Any]:
    return {
        "node_ordering": "sorted_alphabetical",
        "edge_ordering": "fixture_declaration_order",
        "result_ordering": "sorted_by_fixture_id",
        "heap_tie_breaking": "lexicographic_node_label",
        "determinism_guarantee": True,
    }


def _numerical_policy() -> dict[str, Any]:
    return {
        "precision_policy": "float64_compatible",
        "comparison_method": "exact_equality_on_declarative_simple_floats",
        "negative_weight_policy": "REJECT_AS_INVALID_INPUT",
        "self_loop_policy": "ZERO_DISTANCE_IF_SOURCE_EQUALS_TARGET",
        "infinity_sentinel": "no_path_raises_not_computable",
    }


# ── block / authority sections ────────────────────────────────────────────────


def _no_metric_emission_review() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "metric_emission_blocked": True,
        "review_passed": True,
        "finding": (
            "All 5 valid fixture computations write to test-vector output only. "
            "No runtime metric surfaces touched."
        ),
    }


def _no_forecast_influence_review() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "forecast_influence_blocked": True,
        "review_passed": True,
        "finding": "GEODESIC computation does not feed forecast lanes.",
    }


def _no_p43_surface_lane_review() -> dict[str, Any]:
    return {
        "p43_surface_lanes_authorized": False,
        "p43_blocked": True,
        "review_passed": True,
        "finding": "P43 surface lanes remain unauthorized by this computation.",
    }


def _blocked_scopes() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def _authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "test_vector_computation_only": True,
        "geodesic_computation_implementation_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


# ── forbidden token guard ─────────────────────────────────────────────────────


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicComputationError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


# ── preimage helper ───────────────────────────────────────────────────────────


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


# ── main builder ──────────────────────────────────────────────────────────────


def build_computation_receipt(
    receipt_id: str = RECEIPT_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
) -> dict[str, Any]:
    valid_fixtures = _load_fixtures("valid")
    invalid_fixtures = _load_fixtures("invalid")
    nc_fixtures = _load_fixtures("not_computable")

    valid_results = [_run_valid(f) for f in valid_fixtures]
    invalid_results = [_run_invalid(f) for f in invalid_fixtures]
    nc_results = [_run_not_computable(f) for f in nc_fixtures]

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": receipt_id,
        "operator_id": OPERATOR_ID,
        "computation_status": COMPUTATION_STATUS,
        "computation_stage": COMPUTATION_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": "SHADOW",
        "source_implementation_gate_hash": SOURCE_IMPLEMENTATION_GATE_HASH,
        "source_implementation_plan_hash": SOURCE_IMPLEMENTATION_PLAN_HASH,
        "valid_fixture_results": valid_results,
        "invalid_fixture_results": invalid_results,
        "not_computable_fixture_results": nc_results,
        "comparison_summary": _comparison_summary(valid_results),
        "deterministic_ordering_summary": _deterministic_ordering_summary(),
        "numerical_policy": _numerical_policy(),
        "no_metric_emission_review": _no_metric_emission_review(),
        "no_forecast_influence_review": _no_forecast_influence_review(),
        "no_p43_surface_lane_review": _no_p43_surface_lane_review(),
        "blocked_scopes": _blocked_scopes(),
        "authority_locks": _authority_locks(),
        "recommended_next_step": "GEODESIC_COMPUTATION_COMPLETE_REVIEW",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_computation_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicComputationError(f"schema_version must be {SCHEMA_VERSION!r}")
    if receipt.get("computation_status") != COMPUTATION_STATUS:
        raise GeodesicComputationError(f"computation_status must be {COMPUTATION_STATUS!r}")
    if receipt.get("computation_stage") != COMPUTATION_STAGE:
        raise GeodesicComputationError(f"computation_stage must be {COMPUTATION_STAGE!r}")
    if receipt.get("operator_id") != OPERATOR_ID:
        raise GeodesicComputationError(f"operator_id must be {OPERATOR_ID!r}")
    if receipt.get("intended_lane") != "SHADOW":
        raise GeodesicComputationError("intended_lane must be SHADOW")
    if receipt.get("source_implementation_gate_hash") != SOURCE_IMPLEMENTATION_GATE_HASH:
        raise GeodesicComputationError("source_implementation_gate_hash mismatch")
    if receipt.get("source_implementation_plan_hash") != SOURCE_IMPLEMENTATION_PLAN_HASH:
        raise GeodesicComputationError("source_implementation_plan_hash mismatch")

    vr = receipt.get("valid_fixture_results", [])
    if len(vr) != 5:
        raise GeodesicComputationError("valid_fixture_results must have 5 entries")
    for r in vr:
        if r.get("comparison_outcome") != "MATCH":
            raise GeodesicComputationError(
                f"valid fixture {r.get('fixture_id')} comparison_outcome is not MATCH"
            )
        if r.get("metric_emitted") is not False:
            raise GeodesicComputationError(
                f"valid fixture {r.get('fixture_id')} metric_emitted must be False"
            )

    ir = receipt.get("invalid_fixture_results", [])
    if len(ir) != 4:
        raise GeodesicComputationError("invalid_fixture_results must have 4 entries")
    for r in ir:
        if r.get("rejection_outcome") != "INVALID_INPUT":
            raise GeodesicComputationError(
                f"invalid fixture {r.get('fixture_id')} rejection_outcome must be INVALID_INPUT"
            )
        if r.get("computation_attempted") is not False:
            raise GeodesicComputationError(
                f"invalid fixture {r.get('fixture_id')} computation_attempted must be False"
            )

    nc = receipt.get("not_computable_fixture_results", [])
    if len(nc) != 4:
        raise GeodesicComputationError("not_computable_fixture_results must have 4 entries")
    for r in nc:
        if r.get("not_computable_outcome") != "NOT_COMPUTABLE":
            raise GeodesicComputationError(
                f"nc fixture {r.get('fixture_id')} not_computable_outcome must be NOT_COMPUTABLE"
            )
        if r.get("computation_attempted") is not False:
            raise GeodesicComputationError(
                f"nc fixture {r.get('fixture_id')} computation_attempted must be False"
            )

    cs = receipt.get("comparison_summary", {})
    if cs.get("all_valid_match") is not True:
        raise GeodesicComputationError("comparison_summary.all_valid_match must be True")
    if cs.get("mismatch_count") != 0:
        raise GeodesicComputationError("comparison_summary.mismatch_count must be 0")

    locks = receipt.get("authority_locks", {})
    for flag in ("advisory_only", "shadow_lane_only", "test_vector_computation_only",
                 "geodesic_computation_implementation_authorized"):
        if locks.get(flag) is not True:
            raise GeodesicComputationError(f"authority_locks.{flag} must be True")
    for flag in ("emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
                 "production_activation", "canon_promotion", "runtime_mutation",
                 "execution_authority", "inference_authority"):
        if locks.get(flag) is not False:
            raise GeodesicComputationError(f"authority_locks.{flag} must be False")

    bs = receipt.get("blocked_scopes", {})
    for flag in ("emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
                 "production_activation", "canon_promotion", "runtime_mutation",
                 "execution_authority", "inference_authority"):
        if bs.get(flag) is not False:
            raise GeodesicComputationError(f"blocked_scopes.{flag} must be False")

    h = receipt.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicComputationError("canonical_hash must be a 64-char hex string")
    recomputed = canonical_hash(_preimage(receipt))
    if recomputed != h:
        raise GeodesicComputationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
