from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.aal_viz_graph_render_packet import (
    BLOCKED,
    NOT_COMPUTABLE,
    build_aal_viz_graph_render_markdown,
    build_aal_viz_graph_render_packet,
    write_aal_viz_graph_render_packet,
)


def _runtime_projection() -> dict[str, Any]:
    return {
        "schema": "RuntimeProjectionPacket.v1",
        "projection_id": "rp-1",
        "projection_timestamp": "t:001",
        "runtime_health": {"health": "HEALTHY"},
        "replay_topology": {"replay_equivalence_status": {"equivalence_verified": True}},
        "operator_summary": {"status": "PRESENT", "next_actions": ["Inspect advisory overlays"]},
    }


def _snapshot_spine() -> dict[str, Any]:
    return {
        "schema": "TemporalSnapshotIndex.v1",
        "ordered_snapshots": [
            {
                "snapshot_id": "s2",
                "deterministic_timestamp": "t:002",
                "lineage_prev": "s1",
                "lineage_next": None,
            },
            {
                "snapshot_id": "s1",
                "deterministic_timestamp": "t:001",
                "lineage_prev": None,
                "lineage_next": "s2",
            },
        ],
    }


def _projection_bus() -> dict[str, Any]:
    return {
        "schema": "ProjectionBusEnvelope.v1",
        "messages": [
            {"snapshot_id": "s1", "message_id": "m1"},
            {"snapshot_id": "s2", "message_id": "m2"},
        ],
    }


def _chronoscope() -> dict[str, Any]:
    return {
        "schema": "ProjectionChronoscopePacket.v1",
        "remaining_blockers": [],
        "timeline_points": [
            {
                "timeline_point_id": "tp2",
                "snapshot_id": "s2",
                "deterministic_timestamp": "t:002",
                "cursor": "c2",
                "message_id": "m2",
                "link_status": "LINKED",
            },
            {
                "timeline_point_id": "tp1",
                "snapshot_id": "s1",
                "deterministic_timestamp": "t:001",
                "cursor": "c1",
                "message_id": "m1",
                "link_status": "LINKED",
            },
        ],
        "playback_cursors": [
            {"cursor": "c1", "next_cursor": "c2", "ordinal": 0},
            {"cursor": "c2", "next_cursor": None, "ordinal": 1},
        ],
        "timeline_windows": [
            {"window_id": "w1", "timeline_point_ids": ["tp1", "tp2"], "window_status": "PRESENT"}
        ],
        "lineage_evolution": {
            "lineage_status": "PRESENT",
            "lineage_chains": [{"chain_hash": "lc1"}],
        },
        "drift_timeline": {
            "drift_events": ["variance_spike"],
        },
    }


def _incremental_replay() -> dict[str, Any]:
    return {
        "schema": "IncrementalReplayPlan.v1",
        "final_status": "PASS",
        "invalidated_nodes": ["node_b", "node_a"],
        "skipped_surfaces": ["node_c"],
        "nodes": [
            {"node_id": "node_b", "dependencies": ["node_a"]},
            {"node_id": "node_a", "dependencies": []},
        ],
    }


def _runtime_benchmark() -> dict[str, Any]:
    return {
        "schema": "RuntimeBenchmarkArtifact.v1",
        "baseline_suite": {"suite_hash": "base-hash"},
        "optimized_suite": {"suite_hash": "opt-hash"},
    }


def _operator_console() -> dict[str, Any]:
    return {
        "schema": "OperatorRuntimeConsolePacket.v1",
        "packet_id": "console-1",
        "final_status": "PASS",
    }


def _operator_action_queue() -> dict[str, Any]:
    return {
        "operator_action_queue_status": "ADVISORY_ONLY",
        "operator_action_item_count": 5,
        "pending_approval_count": 5,
        "escalation_count": 2,
        "top_action_categories": ["drift_review", "render_blocker_review"],
        "queue_advisory_flags": ["advisory_only", "review_only"],
    }


def _payload_map() -> dict[str, dict[str, Any]]:
    return {
        "out/projections/aal_viz_runtime_projection_001.latest.json": _runtime_projection(),
        "out/projections/temporal_snapshot_spine_001.latest.json": _snapshot_spine(),
        "out/projections/projection_bus_001.latest.json": _projection_bus(),
        "out/projections/projection_chronoscope_001.latest.json": _chronoscope(),
        "out/audit/incremental_replay_001.latest.json": _incremental_replay(),
        "out/audit/runtime_benchmark_001.latest.json": _runtime_benchmark(),
        "out/audit/operator_runtime_console_001.latest.json": _operator_console(),
        "out/audit/operator_action_queue_001.latest.json": _operator_action_queue(),
    }


