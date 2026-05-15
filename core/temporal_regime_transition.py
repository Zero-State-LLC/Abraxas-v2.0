"""Deterministic temporal regime transition and phase-boundary detection for P24.

PATCH-P24-TEMPORAL-REGIME-TRANSITION-AND-PHASE-BOUNDARY-DETECTION-001

Adds deterministic temporal regime transition and phase-boundary detection over
the stabilized P14–P23 projection/transport/diff/convergence/fusion/cartography
stack.

Hard invariants (always enforced):
    advisory_only               = True
    detection_only              = True
    visualization_support_only  = True
    execution_authority         = False
    authority_granted           = False
    mutation_allowed            = False
    promotion_allowed           = False
    auto_execute                = False
    auto_approve                = False
    command_channel             = False
    bidirectional_control       = False
    inference_authority         = False
    replay_mutation_allowed     = False
    canon_mutation_allowed      = False
    forecast_mutation_allowed   = False
    operator_execution_allowed  = False
    autonomous_adaptation       = False

No runtime mutation.  No replay mutation.  No canon mutation.
No forecast mutation.  No optimization auto-apply.
No operator execution authority.  No command channel.
No autonomous adaptation.  No phase-boundary output may create authority.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P24-TEMPORAL-REGIME-TRANSITION-AND-PHASE-BOUNDARY-DETECTION-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"
ADVISORY_ONLY = "ADVISORY_ONLY"

# ---------------------------------------------------------------------------
# Hard invariants — never mutated
# ---------------------------------------------------------------------------

_INVARIANTS: dict[str, Any] = {
    "advisory_only": True,
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
    "replay_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "forecast_mutation_allowed": False,
    "operator_execution_allowed": False,
    "autonomous_adaptation": False,
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
        "replay_mutation_allowed",
        "canon_mutation_allowed",
        "forecast_mutation_allowed",
        "operator_execution_allowed",
        "autonomous_adaptation",
    }
)

# ---------------------------------------------------------------------------
# Regime-severity ordering for transition analytics
# ---------------------------------------------------------------------------

_STATE_SEVERITY: dict[str, int] = {
    "CALM": 0,
    "WATCH": 1,
    "PRESSURE_WAVE": 2,
    "REGIME_RISK": 3,
    "FRACTURE_RISK": 4,
    "UNSTABLE": 5,
    NOT_COMPUTABLE: -1,
    BLOCKED: -1,
}

_TRANSITION_DIRECTION: dict[tuple[int, int], str] = {
    # (before, after) -> direction
}


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------


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
    return round(max(0.0, min(1.0, numerator / denominator)), 6)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / float(len(values)), 6)


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


# ---------------------------------------------------------------------------
# Source entry ingestion
# ---------------------------------------------------------------------------


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
                f"authority_boundary_violation:{source_key}:{path}"
                for path in forbidden
            )
        if status == "PRESENT" and payload_hash is None:
            final_status = BLOCKED
            local_blockers.append(f"hash_not_computable:{source_key}")
        blockers.update(local_blockers)
        entries.append(
            _apply_invariants(
                {
                    "schema": "TemporalRegimeTransitionSourceEntry.v1",
                    "source_key": source_key,
                    "source_path": str(source_path),
                    "source_status": status,
                    "source_hash": payload_hash,
                    "authority_boundary_violations": forbidden,
                    "advisory_flags": sorted(
                        {
                            "advisory_only",
                            "detection_only",
                            "visualization_support_only",
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


# ---------------------------------------------------------------------------
# Phase-boundary detection
# ---------------------------------------------------------------------------


def _detect_phase_boundaries(
    cartography: dict[str, Any] | None,
    regime_detector: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Detect phase boundaries from cartography regime-boundary summaries and detector transitions."""
    boundaries: list[dict[str, Any]] = []

    if isinstance(cartography, dict):
        regime_boundary_summary = cartography.get("regime_boundary_summary")
        if isinstance(regime_boundary_summary, dict):
            for boundary in _as_dict_list(regime_boundary_summary.get("boundaries")):
                track_ref = _as_str(boundary.get("track_ref"))
                velocity = _as_float(boundary.get("velocity_score"))
                boundary_kind = _as_str(boundary.get("boundary_kind"), "HIGH_VELOCITY_TRANSITION")
                boundary_id = str(
                    canonical_hash(
                        {
                            "source": "cartography_regime_boundary",
                            "track_ref": track_ref,
                            "boundary_kind": boundary_kind,
                        }
                    )
                )
                boundaries.append(
                    _apply_invariants(
                        {
                            "schema": "TemporalPhaseBoundary.v1",
                            "boundary_id": boundary_id,
                            "boundary_kind": boundary_kind,
                            "source": "cartography_regime_boundary",
                            "track_ref": track_ref,
                            "velocity_score": velocity,
                            "confidence": 0.75 if velocity >= 0.65 else 0.5,
                            "advisory_flags": [
                                "detection_only",
                                "analytics_only",
                                "bounded_metrics",
                            ],
                            "final_status": ADVISORY_ONLY,
                        }
                    )
                )

    if isinstance(regime_detector, dict):
        for event in _as_dict_list(regime_detector.get("transition_events")):
            from_state = _as_str(event.get("from_state"), NOT_COMPUTABLE)
            to_state = _as_str(event.get("to_state"), NOT_COMPUTABLE)
            prob = _as_float(event.get("transition_probability"))
            boundary_kind = "REGIME_STATE_TRANSITION"
            boundary_id = str(
                canonical_hash(
                    {
                        "source": "regime_detector_transition",
                        "from_state": from_state,
                        "to_state": to_state,
                    }
                )
            )
            boundaries.append(
                _apply_invariants(
                    {
                        "schema": "TemporalPhaseBoundary.v1",
                        "boundary_id": boundary_id,
                        "boundary_kind": boundary_kind,
                        "source": "regime_detector_transition",
                        "from_state": from_state,
                        "to_state": to_state,
                        "transition_probability": prob,
                        "confidence": _as_float(event.get("transition_confidence"), 0.5),
                        "advisory_flags": [
                            "detection_only",
                            "analytics_only",
                            "bounded_metrics",
                        ],
                        "final_status": ADVISORY_ONLY,
                    }
                )
            )

    return sorted(boundaries, key=lambda b: _as_str(b.get("boundary_id")))


