from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import *
from .validator import validate_temporal_pressure_forecast_surface

SCHEMA_VERSION = "TemporalPressureForecastSurface.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_temporal_pressure_forecast_surface_json(surface: TemporalPressureForecastSurface | Mapping[str, Any]) -> str:
    payload = asdict(surface) if isinstance(surface, TemporalPressureForecastSurface) else dict(surface)
    payload.pop("surface_hash", None)
    return _canonical_json(payload)


def temporal_pressure_forecast_surface_hash(surface: TemporalPressureForecastSurface | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_temporal_pressure_forecast_surface_json(surface))


def compute_pressure_forecast_posture(pressure_vectors: Sequence[Mapping[str, Any]], pressure_waves: Sequence[Mapping[str, Any]], regime_transition_signals: Sequence[Mapping[str, Any]]) -> str:
    if any(float(s.get("transition_probability", 0.0)) >= 0.85 for s in regime_transition_signals):
        return "UNSTABLE"
    if any(float(s.get("transition_probability", 0.0)) >= 0.70 for s in regime_transition_signals):
        return "REGIME_RISK"
    if any(float(w.get("convergence_risk", 0.0)) >= 0.70 for w in pressure_waves):
        return "PRESSURE_WAVE"
    if any(v.get("vector_posture") in {"HIGH", "ELEVATED"} for v in pressure_vectors):
        return "WATCH"
    return "CALM" if pressure_vectors or pressure_waves or regime_transition_signals else "INSUFFICIENT_TOPOLOGY"


def build_temporal_pressure_forecast_surface(surface_id: str, input_refs: tuple[TemporalPressureForecastInputRef, ...], pressure_vectors: tuple[TemporalPressureVector, ...], pressure_waves: tuple[TemporalPressureWave, ...], regime_transition_signals: tuple[TemporalRegimeTransitionSignal, ...], metrics: tuple[TemporalPressureForecastMetric, ...], recommendations: tuple[TemporalPressureForecastRecommendation, ...], forecast_status: str, forecast_posture: str, forecast_policy: str, created_by_lane: str, authority_ref: dict | None) -> TemporalPressureForecastSurface:
    draft = TemporalPressureForecastSurface(SCHEMA_VERSION, surface_id, input_refs, pressure_vectors, pressure_waves, regime_transition_signals, metrics, recommendations, forecast_status, forecast_posture, forecast_policy, created_by_lane, authority_ref, False, False, False, False, False, False, False, "PENDING")
    return replace(draft, surface_hash=temporal_pressure_forecast_surface_hash(draft))


