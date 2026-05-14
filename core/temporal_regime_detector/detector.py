from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import TemporalRegimeInputRef, TemporalRegimeState, TemporalRegimeTransitionEvent, TemporalRegimeTrigger, TemporalRegimeInstabilityMetric, TemporalRegimeRecommendation, TemporalRegimeTransitionDetector
from .validator import validate_temporal_regime_transition_detector

SCHEMA_VERSION = "TemporalRegimeTransitionDetector.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_temporal_regime_transition_detector_json(detector: TemporalRegimeTransitionDetector | Mapping[str, Any]) -> str:
    payload = asdict(detector) if isinstance(detector, TemporalRegimeTransitionDetector) else dict(detector)
    payload.pop("detector_hash", None)
    return _canonical_json(payload)


def temporal_regime_transition_detector_hash(detector: TemporalRegimeTransitionDetector | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_temporal_regime_transition_detector_json(detector))


def classify_temporal_regime_state(surface: Mapping[str, Any]) -> TemporalRegimeState:
    status = str(surface.get("forecast_status", "NOT_COMPUTABLE"))
    posture = str(surface.get("forecast_posture", "NOT_COMPUTABLE"))
    mapping = {
        "LOW_PRESSURE": "CALM", "PRESSURE_BUILDING": "WATCH", "PRESSURE_WAVE_DETECTED": "PRESSURE_WAVE", "REGIME_TRANSITION_RISK": "REGIME_RISK", "FRACTURE_ESCALATION_RISK": "FRACTURE_RISK", "OPERATOR_REVIEW_REQUIRED": "UNSTABLE",
    }
    st = mapping.get(status, "UNSTABLE" if posture == "UNSTABLE" else "NOT_COMPUTABLE")
    sc = float(max([m.get("metric_value", 0.0) for m in surface.get("metrics", ())] + [0.0]))
    sp = "HIGH" if sc >= 0.85 else ("ELEVATED" if sc >= 0.55 else ("WATCH" if sc > 0 else "LOW"))
    return TemporalRegimeState(f"state-{st.lower()}", st, sc, 0.8 if st != "NOT_COMPUTABLE" else 0.0, (str(surface.get("surface_id", "")),), sp, False)


def compute_regime_detector_posture(states: Sequence[Mapping[str, Any]], transitions: Sequence[Mapping[str, Any]], triggers: Sequence[Mapping[str, Any]]) -> str:
    if any(s.get("state_type") == "UNSTABLE" for s in states):
        return "UNSTABLE"
    if any(s.get("state_type") == "FRACTURE_RISK" for s in states):
        return "FRACTURE_REGIME"
    if any(s.get("state_type") == "REGIME_RISK" for s in states):
        return "REGIME_RISK"
    if transitions:
        return "TRANSITIONING"
    if any(t.get("trigger_posture") == "WARN" for t in triggers) or any(s.get("state_type") in {"WATCH", "PRESSURE_WAVE"} for s in states):
        return "WATCH"
    return "CALM" if states else "INSUFFICIENT_FORECAST_SURFACE"


def build_temporal_regime_transition_detector(detector_id: str, input_refs: tuple[TemporalRegimeInputRef, ...], current_regime_state: TemporalRegimeState, candidate_regime_states: tuple[TemporalRegimeState, ...], transition_events: tuple[TemporalRegimeTransitionEvent, ...], triggers: tuple[TemporalRegimeTrigger, ...], instability_metrics: tuple[TemporalRegimeInstabilityMetric, ...], recommendations: tuple[TemporalRegimeRecommendation, ...], detector_status: str, detector_posture: str, detector_policy: str, created_by_lane: str, authority_ref: dict | None) -> TemporalRegimeTransitionDetector:
    draft = TemporalRegimeTransitionDetector(SCHEMA_VERSION, detector_id, input_refs, current_regime_state, candidate_regime_states, transition_events, triggers, instability_metrics, recommendations, detector_status, detector_posture, detector_policy, created_by_lane, authority_ref, False, False, False, False, False, False, False, False, "PENDING")
    return replace(draft, detector_hash=temporal_regime_transition_detector_hash(draft))


