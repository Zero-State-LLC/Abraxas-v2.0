from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import *
from .validator import validate_temporal_climate_dashboard_packet

SCHEMA_VERSION = "TemporalClimateDashboardPacket.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_temporal_climate_dashboard_packet_json(packet: TemporalClimateDashboardPacket | Mapping[str, Any]) -> str:
    payload = asdict(packet) if isinstance(packet, TemporalClimateDashboardPacket) else dict(packet)
    payload.pop("packet_hash", None)
    return _canonical_json(payload)


def temporal_climate_dashboard_packet_hash(packet: TemporalClimateDashboardPacket | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_temporal_climate_dashboard_packet_json(packet))


def compute_climate_packet_posture(summary: Mapping[str, Any], alerts: Sequence[Mapping[str, Any]], trend_indicators: Sequence[Mapping[str, Any]]) -> str:
    if summary.get("dominant_risk") in {"BLOCKED_HISTORY", "NONDETERMINISM"} or any(a.get("severity") == "BLOCKED" for a in alerts):
        return "UNSTABLE"
    if summary.get("dominant_risk") == "FRACTURE":
        return "FRACTURE_RISK"
    if summary.get("dominant_risk") == "REGIME_TRANSITION":
        return "REGIME_RISK"
    if summary.get("dominant_risk") == "PRESSURE" or any(t.get("trend_type") == "PRESSURE_TREND" and t.get("trend_direction") in {"WORSENING", "VOLATILE"} for t in trend_indicators):
        return "PRESSURE"
    if summary.get("dominant_risk") == "INSUFFICIENT_INPUTS":
        return "INSUFFICIENT_INPUTS"
    return "STABLE" if not alerts else "WATCH"


def build_temporal_climate_dashboard_packet(packet_id: str, input_refs: tuple[TemporalClimateInputRef, ...], climate_summary: TemporalClimateSummary, status_tiles: tuple[TemporalClimateStatusTile, ...], alerts: tuple[TemporalClimateAlert, ...], trend_indicators: tuple[TemporalClimateTrendIndicator, ...], operator_actions: tuple[TemporalClimateOperatorAction, ...], packet_status: str, packet_posture: str, packet_policy: str, created_by_lane: str, authority_ref: dict | None) -> TemporalClimateDashboardPacket:
    draft = TemporalClimateDashboardPacket(SCHEMA_VERSION, packet_id, input_refs, climate_summary, status_tiles, alerts, trend_indicators, operator_actions, packet_status, packet_posture, packet_policy, created_by_lane, authority_ref, True, False, False, False, False, False, False, False, False, False, "PENDING")
    return replace(draft, packet_hash=temporal_climate_dashboard_packet_hash(draft))