def derive_temporal_pressure_forecast_surface(topology_indexes: Sequence[Mapping[str, Any]], input_refs: Sequence[Mapping[str, Any]] | None = None) -> TemporalPressureForecastSurface:
    refs = tuple(TemporalPressureForecastInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    if not topology_indexes:
        metrics = (TemporalPressureForecastMetric("m-nc", "NOT_COMPUTABLE", 0.0, "ADVISORY_ONLY", "NOT_COMPUTABLE"),)
        rec = (TemporalPressureForecastRecommendation("rec-1", "NOT_COMPUTABLE", "No topology inputs; forecast not computable.", True, False, False, False, False, False, False),)
        return build_temporal_pressure_forecast_surface("surface-1", refs, tuple(), tuple(), tuple(), metrics, rec, "NOT_COMPUTABLE", "NOT_COMPUTABLE", "ADVISORY_ONLY", "FORECAST", None)

    vectors = []
    waves = []
    signals = []

    for i, t in enumerate(topology_indexes, start=1):
        nodes = t.get("nodes", ())
        node_id = nodes[0].get("node_id", f"n-{i}") if nodes else f"n-{i}"
        hotspots = t.get("pressure_hotspots", ())
        fractures = t.get("fracture_zones", ())
        for h in hotspots:
            htype = str(h.get("hotspot_type", "NOT_COMPUTABLE"))
            if htype in {"BLOCKED_PRESSURE", "NONDETERMINISM_PRESSURE", "FRACTURE_PRESSURE", "CONSENSUS_VOLATILITY", "ARBITRATION_VOLATILITY"}:
                mag = float(h.get("pressure_score", 0.0))
                vectors.append(TemporalPressureVector(f"v-{i}-{len(vectors)+1}", node_id, node_id, htype, mag, 0.8, "TOPOLOGY_PROPAGATION_ONLY", "FORECAST_WINDOW_SHORT", "HIGH" if mag >= 0.85 else ("ELEVATED" if mag >= 0.55 else "WATCH"), False))
        for fz in fractures:
            score = float(fz.get("fracture_score", 0.0))
            node_ids = tuple(fz.get("node_ids", (node_id,)))
            edge_ids = tuple(fz.get("edge_ids", ()))
            vectors.append(TemporalPressureVector(f"v-f-{i}-{len(vectors)+1}", node_ids[0] if node_ids else node_id, node_ids[-1] if node_ids else node_id, "FRACTURE_PRESSURE", score, 0.85, "TOPOLOGY_PROPAGATION_ONLY", "FORECAST_WINDOW_MEDIUM", "HIGH" if score >= 0.85 else "ELEVATED", False))
            waves.append(TemporalPressureWave(f"w-{i}-{len(waves)+1}", node_ids, edge_ids, "AMPLIFYING_PRESSURE" if score >= 0.70 else "PROPAGATING_PRESSURE", score, 0.8, score, "HIGH" if score >= 0.85 else "ELEVATED", False))
            if score >= 0.70:
                signals.append(TemporalRegimeTransitionSignal(f"s-{i}-{len(signals)+1}", "PRESSURE_WAVE_TO_REGIME_RISK" if score < 0.85 else "REGIME_RISK_TO_FRACTURE_RISK", "DETERMINISTIC_THRESHOLD", score, 0.8, node_ids, (str(fz.get("fracture_zone_id", "")),), "HIGH" if score >= 0.85 else "ELEVATED", False))

    posture = compute_pressure_forecast_posture([asdict(v) for v in vectors], [asdict(w) for w in waves], [asdict(s) for s in signals])
    if not vectors and not waves and not signals and all(str(t.get("topology_posture", "")) == "STABLE" for t in topology_indexes):
        posture = "CALM"
    if any(s.transition_probability >= 0.70 for s in signals):
        status = "REGIME_TRANSITION_RISK"
    elif any(w.convergence_risk >= 0.70 for w in waves):
        status = "PRESSURE_WAVE_DETECTED"
    elif any(v.vector_posture in {"WATCH", "ELEVATED", "HIGH"} for v in vectors):
        status = "PRESSURE_BUILDING"
    else:
        status = "LOW_PRESSURE"

    if any(v.vector_type in {"BLOCKED_PRESSURE", "NONDETERMINISM_PRESSURE"} and v.vector_posture == "HIGH" for v in vectors):
        status = "OPERATOR_REVIEW_REQUIRED"
        posture = "UNSTABLE"

    mean_p = round(sum(v.magnitude for v in vectors) / max(1, len(vectors)), 10)
    max_p = round(max([v.magnitude for v in vectors] + [0.0]), 10)
    grad = round(max_p - mean_p, 10)
    tr = round(max([s.transition_probability for s in signals] + [0.0]), 10)
    conv = round(max([w.convergence_risk for w in waves] + [0.0]), 10)
    metrics = (
        TemporalPressureForecastMetric("m-max", "MAX_PRESSURE", max_p, "ADVISORY_ONLY", "BLOCKED" if max_p >= 0.85 else "WARN" if max_p >= 0.55 else "PASS"),
        TemporalPressureForecastMetric("m-mean", "MEAN_PRESSURE", mean_p, "ADVISORY_ONLY", "WARN" if mean_p >= 0.55 else "PASS"),
        TemporalPressureForecastMetric("m-grad", "PRESSURE_GRADIENT", grad, "ADVISORY_ONLY", "WARN" if grad > 0 else "PASS"),
        TemporalPressureForecastMetric("m-conv", "CONVERGENCE_RISK", conv, "ADVISORY_ONLY", "BLOCKED" if conv >= 0.85 else "WARN" if conv >= 0.55 else "PASS"),
        TemporalPressureForecastMetric("m-regime", "REGIME_TRANSITION_PROBABILITY", tr, "ADVISORY_ONLY", "BLOCKED" if tr >= 0.70 else "PASS"),
    )
    rec = (TemporalPressureForecastRecommendation("rec-1", "RECOMMEND_OPERATOR_REVIEW" if status in {"OPERATOR_REVIEW_REQUIRED", "REGIME_TRANSITION_RISK", "PRESSURE_WAVE_DETECTED", "PRESSURE_BUILDING"} else "RECOMMEND_TOPOLOGY_MONITORING", "Deterministic pressure forecast advisory recommendation.", True, False, False, False, False, False, False),)
    return build_temporal_pressure_forecast_surface("surface-1", refs, tuple(vectors), tuple(waves), tuple(signals), metrics, rec, status, posture, "ADVISORY_ONLY", "FORECAST", None)


def write_temporal_pressure_forecast_surface_contract_audit(base_dir: Path | str = ".") -> str:
    surface = derive_temporal_pressure_forecast_surface([
        {"topology_status": "TOPOLOGY_STABLE", "topology_posture": "STABLE", "nodes": ({"node_id": "n1"},), "pressure_hotspots": (), "fracture_zones": ()},
        {"topology_status": "TOPOLOGY_STABLE", "topology_posture": "STABLE", "nodes": ({"node_id": "n2"},), "pressure_hotspots": (), "fracture_zones": ()},
    ], [{"source_type": "TEMPORAL_GOVERNANCE_TOPOLOGY_INDEX", "source_id": "t1", "source_hash": "h1"}])
    report = validate_temporal_pressure_forecast_surface(surface)
    payload = {"status": report.status, "surface_hash": surface.surface_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": surface.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/temporal_pressure_forecast_surface_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
