"""Deterministic replay dependency graph primitives for ABRAXAS v2.0.

PATCH-P12-REPLAY-SCALING-AND-INCREMENTAL-EXECUTION-001

Advisory/planning-only.  No runtime mutation authority.

Hard posture:
  authority_granted  = False
  mutation_allowed   = False
  promotion_allowed  = False
"""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

PATCH_ID = "PATCH-P12-REPLAY-SCALING-AND-INCREMENTAL-EXECUTION-001"

# ---------------------------------------------------------------------------
# ReplayNode.v1 — single artifact in the dependency graph
# ---------------------------------------------------------------------------


def build_replay_node(
    *,
    node_id: str,
    artifact_path: str,
    content_hash: str,
    dependencies: list[str] | None = None,
    replay_surface: str = "",
    chunk_id: str = "",
) -> dict[str, Any]:
    """Build a ReplayNode.v1 packet representing one artifact in the graph.

    Immutable.  Does not mutate runtime state.
    """
    deps: list[str] = sorted(dependencies) if dependencies else []
    return {
        "schema": "ReplayNode.v1",
        "patch_id": PATCH_ID,
        "node_id": node_id,
        "artifact_path": artifact_path,
        "content_hash": content_hash,
        "dependencies": deps,
        "replay_surface": replay_surface,
        "chunk_id": chunk_id,
    }


# ---------------------------------------------------------------------------
# ReplayDependencyGraph.v1
# ---------------------------------------------------------------------------