def _build_with_payloads(payloads: dict[str, dict[str, Any] | None]) -> dict[str, Any]:
    def _mock_load(path: str | Path | None) -> dict[str, Any] | None:
        return payloads.get(str(path), None)

    with patch("core.aal_viz_graph_render_packet._load_artifact", side_effect=_mock_load):
        return build_aal_viz_graph_render_packet(packet_id="aal_viz_graph_render_packet_001")


def test_stable_node_ordering() -> None:
    payloads = _payload_map()
    p1 = _build_with_payloads(payloads)
    p2 = _build_with_payloads(payloads)
    assert [node["node_id"] for node in p1["nodes"]] == [node["node_id"] for node in p2["nodes"]]
    assert [node["category"] for node in p1["nodes"]] == [node["category"] for node in p2["nodes"]]


def test_stable_edge_ordering() -> None:
    payloads = _payload_map()
    p1 = _build_with_payloads(payloads)
    p2 = _build_with_payloads(payloads)
    assert [edge["edge_id"] for edge in p1["edges"]] == [edge["edge_id"] for edge in p2["edges"]]
    assert [edge["category"] for edge in p1["edges"]] == [edge["category"] for edge in p2["edges"]]


def test_stable_layer_ordering() -> None:
    packet = _build_with_payloads(_payload_map())
    assert [layer["layer_id"] for layer in packet["layers"]] == sorted(
        layer["layer_id"] for layer in packet["layers"]
    )


def test_stable_packet_hash() -> None:
    payloads = _payload_map()
    p1 = _build_with_payloads(payloads)
    p2 = _build_with_payloads(payloads)
    assert p1["packet_hash"] == p2["packet_hash"]


def test_visualization_hints_deterministic() -> None:
    payloads = _payload_map()
    p1 = _build_with_payloads(payloads)
    p2 = _build_with_payloads(payloads)
    assert p1["visualization_hints"] == p2["visualization_hints"]


def test_missing_artifacts_fail_closed() -> None:
    packet = _build_with_payloads({})
    assert packet["final_status"] == NOT_COMPUTABLE
    assert packet["nodes"] == []
    assert packet["edges"] == []
    assert packet["render_blocker_count"] > 0
    assert all(
        entry["source_status"] == NOT_COMPUTABLE for entry in packet["source_entries"]
    )


def test_corrupt_lineage_cursor_blocks_layers_and_edges() -> None:
    payloads = _payload_map()
    corrupt = deepcopy(_chronoscope())
    corrupt["remaining_blockers"] = [
        "corrupt_lineage:lineage_prev_missing:s2->missing",
        "invalid_start_cursor:c-missing",
    ]
    payloads["out/projections/projection_chronoscope_001.latest.json"] = corrupt
    packet = _build_with_payloads(payloads)
    assert packet["final_status"] == BLOCKED
    layer_status = {layer["layer_id"]: layer["status"] for layer in packet["layers"]}
    assert layer_status["chronoscope_timeline_layer"] == BLOCKED
    assert layer_status["lineage_overlay_layer"] == BLOCKED
    assert all(
        edge["category"] not in {"lineage_edge", "cursor_edge", "window_edge"}
        for edge in packet["edges"]
    )


def test_invariants_locked() -> None:
    packet = _build_with_payloads(_payload_map())
    assert packet["projection_only"] is True
    assert packet["advisory_only"] is True
    assert packet["render_only"] is True
    assert packet["authority_granted"] is False
    assert packet["mutation_allowed"] is False
    assert packet["promotion_allowed"] is False
    assert packet["inference_authority"] is False
    assert packet["operator_action_queue_status"] == "ADVISORY_ONLY"
    assert packet["operator_action_item_count"] == 5
    assert packet["pending_approval_count"] == 5
    assert packet["escalation_count"] == 2


def test_contract_invariants_locked_for_nested_objects() -> None:
    packet = _build_with_payloads(_payload_map())
    for item in (
        packet["source_entries"]
        + packet["nodes"]
        + packet["edges"]
        + packet["layers"]
        + packet["overlays"]
        + packet["timeline_tracks"]
    ):
        assert item["projection_only"] is True
        assert item["advisory_only"] is True
        assert item["render_only"] is True
        assert item["authority_granted"] is False
        assert item["mutation_allowed"] is False
        assert item["promotion_allowed"] is False
        assert item["inference_authority"] is False


def test_no_mutation_of_loaded_payloads() -> None:
    payloads = _payload_map()
    before = deepcopy(payloads)
    _build_with_payloads(payloads)
    assert payloads == before


def test_write_packet_and_markdown(tmp_path: Path) -> None:
    packet = _build_with_payloads(_payload_map())
    out = tmp_path / "graph_render.json"
    write_aal_viz_graph_render_packet(out, packet)
    assert out.read_text(encoding="utf-8").endswith("\n")
    markdown = build_aal_viz_graph_render_markdown(packet)
    assert "Node Count" in markdown
    assert "Operator Action Queue" in markdown
    assert "Render-Only Posture" in markdown
