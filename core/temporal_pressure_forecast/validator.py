from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import TemporalPressureForecastSurface, TemporalPressureForecastValidationFinding, TemporalPressureForecastValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_temporal_pressure_forecast_surface(surface: TemporalPressureForecastSurface | Mapping[str, Any]) -> TemporalPressureForecastValidationReport:
    s = surface if isinstance(surface, TemporalPressureForecastSurface) else TemporalPressureForecastSurface(**dict(surface))
    findings = []
    status = "PASS"
    if s.forecast_authoritative or s.history_rewrite_allowed or s.ledger_mutation_allowed or s.timeline_collapse_allowed or s.canonical_selection_allowed or s.live_execution_allowed or s.routing_change_allowed:
        findings.append(TemporalPressureForecastValidationFinding("FLAGS_FORBIDDEN", "error", "forecast_authoritative/rewrite/mutation/collapse/selection/execution/routing must be false."))
        status = "BLOCKED"
    if any(v.routing_change_allowed for v in s.pressure_vectors):
        findings.append(TemporalPressureForecastValidationFinding("VECTOR_ROUTING_FORBIDDEN", "error", "pressure_vectors[*].routing_change_allowed must be false."))
        status = "BLOCKED"
    if any(w.mutation_allowed for w in s.pressure_waves):
        findings.append(TemporalPressureForecastValidationFinding("WAVE_MUTATION_FORBIDDEN", "error", "pressure_waves[*].mutation_allowed must be false."))
        status = "BLOCKED"
    if any(g.auto_transition_allowed for g in s.regime_transition_signals):
        findings.append(TemporalPressureForecastValidationFinding("SIGNAL_AUTO_TRANSITION_FORBIDDEN", "error", "regime_transition_signals[*].auto_transition_allowed must be false."))
        status = "BLOCKED"
    if any(r.forecast_authoritative or r.history_rewrite_allowed or r.ledger_mutation_allowed or r.timeline_collapse_allowed or r.canonical_selection_allowed or r.routing_change_allowed for r in s.recommendations):
        findings.append(TemporalPressureForecastValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN", "error", "recommendation flags must remain false."))
        status = "BLOCKED"
    if s.forecast_status == "LOW_PRESSURE" and not (s.forecast_posture in {"CALM", "WATCH"} and not any(v.vector_posture == "HIGH" for v in s.pressure_vectors) and not any(w.wave_posture == "HIGH" for w in s.pressure_waves) and not any(g.signal_posture == "HIGH" for g in s.regime_transition_signals)):
        findings.append(TemporalPressureForecastValidationFinding("LOW_PRESSURE_CONSTRAINT", "error", "LOW_PRESSURE requires CALM/WATCH and no HIGH vectors/waves/signals."))
        status = "BLOCKED"
    if s.forecast_status == "PRESSURE_BUILDING" and not (any(v.vector_posture in {"WATCH", "ELEVATED"} for v in s.pressure_vectors) or any(m.metric_type == "PRESSURE_GRADIENT" and m.metric_value > 0 for m in s.metrics)):
        findings.append(TemporalPressureForecastValidationFinding("PRESSURE_BUILDING_CONSTRAINT", "error", "PRESSURE_BUILDING requires watch/elevated vectors or hotspot-derived metric."))
        status = "BLOCKED"
    if s.forecast_status == "PRESSURE_WAVE_DETECTED" and len(s.pressure_waves) < 1:
        findings.append(TemporalPressureForecastValidationFinding("WAVE_DETECTED_CONSTRAINT", "error", "PRESSURE_WAVE_DETECTED requires at least one pressure wave."))
        status = "BLOCKED"
    if s.forecast_status == "REGIME_TRANSITION_RISK" and not any(g.transition_probability >= 0.70 for g in s.regime_transition_signals):
        findings.append(TemporalPressureForecastValidationFinding("REGIME_RISK_CONSTRAINT", "error", "REGIME_TRANSITION_RISK requires transition_probability >= 0.70."))
        status = "BLOCKED"
    if s.forecast_status == "FRACTURE_ESCALATION_RISK" and not (any(v.vector_type == "FRACTURE_PRESSURE" for v in s.pressure_vectors) or len(s.pressure_waves) > 0 or len(s.regime_transition_signals) > 0):
        findings.append(TemporalPressureForecastValidationFinding("FRACTURE_RISK_CONSTRAINT", "error", "FRACTURE_ESCALATION_RISK requires fracture-derived vector/wave/signal."))
        status = "BLOCKED"
    if s.forecast_status == "OPERATOR_REVIEW_REQUIRED" and not any(r.operator_review_required for r in s.recommendations):
        findings.append(TemporalPressureForecastValidationFinding("REVIEW_REQUIRED_MISSING", "error", "OPERATOR_REVIEW_REQUIRED requires operator_review_required recommendation."))
        status = "BLOCKED"
    if s.created_by_lane == "PROJECTION" and s.authority_ref is not None:
        findings.append(TemporalPressureForecastValidationFinding("PROJECTION_AUTH_BLOCKED", "error", "PROJECTION cannot create forecast authority."))
        status = "BLOCKED"
    if s.created_by_lane == "FORECAST" and s.forecast_authoritative:
        findings.append(TemporalPressureForecastValidationFinding("FORECAST_AUTH_BLOCKED", "error", "FORECAST cannot set forecast_authoritative=true."))
        status = "BLOCKED"
    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "surface_id": s.surface_id}))
    return TemporalPressureForecastValidationReport(status, tuple(findings), receipt_hash)
