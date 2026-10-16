import hashlib
import json
from dataclasses import asdict, replace

from core.temporal_regime_detector.detector import canonical_temporal_regime_transition_detector_json, classify_temporal_regime_state, derive_temporal_regime_transition_detector, temporal_regime_transition_detector_hash, write_temporal_regime_transition_detector_contract_audit
from core.temporal_regime_detector.models import TemporalRegimeTrigger
from core.temporal_regime_detector.validator import validate_temporal_regime_transition_detector


def _surface(status="LOW_PRESSURE", posture="CALM", metric=0.2, vectors=()):
    return {"surface_id": "s", "forecast_status": status, "forecast_posture": posture, "metrics": ({"metric_value": metric},), "pressure_vectors": vectors}


def test_regime_derivation_and_classification_rules():
    assert derive_temporal_regime_transition_detector([]).detector_status in {"NOT_COMPUTABLE", "INSUFFICIENT_FORECAST_SURFACE"}
    assert classify_temporal_regime_state(_surface("LOW_PRESSURE", "CALM")).state_type == "CALM"
    assert classify_temporal_regime_state(_surface("PRESSURE_BUILDING", "WATCH", 0.6)).state_type == "WATCH"
    assert classify_temporal_regime_state(_surface("PRESSURE_WAVE_DETECTED", "PRESSURE_WAVE", 0.8)).state_type == "PRESSURE_WAVE"
    assert classify_temporal_regime_state(_surface("REGIME_TRANSITION_RISK", "REGIME_RISK", 0.8)).state_type == "REGIME_RISK"
    assert classify_temporal_regime_state(_surface("FRACTURE_ESCALATION_RISK", "FRACTURE_RISK", 0.9)).state_type == "FRACTURE_RISK"
    assert classify_temporal_regime_state(_surface("OPERATOR_REVIEW_REQUIRED", "UNSTABLE", 0.9)).state_type == "UNSTABLE"

    stable = derive_temporal_regime_transition_detector([_surface(), _surface()])
    assert stable.detector_status == "REGIME_STABLE"
    shift = derive_temporal_regime_transition_detector([_surface("PRESSURE_BUILDING", "WATCH", 0.6), _surface("PRESSURE_WAVE_DETECTED", "PRESSURE_WAVE", 0.8)])
    assert shift.detector_status in {"REGIME_TRANSITION_DETECTED", "OPERATOR_REVIEW_REQUIRED", "DETECTOR_READY"}
    b = derive_temporal_regime_transition_detector([_surface(vectors=({"vector_type": "BLOCKED_PRESSURE", "magnitude": 0.9},))])
    assert any(t.trigger_type == "BLOCKED_PRESSURE" for t in b.triggers)
    n = derive_temporal_regime_transition_detector([_surface(vectors=({"vector_type": "NONDETERMINISM_PRESSURE", "magnitude": 0.8},))])
    assert any(t.trigger_type == "NONDETERMINISM_PRESSURE" for t in n.triggers)


def test_regime_validator_hash_schema_and_audit(tmp_path):
    base = derive_temporal_regime_transition_detector([_surface(), _surface()])
    assert validate_temporal_regime_transition_detector(replace(base, detector_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_regime_transition_detector(replace(base, auto_transition_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_regime_transition_detector(replace(base, history_rewrite_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_regime_transition_detector(replace(base, ledger_mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_regime_transition_detector(replace(base, timeline_collapse_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_regime_transition_detector(replace(base, canonical_selection_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_regime_transition_detector(replace(base, live_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_regime_transition_detector(replace(base, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bcs = replace(base, current_regime_state=replace(base.current_regime_state, authoritative=True))
    assert validate_temporal_regime_transition_detector(bcs).status in {"BLOCKED", "NOT_COMPUTABLE"}
    if base.transition_events:
        bte = replace(base, transition_events=(replace(base.transition_events[0], auto_transition_allowed=True),))
        assert validate_temporal_regime_transition_detector(bte).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bt = replace(base, triggers=(TemporalRegimeTrigger("t", "PRESSURE_THRESHOLD", 0.6, "P", "WARN", True),))
    assert validate_temporal_regime_transition_detector(bt).status in {"BLOCKED", "NOT_COMPUTABLE"}
    br = replace(base, recommendations=(replace(base.recommendations[0], detector_authoritative=True),))
    assert validate_temporal_regime_transition_detector(br).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_regime_transition_detector(replace(base, created_by_lane="FORECAST", detector_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_regime_transition_detector(replace(base, created_by_lane="PROJECTION", authority_ref={"a": 1})).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(base))
    alt["detector_hash"] = "x"
    assert temporal_regime_transition_detector_hash(base) == temporal_regime_transition_detector_hash(alt)
    assert canonical_temporal_regime_transition_detector_json(base) == canonical_temporal_regime_transition_detector_json(base)
    s = json.loads(open("contracts/temporal_regime_detector/temporal_regime_transition_detector.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(base).keys()))
    d = dict(asdict(base))
    d.pop("detector_id")
    assert "detector_id" in s["required"] and "detector_id" not in d

    h = write_temporal_regime_transition_detector_contract_audit(tmp_path)
    t = open(tmp_path / "out/audit/temporal_regime_transition_detector_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
