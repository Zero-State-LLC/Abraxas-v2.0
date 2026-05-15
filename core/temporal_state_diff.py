"""Deterministic temporal state diff and change-detection spine for P14-P19 surfaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P20-TEMPORAL-STATE-DIFF-AND-CHANGE-DETECTION-SPINE-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_CHANGE_TYPE_ORDER = {
    "NO_CHANGE": 0,
    "ADDED": 1,
    "REMOVED": 2,
    "MODIFIED": 3,
    "STATUS_CHANGED": 4,
    "HASH_CHANGED": 5,
    "LINEAGE_SHIFT": 6,
    "TOPOLOGY_SHIFT": 7,
    "DRIFT_ACCELERATION": 8,
    "REPLAY_EQUIVALENCE_SHIFT": 9,
    "TRANSPORT_DELTA": 10,
    "QUEUE_DELTA": 11,
    NOT_COMPUTABLE: 12,
    BLOCKED: 13,
}

_SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
}

_INVARIANTS: dict[str, Any] = {
    "projection_only": True,
    "advisory_only": True,
    "diff_only": True,
    "detection_only": True,
    "execution_authority": False,
    "authority_granted": False,
    "mutation_allowed": False,
    "promotion_allowed": False,
    "auto_execute": False,
    "auto_approve": False,
    "command_channel": False,
    "bidirectional_control": False,
    "inference_authority": False,
}

_FORBIDDEN_TRUE_FLAGS = {
    "execution_authority",
    "authority_granted",
    "mutation_allowed",
    "promotion_allowed",
    "auto_execute",
    "auto_approve",
    "command_channel",
    "bidirectional_control",
    "inference_authority",
}


def _load_artifact(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _safe_hash(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    try:
        return str(canonical_hash(payload))
    except Exception:
        return None


def _scan_forbidden_true_flags(payload: Any, prefix: str = "") -> list[str]:
    matches: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_str = str(key)
            path = f"{prefix}.{key_str}" if prefix else key_str
            if key_str in _FORBIDDEN_TRUE_FLAGS and value is True:
                matches.append(path)
            matches.extend(_scan_forbidden_true_flags(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            matches.extend(_scan_forbidden_true_flags(value, path))
    return sorted(set(matches))


def _make_entry(
    *,
    change_type: str,
    source_surface: str,
    severity: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    entry_id = canonical_hash(
        {
            "change_type": change_type,
            "source_surface": source_surface,
            "severity": severity,
            "evidence": evidence,
        }
    )
    return {
        "schema": "TemporalStateDiffEntry.v1",
        "entry_id": entry_id,
        "change_type": change_type,
        "source_surface": source_surface,
        "severity": severity,
        "evidence": evidence,
        **_INVARIANTS,
    }


def _entry_sort_key(entry: dict[str, Any]) -> tuple[int, str, int, str]:
    return (
        _CHANGE_TYPE_ORDER.get(str(entry.get("change_type", "")), 999),
        str(entry.get("source_surface", "")),
        _SEVERITY_ORDER.get(str(entry.get("severity", "LOW")), 999),
        str(entry.get("entry_id", "")),
    )


def _index_by(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        value = item.get(key)
        if isinstance(value, str) and value:
            indexed[value] = item
    return indexed


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _compare_indexed_entities(
    *,
    previous_items: list[dict[str, Any]],
    current_items: list[dict[str, Any]],
    id_field: str,
    source_surface: str,
    tracked_fields: list[str],
    severity: str,
) -> tuple[list[dict[str, Any]], int, int, int]:
    previous_index = _index_by(previous_items, id_field)
    current_index = _index_by(current_items, id_field)

    previous_ids = set(previous_index)
    current_ids = set(current_index)

    entries: list[dict[str, Any]] = []
    added = 0
    removed = 0
    modified = 0

    for entity_id in sorted(current_ids - previous_ids):
        added += 1
        entries.append(
            _make_entry(
                change_type="ADDED",
                source_surface=source_surface,
                severity=severity,
                evidence={"entity_id": entity_id, "id_field": id_field},
            )
        )

    for entity_id in sorted(previous_ids - current_ids):
        removed += 1
        entries.append(
            _make_entry(
                change_type="REMOVED",
                source_surface=source_surface,
                severity=severity,
                evidence={"entity_id": entity_id, "id_field": id_field},
            )
        )

    for entity_id in sorted(previous_ids & current_ids):
        before = previous_index[entity_id]
        after = current_index[entity_id]
        changed_fields = [
            field for field in tracked_fields if before.get(field) != after.get(field)
        ]
        if changed_fields:
            modified += 1
            entries.append(
                _make_entry(
                    change_type="MODIFIED",
                    source_surface=source_surface,
                    severity=severity,
                    evidence={
                        "entity_id": entity_id,
                        "changed_fields": changed_fields,
                        "before": {field: before.get(field) for field in changed_fields},
                        "after": {field: after.get(field) for field in changed_fields},
                    },
                )
            )

    return entries, added, removed, modified


def _compare_temporal_snapshot_spine(
    previous_payload: dict[str, Any], current_payload: dict[str, Any]
) -> tuple[list[dict[str, Any]], int]:
    previous_snapshots = _as_dict_list(previous_payload.get("ordered_snapshots"))
    current_snapshots = _as_dict_list(current_payload.get("ordered_snapshots"))

    entries: list[dict[str, Any]] = []
    node_entries, added, removed, modified = _compare_indexed_entities(
        previous_items=previous_snapshots,
        current_items=current_snapshots,
        id_field="snapshot_id",
        source_surface="temporal_snapshot_spine.snapshot_node",
        tracked_fields=["projection_hash", "source_hash", "deterministic_timestamp", "cursor"],
        severity="MEDIUM",
    )
    entries.extend(node_entries)

    previous_index = _index_by(previous_snapshots, "snapshot_id")
    current_index = _index_by(current_snapshots, "snapshot_id")

    lineage_shift_count = 0
    for snapshot_id in sorted(set(previous_index) & set(current_index)):
        before = previous_index[snapshot_id]
        after = current_index[snapshot_id]
        if (
            before.get("lineage_prev") != after.get("lineage_prev")
            or before.get("lineage_next") != after.get("lineage_next")
        ):
            lineage_shift_count += 1
            entries.append(
                _make_entry(
                    change_type="LINEAGE_SHIFT",
                    source_surface="temporal_snapshot_spine.lineage",
                    severity="HIGH",
                    evidence={
                        "snapshot_id": snapshot_id,
                        "before": {
                            "lineage_prev": before.get("lineage_prev"),
                            "lineage_next": before.get("lineage_next"),
                        },
                        "after": {
                            "lineage_prev": after.get("lineage_prev"),
                            "lineage_next": after.get("lineage_next"),
                        },
                    },
                )
            )

    topology_change_count = added + removed + modified
    if topology_change_count > 0:
        entries.append(
            _make_entry(
                change_type="TOPOLOGY_SHIFT",
                source_surface="temporal_snapshot_spine",
                severity="HIGH",
                evidence={
                    "added_node_count": added,
                    "removed_node_count": removed,
                    "modified_node_count": modified,
                },
            )
        )

    return entries, lineage_shift_count


def _compare_projection_bus(
    previous_payload: dict[str, Any], current_payload: dict[str, Any]
) -> list[dict[str, Any]]:
    previous_messages = _as_dict_list(previous_payload.get("messages"))
    current_messages = _as_dict_list(current_payload.get("messages"))
    entries, _, _, _ = _compare_indexed_entities(
        previous_items=previous_messages,
        current_items=current_messages,
        id_field="message_id",
        source_surface="projection_bus.message",
        tracked_fields=["snapshot_id", "cursor", "topic", "projection_hash", "source_hash"],
        severity="LOW",
    )

    previous_status = previous_payload.get("final_status")
    current_status = current_payload.get("final_status")
    if previous_status != current_status:
        entries.append(
            _make_entry(
                change_type="STATUS_CHANGED",
                source_surface="projection_bus",
                severity="MEDIUM",
                evidence={"before": previous_status, "after": current_status},
            )
        )
    return entries


def _drift_value(drift_timeline: dict[str, Any], key: str) -> int | float | str:
    value = drift_timeline.get(key, NOT_COMPUTABLE)
    if isinstance(value, int | float):
        return value
    return NOT_COMPUTABLE


def _drift_acceleration_summary(
    previous_payload: dict[str, Any] | None,
    current_payload: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if previous_payload is None or current_payload is None:
        summary = {
            "schema": "DriftAccelerationSummary.v1",
            "drift_acceleration_status": NOT_COMPUTABLE,
            "reason": "missing_previous_or_current_drift_evidence",
            "drift_count_increase": NOT_COMPUTABLE,
            "drift_rate_increase": NOT_COMPUTABLE,
            "blocked_window_increase": NOT_COMPUTABLE,
            "lineage_gap_increase": NOT_COMPUTABLE,
            "corrupt_lineage_increase": NOT_COMPUTABLE,
            "not_computable_increase": NOT_COMPUTABLE,
            **_INVARIANTS,
        }
        return summary, [
            _make_entry(
                change_type=NOT_COMPUTABLE,
                source_surface="projection_chronoscope.drift_acceleration",
                severity="MEDIUM",
                evidence={"reason": "missing_previous_or_current_drift_evidence"},
            )
        ]

    previous_drift = previous_payload.get("drift_timeline")
    current_drift = current_payload.get("drift_timeline")
    if not isinstance(previous_drift, dict) or not isinstance(current_drift, dict):
        summary = {
            "schema": "DriftAccelerationSummary.v1",
            "drift_acceleration_status": NOT_COMPUTABLE,
            "reason": "drift_timeline_missing_or_invalid",
            "drift_count_increase": NOT_COMPUTABLE,
            "drift_rate_increase": NOT_COMPUTABLE,
            "blocked_window_increase": NOT_COMPUTABLE,
            "lineage_gap_increase": NOT_COMPUTABLE,
            "corrupt_lineage_increase": NOT_COMPUTABLE,
            "not_computable_increase": NOT_COMPUTABLE,
            **_INVARIANTS,
        }
        return summary, [
            _make_entry(
                change_type=NOT_COMPUTABLE,
                source_surface="projection_chronoscope.drift_acceleration",
                severity="MEDIUM",
                evidence={"reason": "drift_timeline_missing_or_invalid"},
            )
        ]

    previous_count = _drift_value(previous_drift, "drift_event_count")
    current_count = _drift_value(current_drift, "drift_event_count")
    previous_rate = _drift_value(previous_drift, "drift_rate")
    current_rate = _drift_value(current_drift, "drift_rate")
    previous_blocked = _drift_value(previous_drift, "blocked_window_count")
    current_blocked = _drift_value(current_drift, "blocked_window_count")
    previous_lineage_gap = _drift_value(previous_drift, "lineage_gap_count")
    current_lineage_gap = _drift_value(current_drift, "lineage_gap_count")
    previous_corrupt_lineage = _drift_value(previous_drift, "corrupt_lineage_count")
    current_corrupt_lineage = _drift_value(current_drift, "corrupt_lineage_count")
    previous_not_computable = _drift_value(previous_drift, "not_computable_source_count")
    current_not_computable = _drift_value(current_drift, "not_computable_source_count")

    drift_count_increase = (
        current_count > previous_count
        if isinstance(previous_count, int | float) and isinstance(current_count, int | float)
        else NOT_COMPUTABLE
    )
    drift_rate_increase = (
        current_rate > previous_rate
        if isinstance(previous_rate, int | float) and isinstance(current_rate, int | float)
        else NOT_COMPUTABLE
    )
    blocked_window_increase = (
        current_blocked > previous_blocked
        if isinstance(previous_blocked, int | float)
        and isinstance(current_blocked, int | float)
        else NOT_COMPUTABLE
    )
    lineage_gap_increase = (
        current_lineage_gap > previous_lineage_gap
        if isinstance(previous_lineage_gap, int | float)
        and isinstance(current_lineage_gap, int | float)
        else NOT_COMPUTABLE
    )
    corrupt_lineage_increase = (
        current_corrupt_lineage > previous_corrupt_lineage
        if isinstance(previous_corrupt_lineage, int | float)
        and isinstance(current_corrupt_lineage, int | float)
        else NOT_COMPUTABLE
    )
    not_computable_increase = (
        current_not_computable > previous_not_computable
        if isinstance(previous_not_computable, int | float)
        and isinstance(current_not_computable, int | float)
        else NOT_COMPUTABLE
    )

    boolean_signals = [
        signal
        for signal in [
            drift_count_increase,
            drift_rate_increase,
            blocked_window_increase,
            lineage_gap_increase,
            corrupt_lineage_increase,
            not_computable_increase,
        ]
        if isinstance(signal, bool)
    ]

    if not boolean_signals:
        status = NOT_COMPUTABLE
    elif any(boolean_signals):
        status = "DRIFT_ACCELERATING"
    else:
        status = "NO_ACCELERATION"

    summary = {
        "schema": "DriftAccelerationSummary.v1",
        "drift_acceleration_status": status,
        "drift_count_increase": drift_count_increase,
        "drift_rate_increase": drift_rate_increase,
        "blocked_window_increase": blocked_window_increase,
        "lineage_gap_increase": lineage_gap_increase,
        "corrupt_lineage_increase": corrupt_lineage_increase,
        "not_computable_increase": not_computable_increase,
        **_INVARIANTS,
    }

    entries: list[dict[str, Any]] = []
    if status == "DRIFT_ACCELERATING":
        entries.append(
            _make_entry(
                change_type="DRIFT_ACCELERATION",
                source_surface="projection_chronoscope.drift_timeline",
                severity="HIGH",
                evidence={
                    "drift_count_increase": drift_count_increase,
                    "drift_rate_increase": drift_rate_increase,
                    "blocked_window_increase": blocked_window_increase,
                    "lineage_gap_increase": lineage_gap_increase,
                    "corrupt_lineage_increase": corrupt_lineage_increase,
                    "not_computable_increase": not_computable_increase,
                },
            )
        )
    elif status == NOT_COMPUTABLE:
        entries.append(
            _make_entry(
                change_type=NOT_COMPUTABLE,
                source_surface="projection_chronoscope.drift_acceleration",
                severity="MEDIUM",
                evidence={"reason": "insufficient_numeric_drift_evidence"},
            )
        )

    return summary, entries


def _compare_projection_chronoscope(
    previous_payload: dict[str, Any], current_payload: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
    entries: list[dict[str, Any]] = []

    previous_points = _as_dict_list(previous_payload.get("timeline_points"))
    current_points = _as_dict_list(current_payload.get("timeline_points"))
    point_entries, _, _, _ = _compare_indexed_entities(
        previous_items=previous_points,
        current_items=current_points,
        id_field="timeline_point_id",
        source_surface="projection_chronoscope.timeline_point",
        tracked_fields=["snapshot_id", "cursor", "topic", "link_status", "message_id"],
        severity="MEDIUM",
    )
    entries.extend(point_entries)

    previous_trend = (
        previous_payload.get("drift_timeline", {})
        if isinstance(previous_payload.get("drift_timeline"), dict)
        else {}
    ).get("projection_equivalence_trend", NOT_COMPUTABLE)
    current_trend = (
        current_payload.get("drift_timeline", {})
        if isinstance(current_payload.get("drift_timeline"), dict)
        else {}
    ).get("projection_equivalence_trend", NOT_COMPUTABLE)
    replay_equivalence_change_status = "NO_CHANGE"
    if previous_trend != current_trend:
        replay_equivalence_change_status = "SHIFT_DETECTED"
        entries.append(
            _make_entry(
                change_type="REPLAY_EQUIVALENCE_SHIFT",
                source_surface="projection_chronoscope.replay_equivalence",
                severity="HIGH",
                evidence={"before": previous_trend, "after": current_trend},
            )
        )

    previous_status = previous_payload.get("final_status")
    current_status = current_payload.get("final_status")
    if previous_status != current_status:
        entries.append(
            _make_entry(
                change_type="STATUS_CHANGED",
                source_surface="projection_chronoscope",
                severity="MEDIUM",
                evidence={"before": previous_status, "after": current_status},
            )
        )

    drift_summary, drift_entries = _drift_acceleration_summary(previous_payload, current_payload)
    entries.extend(drift_entries)

    return entries, drift_summary, replay_equivalence_change_status


def _compare_graph_render_packet(
    previous_payload: dict[str, Any], current_payload: dict[str, Any]
) -> tuple[list[dict[str, Any]], int]:
    entries: list[dict[str, Any]] = []

    prev_nodes = _as_dict_list(previous_payload.get("nodes"))
    curr_nodes = _as_dict_list(current_payload.get("nodes"))
    node_entries, add_nodes, remove_nodes, modify_nodes = _compare_indexed_entities(
        previous_items=prev_nodes,
        current_items=curr_nodes,
        id_field="node_id",
        source_surface="aal_viz_graph_render_packet.node",
        tracked_fields=["category", "status", "source_ref"],
        severity="MEDIUM",
    )
    entries.extend(node_entries)

    prev_edges = _as_dict_list(previous_payload.get("edges"))
    curr_edges = _as_dict_list(current_payload.get("edges"))
    edge_entries, add_edges, remove_edges, modify_edges = _compare_indexed_entities(
        previous_items=prev_edges,
        current_items=curr_edges,
        id_field="edge_id",
        source_surface="aal_viz_graph_render_packet.edge",
        tracked_fields=["category", "status", "source_node_id", "target_node_id"],
        severity="MEDIUM",
    )
    entries.extend(edge_entries)

    layer_entries, _, _, _ = _compare_indexed_entities(
        previous_items=_as_dict_list(previous_payload.get("layers")),
        current_items=_as_dict_list(current_payload.get("layers")),
        id_field="layer_id",
        source_surface="aal_viz_graph_render_packet.layer",
        tracked_fields=["status", "node_refs", "edge_refs"],
        severity="LOW",
    )
    entries.extend(layer_entries)

    overlay_entries, _, _, _ = _compare_indexed_entities(
        previous_items=_as_dict_list(previous_payload.get("overlays")),
        current_items=_as_dict_list(current_payload.get("overlays")),
        id_field="overlay_id",
        source_surface="aal_viz_graph_render_packet.overlay",
        tracked_fields=["status", "layer_ref"],
        severity="LOW",
    )
    entries.extend(overlay_entries)

    topology_change_count = (
        add_nodes + remove_nodes + modify_nodes + add_edges + remove_edges + modify_edges
    )
    if topology_change_count > 0:
        entries.append(
            _make_entry(
                change_type="TOPOLOGY_SHIFT",
                source_surface="aal_viz_graph_render_packet",
                severity="HIGH",
                evidence={
                    "added_node_count": add_nodes,
                    "removed_node_count": remove_nodes,
                    "modified_node_count": modify_nodes,
                    "added_edge_count": add_edges,
                    "removed_edge_count": remove_edges,
                    "modified_edge_count": modify_edges,
                },
            )
        )

    return entries, topology_change_count


def _compare_queue(
    previous_payload: dict[str, Any], current_payload: dict[str, Any]
) -> tuple[list[dict[str, Any]], int]:
    entries: list[dict[str, Any]] = []

    item_entries, added, removed, modified = _compare_indexed_entities(
        previous_items=_as_dict_list(previous_payload.get("operator_action_items")),
        current_items=_as_dict_list(current_payload.get("operator_action_items")),
        id_field="item_id",
        source_surface="operator_action_queue.item",
        tracked_fields=[
            "category",
            "severity",
            "source_artifact",
            "related_blockers",
            "evidence",
        ],
        severity="MEDIUM",
    )
    entries.extend(item_entries)

    queue_delta_count = added + removed + modified
    if queue_delta_count > 0:
        entries.append(
            _make_entry(
                change_type="QUEUE_DELTA",
                source_surface="operator_action_queue",
                severity="HIGH",
                evidence={
                    "added_item_count": added,
                    "removed_item_count": removed,
                    "modified_item_count": modified,
                    "before": {
                        "operator_action_item_count": previous_payload.get(
                            "operator_action_item_count", 0
                        ),
                        "pending_approval_count": previous_payload.get(
                            "pending_approval_count", 0
                        ),
                        "escalation_count": previous_payload.get("escalation_count", 0),
                    },
                    "after": {
                        "operator_action_item_count": current_payload.get(
                            "operator_action_item_count", 0
                        ),
                        "pending_approval_count": current_payload.get(
                            "pending_approval_count", 0
                        ),
                        "escalation_count": current_payload.get("escalation_count", 0),
                    },
                },
            )
        )

    return entries, queue_delta_count


def _compare_transport(
    previous_payload: dict[str, Any], current_payload: dict[str, Any]
) -> tuple[list[dict[str, Any]], int]:
    entries: list[dict[str, Any]] = []

    topic_entries, add_topics, remove_topics, modify_topics = _compare_indexed_entities(
        previous_items=_as_dict_list(previous_payload.get("topics")),
        current_items=_as_dict_list(current_payload.get("topics")),
        id_field="topic_id",
        source_surface="read_only_transport.topic",
        tracked_fields=["topic_name", "payload_kind", "source_artifact_path"],
        severity="LOW",
    )
    entries.extend(topic_entries)

    frame_entries, add_frames, remove_frames, modify_frames = _compare_indexed_entities(
        previous_items=_as_dict_list(previous_payload.get("frames")),
        current_items=_as_dict_list(current_payload.get("frames")),
        id_field="frame_id",
        source_surface="read_only_transport.frame",
        tracked_fields=["topic_id", "cursor", "blocker_status", "source_hash", "packet_id"],
        severity="MEDIUM",
    )
    entries.extend(frame_entries)

    transport_delta_count = (
        add_topics + remove_topics + modify_topics + add_frames + remove_frames + modify_frames
    )
    if transport_delta_count > 0:
        entries.append(
            _make_entry(
                change_type="TRANSPORT_DELTA",
                source_surface="read_only_transport",
                severity="HIGH",
                evidence={
                    "added_topic_count": add_topics,
                    "removed_topic_count": remove_topics,
                    "modified_topic_count": modify_topics,
                    "added_frame_count": add_frames,
                    "removed_frame_count": remove_frames,
                    "modified_frame_count": modify_frames,
                    "before_cursor_bounds": previous_payload.get("transport_cursor_bounds"),
                    "after_cursor_bounds": current_payload.get("transport_cursor_bounds"),
                },
            )
        )

    return entries, transport_delta_count


def _surface_paths_from_runtime_paths(paths: RuntimePaths) -> dict[str, Path]:
    return {
        "live_projection_refresh": paths.live_projection_refresh_latest,
        "temporal_snapshot_spine": paths.temporal_snapshot_spine_latest,
        "projection_bus": paths.projection_bus_latest,
        "projection_chronoscope": paths.projection_chronoscope_latest,
        "aal_viz_graph_render_packet": paths.aal_viz_graph_render_packet_latest,
        "operator_action_queue": paths.operator_action_queue_latest,
        "read_only_transport": paths.read_only_transport_latest,
    }


def build_temporal_state_diff_packet(
    *,
    packet_id: str = "temporal_state_diff_001",
    previous_artifact_paths: dict[str, str | Path] | None = None,
    current_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    multi_run_convergence_payload = _load_artifact(paths.multi_run_convergence_latest)
    defaults = _surface_paths_from_runtime_paths(paths)
    previous_paths: dict[str, str | Path] = (
        {**defaults, **previous_artifact_paths}
        if previous_artifact_paths is not None
        else {**defaults}
    )
    current_paths: dict[str, str | Path] = {**defaults, **(current_artifact_paths or {})}

    source_entries: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []

    lineage_shift_count = 0
    topology_change_count = 0
    queue_delta_count = 0
    transport_delta_count = 0
    replay_equivalence_change_status = "NO_CHANGE"
    drift_summary: dict[str, Any] = {
        "schema": "DriftAccelerationSummary.v1",
        "drift_acceleration_status": NOT_COMPUTABLE,
        "reason": "not_evaluated",
        **_INVARIANTS,
    }

    for surface in sorted(defaults):
        previous_path = previous_paths.get(surface)
        current_path = current_paths.get(surface)

        previous_payload = _load_artifact(previous_path)
        current_payload = _load_artifact(current_path)
        previous_hash = _safe_hash(previous_payload)
        current_hash = _safe_hash(current_payload)

        previous_violations = _scan_forbidden_true_flags(previous_payload)
        current_violations = _scan_forbidden_true_flags(current_payload)

        source_entries.append(
            {
                "schema": "TemporalStateDiffSourceEntry.v1",
                "source_surface": surface,
                "previous": {
                    "path": None if previous_path is None else str(previous_path),
                    "status": "PRESENT" if previous_payload is not None else NOT_COMPUTABLE,
                    "source_hash": previous_hash,
                },
                "current": {
                    "path": None if current_path is None else str(current_path),
                    "status": "PRESENT" if current_payload is not None else NOT_COMPUTABLE,
                    "source_hash": current_hash,
                },
                "authority_boundary_violations": {
                    "previous": previous_violations,
                    "current": current_violations,
                },
                **_INVARIANTS,
            }
        )

        if previous_violations or current_violations:
            entries.append(
                _make_entry(
                    change_type=BLOCKED,
                    source_surface=surface,
                    severity="CRITICAL",
                    evidence={
                        "reason": "authority_boundary_violation",
                        "previous_violations": previous_violations,
                        "current_violations": current_violations,
                    },
                )
            )
            continue

        if previous_payload is None or current_payload is None:
            entries.append(
                _make_entry(
                    change_type=NOT_COMPUTABLE,
                    source_surface=surface,
                    severity="HIGH",
                    evidence={
                        "reason": "missing_artifact",
                        "previous_path": None if previous_path is None else str(previous_path),
                        "current_path": None if current_path is None else str(current_path),
                        "previous_present": previous_payload is not None,
                        "current_present": current_payload is not None,
                    },
                )
            )
            continue

        if previous_hash is None or current_hash is None:
            entries.append(
                _make_entry(
                    change_type=BLOCKED,
                    source_surface=surface,
                    severity="HIGH",
                    evidence={"reason": "hash_not_computable"},
                )
            )
            continue

        if previous_hash != current_hash:
            entries.append(
                _make_entry(
                    change_type="HASH_CHANGED",
                    source_surface=surface,
                    severity="MEDIUM",
                    evidence={"before": previous_hash, "after": current_hash},
                )
            )

        if surface == "temporal_snapshot_spine":
            snapshot_entries, lineage_count = _compare_temporal_snapshot_spine(
                previous_payload, current_payload
            )
            entries.extend(snapshot_entries)
            lineage_shift_count += lineage_count
            continue

        if surface == "projection_bus":
            entries.extend(_compare_projection_bus(previous_payload, current_payload))
            continue

        if surface == "projection_chronoscope":
            chronoscope_entries, local_drift_summary, replay_status = (
                _compare_projection_chronoscope(previous_payload, current_payload)
            )
            entries.extend(chronoscope_entries)
            drift_summary = local_drift_summary
            replay_equivalence_change_status = replay_status
            continue

        if surface == "aal_viz_graph_render_packet":
            render_entries, topology_count = _compare_graph_render_packet(
                previous_payload, current_payload
            )
            entries.extend(render_entries)
            topology_change_count += topology_count
            continue

        if surface == "operator_action_queue":
            queue_entries, queue_count = _compare_queue(previous_payload, current_payload)
            entries.extend(queue_entries)
            queue_delta_count += queue_count
            continue

        if surface == "read_only_transport":
            transport_entries, transport_count = _compare_transport(
                previous_payload, current_payload
            )
            entries.extend(transport_entries)
            transport_delta_count += transport_count
            continue

        previous_status = previous_payload.get("final_status")
        current_status = current_payload.get("final_status")
        if previous_status != current_status:
            entries.append(
                _make_entry(
                    change_type="STATUS_CHANGED",
                    source_surface=surface,
                    severity="LOW",
                    evidence={"before": previous_status, "after": current_status},
                )
            )

    entries = sorted(entries, key=_entry_sort_key)

    blocker_entries = [entry for entry in entries if entry["change_type"] == BLOCKED]
    not_computable_entries = [
        entry for entry in entries if entry["change_type"] == NOT_COMPUTABLE
    ]

    total_change_count = len(
        [
            entry
            for entry in entries
            if entry["change_type"] not in {"NO_CHANGE", NOT_COMPUTABLE, BLOCKED}
        ]
    )

    if blocker_entries:
        final_status = BLOCKED
    elif entries and len(not_computable_entries) == len(entries):
        final_status = NOT_COMPUTABLE
    elif total_change_count > 0 or not_computable_entries:
        final_status = "ADVISORY_ONLY"
    else:
        final_status = "PASS"

    topology_change_summary = {
        "schema": "TopologyChangeSummary.v1",
        "topology_change_count": topology_change_count,
        "topology_change_status": "SHIFT_DETECTED" if topology_change_count > 0 else "NO_CHANGE",
        **_INVARIANTS,
    }
    lineage_shift_summary = {
        "schema": "LineageShiftSummary.v1",
        "lineage_shift_count": lineage_shift_count,
        "lineage_shift_status": "SHIFT_DETECTED" if lineage_shift_count > 0 else "NO_CHANGE",
        **_INVARIANTS,
    }
    replay_equivalence_change_summary = {
        "schema": "ReplayEquivalenceChangeSummary.v1",
        "replay_equivalence_change_status": replay_equivalence_change_status,
        **_INVARIANTS,
    }
    queue_change_summary = {
        "schema": "QueueChangeSummary.v1",
        "queue_delta_count": queue_delta_count,
        "queue_delta_status": "SHIFT_DETECTED" if queue_delta_count > 0 else "NO_CHANGE",
        **_INVARIANTS,
    }
    transport_delta_summary = {
        "schema": "TransportDeltaSummary.v1",
        "transport_delta_count": transport_delta_count,
        "transport_delta_status": "SHIFT_DETECTED"
        if transport_delta_count > 0
        else "NO_CHANGE",
        **_INVARIANTS,
    }

    projection_delta_packet = {
        "schema": "ProjectionDeltaPacket.v1",
        "total_change_count": total_change_count,
        "blocked_change_count": len(blocker_entries),
        "not_computable_count": len(not_computable_entries),
        "topology_change_count": topology_change_summary["topology_change_count"],
        "lineage_shift_count": lineage_shift_summary["lineage_shift_count"],
        "queue_delta_count": queue_change_summary["queue_delta_count"],
        "transport_delta_count": transport_delta_summary["transport_delta_count"],
        **_INVARIANTS,
    }

    packet_hash = canonical_hash(
        {
            "packet_id": packet_id,
            "source_entries": source_entries,
            "diff_entries": entries,
            "projection_delta_packet": projection_delta_packet,
            "topology_change_summary": topology_change_summary,
            "lineage_shift_summary": lineage_shift_summary,
            "drift_acceleration_summary": drift_summary,
            "replay_equivalence_change_summary": replay_equivalence_change_summary,
            "queue_change_summary": queue_change_summary,
            "transport_delta_summary": transport_delta_summary,
            "final_status": final_status,
        }
    )

    blockers = sorted(
        {
            f"authority_boundary_violation:{entry['source_surface']}"
            for entry in blocker_entries
            if entry["evidence"].get("reason") == "authority_boundary_violation"
        }
        | {
            f"missing_artifact:{entry['source_surface']}"
            for entry in not_computable_entries
            if entry["evidence"].get("reason") == "missing_artifact"
        }
    )

    return {
        "schema": "TemporalStateDiff.v1",
        "patch_id": PATCH_ID,
        "packet_id": packet_id,
        "packet_hash": packet_hash,
        "source_entries": source_entries,
        "diff_entries": entries,
        "projection_delta_packet": projection_delta_packet,
        "topology_change_summary": topology_change_summary,
        "lineage_shift_summary": lineage_shift_summary,
        "drift_acceleration_summary": drift_summary,
        "replay_equivalence_change_summary": replay_equivalence_change_summary,
        "queue_change_summary": queue_change_summary,
        "transport_delta_summary": transport_delta_summary,
        "temporal_state_diff_status": final_status,
        "total_change_count": total_change_count,
        "topology_change_count": topology_change_summary["topology_change_count"],
        "lineage_shift_count": lineage_shift_summary["lineage_shift_count"],
        "drift_acceleration_status": drift_summary.get(
            "drift_acceleration_status", NOT_COMPUTABLE
        ),
        "replay_equivalence_change_status": replay_equivalence_change_summary[
            "replay_equivalence_change_status"
        ],
        "queue_delta_count": queue_change_summary["queue_delta_count"],
        "transport_delta_count": transport_delta_summary["transport_delta_count"],
        "diff_advisory_flags": sorted(
            {
                "advisory_only",
                "diff_only",
                "detection_only",
                "deterministic_ordering",
                "fail_closed",
                "evidence_backed",
            }
        ),
        "multi_run_convergence_status": str(
            multi_run_convergence_payload.get(
                "multi_run_convergence_status", NOT_COMPUTABLE
            )
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "regime_classification": str(
            multi_run_convergence_payload.get("regime_classification", NOT_COMPUTABLE)
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "convergence_evidence_count": int(
            multi_run_convergence_payload.get("convergence_evidence_count", 0)
            if isinstance(multi_run_convergence_payload, dict)
            else 0
        ),
        "topology_persistence_ratio": float(
            multi_run_convergence_payload.get("topology_persistence_ratio", 0.0)
            if isinstance(multi_run_convergence_payload, dict)
            else 0.0
        ),
        "drift_persistence_ratio": float(
            multi_run_convergence_payload.get("drift_persistence_ratio", 0.0)
            if isinstance(multi_run_convergence_payload, dict)
            else 0.0
        ),
        "lineage_persistence_ratio": float(
            multi_run_convergence_payload.get("lineage_persistence_ratio", 0.0)
            if isinstance(multi_run_convergence_payload, dict)
            else 0.0
        ),
        "replay_stability_status": str(
            multi_run_convergence_payload.get("replay_stability_status", NOT_COMPUTABLE)
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "transport_stability_status": str(
            multi_run_convergence_payload.get(
                "transport_stability_status", NOT_COMPUTABLE
            )
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "queue_stability_status": str(
            multi_run_convergence_payload.get("queue_stability_status", NOT_COMPUTABLE)
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "blocker_persistence_status": str(
            multi_run_convergence_payload.get(
                "blocker_persistence_status", NOT_COMPUTABLE
            )
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "convergence_advisory_flags": [
            str(item)
            for item in (
                multi_run_convergence_payload.get("convergence_advisory_flags", [])
                if isinstance(multi_run_convergence_payload, dict)
                else []
            )
        ],
        "final_status": final_status,
        "remaining_blockers": blockers,
        **_INVARIANTS,
    }


def write_temporal_state_diff_packet(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_temporal_state_diff_markdown(packet: dict[str, Any]) -> str:
    lines = [
        f"# Temporal State Diff — {packet.get('packet_id', '')}",
        "",
        f"**Patch:** `{packet.get('patch_id', '')}`",
        f"**Final Status:** `{packet.get('final_status', '')}`",
        f"**Total Changes:** `{packet.get('total_change_count', 0)}`",
        f"**Topology Changes:** `{packet.get('topology_change_count', 0)}`",
        f"**Lineage Shifts:** `{packet.get('lineage_shift_count', 0)}`",
        (
            f"**Drift Acceleration Status:** "
            f"`{packet.get('drift_acceleration_status', NOT_COMPUTABLE)}`"
        ),
        (
            "**Replay Equivalence Change Status:** "
            f"`{packet.get('replay_equivalence_change_status', NOT_COMPUTABLE)}`"
        ),
        f"**Queue Deltas:** `{packet.get('queue_delta_count', 0)}`",
        f"**Transport Deltas:** `{packet.get('transport_delta_count', 0)}`",
        "",
        "## Blockers",
    ]
    blockers = [str(item) for item in packet.get("remaining_blockers", [])]
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Operator Next Actions"])
    if blockers:
        lines.append("- Review missing/corrupt artifacts and authority-boundary violations.")
        lines.append("- Re-run temporal state diff after upstream evidence is refreshed.")
    elif packet.get("total_change_count", 0):
        lines.append("- Review detected deltas and preserve advisory-only posture.")
    else:
        lines.append("- Continue deterministic advisory-only monitoring.")

    lines.append("")
    return "\n".join(lines)
