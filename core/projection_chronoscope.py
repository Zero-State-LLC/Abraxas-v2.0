"""Deterministic projection chronoscope timeline layer over P15 artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P16-TEMPORAL-CHRONOSCOPE-AND-PROJECTION-TIMELINE-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_AUTHORITY_BOUNDARY: dict[str, Any] = {
    "projection_only": True,
    "advisory_only": True,
    "authority_granted": False,
    "mutation_allowed": False,
    "promotion_allowed": False,
    "inference_authority": False,
}


def _load_artifact(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        text = Path(path).read_text(encoding="utf-8")
        return json.loads(text)  # type: ignore[no-any-return]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _sorted_snapshots(temporal_snapshot_index: dict[str, Any]) -> list[dict[str, Any]]:
    snapshots = [
        snapshot
        for snapshot in temporal_snapshot_index.get("ordered_snapshots", [])
        if isinstance(snapshot, dict)
    ]
    return sorted(
        snapshots,
        key=lambda item: (
            str(item.get("deterministic_timestamp", "")),
            str(item.get("snapshot_id", "")),
        ),
    )


def _snapshot_to_message_index(
    projection_bus_envelope: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    messages = [
        msg for msg in projection_bus_envelope.get("messages", []) if isinstance(msg, dict)
    ]
    ordered = sorted(
        messages,
        key=lambda msg: (str(msg.get("snapshot_id", "")), str(msg.get("message_id", ""))),
    )
    result: dict[str, dict[str, Any]] = {}
    for message in ordered:
        snapshot_id = str(message.get("snapshot_id", ""))
        if snapshot_id and snapshot_id not in result:
            result[snapshot_id] = message
    return result


def _build_timeline_points(
    temporal_snapshot_index: dict[str, Any],
    projection_bus_envelope: dict[str, Any],
    *,
    topic_filter: list[str] | None,
) -> tuple[list[dict[str, Any]], list[str]]:
    snapshots = _sorted_snapshots(temporal_snapshot_index)
    message_by_snapshot = _snapshot_to_message_index(projection_bus_envelope)
    topic_filter_set = set(topic_filter or [])
    blockers: list[str] = []

    points: list[dict[str, Any]] = []
    for snapshot in snapshots:
        snapshot_id = str(snapshot.get("snapshot_id", ""))
        message = message_by_snapshot.get(snapshot_id)
        topic = str(message.get("topic")) if message is not None else NOT_COMPUTABLE
        if topic_filter and topic not in topic_filter_set:
            continue
        if message is None:
            blockers.append(f"missing_message_link:{snapshot_id}")

        point_id = canonical_hash(
            {
                "snapshot_id": snapshot_id,
                "message_id": None if message is None else message.get("message_id"),
                "cursor": snapshot.get("cursor"),
                "timestamp": snapshot.get("deterministic_timestamp"),
                "topic": topic,
            }
        )
        points.append(
            {
                "schema": "ProjectionTimelinePoint.v1",
                "timeline_point_id": point_id,
                "snapshot_id": snapshot_id,
                "message_id": None if message is None else message.get("message_id"),
                "projection_id": snapshot.get("projection_id"),
                "projection_hash": snapshot.get("projection_hash"),
                "source_hash": snapshot.get("source_hash"),
                "deterministic_timestamp": snapshot.get("deterministic_timestamp"),
                "cursor": snapshot.get("cursor"),
                "topic": topic,
                "lineage_prev": snapshot.get("lineage_prev"),
                "lineage_next": snapshot.get("lineage_next"),
                "link_status": "LINKED" if message is not None else NOT_COMPUTABLE,
                **_AUTHORITY_BOUNDARY,
            }
        )

    points = sorted(
        points,
        key=lambda item: (
            str(item.get("deterministic_timestamp", "")),
            str(item.get("snapshot_id", "")),
            str(item.get("timeline_point_id", "")),
        ),
    )
    for idx, point in enumerate(points):
        point["ordinal"] = idx
    return points, sorted(set(blockers))


def _build_playback_cursors(
    timeline_points: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, str | None]]:
    cursors: list[dict[str, Any]] = []
    for idx, point in enumerate(timeline_points):
        cursor_value = str(point.get("cursor", ""))
        prev_cursor = (
            str(timeline_points[idx - 1].get("cursor", "")) if idx > 0 else None
        )
        next_cursor = (
            str(timeline_points[idx + 1].get("cursor", ""))
            if idx < len(timeline_points) - 1
            else None
        )
        cursors.append(
            {
                "schema": "ProjectionPlaybackCursor.v1",
                "cursor": cursor_value,
                "ordinal": idx,
                "timeline_point_id": point.get("timeline_point_id"),
                "snapshot_id": point.get("snapshot_id"),
                "prev_cursor": prev_cursor,
                "next_cursor": next_cursor,
                **_AUTHORITY_BOUNDARY,
            }
        )
    bounds = {
        "first": str(cursors[0]["cursor"]) if cursors else None,
        "last": str(cursors[-1]["cursor"]) if cursors else None,
    }
    return cursors, bounds


def _extract_window_by_cursor(
    timeline_points: list[dict[str, Any]],
    *,
    window_size: int,
    start_cursor: str | None,
    end_cursor: str | None,
) -> list[dict[str, Any]]:
    if not timeline_points:
        return []
    index_by_cursor = {
        str(point.get("cursor", "")): idx for idx, point in enumerate(timeline_points)
    }
    start_index = index_by_cursor.get(start_cursor, 0)
    end_index = index_by_cursor.get(end_cursor, len(timeline_points) - 1)
    if end_index < start_index:
        return []
    clamped = timeline_points[start_index : end_index + 1]
    if not clamped:
        return []
    return clamped[: max(window_size, 1)]


def _build_timeline_windows(
    timeline_points: list[dict[str, Any]],
    *,
    window_size: int,
    start_cursor: str | None,
    end_cursor: str | None,
    corrupt_snapshot_ids: set[str],
) -> tuple[list[dict[str, Any]], dict[str, str], int]:
    selected = _extract_window_by_cursor(
        timeline_points,
        window_size=window_size,
        start_cursor=start_cursor,
        end_cursor=end_cursor,
    )
    if not selected:
        selected = timeline_points

    windows: list[dict[str, Any]] = []
    for start in range(len(selected)):
        subset = selected[start : start + max(window_size, 1)]
        if not subset:
            continue
        point_ids = [str(point.get("timeline_point_id", "")) for point in subset]
        snapshot_ids = [str(point.get("snapshot_id", "")) for point in subset]
        topics = sorted({str(point.get("topic", "")) for point in subset})
        has_missing_link = any(
            point.get("link_status") != "LINKED" for point in subset
        )
        has_corrupt_lineage = any(sid in corrupt_snapshot_ids for sid in snapshot_ids)
        blocked = has_missing_link or has_corrupt_lineage
        blocked_reasons: list[str] = []
        if has_missing_link:
            blocked_reasons.append("missing_snapshot_to_message_link")
        if has_corrupt_lineage:
            blocked_reasons.append("corrupt_lineage_detected")
        windows.append(
            {
                "schema": "ProjectionTimelineWindow.v1",
                "window_id": canonical_hash(
                    {
                        "point_ids": point_ids,
                        "snapshot_ids": snapshot_ids,
                        "topics": topics,
                    }
                ),
                "start_cursor": subset[0].get("cursor"),
                "end_cursor": subset[-1].get("cursor"),
                "timeline_point_ids": point_ids,
                "snapshot_ids": snapshot_ids,
                "topics": topics,
                "window_status": BLOCKED if blocked else "PRESENT",
                "blocked_reasons": blocked_reasons,
                **_AUTHORITY_BOUNDARY,
            }
        )
    ordered = sorted(windows, key=lambda item: str(item["window_id"]))
    window_index = {
        str(window["start_cursor"]): str(window["window_id"]) for window in ordered
    }
    blocked_window_count = sum(1 for window in ordered if window["window_status"] == BLOCKED)
    return ordered, window_index, blocked_window_count


def _build_lineage_evolution(
    timeline_points: list[dict[str, Any]],
    temporal_snapshot_index: dict[str, Any],
) -> tuple[dict[str, Any], set[str], list[str]]:
    snapshot_ids = {str(point.get("snapshot_id", "")) for point in timeline_points}
    blockers: list[str] = []
    corrupt_ids: set[str] = set()

    precomputed_gaps = temporal_snapshot_index.get("lineage_gaps", [])
    lineage_gap_count = int(temporal_snapshot_index.get("lineage_gap_count", 0))
    if isinstance(precomputed_gaps, list):
        for gap in precomputed_gaps:
            if not isinstance(gap, dict):
                continue
            sid = str(gap.get("snapshot_id", ""))
            if sid:
                corrupt_ids.add(sid)

    for point in timeline_points:
        snapshot_id = str(point.get("snapshot_id", ""))
        lineage_prev = point.get("lineage_prev")
        lineage_next = point.get("lineage_next")
        if isinstance(lineage_prev, str) and lineage_prev and lineage_prev not in snapshot_ids:
            corrupt_ids.add(snapshot_id)
            blockers.append(f"corrupt_lineage:lineage_prev_missing:{snapshot_id}->{lineage_prev}")
        if isinstance(lineage_next, str) and lineage_next and lineage_next not in snapshot_ids:
            corrupt_ids.add(snapshot_id)
            blockers.append(f"corrupt_lineage:lineage_next_missing:{snapshot_id}->{lineage_next}")

    roots = sorted(
        [
            str(point.get("snapshot_id", ""))
            for point in timeline_points
            if point.get("lineage_prev") in (None, "", NOT_COMPUTABLE)
        ]
    )
    chains: list[dict[str, Any]] = []
    by_snapshot = {
        str(point.get("snapshot_id", "")): point for point in timeline_points if point.get("snapshot_id")
    }
    for root in roots:
        chain_ids: list[str] = []
        seen: set[str] = set()
        cursor = root
        while cursor and cursor not in seen and cursor in by_snapshot:
            seen.add(cursor)
            chain_ids.append(cursor)
            nxt = by_snapshot[cursor].get("lineage_next")
            cursor = str(nxt) if isinstance(nxt, str) and nxt else ""
        chains.append(
            {
                "chain_root": root,
                "snapshot_ids": chain_ids,
                "chain_hash": canonical_hash({"chain_root": root, "snapshot_ids": chain_ids}),
            }
        )

    lineage = {
        "schema": "ProjectionLineageEvolution.v1",
        "lineage_gap_count": max(lineage_gap_count, len(corrupt_ids)),
        "corrupt_lineage_count": len(corrupt_ids),
        "lineage_chain_count": len(chains),
        "lineage_chains": sorted(chains, key=lambda item: str(item["chain_hash"])),
        "lineage_status": BLOCKED if corrupt_ids else "PRESENT",
        **_AUTHORITY_BOUNDARY,
    }
    return lineage, corrupt_ids, sorted(set(blockers))


def _extract_drift_signals(source_payloads: list[dict[str, Any]]) -> tuple[list[str], list[float]]:
    detections: list[str] = []
    rates: list[float] = []

    for payload in source_payloads:
        optimization_drift = payload.get("optimization_drift_summary", {})
        if isinstance(optimization_drift, dict):
            maybe_detections = optimization_drift.get("detections", [])
            if isinstance(maybe_detections, list):
                detections.extend(str(item) for item in maybe_detections)
            perf = optimization_drift.get("performance_delta", {})
            if isinstance(perf, dict):
                delta_pct = perf.get("delta_pct")
                if isinstance(delta_pct, int | float):
                    rates.append(float(delta_pct))

        benchmark_trends = payload.get("benchmark_trends", {})
        if isinstance(benchmark_trends, dict):
            maybe_detections = benchmark_trends.get("drift_detections", [])
            if isinstance(maybe_detections, list):
                detections.extend(str(item) for item in maybe_detections)

    return sorted(set(detections)), sorted(rates)


def _extract_equivalence_signals(source_payloads: list[dict[str, Any]]) -> tuple[int, int, int]:
    equivalent_true = 0
    equivalent_false = 0
    not_computable = 0

    for payload in source_payloads:
        replay_topology = payload.get("replay_topology", {})
        if not isinstance(replay_topology, dict):
            continue
        equivalence_status = replay_topology.get("replay_equivalence_status", {})
        if not isinstance(equivalence_status, dict):
            not_computable += 1
            continue
        value = equivalence_status.get("equivalence_verified")
        if value is True:
            equivalent_true += 1
        elif value is False:
            equivalent_false += 1
        else:
            not_computable += 1
    return equivalent_true, equivalent_false, not_computable


def _build_drift_timeline(
    *,
    temporal_snapshot_index: dict[str, Any],
    source_payloads: list[dict[str, Any]],
    blocked_window_count: int,
    corrupt_lineage_count: int,
) -> dict[str, Any]:
    detections, rates = _extract_drift_signals(source_payloads)
    not_computable_sources = sum(
        1
        for entry in temporal_snapshot_index.get("source_entries", [])
        if isinstance(entry, dict) and entry.get("status") == NOT_COMPUTABLE
    )
    eq_true, eq_false, eq_not_computable = _extract_equivalence_signals(source_payloads)
    if eq_false > 0:
        equivalence_trend = "DIVERGENT"
    elif eq_true > 0 and eq_false == 0:
        equivalence_trend = "EQUIVALENT"
    else:
        equivalence_trend = NOT_COMPUTABLE

    status = "PRESENT" if source_payloads else NOT_COMPUTABLE
    return {
        "schema": "ProjectionDriftTimeline.v1",
        "drift_timeline_status": status,
        "drift_event_count": len(detections),
        "drift_events": detections,
        "drift_rate": (sum(rates) / len(rates)) if rates else NOT_COMPUTABLE,
        "lineage_gap_count": int(temporal_snapshot_index.get("lineage_gap_count", 0)),
        "corrupt_lineage_count": corrupt_lineage_count,
        "blocked_window_count": blocked_window_count,
        "not_computable_source_count": not_computable_sources,
        "projection_equivalence_trend": equivalence_trend,
        "projection_equivalence_counts": {
            "equivalent_true": eq_true,
            "equivalent_false": eq_false,
            "not_computable": eq_not_computable,
        },
        **_AUTHORITY_BOUNDARY,
    }


def build_projection_chronoscope_packet(
    temporal_snapshot_index: dict[str, Any],
    projection_bus_envelope: dict[str, Any],
    *,
    packet_id: str = "projection_chronoscope_001",
    topic_filter: list[str] | None = None,
    window_size: int = 2,
    start_cursor: str | None = None,
    end_cursor: str | None = None,
    supplemental_source_payloads: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    timeline_points, link_blockers = _build_timeline_points(
        temporal_snapshot_index, projection_bus_envelope, topic_filter=topic_filter
    )
    playback_cursors, playback_cursor_bounds = _build_playback_cursors(timeline_points)
    lineage_evolution, corrupt_snapshot_ids, lineage_blockers = _build_lineage_evolution(
        timeline_points, temporal_snapshot_index
    )
    timeline_windows, window_index, blocked_window_count = _build_timeline_windows(
        timeline_points,
        window_size=window_size,
        start_cursor=start_cursor,
        end_cursor=end_cursor,
        corrupt_snapshot_ids=corrupt_snapshot_ids,
    )
    drift_timeline = _build_drift_timeline(
        temporal_snapshot_index=temporal_snapshot_index,
        source_payloads=supplemental_source_payloads or [],
        blocked_window_count=blocked_window_count,
        corrupt_lineage_count=int(lineage_evolution.get("corrupt_lineage_count", 0)),
    )

    topic_index: dict[str, list[str]] = {}
    for point in timeline_points:
        topic = str(point.get("topic", ""))
        topic_index.setdefault(topic, []).append(str(point.get("timeline_point_id", "")))
    topic_index = {
        key: sorted(values)
        for key, values in sorted(topic_index.items(), key=lambda item: item[0])
    }

    source_artifacts = {
        "temporal_snapshot_spine_ref": temporal_snapshot_index.get("index_hash"),
        "projection_bus_ref": projection_bus_envelope.get("ledger", {}).get("ledger_hash"),
    }
    advisory_flags = sorted(
        {
            "projection_only",
            "advisory_only",
            "deterministic_timeline",
            "timeline_inspection_only",
        }
    )
    authority_boundary_summary = {
        **_AUTHORITY_BOUNDARY,
        "boundary_note": "Chronoscope output is projection-only and non-authoritative.",
    }

    blockers: list[str] = []
    blockers.extend(str(item) for item in temporal_snapshot_index.get("remaining_blockers", []))
    blockers.extend(str(item) for item in projection_bus_envelope.get("remaining_blockers", []))
    blockers.extend(link_blockers)
    blockers.extend(lineage_blockers)

    if not timeline_points:
        final_status = NOT_COMPUTABLE
        blockers.append("missing_timeline_points")
    elif lineage_evolution.get("lineage_status") == BLOCKED or link_blockers:
        final_status = BLOCKED
    elif blockers:
        final_status = "ADVISORY_ONLY"
    else:
        final_status = "PASS"

    packet_hash = canonical_hash(
        {
            "packet_id": packet_id,
            "patch_id": PATCH_ID,
            "timeline_point_ids": [point["timeline_point_id"] for point in timeline_points],
            "window_ids": [window["window_id"] for window in timeline_windows],
            "cursor_bounds": playback_cursor_bounds,
            "lineage_evolution": lineage_evolution,
            "drift_timeline": drift_timeline,
            "topic_index": topic_index,
            "window_index": window_index,
        }
    )

    return {
        "schema": "ProjectionChronoscopePacket.v1",
        "patch_id": PATCH_ID,
        "packet_id": packet_id,
        "packet_hash": packet_hash,
        "source_artifacts": source_artifacts,
        "timeline_points": timeline_points,
        "timeline_windows": timeline_windows,
        "playback_cursors": playback_cursors,
        "lineage_evolution": lineage_evolution,
        "drift_timeline": drift_timeline,
        "topic_index": topic_index,
        "window_index": window_index,
        "playback_cursor_bounds": playback_cursor_bounds,
        "authority_boundary_summary": authority_boundary_summary,
        "visualization_hints": sorted(
            [
                "HINT:timeline_projection_only",
                "HINT:advisory_only_non_authoritative",
                "HINT:no_live_push_transport",
            ]
        ),
        "chronoscope_advisory_flags": advisory_flags,
        "final_status": final_status,
        "remaining_blockers": sorted(set(blockers)),
        **_AUTHORITY_BOUNDARY,
    }


def build_projection_chronoscope_packet_from_artifacts(
    *,
    packet_id: str = "projection_chronoscope_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
    topic_filter: list[str] | None = None,
    window_size: int = 2,
    start_cursor: str | None = None,
    end_cursor: str | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
        "temporal_snapshot_spine": paths.temporal_snapshot_spine_latest,
        "projection_bus": paths.projection_bus_latest,
        "aal_viz_runtime_projection": paths.aal_viz_runtime_projection_latest,
        "live_projection_refresh": paths.live_projection_refresh_latest,
    }
    merged = {**defaults, **(source_artifact_paths or {})}

    snapshot_index = _load_artifact(merged.get("temporal_snapshot_spine"))
    projection_bus = _load_artifact(merged.get("projection_bus"))
    supplemental = [
        payload
        for payload in [
            _load_artifact(merged.get("aal_viz_runtime_projection")),
            _load_artifact(merged.get("live_projection_refresh")),
        ]
        if isinstance(payload, dict)
    ]
    if snapshot_index is None or projection_bus is None:
        blockers = []
        if snapshot_index is None:
            blockers.append(f"missing_artifact:{merged['temporal_snapshot_spine']}")
        if projection_bus is None:
            blockers.append(f"missing_artifact:{merged['projection_bus']}")
        return {
            "schema": "ProjectionChronoscopePacket.v1",
            "patch_id": PATCH_ID,
            "packet_id": packet_id,
            "packet_hash": canonical_hash({"packet_id": packet_id, "blockers": sorted(blockers)}),
            "source_artifacts": {k: str(v) for k, v in merged.items()},
            "timeline_points": [],
            "timeline_windows": [],
            "playback_cursors": [],
            "playback_cursor_bounds": {"first": None, "last": None},
            "lineage_evolution": {
                "schema": "ProjectionLineageEvolution.v1",
                "lineage_status": NOT_COMPUTABLE,
                "lineage_gap_count": 0,
                "corrupt_lineage_count": 0,
                "lineage_chain_count": 0,
                "lineage_chains": [],
                **_AUTHORITY_BOUNDARY,
            },
            "drift_timeline": {
                "schema": "ProjectionDriftTimeline.v1",
                "drift_timeline_status": NOT_COMPUTABLE,
                "drift_event_count": 0,
                "drift_events": [],
                "drift_rate": NOT_COMPUTABLE,
                "lineage_gap_count": 0,
                "corrupt_lineage_count": 0,
                "blocked_window_count": 0,
                "not_computable_source_count": len(blockers),
                "projection_equivalence_trend": NOT_COMPUTABLE,
                "projection_equivalence_counts": {
                    "equivalent_true": 0,
                    "equivalent_false": 0,
                    "not_computable": 0,
                },
                **_AUTHORITY_BOUNDARY,
            },
            "topic_index": {},
            "window_index": {},
            "authority_boundary_summary": {
                **_AUTHORITY_BOUNDARY,
                "boundary_note": "Chronoscope output is projection-only and non-authoritative.",
            },
            "visualization_hints": sorted(
                [
                    "HINT:timeline_projection_only",
                    "HINT:advisory_only_non_authoritative",
                    "HINT:no_live_push_transport",
                ]
            ),
            "chronoscope_advisory_flags": sorted(
                [
                    "projection_only",
                    "advisory_only",
                    "deterministic_timeline",
                    "timeline_inspection_only",
                ]
            ),
            "final_status": NOT_COMPUTABLE,
            "remaining_blockers": sorted(blockers),
            **_AUTHORITY_BOUNDARY,
        }

    packet = build_projection_chronoscope_packet(
        snapshot_index,
        projection_bus,
        packet_id=packet_id,
        topic_filter=topic_filter,
        window_size=window_size,
        start_cursor=start_cursor,
        end_cursor=end_cursor,
        supplemental_source_payloads=supplemental,
    )
    packet["source_artifacts"] = {k: str(v) for k, v in merged.items()}
    return packet


def write_projection_chronoscope_packet(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_projection_chronoscope_markdown(packet: dict[str, Any]) -> str:
    lines = [
        f"# Projection Chronoscope — {packet.get('packet_id', '')}",
        "",
        f"**Patch:** `{packet.get('patch_id', '')}`",
        f"**Final Status:** `{packet.get('final_status', '')}`",
        f"**Timeline Point Count:** `{len(packet.get('timeline_points', []))}`",
        f"**Window Count:** `{len(packet.get('timeline_windows', []))}`",
        "",
        "## Playback Cursor Bounds",
        f"- First: `{packet.get('playback_cursor_bounds', {}).get('first')}`",
        f"- Last: `{packet.get('playback_cursor_bounds', {}).get('last')}`",
        "",
        "## Lineage Posture",
    ]
    lineage = packet.get("lineage_evolution", {})
    lines.append(f"- Status: `{lineage.get('lineage_status', NOT_COMPUTABLE)}`")
    lines.append(f"- Gap count: `{lineage.get('lineage_gap_count', 0)}`")
    lines.append(f"- Corrupt count: `{lineage.get('corrupt_lineage_count', 0)}`")
    lines.append("")
    lines.append("## Drift Posture")
    drift = packet.get("drift_timeline", {})
    lines.append(f"- Status: `{drift.get('drift_timeline_status', NOT_COMPUTABLE)}`")
    lines.append(f"- Drift events: `{drift.get('drift_event_count', 0)}`")
    lines.append(f"- Blocked windows: `{drift.get('blocked_window_count', 0)}`")
    lines.append(f"- NOT_COMPUTABLE sources: `{drift.get('not_computable_source_count', 0)}`")
    lines.append("")
    lines.append("## Missing/Corrupt Source Blockers")
    blockers = packet.get("remaining_blockers", [])
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Operator Next Actions")
    if blockers:
        lines.append("- Inspect missing/corrupt projection artifacts and re-run chronoscope.")
        lines.append("- Resolve lineage gaps before using timeline windows for inspection.")
    else:
        lines.append("- Continue advisory-only timeline inspection for deterministic replay review.")
    lines.append("")
    return "\n".join(lines)
