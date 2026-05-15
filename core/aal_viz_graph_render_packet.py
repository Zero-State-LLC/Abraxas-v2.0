"""Deterministic AAL-Viz graph render packet contracts over P13-P16 projections.

PATCH-P17-AAL-VIZ-GRAPH-RENDER-PACKET-001

Render packet IR only:
- projection-only
- advisory-only
- render-only
- no runtime/replay/canon/forecast/optimization/governance mutation
- no visualization authority
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths
from core.operator_action_queue import summarize_operator_action_queue

PATCH_ID = "PATCH-P17-AAL-VIZ-GRAPH-RENDER-PACKET-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_AUTHORITY_BOUNDARY: dict[str, Any] = {
    "projection_only": True,
    "advisory_only": True,
    "render_only": True,
    "authority_granted": False,
    "mutation_allowed": False,
    "promotion_allowed": False,
    "inference_authority": False,
}


_NODE_ORDER = {
    "replay_node": 0,
    "snapshot_node": 1,
    "bus_message_node": 2,
    "timeline_point_node": 3,
    "lineage_node": 4,
    "drift_event_node": 5,
    "operator_summary_node": 6,
    "benchmark_surface_node": 7,
}

_EDGE_ORDER = {
    "dependency_edge": 0,
    "lineage_edge": 1,
    "cursor_edge": 2,
    "message_edge": 3,
    "window_edge": 4,
    "drift_edge": 5,
    "equivalence_edge": 6,
}


def _load_artifact(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _sorted_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        nodes,
        key=lambda item: (
            _NODE_ORDER.get(str(item.get("category", "")), 999),
            str(item.get("timestamp", "")),
            str(item.get("node_id", "")),
        ),
    )


def _sorted_edges(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        edges,
        key=lambda item: (
            _EDGE_ORDER.get(str(item.get("category", "")), 999),
            str(item.get("timestamp", "")),
            str(item.get("edge_id", "")),
        ),
    )


def _mk_node(
    *,
    category: str,
    source_key: str,
    source_ref: str,
    timestamp: str | None,
    status: str,
    semantic_tokens: list[str],
    label: str,
) -> dict[str, Any]:
    node_id = canonical_hash(
        {
            "category": category,
            "source_key": source_key,
            "source_ref": source_ref,
            "timestamp": timestamp,
        }
    )
    return {
        "schema": "AALVizRenderNode.v1",
        "node_id": node_id,
        "category": category,
        "source_key": source_key,
        "source_ref": source_ref,
        "timestamp": timestamp,
        "status": status,
        "semantic_tokens": sorted(set(semantic_tokens)),
        "label": label,
        **_AUTHORITY_BOUNDARY,
    }


def _mk_edge(
    *,
    category: str,
    source_node_id: str,
    target_node_id: str,
    source_ref: str,
    timestamp: str | None,
    status: str,
    semantic_tokens: list[str],
) -> dict[str, Any]:
    edge_id = canonical_hash(
        {
            "category": category,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "source_ref": source_ref,
            "timestamp": timestamp,
        }
    )
    return {
        "schema": "AALVizRenderEdge.v1",
        "edge_id": edge_id,
        "category": category,
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "source_ref": source_ref,
        "timestamp": timestamp,
        "status": status,
        "semantic_tokens": sorted(set(semantic_tokens)),
        **_AUTHORITY_BOUNDARY,
    }


def _has_corrupt_timeline_or_lineage(chronoscope: dict[str, Any] | None) -> bool:
    if not isinstance(chronoscope, dict):
        return False
    blockers = [str(item) for item in chronoscope.get("remaining_blockers", [])]
    return any(
        blocker.startswith("corrupt_lineage:")
        or blocker.startswith("invalid_start_cursor:")
        or blocker.startswith("invalid_end_cursor:")
        or blocker == "cursor_window_reversed"
        for blocker in blockers
    )


def _source_entries(
    paths: dict[str, str | Path],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any] | None]]:
    payloads: dict[str, dict[str, Any] | None] = {}
    entries: list[dict[str, Any]] = []
    for source_key, source_path in sorted(paths.items(), key=lambda item: item[0]):
        payload = _load_artifact(source_path)
        payloads[source_key] = payload
        if payload is None:
            entries.append(
                {
                    "schema": "AALVizRenderSourceEntry.v1",
                    "source_key": source_key,
                    "source_path": str(source_path),
                    "source_status": NOT_COMPUTABLE,
                    "source_reason": "source artifact missing or unreadable",
                    **_AUTHORITY_BOUNDARY,
                }
            )
        else:
            entries.append(
                {
                    "schema": "AALVizRenderSourceEntry.v1",
                    "source_key": source_key,
                    "source_path": str(source_path),
                    "source_status": "PRESENT",
                    "source_schema": payload.get("schema"),
                    "source_hash": canonical_hash(payload),
                    **_AUTHORITY_BOUNDARY,
                }
            )
    return entries, payloads


def build_aal_viz_graph_render_packet(
    *,
    packet_id: str = "aal_viz_graph_render_packet_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
        "runtime_projection": paths.aal_viz_runtime_projection_latest,
        "temporal_snapshot_spine": paths.temporal_snapshot_spine_latest,
        "projection_bus": paths.projection_bus_latest,
        "projection_chronoscope": paths.projection_chronoscope_latest,
        "incremental_replay": paths.incremental_replay_latest,
        "runtime_benchmark": paths.runtime_benchmark_latest,
        "operator_console": paths.operator_runtime_console_latest,
        "operator_action_queue": paths.operator_action_queue_latest,
        "temporal_state_diff": paths.temporal_state_diff_latest,
    }
    merged_paths = {**defaults, **(source_artifact_paths or {})}
    source_entries, payloads = _source_entries(merged_paths)

    runtime_projection = payloads.get("runtime_projection")
    snapshot_spine = payloads.get("temporal_snapshot_spine")
    projection_bus = payloads.get("projection_bus")
    chronoscope = payloads.get("projection_chronoscope")
    incremental_replay = payloads.get("incremental_replay")
    runtime_benchmark = payloads.get("runtime_benchmark")
    operator_console = payloads.get("operator_console")
    operator_action_queue = payloads.get("operator_action_queue")
    operator_action_queue_summary = summarize_operator_action_queue(
        operator_action_queue
    )

    has_corrupt_lineage_or_cursor = _has_corrupt_timeline_or_lineage(chronoscope)

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    replay_node_by_id: dict[str, str] = {}
    snapshot_node_by_snapshot_id: dict[str, str] = {}
    message_node_by_message_id: dict[str, str] = {}
    timeline_node_by_point_id: dict[str, str] = {}
    timeline_node_by_cursor: dict[str, str] = {}
    benchmark_nodes: list[str] = []
    operator_node_id: str | None = None

    if isinstance(incremental_replay, dict):
        invalidated = sorted(str(item) for item in incremental_replay.get("invalidated_nodes", []))
        skipped = sorted(str(item) for item in incremental_replay.get("skipped_surfaces", []))
        replay_ts = (
            str(runtime_projection.get("projection_timestamp"))
            if isinstance(runtime_projection, dict)
            else None
        )
        for node_ref in invalidated:
            node = _mk_node(
                category="replay_node",
                source_key="incremental_replay",
                source_ref=node_ref,
                timestamp=replay_ts,
                status="PRESENT",
                semantic_tokens=["status.active", "group.replay"],
                label=f"Replay {node_ref}",
            )
            replay_node_by_id[node_ref] = str(node["node_id"])
            nodes.append(node)
        for node_ref in skipped:
            node = _mk_node(
                category="replay_node",
                source_key="incremental_replay",
                source_ref=node_ref,
                timestamp=replay_ts,
                status="SKIPPED",
                semantic_tokens=["status.skipped", "group.replay"],
                label=f"Skipped {node_ref}",
            )
            replay_node_by_id.setdefault(node_ref, str(node["node_id"]))
            nodes.append(node)

        for replay_node in sorted(
            [item for item in incremental_replay.get("nodes", []) if isinstance(item, dict)],
            key=lambda item: str(item.get("node_id", "")),
        ):
            target_ref = str(replay_node.get("node_id", ""))
            target_id = replay_node_by_id.get(target_ref)
            if not target_id:
                continue
            for dep_ref in sorted(str(dep) for dep in replay_node.get("dependencies", [])):
                dep_id = replay_node_by_id.get(dep_ref)
                if not dep_id:
                    continue
                edges.append(
                    _mk_edge(
                        category="dependency_edge",
                        source_node_id=dep_id,
                        target_node_id=target_id,
                        source_ref=f"{dep_ref}->{target_ref}",
                        timestamp=replay_ts,
                        status="PRESENT",
                        semantic_tokens=["edge.dependency", "group.replay"],
                    )
                )

    if isinstance(snapshot_spine, dict):
        snapshots = sorted(
            [item for item in snapshot_spine.get("ordered_snapshots", []) if isinstance(item, dict)],
            key=lambda item: (
                str(item.get("deterministic_timestamp", "")),
                str(item.get("snapshot_id", "")),
            ),
        )
        for snapshot in snapshots:
            snapshot_id = str(snapshot.get("snapshot_id", ""))
            timestamp = str(snapshot.get("deterministic_timestamp", ""))
            node = _mk_node(
                category="snapshot_node",
                source_key="temporal_snapshot_spine",
                source_ref=snapshot_id,
                timestamp=timestamp,
                status="PRESENT",
                semantic_tokens=["group.snapshot", "status.present"],
                label=f"Snapshot {snapshot_id}",
            )
            snapshot_node_by_snapshot_id[snapshot_id] = str(node["node_id"])
            nodes.append(node)

        if not has_corrupt_lineage_or_cursor:
            for snapshot in snapshots:
                snapshot_id = str(snapshot.get("snapshot_id", ""))
                prev_ref = snapshot.get("lineage_prev")
                if not isinstance(prev_ref, str) or not prev_ref:
                    continue
                source_id = snapshot_node_by_snapshot_id.get(prev_ref)
                target_id = snapshot_node_by_snapshot_id.get(snapshot_id)
                if not source_id or not target_id:
                    continue
                edges.append(
                    _mk_edge(
                        category="lineage_edge",
                        source_node_id=source_id,
                        target_node_id=target_id,
                        source_ref=f"{prev_ref}->{snapshot_id}",
                        timestamp=str(snapshot.get("deterministic_timestamp", "")),
                        status="PRESENT",
                        semantic_tokens=["edge.lineage", "group.snapshot"],
                    )
                )

    if isinstance(projection_bus, dict):
        messages = sorted(
            [item for item in projection_bus.get("messages", []) if isinstance(item, dict)],
            key=lambda item: (str(item.get("snapshot_id", "")), str(item.get("message_id", ""))),
        )
        for message in messages:
            message_id = str(message.get("message_id", ""))
            snapshot_id = str(message.get("snapshot_id", ""))
            node = _mk_node(
                category="bus_message_node",
                source_key="projection_bus",
                source_ref=message_id,
                timestamp=None,
                status="PRESENT",
                semantic_tokens=["group.bus", "status.present"],
                label=f"Bus message {message_id}",
            )
            message_node_by_message_id[message_id] = str(node["node_id"])
            nodes.append(node)
            snapshot_node_id = snapshot_node_by_snapshot_id.get(snapshot_id)
            if snapshot_node_id is not None:
                edges.append(
                    _mk_edge(
                        category="message_edge",
                        source_node_id=snapshot_node_id,
                        target_node_id=str(node["node_id"]),
                        source_ref=f"{snapshot_id}->{message_id}",
                        timestamp=None,
                        status="PRESENT",
                        semantic_tokens=["edge.message", "group.bus"],
                    )
                )

    if isinstance(runtime_benchmark, dict):
        for surface in ["baseline_suite", "optimized_suite"]:
            suite = runtime_benchmark.get(surface)
            if not isinstance(suite, dict):
                continue
            suite_hash = str(suite.get("suite_hash", surface))
            node = _mk_node(
                category="benchmark_surface_node",
                source_key="runtime_benchmark",
                source_ref=suite_hash,
                timestamp=None,
                status="PRESENT",
                semantic_tokens=["group.benchmark", "status.present"],
                label=f"Benchmark {surface}",
            )
            benchmark_nodes.append(str(node["node_id"]))
            nodes.append(node)

    if isinstance(chronoscope, dict):
        points = sorted(
            [item for item in chronoscope.get("timeline_points", []) if isinstance(item, dict)],
            key=lambda item: (
                str(item.get("deterministic_timestamp", "")),
                str(item.get("snapshot_id", "")),
                str(item.get("timeline_point_id", "")),
            ),
        )
        for point in points:
            point_id = str(point.get("timeline_point_id", ""))
            cursor = str(point.get("cursor", ""))
            node = _mk_node(
                category="timeline_point_node",
                source_key="projection_chronoscope",
                source_ref=point_id,
                timestamp=str(point.get("deterministic_timestamp", "")),
                status=str(point.get("link_status", "PRESENT")),
                semantic_tokens=["group.timeline", "status.present"],
                label=f"Timeline point {point_id}",
            )
            timeline_node_by_point_id[point_id] = str(node["node_id"])
            timeline_node_by_cursor[cursor] = str(node["node_id"])
            nodes.append(node)

            message_id = point.get("message_id")
            if isinstance(message_id, str) and message_id in message_node_by_message_id:
                edges.append(
                    _mk_edge(
                        category="message_edge",
                        source_node_id=message_node_by_message_id[message_id],
                        target_node_id=str(node["node_id"]),
                        source_ref=f"{message_id}->{point_id}",
                        timestamp=str(point.get("deterministic_timestamp", "")),
                        status="PRESENT",
                        semantic_tokens=["edge.message", "group.timeline"],
                    )
                )

        if not has_corrupt_lineage_or_cursor:
            cursors = sorted(
                [item for item in chronoscope.get("playback_cursors", []) if isinstance(item, dict)],
                key=lambda item: int(item.get("ordinal", 0)),
            )
            for cursor in cursors:
                current_cursor = str(cursor.get("cursor", ""))
                next_cursor = cursor.get("next_cursor")
                if not isinstance(next_cursor, str) or not next_cursor:
                    continue
                source_id = timeline_node_by_cursor.get(current_cursor)
                target_id = timeline_node_by_cursor.get(next_cursor)
                if source_id is None or target_id is None:
                    continue
                edges.append(
                    _mk_edge(
                        category="cursor_edge",
                        source_node_id=source_id,
                        target_node_id=target_id,
                        source_ref=f"{current_cursor}->{next_cursor}",
                        timestamp=None,
                        status="PRESENT",
                        semantic_tokens=["edge.cursor", "group.timeline"],
                    )
                )

            windows = sorted(
                [item for item in chronoscope.get("timeline_windows", []) if isinstance(item, dict)],
                key=lambda item: str(item.get("window_id", "")),
            )
            for window in windows:
                point_refs = [
                    timeline_node_by_point_id.get(str(point_id))
                    for point_id in window.get("timeline_point_ids", [])
                ]
                point_refs = [item for item in point_refs if isinstance(item, str)]
                if len(point_refs) < 2:
                    continue
                edges.append(
                    _mk_edge(
                        category="window_edge",
                        source_node_id=point_refs[0],
                        target_node_id=point_refs[-1],
                        source_ref=str(window.get("window_id", "")),
                        timestamp=None,
                        status=str(window.get("window_status", "PRESENT")),
                        semantic_tokens=["edge.window", "group.timeline"],
                    )
                )

        lineage = chronoscope.get("lineage_evolution", {})
        if isinstance(lineage, dict):
            for chain in sorted(
                [item for item in lineage.get("lineage_chains", []) if isinstance(item, dict)],
                key=lambda item: str(item.get("chain_hash", "")),
            ):
                chain_ref = str(chain.get("chain_hash", ""))
                node = _mk_node(
                    category="lineage_node",
                    source_key="projection_chronoscope",
                    source_ref=chain_ref,
                    timestamp=None,
                    status=str(lineage.get("lineage_status", "PRESENT")),
                    semantic_tokens=["group.lineage", "status.present"],
                    label=f"Lineage chain {chain_ref}",
                )
                nodes.append(node)

        drift = chronoscope.get("drift_timeline", {})
        if isinstance(drift, dict):
            for drift_event in sorted(str(item) for item in drift.get("drift_events", [])):
                node = _mk_node(
                    category="drift_event_node",
                    source_key="projection_chronoscope",
                    source_ref=drift_event,
                    timestamp=None,
                    status="PRESENT",
                    semantic_tokens=["group.drift", "severity.warning"],
                    label=f"Drift {drift_event}",
                )
                nodes.append(node)
                if benchmark_nodes:
                    for benchmark_node_id in benchmark_nodes:
                        edges.append(
                            _mk_edge(
                                category="drift_edge",
                                source_node_id=str(node["node_id"]),
                                target_node_id=benchmark_node_id,
                                source_ref=drift_event,
                                timestamp=None,
                                status="PRESENT",
                                semantic_tokens=["edge.drift", "group.drift"],
                            )
                        )

    if isinstance(runtime_projection, dict):
        summary = runtime_projection.get("operator_summary", {})
        status = str(summary.get("status", "PRESENT")) if isinstance(summary, dict) else "PRESENT"
        operator_node = _mk_node(
            category="operator_summary_node",
            source_key="runtime_projection",
            source_ref=str(runtime_projection.get("projection_id", packet_id)),
            timestamp=str(runtime_projection.get("projection_timestamp", "")),
            status=status,
            semantic_tokens=["group.operator", "status.present"],
            label="Operator summary",
        )
        operator_node_id = str(operator_node["node_id"])
        nodes.append(operator_node)

        replay_equivalence = (
            runtime_projection.get("replay_topology", {})
            .get("replay_equivalence_status", {})
            .get("equivalence_verified")
        )
        if isinstance(replay_equivalence, bool) and replay_node_by_id and operator_node_id is not None:
            reference = sorted(replay_node_by_id.items(), key=lambda item: item[0])[0][1]
            edges.append(
                _mk_edge(
                    category="equivalence_edge",
                    source_node_id=reference,
                    target_node_id=operator_node_id,
                    source_ref="replay_equivalence",
                    timestamp=str(runtime_projection.get("projection_timestamp", "")),
                    status="PRESENT" if replay_equivalence else BLOCKED,
                    semantic_tokens=["edge.equivalence", "group.operator"],
                )
            )

    if operator_node_id is None and isinstance(operator_console, dict):
        operator_node = _mk_node(
            category="operator_summary_node",
            source_key="operator_console",
            source_ref=str(operator_console.get("packet_id", "operator_console")),
            timestamp=None,
            status=str(operator_console.get("final_status", "PRESENT")),
            semantic_tokens=["group.operator", "status.present"],
            label="Operator summary",
        )
        operator_node_id = str(operator_node["node_id"])
        nodes.append(operator_node)

    nodes = _sorted_nodes(nodes)
    edges = _sorted_edges(edges)

    node_ids = {str(node["node_id"]) for node in nodes}
    edges = [
        edge
        for edge in edges
        if str(edge.get("source_node_id")) in node_ids and str(edge.get("target_node_id")) in node_ids
    ]

    def select_nodes(category: str) -> list[str]:
        return [
            str(node["node_id"])
            for node in nodes
            if str(node.get("category")) == category
        ]

    def select_edges(category: str) -> list[str]:
        return [
            str(edge["edge_id"])
            for edge in edges
            if str(edge.get("category")) == category
        ]

    source_status = {
        str(entry["source_key"]): str(entry["source_status"]) for entry in source_entries
    }

    replay_layer_status = (
        NOT_COMPUTABLE
        if source_status.get("incremental_replay") != "PRESENT"
        else str(incremental_replay.get("final_status", "PRESENT"))
        if isinstance(incremental_replay, dict)
        else "PRESENT"
    )
    snapshot_layer_status = (
        NOT_COMPUTABLE if source_status.get("temporal_snapshot_spine") != "PRESENT" else "PRESENT"
    )
    bus_layer_status = (
        NOT_COMPUTABLE if source_status.get("projection_bus") != "PRESENT" else "PRESENT"
    )
    chronoscope_layer_status = (
        NOT_COMPUTABLE
        if source_status.get("projection_chronoscope") != "PRESENT"
        else BLOCKED
        if has_corrupt_lineage_or_cursor
        else "PRESENT"
    )
    lineage_layer_status = chronoscope_layer_status
    drift_layer_status = (
        NOT_COMPUTABLE
        if source_status.get("projection_chronoscope") != "PRESENT"
        else "PRESENT"
    )
    runtime_health_status = (
        NOT_COMPUTABLE
        if source_status.get("runtime_projection") != "PRESENT"
        else str(runtime_projection.get("runtime_health", {}).get("health", NOT_COMPUTABLE))
        if isinstance(runtime_projection, dict)
        else NOT_COMPUTABLE
    )
    operator_layer_status = (
        NOT_COMPUTABLE
        if source_status.get("runtime_projection") != "PRESENT"
        and source_status.get("operator_console") != "PRESENT"
        else "PRESENT"
    )

    layers = [
        {
            "schema": "AALVizRenderLayer.v1",
            "layer_id": "replay_topology_layer",
            "visible_by_default": True,
            "node_refs": select_nodes("replay_node"),
            "edge_refs": select_edges("dependency_edge") + select_edges("equivalence_edge"),
            "advisory_flags": ["projection_only", "advisory_only", "render_only"],
            "layout_hint": "DAG",
            "status": replay_layer_status,
            **_AUTHORITY_BOUNDARY,
        },
        {
            "schema": "AALVizRenderLayer.v1",
            "layer_id": "temporal_snapshot_layer",
            "visible_by_default": True,
            "node_refs": select_nodes("snapshot_node"),
            "edge_refs": select_edges("lineage_edge"),
            "advisory_flags": ["projection_only", "advisory_only", "render_only"],
            "layout_hint": "layered",
            "status": snapshot_layer_status,
            **_AUTHORITY_BOUNDARY,
        },
        {
            "schema": "AALVizRenderLayer.v1",
            "layer_id": "projection_bus_layer",
            "visible_by_default": False,
            "node_refs": select_nodes("bus_message_node"),
            "edge_refs": select_edges("message_edge"),
            "advisory_flags": ["projection_only", "advisory_only", "render_only"],
            "layout_hint": "layered",
            "status": bus_layer_status,
            **_AUTHORITY_BOUNDARY,
        },
        {
            "schema": "AALVizRenderLayer.v1",
            "layer_id": "chronoscope_timeline_layer",
            "visible_by_default": True,
            "node_refs": select_nodes("timeline_point_node"),
            "edge_refs": select_edges("cursor_edge") + select_edges("window_edge"),
            "advisory_flags": ["projection_only", "advisory_only", "render_only"],
            "layout_hint": "timeline",
            "status": chronoscope_layer_status,
            **_AUTHORITY_BOUNDARY,
        },
        {
            "schema": "AALVizRenderLayer.v1",
            "layer_id": "drift_overlay_layer",
            "visible_by_default": True,
            "node_refs": select_nodes("drift_event_node"),
            "edge_refs": select_edges("drift_edge"),
            "advisory_flags": ["projection_only", "advisory_only", "render_only"],
            "layout_hint": "radial",
            "status": drift_layer_status,
            **_AUTHORITY_BOUNDARY,
        },
        {
            "schema": "AALVizRenderLayer.v1",
            "layer_id": "lineage_overlay_layer",
            "visible_by_default": True,
            "node_refs": select_nodes("lineage_node"),
            "edge_refs": select_edges("lineage_edge"),
            "advisory_flags": ["projection_only", "advisory_only", "render_only"],
            "layout_hint": "DAG",
            "status": lineage_layer_status,
            **_AUTHORITY_BOUNDARY,
        },
        {
            "schema": "AALVizRenderLayer.v1",
            "layer_id": "runtime_health_overlay_layer",
            "visible_by_default": True,
            "node_refs": select_nodes("benchmark_surface_node"),
            "edge_refs": select_edges("drift_edge"),
            "advisory_flags": ["projection_only", "advisory_only", "render_only"],
            "layout_hint": "layered",
            "status": runtime_health_status,
            **_AUTHORITY_BOUNDARY,
        },
        {
            "schema": "AALVizRenderLayer.v1",
            "layer_id": "operator_summary_overlay_layer",
            "visible_by_default": True,
            "node_refs": select_nodes("operator_summary_node"),
            "edge_refs": select_edges("equivalence_edge"),
            "advisory_flags": ["projection_only", "advisory_only", "render_only"],
            "layout_hint": "layered",
            "status": operator_layer_status,
            **_AUTHORITY_BOUNDARY,
        },
    ]
    layers = sorted(layers, key=lambda item: str(item["layer_id"]))

    overlays = [
        {
            "schema": "AALVizRenderOverlay.v1",
            "overlay_id": "drift_overlay",
            "overlay_category": "drift",
            "layer_ref": "drift_overlay_layer",
            "visible_by_default": True,
            "status": drift_layer_status,
            "semantic_tokens": ["overlay.drift", "severity.badge"],
            **_AUTHORITY_BOUNDARY,
        },
        {
            "schema": "AALVizRenderOverlay.v1",
            "overlay_id": "lineage_overlay",
            "overlay_category": "lineage",
            "layer_ref": "lineage_overlay_layer",
            "visible_by_default": True,
            "status": lineage_layer_status,
            "semantic_tokens": ["overlay.lineage", "status.badge"],
            **_AUTHORITY_BOUNDARY,
        },
        {
            "schema": "AALVizRenderOverlay.v1",
            "overlay_id": "runtime_health_overlay",
            "overlay_category": "runtime_health",
            "layer_ref": "runtime_health_overlay_layer",
            "visible_by_default": True,
            "status": runtime_health_status,
            "semantic_tokens": ["overlay.runtime", "status.badge"],
            **_AUTHORITY_BOUNDARY,
        },
        {
            "schema": "AALVizRenderOverlay.v1",
            "overlay_id": "operator_summary_overlay",
            "overlay_category": "operator_summary",
            "layer_ref": "operator_summary_overlay_layer",
            "visible_by_default": True,
            "status": operator_layer_status,
            "semantic_tokens": ["overlay.operator", "status.badge"],
            **_AUTHORITY_BOUNDARY,
        },
    ]
    overlays = sorted(overlays, key=lambda item: str(item["overlay_id"]))

    timeline_tracks: list[dict[str, Any]] = []
    if isinstance(chronoscope, dict):
        for window in sorted(
            [item for item in chronoscope.get("timeline_windows", []) if isinstance(item, dict)],
            key=lambda item: str(item.get("window_id", "")),
        ):
            point_ids = [str(item) for item in window.get("timeline_point_ids", [])]
            timeline_tracks.append(
                {
                    "schema": "AALVizTimelineRenderTrack.v1",
                    "track_id": str(window.get("window_id", "")),
                    "track_kind": "window",
                    "timeline_point_refs": point_ids,
                    "window_status": str(window.get("window_status", "PRESENT")),
                    "semantic_tokens": ["track.timeline", "status.badge"],
                    **_AUTHORITY_BOUNDARY,
                }
            )
    timeline_tracks = sorted(timeline_tracks, key=lambda item: str(item["track_id"]))

    visualization_hints = {
        "schema": "AALVizGraphRenderHints.v1",
        "layout_hint": {
            "replay_topology_layer": "DAG",
            "temporal_snapshot_layer": "layered",
            "projection_bus_layer": "layered",
            "chronoscope_timeline_layer": "timeline",
            "drift_overlay_layer": "radial",
            "lineage_overlay_layer": "DAG",
            "runtime_health_overlay_layer": "layered",
            "operator_summary_overlay_layer": "layered",
        },
        "node_grouping": {
            "group.replay": select_nodes("replay_node"),
            "group.timeline": select_nodes("timeline_point_node"),
            "group.snapshot": select_nodes("snapshot_node"),
            "group.bus": select_nodes("bus_message_node"),
        },
        "edge_grouping": {
            "group.replay": select_edges("dependency_edge"),
            "group.timeline": select_edges("cursor_edge") + select_edges("window_edge"),
            "group.lineage": select_edges("lineage_edge"),
            "group.bus": select_edges("message_edge"),
            "group.drift": select_edges("drift_edge"),
        },
        "status_badges": sorted(
            {
                f"{layer['layer_id']}:{layer['status']}"
                for layer in layers
            }
        ),
        "severity_badges": sorted(
            {
                "severity.warning" if any(select_nodes("drift_event_node")) else "severity.none",
                "severity.blocked"
                if any(str(layer.get("status")) == BLOCKED for layer in layers)
                else "severity.none",
            }
        ),
        "timeline_tracks": [track["track_id"] for track in timeline_tracks],
        "focus_candidates": sorted(
            [
                "replay_topology_layer",
                "chronoscope_timeline_layer",
                "drift_overlay_layer",
                "operator_summary_overlay_layer",
            ]
        ),
        "blocked_not_computable": sorted(
            [
                layer["layer_id"]
                for layer in layers
                if str(layer.get("status")) in {BLOCKED, NOT_COMPUTABLE}
            ]
        ),
        "semantic_tokens": [
            "status.badge",
            "severity.badge",
            "layout.token",
            "projection_only",
            "advisory_only",
            "render_only",
        ],
        **_AUTHORITY_BOUNDARY,
    }

    remaining_blockers = sorted(
        {
            f"missing_artifact:{entry['source_path']}"
            for entry in source_entries
            if str(entry.get("source_status")) == NOT_COMPUTABLE
        }
        | {
            "blocked_layer:chronoscope_timeline_layer"
            if chronoscope_layer_status == BLOCKED
            else ""
        }
        | {
            "blocked_layer:lineage_overlay_layer"
            if lineage_layer_status == BLOCKED
            else ""
        }
    )
    remaining_blockers = [item for item in remaining_blockers if item]

    if not nodes:
        final_status = NOT_COMPUTABLE
    elif any(str(layer.get("status")) == BLOCKED for layer in layers):
        final_status = BLOCKED
    elif any(str(entry.get("source_status")) == NOT_COMPUTABLE for entry in source_entries):
        final_status = "ADVISORY_ONLY"
    elif any(str(layer.get("status")) == NOT_COMPUTABLE for layer in layers):
        final_status = "ADVISORY_ONLY"
    else:
        final_status = "PASS"

    packet_hash = canonical_hash(
        {
            "packet_id": packet_id,
            "patch_id": PATCH_ID,
            "node_ids": [node["node_id"] for node in nodes],
            "edge_ids": [edge["edge_id"] for edge in edges],
            "layer_statuses": {layer["layer_id"]: layer["status"] for layer in layers},
            "overlay_statuses": {overlay["overlay_id"]: overlay["status"] for overlay in overlays},
            "timeline_tracks": [track["track_id"] for track in timeline_tracks],
            "remaining_blockers": remaining_blockers,
        }
    )

    return {
        "schema": "AALVizGraphRenderPacket.v1",
        "patch_id": PATCH_ID,
        "packet_id": packet_id,
        "packet_hash": packet_hash,
        "source_entries": source_entries,
        "nodes": nodes,
        "edges": edges,
        "layers": layers,
        "overlays": overlays,
        "timeline_tracks": timeline_tracks,
        "visualization_hints": visualization_hints,
        "render_advisory_flags": [
            "projection_only",
            "advisory_only",
            "render_only",
            "deterministic_render_packet",
            "no_visualization_authority",
            "fail_closed",
        ],
        "render_node_count": len(nodes),
        "render_edge_count": len(edges),
        "render_layer_count": len(layers),
        "render_overlay_count": len(overlays),
        "render_blocker_count": len(remaining_blockers),
        "operator_action_queue_status": operator_action_queue_summary[
            "operator_action_queue_status"
        ],
        "operator_action_item_count": operator_action_queue_summary[
            "operator_action_item_count"
        ],
        "pending_approval_count": operator_action_queue_summary[
            "pending_approval_count"
        ],
        "escalation_count": operator_action_queue_summary["escalation_count"],
        "top_action_categories": operator_action_queue_summary[
            "top_action_categories"
        ],
        "queue_advisory_flags": operator_action_queue_summary[
            "queue_advisory_flags"
        ],
        "temporal_state_diff_status": operator_action_queue_summary[
            "temporal_state_diff_status"
        ],
        "total_change_count": operator_action_queue_summary["total_change_count"],
        "topology_change_count": operator_action_queue_summary[
            "topology_change_count"
        ],
        "lineage_shift_count": operator_action_queue_summary["lineage_shift_count"],
        "drift_acceleration_status": operator_action_queue_summary[
            "drift_acceleration_status"
        ],
        "replay_equivalence_change_status": operator_action_queue_summary[
            "replay_equivalence_change_status"
        ],
        "queue_delta_count": operator_action_queue_summary["queue_delta_count"],
        "transport_delta_count": operator_action_queue_summary[
            "transport_delta_count"
        ],
        "diff_advisory_flags": operator_action_queue_summary["diff_advisory_flags"],
        "multi_run_convergence_status": operator_action_queue_summary[
            "multi_run_convergence_status"
        ],
        "regime_classification": operator_action_queue_summary[
            "regime_classification"
        ],
        "convergence_evidence_count": operator_action_queue_summary[
            "convergence_evidence_count"
        ],
        "topology_persistence_ratio": operator_action_queue_summary[
            "topology_persistence_ratio"
        ],
        "drift_persistence_ratio": operator_action_queue_summary[
            "drift_persistence_ratio"
        ],
        "lineage_persistence_ratio": operator_action_queue_summary[
            "lineage_persistence_ratio"
        ],
        "replay_stability_status": operator_action_queue_summary[
            "replay_stability_status"
        ],
        "transport_stability_status": operator_action_queue_summary[
            "transport_stability_status"
        ],
        "queue_stability_status": operator_action_queue_summary[
            "queue_stability_status"
        ],
        "blocker_persistence_status": operator_action_queue_summary[
            "blocker_persistence_status"
        ],
        "convergence_advisory_flags": operator_action_queue_summary[
            "convergence_advisory_flags"
        ],
        "final_status": final_status,
        "remaining_blockers": remaining_blockers,
        **_AUTHORITY_BOUNDARY,
    }


def write_aal_viz_graph_render_packet(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_aal_viz_graph_render_markdown(packet: dict[str, Any]) -> str:
    blocked_layers = [
        layer["layer_id"]
        for layer in packet.get("layers", [])
        if isinstance(layer, dict) and str(layer.get("status")) == BLOCKED
    ]
    not_computable_layers = [
        layer["layer_id"]
        for layer in packet.get("layers", [])
        if isinstance(layer, dict) and str(layer.get("status")) == NOT_COMPUTABLE
    ]

    source_paths = {
        str(entry.get("source_key")): str(entry.get("source_path"))
        for entry in packet.get("source_entries", [])
        if isinstance(entry, dict)
    }
    runtime_projection_payload = _load_artifact(source_paths.get("runtime_projection"))
    operator_actions = (
        runtime_projection_payload.get("operator_summary", {}).get("next_actions", [])
        if isinstance(runtime_projection_payload, dict)
        else []
    )

    lines = [
        f"# AAL-Viz Graph Render Packet — {packet.get('packet_id', '')}",
        "",
        f"**Patch:** `{packet.get('patch_id', '')}`",
        f"**Final Status:** `{packet.get('final_status', '')}`",
        f"**Node Count:** `{packet.get('render_node_count', 0)}`",
        f"**Edge Count:** `{packet.get('render_edge_count', 0)}`",
        f"**Layer Count:** `{packet.get('render_layer_count', 0)}`",
        f"**Overlay Count:** `{packet.get('render_overlay_count', 0)}`",
        "",
        "## Operator Action Queue",
        f"- Status: `{packet.get('operator_action_queue_status', NOT_COMPUTABLE)}`",
        f"- Queue items: `{packet.get('operator_action_item_count', 0)}`",
        f"- Pending approvals: `{packet.get('pending_approval_count', 0)}`",
        f"- Escalations: `{packet.get('escalation_count', 0)}`",
        "",
        "## Temporal State Diff",
        f"- Status: `{packet.get('temporal_state_diff_status', NOT_COMPUTABLE)}`",
        f"- Total changes: `{packet.get('total_change_count', 0)}`",
        f"- Topology changes: `{packet.get('topology_change_count', 0)}`",
        f"- Lineage shifts: `{packet.get('lineage_shift_count', 0)}`",
        (
            f"- Drift acceleration: "
            f"`{packet.get('drift_acceleration_status', NOT_COMPUTABLE)}`"
        ),
        (
            f"- Replay equivalence changes: "
            f"`{packet.get('replay_equivalence_change_status', NOT_COMPUTABLE)}`"
        ),
        f"- Queue deltas: `{packet.get('queue_delta_count', 0)}`",
        f"- Transport deltas: `{packet.get('transport_delta_count', 0)}`",
        "",
        "## Blocked Surfaces",
    ]

    if blocked_layers:
        for layer_id in blocked_layers:
            lines.append(f"- `{layer_id}`")
    else:
        lines.append("- None")

    lines.extend(["", "## NOT_COMPUTABLE Surfaces"])
    if not_computable_layers:
        for layer_id in not_computable_layers:
            lines.append(f"- `{layer_id}`")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Render-Only Posture",
            "- projection_only: `true`",
            "- advisory_only: `true`",
            "- render_only: `true`",
            "- authority_granted: `false`",
            "- mutation_allowed: `false`",
            "- promotion_allowed: `false`",
            "- inference_authority: `false`",
            "",
            "## Operator Next Actions",
        ]
    )

    if operator_actions:
        for action in operator_actions:
            lines.append(f"- {action}")
    elif packet.get("remaining_blockers"):
        lines.append("- Resolve missing/corrupt projection artifacts and rerun graph render packet.")
    else:
        lines.append("- Continue advisory-only render packet inspection.")

    lines.append("")
    return "\n".join(lines)
