from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import *


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_temporal_regime_transition_detector(detector: TemporalRegimeTransitionDetector | Mapping[str, Any]) -> TemporalRegimeValidationReport:
    d = detector if isinstance(detector, TemporalRegimeTransitionDetector) else TemporalRegimeTransitionDetector(**dict(detector))
    findings = []
    status = "PASS"
    if d.detector_authoritative or d.auto_transition_allowed or d.history_rewrite_allowed or d.ledger_mutation_allowed or d.timeline_collapse_allowed or d.canonical_selection_allowed or d.live_execution_allowed or d.routing_change_allowed:
        findings.append(TemporalRegimeValidationFinding("FLAGS_FORBIDDEN", "error", "authoritative/auto-transition/rewrite/mutation/collapse/selection/execution/routing must be false.")); status = "BLOCKED"
    if d.current_regime_state.authoritative or any(s.authoritative for s in d.candidate_regime_states):
        findings.append(TemporalRegimeValidationFinding("STATE_AUTH_FORBIDDEN", "error", "regime states cannot be authoritative.")); status = "BLOCKED"
    if any(e.auto_transition_allowed for e in d.transition_events):
        findings.append(TemporalRegimeValidationFinding("EVENT_AUTO_TRANSITION_FORBIDDEN", "error", "transition events cannot auto-transition.")); status = "BLOCKED"
    if any(t.normalization_allowed for t in d.triggers):
        findings.append(TemporalRegimeValidationFinding("TRIGGER_NORMALIZATION_FORBIDDEN", "error", "triggers cannot normalize.")); status = "BLOCKED"
    if any(r.detector_authoritative or r.auto_transition_allowed or r.history_rewrite_allowed or r.ledger_mutation_allowed or r.timeline_collapse_allowed or r.canonical_selection_allowed or r.routing_change_allowed for r in d.recommendations):
        findings.append(TemporalRegimeValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN", "error", "recommendation authority/mutation/collapse/selection/routing flags must be false.")); status = "BLOCKED"
    if d.detector_status == "REGIME_STABLE" and not (d.detector_posture in {"CALM", "WATCH"} and not any(e.event_posture == "HIGH" for e in d.transition_events)):
        findings.append(TemporalRegimeValidationFinding("REGIME_STABLE_CONSTRAINT", "error", "REGIME_STABLE requires CALM/WATCH and no HIGH transition events.")); status = "BLOCKED"
    if d.detector_status == "REGIME_TRANSITION_DETECTED" and len(d.transition_events) < 1:
        findings.append(TemporalRegimeValidationFinding("TRANSITION_DETECTED_CONSTRAINT", "error", "REGIME_TRANSITION_DETECTED requires transition events.")); status = "BLOCKED"
    if d.detector_status == "REGIME_TRANSITION_RISK" and not (any(e.to_state == "REGIME_RISK" for e in d.transition_events) or any(t.trigger_type in {"PRESSURE_THRESHOLD", "CONVERGENCE_RISK"} and t.trigger_posture == "BLOCKED" for t in d.triggers)):
        findings.append(TemporalRegimeValidationFinding("TRANSITION_RISK_CONSTRAINT", "error", "REGIME_TRANSITION_RISK requires risk transition/event/trigger.")); status = "BLOCKED"
    if d.detector_status == "FRACTURE_REGIME_DETECTED" and not (d.current_regime_state.state_type == "FRACTURE_RISK" or any(t.trigger_type == "FRACTURE_ESCALATION" for t in d.triggers)):
        findings.append(TemporalRegimeValidationFinding("FRACTURE_DETECTED_CONSTRAINT", "error", "FRACTURE_REGIME_DETECTED requires FRACTURE_RISK state or trigger.")); status = "BLOCKED"
    if d.detector_status == "OPERATOR_REVIEW_REQUIRED" and not any(r.operator_review_required for r in d.recommendations):
        findings.append(TemporalRegimeValidationFinding("REVIEW_REQUIRED_MISSING", "error", "OPERATOR_REVIEW_REQUIRED requires operator_review_required recommendation.")); status = "BLOCKED"
    if d.created_by_lane == "FORECAST" and (d.detector_authoritative or d.auto_transition_allowed):
        findings.append(TemporalRegimeValidationFinding("FORECAST_AUTH_BLOCKED", "error", "FORECAST cannot set detector_authoritative/auto_transition_allowed true.")); status = "BLOCKED"
    if d.created_by_lane == "PROJECTION" and d.authority_ref is not None:
        findings.append(TemporalRegimeValidationFinding("PROJECTION_AUTH_BLOCKED", "error", "PROJECTION cannot create detector authority.")); status = "BLOCKED"
    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "detector_id": d.detector_id}))
    return TemporalRegimeValidationReport(status, tuple(findings), receipt_hash)
