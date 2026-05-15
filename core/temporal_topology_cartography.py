"""Deterministic temporal topology cartography and regime atlas for P14-P22."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P23-TEMPORAL-TOPOLOGY-CARTOGRAPHY-AND-REGIME-ATLAS-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"
ADVISORY_ONLY = "ADVISORY_ONLY"

_INVARIANTS: dict[str, Any] = {
    "advisory_only": True,
    "analytics_only": True,
    "cartography_only": True,
    "visualization_support_only": True,
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

_REGION_KIND_ORDER = {
    "STABLE_REGION": 0,
    "CONVERGENCE_REGION": 1,
    "DIVERGENCE_REGION": 2,
    "VOLATILE_REGION": 3,
    "DRIFT_ZONE": 4,
    "REPLAY_CORRIDOR": 5,
    "CONTINUITY_CORRIDOR": 6,
    "DEGRADED_REGION": 7,
    NOT_COMPUTABLE: 8,
    BLOCKED: 9,
}

_CORRIDOR_KIND_ORDER = {
    "REPLAY_CORRIDOR": 0,
    "CONTINUITY_CORRIDOR": 1,
    "STABLE_REGION": 2,
    "CONVERGENCE_REGION": 3,
    "DIVERGENCE_REGION": 4,
    "VOLATILE_REGION": 5,
    "DRIFT_ZONE": 6,
    "DEGRADED_REGION": 7,
    NOT_COMPUTABLE: 8,
    BLOCKED: 9,
}


def _apply_invariants(payload: dict[str, Any]) -> dict[str, Any]:
    return {**payload, **_INVARIANTS}


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


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted(str(item) for item in value if str(item))


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    value = numerator / denominator
    return round(max(0.0, min(1.0, value)), 6)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / float(len(values)), 6)


def _stability_to_score(status: str) -> float:
    mapping = {
        "PASS": 1.0,
        ADVISORY_ONLY: 0.75,
        "PRESENT": 0.75,
        NOT_COMPUTABLE: 0.25,
        BLOCKED: 0.0,
    }
    return mapping.get(status, 0.5)


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


def _classify_region(
    *,
    blocked: bool,
    not_computable: bool,
    persistence_ratio: float,
    continuity_ratio: float,
    volatility_score: float,
    drift_score: float,
    evidence_count: int,
    advisory_flags: list[str],
) -> tuple[str, str, list[str]]:
    flags = sorted(set(advisory_flags))
    if blocked:
        if "authority_boundary_violation" not in flags:
            flags.append("authority_boundary_violation")
        return BLOCKED, BLOCKED, sorted(set(flags))
    if not_computable or evidence_count < 2:
        if "remaining_blocker: insufficient_cartography_evidence" not in flags:
            flags.append("remaining_blocker: insufficient_cartography_evidence")
        return NOT_COMPUTABLE, NOT_COMPUTABLE, sorted(set(flags))
    if drift_score >= 0.65:
        return "DRIFT_ZONE", ADVISORY_ONLY, flags
    if volatility_score >= 0.65:
        return "VOLATILE_REGION", ADVISORY_ONLY, flags
    if any(flag.startswith("queue_blocker") for flag in flags):
        return "DEGRADED_REGION", ADVISORY_ONLY, flags
    if continuity_ratio <= 0.35 and persistence_ratio <= 0.4:
        return "DIVERGENCE_REGION", ADVISORY_ONLY, flags
    if continuity_ratio >= 0.75 and persistence_ratio >= 0.65:
        return "CONVERGENCE_REGION", ADVISORY_ONLY, flags
    if persistence_ratio >= 0.8 and volatility_score <= 0.2:
        return "STABLE_REGION", ADVISORY_ONLY, flags
    return "STABLE_REGION", ADVISORY_ONLY, flags


def _classify_corridor(
    *,
    blocked: bool,
    not_computable: bool,
    corridor_hint: str,
    persistence_ratio: float,
    continuity_ratio: float,
    volatility_score: float,
    drift_score: float,
    replay_stability: float,
    transport_stability: float,
    evidence_count: int,
    advisory_flags: list[str],
) -> tuple[str, str, list[str]]:
    flags = sorted(set(advisory_flags))
    if blocked:
        if "authority_boundary_violation" not in flags:
            flags.append("authority_boundary_violation")
        return BLOCKED, BLOCKED, sorted(set(flags))
    if not_computable or evidence_count < 2:
        if "remaining_blocker: insufficient_cartography_evidence" not in flags:
            flags.append("remaining_blocker: insufficient_cartography_evidence")
        return NOT_COMPUTABLE, NOT_COMPUTABLE, sorted(set(flags))
    if drift_score >= 0.65:
        return "DRIFT_ZONE", ADVISORY_ONLY, flags
    if corridor_hint == "replay" and replay_stability >= 0.6 and continuity_ratio >= 0.6:
        return "REPLAY_CORRIDOR", ADVISORY_ONLY, flags
    if corridor_hint in {"lineage", "transport", "continuity"} and (
        continuity_ratio >= 0.6 or transport_stability >= 0.6
    ):
        return "CONTINUITY_CORRIDOR", ADVISORY_ONLY, flags
    if volatility_score >= 0.65:
        return "VOLATILE_REGION", ADVISORY_ONLY, flags
    if continuity_ratio <= 0.35 and persistence_ratio <= 0.4:
        return "DIVERGENCE_REGION", ADVISORY_ONLY, flags
    if continuity_ratio >= 0.75 and persistence_ratio >= 0.65:
        return "CONVERGENCE_REGION", ADVISORY_ONLY, flags
    if persistence_ratio >= 0.8 and volatility_score <= 0.2:
        return "STABLE_REGION", ADVISORY_ONLY, flags
    return "DEGRADED_REGION", ADVISORY_ONLY, flags


def _source_entries(
    source_paths: dict[str, str | Path],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any] | None], dict[str, str | None], list[str]]:
    entries: list[dict[str, Any]] = []
    payloads: dict[str, dict[str, Any] | None] = {}
    source_hashes: dict[str, str | None] = {}
    blockers: set[str] = set()

    for source_key, source_path in sorted(source_paths.items(), key=lambda item: item[0]):
        payload, status = _load_artifact(source_path)
        payloads[source_key] = payload
        payload_hash = _safe_hash(payload)
        source_hashes[source_key] = payload_hash
        forbidden = _scan_forbidden_true_flags(payload) if payload is not None else []
        final_status = "PRESENT"
        local_blockers: list[str] = []
        if status != "PRESENT":
            final_status = NOT_COMPUTABLE
            local_blockers.append(f"{status.lower()}_artifact:{source_path}")
        if forbidden:
            final_status = BLOCKED
            local_blockers.extend(
                f"authority_boundary_violation:{source_key}:{path}" for path in forbidden
            )
        if status == "PRESENT" and payload_hash is None:
            final_status = BLOCKED
            local_blockers.append(f"hash_not_computable:{source_key}")
        blockers.update(local_blockers)

        entries.append(
            _apply_invariants(
                {
                    "schema": "TemporalTopologySourceEntry.v1",
                    "source_key": source_key,
                    "source_path": str(source_path),
                    "source_status": status,
                    "source_hash": payload_hash,
                    "authority_boundary_violations": forbidden,
                    "advisory_flags": sorted(
                        {
                            "advisory_only",
                            "analytics_only",
                            "cartography_only",
                            "visualization_support_only",
                            "detection_only",
                            *(["authority_boundary_violation"] if forbidden else []),
                            *(["not_computable"] if final_status == NOT_COMPUTABLE else []),
                            *(["blocked"] if final_status == BLOCKED else []),
                        }
                    ),
                    "remaining_blockers": sorted(local_blockers),
                    "final_status": final_status,
                }
            )
        )

    return entries, payloads, source_hashes, sorted(blockers)


def _build_regions(
    payloads: dict[str, dict[str, Any] | None],
    source_entries_by_key: dict[str, dict[str, Any]],
    source_hashes: dict[str, str | None],
) -> list[dict[str, Any]]:
    regions: list[dict[str, Any]] = []
    fusion = payloads.get("cross_run_topology_fusion")
    if isinstance(fusion, dict):
        for node in _as_dict_list(fusion.get("fusion_nodes")):
            node_id = _as_str(node.get("node_id"), "unknown")
            source_key = "cross_run_topology_fusion"
            source_entry = source_entries_by_key[source_key]
            source_status = _as_str(source_entry.get("final_status"), NOT_COMPUTABLE)
            blocked = source_status == BLOCKED or _as_str(node.get("final_status")) == BLOCKED
            not_computable = source_status == NOT_COMPUTABLE or _as_str(
                node.get("final_status")
            ) == NOT_COMPUTABLE
            evidence_count = _as_int(node.get("evidence_count"), _as_int(node.get("recurrence_count"), 0))
            persistence_ratio = _as_float(node.get("persistence_ratio"), 0.0)
            continuity_ratio = _as_float(node.get("continuity_ratio"), 0.0)
            density_score = _ratio(float(evidence_count), 10.0)
            volatility_score = _as_float(node.get("volatility_score"), 1.0)
            drift_score = 0.75 if "drift_corridor" in _as_str_list(node.get("advisory_flags")) else 0.0
            region_kind, final_status, flags = _classify_region(
                blocked=blocked,
                not_computable=not_computable,
                persistence_ratio=persistence_ratio,
                continuity_ratio=continuity_ratio,
                volatility_score=volatility_score,
                drift_score=drift_score,
                evidence_count=evidence_count,
                advisory_flags=_as_str_list(node.get("advisory_flags")),
            )
            region_id = str(
                canonical_hash(
                    {
                        "source_key": source_key,
                        "node_id": node_id,
                        "region_kind": region_kind,
                    }
                )
            )
            source_hash = source_hashes.get(source_key)
            regions.append(
                _apply_invariants(
                    {
                        "schema": "AtlasRegion.v1",
                        "region_id": region_id,
                        "region_kind": region_kind,
                        "source_runs": _as_str_list(node.get("source_runs")),
                        "persistence_ratio": persistence_ratio,
                        "continuity_ratio": continuity_ratio,
                        "density_score": density_score,
                        "volatility_score": volatility_score,
                        "lineage_refs": _as_str_list(node.get("lineage_refs")),
                        "topology_refs": [node_id],
                        "source_hashes": [source_hash] if isinstance(source_hash, str) else [],
                        "advisory_flags": flags,
                        "final_status": final_status,
                        "stability_score": round(max(0.0, 1.0 - volatility_score), 6),
                        "drift_score": drift_score,
                        "evidence_count": evidence_count,
                    }
                )
            )

        for cluster in _as_dict_list(fusion.get("topology_persistence_clusters")):
            cluster_id = _as_str(cluster.get("cluster_id"), "unknown")
            source_key = "cross_run_topology_fusion"
            source_entry = source_entries_by_key[source_key]
            source_status = _as_str(source_entry.get("final_status"), NOT_COMPUTABLE)
            blocked = source_status == BLOCKED or _as_str(cluster.get("cluster_status")) == BLOCKED
            not_computable = source_status == NOT_COMPUTABLE or _as_str(
                cluster.get("cluster_status")
            ) == NOT_COMPUTABLE
            evidence_count = _as_int(cluster.get("evidence_count"), len(_as_str_list(cluster.get("node_refs"))))
            persistence_ratio = _as_float(cluster.get("persistence_ratio"), 0.0)
            continuity_ratio = _as_float(cluster.get("continuity_ratio"), 0.0)
            density_score = _ratio(
                float(len(_as_str_list(cluster.get("node_refs")))),
                float(max(1, _as_int(fusion.get("fusion_node_count"), 1))),
            )
            volatility_score = max(
                0.0,
                round(
                    1.0
                    - ((persistence_ratio + continuity_ratio) / 2.0),
                    6,
                ),
            )
            drift_score = 0.75 if "drift_corridor" in _as_str_list(cluster.get("advisory_flags")) else 0.0
            region_kind, final_status, flags = _classify_region(
                blocked=blocked,
                not_computable=not_computable,
                persistence_ratio=persistence_ratio,
                continuity_ratio=continuity_ratio,
                volatility_score=volatility_score,
                drift_score=drift_score,
                evidence_count=evidence_count,
                advisory_flags=_as_str_list(cluster.get("advisory_flags")),
            )
            region_id = str(
                canonical_hash(
                    {
                        "source_key": source_key,
                        "cluster_id": cluster_id,
                        "region_kind": region_kind,
                    }
                )
            )
            source_hash = source_hashes.get(source_key)
            regions.append(
                _apply_invariants(
                    {
                        "schema": "AtlasRegion.v1",
                        "region_id": region_id,
                        "region_kind": region_kind,
                        "source_runs": _as_str_list(cluster.get("source_runs")),
                        "persistence_ratio": persistence_ratio,
                        "continuity_ratio": continuity_ratio,
                        "density_score": density_score,
                        "volatility_score": volatility_score,
                        "lineage_refs": _as_str_list(cluster.get("lineage_refs")),
                        "topology_refs": _as_str_list(cluster.get("node_refs")),
                        "source_hashes": [source_hash] if isinstance(source_hash, str) else [],
                        "advisory_flags": flags,
                        "final_status": final_status,
                        "stability_score": round(max(0.0, 1.0 - volatility_score), 6),
                        "drift_score": drift_score,
                        "evidence_count": evidence_count,
                    }
                )
            )

    temporal_diff = payloads.get("temporal_state_diff")
    if isinstance(temporal_diff, dict):
        by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in _as_dict_list(temporal_diff.get("diff_entries")):
            by_surface[_as_str(entry.get("source_surface"), "unknown")].append(entry)
        total_entries = max(1, sum(len(items) for items in by_surface.values()))
        source_key = "temporal_state_diff"
        source_entry = source_entries_by_key[source_key]
        source_status = _as_str(source_entry.get("final_status"), NOT_COMPUTABLE)
        source_hash = source_hashes.get(source_key)
        for source_surface, entries in sorted(by_surface.items(), key=lambda item: item[0]):
            evidence_count = len(entries)
            shift_count = sum(
                1
                for entry in entries
                if _as_str(entry.get("change_type")) in {"TOPOLOGY_SHIFT", "LINEAGE_SHIFT", "MODIFIED"}
            )
            persistence_ratio = _ratio(float(max(evidence_count - shift_count, 0)), float(max(1, evidence_count)))
            continuity_ratio = _ratio(float(max(evidence_count - shift_count, 0)), float(max(1, evidence_count)))
            density_score = _ratio(float(evidence_count), float(total_entries))
            volatility_score = _ratio(float(shift_count), float(max(1, evidence_count)))
            drift_score = (
                0.75
                if any(_as_str(entry.get("change_type")) == "DRIFT_ACCELERATION" for entry in entries)
                else 0.0
            )
            blocked = source_status == BLOCKED
            not_computable = source_status == NOT_COMPUTABLE
            region_kind, final_status, flags = _classify_region(
                blocked=blocked,
                not_computable=not_computable,
                persistence_ratio=persistence_ratio,
                continuity_ratio=continuity_ratio,
                volatility_score=volatility_score,
                drift_score=drift_score,
                evidence_count=evidence_count,
                advisory_flags=_as_str_list(temporal_diff.get("diff_advisory_flags")),
            )
            regions.append(
                _apply_invariants(
                    {
                        "schema": "AtlasRegion.v1",
                        "region_id": str(
                            canonical_hash(
                                {
                                    "source_key": source_key,
                                    "source_surface": source_surface,
                                    "region_kind": region_kind,
                                }
                            )
                        ),
                        "region_kind": region_kind,
                        "source_runs": [],
                        "persistence_ratio": persistence_ratio,
                        "continuity_ratio": continuity_ratio,
                        "density_score": density_score,
                        "volatility_score": volatility_score,
                        "lineage_refs": [],
                        "topology_refs": sorted(_as_str(entry.get("entry_id")) for entry in entries),
                        "source_hashes": [source_hash] if isinstance(source_hash, str) else [],
                        "advisory_flags": flags,
                        "final_status": final_status,
                        "stability_score": round(max(0.0, 1.0 - volatility_score), 6),
                        "drift_score": drift_score,
                        "evidence_count": evidence_count,
                    }
                )
            )

    if not regions:
        regions.append(
            _apply_invariants(
                {
                    "schema": "AtlasRegion.v1",
                    "region_id": str(canonical_hash({"kind": "placeholder_region"})),
                    "region_kind": NOT_COMPUTABLE,
                    "source_runs": [],
                    "persistence_ratio": 0.0,
                    "continuity_ratio": 0.0,
                    "density_score": 0.0,
                    "volatility_score": 1.0,
                    "lineage_refs": [],
                    "topology_refs": [],
                    "source_hashes": [],
                    "advisory_flags": ["remaining_blocker: insufficient_cartography_evidence"],
                    "final_status": NOT_COMPUTABLE,
                    "stability_score": 0.0,
                    "drift_score": 0.0,
                    "evidence_count": 0,
                }
            )
        )

    return sorted(
        regions,
        key=lambda item: (
            _REGION_KIND_ORDER.get(_as_str(item.get("region_kind")), 999),
            -_as_float(item.get("persistence_ratio"), 0.0),
            _as_str(item.get("region_id")),
        ),
    )


def _build_corridors(
    payloads: dict[str, dict[str, Any] | None],
    source_entries_by_key: dict[str, dict[str, Any]],
    source_hashes: dict[str, str | None],
    regions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    corridors: list[dict[str, Any]] = []
    region_ids = [_as_str(region.get("region_id")) for region in regions]
    fusion = payloads.get("cross_run_topology_fusion")
    if isinstance(fusion, dict):
        source_key = "cross_run_topology_fusion"
        source_entry = source_entries_by_key[source_key]
        source_status = _as_str(source_entry.get("final_status"), NOT_COMPUTABLE)
        source_hash = source_hashes.get(source_key)
        for corridor in _as_dict_list(fusion.get("lineage_fusion_corridors")):
            corridor_id = _as_str(corridor.get("corridor_id"), "unknown")
            recurrence_count = _as_int(corridor.get("recurrence_count"), 0)
            continuity_ratio = _as_float(corridor.get("continuity_ratio"), 0.0)
            persistence_ratio = _ratio(float(recurrence_count), float(max(1, len(_as_str_list(corridor.get("source_runs"))))))
            drift_score = _as_float(corridor.get("drift_score"), 0.0)
            replay_stability = _stability_to_score(_as_str(corridor.get("replay_stability_status"), NOT_COMPUTABLE))
            transport_stability = _stability_to_score(
                _as_str(corridor.get("transport_stability_status"), NOT_COMPUTABLE)
            )
            volatility_score = max(0.0, round(1.0 - ((continuity_ratio + persistence_ratio) / 2.0), 6))
            advisory_flags = _as_str_list(corridor.get("advisory_flags"))
            hint = "lineage"
            if "replay_continuity" in advisory_flags:
                hint = "replay"
            elif "transport_continuity" in advisory_flags:
                hint = "transport"
            corridor_kind, final_status, flags = _classify_corridor(
                blocked=source_status == BLOCKED or _as_str(corridor.get("final_status")) == BLOCKED,
                not_computable=source_status == NOT_COMPUTABLE
                or _as_str(corridor.get("final_status")) == NOT_COMPUTABLE,
                corridor_hint=hint,
                persistence_ratio=persistence_ratio,
                continuity_ratio=continuity_ratio,
                volatility_score=volatility_score,
                drift_score=drift_score,
                replay_stability=replay_stability,
                transport_stability=transport_stability,
                evidence_count=max(0, recurrence_count),
                advisory_flags=advisory_flags,
            )
            corridors.append(
                _apply_invariants(
                    {
                        "schema": "AtlasCorridor.v1",
                        "corridor_id": str(
                            canonical_hash(
                                {
                                    "source_key": source_key,
                                    "corridor_ref": corridor_id,
                                    "corridor_kind": corridor_kind,
                                }
                            )
                        ),
                        "corridor_kind": corridor_kind,
                        "source_regions": _as_str_list(corridor.get("node_refs")) or region_ids[:1],
                        "continuity_ratio": continuity_ratio,
                        "persistence_ratio": persistence_ratio,
                        "recurrence_count": recurrence_count,
                        "drift_score": drift_score,
                        "replay_stability": replay_stability,
                        "transport_stability": transport_stability,
                        "source_hashes": sorted(
                            {
                                *(_as_str_list(corridor.get("source_hashes"))),
                                *( [source_hash] if isinstance(source_hash, str) else [] ),
                            }
                        ),
                        "advisory_flags": flags,
                        "final_status": final_status,
                        "evidence_count": recurrence_count,
                        "volatility_score": volatility_score,
                    }
                )
            )

    chronoscope = payloads.get("projection_chronoscope")
    if isinstance(chronoscope, dict):
        source_key = "projection_chronoscope"
        source_entry = source_entries_by_key[source_key]
        source_status = _as_str(source_entry.get("final_status"), NOT_COMPUTABLE)
        source_hash = source_hashes.get(source_key)
        timeline_points = _as_dict_list(chronoscope.get("timeline_points"))
        linked_count = sum(
            1 for point in timeline_points if _as_str(point.get("link_status")) == "LINKED"
        )
        continuity_ratio = _ratio(float(linked_count), float(max(1, len(timeline_points))))
        replay_stability = _stability_to_score(_as_str(chronoscope.get("final_status"), NOT_COMPUTABLE))
        transport_stability = replay_stability
        recurrence_count = len(timeline_points)
        persistence_ratio = _ratio(float(recurrence_count), float(max(1, recurrence_count)))
        drift_score = _ratio(
            float(_as_int((chronoscope.get("drift_timeline") or {}).get("drift_event_count"), 0)),
            10.0,
        )
        volatility_score = max(0.0, round(1.0 - continuity_ratio, 6))
        corridor_kind, final_status, flags = _classify_corridor(
            blocked=source_status == BLOCKED,
            not_computable=source_status == NOT_COMPUTABLE,
            corridor_hint="continuity",
            persistence_ratio=persistence_ratio,
            continuity_ratio=continuity_ratio,
            volatility_score=volatility_score,
            drift_score=drift_score,
            replay_stability=replay_stability,
            transport_stability=transport_stability,
            evidence_count=recurrence_count,
            advisory_flags=_as_str_list(chronoscope.get("chronoscope_advisory_flags")),
        )
        corridors.append(
            _apply_invariants(
                {
                    "schema": "AtlasCorridor.v1",
                    "corridor_id": str(
                        canonical_hash(
                            {
                                "source_key": source_key,
                                "corridor_ref": "chronoscope_timeline",
                                "corridor_kind": corridor_kind,
                            }
                        )
                    ),
                    "corridor_kind": corridor_kind,
                    "source_regions": region_ids[: max(1, min(2, len(region_ids)))],
                    "continuity_ratio": continuity_ratio,
                    "persistence_ratio": persistence_ratio,
                    "recurrence_count": recurrence_count,
                    "drift_score": drift_score,
                    "replay_stability": replay_stability,
                    "transport_stability": transport_stability,
                    "source_hashes": [source_hash] if isinstance(source_hash, str) else [],
                    "advisory_flags": flags,
                    "final_status": final_status,
                    "evidence_count": recurrence_count,
                    "volatility_score": volatility_score,
                }
            )
        )

    transport = payloads.get("read_only_transport")
    if isinstance(transport, dict):
        source_key = "read_only_transport"
        source_entry = source_entries_by_key[source_key]
        source_status = _as_str(source_entry.get("final_status"), NOT_COMPUTABLE)
        source_hash = source_hashes.get(source_key)
        frames = _as_dict_list(transport.get("frames"))
        present_count = sum(
            1 for frame in frames if _as_str(frame.get("blocker_status")) == "PRESENT"
        )
        continuity_ratio = _ratio(float(present_count), float(max(1, len(frames))))
        recurrence_count = len(frames)
        persistence_ratio = continuity_ratio
        drift_score = 0.0
        replay_stability = _stability_to_score(_as_str(transport.get("final_status"), NOT_COMPUTABLE))
        transport_stability = replay_stability
        volatility_score = max(0.0, round(1.0 - continuity_ratio, 6))
        corridor_kind, final_status, flags = _classify_corridor(
            blocked=source_status == BLOCKED,
            not_computable=source_status == NOT_COMPUTABLE,
            corridor_hint="transport",
            persistence_ratio=persistence_ratio,
            continuity_ratio=continuity_ratio,
            volatility_score=volatility_score,
            drift_score=drift_score,
            replay_stability=replay_stability,
            transport_stability=transport_stability,
            evidence_count=recurrence_count,
            advisory_flags=_as_str_list(transport.get("transport_advisory_flags")),
        )
        corridors.append(
            _apply_invariants(
                {
                    "schema": "AtlasCorridor.v1",
                    "corridor_id": str(
                        canonical_hash(
                            {
                                "source_key": source_key,
                                "corridor_ref": "transport_continuity",
                                "corridor_kind": corridor_kind,
                            }
                        )
                    ),
                    "corridor_kind": corridor_kind,
                    "source_regions": region_ids[: max(1, min(2, len(region_ids)))],
                    "continuity_ratio": continuity_ratio,
                    "persistence_ratio": persistence_ratio,
                    "recurrence_count": recurrence_count,
                    "drift_score": drift_score,
                    "replay_stability": replay_stability,
                    "transport_stability": transport_stability,
                    "source_hashes": [source_hash] if isinstance(source_hash, str) else [],
                    "advisory_flags": flags,
                    "final_status": final_status,
                    "evidence_count": recurrence_count,
                    "volatility_score": volatility_score,
                }
            )
        )

    if not corridors:
        corridors.append(
            _apply_invariants(
                {
                    "schema": "AtlasCorridor.v1",
                    "corridor_id": str(canonical_hash({"kind": "placeholder_corridor"})),
                    "corridor_kind": NOT_COMPUTABLE,
                    "source_regions": region_ids[:1],
                    "continuity_ratio": 0.0,
                    "persistence_ratio": 0.0,
                    "recurrence_count": 0,
                    "drift_score": 0.0,
                    "replay_stability": 0.0,
                    "transport_stability": 0.0,
                    "source_hashes": [],
                    "advisory_flags": ["remaining_blocker: insufficient_cartography_evidence"],
                    "final_status": NOT_COMPUTABLE,
                    "evidence_count": 0,
                    "volatility_score": 1.0,
                }
            )
        )

    return sorted(
        corridors,
        key=lambda item: (
            _CORRIDOR_KIND_ORDER.get(_as_str(item.get("corridor_kind")), 999),
            -_as_float(item.get("persistence_ratio"), 0.0),
            _as_str(item.get("corridor_id")),
        ),
    )


def _build_structural_tracks(
    payloads: dict[str, dict[str, Any] | None],
) -> list[dict[str, Any]]:
    tracks: list[dict[str, Any]] = []
    convergence = payloads.get("multi_run_convergence")
    if isinstance(convergence, dict):
        observations = sorted(
            _as_dict_list(convergence.get("run_observations")),
            key=lambda obs: (
                _as_str(obs.get("timestamp_or_sequence")),
                _as_str(obs.get("run_id")),
            ),
        )
        for index in range(max(0, len(observations) - 1)):
            before = observations[index]
            after = observations[index + 1]
            before_delta = (
                _as_int(before.get("topology_change_count"))
                + _as_int(before.get("lineage_shift_count"))
                + _as_int(before.get("queue_delta_count"))
                + _as_int(before.get("transport_delta_count"))
            )
            after_delta = (
                _as_int(after.get("topology_change_count"))
                + _as_int(after.get("lineage_shift_count"))
                + _as_int(after.get("queue_delta_count"))
                + _as_int(after.get("transport_delta_count"))
            )
            velocity = _ratio(abs(float(after_delta - before_delta)), 10.0)
            tracks.append(
                _apply_invariants(
                    {
                        "schema": "StructuralEvolutionTrack.v1",
                        "track_id": str(
                            canonical_hash(
                                {
                                    "before_run": _as_str(before.get("run_id")),
                                    "after_run": _as_str(after.get("run_id")),
                                }
                            )
                        ),
                        "from_ref": _as_str(before.get("run_id"), NOT_COMPUTABLE),
                        "to_ref": _as_str(after.get("run_id"), NOT_COMPUTABLE),
                        "evolution_velocity": velocity,
                        "continuity_delta": _ratio(float(before_delta), 10.0)
                        - _ratio(float(after_delta), 10.0),
                        "evidence_count": 2,
                        "final_status": ADVISORY_ONLY,
                        "advisory_flags": ["deterministic_ordering", "analytics_only"],
                    }
                )
            )

    chronoscope = payloads.get("projection_chronoscope")
    if isinstance(chronoscope, dict) and not tracks:
        points = sorted(
            _as_dict_list(chronoscope.get("timeline_points")),
            key=lambda point: (
                _as_int(point.get("ordinal"), 0),
                _as_str(point.get("timeline_point_id")),
            ),
        )
        for index in range(max(0, len(points) - 1)):
            before = points[index]
            after = points[index + 1]
            velocity = 1.0 if _as_str(before.get("link_status")) != _as_str(after.get("link_status")) else 0.0
            tracks.append(
                _apply_invariants(
                    {
                        "schema": "StructuralEvolutionTrack.v1",
                        "track_id": str(
                            canonical_hash(
                                {
                                    "before_point": _as_str(before.get("timeline_point_id")),
                                    "after_point": _as_str(after.get("timeline_point_id")),
                                }
                            )
                        ),
                        "from_ref": _as_str(before.get("timeline_point_id"), NOT_COMPUTABLE),
                        "to_ref": _as_str(after.get("timeline_point_id"), NOT_COMPUTABLE),
                        "evolution_velocity": velocity,
                        "continuity_delta": 0.0 if velocity == 0.0 else -1.0,
                        "evidence_count": 2,
                        "final_status": ADVISORY_ONLY,
                        "advisory_flags": ["deterministic_ordering", "analytics_only"],
                    }
                )
            )
    return tracks


def _build_density_field(
    regions: list[dict[str, Any]],
    corridors: list[dict[str, Any]],
) -> dict[str, Any]:
    region_density = _mean([_as_float(region.get("density_score")) for region in regions])
    continuity_density = _mean(
        [_as_float(region.get("continuity_ratio")) for region in regions]
        + [_as_float(corridor.get("continuity_ratio")) for corridor in corridors]
    )
    drift_density = _mean(
        [_as_float(region.get("drift_score")) for region in regions]
        + [_as_float(corridor.get("drift_score")) for corridor in corridors]
    )
    topology_density = _ratio(float(len(regions) + len(corridors)), 20.0)
    evidence_count = sum(_as_int(region.get("evidence_count")) for region in regions) + sum(
        _as_int(corridor.get("evidence_count")) for corridor in corridors
    )
    return _apply_invariants(
        {
            "schema": "TopologyDensityField.v1",
            "topology_density_score": topology_density,
            "region_density_score": region_density,
            "continuity_density_score": continuity_density,
            "drift_accumulation_score": drift_density,
            "evidence_count": evidence_count,
            "final_status": ADVISORY_ONLY if evidence_count > 0 else NOT_COMPUTABLE,
            "advisory_flags": ["analytics_only", "deterministic_ordering", "bounded_metrics"],
        }
    )


def _build_regime_boundaries(tracks: list[dict[str, Any]]) -> dict[str, Any]:
    boundaries: list[dict[str, Any]] = []
    for track in tracks:
        velocity = _as_float(track.get("evolution_velocity"))
        if velocity < 0.5:
            continue
        boundaries.append(
            _apply_invariants(
                {
                    "schema": "RegimeBoundary.v1",
                    "boundary_id": str(
                        canonical_hash(
                            {
                                "track_id": _as_str(track.get("track_id")),
                                "velocity": velocity,
                            }
                        )
                    ),
                    "track_ref": _as_str(track.get("track_id")),
                    "boundary_kind": "HIGH_VELOCITY_TRANSITION",
                    "velocity_score": velocity,
                    "final_status": ADVISORY_ONLY,
                    "advisory_flags": ["analytics_only", "bounded_metrics"],
                }
            )
        )
    return _apply_invariants(
        {
            "schema": "RegimeBoundarySummary.v1",
            "boundary_count": len(boundaries),
            "boundaries": boundaries,
            "regime_boundary_status": ADVISORY_ONLY if boundaries else NOT_COMPUTABLE,
            "evidence_count": len(boundaries),
            "advisory_flags": [
                "analytics_only",
                "deterministic_ordering",
                *(["remaining_blocker: insufficient_cartography_evidence"] if not boundaries else []),
            ],
            "final_status": ADVISORY_ONLY if boundaries else NOT_COMPUTABLE,
        }
    )


def summarize_temporal_topology_cartography(
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "temporal_topology_cartography_status": NOT_COMPUTABLE,
            "atlas_region_count": 0,
            "atlas_corridor_count": 0,
            "stable_region_count": 0,
            "volatile_region_count": 0,
            "drift_zone_count": 0,
            "replay_corridor_count": 0,
            "continuity_corridor_count": 0,
            "topology_density_score": 0.0,
            "cartography_advisory_flags": [],
        }
    return {
        "temporal_topology_cartography_status": _as_str(
            payload.get("temporal_topology_cartography_status"), NOT_COMPUTABLE
        ),
        "atlas_region_count": _as_int(payload.get("atlas_region_count"), 0),
        "atlas_corridor_count": _as_int(payload.get("atlas_corridor_count"), 0),
        "stable_region_count": _as_int(payload.get("stable_region_count"), 0),
        "volatile_region_count": _as_int(payload.get("volatile_region_count"), 0),
        "drift_zone_count": _as_int(payload.get("drift_zone_count"), 0),
        "replay_corridor_count": _as_int(payload.get("replay_corridor_count"), 0),
        "continuity_corridor_count": _as_int(payload.get("continuity_corridor_count"), 0),
        "topology_density_score": _as_float(payload.get("topology_density_score"), 0.0),
        "cartography_advisory_flags": _as_str_list(payload.get("cartography_advisory_flags")),
    }


def build_temporal_topology_cartography_packet(
    *,
    packet_id: str = "temporal_topology_cartography_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
        "cross_run_topology_fusion": paths.cross_run_topology_fusion_latest,
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
    source_entries, payloads, source_hashes, source_blockers = _source_entries(resolved_sources)
    source_entries_by_key = {
        _as_str(entry.get("source_key")): entry for entry in source_entries
    }

    atlas_regions = _build_regions(payloads, source_entries_by_key, source_hashes)
    atlas_corridors = _build_corridors(
        payloads, source_entries_by_key, source_hashes, atlas_regions
    )
    structural_tracks = _build_structural_tracks(payloads)
    density_field = _build_density_field(atlas_regions, atlas_corridors)
    regime_boundaries = _build_regime_boundaries(structural_tracks)

    drift_regions = [
        region for region in atlas_regions if _as_str(region.get("region_kind")) == "DRIFT_ZONE"
    ]
    drift_corridors = [
        corridor
        for corridor in atlas_corridors
        if _as_str(corridor.get("corridor_kind")) == "DRIFT_ZONE"
    ]
    replay_corridors = [
        corridor
        for corridor in atlas_corridors
        if _as_str(corridor.get("corridor_kind")) == "REPLAY_CORRIDOR"
    ]
    continuity_corridors = [
        corridor
        for corridor in atlas_corridors
        if _as_str(corridor.get("corridor_kind")) == "CONTINUITY_CORRIDOR"
    ]

    drift_zones = [
        _apply_invariants(
            {
                "schema": "DriftAccumulationZone.v1",
                "zone_id": str(
                    canonical_hash(
                        {
                            "region_ref": _as_str(region.get("region_id")),
                            "drift_score": _as_float(region.get("drift_score")),
                        }
                    )
                ),
                "region_refs": [_as_str(region.get("region_id"))],
                "corridor_refs": [],
                "drift_score": _as_float(region.get("drift_score")),
                "evidence_count": _as_int(region.get("evidence_count")),
                "final_status": _as_str(region.get("final_status"), ADVISORY_ONLY),
                "advisory_flags": _as_str_list(region.get("advisory_flags")),
            }
        )
        for region in drift_regions
    ] + [
        _apply_invariants(
            {
                "schema": "DriftAccumulationZone.v1",
                "zone_id": str(
                    canonical_hash(
                        {
                            "corridor_ref": _as_str(corridor.get("corridor_id")),
                            "drift_score": _as_float(corridor.get("drift_score")),
                        }
                    )
                ),
                "region_refs": [],
                "corridor_refs": [_as_str(corridor.get("corridor_id"))],
                "drift_score": _as_float(corridor.get("drift_score")),
                "evidence_count": _as_int(corridor.get("evidence_count")),
                "final_status": _as_str(corridor.get("final_status"), ADVISORY_ONLY),
                "advisory_flags": _as_str_list(corridor.get("advisory_flags")),
            }
        )
        for corridor in drift_corridors
    ]

    continuity_pathways = [
        _apply_invariants(
            {
                "schema": "ContinuityPathway.v1",
                "pathway_id": str(
                    canonical_hash(
                        {
                            "corridor_ref": _as_str(corridor.get("corridor_id")),
                            "kind": _as_str(corridor.get("corridor_kind")),
                        }
                    )
                ),
                "corridor_ref": _as_str(corridor.get("corridor_id")),
                "pathway_kind": _as_str(corridor.get("corridor_kind")),
                "continuity_ratio": _as_float(corridor.get("continuity_ratio")),
                "persistence_ratio": _as_float(corridor.get("persistence_ratio")),
                "stability_score": round(
                    (
                        _as_float(corridor.get("replay_stability"))
                        + _as_float(corridor.get("transport_stability"))
                    )
                    / 2.0,
                    6,
                ),
                "evidence_count": _as_int(corridor.get("evidence_count")),
                "final_status": _as_str(corridor.get("final_status"), ADVISORY_ONLY),
                "advisory_flags": _as_str_list(corridor.get("advisory_flags")),
            }
        )
        for corridor in sorted(
            replay_corridors + continuity_corridors,
            key=lambda item: (_as_str(item.get("corridor_kind")), _as_str(item.get("corridor_id"))),
        )
    ]

    topology_index = _apply_invariants(
        {
            "schema": "TemporalTopologyIndex.v1",
            "region_ids": [_as_str(region.get("region_id")) for region in atlas_regions],
            "corridor_ids": [
                _as_str(corridor.get("corridor_id")) for corridor in atlas_corridors
            ],
            "region_kind_counts": {
                key: value
                for key, value in sorted(
                    Counter(_as_str(region.get("region_kind")) for region in atlas_regions).items()
                )
            },
            "corridor_kind_counts": {
                key: value
                for key, value in sorted(
                    Counter(
                        _as_str(corridor.get("corridor_kind")) for corridor in atlas_corridors
                    ).items()
                )
            },
            "evidence_count": sum(_as_int(region.get("evidence_count")) for region in atlas_regions)
            + sum(_as_int(corridor.get("evidence_count")) for corridor in atlas_corridors),
            "final_status": ADVISORY_ONLY,
            "advisory_flags": ["deterministic_ordering", "analytics_only", "index_only"],
        }
    )

    stable_region_count = sum(
        1 for region in atlas_regions if _as_str(region.get("region_kind")) == "STABLE_REGION"
    )
    volatile_region_count = sum(
        1
        for region in atlas_regions
        if _as_str(region.get("region_kind")) == "VOLATILE_REGION"
    )
    drift_zone_count = len(drift_zones)
    replay_corridor_count = len(replay_corridors)
    continuity_corridor_count = len(continuity_corridors)
    topology_density_score = _as_float(density_field.get("topology_density_score"), 0.0)

    region_statuses = {_as_str(region.get("final_status")) for region in atlas_regions}
    corridor_statuses = {_as_str(corridor.get("final_status")) for corridor in atlas_corridors}
    source_not_computable = any(
        _as_str(entry.get("final_status")) == NOT_COMPUTABLE for entry in source_entries
    )
    source_blocked = any(_as_str(entry.get("final_status")) == BLOCKED for entry in source_entries)
    evidence_count = _as_int(topology_index.get("evidence_count"), 0)
    remaining_blockers = sorted(set(source_blockers))
    if evidence_count < 2:
        remaining_blockers.append("remaining_blocker: insufficient_cartography_evidence")
    remaining_blockers = sorted(set(remaining_blockers))

    if source_blocked or BLOCKED in region_statuses or BLOCKED in corridor_statuses:
        final_status = BLOCKED
    elif source_not_computable or evidence_count < 2:
        final_status = NOT_COMPUTABLE
    else:
        final_status = ADVISORY_ONLY

    regime_atlas_summary = _apply_invariants(
        {
            "schema": "RegimeAtlasSummary.v1",
            "atlas_region_count": len(atlas_regions),
            "atlas_corridor_count": len(atlas_corridors),
            "stable_region_count": stable_region_count,
            "volatile_region_count": volatile_region_count,
            "drift_zone_count": drift_zone_count,
            "replay_corridor_count": replay_corridor_count,
            "continuity_corridor_count": continuity_corridor_count,
            "regime_boundary_count": _as_int(regime_boundaries.get("boundary_count"), 0),
            "structural_evolution_track_count": len(structural_tracks),
            "topology_density_score": topology_density_score,
            "continuity_density_score": _as_float(
                density_field.get("continuity_density_score"), 0.0
            ),
            "drift_accumulation_score": _as_float(
                density_field.get("drift_accumulation_score"), 0.0
            ),
            "structural_evolution_velocity": _mean(
                [_as_float(track.get("evolution_velocity")) for track in structural_tracks]
            ),
            "blocker_count": len(remaining_blockers),
            "advisory_flags": sorted(
                {
                    "advisory_only",
                    "analytics_only",
                    "cartography_only",
                    "visualization_support_only",
                    "detection_only",
                    "deterministic_ordering",
                    "bounded_metrics",
                    *(["authority_boundary_violation"] if source_blocked else []),
                    *(["not_computable"] if final_status == NOT_COMPUTABLE else []),
                    *(["blocked"] if final_status == BLOCKED else []),
                }
            ),
            "recommended_operator_next_actions": (
                [
                    "Review authority boundary violations in source artifacts before relying on atlas outputs.",
                    "Regenerate missing/corrupt source artifacts and rerun temporal topology cartography.",
                    "Maintain advisory-only posture and require manual operator review.",
                ]
                if remaining_blockers
                else [
                    "Continue advisory-only temporal cartography monitoring.",
                    "Review stable and volatile regions for manual governance triage.",
                ]
            ),
            "final_status": final_status,
        }
    )

    packet_hash = str(
        canonical_hash(
            {
                "packet_id": packet_id,
                "source_entries": source_entries,
                "atlas_regions": atlas_regions,
                "atlas_corridors": atlas_corridors,
                "drift_zones": drift_zones,
                "continuity_pathways": continuity_pathways,
                "density_field": density_field,
                "structural_tracks": structural_tracks,
                "regime_boundaries": regime_boundaries,
                "topology_index": topology_index,
                "regime_atlas_summary": regime_atlas_summary,
                "remaining_blockers": remaining_blockers,
                "final_status": final_status,
            }
        )
    )

    return _apply_invariants(
        {
            "schema": "TemporalTopologyAtlas.v1",
            "patch_id": PATCH_ID,
            "packet_id": packet_id,
            "packet_hash": packet_hash,
            "source_entries": source_entries,
            "source_artifacts": {key: str(value) for key, value in sorted(resolved_sources.items())},
            "atlas_regions": atlas_regions,
            "atlas_corridors": atlas_corridors,
            "drift_accumulation_zones": sorted(
                drift_zones, key=lambda item: (_as_str(item.get("final_status")), _as_str(item.get("zone_id")))
            ),
            "continuity_pathways": continuity_pathways,
            "topology_density_field": density_field,
            "structural_evolution_tracks": structural_tracks,
            "regime_boundary_summary": regime_boundaries,
            "temporal_topology_index": topology_index,
            "regime_atlas_summary": regime_atlas_summary,
            "temporal_topology_cartography_status": final_status,
            "atlas_region_count": len(atlas_regions),
            "atlas_corridor_count": len(atlas_corridors),
            "stable_region_count": stable_region_count,
            "volatile_region_count": volatile_region_count,
            "drift_zone_count": drift_zone_count,
            "replay_corridor_count": replay_corridor_count,
            "continuity_corridor_count": continuity_corridor_count,
            "topology_density_score": topology_density_score,
            "cartography_advisory_flags": _as_str_list(
                regime_atlas_summary.get("advisory_flags")
            ),
            "recommended_operator_next_actions": _as_str_list(
                regime_atlas_summary.get("recommended_operator_next_actions")
            ),
            "final_status": final_status,
            "remaining_blockers": remaining_blockers,
        }
    )


def write_temporal_topology_cartography_packet(
    path: str | Path, packet: dict[str, Any]
) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_temporal_topology_cartography_markdown(packet: dict[str, Any]) -> str:
    lines = [
        f"# Temporal Topology Cartography — {_as_str(packet.get('packet_id'))}",
        "",
        f"**Patch:** `{_as_str(packet.get('patch_id'))}`",
        f"**Final Status:** `{_as_str(packet.get('final_status'), NOT_COMPUTABLE)}`",
        f"**Atlas Region Count:** `{_as_int(packet.get('atlas_region_count'))}`",
        f"**Atlas Corridor Count:** `{_as_int(packet.get('atlas_corridor_count'))}`",
        f"**Stable Region Count:** `{_as_int(packet.get('stable_region_count'))}`",
        f"**Volatile Region Count:** `{_as_int(packet.get('volatile_region_count'))}`",
        f"**Drift Zone Count:** `{_as_int(packet.get('drift_zone_count'))}`",
        f"**Replay Corridor Count:** `{_as_int(packet.get('replay_corridor_count'))}`",
        f"**Continuity Corridor Count:** `{_as_int(packet.get('continuity_corridor_count'))}`",
        (
            f"**Regime Boundaries:** "
            f"`{_as_int((packet.get('regime_boundary_summary') or {}).get('boundary_count'))}`"
        ),
        (
            f"**Structural Evolution Summary:** "
            f"`tracks={len(_as_dict_list(packet.get('structural_evolution_tracks')))}, "
            f"velocity={_as_float((packet.get('regime_atlas_summary') or {}).get('structural_evolution_velocity'))}`"
        ),
        "",
        "## Blockers",
    ]
    blockers = _as_str_list(packet.get("remaining_blockers"))
    if blockers:
        lines.extend(f"- `{blocker}`" for blocker in blockers)
    else:
        lines.append("- None")

    lines.extend(["", "## Operator Next Actions"])
    next_actions = _as_str_list(packet.get("recommended_operator_next_actions"))
    if next_actions:
        lines.extend(f"- {action}" for action in next_actions)
    else:
        lines.append("- Continue advisory-only cartography monitoring.")

    lines.append("")
    return "\n".join(lines)
