"""Deterministic tests for replay dependency graph primitives.

PATCH-P12-REPLAY-SCALING-AND-INCREMENTAL-EXECUTION-001

Proves:
- ReplayNode.v1 packet shape stability
- ReplayDependencyGraph.v1 deterministic construction
- graph hash is stable for identical inputs
- chunk partitioning deterministic
- invalidation lineage: direct and transitive
- invalidation fails closed on unknown dependency
- graph stability verification
- all authority flags always False
"""

from __future__ import annotations

from typing import Any

from core.replay_graph import (
    PATCH_ID,
    build_replay_graph,
    build_replay_node,
    compute_invalidation_lineage,
    partition_into_chunks,
    verify_graph_stability,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _node(
    node_id: str,
    artifact_path: str = "out/artifact.json",
    content_hash: str = "abc123",
    dependencies: list[str] | None = None,
) -> dict[str, Any]:
    return build_replay_node(
        node_id=node_id,
        artifact_path=artifact_path,
        content_hash=content_hash,
        dependencies=dependencies,
        replay_surface="test_surface",
    )


def _simple_graph() -> dict[str, Any]:
    """Build a simple linear dependency graph: A -> B -> C."""
    nodes = [
        _node("node_a", dependencies=[]),
        _node("node_b", dependencies=["node_a"]),
        _node("node_c", dependencies=["node_b"]),
    ]
    return build_replay_graph(graph_id="test_graph", nodes=nodes)


def _diamond_graph() -> dict[str, Any]:
    """Build a diamond dependency graph: A -> B, A -> C, B -> D, C -> D."""
    nodes = [
        _node("node_a", dependencies=[]),
        _node("node_b", dependencies=["node_a"]),
        _node("node_c", dependencies=["node_a"]),
        _node("node_d", dependencies=["node_b", "node_c"]),
    ]
    return build_replay_graph(graph_id="diamond_graph", nodes=nodes)


# ---------------------------------------------------------------------------
# ReplayNode.v1 — packet shape
# ---------------------------------------------------------------------------


def test_replay_node_schema_present() -> None:
    node = _node("n1")
    assert node["schema"] == "ReplayNode.v1"


def test_replay_node_patch_id() -> None:
    node = _node("n1")
    assert node["patch_id"] == PATCH_ID


def test_replay_node_authority_flags_all_false() -> None:
    node = _node("n1")
    assert "authority_granted" not in node
    assert "mutation_allowed" not in node


def test_replay_node_dependencies_sorted() -> None:
    node = build_replay_node(
        node_id="n1",
        artifact_path="p",
        content_hash="h",
        dependencies=["node_z", "node_a", "node_m"],
    )
    assert node["dependencies"] == ["node_a", "node_m", "node_z"]


def test_replay_node_empty_dependencies_default() -> None:
    node = _node("n1")
    assert node["dependencies"] == []


# ---------------------------------------------------------------------------
# ReplayDependencyGraph.v1 — construction and determinism
# ---------------------------------------------------------------------------


def test_graph_schema_present() -> None:
    g = _simple_graph()
    assert g["schema"] == "ReplayDependencyGraph.v1"


def test_graph_patch_id() -> None:
    g = _simple_graph()
    assert g["patch_id"] == PATCH_ID


def test_graph_authority_flags_all_false() -> None:
    g = _simple_graph()
    assert g["authority_granted"] is False
    assert g["mutation_allowed"] is False
    assert g["promotion_allowed"] is False


def test_graph_node_count() -> None:
    g = _simple_graph()
    assert g["node_count"] == 3


def test_graph_traversal_order_deterministic() -> None:
    """Traversal order must be sorted by node_id."""
    g = _simple_graph()
    assert g["traversal_order"] == ["node_a", "node_b", "node_c"]


def test_graph_hash_stable_for_identical_inputs() -> None:
    g_a = _simple_graph()
    g_b = _simple_graph()
    assert g_a["graph_hash"] == g_b["graph_hash"]


def test_graph_hash_changes_with_different_node_hashes() -> None:
    nodes_a = [_node("node_a", content_hash="hash1")]
    nodes_b = [_node("node_a", content_hash="hash2")]
    g_a = build_replay_graph(graph_id="g", nodes=nodes_a)
    g_b = build_replay_graph(graph_id="g", nodes=nodes_b)
    assert g_a["graph_hash"] != g_b["graph_hash"]


def test_graph_adjacency_structure() -> None:
    g = _simple_graph()
    adj = g["adjacency"]
    assert adj["node_a"] == []
    assert adj["node_b"] == ["node_a"]
    assert adj["node_c"] == ["node_b"]


def test_graph_unsorted_input_nodes_produce_sorted_traversal() -> None:
    """Input nodes in reverse order must still yield sorted traversal_order."""
    nodes = [
        _node("node_c"),
        _node("node_a"),
        _node("node_b"),
    ]
    g = build_replay_graph(graph_id="g", nodes=nodes)
    assert g["traversal_order"] == ["node_a", "node_b", "node_c"]


# ---------------------------------------------------------------------------
# Chunk partitioning — determinism
# ---------------------------------------------------------------------------


def test_chunks_partition_all_nodes() -> None:
    g = _simple_graph()
    chunks = partition_into_chunks(g, chunk_size=2)
    all_node_ids = [nid for chunk in chunks for nid in chunk["node_ids"]]
    assert sorted(all_node_ids) == sorted(g["traversal_order"])


def test_chunks_respect_chunk_size() -> None:
    nodes = [_node(f"node_{i:02d}") for i in range(7)]
    g = build_replay_graph(graph_id="g", nodes=nodes)
    chunks = partition_into_chunks(g, chunk_size=3)
    assert len(chunks) == 3  # ceil(7/3) = 3
    assert chunks[0]["node_count"] == 3
    assert chunks[1]["node_count"] == 3
    assert chunks[2]["node_count"] == 1


def test_chunks_hash_deterministic() -> None:
    g = _simple_graph()
    chunks_a = partition_into_chunks(g, chunk_size=2)
    chunks_b = partition_into_chunks(g, chunk_size=2)
    assert [c["chunk_hash"] for c in chunks_a] == [c["chunk_hash"] for c in chunks_b]


def test_chunks_empty_graph_produces_no_chunks() -> None:
    g = build_replay_graph(graph_id="empty", nodes=[])
    chunks = partition_into_chunks(g)
    assert chunks == []


# ---------------------------------------------------------------------------
# Invalidation lineage — direct
# ---------------------------------------------------------------------------


def test_invalidation_includes_changed_node() -> None:
    g = _simple_graph()
    lineage = compute_invalidation_lineage(g, changed_node_ids=["node_a"])
    assert "node_a" in lineage["invalidated_nodes"]


def test_invalidation_schema_present() -> None:
    g = _simple_graph()
    lineage = compute_invalidation_lineage(g, changed_node_ids=["node_a"])
    assert lineage["schema"] == "InvalidationLineage.v1"


def test_invalidation_authority_flags_all_false() -> None:
    g = _simple_graph()
    lineage = compute_invalidation_lineage(g, changed_node_ids=["node_a"])
    assert lineage["authority_granted"] is False
    assert lineage["mutation_allowed"] is False
    assert lineage["promotion_allowed"] is False


def test_invalidation_leaf_node_only_invalidates_itself() -> None:
    """Changing a leaf node with no dependents should only invalidate itself."""
    g = _simple_graph()
    lineage = compute_invalidation_lineage(g, changed_node_ids=["node_c"])
    assert lineage["invalidated_nodes"] == ["node_c"]
    assert sorted(lineage["safe_nodes"]) == ["node_a", "node_b"]


def test_invalidation_root_node_invalidates_all() -> None:
    """Changing the root node (all others depend on it transitively) invalidates all."""
    g = _simple_graph()
    lineage = compute_invalidation_lineage(g, changed_node_ids=["node_a"])
    assert sorted(lineage["invalidated_nodes"]) == ["node_a", "node_b", "node_c"]
    assert lineage["safe_nodes"] == []


# ---------------------------------------------------------------------------
# Invalidation lineage — transitive (diamond)
# ---------------------------------------------------------------------------


def test_invalidation_transitive_diamond_root() -> None:
    g = _diamond_graph()
    lineage = compute_invalidation_lineage(g, changed_node_ids=["node_a"])
    assert sorted(lineage["invalidated_nodes"]) == [
        "node_a",
        "node_b",
        "node_c",
        "node_d",
    ]


def test_invalidation_transitive_diamond_middle() -> None:
    g = _diamond_graph()
    lineage = compute_invalidation_lineage(g, changed_node_ids=["node_b"])
    assert "node_b" in lineage["invalidated_nodes"]
    assert "node_d" in lineage["invalidated_nodes"]
    assert "node_a" in lineage["safe_nodes"]
    assert "node_c" in lineage["safe_nodes"]


# ---------------------------------------------------------------------------
# Invalidation fail-closed
# ---------------------------------------------------------------------------


def test_invalidation_fail_closed_on_unknown_dependency() -> None:
    """A dependency reference to an unknown node must fail closed."""
    nodes = [
        _node("node_a", dependencies=["node_unknown"]),
    ]
    g = build_replay_graph(graph_id="bad_graph", nodes=nodes)
    lineage = compute_invalidation_lineage(g, changed_node_ids=["node_a"])
    assert lineage["fail_closed"] is True
    assert sorted(lineage["invalidated_nodes"]) == sorted(g["traversal_order"])
    assert lineage["safe_nodes"] == []


def test_invalidation_fail_closed_is_deterministic() -> None:
    nodes = [_node("node_a", dependencies=["node_missing"])]
    g = build_replay_graph(graph_id="bg", nodes=nodes)
    lin_a = compute_invalidation_lineage(g, changed_node_ids=["node_a"])
    lin_b = compute_invalidation_lineage(g, changed_node_ids=["node_a"])
    assert lin_a["lineage_hash"] == lin_b["lineage_hash"]


# ---------------------------------------------------------------------------
# Invalidation lineage hash determinism
# ---------------------------------------------------------------------------


def test_invalidation_lineage_hash_deterministic() -> None:
    g = _simple_graph()
    lin_a = compute_invalidation_lineage(g, changed_node_ids=["node_b"])
    lin_b = compute_invalidation_lineage(g, changed_node_ids=["node_b"])
    assert lin_a["lineage_hash"] == lin_b["lineage_hash"]


def test_invalidation_lineage_hash_differs_for_different_changes() -> None:
    g = _simple_graph()
    lin_a = compute_invalidation_lineage(g, changed_node_ids=["node_b"])
    lin_b = compute_invalidation_lineage(g, changed_node_ids=["node_c"])
    assert lin_a["lineage_hash"] != lin_b["lineage_hash"]


# ---------------------------------------------------------------------------
# Graph stability verification
# ---------------------------------------------------------------------------


def test_verify_graph_stability_same_graph() -> None:
    g_a = _simple_graph()
    g_b = _simple_graph()
    result = verify_graph_stability(g_a, g_b)
    assert result["schema"] == "GraphStabilityVerification.v1"
    assert result["stable"] is True
    assert result["graph_hash_a"] == result["graph_hash_b"]


def test_verify_graph_stability_different_graphs() -> None:
    g_a = _simple_graph()
    nodes_b = [_node("node_a", content_hash="different")]
    g_b = build_replay_graph(graph_id="test_graph", nodes=nodes_b)
    result = verify_graph_stability(g_a, g_b)
    assert result["stable"] is False


def test_verify_graph_stability_authority_flags_false() -> None:
    g = _simple_graph()
    result = verify_graph_stability(g, g)
    assert result["authority_granted"] is False
    assert result["mutation_allowed"] is False
    assert result["promotion_allowed"] is False


def test_verify_graph_stability_empty_hashes_not_stable() -> None:
    """Two graphs with empty hashes must not be considered stable."""
    g_a: dict[str, Any] = {"graph_id": "a", "graph_hash": ""}
    g_b: dict[str, Any] = {"graph_id": "b", "graph_hash": ""}
    result = verify_graph_stability(g_a, g_b)
    assert result["stable"] is False