def derive_temporal_regime_transition_detector(forecast_surfaces: Sequence[Mapping[str, Any]], input_refs: Sequence[Mapping[str, Any]] | None = None) -> TemporalRegimeTransitionDetector:
    refs = tuple(TemporalRegimeInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    if not forecast_surfaces:
        s = TemporalRegimeState("state-not-computable", "NOT_COMPUTABLE", 0.0, 0.0, tuple(), "NOT_COMPUTABLE", False)
        rec = (TemporalRegimeRecommendation("rec-1", "NOT_COMPUTABLE", "No forecast surfaces; detector not computable.", True, False, False, False, False, False, False, False),)
        met = (TemporalRegimeInstabilityMetric("m-nc", "NOT_COMPUTABLE", 0.0, "ADVISORY_ONLY", "NOT_COMPUTABLE"),)
        return build_temporal_regime_transition_detector("detector-1", refs, s, (s,), tuple(), tuple(), met, rec, "NOT_COMPUTABLE", "NOT_COMPUTABLE", "ADVISORY_ONLY", "FORECAST", None)

    states = [classify_temporal_regime_state(s) for s in forecast_surfaces]
    triggers = []
    for i, s in enumerate(forecast_surfaces, start=1):
        for v in s.get("pressure_vectors", ()):
            vtype = str(v.get("vector_type", "NOT_COMPUTABLE"))
            if vtype in {"BLOCKED_PRESSURE", "NONDETERMINISM_PRESSURE"}:
                ttype = "BLOCKED_PRESSURE" if vtype == "BLOCKED_PRESSURE" else "NONDETERMINISM_PRESSURE"
                triggers.append(TemporalRegimeTrigger(f"t-{i}-{len(triggers)+1}", ttype, float(v.get("magnitude", 0.0)), "DETERMINISTIC_THRESHOLD", "BLOCKED", False))

    transitions = []
    for i in range(1, len(states)):
        a, b = states[i - 1], states[i]
        if a.state_type != b.state_type:
            p = max(a.state_score, b.state_score)
            ep = "HIGH" if p >= 0.85 else ("ELEVATED" if p >= 0.55 else "WATCH")
            transitions.append(TemporalRegimeTransitionEvent(f"tr-{i}", a.state_type, b.state_type, p, 0.8, tuple(t.trigger_id for t in triggers), tuple(), tuple(), ep, False))

    posture = compute_regime_detector_posture([asdict(s) for s in states], [asdict(t) for t in transitions], [asdict(t) for t in triggers])
    uniq = {s.state_type for s in states}
    if len(uniq) == 1:
        status = "REGIME_STABLE" if "NOT_COMPUTABLE" not in uniq else "INSUFFICIENT_FORECAST_SURFACE"
    elif any(t.from_state == "CALM" and t.to_state == "WATCH" for t in transitions):
        status = "REGIME_WATCH"
    elif any((t.from_state, t.to_state) in {("WATCH", "PRESSURE_WAVE"), ("PRESSURE_WAVE", "REGIME_RISK")} for t in transitions):
        status = "REGIME_TRANSITION_DETECTED"
    elif any((t.from_state, t.to_state) == ("REGIME_RISK", "FRACTURE_RISK") for t in transitions):
        status = "REGIME_TRANSITION_RISK"
    elif any((t.from_state, t.to_state) == ("FRACTURE_RISK", "UNSTABLE") for t in transitions):
        status = "FRACTURE_REGIME_DETECTED"
    else:
        status = "DETECTOR_READY"

    if any(t.trigger_type in {"BLOCKED_PRESSURE", "NONDETERMINISM_PRESSURE"} for t in triggers):
        status = "OPERATOR_REVIEW_REQUIRED"
        posture = "UNSTABLE"

    maxp = max([s.state_score for s in states] + [0.0])
    met = (
        TemporalRegimeInstabilityMetric("m-instability", "REGIME_INSTABILITY", maxp, "ADVISORY_ONLY", "BLOCKED" if maxp >= 0.85 else "WARN" if maxp >= 0.55 else "PASS"),
        TemporalRegimeInstabilityMetric("m-trans", "TRANSITION_PROBABILITY", max([t.transition_probability for t in transitions] + [0.0]), "ADVISORY_ONLY", "WARN" if transitions else "PASS"),
        TemporalRegimeInstabilityMetric("m-blocked", "BLOCKED_PRESSURE_INDEX", float(sum(1 for t in triggers if t.trigger_type == "BLOCKED_PRESSURE")), "ADVISORY_ONLY", "BLOCKED" if any(t.trigger_type == "BLOCKED_PRESSURE" for t in triggers) else "PASS"),
        TemporalRegimeInstabilityMetric("m-nondet", "NONDETERMINISM_INDEX", float(sum(1 for t in triggers if t.trigger_type == "NONDETERMINISM_PRESSURE")), "ADVISORY_ONLY", "BLOCKED" if any(t.trigger_type == "NONDETERMINISM_PRESSURE" for t in triggers) else "PASS"),
    )
    rec = (TemporalRegimeRecommendation("rec-1", "RECOMMEND_OPERATOR_REVIEW" if status in {"OPERATOR_REVIEW_REQUIRED", "REGIME_TRANSITION_DETECTED", "REGIME_TRANSITION_RISK", "FRACTURE_REGIME_DETECTED"} else "RECOMMEND_TOPOLOGY_MONITORING", "Deterministic regime detector recommendation.", True, False, False, False, False, False, False, False),)
    return build_temporal_regime_transition_detector("detector-1", refs, states[-1], tuple(states), tuple(transitions), tuple(triggers), met, rec, status, posture, "ADVISORY_ONLY", "FORECAST", None)


def write_temporal_regime_transition_detector_contract_audit(base_dir: Path | str = ".") -> str:
    d = derive_temporal_regime_transition_detector([
        {"surface_id": "s1", "forecast_status": "LOW_PRESSURE", "forecast_posture": "CALM", "metrics": ({"metric_value": 0.2},), "pressure_vectors": ()},
        {"surface_id": "s2", "forecast_status": "PRESSURE_BUILDING", "forecast_posture": "WATCH", "metrics": ({"metric_value": 0.6},), "pressure_vectors": ()},
    ], [{"source_type": "TEMPORAL_PRESSURE_FORECAST_SURFACE", "source_id": "s1", "source_hash": "h1"}])
    report = validate_temporal_regime_transition_detector(d)
    payload = {"status": report.status, "detector_hash": d.detector_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": d.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/temporal_regime_transition_detector_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