# ---------------------------------------------------------------------------
# Replay collapse detection
# ---------------------------------------------------------------------------


def _detect_replay_collapse(
    cartography: dict[str, Any] | None,
    regime_detector: dict[str, Any] | None,
) -> dict[str, Any]:
    """Detect replay collapse signals from cartography corridors and regime instability."""
    collapse_signals: list[dict[str, Any]] = []

    if isinstance(cartography, dict):
        for corridor in _as_dict_list(cartography.get("atlas_corridors")):
            corridor_kind = _as_str(corridor.get("corridor_kind"))
            replay_stability = _as_float(corridor.get("replay_stability"))
            drift_score = _as_float(corridor.get("drift_score"))
            if corridor_kind == "REPLAY_CORRIDOR" and (
                replay_stability < 0.4 or drift_score >= 0.5
            ):
                signal_id = str(
                    canonical_hash(
                        {
                            "source": "replay_corridor_collapse",
                            "corridor_id": _as_str(corridor.get("corridor_id")),
                        }
                    )
                )
                collapse_signals.append(
                    _apply_invariants(
                        {
                            "schema": "ReplayCollapseSignal.v1",
                            "signal_id": signal_id,
                            "corridor_ref": _as_str(corridor.get("corridor_id")),
                            "replay_stability": replay_stability,
                            "drift_score": drift_score,
                            "severity": (
                                "HIGH" if replay_stability < 0.2 or drift_score >= 0.75
                                else "ELEVATED"
                            ),
                            "advisory_flags": ["detection_only", "analytics_only"],
                            "final_status": ADVISORY_ONLY,
                        }
                    )
                )

    if isinstance(regime_detector, dict):
        for metric in _as_dict_list(regime_detector.get("instability_metrics")):
            metric_type = _as_str(metric.get("metric_type"))
            metric_posture = _as_str(metric.get("metric_posture"))
            if metric_type == "TRANSITION_PROBABILITY" and metric_posture in {"BLOCKED", "WARN"}:
                signal_id = str(
                    canonical_hash(
                        {
                            "source": "regime_instability_transition_prob",
                            "metric_posture": metric_posture,
                        }
                    )
                )
                collapse_signals.append(
                    _apply_invariants(
                        {
                            "schema": "ReplayCollapseSignal.v1",
                            "signal_id": signal_id,
                            "metric_type": metric_type,
                            "metric_value": _as_float(metric.get("metric_value")),
                            "metric_posture": metric_posture,
                            "severity": "HIGH" if metric_posture == "BLOCKED" else "ELEVATED",
                            "advisory_flags": ["detection_only", "analytics_only"],
                            "final_status": ADVISORY_ONLY,
                        }
                    )
                )

    collapse_status = (
        "COLLAPSE_RISK_DETECTED"
        if any(_as_str(s.get("severity")) == "HIGH" for s in collapse_signals)
        else (
            "COLLAPSE_WATCH"
            if collapse_signals
            else NOT_COMPUTABLE
        )
    )

    return _apply_invariants(
        {
            "schema": "ReplayCollapseReport.v1",
            "collapse_status": collapse_status,
            "signal_count": len(collapse_signals),
            "signals": sorted(collapse_signals, key=lambda s: _as_str(s.get("signal_id"))),
            "advisory_flags": ["detection_only", "analytics_only", "bounded_metrics"],
            "final_status": ADVISORY_ONLY if collapse_signals else NOT_COMPUTABLE,
        }
    )