def derive_temporal_climate_dashboard_packet(regime_detectors: Sequence[Mapping[str, Any]], pressure_surfaces: Sequence[Mapping[str, Any]] | None = None, topology_indexes: Sequence[Mapping[str, Any]] | None = None, continuity_indexes: Sequence[Mapping[str, Any]] | None = None, input_refs: Sequence[Mapping[str, Any]] | None = None) -> TemporalClimateDashboardPacket:
    refs = tuple(TemporalClimateInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    pressure_surfaces = pressure_surfaces or []
    topology_indexes = topology_indexes or []
    continuity_indexes = continuity_indexes or []

    if not (regime_detectors or pressure_surfaces or topology_indexes or continuity_indexes):
        summary = TemporalClimateSummary("sum-1", "NOT_COMPUTABLE", "NOT_COMPUTABLE", "NOT_COMPUTABLE", "NOT_COMPUTABLE", "INSUFFICIENT_INPUTS", 0.0, True, True)
        action = (TemporalClimateOperatorAction("act-1", "REVIEW", "No temporal inputs; operator review required.", True, False, False, False, False, False, False, False),)
        return build_temporal_climate_dashboard_packet("packet-1", refs, summary, tuple(), (TemporalClimateAlert("al-1", "INSUFFICIENT_INPUTS", "WARN", "Temporal inputs missing.", tuple(), True, False),), (TemporalClimateTrendIndicator("tr-1", "NOT_COMPUTABLE", "NOT_COMPUTABLE", 0.0, 0.0, tuple(), True),), action, "NOT_COMPUTABLE", "NOT_COMPUTABLE", "PROJECTION_ONLY", "PROJECTION", None)

    r = regime_detectors[-1] if regime_detectors else {}
    p = pressure_surfaces[-1] if pressure_surfaces else {}
    t = topology_indexes[-1] if topology_indexes else {}
    c = continuity_indexes[-1] if continuity_indexes else {}

    regime_state = str(r.get("current_regime_state", {}).get("state_type", "NOT_COMPUTABLE"))
    pressure_state = str(p.get("forecast_status", "NOT_COMPUTABLE"))
    topology_state = str(t.get("topology_status", "NOT_COMPUTABLE"))
    continuity_state = str(c.get("index_status", "NOT_COMPUTABLE"))

    blocked = any(x in {"BLOCKED_HISTORY_PRESSURE", "BLOCKED_PRESSURE"} for x in [f.get("finding_type") for f in c.get("findings", ())] + [h.get("hotspot_type") for h in t.get("pressure_hotspots", ())] + [v.get("vector_type") for v in p.get("pressure_vectors", ())])
    nondet = any(x in {"NONDETERMINISM_PRESSURE"} for x in [f.get("finding_type") for f in c.get("findings", ())] + [h.get("hotspot_type") for h in t.get("pressure_hotspots", ())] + [v.get("vector_type") for v in p.get("pressure_vectors", ())])

    if regime_state == "UNSTABLE" or pressure_state == "OPERATOR_REVIEW_REQUIRED":
        risk = "BLOCKED_HISTORY"
    elif blocked:
        risk = "BLOCKED_HISTORY"
    elif nondet:
        risk = "NONDETERMINISM"
    elif regime_state in {"FRACTURE_RISK"} or pressure_state == "FRACTURE_ESCALATION_RISK":
        risk = "FRACTURE"
    elif regime_state == "REGIME_RISK" or pressure_state == "REGIME_TRANSITION_RISK":
        risk = "REGIME_TRANSITION"
    elif pressure_state in {"PRESSURE_BUILDING", "PRESSURE_WAVE_DETECTED"}:
        risk = "PRESSURE"
    else:
        risk = "NONE"

    summary = TemporalClimateSummary("sum-1", regime_state, pressure_state, topology_state, continuity_state, risk, 0.8 if risk != "NONE" else 0.9, risk != "NONE", True)

    tiles = [
        TemporalClimateStatusTile("tile-regime", "REGIME", "Regime", regime_state, "BLOCKED" if regime_state == "UNSTABLE" else "WARN" if regime_state in {"REGIME_RISK", "FRACTURE_RISK"} else "WATCH" if regime_state == "WATCH" else "PASS", tuple(), True),
        TemporalClimateStatusTile("tile-pressure", "PRESSURE", "Pressure", pressure_state, "BLOCKED" if pressure_state in {"OPERATOR_REVIEW_REQUIRED"} else "WARN" if pressure_state in {"REGIME_TRANSITION_RISK", "FRACTURE_ESCALATION_RISK"} else "WATCH" if pressure_state in {"PRESSURE_BUILDING", "PRESSURE_WAVE_DETECTED"} else "PASS", tuple(), True),
        TemporalClimateStatusTile("tile-topology", "TOPOLOGY", "Topology", topology_state, "WARN" if topology_state in {"PRESSURE_HOTSPOTS_PRESENT", "FRACTURE_ZONES_PRESENT"} else "PASS", tuple(), True),
        TemporalClimateStatusTile("tile-continuity", "CONTINUITY", "Continuity", continuity_state, "WARN" if continuity_state in {"CONTINUITY_MIXED", "CONTINUITY_UNSTABLE", "OPERATOR_REVIEW_REQUIRED"} else "PASS", tuple(), True),
    ]
    if blocked:
        tiles.append(TemporalClimateStatusTile("tile-blocked", "BLOCKED_HISTORY", "Blocked History", "VISIBLE", "BLOCKED", tuple(), True))
    if nondet:
        tiles.append(TemporalClimateStatusTile("tile-nondet", "NONDETERMINISM", "Nondeterminism", "VISIBLE", "BLOCKED", tuple(), True))

    alerts = []
    if pressure_state in {"PRESSURE_BUILDING", "PRESSURE_WAVE_DETECTED"}:
        alerts.append(TemporalClimateAlert("al-pressure", "PRESSURE_BUILDING", "WATCH", "Pressure is building across temporal surfaces.", tuple(), True, False))
    if regime_state == "REGIME_RISK" or pressure_state == "REGIME_TRANSITION_RISK":
        alerts.append(TemporalClimateAlert("al-regime", "REGIME_TRANSITION_RISK", "WARN", "Regime transition risk detected.", tuple(), True, False))
    if regime_state == "FRACTURE_RISK" or pressure_state == "FRACTURE_ESCALATION_RISK":
        alerts.append(TemporalClimateAlert("al-fracture", "FRACTURE_ESCALATION", "WARN", "Fracture escalation risk detected.", tuple(), True, False))
    if blocked:
        alerts.append(TemporalClimateAlert("al-blocked", "BLOCKED_HISTORY_PRESENT", "BLOCKED", "Blocked history signal remains visible.", tuple(), True, False))
    if nondet:
        alerts.append(TemporalClimateAlert("al-nondet", "NONDETERMINISM_PRESENT", "BLOCKED", "Nondeterminism signal remains visible.", tuple(), True, False))

    trends = [
        TemporalClimateTrendIndicator("tr-pressure", "PRESSURE_TREND", "WORSENING" if pressure_state in {"PRESSURE_BUILDING", "PRESSURE_WAVE_DETECTED", "REGIME_TRANSITION_RISK"} else "STABLE", 0.7, 0.8, tuple(), True),
        TemporalClimateTrendIndicator("tr-regime", "REGIME_TREND", "WORSENING" if regime_state in {"REGIME_RISK", "FRACTURE_RISK", "UNSTABLE"} else "STABLE", 0.7, 0.8, tuple(), True),
    ]

    posture = compute_climate_packet_posture(asdict(summary), [asdict(a) for a in alerts], [asdict(ti) for ti in trends])
    if posture == "UNSTABLE":
        packet_status = "OPERATOR_REVIEW_REQUIRED" if summary.operator_review_required else "CLIMATE_UNSTABLE"
    elif posture == "FRACTURE_RISK":
        packet_status = "CLIMATE_FRACTURE_RISK"
    elif posture == "REGIME_RISK":
        packet_status = "CLIMATE_REGIME_RISK"
    elif posture == "PRESSURE":
        packet_status = "CLIMATE_PRESSURE"
    elif posture == "WATCH":
        packet_status = "CLIMATE_WATCH"
    else:
        packet_status = "CLIMATE_STABLE"

    actions = (TemporalClimateOperatorAction("act-1", "REVIEW" if packet_status != "CLIMATE_STABLE" else "MONITOR_TOPOLOGY", "Deterministic climate dashboard operator action.", True, False, False, False, False, False, False, False),)
    return build_temporal_climate_dashboard_packet("packet-1", refs, summary, tuple(tiles), tuple(alerts), tuple(trends), actions, packet_status, posture, "PROJECTION_ONLY", "PROJECTION", None)


def write_temporal_climate_dashboard_packet_contract_audit(base_dir: Path | str = ".") -> str:
    packet = derive_temporal_climate_dashboard_packet(
        regime_detectors=[{"current_regime_state": {"state_type": "WATCH"}}],
        pressure_surfaces=[{"forecast_status": "PRESSURE_BUILDING", "pressure_vectors": ()}],
        topology_indexes=[{"topology_status": "PRESSURE_HOTSPOTS_PRESENT", "pressure_hotspots": ()}],
        continuity_indexes=[{"index_status": "CONTINUITY_MIXED", "findings": ()}],
        input_refs=[{"source_type": "TEMPORAL_REGIME_TRANSITION_DETECTOR", "source_id": "d1", "source_hash": "h1"}],
    )
    report = validate_temporal_climate_dashboard_packet(packet)
    payload = {"status": report.status, "packet_hash": packet.packet_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": packet.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/temporal_climate_dashboard_packet_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
