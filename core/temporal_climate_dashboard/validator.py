from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import TemporalClimateDashboardPacket, TemporalClimateValidationFinding, TemporalClimateValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_temporal_climate_dashboard_packet(packet: TemporalClimateDashboardPacket | Mapping[str, Any]) -> TemporalClimateValidationReport:
    p = packet if isinstance(packet, TemporalClimateDashboardPacket) else TemporalClimateDashboardPacket(**dict(packet))
    findings = []
    status = "PASS"
    if (not p.projection_only) or p.packet_authoritative or p.action_authorization_allowed or p.auto_transition_allowed or p.history_rewrite_allowed or p.ledger_mutation_allowed or p.timeline_collapse_allowed or p.canonical_selection_allowed or p.live_execution_allowed or p.routing_change_allowed:
        findings.append(TemporalClimateValidationFinding("FLAGS_FORBIDDEN", "error", "projection_only must be true and authority/action/mutation/collapse/selection/execution/routing flags must be false."))
        status = "BLOCKED"
    if not p.climate_summary.projection_only:
        findings.append(TemporalClimateValidationFinding("SUMMARY_PROJECTION_REQUIRED", "error", "climate_summary.projection_only must be true."))
        status = "BLOCKED"
    if any(not t.projection_only for t in p.status_tiles):
        findings.append(TemporalClimateValidationFinding("TILE_PROJECTION_REQUIRED", "error", "status_tiles[*].projection_only must be true."))
        status = "BLOCKED"
    if any(a.action_authorization_allowed for a in p.alerts):
        findings.append(TemporalClimateValidationFinding("ALERT_AUTH_FORBIDDEN", "error", "alerts[*].action_authorization_allowed must be false."))
        status = "BLOCKED"
    if any(not t.projection_only for t in p.trend_indicators):
        findings.append(TemporalClimateValidationFinding("TREND_PROJECTION_REQUIRED", "error", "trend_indicators[*].projection_only must be true."))
        status = "BLOCKED"
    if any(a.action_authorization_allowed or a.history_rewrite_allowed or a.ledger_mutation_allowed or a.timeline_collapse_allowed or a.canonical_selection_allowed or a.routing_change_allowed or a.live_execution_allowed for a in p.operator_actions):
        findings.append(TemporalClimateValidationFinding("ACTION_FLAGS_FORBIDDEN", "error", "operator actions cannot authorize/execute/mutate/collapse/select/route."))
        status = "BLOCKED"
    if p.packet_status == "CLIMATE_STABLE" and not (p.packet_posture == "STABLE" and not any(a.severity in {"WARN", "BLOCKED"} for a in p.alerts)):
        findings.append(TemporalClimateValidationFinding("CLIMATE_STABLE_CONSTRAINT", "error", "CLIMATE_STABLE requires STABLE posture and no WARN/BLOCKED alerts."))
        status = "BLOCKED"
    if p.packet_status == "CLIMATE_PRESSURE" and not any(x in {"PRESSURE_BUILDING", "PRESSURE"} for x in [a.alert_type for a in p.alerts] + [t.tile_type for t in p.status_tiles] + [t.trend_type for t in p.trend_indicators]):
        findings.append(TemporalClimateValidationFinding("CLIMATE_PRESSURE_CONSTRAINT", "error", "CLIMATE_PRESSURE requires pressure alert/tile/trend."))
        status = "BLOCKED"
    if p.packet_status == "CLIMATE_REGIME_RISK" and not any(x in {"REGIME_TRANSITION_RISK", "REGIME", "REGIME_TREND"} for x in [a.alert_type for a in p.alerts] + [t.tile_type for t in p.status_tiles] + [t.trend_type for t in p.trend_indicators]):
        findings.append(TemporalClimateValidationFinding("CLIMATE_REGIME_RISK_CONSTRAINT", "error", "CLIMATE_REGIME_RISK requires regime risk alert/tile/trend."))
        status = "BLOCKED"
    if p.packet_status == "CLIMATE_FRACTURE_RISK" and not any(x in {"FRACTURE_ESCALATION", "FRACTURE_TREND", "TOPOLOGY_HOTSPOT"} for x in [a.alert_type for a in p.alerts] + [t.trend_type for t in p.trend_indicators]):
        findings.append(TemporalClimateValidationFinding("CLIMATE_FRACTURE_RISK_CONSTRAINT", "error", "CLIMATE_FRACTURE_RISK requires fracture risk alert/tile/trend."))
        status = "BLOCKED"
    if p.packet_status == "CLIMATE_UNSTABLE" and not (p.packet_posture == "UNSTABLE" or any(a.severity == "BLOCKED" for a in p.alerts)):
        findings.append(TemporalClimateValidationFinding("CLIMATE_UNSTABLE_CONSTRAINT", "error", "CLIMATE_UNSTABLE requires UNSTABLE posture or BLOCKED alert."))
        status = "BLOCKED"
    if p.packet_status == "OPERATOR_REVIEW_REQUIRED" and not any(a.operator_review_required for a in p.operator_actions):
        findings.append(TemporalClimateValidationFinding("REVIEW_REQUIRED_MISSING", "error", "OPERATOR_REVIEW_REQUIRED requires an operator action with operator_review_required=true."))
        status = "BLOCKED"
    if p.created_by_lane == "PROJECTION" and (not p.projection_only or p.packet_authoritative):
        findings.append(TemporalClimateValidationFinding("PROJECTION_AUTH_BLOCKED", "error", "PROJECTION packets must remain projection_only and non-authoritative."))
        status = "BLOCKED"
    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "packet_id": p.packet_id}))
    return TemporalClimateValidationReport(status, tuple(findings), receipt_hash)
