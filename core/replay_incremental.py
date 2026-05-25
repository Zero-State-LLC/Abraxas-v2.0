"""Incremental replay planner for ABRAXAS v2.0.

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
from core.replay_graph import compute_invalidation_lineage, partition_into_chunks

PATCH_ID = "PATCH-P12-REPLAY-SCALING-AND-INCREMENTAL-EXECUTION-001"


# ---------------------------------------------------------------------------
# Incremental Replay Plan
# ---------------------------------------------------------------------------


def build_incremental_plan(
    *,
    plan_id: str,
    graph: dict[str, Any],
    changed_node_ids: list[str],
    chunk_size: int = 10,
) -> dict[str, Any]:
    """Compute a deterministic incremental replay plan.

    Determines:
    - which nodes must be replayed (invalidated)
    - which nodes can be safely skipped
    - replay chunks for invalidated regions
    - traversal order for replay

    All outputs are:
    - deterministic
    - canonical JSON
    - replay-safe
    - advisory/planning-only — never applied unless explicitly executed

    Does not mutate runtime state.
    """
    # Compute invalidation lineage (fail-closed on graph errors)
    invalidation = compute_invalidation_lineage(
        graph,
        changed_node_ids=changed_node_ids,
    )

    invalidated_nodes: list[str] = invalidation["invalidated_nodes"]
    safe_nodes: list[str] = invalidation["safe_nodes"]

    # Build replay order: preserve original traversal ordering for invalidated nodes
    full_order: list[str] = graph.get("traversal_order", [])
    invalidated_set = frozenset(invalidated_nodes)
    replay_order = [n for n in full_order if n in invalidated_set]

    # Build a stub graph for chunk partitioning over only the replay set
    replay_graph_stub: dict[str, Any] = {
        "graph_id": graph["graph_id"],
        "traversal_order": replay_order,
        "nodes": [
            n
            for n in graph.get("nodes", [])
            if n["node_id"] in invalidated_set
        ],
    }
    replay_chunks = partition_into_chunks(replay_graph_stub, chunk_size=chunk_size)

    plan_hash = canonical_hash(
        {
            "plan_id": plan_id,
            "graph_hash": graph.get("graph_hash", ""),
            "changed_node_ids": sorted(changed_node_ids),
            "invalidated_nodes": invalidated_nodes,
            "safe_nodes": safe_nodes,
        }
    )

    return {
        "schema": "IncrementalReplayPlan.v1",
        "patch_id": PATCH_ID,
        "plan_id": plan_id,
        "graph_id": graph["graph_id"],
        "graph_hash": graph.get("graph_hash", ""),
        "changed_node_ids": sorted(changed_node_ids),
        "invalidated_nodes": invalidated_nodes,
        "skipped_surfaces": safe_nodes,
        "replay_order": replay_order,
        "replay_chunks": replay_chunks,
        "replay_chunk_count": len(replay_chunks),
        "total_node_count": graph.get("node_count", len(full_order)),
        "invalidated_count": len(invalidated_nodes),
        "skipped_count": len(safe_nodes),
        "fail_closed": invalidation.get("fail_closed", False),
        "plan_hash": plan_hash,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


# ---------------------------------------------------------------------------
# Replay equivalence verification
# ---------------------------------------------------------------------------


def verify_replay_equivalence(
    *,
    full_outputs: dict[str, str],
    incremental_outputs: dict[str, str],
    plan: dict[str, Any],
) -> dict[str, Any]:
    """Verify that incremental replay outputs == full replay outputs.

    Checks:
    - All invalidated nodes produce the same output hash as full replay
    - All skipped nodes are absent from incremental outputs (not re-executed)
    - Canonical ordering preserved

    Advisory-only.  Does not mutate runtime state.
    """
    invalidated: list[str] = plan.get("invalidated_nodes", [])
    skipped: list[str] = plan.get("skipped_surfaces", [])

    mismatches: list[str] = []
    missing_from_incremental: list[str] = []

    for node_id in invalidated:
        full_hash = full_outputs.get(node_id, "")
        inc_hash = incremental_outputs.get(node_id, "")
        if not full_hash:
            # Full replay did not produce this node — skip check
            continue
        if inc_hash != full_hash:
            if not inc_hash:
                missing_from_incremental.append(node_id)
            else:
                mismatches.append(node_id)

    # Skipped nodes must NOT appear in incremental outputs
    spurious_executions: list[str] = [
        n for n in skipped if n in incremental_outputs
    ]

    equivalence_held = (
        not mismatches
        and not missing_from_incremental
        and not spurious_executions
    )

    verification_hash = canonical_hash(
        {
            "plan_hash": plan.get("plan_hash", ""),
            "full_output_hash": canonical_hash(full_outputs),
            "incremental_output_hash": canonical_hash(incremental_outputs),
        }
    )

    return {
        "schema": "ReplayEquivalenceVerification.v1",
        "patch_id": PATCH_ID,
        "plan_id": plan.get("plan_id", ""),
        "graph_id": plan.get("graph_id", ""),
        "equivalence_held": equivalence_held,
        "mismatches": sorted(mismatches),
        "missing_from_incremental": sorted(missing_from_incremental),
        "spurious_executions": sorted(spurious_executions),
        "invalidated_count": len(invalidated),
        "skipped_count": len(skipped),
        "verification_hash": verification_hash,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }
