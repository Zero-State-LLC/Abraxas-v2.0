from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.temporal_state_diff import (
    BLOCKED,
    NOT_COMPUTABLE,
    build_temporal_state_diff_markdown,
    build_temporal_state_diff_packet,
    write_temporal_state_diff_packet,
)
from scripts import run_temporal_state_diff


def _snapshot(snapshot_id: str, *, lineage_prev: str | None = None) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot_id,
        "projection_hash": f"ph:{snapshot_id}",
        "source_hash": f"sh:{snapshot_id}",
        "deterministic_timestamp": f"t:{snapshot_id}",
        "cursor": f"c:{snapshot_id}",
        "lineage_prev": lineage_prev,
        "lineage_next": None,
    }


def _chronoscope(*, drift_rate: float | str = 1.0, trend: str = "EQUIVALENT") -> dict[str, Any]:
    return {
        "final_status": "ADVISORY_ONLY",
        "timeline_points": [
            {
                "timeline_point_id": "tp-1",
                "snapshot_id": "s1",
                "cursor": "c:s1",
                "topic": "aal_viz.projection.refresh",
                "link_status": "LINKED",
                "message_id": "m-1",
            }
        ],
        "drift_timeline": {
            "drift_event_count": 1,
            "drift_rate": drift_rate,
            "blocked_window_count": 0,
            "lineage_gap_count": 0,
            "corrupt_lineage_count": 0,
            "not_computable_source_count": 0,
            "projection_equivalence_trend": trend,
        },
    }


def _render(nodes: list[str], edges: list[str]) -> dict[str, Any]:
    return {
        "nodes": [
            {"node_id": node_id, "category": "snapshot_node", "status": "PRESENT", "source_ref": node_id}
            for node_id in nodes
        ],
        "edges": [
            {
                "edge_id": edge_id,
                "category": "lineage_edge",
                "status": "PRESENT",
                "source_node_id": "n1",
                "target_node_id": "n2",
            }
            for edge_id in edges
        ],
        "layers": [{"layer_id": "l1", "status": "PRESENT", "node_refs": nodes, "edge_refs": edges}],
        "overlays": [{"overlay_id": "o1", "status": "PRESENT", "layer_ref": "l1"}],
    }


def _queue(items: list[str], *, severity: str = "HIGH") -> dict[str, Any]:
    return {
        "operator_action_items": [
            {
                "item_id": item_id,
                "category": "drift_review",
                "severity": severity,
                "source_artifact": "a.json",
                "related_blockers": [],
                "evidence": {"item_id": item_id},
            }
            for item_id in items
        ],
        "operator_action_item_count": len(items),
        "pending_approval_count": len(items),
        "escalation_count": 0,
    }


def _transport(topic_ids: list[str], frame_ids: list[str]) -> dict[str, Any]:
    return {
        "topics": [
            {
                "topic_id": topic_id,
                "topic_name": f"topic:{topic_id}",
                "payload_kind": "projection_snapshot_ref",
                "source_artifact_path": "x.json",
            }
            for topic_id in topic_ids
        ],
        "frames": [
            {
                "frame_id": frame_id,
                "topic_id": topic_ids[0] if topic_ids else "t1",
                "cursor": f"cursor:{frame_id}",
                "blocker_status": "PRESENT",
                "source_hash": frame_id,
                "packet_id": "pkt",
            }
            for frame_id in frame_ids
        ],
        "transport_cursor_bounds": {"first": "cursor:first", "last": "cursor:last"},
    }


def _payload_map() -> dict[str, dict[str, Any]]:
    return {
        "prev/live.json": {"final_status": "PASS", "cursor": "c1"},
        "curr/live.json": {"final_status": "PASS", "cursor": "c2"},
        "prev/snapshot.json": {"ordered_snapshots": [_snapshot("s1")]},
        "curr/snapshot.json": {"ordered_snapshots": [_snapshot("s1", lineage_prev="s0")]},
        "prev/bus.json": {"messages": [{"message_id": "m-1", "snapshot_id": "s1"}], "final_status": "PASS"},
        "curr/bus.json": {"messages": [{"message_id": "m-2", "snapshot_id": "s2"}], "final_status": "ADVISORY_ONLY"},
        "prev/chronoscope.json": _chronoscope(drift_rate=1.0, trend="EQUIVALENT"),
        "curr/chronoscope.json": _chronoscope(drift_rate=2.0, trend="DIVERGENT"),
        "prev/render.json": _render(["n1"], ["e1"]),
        "curr/render.json": _render(["n1", "n2"], ["e1", "e2"]),
        "prev/queue.json": _queue(["q1", "q2"], severity="LOW"),
        "curr/queue.json": _queue(["q2", "q3"], severity="HIGH"),
        "prev/transport.json": _transport(["t1"], ["f1"]),
        "curr/transport.json": _transport(["t1", "t2"], ["f1", "f2"]),
        "prev/ingest.json": {"receipt_hash": "h1", "item_hashes": ["a"], "status": "ADVISORY_ONLY"},
        "curr/ingest.json": {"receipt_hash": "h1", "item_hashes": ["a"], "status": "ADVISORY_ONLY"},
    }


def _paths() -> tuple[dict[str, str], dict[str, str]]:
    previous = {
        "live_projection_refresh": "prev/live.json",
        "temporal_snapshot_spine": "prev/snapshot.json",
        "projection_bus": "prev/bus.json",
        "projection_chronoscope": "prev/chronoscope.json",
        "aal_viz_graph_render_packet": "prev/render.json",
        "operator_action_queue": "prev/queue.json",
        "read_only_transport": "prev/transport.json",
        "universal_ingest_receipt": "prev/ingest.json",
    }
    current = {
        "live_projection_refresh": "curr/live.json",
        "temporal_snapshot_spine": "curr/snapshot.json",
        "projection_bus": "curr/bus.json",
        "projection_chronoscope": "curr/chronoscope.json",
        "aal_viz_graph_render_packet": "curr/render.json",
        "operator_action_queue": "curr/queue.json",
        "read_only_transport": "curr/transport.json",
        "universal_ingest_receipt": "curr/ingest.json",
    }
    return previous, current


def _build_with_payloads(payloads: dict[str, dict[str, Any] | None]) -> dict[str, Any]:
    previous, current = _paths()
    with patch(
        "core.temporal_state_diff._load_artifact",
        side_effect=lambda path: payloads.get(str(path)),
    ):
        return build_temporal_state_diff_packet(
            previous_artifact_paths=previous,
            current_artifact_paths=current,
        )


def test_stable_diff_ordering_and_packet_hash() -> None:
    payloads = _payload_map()
    p1 = _build_with_payloads(payloads)
    p2 = _build_with_payloads(payloads)
    assert [entry["entry_id"] for entry in p1["diff_entries"]] == [
        entry["entry_id"] for entry in p2["diff_entries"]
    ]
    assert p1["packet_hash"] == p2["packet_hash"]


def test_classifies_added_removed_modified_topology_and_lineage() -> None:
    packet = _build_with_payloads(_payload_map())
    change_types = {entry["change_type"] for entry in packet["diff_entries"]}
    assert {"ADDED", "REMOVED", "MODIFIED"} <= change_types
    assert "TOPOLOGY_SHIFT" in change_types
    assert "LINEAGE_SHIFT" in change_types
    assert packet["topology_change_count"] > 0
    assert packet["lineage_shift_count"] > 0


def test_classifies_replay_queue_and_transport_deltas() -> None:
    packet = _build_with_payloads(_payload_map())
    change_types = {entry["change_type"] for entry in packet["diff_entries"]}
    assert "REPLAY_EQUIVALENCE_SHIFT" in change_types
    assert "QUEUE_DELTA" in change_types
    assert "TRANSPORT_DELTA" in change_types
    assert packet["queue_delta_count"] > 0
    assert packet["transport_delta_count"] > 0


def test_drift_acceleration_and_not_computable_behavior() -> None:
    payloads = _payload_map()
    packet = _build_with_payloads(payloads)
    assert packet["drift_acceleration_status"] == "DRIFT_ACCELERATING"

    payloads["prev/chronoscope.json"] = {"final_status": "ADVISORY_ONLY"}
    packet_nc = _build_with_payloads(payloads)
    assert packet_nc["drift_acceleration_status"] == NOT_COMPUTABLE
    assert any(
        entry["source_surface"] == "projection_chronoscope.drift_acceleration"
        and entry["change_type"] == NOT_COMPUTABLE
        for entry in packet_nc["diff_entries"]
    )


def test_missing_artifact_fail_closed() -> None:
    packet = _build_with_payloads({})
    assert packet["final_status"] == NOT_COMPUTABLE
    assert all(entry["change_type"] == NOT_COMPUTABLE for entry in packet["diff_entries"])
    assert packet["remaining_blockers"]


def test_authority_boundary_violation_blocks_surface() -> None:
    payloads = _payload_map()
    payloads["curr/queue.json"] = {**_queue(["q1"]), "authority_granted": True}
    packet = _build_with_payloads(payloads)
    assert packet["final_status"] == BLOCKED
    assert any(
        entry["change_type"] == BLOCKED
        and entry["evidence"].get("reason") == "authority_boundary_violation"
        for entry in packet["diff_entries"]
    )


def test_invariants_locked_and_no_mutation() -> None:
    payloads = _payload_map()
    before = deepcopy(payloads)
    packet = _build_with_payloads(payloads)
    assert payloads == before
    assert packet["advisory_only"] is True
    assert packet["diff_only"] is True
    assert packet["detection_only"] is True
    assert packet["execution_authority"] is False
    assert packet["authority_granted"] is False
    assert packet["mutation_allowed"] is False
    assert packet["promotion_allowed"] is False
    assert packet["auto_execute"] is False
    assert packet["auto_approve"] is False
    assert packet["command_channel"] is False
    assert packet["bidirectional_control"] is False
    assert packet["inference_authority"] is False
    assert all(entry["advisory_only"] is True for entry in packet["diff_entries"])


def test_optional_ingest_missing_is_non_breaking() -> None:
    payloads = _payload_map()
    payloads["prev/ingest.json"] = None
    payloads["curr/ingest.json"] = None
    packet = _build_with_payloads(payloads)
    assert packet["final_status"] in {"ADVISORY_ONLY", "PASS"}
    assert not any(
        entry["source_surface"] == "universal_ingest_receipt"
        and entry["change_type"] in {NOT_COMPUTABLE, BLOCKED}
        for entry in packet["diff_entries"]
    )


def test_optional_ingest_hash_change_produces_deterministic_diff_entry() -> None:
    payloads = _payload_map()
    payloads["curr/ingest.json"] = {"receipt_hash": "h2", "item_hashes": ["b"], "status": "ADVISORY_ONLY"}
    a = _build_with_payloads(payloads)
    b = _build_with_payloads(payloads)
    ingest_entries_a = [
        entry for entry in a["diff_entries"] if entry["source_surface"] == "universal_ingest_receipt"
    ]
    ingest_entries_b = [
        entry for entry in b["diff_entries"] if entry["source_surface"] == "universal_ingest_receipt"
    ]
    assert any(entry["change_type"] == "HASH_CHANGED" for entry in ingest_entries_a)
    assert ingest_entries_a == ingest_entries_b


def test_writer_and_markdown(tmp_path: Path) -> None:
    packet = _build_with_payloads(_payload_map())
    out_path = tmp_path / "temporal_state_diff.json"
    write_temporal_state_diff_packet(out_path, packet)
    markdown = build_temporal_state_diff_markdown(packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
    assert "Temporal State Diff" in markdown
    assert "Operator Next Actions" in markdown


def test_run_script_writes_artifacts(tmp_path: Path) -> None:
    payloads = _payload_map()
    previous_manifest = tmp_path / "previous_manifest.json"
    current_manifest = tmp_path / "current_manifest.json"
    previous_paths, current_paths = _paths()
    previous_manifest.write_text(
        json.dumps(previous_paths, sort_keys=True), encoding="utf-8"
    )
    current_manifest.write_text(
        json.dumps(current_paths, sort_keys=True), encoding="utf-8"
    )

    runtime_paths = run_temporal_state_diff.RuntimePaths(
        contracts_dir=tmp_path / "contracts",
        out_dir=tmp_path / "out",
    )
    with (
        patch(
            "core.temporal_state_diff._load_artifact",
            side_effect=lambda path: payloads.get(str(path)),
        ),
        patch.object(run_temporal_state_diff, "_PATHS", runtime_paths),
        patch.object(run_temporal_state_diff, "OUT_PATH", runtime_paths.temporal_state_diff_latest),
    ):
        run_temporal_state_diff.main(
            [
                "--previous-manifest",
                previous_manifest.as_posix(),
                "--current-manifest",
                current_manifest.as_posix(),
            ]
        )

    assert runtime_paths.temporal_state_diff_latest.exists()
    assert runtime_paths.temporal_state_diff_latest.with_suffix(".md").exists()
