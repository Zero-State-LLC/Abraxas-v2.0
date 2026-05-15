"""Deterministic cross-run topology and lineage fusion analytics for P14-P21 surfaces."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P22-CROSS-RUN-TOPOLOGY-AND-LINEAGE-FUSION-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_INVARIANTS: dict[str, Any] = {
    "advisory_only": True,
    "analytics_only": True,
    "fusion_only": True,
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

_MOTIF_ORDER = {
    "PERSISTENT": 0,
    "RECURRING": 1,
    "TRANSIENT": 2,
    "VOLATILE": 3,
    "DEGRADED": 4,
    NOT_COMPUTABLE: 5,
    BLOCKED: 6,
}


def _apply_invariants(payload: dict[str, Any]) -> dict[str, Any]:
    return {**payload, **_INVARIANTS}


def _load_artifact(path: str | Path | None) -> tuple[dict[str, Any] | None, str]:
    if path is None:
        return None, "MISSING"
    target = Path(path)
    if not target.exists():
        return None, "MISSING"
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "CORRUPT"
    except OSError:
        return None, "UNREADABLE"
    if isinstance(payload, dict):
        return payload, "PRESENT"
    return None, "CORRUPT"


def _safe_hash(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    try:
        return str(canonical_hash(payload))
    except (TypeError, ValueError):
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


def _as_str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return default
    return default


def _as_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted(str(item) for item in value if str(item))


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round(max(0.0, min(1.0, numerator / denominator)), 6)


def _derive_scores(
    *,
    recurrence_count: int,
    evidence_count: int,
    continuity_count: int,
    run_count: int,
) -> tuple[float, float, float, float]:
    persistence_ratio = _ratio(float(recurrence_count), float(max(1, run_count)))
    continuity_ratio = _ratio(float(continuity_count), float(max(1, recurrence_count)))
    stability_score = round((persistence_ratio + continuity_ratio) / 2.0, 6)
    volatility_score = round(max(0.0, 1.0 - stability_score), 6)
    if evidence_count <= 0:
        return 0.0, 0.0, 0.0, 1.0
    return persistence_ratio, continuity_ratio, stability_score, volatility_score


def _classify_motif(
    *,
    recurrence_count: int,
    persistence_ratio: float,
    continuity_ratio: float,
    volatility_score: float,
    evidence_count: int,
    blocked: bool,
    degraded: bool,
) -> tuple[str, list[str]]:
    blockers: list[str] = []
    if blocked:
        blockers.append("authority_boundary_violation")
        return BLOCKED, blockers
    if evidence_count < 2:
        blockers.append("insufficient_fusion_evidence")
        return NOT_COMPUTABLE, blockers
    if degraded:
        return "DEGRADED", blockers
    if (
        recurrence_count >= 3
        and persistence_ratio >= 0.75
        and continuity_ratio >= 0.8
        and volatility_score <= 0.2
    ):
        return "PERSISTENT", blockers
    if volatility_score >= 0.6:
        return "VOLATILE", blockers
    if recurrence_count >= 2 and continuity_ratio >= 0.5:
        return "RECURRING", blockers
    return "TRANSIENT", blockers


def _finalize_node(
    *,
    node_id: str,
    node_kind: str,
    accumulator: dict[str, Any],
    run_count: int,
) -> dict[str, Any]:
    recurrence_count = _as_int(accumulator.get("occurrence_count"))
    source_runs = sorted(str(item) for item in accumulator.get("source_runs", set()))
    lineage_refs = sorted(str(item) for item in accumulator.get("lineage_refs", set()))
    source_hashes = sorted(
        str(item)
        for item in accumulator.get("source_hashes", set())
        if isinstance(item, str) and item
    )
    topology_counter: Counter[str] = accumulator.get("topology_status_counter", Counter())
    advisory_flags = sorted(str(item) for item in accumulator.get("advisory_flags", set()))
    blocked = bool(accumulator.get("blocked"))
    not_computable = bool(accumulator.get("not_computable"))
    persistence_ratio, continuity_ratio, stability_score, volatility_score = _derive_scores(
        recurrence_count=recurrence_count,
        evidence_count=recurrence_count,
        continuity_count=len(source_runs),
        run_count=run_count,
    )
    topology_status = (
        sorted(topology_counter.items(), key=lambda item: (-item[1], item[0]))[0][0]
        if topology_counter
        else NOT_COMPUTABLE
    )
    if blocked:
        final_status = BLOCKED
        if "authority_boundary_violation" not in advisory_flags:
            advisory_flags.append("authority_boundary_violation")
    elif not_computable:
        final_status = NOT_COMPUTABLE
        if "insufficient_fusion_evidence" not in advisory_flags:
            advisory_flags.append("insufficient_fusion_evidence")
    else:
        final_status = "ADVISORY_ONLY"
    return _apply_invariants(
        {
            "schema": "FusionNode.v1",
            "node_id": node_id,
            "node_kind": node_kind,
            "source_runs": source_runs,
            "recurrence_count": recurrence_count,
            "persistence_ratio": persistence_ratio,
            "continuity_ratio": continuity_ratio,
            "topology_status": topology_status,
            "lineage_refs": lineage_refs,
            "source_hashes": source_hashes,
            "advisory_flags": sorted(set(advisory_flags)),
            "final_status": final_status,
            "stability_score": stability_score,
            "volatility_score": volatility_score,
            "evidence_count": recurrence_count,
        }
    )


def _finalize_edge(
    *,
    edge_id: str,
    edge_kind: str,
    accumulator: dict[str, Any],
    run_count: int,
) -> dict[str, Any]:
    recurrence_count = _as_int(accumulator.get("occurrence_count"))
    source_runs = sorted(str(item) for item in accumulator.get("source_runs", set()))
    connected_node_refs = sorted(
        str(item) for item in accumulator.get("connected_node_refs", set())
    )
    source_hashes = sorted(
        str(item)
        for item in accumulator.get("source_hashes", set())
        if isinstance(item, str) and item
    )
    advisory_flags = sorted(str(item) for item in accumulator.get("advisory_flags", set()))
    blocked = bool(accumulator.get("blocked"))
    not_computable = bool(accumulator.get("not_computable"))
    _, continuity_ratio, stability_score, volatility_score = _derive_scores(
        recurrence_count=recurrence_count,
        evidence_count=recurrence_count,
        continuity_count=len(source_runs),
        run_count=run_count,
    )
    if blocked:
        final_status = BLOCKED
        if "authority_boundary_violation" not in advisory_flags:
            advisory_flags.append("authority_boundary_violation")
    elif not_computable:
        final_status = NOT_COMPUTABLE
        if "insufficient_fusion_evidence" not in advisory_flags:
            advisory_flags.append("insufficient_fusion_evidence")
    else:
        final_status = "ADVISORY_ONLY"
    return _apply_invariants(
        {
            "schema": "FusionEdge.v1",
            "edge_id": edge_id,
            "edge_kind": edge_kind,
            "source_runs": source_runs,
            "recurrence_count": recurrence_count,
            "continuity_ratio": continuity_ratio,
            "connected_node_refs": connected_node_refs,
            "source_hashes": source_hashes,
            "advisory_flags": sorted(set(advisory_flags)),
            "final_status": final_status,
            "stability_score": stability_score,
            "volatility_score": volatility_score,
            "evidence_count": recurrence_count,
        }
    )


def build_cross_run_topology_fusion_packet(
    *,
    packet_id: str = "cross_run_topology_fusion_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
        "multi_run_convergence": paths.multi_run_convergence_latest,
        "temporal_state_diff": paths.temporal_state_diff_latest,
        "aal_viz_graph_render_packet": paths.aal_viz_graph_render_packet_latest,
        "projection_chronoscope": paths.projection_chronoscope_latest,
        "read_only_transport": paths.read_only_transport_latest,
        "operator_action_queue": paths.operator_action_queue_latest,
        "projection_bus": paths.projection_bus_latest,
        "temporal_snapshot_spine": paths.temporal_snapshot_spine_latest,
    }
    resolved_sources = {**defaults, **(source_artifact_paths or {})}

    source_entries: list[dict[str, Any]] = []
    source_payloads: dict[str, dict[str, Any] | None] = {}
    source_hashes: dict[str, str | None] = {}
    source_status: dict[str, str] = {}
    source_flags: dict[str, list[str]] = {}

    global_blockers: set[str] = set()
    blocked_sources: set[str] = set()
    not_computable_sources: set[str] = set()

    for source_key in sorted(resolved_sources):
        source_path = resolved_sources[source_key]
        payload, status = _load_artifact(source_path)
        payload_hash = _safe_hash(payload)
        forbidden = _scan_forbidden_true_flags(payload) if isinstance(payload, dict) else []

        source_payloads[source_key] = payload
        source_hashes[source_key] = payload_hash
        source_status[source_key] = status
        source_flags[source_key] = forbidden

        entry_blockers: list[str] = []
        final_status = "PRESENT"

        if status != "PRESENT":
            final_status = NOT_COMPUTABLE
            reason = f"{status.lower()}_artifact:{source_path}"
            entry_blockers.append(reason)
            global_blockers.add(reason)
            not_computable_sources.add(source_key)
        elif forbidden:
            final_status = BLOCKED
            violation = f"authority_boundary_violation:{source_key}"
            entry_blockers.append(violation)
            global_blockers.add(violation)
            blocked_sources.add(source_key)
        elif payload_hash is None:
            final_status = BLOCKED
            hash_blocker = f"hash_not_computable:{source_key}"
            entry_blockers.append(hash_blocker)
            global_blockers.add(hash_blocker)
            blocked_sources.add(source_key)

        source_entries.append(
            _apply_invariants(
                {
                    "schema": "CrossRunTopologyFusionSourceEntry.v1",
                    "source_key": source_key,
                    "source_path": str(source_path),
                    "source_status": status,
                    "source_hash": payload_hash,
                    "authority_boundary_violations": forbidden,
                    "advisory_flags": sorted(
                        {
                            "advisory_only",
                            "analytics_only",
                            "fusion_only",
                            "detection_only",
                            *(
                                ["authority_boundary_violation"]
                                if final_status == BLOCKED and forbidden
                                else []
                            ),
                        }
                    ),
                    "final_status": final_status,
                    "remaining_blockers": sorted(entry_blockers),
                }
            )
        )

    run_labels: list[str] = []
    convergence = source_payloads.get("multi_run_convergence")
    if isinstance(convergence, dict):
        observations = convergence.get("run_observations", [])
        if isinstance(observations, list):
            run_labels = sorted(
                {
                    _as_str(obs.get("run_id"), _as_str(obs.get("packet_id"), ""))
                    for obs in observations
                    if isinstance(obs, dict)
                }
                - {""}
            )
    if not run_labels:
        run_labels = sorted(source_entries[index]["source_key"] for index in range(len(source_entries)))

    node_acc: dict[tuple[str, str], dict[str, Any]] = {}
    edge_acc: dict[tuple[str, str], dict[str, Any]] = {}

    def add_node(
        *,
        node_id: str,
        node_kind: str,
        source_run: str,
        topology_status: str,
        lineage_refs: Iterable[str],
        source_key: str,
        advisory_flags: Iterable[str],
    ) -> None:
        key = (node_id, node_kind)
        item = node_acc.setdefault(
            key,
            {
                "occurrence_count": 0,
                "source_runs": set(),
                "lineage_refs": set(),
                "source_hashes": set(),
                "advisory_flags": set(),
                "topology_status_counter": Counter(),
                "blocked": False,
                "not_computable": False,
            },
        )
        item["occurrence_count"] += 1
        item["source_runs"].add(source_run)
        item["lineage_refs"].update(str(ref) for ref in lineage_refs if str(ref))
        source_hash = source_hashes.get(source_key)
        if isinstance(source_hash, str) and source_hash:
            item["source_hashes"].add(source_hash)
        item["advisory_flags"].update(str(flag) for flag in advisory_flags if str(flag))
        item["topology_status_counter"][topology_status or NOT_COMPUTABLE] += 1
        if source_key in blocked_sources:
            item["blocked"] = True
        if source_key in not_computable_sources:
            item["not_computable"] = True

    def add_edge(
        *,
        edge_id: str,
        edge_kind: str,
        source_run: str,
        connected_node_refs: Iterable[str],
        source_key: str,
        advisory_flags: Iterable[str],
    ) -> None:
        key = (edge_id, edge_kind)
        item = edge_acc.setdefault(
            key,
            {
                "occurrence_count": 0,
                "source_runs": set(),
                "connected_node_refs": set(),
                "source_hashes": set(),
                "advisory_flags": set(),
                "blocked": False,
                "not_computable": False,
            },
        )
        item["occurrence_count"] += 1
        item["source_runs"].add(source_run)
        item["connected_node_refs"].update(
            str(ref) for ref in connected_node_refs if str(ref)
        )
        source_hash = source_hashes.get(source_key)
        if isinstance(source_hash, str) and source_hash:
            item["source_hashes"].add(source_hash)
        item["advisory_flags"].update(str(flag) for flag in advisory_flags if str(flag))
        if source_key in blocked_sources:
            item["blocked"] = True
        if source_key in not_computable_sources:
            item["not_computable"] = True

    if isinstance(convergence, dict):
        observations = convergence.get("run_observations", [])
        ordered_observations = sorted(
            [obs for obs in observations if isinstance(obs, dict)],
            key=lambda obs: (
                _as_str(obs.get("timestamp_or_sequence")),
                _as_str(obs.get("run_id")),
                _as_str(obs.get("source_hash")),
            ),
        )
        previous_run_id: str | None = None
        for obs in ordered_observations:
            run_id = _as_str(obs.get("run_id"), _as_str(obs.get("packet_id"), NOT_COMPUTABLE))
            if not run_id:
                continue
            add_node(
                node_id=run_id,
                node_kind="run_observation",
                source_run=run_id,
                topology_status=_as_str(obs.get("final_status"), NOT_COMPUTABLE),
                lineage_refs=[
                    _as_str(obs.get("packet_id")),
                    _as_str(obs.get("source_artifact")),
                ],
                source_key="multi_run_convergence",
                advisory_flags=_as_str_list(obs.get("advisory_flags")),
            )
            if previous_run_id is not None:
                add_edge(
                    edge_id=str(
                        canonical_hash(
                            {
                                "edge_kind": "replay_path_edge",
                                "source": previous_run_id,
                                "target": run_id,
                            }
                        )
                    ),
                    edge_kind="replay_path_edge",
                    source_run=run_id,
                    connected_node_refs=[previous_run_id, run_id],
                    source_key="multi_run_convergence",
                    advisory_flags=["replay_continuity"],
                )
            previous_run_id = run_id

    temporal_diff = source_payloads.get("temporal_state_diff")
    if isinstance(temporal_diff, dict):
        grouped_entries: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in temporal_diff.get("diff_entries", []):
            if isinstance(entry, dict):
                grouped_entries[_as_str(entry.get("source_surface"), "unknown")].append(entry)
        for source_surface in sorted(grouped_entries):
            ordered_entries = sorted(
                grouped_entries[source_surface],
                key=lambda entry: (
                    _as_str(entry.get("change_type")),
                    _as_str(entry.get("entry_id")),
                ),
            )
            previous_entry_id: str | None = None
            for entry in ordered_entries:
                entry_id = _as_str(entry.get("entry_id"))
                if not entry_id:
                    continue
                add_node(
                    node_id=entry_id,
                    node_kind="diff_entry",
                    source_run=source_surface,
                    topology_status=_as_str(entry.get("change_type"), NOT_COMPUTABLE),
                    lineage_refs=[source_surface],
                    source_key="temporal_state_diff",
                    advisory_flags=_as_str_list(temporal_diff.get("diff_advisory_flags")),
                )
                if previous_entry_id is not None:
                    add_edge(
                        edge_id=str(
                            canonical_hash(
                                {
                                    "edge_kind": "drift_corridor_edge",
                                    "source": previous_entry_id,
                                    "target": entry_id,
                                    "source_surface": source_surface,
                                }
                            )
                        ),
                        edge_kind="drift_corridor_edge",
                        source_run=source_surface,
                        connected_node_refs=[previous_entry_id, entry_id],
                        source_key="temporal_state_diff",
                        advisory_flags=["drift_corridor"],
                    )
                previous_entry_id = entry_id

    graph_packet = source_payloads.get("aal_viz_graph_render_packet")
    if isinstance(graph_packet, dict):
        for node in sorted(
            [item for item in graph_packet.get("nodes", []) if isinstance(item, dict)],
            key=lambda item: (_as_str(item.get("category")), _as_str(item.get("node_id"))),
        ):
            node_id = _as_str(node.get("node_id"))
            if not node_id:
                continue
            add_node(
                node_id=node_id,
                node_kind=_as_str(node.get("category"), "graph_node"),
                source_run="aal_viz_graph_render_packet",
                topology_status=_as_str(node.get("status"), "PRESENT"),
                lineage_refs=[_as_str(node.get("source_ref"))],
                source_key="aal_viz_graph_render_packet",
                advisory_flags=_as_str_list(graph_packet.get("render_advisory_flags")),
            )
        for edge in sorted(
            [item for item in graph_packet.get("edges", []) if isinstance(item, dict)],
            key=lambda item: (_as_str(item.get("category")), _as_str(item.get("edge_id"))),
        ):
            edge_id = _as_str(edge.get("edge_id"))
            if not edge_id:
                continue
            add_edge(
                edge_id=edge_id,
                edge_kind=_as_str(edge.get("category"), "graph_edge"),
                source_run="aal_viz_graph_render_packet",
                connected_node_refs=[
                    _as_str(edge.get("source_node_id")),
                    _as_str(edge.get("target_node_id")),
                ],
                source_key="aal_viz_graph_render_packet",
                advisory_flags=_as_str_list(graph_packet.get("render_advisory_flags")),
            )

    chronoscope = source_payloads.get("projection_chronoscope")
    if isinstance(chronoscope, dict):
        timeline_points = sorted(
            [item for item in chronoscope.get("timeline_points", []) if isinstance(item, dict)],
            key=lambda item: (_as_int(item.get("ordinal")), _as_str(item.get("timeline_point_id"))),
        )
        for point in timeline_points:
            point_id = _as_str(point.get("timeline_point_id"))
            if not point_id:
                continue
            add_node(
                node_id=point_id,
                node_kind="timeline_point",
                source_run="projection_chronoscope",
                topology_status=_as_str(point.get("link_status"), "PRESENT"),
                lineage_refs=[
                    _as_str(point.get("snapshot_id")),
                    _as_str(point.get("message_id")),
                ],
                source_key="projection_chronoscope",
                advisory_flags=_as_str_list(chronoscope.get("chronoscope_advisory_flags")),
            )
            lineage_prev = _as_str(point.get("lineage_prev"))
            snapshot_id = _as_str(point.get("snapshot_id"))
            if lineage_prev and snapshot_id:
                add_edge(
                    edge_id=str(
                        canonical_hash(
                            {
                                "edge_kind": "lineage_edge",
                                "source": lineage_prev,
                                "target": snapshot_id,
                            }
                        )
                    ),
                    edge_kind="lineage_edge",
                    source_run="projection_chronoscope",
                    connected_node_refs=[lineage_prev, snapshot_id],
                    source_key="projection_chronoscope",
                    advisory_flags=["lineage_continuity"],
                )

        cursors = sorted(
            [item for item in chronoscope.get("playback_cursors", []) if isinstance(item, dict)],
            key=lambda item: (_as_int(item.get("ordinal")), _as_str(item.get("cursor"))),
        )
        for cursor in cursors:
            current_cursor = _as_str(cursor.get("cursor"))
            next_cursor = _as_str(cursor.get("next_cursor"))
            if current_cursor and next_cursor:
                add_edge(
                    edge_id=str(
                        canonical_hash(
                            {
                                "edge_kind": "replay_cursor_edge",
                                "source": current_cursor,
                                "target": next_cursor,
                            }
                        )
                    ),
                    edge_kind="replay_cursor_edge",
                    source_run="projection_chronoscope",
                    connected_node_refs=[current_cursor, next_cursor],
                    source_key="projection_chronoscope",
                    advisory_flags=["replay_continuity"],
                )

    transport = source_payloads.get("read_only_transport")
    if isinstance(transport, dict):
        for topic in sorted(
            [item for item in transport.get("topics", []) if isinstance(item, dict)],
            key=lambda item: (_as_str(item.get("topic_name")), _as_str(item.get("topic_id"))),
        ):
            topic_id = _as_str(topic.get("topic_id"))
            if not topic_id:
                continue
            add_node(
                node_id=topic_id,
                node_kind="transport_topic",
                source_run="read_only_transport",
                topology_status="PRESENT",
                lineage_refs=[_as_str(topic.get("topic_name"))],
                source_key="read_only_transport",
                advisory_flags=_as_str_list(transport.get("transport_advisory_flags")),
            )
        frames = sorted(
            [item for item in transport.get("frames", []) if isinstance(item, dict)],
            key=lambda item: (_as_int(item.get("sequence_number")), _as_str(item.get("frame_id"))),
        )
        previous_frame_id: str | None = None
        for frame in frames:
            frame_id = _as_str(frame.get("frame_id"))
            if not frame_id:
                continue
            add_node(
                node_id=frame_id,
                node_kind="transport_frame",
                source_run="read_only_transport",
                topology_status=_as_str(frame.get("blocker_status"), "PRESENT"),
                lineage_refs=[_as_str(frame.get("topic_id"))],
                source_key="read_only_transport",
                advisory_flags=_as_str_list(frame.get("advisory_flags")),
            )
            if previous_frame_id is not None:
                add_edge(
                    edge_id=str(
                        canonical_hash(
                            {
                                "edge_kind": "transport_path_edge",
                                "source": previous_frame_id,
                                "target": frame_id,
                            }
                        )
                    ),
                    edge_kind="transport_path_edge",
                    source_run="read_only_transport",
                    connected_node_refs=[previous_frame_id, frame_id],
                    source_key="read_only_transport",
                    advisory_flags=["transport_continuity"],
                )
            previous_frame_id = frame_id

    operator_queue = source_payloads.get("operator_action_queue")
    if isinstance(operator_queue, dict):
        for item in sorted(
            [
                entry
                for entry in operator_queue.get("operator_action_items", [])
                if isinstance(entry, dict)
            ],
            key=lambda entry: (_as_str(entry.get("category")), _as_str(entry.get("item_id"))),
        ):
            item_id = _as_str(item.get("item_id"))
            if not item_id:
                continue
            add_node(
                node_id=item_id,
                node_kind="queue_item",
                source_run="operator_action_queue",
                topology_status=_as_str(item.get("severity"), "LOW"),
                lineage_refs=[_as_str(item.get("source_artifact"))],
                source_key="operator_action_queue",
                advisory_flags=_as_str_list(operator_queue.get("queue_advisory_flags")),
            )
        for escalation in sorted(
            [
                entry
                for entry in operator_queue.get("escalation_paths", [])
                if isinstance(entry, dict)
            ],
            key=lambda entry: _as_str(entry.get("escalation_id")),
        ):
            escalation_id = _as_str(escalation.get("escalation_id"))
            related = _as_str_list(escalation.get("related_action_item_ids"))
            if not escalation_id or len(related) < 2:
                continue
            for source_item, target_item in zip(related, related[1:]):
                add_edge(
                    edge_id=str(
                        canonical_hash(
                            {
                                "edge_kind": "queue_escalation_edge",
                                "escalation_id": escalation_id,
                                "source": source_item,
                                "target": target_item,
                            }
                        )
                    ),
                    edge_kind="queue_escalation_edge",
                    source_run="operator_action_queue",
                    connected_node_refs=[source_item, target_item],
                    source_key="operator_action_queue",
                    advisory_flags=["queue_blocker_structure"],
                )

    projection_bus = source_payloads.get("projection_bus")
    if isinstance(projection_bus, dict):
        for message in sorted(
            [item for item in projection_bus.get("messages", []) if isinstance(item, dict)],
            key=lambda item: (_as_str(item.get("topic")), _as_str(item.get("message_id"))),
        ):
            message_id = _as_str(message.get("message_id"))
            if not message_id:
                continue
            add_node(
                node_id=message_id,
                node_kind="projection_bus_message",
                source_run="projection_bus",
                topology_status=_as_str(message.get("topic"), "PRESENT"),
                lineage_refs=[_as_str(message.get("snapshot_id"))],
                source_key="projection_bus",
                advisory_flags=_as_str_list(message.get("advisory_flags")),
            )

    snapshot_spine = source_payloads.get("temporal_snapshot_spine")
    if isinstance(snapshot_spine, dict):
        for snapshot in sorted(
            [
                item
                for item in snapshot_spine.get("ordered_snapshots", [])
                if isinstance(item, dict)
            ],
            key=lambda item: (_as_int(item.get("ordinal")), _as_str(item.get("snapshot_id"))),
        ):
            snapshot_id = _as_str(snapshot.get("snapshot_id"))
            if not snapshot_id:
                continue
            add_node(
                node_id=snapshot_id,
                node_kind="snapshot",
                source_run="temporal_snapshot_spine",
                topology_status=_as_str(snapshot.get("status"), "PRESENT"),
                lineage_refs=[
                    _as_str(snapshot.get("projection_id")),
                    _as_str(snapshot.get("projection_hash")),
                ],
                source_key="temporal_snapshot_spine",
                advisory_flags=["snapshot_lineage"],
            )
            lineage_prev = _as_str(snapshot.get("lineage_prev"))
            if lineage_prev:
                add_edge(
                    edge_id=str(
                        canonical_hash(
                            {
                                "edge_kind": "snapshot_lineage_edge",
                                "source": lineage_prev,
                                "target": snapshot_id,
                            }
                        )
                    ),
                    edge_kind="snapshot_lineage_edge",
                    source_run="temporal_snapshot_spine",
                    connected_node_refs=[lineage_prev, snapshot_id],
                    source_key="temporal_snapshot_spine",
                    advisory_flags=["lineage_continuity"],
                )

    run_count = len(run_labels)
    fusion_nodes = [
        _finalize_node(node_id=node_id, node_kind=node_kind, accumulator=acc, run_count=run_count)
        for (node_id, node_kind), acc in node_acc.items()
    ]
    fusion_edges = [
        _finalize_edge(edge_id=edge_id, edge_kind=edge_kind, accumulator=acc, run_count=run_count)
        for (edge_id, edge_kind), acc in edge_acc.items()
    ]
    fusion_nodes = sorted(
        fusion_nodes,
        key=lambda node: (
            _as_str(node.get("node_kind")),
            -_as_int(node.get("recurrence_count")),
            _as_str(node.get("node_id")),
            _as_str((node.get("source_hashes") or [""])[0] if isinstance(node.get("source_hashes"), list) else ""),
        ),
    )
    fusion_edges = sorted(
        fusion_edges,
        key=lambda edge: (
            _as_str(edge.get("edge_kind")),
            -_as_int(edge.get("recurrence_count")),
            _as_str(edge.get("edge_id")),
            _as_str((edge.get("source_hashes") or [""])[0] if isinstance(edge.get("source_hashes"), list) else ""),
        ),
    )

    grouped_nodes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in fusion_nodes:
        grouped_nodes[_as_str(node.get("node_kind"), "unknown")].append(node)

    persistence_clusters: list[dict[str, Any]] = []
    for node_kind in sorted(grouped_nodes):
        nodes = grouped_nodes[node_kind]
        recurrence_count = sum(_as_int(node.get("recurrence_count")) for node in nodes)
        evidence_count = sum(_as_int(node.get("evidence_count")) for node in nodes)
        persistence_ratio = (
            sum(_as_float(node.get("persistence_ratio")) for node in nodes) / len(nodes)
            if nodes
            else 0.0
        )
        continuity_ratio = (
            sum(_as_float(node.get("continuity_ratio")) for node in nodes) / len(nodes)
            if nodes
            else 0.0
        )
        stability_score = (
            sum(_as_float(node.get("stability_score")) for node in nodes) / len(nodes)
            if nodes
            else 0.0
        )
        volatility_score = (
            sum(_as_float(node.get("volatility_score")) for node in nodes) / len(nodes)
            if nodes
            else 1.0
        )
        cluster_status = (
            BLOCKED
            if any(_as_str(node.get("final_status")) == BLOCKED for node in nodes)
            else NOT_COMPUTABLE
            if any(_as_str(node.get("final_status")) == NOT_COMPUTABLE for node in nodes)
            else "ADVISORY_ONLY"
        )
        persistence_clusters.append(
            _apply_invariants(
                {
                    "schema": "TopologyPersistenceCluster.v1",
                    "cluster_id": str(
                        canonical_hash(
                            {
                                "cluster_kind": "topology_persistence",
                                "node_kind": node_kind,
                                "node_refs": [node["node_id"] for node in nodes],
                            }
                        )
                    ),
                    "cluster_kind": node_kind,
                    "node_refs": [node["node_id"] for node in nodes],
                    "recurrence_count": recurrence_count,
                    "persistence_ratio": round(persistence_ratio, 6),
                    "continuity_ratio": round(continuity_ratio, 6),
                    "stability_score": round(stability_score, 6),
                    "volatility_score": round(volatility_score, 6),
                    "evidence_count": evidence_count,
                    "advisory_flags": sorted(
                        {
                            "topology_persistence",
                            *(
                                ["authority_boundary_violation"]
                                if cluster_status == BLOCKED
                                else []
                            ),
                            *(
                                ["insufficient_fusion_evidence"]
                                if cluster_status == NOT_COMPUTABLE
                                else []
                            ),
                        }
                    ),
                    "final_status": cluster_status,
                }
            )
        )

    lineage_edges = [
        edge for edge in fusion_edges if _as_str(edge.get("edge_kind")).endswith("lineage_edge")
    ]
    lineage_corridors: list[dict[str, Any]] = []
    if lineage_edges:
        for index, edge in enumerate(lineage_edges):
            lineage_corridors.append(
                _apply_invariants(
                    {
                        "schema": "LineageFusionCorridor.v1",
                        "corridor_id": str(
                            canonical_hash(
                                {
                                    "corridor_kind": "lineage",
                                    "edge_id": edge["edge_id"],
                                    "ordinal": index,
                                }
                            )
                        ),
                        "corridor_refs": [edge["edge_id"]],
                        "lineage_refs": edge.get("connected_node_refs", []),
                        "recurrence_count": _as_int(edge.get("recurrence_count")),
                        "persistence_ratio": _as_float(edge.get("continuity_ratio")),
                        "continuity_ratio": _as_float(edge.get("continuity_ratio")),
                        "stability_score": _as_float(edge.get("stability_score")),
                        "volatility_score": _as_float(edge.get("volatility_score")),
                        "evidence_count": _as_int(edge.get("evidence_count")),
                        "advisory_flags": sorted(
                            {
                                "lineage_continuity",
                                *(
                                    ["authority_boundary_violation"]
                                    if _as_str(edge.get("final_status")) == BLOCKED
                                    else []
                                ),
                            }
                        ),
                        "final_status": _as_str(edge.get("final_status"), NOT_COMPUTABLE),
                    }
                )
            )
    else:
        lineage_corridors.append(
            _apply_invariants(
                {
                    "schema": "LineageFusionCorridor.v1",
                    "corridor_id": str(
                        canonical_hash({"corridor_kind": "lineage", "packet_id": packet_id})
                    ),
                    "corridor_refs": [],
                    "lineage_refs": [],
                    "recurrence_count": 0,
                    "persistence_ratio": 0.0,
                    "continuity_ratio": 0.0,
                    "stability_score": 0.0,
                    "volatility_score": 1.0,
                    "evidence_count": 0,
                    "advisory_flags": ["lineage_continuity", "insufficient_fusion_evidence"],
                    "final_status": NOT_COMPUTABLE,
                }
            )
        )
        global_blockers.add("insufficient_fusion_evidence:lineage")

    replay_edges = [
        edge
        for edge in fusion_edges
        if _as_str(edge.get("edge_kind")) in {"replay_path_edge", "replay_cursor_edge"}
    ]
    replay_cluster = _apply_invariants(
        {
            "schema": "ReplayContinuityCluster.v1",
            "cluster_id": str(
                canonical_hash(
                    {
                        "cluster_kind": "replay_continuity",
                        "edge_ids": [edge["edge_id"] for edge in replay_edges],
                    }
                )
            ),
            "edge_refs": [edge["edge_id"] for edge in replay_edges],
            "recurrence_count": sum(_as_int(edge.get("recurrence_count")) for edge in replay_edges),
            "persistence_ratio": round(
                (
                    sum(_as_float(edge.get("continuity_ratio")) for edge in replay_edges)
                    / len(replay_edges)
                )
                if replay_edges
                else 0.0,
                6,
            ),
            "continuity_ratio": round(
                (
                    sum(_as_float(edge.get("continuity_ratio")) for edge in replay_edges)
                    / len(replay_edges)
                )
                if replay_edges
                else 0.0,
                6,
            ),
            "stability_score": round(
                (
                    sum(_as_float(edge.get("stability_score")) for edge in replay_edges)
                    / len(replay_edges)
                )
                if replay_edges
                else 0.0,
                6,
            ),
            "volatility_score": round(
                (
                    sum(_as_float(edge.get("volatility_score")) for edge in replay_edges)
                    / len(replay_edges)
                )
                if replay_edges
                else 1.0,
                6,
            ),
            "evidence_count": len(replay_edges),
            "advisory_flags": sorted(
                {"replay_continuity", *(["insufficient_fusion_evidence"] if not replay_edges else [])}
            ),
            "final_status": (
                NOT_COMPUTABLE if not replay_edges else "ADVISORY_ONLY"
            ),
        }
    )
    if not replay_edges:
        global_blockers.add("insufficient_fusion_evidence:replay")

    transport_edges = [
        edge for edge in fusion_edges if _as_str(edge.get("edge_kind")) == "transport_path_edge"
    ]
    transport_cluster = _apply_invariants(
        {
            "schema": "TransportContinuityCluster.v1",
            "cluster_id": str(
                canonical_hash(
                    {
                        "cluster_kind": "transport_continuity",
                        "edge_ids": [edge["edge_id"] for edge in transport_edges],
                    }
                )
            ),
            "edge_refs": [edge["edge_id"] for edge in transport_edges],
            "recurrence_count": sum(
                _as_int(edge.get("recurrence_count")) for edge in transport_edges
            ),
            "persistence_ratio": round(
                (
                    sum(_as_float(edge.get("continuity_ratio")) for edge in transport_edges)
                    / len(transport_edges)
                )
                if transport_edges
                else 0.0,
                6,
            ),
            "continuity_ratio": round(
                (
                    sum(_as_float(edge.get("continuity_ratio")) for edge in transport_edges)
                    / len(transport_edges)
                )
                if transport_edges
                else 0.0,
                6,
            ),
            "stability_score": round(
                (
                    sum(_as_float(edge.get("stability_score")) for edge in transport_edges)
                    / len(transport_edges)
                )
                if transport_edges
                else 0.0,
                6,
            ),
            "volatility_score": round(
                (
                    sum(_as_float(edge.get("volatility_score")) for edge in transport_edges)
                    / len(transport_edges)
                )
                if transport_edges
                else 1.0,
                6,
            ),
            "evidence_count": len(transport_edges),
            "advisory_flags": sorted(
                {
                    "transport_continuity",
                    *(["insufficient_fusion_evidence"] if not transport_edges else []),
                }
            ),
            "final_status": NOT_COMPUTABLE if not transport_edges else "ADVISORY_ONLY",
        }
    )
    if not transport_edges:
        global_blockers.add("insufficient_fusion_evidence:transport")

    drift_edges = [
        edge for edge in fusion_edges if _as_str(edge.get("edge_kind")) == "drift_corridor_edge"
    ]
    drift_summary = _apply_invariants(
        {
            "schema": "DriftCorridorSummary.v1",
            "drift_corridor_status": NOT_COMPUTABLE if not drift_edges else "ADVISORY_ONLY",
            "corridor_refs": [edge["edge_id"] for edge in drift_edges],
            "recurrence_count": sum(_as_int(edge.get("recurrence_count")) for edge in drift_edges),
            "persistence_ratio": round(
                (
                    sum(_as_float(edge.get("continuity_ratio")) for edge in drift_edges)
                    / len(drift_edges)
                )
                if drift_edges
                else 0.0,
                6,
            ),
            "continuity_ratio": round(
                (
                    sum(_as_float(edge.get("continuity_ratio")) for edge in drift_edges)
                    / len(drift_edges)
                )
                if drift_edges
                else 0.0,
                6,
            ),
            "stability_score": round(
                (
                    sum(_as_float(edge.get("stability_score")) for edge in drift_edges)
                    / len(drift_edges)
                )
                if drift_edges
                else 0.0,
                6,
            ),
            "volatility_score": round(
                (
                    sum(_as_float(edge.get("volatility_score")) for edge in drift_edges)
                    / len(drift_edges)
                )
                if drift_edges
                else 1.0,
                6,
            ),
            "evidence_count": len(drift_edges),
            "advisory_flags": sorted(
                {"drift_corridor", *(["insufficient_fusion_evidence"] if not drift_edges else [])}
            ),
            "final_status": NOT_COMPUTABLE if not drift_edges else "ADVISORY_ONLY",
        }
    )
    if not drift_edges:
        global_blockers.add("insufficient_fusion_evidence:drift")

    unstable_topology_zones = sorted(
        {
            _as_str(node.get("node_id"))
            for node in fusion_nodes
            if _as_str(node.get("final_status")) == BLOCKED
            or _as_float(node.get("volatility_score")) >= 0.6
        }
        - {""}
    )

    queue_items = [
        node for node in fusion_nodes if _as_str(node.get("node_kind")) == "queue_item"
    ]
    blocked_queue_items = [
        node for node in queue_items if _as_str(node.get("topology_status")) in {"HIGH", "CRITICAL"}
    ]
    blocker_recurrence_count = len(blocked_queue_items)

    motif_inputs = [
        (
            "topology_structure",
            len(fusion_nodes),
            (
                sum(_as_float(node.get("persistence_ratio")) for node in fusion_nodes)
                / len(fusion_nodes)
            )
            if fusion_nodes
            else 0.0,
            (
                sum(_as_float(node.get("continuity_ratio")) for node in fusion_nodes)
                / len(fusion_nodes)
            )
            if fusion_nodes
            else 0.0,
            (
                sum(_as_float(node.get("volatility_score")) for node in fusion_nodes)
                / len(fusion_nodes)
            )
            if fusion_nodes
            else 1.0,
            len(fusion_nodes),
            False,
            bool(unstable_topology_zones),
        ),
        (
            "lineage_corridor",
            sum(_as_int(item.get("recurrence_count")) for item in lineage_corridors),
            (
                sum(_as_float(item.get("persistence_ratio")) for item in lineage_corridors)
                / len(lineage_corridors)
            ),
            (
                sum(_as_float(item.get("continuity_ratio")) for item in lineage_corridors)
                / len(lineage_corridors)
            ),
            (
                sum(_as_float(item.get("volatility_score")) for item in lineage_corridors)
                / len(lineage_corridors)
            ),
            sum(_as_int(item.get("evidence_count")) for item in lineage_corridors),
            any(_as_str(item.get("final_status")) == BLOCKED for item in lineage_corridors),
            False,
        ),
        (
            "replay_continuity",
            _as_int(replay_cluster.get("recurrence_count")),
            _as_float(replay_cluster.get("persistence_ratio")),
            _as_float(replay_cluster.get("continuity_ratio")),
            _as_float(replay_cluster.get("volatility_score"), 1.0),
            _as_int(replay_cluster.get("evidence_count")),
            _as_str(replay_cluster.get("final_status")) == BLOCKED,
            False,
        ),
        (
            "transport_continuity",
            _as_int(transport_cluster.get("recurrence_count")),
            _as_float(transport_cluster.get("persistence_ratio")),
            _as_float(transport_cluster.get("continuity_ratio")),
            _as_float(transport_cluster.get("volatility_score"), 1.0),
            _as_int(transport_cluster.get("evidence_count")),
            _as_str(transport_cluster.get("final_status")) == BLOCKED,
            False,
        ),
        (
            "drift_corridor",
            _as_int(drift_summary.get("recurrence_count")),
            _as_float(drift_summary.get("persistence_ratio")),
            _as_float(drift_summary.get("continuity_ratio")),
            _as_float(drift_summary.get("volatility_score"), 1.0),
            _as_int(drift_summary.get("evidence_count")),
            _as_str(drift_summary.get("final_status")) == BLOCKED,
            False,
        ),
        (
            "queue_blocker_structure",
            blocker_recurrence_count,
            _ratio(float(blocker_recurrence_count), float(max(1, len(queue_items)))),
            _ratio(float(blocker_recurrence_count), float(max(1, len(queue_items)))),
            round(1.0 - _ratio(float(blocker_recurrence_count), float(max(1, len(queue_items)))), 6),
            len(queue_items),
            False,
            blocker_recurrence_count > 0,
        ),
    ]

    motif_summaries: list[dict[str, Any]] = []
    for motif_kind, recurrence_count, persistence_ratio, continuity_ratio, volatility_score, evidence_count, blocked, degraded in motif_inputs:
        classification, motif_blockers = _classify_motif(
            recurrence_count=recurrence_count,
            persistence_ratio=persistence_ratio,
            continuity_ratio=continuity_ratio,
            volatility_score=volatility_score,
            evidence_count=evidence_count,
            blocked=blocked
            or bool(
                blocked_sources
                and motif_kind in {"topology_structure", "lineage_corridor", "queue_blocker_structure"}
            ),
            degraded=degraded,
        )
        motif_stability = round(max(0.0, 1.0 - volatility_score), 6)
        motif_summaries.append(
            _apply_invariants(
                {
                    "schema": "StructuralMotifSummary.v1",
                    "motif_id": str(canonical_hash({"motif_kind": motif_kind, "packet_id": packet_id})),
                    "motif_kind": motif_kind,
                    "classification": classification,
                    "recurrence_count": recurrence_count,
                    "persistence_ratio": round(persistence_ratio, 6),
                    "continuity_ratio": round(continuity_ratio, 6),
                    "stability_score": motif_stability,
                    "volatility_score": round(volatility_score, 6),
                    "evidence_count": evidence_count,
                    "advisory_flags": sorted(
                        {
                            "structural_motif",
                            *(
                                ["insufficient_fusion_evidence"]
                                if classification == NOT_COMPUTABLE
                                else []
                            ),
                            *(
                                ["authority_boundary_violation"]
                                if classification == BLOCKED
                                else []
                            ),
                            *(["degraded_structure"] if classification == "DEGRADED" else []),
                        }
                    ),
                    "remaining_blockers": sorted(motif_blockers),
                    "final_status": (
                        BLOCKED
                        if classification == BLOCKED
                        else NOT_COMPUTABLE
                        if classification == NOT_COMPUTABLE
                        else "ADVISORY_ONLY"
                    ),
                }
            )
        )

    motif_summaries = sorted(
        motif_summaries,
        key=lambda motif: (
            _MOTIF_ORDER.get(_as_str(motif.get("classification"), NOT_COMPUTABLE), 999),
            _as_str(motif.get("motif_kind")),
            _as_str(motif.get("motif_id")),
        ),
    )

    topology_index = _apply_invariants(
        {
            "schema": "CrossRunTopologyIndex.v1",
            "node_ids_by_kind": {
                kind: sorted(node["node_id"] for node in nodes)
                for kind, nodes in sorted(grouped_nodes.items())
            },
            "edge_ids_by_kind": {
                kind: sorted(
                    edge["edge_id"]
                    for edge in fusion_edges
                    if _as_str(edge.get("edge_kind")) == kind
                )
                for kind in sorted(
                    {_as_str(edge.get("edge_kind")) for edge in fusion_edges if edge.get("edge_kind")}
                )
            },
            "run_index": {
                run_id: sorted(
                    {
                        _as_str(node.get("node_id"))
                        for node in fusion_nodes
                        if run_id in _as_str_list(node.get("source_runs"))
                    }
                )
                for run_id in sorted(run_labels)
            },
            "shared_node_ids": sorted(
                {
                    _as_str(node.get("node_id"))
                    for node in fusion_nodes
                    if _as_int(node.get("recurrence_count")) > 1
                }
            ),
            "shared_source_hashes": sorted(
                {
                    source_hash
                    for node in fusion_nodes
                    for source_hash in _as_str_list(node.get("source_hashes"))
                    if source_hash
                }
            ),
            "evidence_count": len(fusion_nodes) + len(fusion_edges),
            "final_status": (
                BLOCKED
                if blocked_sources
                else NOT_COMPUTABLE
                if not_computable_sources
                else "ADVISORY_ONLY"
            ),
        }
    )

    topology_stability_score = round(
        (
            sum(_as_float(node.get("stability_score")) for node in fusion_nodes)
            / len(fusion_nodes)
        )
        if fusion_nodes
        else 0.0,
        6,
    )

    if blocked_sources:
        final_status = BLOCKED
    elif not_computable_sources:
        final_status = NOT_COMPUTABLE
    else:
        final_status = "ADVISORY_ONLY"

    advisory_flags = sorted(
        {
            "advisory_only",
            "analytics_only",
            "fusion_only",
            "detection_only",
            "deterministic_ordering",
            "evidence_backed",
            "fail_closed",
            *(["authority_boundary_violation"] if blocked_sources else []),
            *(["insufficient_fusion_evidence"] if not_computable_sources else []),
        }
    )

    remaining_blockers = sorted(
        set(global_blockers)
        | {
            blocker
            for motif in motif_summaries
            for blocker in _as_str_list(motif.get("remaining_blockers"))
            if blocker
        }
    )

    packet_hash = str(
        canonical_hash(
            {
                "packet_id": packet_id,
                "source_entries": source_entries,
                "fusion_nodes": fusion_nodes,
                "fusion_edges": fusion_edges,
                "topology_persistence_clusters": persistence_clusters,
                "lineage_fusion_corridors": lineage_corridors,
                "replay_continuity_cluster": replay_cluster,
                "transport_continuity_cluster": transport_cluster,
                "drift_corridor_summary": drift_summary,
                "structural_motif_summaries": motif_summaries,
                "cross_run_topology_index": topology_index,
                "remaining_blockers": remaining_blockers,
                "final_status": final_status,
            }
        )
    )

    return _apply_invariants(
        {
            "schema": "CrossRunTopologyFusionPacket.v1",
            "patch_id": PATCH_ID,
            "packet_id": packet_id,
            "packet_hash": packet_hash,
            "source_entries": source_entries,
            "source_artifacts": {key: str(value) for key, value in sorted(resolved_sources.items())},
            "fusion_nodes": fusion_nodes,
            "fusion_edges": fusion_edges,
            "topology_persistence_clusters": persistence_clusters,
            "lineage_fusion_corridors": lineage_corridors,
            "drift_corridor_summary": drift_summary,
            "replay_continuity_cluster": replay_cluster,
            "transport_continuity_cluster": transport_cluster,
            "structural_motif_summaries": motif_summaries,
            "cross_run_topology_index": topology_index,
            "cross_run_topology_fusion_status": final_status,
            "fusion_node_count": len(fusion_nodes),
            "fusion_edge_count": len(fusion_edges),
            "persistent_cluster_count": len(
                [
                    cluster
                    for cluster in persistence_clusters
                    if _as_float(cluster.get("persistence_ratio")) >= 0.75
                    and _as_float(cluster.get("continuity_ratio")) >= 0.75
                ]
            ),
            "lineage_corridor_count": len(lineage_corridors),
            "replay_continuity_status": _as_str(
                replay_cluster.get("final_status"), NOT_COMPUTABLE
            ),
            "transport_continuity_status": _as_str(
                transport_cluster.get("final_status"), NOT_COMPUTABLE
            ),
            "topology_stability_score": topology_stability_score,
            "blocker_recurrence_count": blocker_recurrence_count,
            "unstable_topology_zones": unstable_topology_zones,
            "fusion_advisory_flags": advisory_flags,
            "recommended_operator_next_actions": (
                [
                    "Review authority boundary violations before trusting fused topology structures.",
                    "Regenerate missing/corrupt source artifacts and rerun cross-run topology fusion.",
                    "Preserve advisory-only posture and require manual operator review.",
                ]
                if remaining_blockers
                else [
                    "Continue deterministic advisory-only topology fusion monitoring.",
                    "Review recurring motifs for manual governance triage.",
                ]
            ),
            "final_status": final_status,
            "remaining_blockers": remaining_blockers,
        }
    )


def write_cross_run_topology_fusion_packet(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_cross_run_topology_fusion_markdown(packet: dict[str, Any]) -> str:
    motifs = packet.get("structural_motif_summaries", [])
    motif_lines = [
        (
            f"- `{_as_str(motif.get('motif_kind'), NOT_COMPUTABLE)}`: "
            f"`{_as_str(motif.get('classification'), NOT_COMPUTABLE)}`"
        )
        for motif in motifs
        if isinstance(motif, dict)
    ]

    blockers = _as_str_list(packet.get("remaining_blockers"))
    actions = _as_str_list(packet.get("recommended_operator_next_actions"))

    lines = [
        f"# Cross-Run Topology Fusion — {_as_str(packet.get('packet_id'))}",
        "",
        f"**Patch:** `{_as_str(packet.get('patch_id'))}`",
        f"**Final Status:** `{_as_str(packet.get('final_status'), NOT_COMPUTABLE)}`",
        f"**Fusion Node Count:** `{_as_int(packet.get('fusion_node_count'))}`",
        f"**Fusion Edge Count:** `{_as_int(packet.get('fusion_edge_count'))}`",
        f"**Persistent Cluster Count:** `{_as_int(packet.get('persistent_cluster_count'))}`",
        f"**Lineage Corridor Count:** `{_as_int(packet.get('lineage_corridor_count'))}`",
        f"**Replay Continuity Status:** `{_as_str(packet.get('replay_continuity_status'), NOT_COMPUTABLE)}`",
        (
            f"**Drift Corridor Status:** "
            f"`{_as_str((packet.get('drift_corridor_summary') or {}).get('drift_corridor_status'), NOT_COMPUTABLE)}`"
        ),
        f"**Transport Continuity Status:** `{_as_str(packet.get('transport_continuity_status'), NOT_COMPUTABLE)}`",
        f"**Topology Stability Score:** `{_as_float(packet.get('topology_stability_score'))}`",
        "",
        "## Unstable Topology Zones",
    ]

    zones = _as_str_list(packet.get("unstable_topology_zones"))
    if zones:
        lines.extend(f"- `{zone}`" for zone in zones)
    else:
        lines.append("- None")

    lines.extend(["", "## Motif Classifications"])
    if motif_lines:
        lines.extend(motif_lines)
    else:
        lines.append(f"- `{NOT_COMPUTABLE}`")

    lines.extend(["", "## Blockers"])
    if blockers:
        lines.extend(f"- `{blocker}`" for blocker in blockers)
    else:
        lines.append("- None")

    lines.extend(["", "## Operator Next Actions"])
    if actions:
        lines.extend(f"- {action}" for action in actions)
    else:
        lines.append("- Continue advisory-only fusion monitoring.")

    lines.append("")
    return "\n".join(lines)