# ---------------------------------------------------------------------------
# Continuity fracture detection
# ---------------------------------------------------------------------------


def _detect_continuity_fractures(
    cartography: dict[str, Any] | None,
    regime_detector: dict[str, Any] | None,
) -> dict[str, Any]:
    """Detect continuity fracture signals from low-continuity regions and detector states."""
    fractures: list[dict[str, Any]] = []

    if isinstance(cartography, dict):
        for region in _as_dict_list(cartography.get("atlas_regions")):
            region_kind = _as_str(region.get("region_kind"))
            continuity_ratio = _as_float(region.get("continuity_ratio"))
            if region_kind in {"DIVERGENCE_REGION", "VOLATILE_REGION", "DRIFT_ZONE"} and continuity_ratio < 0.4:
                fracture_id = str(
                    canonical_hash(
                        {
                            "source": "atlas_region_fracture",
                            "region_id": _as_str(region.get("region_id")),
                            "region_kind": region_kind,
                        }
                    )
                )
                fractures.append(
                    _apply_invariants(
                        {
                            "schema": "ContinuityFracture.v1",
                            "fracture_id": fracture_id,
                            "region_ref": _as_str(region.get("region_id")),
                            "region_kind": region_kind,
                            "continuity_ratio": continuity_ratio,
                            "severity": "HIGH" if continuity_ratio < 0.2 else "ELEVATED",
                            "advisory_flags": ["detection_only", "analytics_only"],
                            "final_status": ADVISORY_ONLY,
                        }
                    )
                )

    if isinstance(regime_detector, dict):
        current_state = regime_detector.get("current_regime_state")
        if isinstance(current_state, dict):
            state_type = _as_str(current_state.get("state_type"))
            state_score = _as_float(current_state.get("state_score"))
            if state_type in {"FRACTURE_RISK", "UNSTABLE"} and state_score >= 0.7:
                fracture_id = str(
                    canonical_hash(
                        {
                            "source": "regime_fracture_state",
                            "state_type": state_type,
                        }
                    )
                )
                fractures.append(
                    _apply_invariants(
                        {
                            "schema": "ContinuityFracture.v1",
                            "fracture_id": fracture_id,
                            "state_type": state_type,
                            "state_score": state_score,
                            "severity": "HIGH" if state_type == "UNSTABLE" else "ELEVATED",
                            "advisory_flags": ["detection_only", "analytics_only"],
                            "final_status": ADVISORY_ONLY,
                        }
                    )
                )

    fracture_status = (
        "FRACTURE_DETECTED"
        if any(_as_str(f.get("severity")) == "HIGH" for f in fractures)
        else (
            "FRACTURE_WATCH"
            if fractures
            else NOT_COMPUTABLE
        )
    )

    return _apply_invariants(
        {
            "schema": "ContinuityFractureReport.v1",
            "fracture_status": fracture_status,
            "fracture_count": len(fractures),
            "fractures": sorted(fractures, key=lambda f: _as_str(f.get("fracture_id"))),
            "advisory_flags": ["detection_only", "analytics_only", "bounded_metrics"],
            "final_status": ADVISORY_ONLY if fractures else NOT_COMPUTABLE,
        }
    )


# ---------------------------------------------------------------------------
# Drift escalation boundaries
# ---------------------------------------------------------------------------


