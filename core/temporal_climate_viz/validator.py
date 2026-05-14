from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import TemporalClimateAALVizProjectionBinding, TemporalClimateVizValidationFinding, TemporalClimateVizValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_temporal_climate_aal_viz_projection_binding(binding: TemporalClimateAALVizProjectionBinding | Mapping[str, Any]) -> TemporalClimateVizValidationReport:
    b = binding if isinstance(binding, TemporalClimateAALVizProjectionBinding) else TemporalClimateAALVizProjectionBinding(**dict(binding))
    findings = []
    status = "PASS"
    if (not b.projection_only) or b.binding_authoritative or b.inference_authority_allowed or b.action_authorization_allowed or b.auto_transition_allowed or b.history_rewrite_allowed or b.ledger_mutation_allowed or b.timeline_collapse_allowed or b.canonical_selection_allowed or b.live_execution_allowed or b.routing_change_allowed:
        findings.append(TemporalClimateVizValidationFinding("FLAGS_FORBIDDEN", "error", "projection_only must be true and authority/inference/action/transition/mutation/collapse/selection/execution/routing flags must be false."))
        status = "BLOCKED"
    if any((not p.projection_only) or p.inference_authority_allowed for p in b.panels):
        findings.append(TemporalClimateVizValidationFinding("PANEL_FLAGS_FORBIDDEN", "error", "panels must be projection_only and inference_authority_allowed=false."))
        status = "BLOCKED"
    if any((not w.projection_only) or w.action_authorization_allowed for w in b.widgets):
        findings.append(TemporalClimateVizValidationFinding("WIDGET_FLAGS_FORBIDDEN", "error", "widgets must be projection_only and action_authorization_allowed=false."))
        status = "BLOCKED"
    req = {"PROJECTION_ONLY", "NON_AUTHORITATIVE", "NO_EXECUTION", "NO_MUTATION", "NO_ROUTING"}
    have = {x.badge_type for x in b.badges if x.required}
    if not req.issubset(have):
        findings.append(TemporalClimateVizValidationFinding("REQUIRED_BADGES_MISSING", "error", "required governance badges missing."))
        status = "BLOCKED"
    if any(a.action_authorization_allowed for a in b.alert_surfaces):
        findings.append(TemporalClimateVizValidationFinding("ALERT_AUTH_FORBIDDEN", "error", "alert surfaces cannot authorize actions."))
        status = "BLOCKED"
    if any(h.action_authorization_allowed or h.live_execution_allowed or h.routing_change_allowed for h in b.interaction_hints):
        findings.append(TemporalClimateVizValidationFinding("HINT_FLAGS_FORBIDDEN", "error", "interaction hints cannot authorize/execute/route."))
        status = "BLOCKED"
    if b.binding_status == "VIZ_STABLE" and not (b.binding_posture == "STABLE" and not any(a.severity in {"WARN", "BLOCKED"} for a in b.alert_surfaces)):
        findings.append(TemporalClimateVizValidationFinding("VIZ_STABLE_CONSTRAINT", "error", "VIZ_STABLE requires STABLE posture and no WARN/BLOCKED alert surfaces."))
        status = "BLOCKED"
    if b.binding_status == "VIZ_PRESSURE" and not any(x in {"PRESSURE_SURFACE", "PRESSURE_GAUGE", "PRESSURE_BUILDING"} for x in [p.panel_type for p in b.panels] + [w.widget_type for w in b.widgets] + [a.alert_type for a in b.alert_surfaces]):
        findings.append(TemporalClimateVizValidationFinding("VIZ_PRESSURE_CONSTRAINT", "error", "VIZ_PRESSURE requires pressure panel/widget/alert."))
        status = "BLOCKED"
    if b.binding_status == "VIZ_REGIME_RISK" and not any(x in {"REGIME_STATE", "REGIME_BADGE", "REGIME_TRANSITION_RISK"} for x in [p.panel_type for p in b.panels] + [w.widget_type for w in b.widgets] + [a.alert_type for a in b.alert_surfaces]):
        findings.append(TemporalClimateVizValidationFinding("VIZ_REGIME_RISK_CONSTRAINT", "error", "VIZ_REGIME_RISK requires regime panel/widget/alert."))
        status = "BLOCKED"
    if b.binding_status == "VIZ_FRACTURE_RISK" and not any(x in {"FRACTURE_MARKER", "FRACTURE_ESCALATION"} for x in [w.widget_type for w in b.widgets] + [a.alert_type for a in b.alert_surfaces]):
        findings.append(TemporalClimateVizValidationFinding("VIZ_FRACTURE_RISK_CONSTRAINT", "error", "VIZ_FRACTURE_RISK requires fracture widget/alert."))
        status = "BLOCKED"
    if b.binding_status == "VIZ_UNSTABLE" and not (b.binding_posture == "UNSTABLE" or any(a.severity == "BLOCKED" for a in b.alert_surfaces)):
        findings.append(TemporalClimateVizValidationFinding("VIZ_UNSTABLE_CONSTRAINT", "error", "VIZ_UNSTABLE requires UNSTABLE posture or BLOCKED alert."))
        status = "BLOCKED"
    if b.binding_status == "OPERATOR_REVIEW_REQUIRED" and not any(h.operator_review_required for h in b.interaction_hints):
        findings.append(TemporalClimateVizValidationFinding("REVIEW_REQUIRED_MISSING", "error", "OPERATOR_REVIEW_REQUIRED requires interaction hint with operator_review_required=true."))
        status = "BLOCKED"
    if b.created_by_lane == "PROJECTION" and ((not b.projection_only) or b.binding_authoritative):
        findings.append(TemporalClimateVizValidationFinding("PROJECTION_AUTH_BLOCKED", "error", "PROJECTION bindings must remain projection_only and non-authoritative."))
        status = "BLOCKED"
    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "binding_id": b.binding_id}))
    return TemporalClimateVizValidationReport(status, tuple(findings), receipt_hash)
