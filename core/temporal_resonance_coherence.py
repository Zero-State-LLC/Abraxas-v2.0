"""Deterministic temporal resonance and coherence-field analytics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

from core.status_result import (
    STATUS_BLOCKED as BLOCKED,
    STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE,
)

PATCH_ID = "PATCH-P27-TEMPORAL-RESONANCE-AND-COHERENCE-FIELD-ANALYTICS-001"
ADVISORY_ONLY = "ADVISORY_ONLY"

_PHASE_ALIGNMENT_BUCKETS = (
    "LOW",
    "MODERATE",
    "HIGH",
    "LOCKED",
    NOT_COMPUTABLE,
    BLOCKED,
)

_COHERENCE_ZONE_KINDS = {
    "LOW_COHERENCE",
    "MODERATE_COHERENCE",
    "HIGH_COHERENCE",
    "LOCKED_COHERENCE",
    "RESONANCE_ZONE",
    "DISSONANCE_ZONE",
    "REPLAY_RESONANCE_ZONE",
    "TOPOLOGY_ALIGNMENT_ZONE",
    "PHASE_ALIGNMENT_ZONE",
    NOT_COMPUTABLE,
    BLOCKED,
}

_INVARIANTS: dict[str, Any] = {
    "advisory_only": True,
    "analytics_only": True,
    "resonance_only": True,
    "coherence_field_only": True,
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

_COMPONENT_ORDER = (
    "topology_alignment",
    "lineage_alignment",
    "replay_resonance",
    "transition_alignment",
    "pressure_memory_alignment",
    "drift_alignment",
    "transport_alignment",
    "blocker_disruption",
)

_ALIGNMENT_COMPONENT_ORDER = (
    "topology_alignment",
    "lineage_alignment",
    "replay_resonance",
    "transition_alignment",
    "pressure_memory_alignment",
    "drift_alignment",
    "transport_alignment",
)

_RESONANCE_COMPONENT_ORDER = (
    "replay_resonance",
    "transition_alignment",
    "pressure_memory_alignment",
    "topology_alignment",
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


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


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
    if denominator <= 0.0:
        return 0.0
    return _bound(numerator / denominator)


def _status_alignment(value: str) -> float:
    normalized = _as_str(value).upper()
    if normalized in {"PASS", ADVISORY_ONLY, "PRESENT", "STABLE", "HELD", "NO_CHANGE"}:
        return 1.0
    if normalized in {"VOLATILE", "WATCH", "SHIFT_DETECTED", "DRIFT_ACCELERATING"}:
        return 0.5
    if normalized in {NOT_COMPUTABLE, BLOCKED, "FAILED"}:
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


def _source_entries(
    source_paths: dict[str, str | Path],
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

    for source_key, source_path in sorted(source_paths.items()):
        payload, source_status = _load_artifact(source_path)
        payloads[source_key] = payload
        source_hash = _safe_hash(payload)
        violations = _scan_forbidden_true_flags(payload) if payload is not None else []

        final_status = "PRESENT"
        advisory_flags = [
            "advisory_only",
            "analytics_only",
            "resonance_only",
            "coherence_field_only",
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
                    "schema": "TemporalResonanceCoherenceSourceEntry.v1",
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


def _component_scores(payloads: dict[str, dict[str, Any] | None]) -> dict[str, float]:
    cartography = _as_dict(payloads.get("temporal_topology_cartography"))
    fusion = _as_dict(payloads.get("cross_run_topology_fusion"))
    convergence = _as_dict(payloads.get("multi_run_convergence"))
    transition = _as_dict(payloads.get("temporal_regime_transition"))
    pressure = _as_dict(payloads.get("temporal_stability_pressure"))
    memory = _as_dict(payloads.get("temporal_persistence_memory"))
    diff = _as_dict(payloads.get("temporal_state_diff"))
    transport = _as_dict(payloads.get("read_only_transport"))
    chronoscope = _as_dict(payloads.get("projection_chronoscope"))
    render = _as_dict(payloads.get("aal_viz_graph_render_packet"))
    queue = _as_dict(payloads.get("operator_action_queue"))

    topology_alignment = _mean(
        [
            _as_float(cartography.get("topology_density_score")),
            _as_float(fusion.get("topology_stability_score")),
            _as_float(convergence.get("topology_persistence_ratio")),
        ]
    )
    lineage_alignment = _mean(
        [
            _as_float(convergence.get("lineage_persistence_ratio")),
            _ratio(
                _as_float(fusion.get("lineage_corridor_count")),
                max(1.0, _as_float(cartography.get("atlas_corridor_count"))),
            ),
            _status_alignment(
                _as_str(
                    _as_dict(chronoscope.get("lineage_evolution")).get(
                        "lineage_status", NOT_COMPUTABLE
                    )
                )
            ),
        ]
    )
    replay_resonance = _mean(
        [
            _status_alignment(_as_str(convergence.get("replay_stability_status"))),
            _status_alignment(_as_str(transition.get("replay_collapse_status"))),
            _status_alignment(_as_str(fusion.get("replay_continuity_status"))),
            _status_alignment(_as_str(diff.get("replay_equivalence_change_status"))),
        ]
    )
    transition_alignment = _mean(
        [
            _as_float(_as_dict(transition.get("transition_density_metrics")).get("transition_density_score")),
            _bound(
                1.0
                - _ratio(
                    _as_float(transition.get("drift_escalation_boundary_count")),
                    max(
                        1.0,
                        _as_float(transition.get("phase_boundary_count"))
                        + _as_float(transition.get("phase_shift_count")),
                    ),
                )
            ),
            _bound(1.0 - _as_float(pressure.get("transition_pressure_gradient_score"))),
        ]
    )
    pressure_memory_alignment = _mean(
        [
            _bound(1.0 - _as_float(pressure.get("aggregate_stress_score"))),
            _as_float(memory.get("aggregate_memory_score")),
            _bound(1.0 - _as_float(memory.get("decay_score"))),
        ]
    )
    drift_alignment = _mean(
        [
            _bound(1.0 - _as_float(diff.get("drift_acceleration_ratio"))),
            _bound(1.0 - _ratio(
                _as_float(_as_dict(chronoscope.get("drift_timeline")).get("drift_event_count")),
                max(
                    1.0,
                    _as_float(chronoscope.get("timeline_point_count")),
                ),
            )),
            _status_alignment(_as_str(diff.get("drift_acceleration_status"))),
        ]
    )
    transport_alignment = _mean(
        [
            _status_alignment(_as_str(transport.get("read_only_transport_status"))),
            _status_alignment(_as_str(transport.get("final_status"))),
            _bound(
                1.0
                - _ratio(
                    _as_float(transport.get("transport_blocker_count")),
                    max(1.0, _as_float(transport.get("transport_frame_count"))),
                )
            ),
            _bound(
                1.0
                - _ratio(
                    _as_float(render.get("render_blocker_count")),
                    max(1.0, _as_float(render.get("render_layer_count"))),
                )
            ),
        ]
    )

    blocker_counts = [
        len(_as_str_list(_as_dict(payloads.get(key)).get("remaining_blockers")))
        for key in sorted(payloads)
        if isinstance(payloads.get(key), dict)
    ]
    total_blockers = sum(blocker_counts)
    source_count = len([1 for key in payloads if isinstance(payloads.get(key), dict)])
    blocker_disruption = _bound(
        _mean(
            [
                _ratio(float(total_blockers), max(1.0, float(source_count * 3))),
                _status_alignment(_as_str(queue.get("final_status"))),
            ]
        )
    )

    return {
        "topology_alignment": topology_alignment,
        "lineage_alignment": lineage_alignment,
        "replay_resonance": replay_resonance,
        "transition_alignment": transition_alignment,
        "pressure_memory_alignment": pressure_memory_alignment,
        "drift_alignment": drift_alignment,
        "transport_alignment": transport_alignment,
        "blocker_disruption": blocker_disruption,
    }


def _dominant_alignment_component(components: dict[str, float]) -> str:
    ranked = sorted(
        ((name, _as_float(components.get(name), 0.0)) for name in _ALIGNMENT_COMPONENT_ORDER),
        key=lambda item: (-item[1], _ALIGNMENT_COMPONENT_ORDER.index(item[0]), item[0]),
    )
    if not ranked:
        return NOT_COMPUTABLE
    if ranked[0][1] <= 0.0:
        return NOT_COMPUTABLE
    return ranked[0][0]


def _phase_alignment_bucket(*, aggregate_coherence_score: float, final_status: str) -> str:
    if final_status == BLOCKED:
        return BLOCKED
    if final_status == NOT_COMPUTABLE:
        return NOT_COMPUTABLE
    if aggregate_coherence_score >= 0.75:
        return "LOCKED"
    if aggregate_coherence_score >= 0.50:
        return "HIGH"
    if aggregate_coherence_score >= 0.25:
        return "MODERATE"
    return "LOW"


def _zone_kind(
    *,
    coherence_score: float,
    resonance_score: float,
    dissonance_score: float,
    dominant_component: str,
    final_status: str,
) -> str:
    if final_status == BLOCKED:
        return BLOCKED
    if final_status == NOT_COMPUTABLE:
        return NOT_COMPUTABLE
    if dominant_component == "replay_resonance":
        return "REPLAY_RESONANCE_ZONE"
    if dominant_component == "topology_alignment":
        return "TOPOLOGY_ALIGNMENT_ZONE"
    if dominant_component == "transition_alignment":
        return "PHASE_ALIGNMENT_ZONE"
    if dissonance_score >= 0.60:
        return "DISSONANCE_ZONE"
    if resonance_score >= 0.60:
        return "RESONANCE_ZONE"
    if coherence_score >= 0.75:
        return "LOCKED_COHERENCE"
    if coherence_score >= 0.50:
        return "HIGH_COHERENCE"
    if coherence_score >= 0.25:
        return "MODERATE_COHERENCE"
    return "LOW_COHERENCE"


def _source_regions(payloads: dict[str, dict[str, Any] | None]) -> list[str]:
    regions = _as_dict_list(_as_dict(payloads.get("temporal_topology_cartography")).get("atlas_regions"))
    return sorted(_as_str(item.get("region_id")) for item in regions if _as_str(item.get("region_id")))


def _source_memory_zones(payloads: dict[str, dict[str, Any] | None]) -> list[str]:
    zones = _as_dict_list(_as_dict(payloads.get("temporal_persistence_memory")).get("memory_zones"))
    return sorted(_as_str(item.get("zone_id")) for item in zones if _as_str(item.get("zone_id")))


def _source_pressure_zones(payloads: dict[str, dict[str, Any] | None]) -> list[str]:
    zones = _as_dict_list(_as_dict(payloads.get("temporal_stability_pressure")).get("pressure_zones"))
    return sorted(_as_str(item.get("zone_id")) for item in zones if _as_str(item.get("zone_id")))


def _build_zones(
    *,
    packet_id: str,
    source_hashes: dict[str, str],
    payloads: dict[str, dict[str, Any] | None],
    components: dict[str, float],
    aggregate_coherence_score: float,
    resonance_score: float,
    dissonance_score: float,
    dominant_component: str,
    final_status: str,
) -> list[dict[str, Any]]:
    zones: list[dict[str, Any]] = []
    source_regions = _source_regions(payloads)
    source_memory_zones = _source_memory_zones(payloads)
    source_pressure_zones = _source_pressure_zones(payloads)

    for component_name in _COMPONENT_ORDER:
        coherence_score = _as_float(components.get(component_name), 0.0)
        local_resonance = _mean(
            [
                resonance_score,
                coherence_score
                if component_name in _RESONANCE_COMPONENT_ORDER
                else aggregate_coherence_score,
            ]
        )
        local_dissonance = _bound(
            _mean(
                [
                    dissonance_score,
                    _bound(1.0 - coherence_score),
                    _as_float(components.get("blocker_disruption"), 0.0),
                ]
            )
        )
        component_dominant = (
            component_name if component_name in _ALIGNMENT_COMPONENT_ORDER else dominant_component
        )
        zone_kind = _zone_kind(
            coherence_score=coherence_score,
            resonance_score=local_resonance,
            dissonance_score=local_dissonance,
            dominant_component=component_dominant,
            final_status=final_status,
        )
        zone_id = str(
            canonical_hash(
                {
                    "packet_id": packet_id,
                    "component": component_name,
                    "zone_kind": zone_kind,
                    "source_hashes": source_hashes,
                }
            )
        )
        zones.append(
            _apply_invariants(
                {
                    "schema": "CoherenceZone.v1",
                    "zone_id": zone_id,
                    "zone_kind": zone_kind,
                    "source_regions": source_regions,
                    "source_memory_zones": source_memory_zones,
                    "source_pressure_zones": source_pressure_zones,
                    "coherence_score": coherence_score,
                    "resonance_score": local_resonance,
                    "dissonance_score": local_dissonance,
                    "dominant_coherence_component": component_dominant,
                    "source_hashes": [value for _, value in sorted(source_hashes.items())],
                    "advisory_flags": sorted(
                        {
                            "advisory_only",
                            "analytics_only",
                            "resonance_only",
                            "coherence_field_only",
                            "detection_only",
                            "bounded_metrics",
                            "deterministic_ordering",
                            *(["blocked"] if zone_kind == BLOCKED else []),
                            *(["not_computable"] if zone_kind == NOT_COMPUTABLE else []),
                        }
                    ),
                    "final_status": final_status if zone_kind not in {BLOCKED, NOT_COMPUTABLE} else zone_kind,
                }
            )
        )

    return sorted(
        zones,
        key=lambda item: (
            _as_str(item.get("zone_kind")),
            -_as_float(item.get("coherence_score")),
            -_as_float(item.get("resonance_score")),
            _as_str(item.get("zone_id")),
        ),
    )


def build_temporal_resonance_coherence_packet(
    *,
    packet_id: str = "temporal_resonance_coherence_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
        "temporal_persistence_memory": paths.temporal_persistence_memory_latest,
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

    components = _component_scores(payloads)
    alignment_values = [_as_float(components.get(name), 0.0) for name in _ALIGNMENT_COMPONENT_ORDER]
    aggregate_coherence_score = _mean(alignment_values)
    resonance_score = _mean([_as_float(components.get(name), 0.0) for name in _RESONANCE_COMPONENT_ORDER])
    dissonance_score = _bound(
        _mean(
            [
                _bound(1.0 - aggregate_coherence_score),
                _as_float(components.get("blocker_disruption"), 0.0),
            ]
        )
    )
    dominant_component = _dominant_alignment_component(components)
    evidence_count = sum(
        1 for name in _ALIGNMENT_COMPONENT_ORDER if _as_float(components.get(name), 0.0) > 0.0
    )

    remaining_blockers = sorted(set(source_blockers))
    if present_count < 3 or evidence_count < 3:
        remaining_blockers.append("remaining_blocker: insufficient_coherence_evidence")
    remaining_blockers = sorted(set(remaining_blockers))

    if source_blocked:
        final_status = BLOCKED
    elif source_not_computable or present_count < 3 or evidence_count < 3:
        final_status = NOT_COMPUTABLE
    else:
        final_status = ADVISORY_ONLY

    phase_alignment_bucket = _phase_alignment_bucket(
        aggregate_coherence_score=aggregate_coherence_score,
        final_status=final_status,
    )
    if phase_alignment_bucket not in _PHASE_ALIGNMENT_BUCKETS:
        phase_alignment_bucket = NOT_COMPUTABLE

    zones = _build_zones(
        packet_id=packet_id,
        source_hashes=source_hashes,
        payloads=payloads,
        components=components,
        aggregate_coherence_score=aggregate_coherence_score,
        resonance_score=resonance_score,
        dissonance_score=dissonance_score,
        dominant_component=dominant_component,
        final_status=final_status,
    )
    zone_kind_counts = {
        kind: sum(1 for zone in zones if _as_str(zone.get("zone_kind")) == kind)
        for kind in sorted(_COHERENCE_ZONE_KINDS)
    }

    packet_hash = str(
        canonical_hash(
            {
                "packet_id": packet_id,
                "source_entries": source_entries,
                "coherence_components": components,
                "aggregate_coherence_score": aggregate_coherence_score,
                "resonance_score": resonance_score,
                "dissonance_score": dissonance_score,
                "phase_alignment_bucket": phase_alignment_bucket,
                "dominant_coherence_component": dominant_component,
                "zones": zones,
                "final_status": final_status,
                "remaining_blockers": remaining_blockers,
            }
        )
    )

    coherence_field_id = str(
        canonical_hash(
            {
                "packet_id": packet_id,
                "packet_hash": packet_hash,
                "source_hashes": source_hashes,
            }
        )
    )

    coherence_field = _apply_invariants(
        {
            "schema": "CoherenceField.v1",
            "coherence_field_id": coherence_field_id,
            "source_surfaces": sorted(str(key) for key in resolved_sources),
            "coherence_components": {
                key: _as_float(components.get(key), 0.0) for key in _COMPONENT_ORDER
            },
            "aggregate_coherence_score": aggregate_coherence_score,
            "resonance_score": resonance_score,
            "dissonance_score": dissonance_score,
            "phase_alignment_bucket": phase_alignment_bucket,
            "evidence_count": evidence_count,
            "source_hashes": {key: value for key, value in sorted(source_hashes.items())},
            "advisory_flags": sorted(
                {
                    "advisory_only",
                    "analytics_only",
                    "resonance_only",
                    "coherence_field_only",
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

    resonance_vector = _apply_invariants(
        {
            "schema": "ResonanceVector.v1",
            "components": [
                {"component": key, "score": _as_float(components.get(key), 0.0)}
                for key in _RESONANCE_COMPONENT_ORDER
            ],
            "resonance_score": resonance_score,
            "dissonance_score": dissonance_score,
            "dominant_coherence_component": dominant_component,
            "final_status": final_status,
        }
    )
    cross_surface_alignment_summary = _apply_invariants(
        {
            "schema": "CrossSurfaceAlignmentSummary.v1",
            "topology_alignment": _as_float(components.get("topology_alignment")),
            "lineage_alignment": _as_float(components.get("lineage_alignment")),
            "drift_alignment": _as_float(components.get("drift_alignment")),
            "transport_alignment": _as_float(components.get("transport_alignment")),
            "aggregate_coherence_score": aggregate_coherence_score,
            "final_status": final_status,
        }
    )
    replay_resonance_summary = _apply_invariants(
        {
            "schema": "ReplayResonanceSummary.v1",
            "replay_resonance": _as_float(components.get("replay_resonance")),
            "resonance_score": resonance_score,
            "replay_resonance_zone_count": zone_kind_counts.get("REPLAY_RESONANCE_ZONE", 0),
            "final_status": final_status,
        }
    )
    phase_coherence_summary = _apply_invariants(
        {
            "schema": "PhaseCoherenceSummary.v1",
            "transition_alignment": _as_float(components.get("transition_alignment")),
            "phase_alignment_bucket": phase_alignment_bucket,
            "phase_alignment_zone_count": zone_kind_counts.get("PHASE_ALIGNMENT_ZONE", 0),
            "final_status": final_status,
        }
    )
    continuity_coherence_field = _apply_invariants(
        {
            "schema": "ContinuityCoherenceField.v1",
            "pressure_memory_alignment": _as_float(components.get("pressure_memory_alignment")),
            "drift_alignment": _as_float(components.get("drift_alignment")),
            "transport_alignment": _as_float(components.get("transport_alignment")),
            "aggregate_coherence_score": aggregate_coherence_score,
            "final_status": final_status,
        }
    )
    transition_resonance_gradient = _apply_invariants(
        {
            "schema": "TransitionResonanceGradient.v1",
            "transition_alignment": _as_float(components.get("transition_alignment")),
            "replay_resonance": _as_float(components.get("replay_resonance")),
            "gradient_score": _bound(
                abs(
                    _as_float(components.get("transition_alignment"))
                    - _as_float(components.get("replay_resonance"))
                )
            ),
            "final_status": final_status,
        }
    )
    topology_alignment_persistence = _apply_invariants(
        {
            "schema": "TopologyAlignmentPersistence.v1",
            "topology_alignment": _as_float(components.get("topology_alignment")),
            "lineage_alignment": _as_float(components.get("lineage_alignment")),
            "alignment_persistence": _mean(
                [
                    _as_float(components.get("topology_alignment")),
                    _as_float(components.get("lineage_alignment")),
                ]
            ),
            "final_status": final_status,
        }
    )
    coherence_field_index = _apply_invariants(
        {
            "schema": "CoherenceFieldIndex.v1",
            "coherence_field_id": coherence_field_id,
            "zone_ids": [_as_str(zone.get("zone_id")) for zone in zones],
            "zone_kind_counts": zone_kind_counts,
            "dominant_coherence_component": dominant_component,
            "phase_alignment_bucket": phase_alignment_bucket,
            "final_status": final_status,
        }
    )

    locked_coherence_count = zone_kind_counts.get("LOCKED_COHERENCE", 0)
    resonance_zone_count = zone_kind_counts.get("RESONANCE_ZONE", 0)
    dissonance_zone_count = zone_kind_counts.get("DISSONANCE_ZONE", 0)
    replay_resonance_zone_count = zone_kind_counts.get("REPLAY_RESONANCE_ZONE", 0)
    topology_alignment_zone_count = zone_kind_counts.get("TOPOLOGY_ALIGNMENT_ZONE", 0)
    phase_alignment_zone_count = zone_kind_counts.get("PHASE_ALIGNMENT_ZONE", 0)

    coherence_advisory_flags = sorted(
        {
            "advisory_only",
            "analytics_only",
            "resonance_only",
            "coherence_field_only",
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
            "Review authority boundary violations before using resonance/coherence analytics.",
            "Regenerate missing/corrupt source artifacts and rerun temporal resonance coherence.",
            "Keep resonance/coherence outputs advisory-only with manual governance review.",
        ]
        if remaining_blockers
        else [
            "Continue advisory-only monitoring of coherence and resonance fields.",
            "Review resonance, dissonance, and locked-coherence zones for manual operator triage.",
        ]
    )

    return _apply_invariants(
        {
            "schema": "TemporalResonanceCoherencePacket.v1",
            "patch_id": PATCH_ID,
            "packet_id": packet_id,
            "packet_hash": packet_hash,
            "source_entries": source_entries,
            "source_artifacts": {
                key: str(value) for key, value in sorted(resolved_sources.items())
            },
            "coherence_field": coherence_field,
            "resonance_vector": resonance_vector,
            "cross_surface_alignment_summary": cross_surface_alignment_summary,
            "replay_resonance_summary": replay_resonance_summary,
            "phase_coherence_summary": phase_coherence_summary,
            "continuity_coherence_field": continuity_coherence_field,
            "transition_resonance_gradient": transition_resonance_gradient,
            "topology_alignment_persistence": topology_alignment_persistence,
            "coherence_zones": zones,
            "coherence_field_index": coherence_field_index,
            "temporal_resonance_coherence_status": final_status,
            "aggregate_coherence_score": aggregate_coherence_score,
            "resonance_score": resonance_score,
            "dissonance_score": dissonance_score,
            "dominant_coherence_component": dominant_component,
            "phase_alignment_bucket": phase_alignment_bucket,
            "coherence_zone_count": len(zones),
            "locked_coherence_count": locked_coherence_count,
            "resonance_zone_count": resonance_zone_count,
            "dissonance_zone_count": dissonance_zone_count,
            "replay_resonance_zone_count": replay_resonance_zone_count,
            "topology_alignment_zone_count": topology_alignment_zone_count,
            "phase_alignment_zone_count": phase_alignment_zone_count,
            "coherence_advisory_flags": coherence_advisory_flags,
            "recommended_operator_next_actions": operator_next_actions,
            "remaining_blockers": remaining_blockers,
            "final_status": final_status,
        }
    )


def write_temporal_resonance_coherence_packet(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_temporal_resonance_coherence_markdown(packet: dict[str, Any]) -> str:
    blockers = [str(item) for item in packet.get("remaining_blockers", [])]
    actions = [str(item) for item in packet.get("recommended_operator_next_actions", [])]
    lines = [
        f"# Temporal Resonance Coherence — {packet.get('packet_id', '')}",
        "",
        f"**Patch:** `{packet.get('patch_id', '')}`",
        f"**Final Status:** `{packet.get('final_status', NOT_COMPUTABLE)}`",
        f"**Aggregate Coherence Score:** `{packet.get('aggregate_coherence_score', 0.0)}`",
        f"**Resonance Score:** `{packet.get('resonance_score', 0.0)}`",
        f"**Dissonance Score:** `{packet.get('dissonance_score', 0.0)}`",
        f"**Dominant Coherence Component:** `{packet.get('dominant_coherence_component', NOT_COMPUTABLE)}`",
        f"**Phase Alignment Bucket:** `{packet.get('phase_alignment_bucket', NOT_COMPUTABLE)}`",
        f"**Coherence Zone Count:** `{packet.get('coherence_zone_count', 0)}`",
        f"**Locked Coherence Count:** `{packet.get('locked_coherence_count', 0)}`",
        f"**Resonance Zone Count:** `{packet.get('resonance_zone_count', 0)}`",
        f"**Dissonance Zone Count:** `{packet.get('dissonance_zone_count', 0)}`",
        f"**Replay Resonance Zone Count:** `{packet.get('replay_resonance_zone_count', 0)}`",
        f"**Topology Alignment Zone Count:** `{packet.get('topology_alignment_zone_count', 0)}`",
        f"**Phase Alignment Zone Count:** `{packet.get('phase_alignment_zone_count', 0)}`",
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
        lines.append("- Continue advisory-only resonance/coherence monitoring.")
    lines.append("")
    return "\n".join(lines) + "\n"


def summarize_temporal_resonance_coherence(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "temporal_resonance_coherence_status": NOT_COMPUTABLE,
            "aggregate_coherence_score": 0.0,
            "resonance_score": 0.0,
            "dissonance_score": 0.0,
            "dominant_coherence_component": NOT_COMPUTABLE,
            "phase_alignment_bucket": NOT_COMPUTABLE,
            "coherence_zone_count": 0,
            "locked_coherence_count": 0,
            "resonance_zone_count": 0,
            "dissonance_zone_count": 0,
            "replay_resonance_zone_count": 0,
            "topology_alignment_zone_count": 0,
            "phase_alignment_zone_count": 0,
            "coherence_advisory_flags": [],
        }

    bucket = _as_str(payload.get("phase_alignment_bucket"), NOT_COMPUTABLE)
    if bucket not in _PHASE_ALIGNMENT_BUCKETS:
        bucket = NOT_COMPUTABLE

    return {
        "temporal_resonance_coherence_status": _as_str(
            payload.get("temporal_resonance_coherence_status"),
            _as_str(payload.get("final_status"), NOT_COMPUTABLE),
        ),
        "aggregate_coherence_score": _as_float(payload.get("aggregate_coherence_score"), 0.0),
        "resonance_score": _as_float(payload.get("resonance_score"), 0.0),
        "dissonance_score": _as_float(payload.get("dissonance_score"), 0.0),
        "dominant_coherence_component": _as_str(
            payload.get("dominant_coherence_component"), NOT_COMPUTABLE
        ),
        "phase_alignment_bucket": bucket,
        "coherence_zone_count": _as_int(payload.get("coherence_zone_count"), 0),
        "locked_coherence_count": _as_int(payload.get("locked_coherence_count"), 0),
        "resonance_zone_count": _as_int(payload.get("resonance_zone_count"), 0),
        "dissonance_zone_count": _as_int(payload.get("dissonance_zone_count"), 0),
        "replay_resonance_zone_count": _as_int(payload.get("replay_resonance_zone_count"), 0),
        "topology_alignment_zone_count": _as_int(payload.get("topology_alignment_zone_count"), 0),
        "phase_alignment_zone_count": _as_int(payload.get("phase_alignment_zone_count"), 0),
        "coherence_advisory_flags": _as_str_list(payload.get("coherence_advisory_flags")),
    }