def build_replay_graph(
    *,
    graph_id: str,
    nodes: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a ReplayDependencyGraph.v1 from a list of ReplayNode.v1 packets.

    Deterministically orders nodes by node_id for stable traversal.
    Advisory/planning-only.  Does not mutate runtime state.
    """
    sorted_nodes = sorted(nodes, key=lambda n: n["node_id"])
    node_ids = [n["node_id"] for n in sorted_nodes]

    graph_hash = canonical_hash(
        {
            "graph_id": graph_id,
            "node_ids": node_ids,
            "node_hashes": {n["node_id"]: n["content_hash"] for n in sorted_nodes},
        }
    )

    # Build adjacency index: node_id -> list of dependency node_ids
    adjacency: dict[str, list[str]] = {
        n["node_id"]: sorted(n.get("dependencies", [])) for n in sorted_nodes
    }

    return {
        "schema": "ReplayDependencyGraph.v1",
        "patch_id": PATCH_ID,
        "graph_id": graph_id,
        "node_count": len(sorted_nodes),
        "nodes": sorted_nodes,
        "adjacency": adjacency,
        "traversal_order": node_ids,
        "graph_hash": graph_hash,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


# ---------------------------------------------------------------------------
# Replay chunk partitioning
# ---------------------------------------------------------------------------


def partition_into_chunks(
    graph: dict[str, Any],
    *,
    chunk_size: int = 10,
) -> list[dict[str, Any]]:
    """Partition the graph traversal order into deterministic replay chunks.

    Chunks are purely advisory — they describe which nodes to replay together.
    Does not mutate runtime state.
    """
    traversal_order: list[str] = graph["traversal_order"]
    chunks: list[dict[str, Any]] = []

    for i in range(0, len(traversal_order), chunk_size):
        chunk_nodes = traversal_order[i : i + chunk_size]
        chunk_id = f"chunk_{i // chunk_size:04d}"
        chunk_hash = canonical_hash(
            {
                "chunk_id": chunk_id,
                "graph_id": graph["graph_id"],
                "node_ids": chunk_nodes,
            }
        )
        chunks.append(
            {
                "chunk_id": chunk_id,
                "node_ids": chunk_nodes,
                "node_count": len(chunk_nodes),
                "chunk_hash": chunk_hash,
            }
        )

    return chunks


# ---------------------------------------------------------------------------
# Invalidation lineage
# ---------------------------------------------------------------------------


def compute_invalidation_lineage(
    graph: dict[str, Any],
    *,
    changed_node_ids: list[str],
) -> dict[str, Any]:
    """Compute which nodes are invalidated by the changed node set.

    A node is invalidated if:
    - it is in the changed set, OR
    - any of its transitive dependents (nodes that depend on it) appear in the
      changed set.

    Fail-closed: if the graph is malformed or a dependency reference is not
    found in the graph node set, all nodes are treated as invalidated.

    Returns a deterministic InvalidationLineage.v1 packet.
    """
    adjacency: dict[str, list[str]] = graph.get("adjacency", {})
    all_node_ids: list[str] = graph.get("traversal_order", [])
    all_node_set = frozenset(all_node_ids)

    changed = frozenset(changed_node_ids)

    # Build reverse adjacency: node_id -> list of nodes that depend on it
    reverse_adj: dict[str, list[str]] = {nid: [] for nid in all_node_ids}
    for nid, deps in adjacency.items():
        for dep in deps:
            if dep not in all_node_set:
                # Dependency references unknown node — fail closed
                return _invalidation_all(
                    graph, changed_node_ids, reason="unknown_dependency"
                )
            reverse_adj[dep].append(nid)

    # BFS from changed nodes through reverse adjacency
    invalidated: set[str] = set(changed)
    queue = list(changed)
    while queue:
        current = queue.pop()
        for dependent in reverse_adj.get(current, []):
            if dependent not in invalidated:
                invalidated.add(dependent)
                queue.append(dependent)

    invalidated_sorted = sorted(invalidated)
    safe_sorted = sorted(all_node_set - invalidated)

    lineage_hash = canonical_hash(
        {
            "graph_id": graph["graph_id"],
            "changed_node_ids": sorted(changed_node_ids),
            "invalidated_nodes": invalidated_sorted,
        }
    )

    return {
        "schema": "InvalidationLineage.v1",
        "patch_id": PATCH_ID,
        "graph_id": graph["graph_id"],
        "changed_node_ids": sorted(changed_node_ids),
        "invalidated_nodes": invalidated_sorted,
        "safe_nodes": safe_sorted,
        "invalidation_count": len(invalidated_sorted),
        "safe_count": len(safe_sorted),
        "fail_closed": False,
        "lineage_hash": lineage_hash,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


def _invalidation_all(
    graph: dict[str, Any],
    changed_node_ids: list[str],
    *,
    reason: str,
) -> dict[str, Any]:
    """Fail-closed fallback: mark all nodes as invalidated."""
    all_node_ids: list[str] = graph.get("traversal_order", [])
    lineage_hash = canonical_hash(
        {
            "graph_id": graph["graph_id"],
            "changed_node_ids": sorted(changed_node_ids),
            "invalidated_nodes": sorted(all_node_ids),
            "fail_closed": True,
        }
    )
    return {
        "schema": "InvalidationLineage.v1",
        "patch_id": PATCH_ID,
        "graph_id": graph["graph_id"],
        "changed_node_ids": sorted(changed_node_ids),
        "invalidated_nodes": sorted(all_node_ids),
        "safe_nodes": [],
        "invalidation_count": len(all_node_ids),
        "safe_count": 0,
        "fail_closed": True,
        "fail_closed_reason": reason,
        "lineage_hash": lineage_hash,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


# ---------------------------------------------------------------------------
# Graph stability verification
# ---------------------------------------------------------------------------


def verify_graph_stability(
    graph_a: dict[str, Any],
    graph_b: dict[str, Any],
) -> dict[str, Any]:
    """Verify that two replay graphs produce identical graph hashes.

    Proves that identical inputs yield identical graph structure.
    Advisory-only.  Does not mutate runtime state.
    """
    hash_a = graph_a.get("graph_hash", "")
    hash_b = graph_b.get("graph_hash", "")
    stable = bool(hash_a) and hash_a == hash_b

    return {
        "schema": "GraphStabilityVerification.v1",
        "patch_id": PATCH_ID,
        "graph_id_a": graph_a.get("graph_id", ""),
        "graph_id_b": graph_b.get("graph_id", ""),
        "graph_hash_a": hash_a,
        "graph_hash_b": hash_b,
        "stable": stable,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }
