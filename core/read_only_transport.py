"""Deterministic read-only live transport scaffold for projection/operator surfaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths
from core.temporal_persistence_memory import summarize_temporal_persistence_memory
from core.temporal_resonance_coherence import summarize_temporal_resonance_coherence
from core.temporal_stability_pressure import summarize_temporal_stability_pressure
from core.temporal_topology_cartography import summarize_temporal_topology_cartography

from core.status_result import (
    STATUS_BLOCKED as BLOCKED,
    STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE,
)

PATCH_ID = "PATCH-P19-READ-ONLY-LIVE-TRANSPORT-SCAFFOLD-001"

_INVARIANTS: dict[str, Any] = {
    "read_only": True,
    "advisory_only": True,
    "transport_only": True,
    "command_channel": False,
    "bidirectional_control": False,
    "execution_authority": False,
    "authority_granted": False,
    "mutation_allowed": False,
    "promotion_allowed": False,
    "auto_execute": False,
    "auto_approve": False,
    "inference_authority": False,
}

_FORBIDDEN_TRUE_FLAGS = {
    "command_channel",
    "bidirectional_control",
    "execution_authority",
    "authority_granted",
    "mutation_allowed",
    "promotion_allowed",
    "auto_execute",
    "auto_approve",
    "inference_authority",
}


def _load_artifact(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
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


def _safe_hash(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    try:
        return str(canonical_hash(payload))
    except Exception:
        return None


def _packet_id(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return NOT_COMPUTABLE
    for key in ("packet_id", "queue_id", "projection_id", "artifact_id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return NOT_COMPUTABLE


def _topic_registry(source_artifact_paths: dict[str, str | Path]) -> list[dict[str, Any]]:
    specs = [
        ("projection.runtime", "projection.runtime", source_artifact_paths["projection_runtime"], "runtime_projection_packet_ref"),
        ("projection.refresh", "projection.refresh", source_artifact_paths["projection_refresh"], "live_projection_refresh_ref"),
        ("projection.bus", "projection.bus", source_artifact_paths["projection_bus"], "projection_bus_envelope_ref"),
        ("projection.chronoscope", "projection.chronoscope", source_artifact_paths["projection_chronoscope"], "projection_chronoscope_packet_ref"),
        ("projection.render", "projection.render", source_artifact_paths["projection_render"], "aal_viz_graph_render_packet_ref"),
        ("operator.review_queue", "operator.review_queue", source_artifact_paths["operator_review_queue"], "operator_review_queue_ref"),
        ("governance.blockers", "governance.blockers", source_artifact_paths["projection_runtime"], "runtime_governance_blockers_ref"),
        ("drift.timeline", "drift.timeline", source_artifact_paths["projection_chronoscope"], "chronoscope_drift_timeline_ref"),
        ("replay.equivalence", "replay.equivalence", source_artifact_paths["projection_runtime"], "runtime_replay_equivalence_ref"),
        ("lineage.gaps", "lineage.gaps", source_artifact_paths["projection_chronoscope"], "chronoscope_lineage_gaps_ref"),
        (
            "pressure.tensor",
            "pressure.tensor",
            source_artifact_paths["temporal_stability_pressure"],
            "temporal_stability_pressure_ref",
        ),
    ]
    topics: list[dict[str, Any]] = []
    for topic_key, topic_name, source_path, payload_kind in specs:
        topic_id = canonical_hash(
            {
                "topic_key": topic_key,
                "topic_name": topic_name,
                "source_artifact_path": str(source_path),
                "payload_kind": payload_kind,
            }
        )
        topics.append(
            {
                "schema": "ReadOnlyTransportTopic.v1",
                "topic_id": topic_id,
                "topic_name": topic_name,
                "source_artifact_path": str(source_path),
                "payload_kind": payload_kind,
                "allowed_direction": "outbound_only",
                "command_allowed": False,
                **_INVARIANTS,
            }
        )
    return sorted(topics, key=lambda item: (str(item["topic_name"]), str(item["topic_id"])))


def _payload_ref_for_topic(topic_name: str, source_path: str) -> str:
    suffix = {
        "governance.blockers": "#/remaining_blockers",
        "drift.timeline": "#/drift_timeline",
        "replay.equivalence": "#/replay_topology/replay_equivalence_status",
        "lineage.gaps": "#/lineage_evolution",
    }.get(topic_name, "")
    return f"{source_path}{suffix}"


def _cursor_for_topic(topic_name: str, payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    if topic_name == "projection.runtime":
        value = payload.get("projection_timestamp")
        return str(value) if isinstance(value, str) and value else None
    if topic_name == "projection.refresh":
        value = payload.get("cursor")
        return str(value) if isinstance(value, str) and value else None
    if topic_name == "projection.bus":
        bounds = payload.get("ledger", {}).get("cursor_bounds")
        if isinstance(bounds, dict):
            last = bounds.get("last")
            return str(last) if isinstance(last, str) and last else None
        return None
    if topic_name == "projection.chronoscope":
        bounds = payload.get("playback_cursor_bounds")
        if isinstance(bounds, dict):
            last = bounds.get("last")
            return str(last) if isinstance(last, str) and last else None
        return None
    return None


def _advisory_flags_for_topic(
    topic_name: str,
    payload: dict[str, Any] | None,
    authority_violations: list[str],
    status: str,
) -> list[str]:
    flags = {
        "read_only_transport",
        "advisory_only",
        "transport_only",
        "deterministic_ordering",
    }
    if isinstance(payload, dict):
        for key in ("advisory_flags", "chronoscope_advisory_flags", "render_advisory_flags", "queue_advisory_flags"):
            value = payload.get(key)
            if isinstance(value, list):
                flags.update(str(item) for item in value if str(item))
    if status == NOT_COMPUTABLE:
        flags.add("not_computable")
    if status == BLOCKED:
        flags.add("blocked")
    if authority_violations:
        flags.add("authority_boundary_violation")
    if topic_name == "projection.refresh":
        flags.add("live_projection_refresh_surface")
    return sorted(flags)


def _blockers_for_topic(
    topic_name: str,
    payload: dict[str, Any] | None,
    source_path: str,
    source_hash: str | None,
    authority_violations: list[str],
) -> list[str]:
    blockers: list[str] = []
    if payload is None:
        blockers.append(f"missing_artifact:{source_path}")
    if source_hash is None:
        blockers.append(f"missing_source_hash:{source_path}")
    if isinstance(payload, dict):
        blockers.extend(str(item) for item in payload.get("remaining_blockers", []))
    if authority_violations:
        blockers.extend(f"authority_boundary_violation:{path}" for path in authority_violations)
    if topic_name == "projection.refresh" and payload is None:
        blockers.append("live_projection_refresh_not_available")
    return sorted(set(item for item in blockers if item))


def _status_for_frame(payload: dict[str, Any] | None, blockers: list[str]) -> str:
    if payload is None:
        return NOT_COMPUTABLE
    if blockers:
        return BLOCKED
    return "PRESENT"


def build_read_only_transport_packet(
    *,
    packet_id: str = "read_only_transport_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
        "projection_runtime": paths.aal_viz_runtime_projection_latest,
        "projection_refresh": paths.live_projection_refresh_latest,
        "projection_bus": paths.projection_bus_latest,
        "projection_chronoscope": paths.projection_chronoscope_latest,
        "projection_render": paths.aal_viz_graph_render_packet_latest,
        "operator_review_queue": paths.operator_action_queue_latest,
        "temporal_state_diff": paths.temporal_state_diff_latest,
        "multi_run_convergence": paths.multi_run_convergence_latest,
        "temporal_topology_cartography": paths.temporal_topology_cartography_latest,
        "temporal_stability_pressure": paths.temporal_stability_pressure_latest,
        "temporal_persistence_memory": paths.temporal_persistence_memory_latest,
        "temporal_resonance_coherence": paths.temporal_resonance_coherence_latest,
    }
    merged_paths = {**defaults, **(source_artifact_paths or {})}
    topics = _topic_registry(merged_paths)

    frames: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for topic in topics:
        topic_id = str(topic["topic_id"])
        topic_name = str(topic["topic_name"])
        source_path = str(topic["source_artifact_path"])
        payload = _load_artifact(source_path)
        source_hash = _safe_hash(payload)
        authority_violations = _scan_forbidden_true_flags(payload) if payload is not None else []
        blockers = _blockers_for_topic(
            topic_name=topic_name,
            payload=payload,
            source_path=source_path,
            source_hash=source_hash,
            authority_violations=authority_violations,
        )
        status = _status_for_frame(payload, blockers)
        packet_ref = _packet_id(payload)
        cursor = _cursor_for_topic(topic_name, payload)
        advisory_flags = _advisory_flags_for_topic(
            topic_name=topic_name,
            payload=payload,
            authority_violations=authority_violations,
            status=status,
        )
        sequence_number = 1
        frame_id = canonical_hash(
            {
                "topic_id": topic_id,
                "sequence_number": sequence_number,
                "source_hash": source_hash,
                "packet_id": packet_ref,
                "payload_ref": _payload_ref_for_topic(topic_name, source_path),
                "cursor": cursor,
            }
        )
        frame_hash = canonical_hash(
            {
                "frame_id": frame_id,
                "status": status,
                "blockers": blockers,
                "advisory_flags": advisory_flags,
            }
        )
        frame = {
            "schema": "ReadOnlyTransportFrame.v1",
            "frame_id": frame_id,
            "topic_id": topic_id,
            "topic_name": topic_name,
            "source_artifact": source_path,
            "source_hash": source_hash,
            "packet_id": packet_ref,
            "payload_ref": _payload_ref_for_topic(topic_name, source_path),
            "cursor": cursor,
            "sequence_number": sequence_number,
            "advisory_flags": advisory_flags,
            "blocker_status": status,
            "remaining_blockers": blockers,
            "frame_hash": frame_hash,
            **_INVARIANTS,
        }
        frames.append(frame)
        events.append(
            {
                "schema": "ReadOnlyTransportEvent.v1",
                "event_id": canonical_hash(
                    {"frame_id": frame_id, "topic_id": topic_id, "sequence_number": sequence_number}
                ),
                "frame_id": frame_id,
                "topic_id": topic_id,
                "event_kind": "transport_frame_observation",
                "status": status,
                "advisory_flags": advisory_flags,
                **_INVARIANTS,
            }
        )

    frames = sorted(
        frames,
        key=lambda item: (
            str(item["topic_id"]),
            int(item["sequence_number"]),
            str(item.get("source_hash") or item["frame_hash"]),
        ),
    )
    events = sorted(events, key=lambda item: (str(item["topic_id"]), str(item["event_id"])))

    temporal_state_diff_payload = _load_artifact(merged_paths.get("temporal_state_diff"))
    multi_run_convergence_payload = _load_artifact(
        merged_paths.get("multi_run_convergence")
    )
    cross_run_topology_fusion_payload = _load_artifact(
        paths.cross_run_topology_fusion_latest
    )
    temporal_topology_cartography_payload = _load_artifact(
        merged_paths.get("temporal_topology_cartography")
    )
    temporal_stability_pressure_payload = _load_artifact(
        merged_paths.get("temporal_stability_pressure")
    )
    cartography_summary = summarize_temporal_topology_cartography(
        temporal_topology_cartography_payload
    )
    pressure_summary = summarize_temporal_stability_pressure(
        temporal_stability_pressure_payload
    )
    temporal_persistence_memory_payload = _load_artifact(
        merged_paths.get("temporal_persistence_memory")
    )
    memory_summary = summarize_temporal_persistence_memory(
        temporal_persistence_memory_payload
    )
    temporal_resonance_coherence_payload = _load_artifact(
        merged_paths.get("temporal_resonance_coherence")
    )
    resonance_summary = summarize_temporal_resonance_coherence(
        temporal_resonance_coherence_payload
    )

    topic_index: dict[str, list[str]] = {}
    artifact_index: dict[str, list[str]] = {}
    for frame in frames:
        topic_index.setdefault(str(frame["topic_id"]), []).append(str(frame["frame_id"]))
        artifact_index.setdefault(str(frame["source_artifact"]), []).append(str(frame["frame_id"]))
    topic_index = {key: sorted(value) for key, value in sorted(topic_index.items())}
    artifact_index = {key: sorted(value) for key, value in sorted(artifact_index.items())}

    ordered_topics = [str(topic["topic_id"]) for topic in topics]
    ordered_frames = [str(frame["frame_id"]) for frame in frames]
    cursors: list[str] = []
    for frame in frames:
        frame_cursor = frame.get("cursor")
        if isinstance(frame_cursor, str) and frame_cursor:
            cursors.append(frame_cursor)
    cursor_bounds = {
        "schema": "ReadOnlyTransportCursor.v1",
        "first": cursors[0] if cursors else None,
        "last": cursors[-1] if cursors else None,
        **_INVARIANTS,
    }

    blocked_frames = [frame for frame in frames if str(frame.get("blocker_status")) == BLOCKED]
    not_computable_frames = [frame for frame in frames if str(frame.get("blocker_status")) == NOT_COMPUTABLE]
    remaining_blockers = sorted(
        {
            blocker
            for frame in frames
            for blocker in frame.get("remaining_blockers", [])
            if blocker
        }
    )

    blocker_summary = {
        "blocked_frame_count": len(blocked_frames),
        "blocked_topic_count": len({str(frame["topic_id"]) for frame in blocked_frames}),
        "authority_boundary_violation_count": sum(
            1
            for blocker in remaining_blockers
            if str(blocker).startswith("authority_boundary_violation:")
        ),
    }
    not_computable_summary = {
        "not_computable_frame_count": len(not_computable_frames),
        "not_computable_topic_count": len({str(frame["topic_id"]) for frame in not_computable_frames}),
    }

    if len(not_computable_frames) == len(frames):
        final_status = NOT_COMPUTABLE
    elif blocked_frames:
        final_status = BLOCKED
    elif not_computable_frames:
        final_status = "ADVISORY_ONLY"
    else:
        final_status = "PASS"

    ledger_hash = canonical_hash(
        {
            "packet_id": packet_id,
            "ordered_topics": ordered_topics,
            "ordered_frames": ordered_frames,
            "topic_index": topic_index,
            "artifact_index": artifact_index,
            "cursor_bounds": cursor_bounds,
            "final_status": final_status,
            "remaining_blockers": remaining_blockers,
        }
    )
    ledger = {
        "schema": "ReadOnlyTransportLedger.v1",
        "ordered_topics": ordered_topics,
        "ordered_frames": ordered_frames,
        "cursor_bounds": cursor_bounds,
        "topic_index": topic_index,
        "artifact_index": artifact_index,
        "blocker_summary": blocker_summary,
        "not_computable_summary": not_computable_summary,
        "final_status": final_status,
        "remaining_blockers": remaining_blockers,
        "ledger_hash": ledger_hash,
        **_INVARIANTS,
    }

    return {
        "schema": "ReadOnlyTransportFeedPacket.v1",
        "patch_id": PATCH_ID,
        "packet_id": packet_id,
        "topics": topics,
        "events": events,
        "frames": frames,
        "ledger": ledger,
        "read_only_transport_status": final_status,
        "transport_topic_count": len(topics),
        "transport_frame_count": len(frames),
        "transport_cursor_bounds": {
            "first": cursor_bounds["first"],
            "last": cursor_bounds["last"],
        },
        "transport_blocker_count": len(remaining_blockers),
        "transport_advisory_flags": sorted(
            {
                "read_only_transport",
                "advisory_only",
                "transport_only",
                "deterministic_ordering",
                "fail_closed",
            }
        ),
        "temporal_state_diff_status": str(
            temporal_state_diff_payload.get("temporal_state_diff_status", NOT_COMPUTABLE)
            if isinstance(temporal_state_diff_payload, dict)
            else NOT_COMPUTABLE
        ),
        "total_change_count": int(
            temporal_state_diff_payload.get("total_change_count", 0)
            if isinstance(temporal_state_diff_payload, dict)
            else 0
        ),
        "topology_change_count": int(
            temporal_state_diff_payload.get("topology_change_count", 0)
            if isinstance(temporal_state_diff_payload, dict)
            else 0
        ),
        "lineage_shift_count": int(
            temporal_state_diff_payload.get("lineage_shift_count", 0)
            if isinstance(temporal_state_diff_payload, dict)
            else 0
        ),
        "drift_acceleration_status": str(
            temporal_state_diff_payload.get("drift_acceleration_status", NOT_COMPUTABLE)
            if isinstance(temporal_state_diff_payload, dict)
            else NOT_COMPUTABLE
        ),
        "replay_equivalence_change_status": str(
            temporal_state_diff_payload.get("replay_equivalence_change_status", NOT_COMPUTABLE)
            if isinstance(temporal_state_diff_payload, dict)
            else NOT_COMPUTABLE
        ),
        "queue_delta_count": int(
            temporal_state_diff_payload.get("queue_delta_count", 0)
            if isinstance(temporal_state_diff_payload, dict)
            else 0
        ),
        "transport_delta_count": int(
            temporal_state_diff_payload.get("transport_delta_count", 0)
            if isinstance(temporal_state_diff_payload, dict)
            else 0
        ),
        "diff_advisory_flags": [
            str(item)
            for item in (
                temporal_state_diff_payload.get("diff_advisory_flags", [])
                if isinstance(temporal_state_diff_payload, dict)
                else []
            )
        ],
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
        "cross_run_topology_fusion_status": str(
            cross_run_topology_fusion_payload.get(
                "cross_run_topology_fusion_status", NOT_COMPUTABLE
            )
            if isinstance(cross_run_topology_fusion_payload, dict)
            else NOT_COMPUTABLE
        ),
        "fusion_node_count": int(
            cross_run_topology_fusion_payload.get("fusion_node_count", 0)
            if isinstance(cross_run_topology_fusion_payload, dict)
            else 0
        ),
        "fusion_edge_count": int(
            cross_run_topology_fusion_payload.get("fusion_edge_count", 0)
            if isinstance(cross_run_topology_fusion_payload, dict)
            else 0
        ),
        "persistent_cluster_count": int(
            cross_run_topology_fusion_payload.get("persistent_cluster_count", 0)
            if isinstance(cross_run_topology_fusion_payload, dict)
            else 0
        ),
        "lineage_corridor_count": int(
            cross_run_topology_fusion_payload.get("lineage_corridor_count", 0)
            if isinstance(cross_run_topology_fusion_payload, dict)
            else 0
        ),
        "replay_continuity_status": str(
            cross_run_topology_fusion_payload.get(
                "replay_continuity_status", NOT_COMPUTABLE
            )
            if isinstance(cross_run_topology_fusion_payload, dict)
            else NOT_COMPUTABLE
        ),
        "transport_continuity_status": str(
            cross_run_topology_fusion_payload.get(
                "transport_continuity_status", NOT_COMPUTABLE
            )
            if isinstance(cross_run_topology_fusion_payload, dict)
            else NOT_COMPUTABLE
        ),
        "topology_stability_score": float(
            cross_run_topology_fusion_payload.get("topology_stability_score", 0.0)
            if isinstance(cross_run_topology_fusion_payload, dict)
            else 0.0
        ),
        "fusion_advisory_flags": [
            str(item)
            for item in (
                cross_run_topology_fusion_payload.get("fusion_advisory_flags", [])
                if isinstance(cross_run_topology_fusion_payload, dict)
                else []
            )
        ],
        "temporal_topology_cartography_status": cartography_summary[
            "temporal_topology_cartography_status"
        ],
        "atlas_region_count": cartography_summary["atlas_region_count"],
        "atlas_corridor_count": cartography_summary["atlas_corridor_count"],
        "stable_region_count": cartography_summary["stable_region_count"],
        "volatile_region_count": cartography_summary["volatile_region_count"],
        "drift_zone_count": cartography_summary["drift_zone_count"],
        "replay_corridor_count": cartography_summary["replay_corridor_count"],
        "continuity_corridor_count": cartography_summary["continuity_corridor_count"],
        "topology_density_score": cartography_summary["topology_density_score"],
        "cartography_advisory_flags": cartography_summary[
            "cartography_advisory_flags"
        ],
        "temporal_stability_pressure_status": pressure_summary[
            "temporal_stability_pressure_status"
        ],
        "aggregate_stress_score": pressure_summary["aggregate_stress_score"],
        "resilience_score": pressure_summary["resilience_score"],
        "dominant_pressure_component": pressure_summary[
            "dominant_pressure_component"
        ],
        "pressure_zone_count": pressure_summary["pressure_zone_count"],
        "critical_pressure_count": pressure_summary["critical_pressure_count"],
        "strain_zone_count": pressure_summary["strain_zone_count"],
        "collapse_pressure_zone_count": pressure_summary[
            "collapse_pressure_zone_count"
        ],
        "drift_load_zone_count": pressure_summary["drift_load_zone_count"],
        "transition_pressure_gradient": pressure_summary[
            "transition_pressure_gradient"
        ],
        "pressure_advisory_flags": pressure_summary["pressure_advisory_flags"],
        "temporal_persistence_memory_status": memory_summary[
            "temporal_persistence_memory_status"
        ],
        "aggregate_memory_score": memory_summary["aggregate_memory_score"],
        "decay_score": memory_summary["decay_score"],
        "hysteresis_score": memory_summary["hysteresis_score"],
        "dominant_memory_component": memory_summary["dominant_memory_component"],
        "persistence_half_life_bucket": memory_summary["persistence_half_life_bucket"],
        "memory_zone_count": memory_summary["memory_zone_count"],
        "persistent_memory_count": memory_summary["persistent_memory_count"],
        "rapid_decay_zone_count": memory_summary["rapid_decay_zone_count"],
        "hysteresis_zone_count": memory_summary["hysteresis_zone_count"],
        "replay_memory_zone_count": memory_summary["replay_memory_zone_count"],
        "topology_memory_zone_count": memory_summary["topology_memory_zone_count"],
        "drift_memory_zone_count": memory_summary["drift_memory_zone_count"],
        "memory_advisory_flags": memory_summary["memory_advisory_flags"],
        "temporal_resonance_coherence_status": resonance_summary[
            "temporal_resonance_coherence_status"
        ],
        "aggregate_coherence_score": resonance_summary["aggregate_coherence_score"],
        "resonance_score": resonance_summary["resonance_score"],
        "dissonance_score": resonance_summary["dissonance_score"],
        "dominant_coherence_component": resonance_summary[
            "dominant_coherence_component"
        ],
        "phase_alignment_bucket": resonance_summary["phase_alignment_bucket"],
        "coherence_zone_count": resonance_summary["coherence_zone_count"],
        "locked_coherence_count": resonance_summary["locked_coherence_count"],
        "resonance_zone_count": resonance_summary["resonance_zone_count"],
        "dissonance_zone_count": resonance_summary["dissonance_zone_count"],
        "replay_resonance_zone_count": resonance_summary["replay_resonance_zone_count"],
        "topology_alignment_zone_count": resonance_summary[
            "topology_alignment_zone_count"
        ],
        "phase_alignment_zone_count": resonance_summary["phase_alignment_zone_count"],
        "coherence_advisory_flags": resonance_summary["coherence_advisory_flags"],
        "final_status": final_status,
        "remaining_blockers": remaining_blockers,
        **_INVARIANTS,
    }


def write_read_only_transport_packet(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_read_only_transport_markdown(packet: dict[str, Any]) -> str:
    ledger = packet.get("ledger", {})
    blockers = [str(item) for item in packet.get("remaining_blockers", [])]
    lines = [
        f"# Read-Only Transport — {packet.get('packet_id', '')}",
        "",
        f"**Patch:** `{packet.get('patch_id', '')}`",
        f"**Final Status:** `{packet.get('final_status', '')}`",
        f"**Topic Count:** `{packet.get('transport_topic_count', 0)}`",
        f"**Frame Count:** `{packet.get('transport_frame_count', 0)}`",
        f"**Cursor Bounds:** `{packet.get('transport_cursor_bounds', {})}`",
        f"**Blocker Count:** `{packet.get('transport_blocker_count', 0)}`",
        (
            f"**Not Computable Frame Count:** "
            f"`{ledger.get('not_computable_summary', {}).get('not_computable_frame_count', 0)}`"
        ),
        f"**Temporal State Diff Status:** `{packet.get('temporal_state_diff_status', NOT_COMPUTABLE)}`",
        f"**Total Changes:** `{packet.get('total_change_count', 0)}`",
        f"**Topology Changes:** `{packet.get('topology_change_count', 0)}`",
        f"**Lineage Shifts:** `{packet.get('lineage_shift_count', 0)}`",
        (
            f"**Drift Acceleration:** "
            f"`{packet.get('drift_acceleration_status', NOT_COMPUTABLE)}`"
        ),
        (
            f"**Replay Equivalence Changes:** "
            f"`{packet.get('replay_equivalence_change_status', NOT_COMPUTABLE)}`"
        ),
        f"**Queue Deltas:** `{packet.get('queue_delta_count', 0)}`",
        f"**Transport Deltas:** `{packet.get('transport_delta_count', 0)}`",
        "",
        "## Read-Only Posture",
        "- read_only: `true`",
        "- advisory_only: `true`",
        "- transport_only: `true`",
        "- command_channel: `false`",
        "- bidirectional_control: `false`",
        "- execution_authority: `false`",
        "- mutation_allowed: `false`",
        "- auto_execute: `false`",
        "- auto_approve: `false`",
        "",
        "## Operator Next Actions",
    ]
    if blockers:
        lines.append("- Review blocker evidence and regenerate missing/corrupt source artifacts.")
        lines.append("- Continue read-only projection/operator inspection only.")
    else:
        lines.append("- Continue read-only advisory monitoring.")
    lines.append("")
    return "\n".join(lines)
