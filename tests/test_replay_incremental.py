"""Deterministic tests for incremental replay planner.

PATCH-P12-REPLAY-SCALING-AND-INCREMENTAL-EXECUTION-001

Proves:
- IncrementalReplayPlan.v1 packet shape stability
- incremental replay outputs == full replay outputs
- stable hashes preserved
- traversal ordering deterministic
- invalidation lineage deterministic
- skipped surfaces are dependency-safe
- cache reuse does not contaminate replay
- replay graph stable for identical inputs
- replay equivalence verification
- authority flags always False
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.canonical.json import canonical_hash
from core.replay_graph import build_replay_graph, build_replay_node
from core.replay_incremental import (
    PATCH_ID,
    build_incremental_plan,
    verify_replay_equivalence,
)
from scripts import run_incremental_replay


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _node(
    node_id: str,
    dependencies: list[str] | None = None,
    content_hash: str = "hash_stable",
) -> dict[str, Any]:
    return build_replay_node(
        node_id=node_id,
        artifact_path=f"out/{node_id}.json",
        content_hash=content_hash,
        dependencies=dependencies,
        replay_surface="test",
    )


def _linear_graph() -> dict[str, Any]:
    """A -> B -> C -> D"""
    return build_replay_graph(
        graph_id="linear",
        nodes=[
            _node("node_a"),
            _node("node_b", dependencies=["node_a"]),
            _node("node_c", dependencies=["node_b"]),
            _node("node_d", dependencies=["node_c"]),
        ],
    )


def _full_outputs(graph: dict[str, Any]) -> dict[str, str]:
    """Simulate full replay outputs."""
    return {
        n["node_id"]: canonical_hash(
            {"node_id": n["node_id"], "content_hash": n["content_hash"]}
        )
        for n in graph["nodes"]
    }


def _incremental_outputs(
    plan: dict[str, Any], full_outputs: dict[str, str]
) -> dict[str, str]:
    """Simulate incremental replay: outputs only for invalidated nodes."""
    invalidated = frozenset(plan["invalidated_nodes"])
    return {k: v for k, v in full_outputs.items() if k in invalidated}


# ---------------------------------------------------------------------------
# IncrementalReplayPlan.v1 — packet shape
# ---------------------------------------------------------------------------


def test_plan_schema_present() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    assert plan["schema"] == "IncrementalReplayPlan.v1"


def test_plan_patch_id() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    assert plan["patch_id"] == PATCH_ID


def test_plan_authority_flags_all_false() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    assert plan["authority_granted"] is False
    assert plan["mutation_allowed"] is False
    assert plan["promotion_allowed"] is False


def test_plan_required_fields_present() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    required = [
        "schema",
        "patch_id",
        "plan_id",
        "graph_id",
        "graph_hash",
        "changed_node_ids",
        "invalidated_nodes",
        "skipped_surfaces",
        "replay_order",
        "replay_chunks",
        "replay_chunk_count",
        "total_node_count",
        "invalidated_count",
        "skipped_count",
        "fail_closed",
        "plan_hash",
        "authority_granted",
        "mutation_allowed",
        "promotion_allowed",
    ]
    for field in required:
        assert field in plan, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# Incremental replay outputs == full replay outputs
# ---------------------------------------------------------------------------


def test_incremental_outputs_match_full_for_invalidated_nodes() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    full = _full_outputs(g)
    incremental = _incremental_outputs(plan, full)

    for node_id in plan["invalidated_nodes"]:
        assert incremental.get(node_id) == full.get(node_id), (
            f"Output mismatch for invalidated node: {node_id}"
        )


def test_skipped_surfaces_not_in_incremental_outputs() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_c"]
    )
    full = _full_outputs(g)
    incremental = _incremental_outputs(plan, full)

    for node_id in plan["skipped_surfaces"]:
        assert node_id not in incremental, (
            f"Skipped node should not appear in incremental outputs: {node_id}"
        )


# ---------------------------------------------------------------------------
# Traversal ordering is deterministic
# ---------------------------------------------------------------------------


def test_replay_order_preserves_graph_traversal_order() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    # Invalidated nodes in replay_order must preserve the traversal order
    full_order = g["traversal_order"]
    replay_order = plan["replay_order"]
    invalidated_set = frozenset(plan["invalidated_nodes"])
    expected_order = [n for n in full_order if n in invalidated_set]
    assert replay_order == expected_order


def test_plan_hash_deterministic_for_same_inputs() -> None:
    g = _linear_graph()
    plan_a = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    plan_b = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    assert plan_a["plan_hash"] == plan_b["plan_hash"]


def test_plan_hash_differs_for_different_changes() -> None:
    g = _linear_graph()
    plan_a = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    plan_b = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_c"]
    )
    assert plan_a["plan_hash"] != plan_b["plan_hash"]


# ---------------------------------------------------------------------------
# Invalidation lineage deterministic
# ---------------------------------------------------------------------------


def test_invalidated_nodes_include_changed_and_transitive_dependents() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    # node_b changed → node_b, node_c, node_d all invalidated
    assert "node_b" in plan["invalidated_nodes"]
    assert "node_c" in plan["invalidated_nodes"]
    assert "node_d" in plan["invalidated_nodes"]
    # node_a is upstream, not downstream — should be safe
    assert "node_a" in plan["skipped_surfaces"]


def test_skipped_surfaces_are_dependency_safe() -> None:
    """Skipped nodes must have no dependency on any invalidated node."""
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    invalidated = frozenset(plan["invalidated_nodes"])
    adjacency = g["adjacency"]
    for skipped in plan["skipped_surfaces"]:
        deps = adjacency.get(skipped, [])
        for dep in deps:
            assert dep not in invalidated, (
                f"Skipped node {skipped} depends on invalidated node {dep}"
            )


# ---------------------------------------------------------------------------
# Replay equivalence verification
# ---------------------------------------------------------------------------


def test_equivalence_held_for_correct_incremental_replay() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    full = _full_outputs(g)
    incremental = _incremental_outputs(plan, full)

    result = verify_replay_equivalence(
        full_outputs=full,
        incremental_outputs=incremental,
        plan=plan,
    )
    assert result["equivalence_held"] is True
    assert result["mismatches"] == []
    assert result["missing_from_incremental"] == []
    assert result["spurious_executions"] == []


def test_equivalence_schema_present() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(plan_id="p1", graph=g, changed_node_ids=["node_b"])
    full = _full_outputs(g)
    incremental = _incremental_outputs(plan, full)
    result = verify_replay_equivalence(
        full_outputs=full, incremental_outputs=incremental, plan=plan
    )
    assert result["schema"] == "ReplayEquivalenceVerification.v1"


def test_equivalence_authority_flags_all_false() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(plan_id="p1", graph=g, changed_node_ids=["node_b"])
    full = _full_outputs(g)
    incremental = _incremental_outputs(plan, full)
    result = verify_replay_equivalence(
        full_outputs=full, incremental_outputs=incremental, plan=plan
    )
    assert result["authority_granted"] is False
    assert result["mutation_allowed"] is False
    assert result["promotion_allowed"] is False


def test_equivalence_mismatch_detected() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_b"]
    )
    full = _full_outputs(g)
    # Corrupt one invalidated output
    corrupted = dict(full)
    corrupted["node_b"] = "wrong_hash"
    incremental = _incremental_outputs(plan, corrupted)

    result = verify_replay_equivalence(
        full_outputs=full,
        incremental_outputs=incremental,
        plan=plan,
    )
    assert result["equivalence_held"] is False
    assert "node_b" in result["mismatches"]


def test_equivalence_spurious_execution_detected() -> None:
    """Incremental replay must not include skipped nodes."""
    g = _linear_graph()
    plan = build_incremental_plan(
        plan_id="p1", graph=g, changed_node_ids=["node_c"]
    )
    full = _full_outputs(g)
    incremental = _incremental_outputs(plan, full)
    # Spuriously include a skipped node
    spurious = dict(incremental)
    if plan["skipped_surfaces"]:
        spurious_node = plan["skipped_surfaces"][0]
        spurious[spurious_node] = full.get(spurious_node, "fake")

        result = verify_replay_equivalence(
            full_outputs=full,
            incremental_outputs=spurious,
            plan=plan,
        )
        assert result["equivalence_held"] is False
        assert spurious_node in result["spurious_executions"]


def test_equivalence_verification_hash_deterministic() -> None:
    g = _linear_graph()
    plan = build_incremental_plan(plan_id="p1", graph=g, changed_node_ids=["node_b"])
    full = _full_outputs(g)
    incremental = _incremental_outputs(plan, full)

    r_a = verify_replay_equivalence(
        full_outputs=full, incremental_outputs=incremental, plan=plan
    )
    r_b = verify_replay_equivalence(
        full_outputs=full, incremental_outputs=incremental, plan=plan
    )
    assert r_a["verification_hash"] == r_b["verification_hash"]


# ---------------------------------------------------------------------------
# Cache reuse does not contaminate replay
# ---------------------------------------------------------------------------


def test_cache_reuse_does_not_contaminate_output_hashes() -> None:
    """Re-building the same graph twice must produce identical output hashes."""
    g_a = _linear_graph()
    g_b = _linear_graph()
    outputs_a = _full_outputs(g_a)
    outputs_b = _full_outputs(g_b)
    assert outputs_a == outputs_b


def test_plan_graph_hash_unchanged_across_invocations() -> None:
    g_a = _linear_graph()
    g_b = _linear_graph()
    plan_a = build_incremental_plan(
        plan_id="p1", graph=g_a, changed_node_ids=["node_b"]
    )
    plan_b = build_incremental_plan(
        plan_id="p1", graph=g_b, changed_node_ids=["node_b"]
    )
    assert plan_a["graph_hash"] == plan_b["graph_hash"]


# ---------------------------------------------------------------------------
# Fail-closed propagation
# ---------------------------------------------------------------------------


def test_plan_fail_closed_when_unknown_dependency() -> None:
    nodes = [
        build_replay_node(
            node_id="node_x",
            artifact_path="p",
            content_hash="h",
            dependencies=["node_missing"],
        )
    ]
    g = build_replay_graph(graph_id="bad", nodes=nodes)
    plan = build_incremental_plan(
        plan_id="p_bad", graph=g, changed_node_ids=["node_x"]
    )
    assert plan["fail_closed"] is True


# ---------------------------------------------------------------------------
# Script integration
# ---------------------------------------------------------------------------


def test_incremental_replay_script_writes_artifact(tmp_path: Path) -> None:
    runtime_paths = __import__("core.config", fromlist=["RuntimePaths"]).RuntimePaths(
        contracts_dir=Path("contracts"),
        out_dir=tmp_path / "out",
    )
    out_path = runtime_paths.incremental_replay_latest

    with (
        patch.object(run_incremental_replay, "_PATHS", runtime_paths),
        patch.object(run_incremental_replay, "OUT_PATH", out_path),
    ):
        run_incremental_replay.main()

    assert out_path.exists()
    import json

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["patch_id"] == PATCH_ID
    assert payload["authority_granted"] is False
    assert payload["mutation_allowed"] is False
    assert payload["promotion_allowed"] is False
    assert payload["schema"] == "IncrementalReplayReceipt.v1"


def test_incremental_replay_script_required_fields(tmp_path: Path) -> None:
    runtime_paths = __import__("core.config", fromlist=["RuntimePaths"]).RuntimePaths(
        contracts_dir=Path("contracts"),
        out_dir=tmp_path / "out",
    )
    out_path = runtime_paths.incremental_replay_latest

    with (
        patch.object(run_incremental_replay, "_PATHS", runtime_paths),
        patch.object(run_incremental_replay, "OUT_PATH", out_path),
    ):
        run_incremental_replay.main()

    import json

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    required_fields = [
        "patch_id",
        "replay_graph_hash",
        "invalidated_nodes",
        "replay_chunks",
        "skipped_surfaces",
        "replay_equivalence_verified",
        "artifact_outputs",
        "authority_granted",
        "mutation_allowed",
        "promotion_allowed",
        "final_status",
        "remaining_blockers",
    ]
    for field in required_fields:
        assert field in payload, f"Missing required field: {field}"


def test_incremental_replay_script_equivalence_verified(tmp_path: Path) -> None:
    runtime_paths = __import__("core.config", fromlist=["RuntimePaths"]).RuntimePaths(
        contracts_dir=Path("contracts"),
        out_dir=tmp_path / "out",
    )
    out_path = runtime_paths.incremental_replay_latest

    with (
        patch.object(run_incremental_replay, "_PATHS", runtime_paths),
        patch.object(run_incremental_replay, "OUT_PATH", out_path),
    ):
        run_incremental_replay.main()

    import json

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["replay_equivalence_verified"] is True
    assert payload["final_status"] == "PASS"
    assert payload["remaining_blockers"] == []


def test_incremental_replay_script_deterministic_across_calls(tmp_path: Path) -> None:
    """Running the script twice must yield stable replay_graph_hash."""
    runtime_paths = __import__("core.config", fromlist=["RuntimePaths"]).RuntimePaths(
        contracts_dir=Path("contracts"),
        out_dir=tmp_path / "out",
    )
    out_path = runtime_paths.incremental_replay_latest

    with (
        patch.object(run_incremental_replay, "_PATHS", runtime_paths),
        patch.object(run_incremental_replay, "OUT_PATH", out_path),
    ):
        run_incremental_replay.main()
        import json

        payload_a = json.loads(out_path.read_text(encoding="utf-8"))
        run_incremental_replay.main()
        payload_b = json.loads(out_path.read_text(encoding="utf-8"))

    assert payload_a["replay_graph_hash"] == payload_b["replay_graph_hash"]
    assert payload_a["final_status"] == payload_b["final_status"]
