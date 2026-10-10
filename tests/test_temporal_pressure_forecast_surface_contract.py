import hashlib
import json
from dataclasses import asdict, replace

from core.temporal_pressure_forecast.models import TemporalPressureVector, TemporalPressureWave, TemporalRegimeTransitionSignal
from core.temporal_pressure_forecast.surface import canonical_temporal_pressure_forecast_surface_json, derive_temporal_pressure_forecast_surface, temporal_pressure_forecast_surface_hash, write_temporal_pressure_forecast_surface_contract_audit
from core.temporal_pressure_forecast.validator import validate_temporal_pressure_forecast_surface


def _topology(stable=True, hotspot=None, fracture=None, posture=None, status=None):
    p = posture or ("STABLE" if stable else "HOTSPOT_PRESSURE")
    s = status or ("TOPOLOGY_STABLE" if stable else "PRESSURE_HOTSPOTS_PRESENT")
    hotspots = tuple([hotspot] if hotspot else [])
    fractures = tuple([fracture] if fracture else [])
    return {"topology_posture": p, "topology_status": s, "nodes": ({"node_id": "n1"}, {"node_id": "n2"}), "pressure_hotspots": hotspots, "fracture_zones": fractures}


def test_forecast_derivation_contract_rules():
    assert derive_temporal_pressure_forecast_surface([]).forecast_status in {"NOT_COMPUTABLE", "INSUFFICIENT_TOPOLOGY"}
    stable = derive_temporal_pressure_forecast_surface([_topology(), _topology()])
    assert stable.forecast_status in {"LOW_PRESSURE", "FORECAST_READY"} and stable.forecast_posture in {"CALM", "WATCH"}
    mixed = derive_temporal_pressure_forecast_surface([_topology(), _topology(stable=False, hotspot={"hotspot_type": "CONSENSUS_VOLATILITY", "pressure_score": 0.6})])
    assert mixed.forecast_status in {"PRESSURE_BUILDING", "PRESSURE_WAVE_DETECTED", "REGIME_TRANSITION_RISK", "OPERATOR_REVIEW_REQUIRED"}
    h = derive_temporal_pressure_forecast_surface([_topology(stable=False, hotspot={"hotspot_type": "BLOCKED_PRESSURE", "pressure_score": 0.9})])
    assert len(h.pressure_vectors) >= 1
    f = derive_temporal_pressure_forecast_surface([_topology(stable=False, fracture={"fracture_zone_id": "fz-1", "node_ids": ("n1", "n2"), "edge_ids": ("e1",), "fracture_score": 0.9})])
    assert len(f.pressure_waves) >= 1 or len(f.regime_transition_signals) >= 1
    assert any(w.convergence_risk >= 0.70 for w in f.pressure_waves) and f.forecast_status in {"PRESSURE_WAVE_DETECTED", "REGIME_TRANSITION_RISK", "OPERATOR_REVIEW_REQUIRED"}
    assert any(s.transition_probability >= 0.70 for s in f.regime_transition_signals) and f.forecast_status in {"REGIME_TRANSITION_RISK", "OPERATOR_REVIEW_REQUIRED"}
    assert any(v.vector_type == "BLOCKED_PRESSURE" for v in h.pressure_vectors)
    n = derive_temporal_pressure_forecast_surface([_topology(stable=False, hotspot={"hotspot_type": "NONDETERMINISM_PRESSURE", "pressure_score": 0.85})])
    assert any(v.vector_type == "NONDETERMINISM_PRESSURE" for v in n.pressure_vectors)


def test_forecast_validation_hash_schema_and_audit(tmp_path):
    base = derive_temporal_pressure_forecast_surface([_topology(), _topology()])
    assert validate_temporal_pressure_forecast_surface(replace(base, forecast_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_pressure_forecast_surface(replace(base, history_rewrite_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_pressure_forecast_surface(replace(base, ledger_mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_pressure_forecast_surface(replace(base, timeline_collapse_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_pressure_forecast_surface(replace(base, canonical_selection_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_pressure_forecast_surface(replace(base, live_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_pressure_forecast_surface(replace(base, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bv = replace(base, pressure_vectors=(TemporalPressureVector("v", "n1", "n2", "BLOCKED_PRESSURE", 0.7, 0.8, "P", "H", "ELEVATED", True),))
    assert validate_temporal_pressure_forecast_surface(bv).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bw = replace(base, pressure_waves=(TemporalPressureWave("w", ("n1",), ("e1",), "PROPAGATING_PRESSURE", 0.7, 0.8, 0.7, "ELEVATED", True),))
    assert validate_temporal_pressure_forecast_surface(bw).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bs = replace(base, regime_transition_signals=(TemporalRegimeTransitionSignal("s", "WATCH_TO_PRESSURE_WAVE", "T", 0.75, 0.8, ("n1",), ("fz",), "ELEVATED", True),))
    assert validate_temporal_pressure_forecast_surface(bs).status in {"BLOCKED", "NOT_COMPUTABLE"}
    br = replace(base, recommendations=(replace(base.recommendations[0], forecast_authoritative=True),))
    assert validate_temporal_pressure_forecast_surface(br).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_pressure_forecast_surface(replace(base, created_by_lane="FORECAST", forecast_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_pressure_forecast_surface(replace(base, created_by_lane="PROJECTION", authority_ref={"a": 1})).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(base))
    alt["surface_hash"] = "x"
    assert temporal_pressure_forecast_surface_hash(base) == temporal_pressure_forecast_surface_hash(alt)
    assert canonical_temporal_pressure_forecast_surface_json(base) == canonical_temporal_pressure_forecast_surface_json(base)
    s = json.loads(open("contracts/temporal_pressure_forecast/temporal_pressure_forecast_surface.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(base).keys()))
    d = dict(asdict(base))
    d.pop("surface_id")
    assert "surface_id" in s["required"] and "surface_id" not in d

    h = write_temporal_pressure_forecast_surface_contract_audit(tmp_path)
    t = open(tmp_path / "out/audit/temporal_pressure_forecast_surface_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
