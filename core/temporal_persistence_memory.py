"""Deterministic temporal persistence and memory-field analytics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P26-TEMPORAL-PERSISTENCE-AND-MEMORY-FIELD-ANALYTICS-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"
ADVISORY_ONLY = "ADVISORY_ONLY"

_HALF_LIFE_BUCKETS = ("SHORT", "MEDIUM", "LONG", "PERSISTENT", NOT_COMPUTABLE, BLOCKED)
_MEMORY_ZONE_KINDS = {
    "LOW_MEMORY",
    "MODERATE_MEMORY",
    "HIGH_MEMORY",
    "PERSISTENT_MEMORY",
    "RAPID_DECAY_ZONE",
    "HYSTERESIS_ZONE",
    "REPLAY_MEMORY_ZONE",
    "TOPOLOGY_MEMORY_ZONE",
    "DRIFT_MEMORY_ZONE",
    NOT_COMPUTABLE,
    BLOCKED,
}

_INVARIANTS: dict[str, Any] = {
    "advisory_only": True,
    "analytics_only": True,
    "persistence_only": True,
    "memory_field_only": True,
    "detection_only": True,
    "visualization_support_only": True,
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

_FORBIDDEN_TRUE_FLAGS = frozenset(
    {
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
)

_RETENTION_COMPONENT_ORDER = (
    "topology_retention",
    "lineage_retention",
    "replay_retention",
    "transition_recurrence",
    "stress_persistence",
    "drift_persistence",
    "blocker_persistence",
    "volatility_persistence",
)


def _apply_invariants(payload: dict[str, Any]) -> dict[str, Any]:
    return {**payload, **_INVARIANTS}


def _as_str(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


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


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted(str(item) for item in value if str(item))


def _bound(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return _bound(sum(values) / float(len(values)))


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return _bound(numerator / denominator)


def _status_score(value: str) -> float:
    normalized = _as_str(value).upper()
    if normalized in {"PASS", ADVISORY_ONLY, "PRESENT", "STABLE", "HELD", "NO_CHANGE"}:
        return 1.0
    if normalized in {
        "VOLATILE",
        "WATCH",
        "COLLAPSE_WATCH",
        "DRIFT_ACCELERATING",
        "SHIFT_DETECTED",
    }:
        return 0.5
    if normalized in {BLOCKED, NOT_COMPUTABLE, "FAILED"}:
        return 0.0
    return 0.25


def _load_artifact(path: str | Path | None) -> tuple[dict[str, Any] | None, str]:
    if path is None:
        return None, "MISSING"
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (json.JSONDecodeError, OSError):
        return None, "CORRUPT"
    if not isinstance(payload, dict):
        return None, "CORRUPT"
    return payload, "PRESENT"


def _safe_hash(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    try:
        return str(canonical_hash(payload))
    except Exception:
        return None


def _scan_forbidden_true_flags(payload: Any, prefix: str = "") -> list[str]:
    violations: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_str = str(key)
            path = f"{prefix}.{key_str}" if prefix else key_str
            if key_str in _FORBIDDEN_TRUE_FLAGS and value is True:
                violations.append(path)
            violations.extend(_scan_forbidden_true_flags(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            violations.extend(_scan_forbidden_true_flags(value, path))
    return sorted(set(violations))


def _source_entries(
    source_artifact_paths: dict[str, str | Path]
) -> tuple[
    list[dict[str, Any]],
    dict[str, dict[str, Any] | None],
    dict[str, str],
    list[str],
]:
    entries: list[dict[str, Any]] = []
    payloads: dict[str, dict[str, Any] | None] = {}
    source_hashes: dict[str, str] = {}
    blockers: list[str] = []

    for source_key, source_path in sorted(source_artifact_paths.items()):
        payload, source_status = _load_artifact(source_path)
        payloads[source_key] = payload
        source_hash = _safe_hash(payload)
        violations = _scan_forbidden_true_flags(payload) if payload is not None else []

        final_status = "PRESENT"
        advisory_flags = [
            "advisory_only",
            "analytics_only",
            "persistence_only",
            "memory_field_only",
        ]
        if source_status != "PRESENT":
            final_status = NOT_COMPUTABLE
            advisory_flags.append("not_computable")
            blockers.append(f"{source_status.lower()}_artifact:{source_key}:{source_path}")
        elif violations:
            final_status = BLOCKED
            advisory_flags.extend(["blocked", "authority_boundary_violation"])
            blockers.extend(
                f"authority_boundary_violation:{source_key}:{path}" for path in violations
            )
        elif source_hash is None:
            final_status = NOT_COMPUTABLE
            advisory_flags.append("not_computable")
            blockers.append(f"missing_source_hash:{source_key}:{source_path}")
        else:
            source_hashes[source_key] = source_hash

        entries.append(
            _apply_invariants(
                {
                    "schema": "TemporalPersistenceMemorySourceEntry.v1",
                    "source_key": source_key,
                    "source_path": str(source_path),
                    "source_status": source_status,
                    "source_hash": source_hash,
                    "source_schema": _as_str(_as_dict(payload).get("schema"), NOT_COMPUTABLE),
                    "authority_boundary_violations": violations,
                    "advisory_flags": sorted(
                        set(
                            advisory_flags
                            + (["authority_boundary_violation"] if violations else [])
                            + (["blocked"] if final_status == BLOCKED else [])
                        )
                    ),
                    "final_status": final_status,
                }
            )
        )

    return entries, payloads, source_hashes, sorted(set(blockers))


def _compute_retention_components(payloads: dict[str, dict[str, Any] | None]) -> dict[str, float]:
    pressure = _as_dict(payloads.get("temporal_stability_pressure"))
    transition = _as_dict(payloads.get("temporal_regime_transition"))
    cartography = _as_dict(payloads.get("temporal_topology_cartography"))
    fusion = _as_dict(payloads.get("cross_run_topology_fusion"))
    convergence = _as_dict(payloads.get("multi_run_convergence"))
    diff = _as_dict(payloads.get("temporal_state_diff"))
    render = _as_dict(payloads.get("aal_viz_graph_render_packet"))
    chronoscope = _as_dict(payloads.get("projection_chronoscope"))
    transport = _as_dict(payloads.get("read_only_transport"))
    queue = _as_dict(payloads.get("operator_action_queue"))

    stable_regions = _as_float(cartography.get("stable_region_count"), 0.0)
    atlas_regions = _as_float(cartography.get("atlas_region_count"), 0.0)
    replay_corridors = _as_float(cartography.get("replay_corridor_count"), 0.0)
    atlas_corridors = _as_float(cartography.get("atlas_corridor_count"), 0.0)
    volatile_regions = _as_float(cartography.get("volatile_region_count"), 0.0)

    components = {
        "topology_retention": _mean(
            [
                _ratio(stable_regions, atlas_regions),
                _as_float(convergence.get("topology_persistence_ratio"), 0.0),
                _as_float(fusion.get("topology_stability_score"), 0.0),
            ]
        ),
        "lineage_retention": _mean(
            [
                _as_float(convergence.get("lineage_persistence_ratio"), 0.0),
                _ratio(_as_float(fusion.get("lineage_corridor_count"), 0.0), 6.0),
                _bound(1.0 - _ratio(_as_float(diff.get("lineage_shift_count"), 0.0), 10.0)),
            ]
        ),
        "replay_retention": _mean(
            [
                _ratio(replay_corridors, atlas_corridors),
                _status_score(_as_str(convergence.get("replay_stability_status"))),
                _status_score(_as_str(fusion.get("replay_continuity_status"))),
                _bound(1.0 - _ratio(_as_float(diff.get("queue_delta_count"), 0.0), 12.0)),
            ]
        ),
        "transition_recurrence": _mean(
            [
                _ratio(_as_float(transition.get("phase_shift_count"), 0.0), 8.0),
                _ratio(_as_float(transition.get("phase_boundary_count"), 0.0), 8.0),
                _as_float(
                    _as_dict(transition.get("transition_density_metrics")).get(
                        "transition_density_score"
                    ),
                    0.0,
                ),
            ]
        ),
        "stress_persistence": _mean(
            [
                _as_float(pressure.get("aggregate_stress_score"), 0.0),
                _bound(1.0 - _as_float(pressure.get("resilience_score"), 0.0)),
                _as_float(pressure.get("transition_pressure_gradient_score"), 0.0),
            ]
        ),
        "drift_persistence": _mean(
            [
                _as_float(convergence.get("drift_persistence_ratio"), 0.0),
                _status_score(_as_str(diff.get("drift_acceleration_status"))),
                _ratio(_as_float(pressure.get("drift_load_zone_count"), 0.0), 6.0),
            ]
        ),
        "blocker_persistence": _mean(
            [
                _status_score(_as_str(convergence.get("blocker_persistence_status"))),
                _ratio(_as_float(transport.get("transport_blocker_count"), 0.0), 12.0),
                _ratio(_as_float(queue.get("escalation_count"), 0.0), 10.0),
            ]
        ),
        "volatility_persistence": _mean(
            [
                _ratio(volatile_regions, atlas_regions),
                _ratio(_as_float(render.get("render_blocker_count"), 0.0), 10.0),
                _ratio(
                    _as_float(chronoscope.get("drift_timeline", {}).get("drift_event_count", 0), 0.0),
                    10.0,
                ),
            ]
        ),
    }
    return {key: _bound(value) for key, value in components.items()}


def _dominant_component(components: dict[str, float]) -> str:
    return sorted(
        components,
        key=lambda key: (-components[key], _RETENTION_COMPONENT_ORDER.index(key), key),
    )[0]


def _persistence_half_life_bucket(
    *,
    aggregate_memory_score: float,
    final_status: str,
) -> str:
    if final_status == BLOCKED:
        return BLOCKED
    if final_status == NOT_COMPUTABLE:
        return NOT_COMPUTABLE
    if aggregate_memory_score >= 0.85:
        return "PERSISTENT"
    if aggregate_memory_score >= 0.65:
        return "LONG"
    if aggregate_memory_score >= 0.4:
        return "MEDIUM"
    return "SHORT"


def _classify_memory_zone(
    *,
    aggregate_memory_score: float,
    decay_score: float,
    hysteresis_score: float,
    dominant_memory_component: str,
    final_status: str,
) -> str:
    if final_status == BLOCKED:
        return BLOCKED
    if final_status == NOT_COMPUTABLE:
        return NOT_COMPUTABLE
    if decay_score >= 0.75:
        return "RAPID_DECAY_ZONE"
    if hysteresis_score >= 0.5:
        return "HYSTERESIS_ZONE"
    if dominant_memory_component == "replay_retention":
        return "REPLAY_MEMORY_ZONE"
    if dominant_memory_component == "topology_retention":
        return "TOPOLOGY_MEMORY_ZONE"
    if dominant_memory_component == "drift_persistence":
        return "DRIFT_MEMORY_ZONE"
    if aggregate_memory_score >= 0.75:
        return "PERSISTENT_MEMORY"
    if aggregate_memory_score >= 0.5:
        return "HIGH_MEMORY"
    if aggregate_memory_score >= 0.25:
        return "MODERATE_MEMORY"
    return "LOW_MEMORY"


def _build_memory_zones(
    *,
    packet_id: str,
    source_hashes: dict[str, str],
    retention_components: dict[str, float],
    aggregate_memory_score: float,
    hysteresis_score: float,
    final_status: str,
) -> list[dict[str, Any]]:
    zones: list[dict[str, Any]] = []
    for component in _RETENTION_COMPONENT_ORDER:
        retention_score = _as_float(retention_components.get(component), 0.0)
        component_hysteresis = _bound(_mean([retention_score, hysteresis_score]))
        component_decay = _bound(1.0 - retention_score)
        zone_kind = _classify_memory_zone(
            aggregate_memory_score=aggregate_memory_score,
            decay_score=component_decay,
            hysteresis_score=component_hysteresis,
            dominant_memory_component=component,
            final_status=final_status,
        )
        zone_id = str(
            canonical_hash(
                {
                    "packet_id": packet_id,
                    "component": component,
                    "retention_score": retention_score,
                    "hysteresis_score": component_hysteresis,
                    "zone_kind": zone_kind,
                }
            )
        )
        zones.append(
            _apply_invariants(
                {
                    "schema": "MemoryZone.v1",
                    "zone_id": zone_id,
                    "zone_kind": zone_kind,
                    "source_regions": sorted(
                        [
                            "topology_atlas"
                            if component in {"topology_retention", "volatility_persistence"}
                            else "cross_surface"
                        ]
                    ),
                    "source_pressure_zones": sorted(
                        [
                            "stress_tensor"
                            if component in {"stress_persistence", "drift_persistence"}
                            else "memory_field"
                        ]
                    ),
                    "retention_score": retention_score,
                    "decay_score": component_decay,
                    "hysteresis_score": component_hysteresis,
                    "dominant_memory_component": component,
                    "source_hashes": {
                        key: value
                        for key, value in sorted(source_hashes.items())
                        if key
                        in {
                            "temporal_stability_pressure",
                            "temporal_topology_cartography",
                            "cross_run_topology_fusion",
                            "multi_run_convergence",
                            "temporal_state_diff",
                        }
                    },
                    "advisory_flags": sorted(
                        {
                            "advisory_only",
                            "analytics_only",
                            "persistence_only",
                            "memory_field_only",
                            "detection_only",
                            "deterministic_ordering",
                            *(["blocked"] if zone_kind == BLOCKED else []),
                            *(["not_computable"] if zone_kind == NOT_COMPUTABLE else []),
                        }
                    ),
                    "final_status": final_status,
                }
            )
        )

    return sorted(
        zones,
        key=lambda item: (
            _as_str(item.get("zone_kind")),
            -_as_float(item.get("retention_score"), 0.0),
            -_as_float(item.get("hysteresis_score"), 0.0),
            _as_str(item.get("zone_id")),
        ),
    )


def build_temporal_persistence_memory_packet(
    *,
    packet_id: str = "temporal_persistence_memory_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
        "temporal_stability_pressure": paths.temporal_stability_pressure_latest,
        "temporal_regime_transition": paths.temporal_regime_transition_latest,
        "temporal_topology_cartography": paths.temporal_topology_cartography_latest,
        "cross_run_topology_fusion": paths.cross_run_topology_fusion_latest,
        "multi_run_convergence": paths.multi_run_convergence_latest,
        "temporal_state_diff": paths.temporal_state_diff_latest,
        "aal_viz_graph_render_packet": paths.aal_viz_graph_render_packet_latest,
        "projection_chronoscope": paths.projection_chronoscope_latest,
        "read_only_transport": paths.read_only_transport_latest,
        "operator_action_queue": paths.operator_action_queue_latest,
    }

    if source_artifact_paths is None:
        resolved_sources = defaults
    else:
        missing_root = Path("__missing__")
        provided_sources = dict(source_artifact_paths)
        resolved_sources = {
            key: provided_sources.get(key, missing_root / f"{key}.latest.json")
            for key in defaults
        }
        for key, value in provided_sources.items():
            resolved_sources[key] = value

    source_entries, payloads, source_hashes, source_blockers = _source_entries(resolved_sources)
    source_blocked = any(_as_str(entry.get("final_status")) == BLOCKED for entry in source_entries)
    source_not_computable = any(
        _as_str(entry.get("final_status")) == NOT_COMPUTABLE for entry in source_entries
    )

    present_count = sum(
        1 for entry in source_entries if _as_str(entry.get("source_status")) == "PRESENT"
    )
    retention_components = _compute_retention_components(payloads)

    aggregate_memory_score = _mean(
        [_as_float(retention_components.get(name), 0.0) for name in _RETENTION_COMPONENT_ORDER]
    )
    decay_score = _bound(1.0 - aggregate_memory_score)
    hysteresis_score = _mean(
        [
            _as_float(retention_components.get("stress_persistence"), 0.0),
            _as_float(retention_components.get("transition_recurrence"), 0.0),
            _as_float(retention_components.get("blocker_persistence"), 0.0),
        ]
    )
    dominant_memory_component = _dominant_component(retention_components)

    remaining_blockers = sorted(set(source_blockers))
    evidence_count = sum(1 for value in retention_components.values() if value > 0.0)
    if present_count < 3 or evidence_count < 3:
        remaining_blockers.append("remaining_blocker: insufficient_memory_evidence")
    remaining_blockers = sorted(set(remaining_blockers))

    if source_blocked:
        final_status = BLOCKED
    elif source_not_computable or present_count < 3 or evidence_count < 3:
        final_status = NOT_COMPUTABLE
    else:
        final_status = ADVISORY_ONLY

    persistence_half_life_bucket = _persistence_half_life_bucket(
        aggregate_memory_score=aggregate_memory_score,
        final_status=final_status,
    )

    zones = _build_memory_zones(
        packet_id=packet_id,
        source_hashes=source_hashes,
        retention_components=retention_components,
        aggregate_memory_score=aggregate_memory_score,
        hysteresis_score=hysteresis_score,
        final_status=final_status,
    )

    packet_hash = str(
        canonical_hash(
            {
                "packet_id": packet_id,
                "source_entries": source_entries,
                "retention_components": retention_components,
                "aggregate_memory_score": aggregate_memory_score,
                "decay_score": decay_score,
                "hysteresis_score": hysteresis_score,
                "dominant_memory_component": dominant_memory_component,
                "persistence_half_life_bucket": persistence_half_life_bucket,
                "zones": zones,
                "final_status": final_status,
                "remaining_blockers": remaining_blockers,
            }
        )
    )

    memory_field_id = str(
        canonical_hash(
            {
                "packet_id": packet_id,
                "packet_hash": packet_hash,
                "source_hashes": source_hashes,
            }
        )
    )

    zone_kind_counts = {
        kind: sum(1 for zone in zones if _as_str(zone.get("zone_kind")) == kind)
        for kind in sorted(_MEMORY_ZONE_KINDS)
    }

    memory_field = _apply_invariants(
        {
            "schema": "MemoryField.v1",
            "memory_field_id": memory_field_id,
            "source_surfaces": sorted(str(key) for key in resolved_sources),
            "retention_components": {
                key: _as_float(retention_components.get(key), 0.0)
                for key in _RETENTION_COMPONENT_ORDER
            },
            "aggregate_memory_score": aggregate_memory_score,
            "decay_score": decay_score,
            "hysteresis_score": hysteresis_score,
            "persistence_half_life_bucket": persistence_half_life_bucket,
            "evidence_count": evidence_count,
            "source_hashes": {key: value for key, value in sorted(source_hashes.items())},
            "advisory_flags": sorted(
                {
                    "advisory_only",
                    "analytics_only",
                    "persistence_only",
                    "memory_field_only",
                    "detection_only",
                    "bounded_metrics",
                    "deterministic_ordering",
                    *(["authority_boundary_violation"] if final_status == BLOCKED else []),
                    *(["not_computable"] if final_status == NOT_COMPUTABLE else []),
                }
            ),
            "final_status": final_status,
        }
    )

    topology_memory_retention = _apply_invariants(
        {
            "schema": "TopologyMemoryRetention.v1",
            "topology_retention": _as_float(retention_components["topology_retention"]),
            "lineage_retention": _as_float(retention_components["lineage_retention"]),
            "volatility_persistence": _as_float(retention_components["volatility_persistence"]),
            "final_status": final_status,
        }
    )
    replay_memory_continuity = _apply_invariants(
        {
            "schema": "ReplayMemoryContinuity.v1",
            "replay_retention": _as_float(retention_components["replay_retention"]),
            "transition_recurrence": _as_float(retention_components["transition_recurrence"]),
            "continuity_memory_score": _mean(
                [
                    _as_float(retention_components["replay_retention"]),
                    _as_float(retention_components["lineage_retention"]),
                ]
            ),
            "final_status": final_status,
        }
    )
    stress_persistence_decay = _apply_invariants(
        {
            "schema": "StressPersistenceDecay.v1",
            "stress_persistence": _as_float(retention_components["stress_persistence"]),
            "decay_score": decay_score,
            "drift_persistence": _as_float(retention_components["drift_persistence"]),
            "final_status": final_status,
        }
    )
    transition_recurrence_memory = _apply_invariants(
        {
            "schema": "TransitionRecurrenceMemory.v1",
            "transition_recurrence": _as_float(retention_components["transition_recurrence"]),
            "replay_retention": _as_float(retention_components["replay_retention"]),
            "final_status": final_status,
        }
    )
    structural_hysteresis_summary = _apply_invariants(
        {
            "schema": "StructuralHysteresisSummary.v1",
            "hysteresis_score": hysteresis_score,
            "post_transition_pressure": _as_float(retention_components["stress_persistence"]),
            "recurrence_memory": _as_float(retention_components["transition_recurrence"]),
            "final_status": final_status,
        }
    )
    continuity_memory_field = _apply_invariants(
        {
            "schema": "ContinuityMemoryField.v1",
            "dominant_memory_component": dominant_memory_component,
            "aggregate_memory_score": aggregate_memory_score,
            "decay_score": decay_score,
            "final_status": final_status,
        }
    )
    half_life_summary = _apply_invariants(
        {
            "schema": "PersistenceHalfLifeSummary.v1",
            "persistence_half_life_bucket": persistence_half_life_bucket,
            "aggregate_memory_score": aggregate_memory_score,
            "decay_score": decay_score,
            "final_status": final_status,
        }
    )
    memory_index = _apply_invariants(
        {
            "schema": "MemoryFieldIndex.v1",
            "memory_field_id": memory_field_id,
            "zone_ids": [_as_str(zone.get("zone_id")) for zone in zones],
            "zone_kind_counts": zone_kind_counts,
            "dominant_memory_component": dominant_memory_component,
            "final_status": final_status,
        }
    )

    persistent_memory_count = zone_kind_counts.get("PERSISTENT_MEMORY", 0)
    rapid_decay_zone_count = zone_kind_counts.get("RAPID_DECAY_ZONE", 0)
    hysteresis_zone_count = zone_kind_counts.get("HYSTERESIS_ZONE", 0)
    replay_memory_zone_count = zone_kind_counts.get("REPLAY_MEMORY_ZONE", 0)
    topology_memory_zone_count = zone_kind_counts.get("TOPOLOGY_MEMORY_ZONE", 0)
    drift_memory_zone_count = zone_kind_counts.get("DRIFT_MEMORY_ZONE", 0)

    memory_advisory_flags = sorted(
        {
            "advisory_only",
            "analytics_only",
            "persistence_only",
            "memory_field_only",
            "detection_only",
            "visualization_support_only",
            "bounded_metrics",
            "deterministic_ordering",
            *(["authority_boundary_violation"] if final_status == BLOCKED else []),
            *(["not_computable"] if final_status == NOT_COMPUTABLE else []),
        }
    )

    operator_next_actions = (
        [
            "Review authority boundary violations before using persistence-memory analytics.",
            "Regenerate missing/corrupt persistence source artifacts and rerun temporal persistence memory.",
            "Keep persistence-memory output advisory-only with manual review.",
        ]
        if remaining_blockers
        else [
            "Continue advisory-only monitoring of persistence-memory fields.",
            "Review persistent, hysteresis, and rapid-decay zones for manual governance triage.",
        ]
    )

    return _apply_invariants(
        {
            "schema": "TemporalPersistenceMemoryPacket.v1",
            "patch_id": PATCH_ID,
            "packet_id": packet_id,
            "packet_hash": packet_hash,
            "source_entries": source_entries,
            "source_artifacts": {
                key: str(value) for key, value in sorted(resolved_sources.items())
            },
            "memory_field": memory_field,
            "topology_memory_retention": topology_memory_retention,
            "replay_memory_continuity": replay_memory_continuity,
            "stress_persistence_decay": stress_persistence_decay,
            "transition_recurrence_memory": transition_recurrence_memory,
            "structural_hysteresis_summary": structural_hysteresis_summary,
            "continuity_memory_field": continuity_memory_field,
            "persistence_half_life_summary": half_life_summary,
            "memory_zones": zones,
            "memory_field_index": memory_index,
            "temporal_persistence_memory_status": final_status,
            "aggregate_memory_score": aggregate_memory_score,
            "decay_score": decay_score,
            "hysteresis_score": hysteresis_score,
            "dominant_memory_component": dominant_memory_component,
            "persistence_half_life_bucket": persistence_half_life_bucket,
            "memory_zone_count": len(zones),
            "persistent_memory_count": persistent_memory_count,
            "rapid_decay_zone_count": rapid_decay_zone_count,
            "hysteresis_zone_count": hysteresis_zone_count,
            "replay_memory_zone_count": replay_memory_zone_count,
            "topology_memory_zone_count": topology_memory_zone_count,
            "drift_memory_zone_count": drift_memory_zone_count,
            "memory_advisory_flags": memory_advisory_flags,
            "recommended_operator_next_actions": operator_next_actions,
            "remaining_blockers": remaining_blockers,
            "final_status": final_status,
        }
    )


def write_temporal_persistence_memory_packet(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_temporal_persistence_memory_markdown(packet: dict[str, Any]) -> str:
    blockers = [str(item) for item in packet.get("remaining_blockers", [])]
    actions = [str(item) for item in packet.get("recommended_operator_next_actions", [])]
    lines = [
        f"# Temporal Persistence Memory — {packet.get('packet_id', '')}",
        "",
        f"**Patch:** `{packet.get('patch_id', '')}`",
        f"**Final Status:** `{packet.get('final_status', NOT_COMPUTABLE)}`",
        f"**Aggregate Memory Score:** `{packet.get('aggregate_memory_score', 0.0)}`",
        f"**Decay Score:** `{packet.get('decay_score', 0.0)}`",
        f"**Hysteresis Score:** `{packet.get('hysteresis_score', 0.0)}`",
        f"**Dominant Memory Component:** `{packet.get('dominant_memory_component', NOT_COMPUTABLE)}`",
        f"**Persistence Half-Life Bucket:** `{packet.get('persistence_half_life_bucket', NOT_COMPUTABLE)}`",
        f"**Memory Zone Count:** `{packet.get('memory_zone_count', 0)}`",
        f"**Persistent Memory Count:** `{packet.get('persistent_memory_count', 0)}`",
        f"**Rapid Decay Zone Count:** `{packet.get('rapid_decay_zone_count', 0)}`",
        f"**Hysteresis Zone Count:** `{packet.get('hysteresis_zone_count', 0)}`",
        f"**Replay Memory Zone Count:** `{packet.get('replay_memory_zone_count', 0)}`",
        f"**Topology Memory Zone Count:** `{packet.get('topology_memory_zone_count', 0)}`",
        f"**Drift Memory Zone Count:** `{packet.get('drift_memory_zone_count', 0)}`",
        "",
        "## Blockers",
    ]
    if blockers:
        lines.extend(f"- {item}" for item in blockers)
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Operator Next Actions")
    if actions:
        lines.extend(f"- {item}" for item in actions)
    else:
        lines.append("- Continue advisory-only persistence-memory monitoring.")
    lines.append("")
    lines.extend(
        [
            "## Invariants",
            "- advisory_only: `true`",
            "- analytics_only: `true`",
            "- persistence_only: `true`",
            "- memory_field_only: `true`",
            "- detection_only: `true`",
            "- visualization_support_only: `true`",
            "- execution_authority: `false`",
            "- authority_granted: `false`",
            "- mutation_allowed: `false`",
            "- promotion_allowed: `false`",
            "- auto_execute: `false`",
            "- auto_approve: `false`",
            "- command_channel: `false`",
            "- bidirectional_control: `false`",
            "- inference_authority: `false`",
        ]
    )
    return "\n".join(lines) + "\n"


def summarize_temporal_persistence_memory(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "temporal_persistence_memory_status": NOT_COMPUTABLE,
            "aggregate_memory_score": 0.0,
            "decay_score": 0.0,
            "hysteresis_score": 0.0,
            "dominant_memory_component": NOT_COMPUTABLE,
            "persistence_half_life_bucket": NOT_COMPUTABLE,
            "memory_zone_count": 0,
            "persistent_memory_count": 0,
            "rapid_decay_zone_count": 0,
            "hysteresis_zone_count": 0,
            "replay_memory_zone_count": 0,
            "topology_memory_zone_count": 0,
            "drift_memory_zone_count": 0,
            "memory_advisory_flags": [],
        }

    bucket = _as_str(payload.get("persistence_half_life_bucket"), NOT_COMPUTABLE)
    if bucket not in _HALF_LIFE_BUCKETS:
        bucket = NOT_COMPUTABLE

    return {
        "temporal_persistence_memory_status": _as_str(
            payload.get("temporal_persistence_memory_status"),
            _as_str(payload.get("final_status"), NOT_COMPUTABLE),
        ),
        "aggregate_memory_score": _as_float(payload.get("aggregate_memory_score"), 0.0),
        "decay_score": _as_float(payload.get("decay_score"), 0.0),
        "hysteresis_score": _as_float(payload.get("hysteresis_score"), 0.0),
        "dominant_memory_component": _as_str(
            payload.get("dominant_memory_component"), NOT_COMPUTABLE
        ),
        "persistence_half_life_bucket": bucket,
        "memory_zone_count": _as_int(payload.get("memory_zone_count"), 0),
        "persistent_memory_count": _as_int(payload.get("persistent_memory_count"), 0),
        "rapid_decay_zone_count": _as_int(payload.get("rapid_decay_zone_count"), 0),
        "hysteresis_zone_count": _as_int(payload.get("hysteresis_zone_count"), 0),
        "replay_memory_zone_count": _as_int(payload.get("replay_memory_zone_count"), 0),
        "topology_memory_zone_count": _as_int(payload.get("topology_memory_zone_count"), 0),
        "drift_memory_zone_count": _as_int(payload.get("drift_memory_zone_count"), 0),
        "memory_advisory_flags": _as_str_list(payload.get("memory_advisory_flags")),
    }