def _compute_drift_escalation_boundaries(
    cartography: dict[str, Any] | None,
    regime_detector: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Identify drift escalation boundary thresholds from cartography density and detector metrics."""
    drift_boundaries: list[dict[str, Any]] = []

    if isinstance(cartography, dict):
        density_field = cartography.get("topology_density_field")
        if isinstance(density_field, dict):
            drift_acc = _as_float(density_field.get("drift_accumulation_score"))
            if drift_acc > 0.0:
                posture = (
                    "ESCALATION_CRITICAL" if drift_acc >= 0.75
                    else "ESCALATION_ELEVATED" if drift_acc >= 0.45
                    else "ESCALATION_WATCH"
                )
                boundary_id = str(
                    canonical_hash(
                        {
                            "source": "topology_density_drift",
                            "drift_accumulation_score": round(drift_acc, 6),
                        }
                    )
                )
                drift_boundaries.append(
                    _apply_invariants(
                        {
                            "schema": "DriftEscalationBoundary.v1",
                            "boundary_id": boundary_id,
                            "source": "topology_density_drift",
                            "drift_accumulation_score": drift_acc,
                            "escalation_posture": posture,
                            "advisory_flags": [
                                "detection_only",
                                "analytics_only",
                                "bounded_metrics",
                            ],
                            "final_status": ADVISORY_ONLY,
                        }
                    )
                )

        for zone in _as_dict_list(cartography.get("drift_accumulation_zones")):
            drift_score = _as_float(zone.get("drift_score"))
            if drift_score >= 0.45:
                posture = (
                    "ESCALATION_CRITICAL" if drift_score >= 0.75
                    else "ESCALATION_ELEVATED"
                )
                boundary_id = str(
                    canonical_hash(
                        {
                            "source": "drift_zone",
                            "zone_id": _as_str(zone.get("zone_id")),
                        }
                    )
                )
                drift_boundaries.append(
                    _apply_invariants(
                        {
                            "schema": "DriftEscalationBoundary.v1",
                            "boundary_id": boundary_id,
                            "source": "drift_zone",
                            "zone_ref": _as_str(zone.get("zone_id")),
                            "drift_score": drift_score,
                            "escalation_posture": posture,
                            "advisory_flags": ["detection_only", "analytics_only"],
                            "final_status": ADVISORY_ONLY,
                        }
                    )
                )

    if isinstance(regime_detector, dict):
        for metric in _as_dict_list(regime_detector.get("instability_metrics")):
            metric_type = _as_str(metric.get("metric_type"))
            metric_posture = _as_str(metric.get("metric_posture"))
            metric_value = _as_float(metric.get("metric_value"))
            if metric_type == "REGIME_INSTABILITY" and metric_posture in {"BLOCKED", "WARN"}:
                boundary_id = str(
                    canonical_hash(
                        {
                            "source": "regime_instability_metric",
                            "metric_type": metric_type,
                            "metric_posture": metric_posture,
                        }
                    )
                )
                drift_boundaries.append(
                    _apply_invariants(
                        {
                            "schema": "DriftEscalationBoundary.v1",
                            "boundary_id": boundary_id,
                            "source": "regime_instability_metric",
                            "metric_type": metric_type,
                            "metric_value": metric_value,
                            "metric_posture": metric_posture,
                            "escalation_posture": (
                                "ESCALATION_CRITICAL"
                                if metric_posture == "BLOCKED"
                                else "ESCALATION_ELEVATED"
                            ),
                            "advisory_flags": ["detection_only", "analytics_only"],
                            "final_status": ADVISORY_ONLY,
                        }
                    )
                )

    return sorted(drift_boundaries, key=lambda b: _as_str(b.get("boundary_id")))


# ---------------------------------------------------------------------------
# Phase-shift tracking
# ---------------------------------------------------------------------------


def _build_phase_shift_tracks(
    cartography: dict[str, Any] | None,
    regime_detector: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Track phase shifts from structural evolution tracks and detector transition events."""
    shifts: list[dict[str, Any]] = []

    if isinstance(cartography, dict):
        for track in _as_dict_list(cartography.get("structural_evolution_tracks")):
            velocity = _as_float(track.get("evolution_velocity"))
            from_ref = _as_str(track.get("from_ref"), NOT_COMPUTABLE)
            to_ref = _as_str(track.get("to_ref"), NOT_COMPUTABLE)
            continuity_delta = _as_float(track.get("continuity_delta"))
            is_shift = velocity >= 0.3 or abs(continuity_delta) >= 0.3
            if is_shift:
                shift_id = str(
                    canonical_hash(
                        {
                            "source": "structural_track_shift",
                            "track_id": _as_str(track.get("track_id")),
                        }
                    )
                )
                severity = (
                    "HIGH" if velocity >= 0.75 or abs(continuity_delta) >= 0.6
                    else "ELEVATED" if velocity >= 0.5 or abs(continuity_delta) >= 0.4
                    else "WATCH"
                )
                shifts.append(
                    _apply_invariants(
                        {
                            "schema": "PhaseShiftTrack.v1",
                            "shift_id": shift_id,
                            "source": "structural_track_shift",
                            "track_ref": _as_str(track.get("track_id")),
                            "from_ref": from_ref,
                            "to_ref": to_ref,
                            "evolution_velocity": velocity,
                            "continuity_delta": continuity_delta,
                            "severity": severity,
                            "advisory_flags": ["detection_only", "analytics_only"],
                            "final_status": ADVISORY_ONLY,
                        }
                    )
                )

    if isinstance(regime_detector, dict):
        for event in _as_dict_list(regime_detector.get("transition_events")):
            from_state = _as_str(event.get("from_state"), NOT_COMPUTABLE)
            to_state = _as_str(event.get("to_state"), NOT_COMPUTABLE)
            prob = _as_float(event.get("transition_probability"))
            from_sev = _STATE_SEVERITY.get(from_state, 0)
            to_sev = _STATE_SEVERITY.get(to_state, 0)
            delta = to_sev - from_sev
            if delta != 0:
                shift_id = str(
                    canonical_hash(
                        {
                            "source": "regime_transition_event",
                            "from_state": from_state,
                            "to_state": to_state,
                        }
                    )
                )
                direction = "ESCALATION" if delta > 0 else "DE_ESCALATION"
                severity = (
                    "HIGH" if abs(delta) >= 3
                    else "ELEVATED" if abs(delta) >= 2
                    else "WATCH"
                )
                shifts.append(
                    _apply_invariants(
                        {
                            "schema": "PhaseShiftTrack.v1",
                            "shift_id": shift_id,
                            "source": "regime_transition_event",
                            "from_state": from_state,
                            "to_state": to_state,
                            "transition_probability": prob,
                            "severity_delta": delta,
                            "direction": direction,
                            "severity": severity,
                            "advisory_flags": ["detection_only", "analytics_only"],
                            "final_status": ADVISORY_ONLY,
                        }
                    )
                )

    return sorted(shifts, key=lambda s: _as_str(s.get("shift_id")))


# ---------------------------------------------------------------------------
# Transition density metrics
# ---------------------------------------------------------------------------


def _compute_transition_density(
    phase_boundaries: list[dict[str, Any]],
    phase_shifts: list[dict[str, Any]],
    drift_escalation_boundaries: list[dict[str, Any]],
    replay_collapse: dict[str, Any],
    continuity_fractures: dict[str, Any],
) -> dict[str, Any]:
    """Compute transition density metrics from all detected events."""
    boundary_count = len(phase_boundaries)
    shift_count = len(phase_shifts)
    drift_boundary_count = len(drift_escalation_boundaries)
    collapse_count = _as_int(replay_collapse.get("signal_count"))
    fracture_count = _as_int(continuity_fractures.get("fracture_count"))

    total_events = boundary_count + shift_count + drift_boundary_count + collapse_count + fracture_count
    high_severity_events = (
        sum(1 for b in phase_boundaries if _as_str(b.get("boundary_kind")) == "REGIME_STATE_TRANSITION")
        + sum(1 for s in phase_shifts if _as_str(s.get("severity")) == "HIGH")
        + sum(1 for d in drift_escalation_boundaries if _as_str(d.get("escalation_posture")) == "ESCALATION_CRITICAL")
    )

    transition_density_score = _ratio(float(total_events), 20.0)
    high_severity_ratio = _ratio(float(high_severity_events), float(max(1, total_events)))

    source_distribution = dict(
        sorted(
            Counter(
                _as_str(b.get("source"), "unknown")
                for b in phase_boundaries + phase_shifts + drift_escalation_boundaries
            ).items()
        )
    )

    posture = (
        "TRANSITION_DENSE"
        if transition_density_score >= 0.6 or high_severity_ratio >= 0.5
        else "TRANSITION_ELEVATED"
        if transition_density_score >= 0.3 or high_severity_ratio >= 0.25
        else "TRANSITION_NOMINAL"
        if total_events > 0
        else NOT_COMPUTABLE
    )

    return _apply_invariants(
        {
            "schema": "TransitionDensityMetrics.v1",
            "total_transition_events": total_events,
            "phase_boundary_count": boundary_count,
            "phase_shift_count": shift_count,
            "drift_escalation_boundary_count": drift_boundary_count,
            "replay_collapse_signal_count": collapse_count,
            "continuity_fracture_count": fracture_count,
            "high_severity_event_count": high_severity_events,
            "transition_density_score": transition_density_score,
            "high_severity_ratio": high_severity_ratio,
            "source_distribution": source_distribution,
            "transition_density_posture": posture,
            "advisory_flags": ["detection_only", "analytics_only", "bounded_metrics"],
            "final_status": ADVISORY_ONLY if total_events > 0 else NOT_COMPUTABLE,
        }
    )


# ---------------------------------------------------------------------------
# Regime transition summaries
# ---------------------------------------------------------------------------


def _build_regime_transition_summary(
    regime_detector: dict[str, Any] | None,
    phase_boundaries: list[dict[str, Any]],
    phase_shifts: list[dict[str, Any]],
    replay_collapse: dict[str, Any],
    continuity_fractures: dict[str, Any],
    drift_escalation_boundaries: list[dict[str, Any]],
    transition_density: dict[str, Any],
) -> dict[str, Any]:
    """Build a high-level regime transition summary."""
    detector_status = NOT_COMPUTABLE
    detector_posture = NOT_COMPUTABLE
    current_state_type = NOT_COMPUTABLE

    if isinstance(regime_detector, dict):
        detector_status = _as_str(regime_detector.get("detector_status"), NOT_COMPUTABLE)
        detector_posture = _as_str(regime_detector.get("detector_posture"), NOT_COMPUTABLE)
        current_state = regime_detector.get("current_regime_state")
        if isinstance(current_state, dict):
            current_state_type = _as_str(current_state.get("state_type"), NOT_COMPUTABLE)

    has_collapse = _as_str(replay_collapse.get("collapse_status")) in {
        "COLLAPSE_RISK_DETECTED",
        "COLLAPSE_WATCH",
    }
    has_fracture = _as_str(continuity_fractures.get("fracture_status")) in {
        "FRACTURE_DETECTED",
        "FRACTURE_WATCH",
    }
    has_critical_drift = any(
        _as_str(d.get("escalation_posture")) == "ESCALATION_CRITICAL"
        for d in drift_escalation_boundaries
    )

    overall_regime_posture = (
        "REGIME_CRITICAL"
        if detector_posture in {"FRACTURE_REGIME", "UNSTABLE"} or has_collapse and has_fracture
        else "REGIME_ELEVATED"
        if detector_posture in {"REGIME_RISK", "TRANSITIONING"} or has_collapse or has_fracture or has_critical_drift
        else "REGIME_WATCH"
        if detector_posture == "WATCH" or phase_boundaries or drift_escalation_boundaries
        else "REGIME_STABLE"
        if detector_posture == "CALM"
        else NOT_COMPUTABLE
    )

    recommended_actions: list[str] = []
    if overall_regime_posture == "REGIME_CRITICAL":
        recommended_actions.append(
            "Operator review required: critical regime transition signals detected. "
            "Inspect replay collapse and continuity fracture reports."
        )
    if has_critical_drift:
        recommended_actions.append(
            "Critical drift escalation detected. Advisory monitoring only — no auto-apply."
        )
    if has_collapse:
        recommended_actions.append(
            "Replay collapse signals present. Review replay corridor stability."
        )
    if has_fracture:
        recommended_actions.append(
            "Continuity fractures detected. Review divergence and volatile regions."
        )
    if not recommended_actions:
        recommended_actions.append("No critical regime transition signals. Continue advisory monitoring.")

    return _apply_invariants(
        {
            "schema": "RegimeTransitionSummary.v1",
            "detector_status": detector_status,
            "detector_posture": detector_posture,
            "current_state_type": current_state_type,
            "overall_regime_posture": overall_regime_posture,
            "phase_boundary_count": len(phase_boundaries),
            "phase_shift_count": len(phase_shifts),
            "replay_collapse_status": _as_str(replay_collapse.get("collapse_status"), NOT_COMPUTABLE),
            "continuity_fracture_status": _as_str(continuity_fractures.get("fracture_status"), NOT_COMPUTABLE),
            "drift_escalation_boundary_count": len(drift_escalation_boundaries),
            "transition_density_posture": _as_str(
                transition_density.get("transition_density_posture"), NOT_COMPUTABLE
            ),
            "has_critical_drift": has_critical_drift,
            "has_collapse_signals": has_collapse,
            "has_fracture_signals": has_fracture,
            "recommended_actions": recommended_actions,
            "advisory_flags": sorted(
                {
                    "advisory_only",
                    "detection_only",
                    "visualization_support_only",
                    "analytics_only",
                    *(
                        ["authority_boundary_violation"]
                        if overall_regime_posture == "REGIME_CRITICAL"
                        else []
                    ),
                }
            ),
            "final_status": ADVISORY_ONLY,
        }
    )


# ---------------------------------------------------------------------------
# AAL-Viz integration surface
# ---------------------------------------------------------------------------


def _build_aal_viz_surface(
    regime_transition_summary: dict[str, Any],
    phase_boundaries: list[dict[str, Any]],
    phase_shifts: list[dict[str, Any]],
    transition_density: dict[str, Any],
    replay_collapse: dict[str, Any],
    continuity_fractures: dict[str, Any],
) -> dict[str, Any]:
    """Build an AAL-Viz-compatible projection surface for the regime transition packet."""
    overall_posture = _as_str(
        regime_transition_summary.get("overall_regime_posture"), NOT_COMPUTABLE
    )
    posture_score_map = {
        "REGIME_CRITICAL": 0.9,
        "REGIME_ELEVATED": 0.65,
        "REGIME_WATCH": 0.45,
        "REGIME_STABLE": 0.15,
        NOT_COMPUTABLE: 0.0,
    }
    posture_score = posture_score_map.get(overall_posture, 0.5)

    boundary_kinds = sorted(
        {_as_str(b.get("boundary_kind")) for b in phase_boundaries if _as_str(b.get("boundary_kind"))}
    )
    shift_directions = sorted(
        {_as_str(s.get("direction", "UNCLASSIFIED")) for s in phase_shifts if _as_str(s.get("source")) == "regime_transition_event"}
    )

    return _apply_invariants(
        {
            "schema": "TemporalRegimeTransitionVizSurface.v1",
            "overall_regime_posture": overall_posture,
            "posture_score": posture_score,
            "transition_density_score": _as_float(
                transition_density.get("transition_density_score")
            ),
            "phase_boundary_count": len(phase_boundaries),
            "phase_shift_count": len(phase_shifts),
            "boundary_kinds": boundary_kinds,
            "shift_directions": shift_directions,
            "replay_collapse_status": _as_str(
                replay_collapse.get("collapse_status"), NOT_COMPUTABLE
            ),
            "continuity_fracture_status": _as_str(
                continuity_fractures.get("fracture_status"), NOT_COMPUTABLE
            ),
            "high_severity_event_count": _as_int(
                transition_density.get("high_severity_event_count")
            ),
            "advisory_flags": [
                "advisory_only",
                "detection_only",
                "visualization_support_only",
                "analytics_only",
                "aal_viz_surface",
            ],
            "final_status": ADVISORY_ONLY,
        }
    )


# ---------------------------------------------------------------------------
# Main packet builder
# ---------------------------------------------------------------------------


def build_temporal_regime_transition_packet(
    *,
    packet_id: str = "temporal_regime_transition_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    """Build a deterministic temporal regime transition and phase-boundary detection packet."""
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
        "temporal_topology_cartography": paths.temporal_topology_cartography_latest,
        "temporal_regime_detector": paths.audit_dir / "temporal_regime_transition_detector_contract.latest.json",
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
    _ = source_hashes  # consumed indirectly via source_entries authority checks

    cartography = payloads.get("temporal_topology_cartography")
    regime_detector_audit = payloads.get("temporal_regime_detector")

    # Extract regime_detector payload from audit wrapper if nested
    regime_detector: dict[str, Any] | None = None
    if isinstance(regime_detector_audit, dict):
        # The audit file contains {status, detector_hash, receipt_hash, findings, schema_version}
        # We need to re-derive from cartography if no embedded detector
        # Use the audit status to construct a minimal summary
        regime_detector = regime_detector_audit  # advisory surface only

    # Phase-boundary detection
    phase_boundaries = _detect_phase_boundaries(cartography, regime_detector)

    # Replay collapse detection
    replay_collapse = _detect_replay_collapse(cartography, regime_detector)

    # Continuity fracture detection
    continuity_fractures = _detect_continuity_fractures(cartography, regime_detector)

    # Drift escalation boundaries
    drift_escalation_boundaries = _compute_drift_escalation_boundaries(
        cartography, regime_detector
    )

    # Phase-shift tracking
    phase_shifts = _build_phase_shift_tracks(cartography, regime_detector)

    # Transition density metrics
    transition_density = _compute_transition_density(
        phase_boundaries,
        phase_shifts,
        drift_escalation_boundaries,
        replay_collapse,
        continuity_fractures,
    )

    # Regime transition summary
    regime_transition_summary = _build_regime_transition_summary(
        regime_detector,
        phase_boundaries,
        phase_shifts,
        replay_collapse,
        continuity_fractures,
        drift_escalation_boundaries,
        transition_density,
    )

    # AAL-Viz surface
    aal_viz_surface = _build_aal_viz_surface(
        regime_transition_summary,
        phase_boundaries,
        phase_shifts,
        transition_density,
        replay_collapse,
        continuity_fractures,
    )

    # Forbidden flags scan across all sub-payloads
    forbidden_flags: list[str] = []
    for source_entry in source_entries:
        forbidden_flags.extend(_as_str_list(source_entry.get("authority_boundary_violations")))

    source_blocked = any(
        _as_str(entry.get("final_status")) == BLOCKED for entry in source_entries
    )
    source_not_computable = any(
        _as_str(entry.get("final_status")) == NOT_COMPUTABLE for entry in source_entries
    )
    source_present_count = sum(
        1 for entry in source_entries if _as_str(entry.get("source_status")) == "PRESENT"
    )

    remaining_blockers = sorted(set(source_blockers + forbidden_flags))

    if source_blocked:
        final_status = BLOCKED
    elif source_not_computable or source_present_count == 0:
        final_status = NOT_COMPUTABLE
    else:
        final_status = ADVISORY_ONLY

    packet_hash = str(
        canonical_hash(
            {
                "packet_id": packet_id,
                "source_entries": source_entries,
                "phase_boundaries": phase_boundaries,
                "phase_shifts": phase_shifts,
                "replay_collapse": replay_collapse,
                "continuity_fractures": continuity_fractures,
                "drift_escalation_boundaries": drift_escalation_boundaries,
                "transition_density": transition_density,
                "regime_transition_summary": regime_transition_summary,
                "aal_viz_surface": aal_viz_surface,
                "remaining_blockers": remaining_blockers,
                "final_status": final_status,
            }
        )
    )

    return _apply_invariants(
        {
            "schema": "TemporalRegimeTransitionPacket.v1",
            "patch_id": PATCH_ID,
            "packet_id": packet_id,
            "packet_hash": packet_hash,
            "source_entries": source_entries,
            "source_artifacts": {
                key: str(value) for key, value in sorted(resolved_sources.items())
            },
            "phase_boundaries": phase_boundaries,
            "phase_shifts": phase_shifts,
            "replay_collapse_report": replay_collapse,
            "continuity_fracture_report": continuity_fractures,
            "drift_escalation_boundaries": drift_escalation_boundaries,
            "transition_density_metrics": transition_density,
            "regime_transition_summary": regime_transition_summary,
            "aal_viz_surface": aal_viz_surface,
            "temporal_regime_transition_status": final_status,
            "phase_boundary_count": len(phase_boundaries),
            "phase_shift_count": len(phase_shifts),
            "drift_escalation_boundary_count": len(drift_escalation_boundaries),
            "remaining_blockers": remaining_blockers,
            "final_status": final_status,
        }
    )


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------


def write_temporal_regime_transition_packet(
    path: str | Path, packet: dict[str, Any]
) -> Path:
    """Write a canonical JSON temporal regime transition packet to disk."""
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_temporal_regime_transition_markdown(packet: dict[str, Any]) -> str:
    """Build a human-readable markdown summary for the temporal regime transition packet."""
    summary = packet.get("regime_transition_summary") or {}
    density = packet.get("transition_density_metrics") or {}
    collapse = packet.get("replay_collapse_report") or {}
    fractures = packet.get("continuity_fracture_report") or {}

    lines = [
        f"# Temporal Regime Transition — {_as_str(packet.get('packet_id'))}",
        "",
        f"**Patch:** `{_as_str(packet.get('patch_id'))}`",
        f"**Final Status:** `{_as_str(packet.get('final_status'), NOT_COMPUTABLE)}`",
        f"**Overall Regime Posture:** `{_as_str(summary.get('overall_regime_posture'), NOT_COMPUTABLE)}`",
        f"**Phase Boundary Count:** `{_as_int(packet.get('phase_boundary_count'))}`",
        f"**Phase Shift Count:** `{_as_int(packet.get('phase_shift_count'))}`",
        f"**Drift Escalation Boundary Count:** `{_as_int(packet.get('drift_escalation_boundary_count'))}`",
        f"**Transition Density Posture:** `{_as_str(density.get('transition_density_posture'), NOT_COMPUTABLE)}`",
        f"**Transition Density Score:** `{_as_float(density.get('transition_density_score')):.4f}`",
        f"**Replay Collapse Status:** `{_as_str(collapse.get('collapse_status'), NOT_COMPUTABLE)}`",
        f"**Continuity Fracture Status:** `{_as_str(fractures.get('fracture_status'), NOT_COMPUTABLE)}`",
        f"**Detector Status:** `{_as_str(summary.get('detector_status'), NOT_COMPUTABLE)}`",
        f"**Detector Posture:** `{_as_str(summary.get('detector_posture'), NOT_COMPUTABLE)}`",
        f"**Current State Type:** `{_as_str(summary.get('current_state_type'), NOT_COMPUTABLE)}`",
        "",
        "## Blockers",
    ]
    blockers = _as_str_list(packet.get("remaining_blockers"))
    if blockers:
        lines.extend(f"- `{blocker}`" for blocker in blockers)
    else:
        lines.append("- None")

    lines.extend(["", "## Recommended Actions"])
    for action in _as_str_list(summary.get("recommended_actions")):
        lines.append(f"- {action}")

    lines.extend(
        [
            "",
            "---",
            "",
            "> **Advisory Only.** Detection only. No mutations, authority, or execution.",
            f"> Patch: `{_as_str(packet.get('patch_id'))}`",
        ]
    )
    return "\n".join(lines) + "\n"


def summarize_temporal_regime_transition(
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    """Extract a compact summary for downstream AAL-Viz integration."""
    if not isinstance(payload, dict):
        return {
            "temporal_regime_transition_status": NOT_COMPUTABLE,
            "overall_regime_posture": NOT_COMPUTABLE,
            "phase_boundary_count": 0,
            "phase_shift_count": 0,
            "drift_escalation_boundary_count": 0,
            "transition_density_score": 0.0,
            "transition_density_posture": NOT_COMPUTABLE,
            "replay_collapse_status": NOT_COMPUTABLE,
            "continuity_fracture_status": NOT_COMPUTABLE,
        }
    summary = payload.get("regime_transition_summary") or {}
    density = payload.get("transition_density_metrics") or {}
    collapse = payload.get("replay_collapse_report") or {}
    fractures = payload.get("continuity_fracture_report") or {}
    return {
        "temporal_regime_transition_status": _as_str(
            payload.get("temporal_regime_transition_status"), NOT_COMPUTABLE
        ),
        "overall_regime_posture": _as_str(
            summary.get("overall_regime_posture"), NOT_COMPUTABLE
        ),
        "phase_boundary_count": _as_int(payload.get("phase_boundary_count")),
        "phase_shift_count": _as_int(payload.get("phase_shift_count")),
        "drift_escalation_boundary_count": _as_int(
            payload.get("drift_escalation_boundary_count")
        ),
        "transition_density_score": _as_float(density.get("transition_density_score")),
        "transition_density_posture": _as_str(
            density.get("transition_density_posture"), NOT_COMPUTABLE
        ),
        "replay_collapse_status": _as_str(
            collapse.get("collapse_status"), NOT_COMPUTABLE
        ),
        "continuity_fracture_status": _as_str(
            fractures.get("fracture_status"), NOT_COMPUTABLE
        ),
    }
