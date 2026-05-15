"""Deterministic temporal stability pressure and regime stress tensor analytics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P25-TEMPORAL-STABILITY-PRESSURE-AND-REGIME-STRESS-TENSOR-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"
ADVISORY_ONLY = "ADVISORY_ONLY"

_INVARIANTS: dict[str, Any] = {
    "advisory_only": True,
    "analytics_only": True,
    "pressure_only": True,
    "stress_tensor_only": True,
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
    "topology_stress",
    "continuity_stress",
    "replay_stress",
    "drift_stress",
    "transport_stress",
    "blocker_stress",
    "volatility_stress",
)


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


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


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
    if denominator <= 0:
        return 0.0
    return _bound(numerator / denominator)


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


def _source_entries(
    source_paths: dict[str, str | Path],
) -> tuple[
    list[dict[str, Any]],
    dict[str, dict[str, Any] | None],
    dict[str, str | None],
    list[str],
]:
    entries: list[dict[str, Any]] = []
    payloads: dict[str, dict[str, Any] | None] = {}
    source_hashes: dict[str, str | None] = {}
    blockers: set[str] = set()

    for source_key, source_path in sorted(source_paths.items(), key=lambda item: item[0]):
        payload, status = _load_artifact(source_path)
        payloads[source_key] = payload
        source_hash = _safe_hash(payload)
        source_hashes[source_key] = source_hash
        forbidden_paths = _scan_forbidden_true_flags(payload) if payload is not None else []
        final_status = "PRESENT"
        advisory_flags = ["advisory_only", "pressure_only", "analytics_only"]
        remaining_blockers: list[str] = []

        if status != "PRESENT":
            final_status = NOT_COMPUTABLE
            advisory_flags.append("not_computable")
            remaining_blockers.append(f"{status.lower()}_artifact:{source_path}")
        if forbidden_paths:
            final_status = BLOCKED
            advisory_flags.extend(["blocked", "authority_boundary_violation"])
            remaining_blockers.extend(
                f"authority_boundary_violation:{source_key}:{path}" for path in forbidden_paths
            )
        if status == "PRESENT" and source_hash is None:
            final_status = BLOCKED
            advisory_flags.extend(["blocked", "authority_boundary_violation"])
            remaining_blockers.append(f"hash_not_computable:{source_key}")

        blockers.update(remaining_blockers)
        entries.append(
            _apply_invariants(
                {
                    "schema": "TemporalStabilityPressureSourceEntry.v1",
                    "source_key": source_key,
                    "source_path": str(source_path),
                    "source_status": status,
                    "source_hash": source_hash,
                    "final_status": final_status,
                    "authority_boundary_violations": [
                        f"{source_key}:{path}" for path in forbidden_paths
                    ],
                    "remaining_blockers": sorted(set(remaining_blockers)),
                    "advisory_flags": sorted(set(advisory_flags)),
                }
            )
        )

    return entries, payloads, source_hashes, sorted(blockers)


def _status_to_pressure(status: str) -> float:
    mapping = {
        "PASS": 0.1,
        ADVISORY_ONLY: 0.4,
        "PRESENT": 0.35,
        NOT_COMPUTABLE: 0.85,
        BLOCKED: 1.0,
        "DRIFT_ACCELERATING": 0.8,
        "SHIFT_DETECTED": 0.75,
    }
    return mapping.get(status, 0.5)


def _collect_blockers(entries: list[dict[str, Any]], payloads: dict[str, dict[str, Any] | None]) -> list[str]:
    blockers: set[str] = set()
    for entry in entries:
        blockers.update(_as_str_list(entry.get("remaining_blockers")))
    for source_key, payload in payloads.items():
        if not isinstance(payload, dict):
            continue
        blockers.update(f"{source_key}:{item}" for item in _as_str_list(payload.get("remaining_blockers")))
    return sorted(blockers)


def _compute_components(
    payloads: dict[str, dict[str, Any] | None],
    source_entries: list[dict[str, Any]],
) -> tuple[dict[str, float], int]:
    cartography = _as_dict(payloads.get("temporal_topology_cartography"))
    fusion = _as_dict(payloads.get("cross_run_topology_fusion"))
    convergence = _as_dict(payloads.get("multi_run_convergence"))
    state_diff = _as_dict(payloads.get("temporal_state_diff"))
    transition = _as_dict(payloads.get("temporal_regime_transition"))
    chronoscope = _as_dict(payloads.get("projection_chronoscope"))
    transport = _as_dict(payloads.get("read_only_transport"))

    atlas_region_count = max(_as_int(cartography.get("atlas_region_count")), 0)
    volatile_region_count = max(_as_int(cartography.get("volatile_region_count")), 0)
    topology_density_score = _bound(_as_float(cartography.get("topology_density_score"), 0.0))
    topology_stability_score = _bound(_as_float(fusion.get("topology_stability_score"), 0.0))

    continuity_ratio = _bound(_as_float(convergence.get("lineage_persistence_ratio"), 0.0))
    replay_ratio = _bound(_as_float(convergence.get("topology_persistence_ratio"), 0.0))
    drift_ratio = _bound(_as_float(convergence.get("drift_persistence_ratio"), 0.0))

    fracture_count = _as_int(_as_dict(transition.get("continuity_fracture_report")).get("fracture_count"))
    collapse_signal_count = _as_int(_as_dict(transition.get("replay_collapse_report")).get("signal_count"))
    drift_boundary_count = _as_int(transition.get("drift_escalation_boundary_count"))
    phase_boundary_count = _as_int(transition.get("phase_boundary_count"))
    phase_shift_count = _as_int(transition.get("phase_shift_count"))
    density_score = _bound(
        _as_float(_as_dict(transition.get("transition_density_metrics")).get("transition_density_score"))
    )

    not_computable_frames = _as_int(
        _as_dict(_as_dict(transport.get("ledger")).get("not_computable_summary")).get(
            "not_computable_frame_count"
        )
    )
    blocked_frames = _as_int(
        _as_dict(_as_dict(transport.get("ledger")).get("blocker_summary")).get(
            "blocked_frame_count"
        )
    )
    frame_count = max(_as_int(transport.get("transport_frame_count")), 0)
    transport_stability_status = _as_str(transport.get("transport_stability_status"), NOT_COMPUTABLE)

    drift_acceleration_status = _as_str(state_diff.get("drift_acceleration_status"), NOT_COMPUTABLE)
    replay_equivalence_change_status = _as_str(
        state_diff.get("replay_equivalence_change_status"), NOT_COMPUTABLE
    )
    chronoscope_drift_events = _as_int(_as_dict(chronoscope.get("drift_timeline")).get("drift_event_count"))

    topology_stress = _mean(
        [
            1.0 - topology_stability_score,
            _ratio(float(volatile_region_count), float(max(atlas_region_count, 1))),
            1.0 - topology_density_score,
        ]
    )
    continuity_stress = _mean(
        [
            1.0 - continuity_ratio,
            _ratio(float(fracture_count), 8.0),
            _status_to_pressure(_as_str(transition.get("continuity_fracture_status"), NOT_COMPUTABLE)),
        ]
    )
    replay_stress = _mean(
        [
            1.0 - replay_ratio,
            _ratio(float(collapse_signal_count), 8.0),
            _status_to_pressure(replay_equivalence_change_status),
        ]
    )
    drift_stress = _mean(
        [
            1.0 - drift_ratio,
            _ratio(float(drift_boundary_count + chronoscope_drift_events), 12.0),
            _status_to_pressure(drift_acceleration_status),
        ]
    )
    transport_stress = _mean(
        [
            _ratio(float(blocked_frames + not_computable_frames), float(max(frame_count, 1))),
            _status_to_pressure(transport_stability_status),
            _status_to_pressure(_as_str(transport.get("final_status"), NOT_COMPUTABLE)),
        ]
    )
    blocker_stress = _ratio(float(len(_collect_blockers(source_entries, payloads))), 20.0)
    volatility_stress = _mean(
        [
            _ratio(float(volatile_region_count), float(max(atlas_region_count, 1))),
            density_score,
            _ratio(float(phase_shift_count + phase_boundary_count), 10.0),
        ]
    )

    components = {
        "topology_stress": topology_stress,
        "continuity_stress": continuity_stress,
        "replay_stress": replay_stress,
        "drift_stress": drift_stress,
        "transport_stress": transport_stress,
        "blocker_stress": blocker_stress,
        "volatility_stress": volatility_stress,
    }

    evidence_count = sum(
        1 for entry in source_entries if _as_str(entry.get("source_status")) == "PRESENT"
    ) + max(
        0,
        atlas_region_count + _as_int(cartography.get("atlas_corridor_count")) + phase_shift_count,
    )
    return components, evidence_count


def _dominant_component(components: dict[str, float]) -> str:
    return max(
        _COMPONENT_ORDER,
        key=lambda key: (components.get(key, 0.0), -_COMPONENT_ORDER.index(key)),
    )


def _transition_pressure_gradient(
    transition_payload: dict[str, Any] | None,
    components: dict[str, float],
    aggregate_stress_score: float,
) -> dict[str, Any]:
    transition = _as_dict(transition_payload)
    density = _as_dict(transition.get("transition_density_metrics"))
    boundary_count = _as_int(transition.get("phase_boundary_count"))
    shift_count = _as_int(transition.get("phase_shift_count"))
    drift_count = _as_int(transition.get("drift_escalation_boundary_count"))
    transition_density_score = _bound(_as_float(density.get("transition_density_score"), 0.0))
    gradient_score = _mean(
        [
            transition_density_score,
            _ratio(float(boundary_count + shift_count + drift_count), 15.0),
            aggregate_stress_score,
            components["volatility_stress"],
        ]
    )
    return _apply_invariants(
        {
            "schema": "TransitionPressureGradient.v1",
            "gradient_score": gradient_score,
            "phase_boundary_count": boundary_count,
            "phase_shift_count": shift_count,
            "drift_escalation_boundary_count": drift_count,
            "final_status": ADVISORY_ONLY,
            "advisory_flags": ["bounded_metrics", "detection_only", "analytics_only"],
        }
    )


def _zone_candidates(payloads: dict[str, dict[str, Any] | None]) -> list[dict[str, Any]]:
    transition = _as_dict(payloads.get("temporal_regime_transition"))
    cartography = _as_dict(payloads.get("temporal_topology_cartography"))
    candidates: list[dict[str, Any]] = []

    for boundary in _as_dict_list(transition.get("phase_boundaries")):
        candidates.append(
            {
                "source_boundaries": [_as_str(boundary.get("boundary_id"))],
                "source_regions": [],
                "local_stress": _bound(_as_float(boundary.get("velocity_score"), 0.5)),
            }
        )
    for region in _as_dict_list(cartography.get("atlas_regions")):
        candidates.append(
            {
                "source_boundaries": [],
                "source_regions": [_as_str(region.get("region_id"))],
                "local_stress": _bound(
                    _mean(
                        [
                            _as_float(region.get("drift_score"), 0.0),
                            _as_float(region.get("volatility_score"), 0.0),
                            1.0 - _as_float(region.get("continuity_ratio"), 0.0),
                        ]
                    )
                ),
            }
        )
    for corridor in _as_dict_list(cartography.get("atlas_corridors")):
        candidates.append(
            {
                "source_boundaries": [],
                "source_regions": [_as_str(corridor.get("corridor_id"))],
                "local_stress": _bound(
                    _mean(
                        [
                            _as_float(corridor.get("drift_score"), 0.0),
                            _as_float(corridor.get("volatility_score"), 0.0),
                            1.0 - _as_float(corridor.get("continuity_ratio"), 0.0),
                        ]
                    )
                ),
            }
        )
    return candidates


def _classify_zone(
    *,
    blocked: bool,
    not_computable: bool,
    stress_score: float,
    resilience_score: float,
    dominant_component: str,
) -> str:
    if blocked:
        return BLOCKED
    if not_computable:
        return NOT_COMPUTABLE
    if dominant_component == "continuity_stress":
        return "STRAIN_ZONE"
    if dominant_component == "replay_stress":
        return "COLLAPSE_PRESSURE_ZONE"
    if dominant_component == "drift_stress":
        return "DRIFT_LOAD_ZONE"
    if resilience_score >= 0.75:
        return "RESILIENT_ZONE"
    if stress_score < 0.25:
        return "LOW_PRESSURE"
    if stress_score < 0.50:
        return "MODERATE_PRESSURE"
    if stress_score < 0.75:
        return "HIGH_PRESSURE"
    return "CRITICAL_PRESSURE"


def _build_pressure_zones(
    *,
    payloads: dict[str, dict[str, Any] | None],
    source_hashes: dict[str, str | None],
    source_blocked: bool,
    source_not_computable: bool,
    evidence_count: int,
    aggregate_stress_score: float,
    gradient_score: float,
    components: dict[str, float],
) -> list[dict[str, Any]]:
    dominant_component = _dominant_component(components)
    candidates = _zone_candidates(payloads)
    if not candidates:
        candidates = [{"source_boundaries": [], "source_regions": [], "local_stress": aggregate_stress_score}]

    zones: list[dict[str, Any]] = []
    for candidate in candidates:
        local_stress = _bound(_mean([aggregate_stress_score, _as_float(candidate.get("local_stress"), 0.0)]))
        resilience = _bound(1.0 - local_stress)
        zone_kind = _classify_zone(
            blocked=source_blocked,
            not_computable=source_not_computable or evidence_count < 2,
            stress_score=local_stress,
            resilience_score=resilience,
            dominant_component=dominant_component,
        )
        advisory_flags = ["pressure_only", "analytics_only", "detection_only", "bounded_metrics"]
        remaining_blockers: list[str] = []
        if zone_kind == BLOCKED:
            advisory_flags.append("authority_boundary_violation")
            remaining_blockers.append("authority_boundary_violation")
        if zone_kind == NOT_COMPUTABLE:
            advisory_flags.append("not_computable")
            remaining_blockers.append("remaining_blocker: insufficient_pressure_evidence")
        zone_id = str(
            canonical_hash(
                {
                    "zone_kind": zone_kind,
                    "source_boundaries": _as_str_list(candidate.get("source_boundaries")),
                    "source_regions": _as_str_list(candidate.get("source_regions")),
                    "stress_score": local_stress,
                    "pressure_gradient": gradient_score,
                }
            )
        )
        zones.append(
            _apply_invariants(
                {
                    "schema": "PressureZone.v1",
                    "zone_id": zone_id,
                    "zone_kind": zone_kind,
                    "source_boundaries": _as_str_list(candidate.get("source_boundaries")),
                    "source_regions": _as_str_list(candidate.get("source_regions")),
                    "stress_score": local_stress,
                    "pressure_gradient": gradient_score,
                    "resilience_score": resilience,
                    "dominant_component": dominant_component,
                    "source_hashes": [value for _, value in sorted(source_hashes.items()) if value],
                    "advisory_flags": sorted(set(advisory_flags)),
                    "remaining_blockers": sorted(set(remaining_blockers)),
                    "final_status": ADVISORY_ONLY
                    if zone_kind not in {BLOCKED, NOT_COMPUTABLE}
                    else zone_kind,
                }
            )
        )
    return sorted(
        zones,
        key=lambda zone: (
            _as_str(zone.get("zone_kind")),
            -_as_float(zone.get("stress_score")),
            -_as_float(zone.get("pressure_gradient")),
            _as_str(zone.get("zone_id")),
        ),
    )


def build_temporal_stability_pressure_packet(
    *,
    packet_id: str = "temporal_stability_pressure_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
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
        provided_sources = dict(source_artifact_paths)
        missing_root = Path("__missing__")
        resolved_sources = {
            key: provided_sources.get(key, missing_root / f"{key}.latest.json")
            for key in defaults
        }
        for key, value in provided_sources.items():
            resolved_sources[key] = value

    source_entries, payloads, source_hashes, source_blockers = _source_entries(resolved_sources)
    components, evidence_count = _compute_components(payloads, source_entries)
    aggregate_stress_score = _mean([components[key] for key in _COMPONENT_ORDER])
    resilience_score = _bound(1.0 - aggregate_stress_score)
    dominant_component = _dominant_component(components)
    gradient = _transition_pressure_gradient(
        payloads.get("temporal_regime_transition"),
        components,
        aggregate_stress_score,
    )
    pressure_gradient = _as_float(gradient.get("gradient_score"))

    source_blocked = any(_as_str(entry.get("final_status")) == BLOCKED for entry in source_entries)
    source_not_computable = any(
        _as_str(entry.get("final_status")) == NOT_COMPUTABLE for entry in source_entries
    )
    present_count = sum(
        1 for entry in source_entries if _as_str(entry.get("source_status")) == "PRESENT"
    )

    zones = _build_pressure_zones(
        payloads=payloads,
        source_hashes=source_hashes,
        source_blocked=source_blocked,
        source_not_computable=source_not_computable,
        evidence_count=evidence_count,
        aggregate_stress_score=aggregate_stress_score,
        gradient_score=pressure_gradient,
        components=components,
    )

    stress_index = _apply_invariants(
        {
            "schema": "StressTensorIndex.v1",
            "zone_ids": [_as_str(zone.get("zone_id")) for zone in zones],
            "zone_kind_counts": {
                key: sum(1 for zone in zones if _as_str(zone.get("zone_kind")) == key)
                for key in sorted({_as_str(zone.get("zone_kind")) for zone in zones})
            },
            "stress_concentration_index": _bound(
                _as_float(zones[0].get("stress_score")) if zones else 0.0
            ),
            "final_status": ADVISORY_ONLY,
            "advisory_flags": ["deterministic_ordering", "index_only", "analytics_only"],
        }
    )

    stability_vector = _apply_invariants(
        {
            "schema": "StabilityPressureVector.v1",
            "components": [
                {"component": key, "score": components[key]}
                for key in sorted(_COMPONENT_ORDER)
            ],
            "dominant_component": dominant_component,
            "aggregate_stress_score": aggregate_stress_score,
            "resilience_score": resilience_score,
            "pressure_gradient": pressure_gradient,
            "final_status": ADVISORY_ONLY,
            "advisory_flags": ["bounded_metrics", "analytics_only"],
        }
    )
    continuity_summary = _apply_invariants(
        {
            "schema": "ContinuityStrainSummary.v1",
            "continuity_stress": components["continuity_stress"],
            "classification": "STRAIN_ZONE"
            if dominant_component == "continuity_stress"
            else "MONITORED",
            "final_status": ADVISORY_ONLY,
            "advisory_flags": ["bounded_metrics", "analytics_only"],
        }
    )
    replay_summary = _apply_invariants(
        {
            "schema": "ReplayPressureSummary.v1",
            "replay_stress": components["replay_stress"],
            "classification": "COLLAPSE_PRESSURE_ZONE"
            if dominant_component == "replay_stress"
            else "MONITORED",
            "final_status": ADVISORY_ONLY,
            "advisory_flags": ["bounded_metrics", "analytics_only"],
        }
    )
    drift_summary = _apply_invariants(
        {
            "schema": "DriftLoadSummary.v1",
            "drift_stress": components["drift_stress"],
            "classification": "DRIFT_LOAD_ZONE"
            if dominant_component == "drift_stress"
            else "MONITORED",
            "final_status": ADVISORY_ONLY,
            "advisory_flags": ["bounded_metrics", "analytics_only"],
        }
    )
    topology_field = _apply_invariants(
        {
            "schema": "TopologyStressField.v1",
            "topology_stress": components["topology_stress"],
            "volatility_stress": components["volatility_stress"],
            "region_count": _as_int(_as_dict(payloads.get("temporal_topology_cartography")).get("atlas_region_count")),
            "corridor_count": _as_int(
                _as_dict(payloads.get("temporal_topology_cartography")).get("atlas_corridor_count")
            ),
            "final_status": ADVISORY_ONLY,
            "advisory_flags": ["bounded_metrics", "analytics_only"],
        }
    )
    resilience_summary = _apply_invariants(
        {
            "schema": "RegimeResilienceSummary.v1",
            "resilience_score": resilience_score,
            "aggregate_stress_score": aggregate_stress_score,
            "regime_resilience": "RESILIENT" if resilience_score >= 0.75 else "STRAINED",
            "final_status": ADVISORY_ONLY,
            "advisory_flags": ["bounded_metrics", "analytics_only"],
        }
    )

    stress_tensor = _apply_invariants(
        {
            "schema": "RegimeStressTensor.v1",
            "tensor_id": str(
                canonical_hash(
                    {
                        "packet_id": packet_id,
                        "components": components,
                        "aggregate_stress_score": aggregate_stress_score,
                        "pressure_gradient": pressure_gradient,
                    }
                )
            ),
            "source_surfaces": sorted(resolved_sources.keys()),
            "stress_components": components,
            "aggregate_stress_score": aggregate_stress_score,
            "resilience_score": resilience_score,
            "pressure_gradient": pressure_gradient,
            "evidence_count": evidence_count,
            "source_hashes": {key: value for key, value in sorted(source_hashes.items())},
            "advisory_flags": ["analytics_only", "pressure_only", "stress_tensor_only"],
            "final_status": ADVISORY_ONLY,
        }
    )

    remaining_blockers = sorted(set(source_blockers))
    if present_count < 2 or evidence_count < 2:
        remaining_blockers.append("remaining_blocker: insufficient_pressure_evidence")
    remaining_blockers = sorted(set(remaining_blockers))
    if source_blocked:
        final_status = BLOCKED
    elif source_not_computable or present_count < 2 or evidence_count < 2:
        final_status = NOT_COMPUTABLE
    else:
        final_status = ADVISORY_ONLY

    critical_pressure_count = sum(
        1 for zone in zones if _as_str(zone.get("zone_kind")) == "CRITICAL_PRESSURE"
    )
    strain_zone_count = sum(
        1 for zone in zones if _as_str(zone.get("zone_kind")) == "STRAIN_ZONE"
    )
    collapse_pressure_zone_count = sum(
        1
        for zone in zones
        if _as_str(zone.get("zone_kind")) == "COLLAPSE_PRESSURE_ZONE"
    )
    drift_load_zone_count = sum(
        1 for zone in zones if _as_str(zone.get("zone_kind")) == "DRIFT_LOAD_ZONE"
    )

    packet_hash = str(
        canonical_hash(
            {
                "packet_id": packet_id,
                "source_entries": source_entries,
                "stress_tensor": stress_tensor,
                "stability_vector": stability_vector,
                "zones": zones,
                "stress_index": stress_index,
                "final_status": final_status,
                "remaining_blockers": remaining_blockers,
            }
        )
    )
    pressure_advisory_flags = sorted(
        {
            "advisory_only",
            "analytics_only",
            "pressure_only",
            "stress_tensor_only",
            "detection_only",
            "visualization_support_only",
            "deterministic_ordering",
            "bounded_metrics",
            *(["authority_boundary_violation"] if final_status == BLOCKED else []),
            *(["not_computable"] if final_status == NOT_COMPUTABLE else []),
        }
    )
    operator_next_actions = (
        [
            "Review authority boundary violations and keep pressure analytics blocked until resolved.",
            "Regenerate missing/corrupt pressure source artifacts and rerun temporal stability pressure.",
            "Maintain advisory-only monitoring with manual operator review.",
        ]
        if remaining_blockers
        else [
            "Continue advisory-only temporal stability pressure monitoring.",
            "Review critical/strain/collapse/drift zones for manual governance triage.",
        ]
    )

    return _apply_invariants(
        {
            "schema": "TemporalStabilityPressurePacket.v1",
            "patch_id": PATCH_ID,
            "packet_id": packet_id,
            "packet_hash": packet_hash,
            "source_entries": source_entries,
            "source_artifacts": {key: str(value) for key, value in sorted(resolved_sources.items())},
            "regime_stress_tensor": stress_tensor,
            "stability_pressure_vector": stability_vector,
            "continuity_strain_summary": continuity_summary,
            "replay_pressure_summary": replay_summary,
            "drift_load_summary": drift_summary,
            "topology_stress_field": topology_field,
            "transition_pressure_gradient": gradient,
            "regime_resilience_summary": resilience_summary,
            "pressure_zones": zones,
            "stress_tensor_index": stress_index,
            "aggregate_stress_score": aggregate_stress_score,
            "resilience_score": resilience_score,
            "dominant_pressure_component": dominant_component,
            "pressure_zone_count": len(zones),
            "critical_pressure_count": critical_pressure_count,
            "strain_zone_count": strain_zone_count,
            "collapse_pressure_zone_count": collapse_pressure_zone_count,
            "drift_load_zone_count": drift_load_zone_count,
            "transition_pressure_gradient_score": pressure_gradient,
            "pressure_advisory_flags": pressure_advisory_flags,
            "recommended_operator_next_actions": operator_next_actions,
            "temporal_stability_pressure_status": final_status,
            "remaining_blockers": remaining_blockers,
            "final_status": final_status,
        }
    )


def write_temporal_stability_pressure_packet(
    path: str | Path, packet: dict[str, Any]
) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_temporal_stability_pressure_markdown(packet: dict[str, Any]) -> str:
    blockers = _as_str_list(packet.get("remaining_blockers"))
    actions = _as_str_list(packet.get("recommended_operator_next_actions"))
    lines = [
        f"# Temporal Stability Pressure — {_as_str(packet.get('packet_id'))}",
        "",
        f"**Patch:** `{_as_str(packet.get('patch_id'))}`",
        f"**Final Status:** `{_as_str(packet.get('final_status'), NOT_COMPUTABLE)}`",
        f"**Aggregate Stress Score:** `{_as_float(packet.get('aggregate_stress_score')):.4f}`",
        f"**Resilience Score:** `{_as_float(packet.get('resilience_score')):.4f}`",
        f"**Dominant Pressure Component:** `{_as_str(packet.get('dominant_pressure_component'), NOT_COMPUTABLE)}`",
        f"**Pressure Zone Count:** `{_as_int(packet.get('pressure_zone_count'))}`",
        f"**Critical Pressure Count:** `{_as_int(packet.get('critical_pressure_count'))}`",
        f"**Strain Zone Count:** `{_as_int(packet.get('strain_zone_count'))}`",
        f"**Collapse Pressure Zone Count:** `{_as_int(packet.get('collapse_pressure_zone_count'))}`",
        f"**Drift Load Zone Count:** `{_as_int(packet.get('drift_load_zone_count'))}`",
        f"**Transition Pressure Gradient:** `{_as_float(packet.get('transition_pressure_gradient_score')):.4f}`",
        "",
        "## Blockers",
    ]
    if blockers:
        lines.extend(f"- `{blocker}`" for blocker in blockers)
    else:
        lines.append("- None")
    lines.extend(["", "## Operator Next Actions"])
    if actions:
        lines.extend(f"- {action}" for action in actions)
    else:
        lines.append("- Continue advisory-only temporal stability pressure monitoring.")
    lines.extend(
        [
            "",
            "---",
            "",
            "> **Advisory Only.** Pressure/stress analytics only; no authority or mutation.",
            f"> Patch: `{_as_str(packet.get('patch_id'))}`",
        ]
    )
    return "\n".join(lines) + "\n"


def summarize_temporal_stability_pressure(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "temporal_stability_pressure_status": NOT_COMPUTABLE,
            "aggregate_stress_score": 0.0,
            "resilience_score": 0.0,
            "dominant_pressure_component": NOT_COMPUTABLE,
            "pressure_zone_count": 0,
            "critical_pressure_count": 0,
            "strain_zone_count": 0,
            "collapse_pressure_zone_count": 0,
            "drift_load_zone_count": 0,
            "transition_pressure_gradient": 0.0,
            "pressure_advisory_flags": [],
        }
    gradient = _as_dict(payload.get("transition_pressure_gradient"))
    return {
        "temporal_stability_pressure_status": _as_str(
            payload.get("temporal_stability_pressure_status"), NOT_COMPUTABLE
        ),
        "aggregate_stress_score": _as_float(payload.get("aggregate_stress_score"), 0.0),
        "resilience_score": _as_float(payload.get("resilience_score"), 0.0),
        "dominant_pressure_component": _as_str(
            payload.get("dominant_pressure_component"), NOT_COMPUTABLE
        ),
        "pressure_zone_count": _as_int(payload.get("pressure_zone_count"), 0),
        "critical_pressure_count": _as_int(payload.get("critical_pressure_count"), 0),
        "strain_zone_count": _as_int(payload.get("strain_zone_count"), 0),
        "collapse_pressure_zone_count": _as_int(
            payload.get("collapse_pressure_zone_count"), 0
        ),
        "drift_load_zone_count": _as_int(payload.get("drift_load_zone_count"), 0),
        "transition_pressure_gradient": _as_float(
            payload.get("transition_pressure_gradient_score"),
            _as_float(gradient.get("gradient_score"), 0.0),
        ),
        "pressure_advisory_flags": _as_str_list(payload.get("pressure_advisory_flags")),
    }
