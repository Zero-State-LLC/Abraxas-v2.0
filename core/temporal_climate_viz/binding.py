from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import TemporalClimateVizInputRef, TemporalClimateVizPanel, TemporalClimateVizWidget, TemporalClimateVizBadge, TemporalClimateVizAlertSurface, TemporalClimateVizInteractionHint, TemporalClimateAALVizProjectionBinding
from .validator import validate_temporal_climate_aal_viz_projection_binding

SCHEMA_VERSION = "TemporalClimateAALVizProjectionBinding.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_temporal_climate_aal_viz_projection_binding_json(binding: TemporalClimateAALVizProjectionBinding | Mapping[str, Any]) -> str:
    payload = asdict(binding) if isinstance(binding, TemporalClimateAALVizProjectionBinding) else dict(binding)
    payload.pop("binding_hash", None)
    return _canonical_json(payload)


def temporal_climate_aal_viz_projection_binding_hash(binding: TemporalClimateAALVizProjectionBinding | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_temporal_climate_aal_viz_projection_binding_json(binding))


def compute_temporal_climate_viz_binding_posture(panels: Sequence[Mapping[str, Any]], widgets: Sequence[Mapping[str, Any]], alert_surfaces: Sequence[Mapping[str, Any]]) -> str:
    if any(a.get("severity") == "BLOCKED" for a in alert_surfaces):
        return "UNSTABLE"
    if any(a.get("alert_type") in {"FRACTURE_ESCALATION"} for a in alert_surfaces):
        return "FRACTURE_RISK"
    if any(a.get("alert_type") in {"REGIME_TRANSITION_RISK"} for a in alert_surfaces):
        return "REGIME_RISK"
    if any(a.get("alert_type") in {"PRESSURE_BUILDING"} for a in alert_surfaces):
        return "PRESSURE"
    if any(p.get("panel_posture") == "WATCH" for p in panels) or any(w.get("widget_posture") == "WATCH" for w in widgets):
        return "WATCH"
    return "STABLE" if panels or widgets else "INSUFFICIENT_INPUTS"


def build_temporal_climate_aal_viz_projection_binding(binding_id: str, input_refs: tuple[TemporalClimateVizInputRef, ...], panels: tuple[TemporalClimateVizPanel, ...], widgets: tuple[TemporalClimateVizWidget, ...], badges: tuple[TemporalClimateVizBadge, ...], alert_surfaces: tuple[TemporalClimateVizAlertSurface, ...], interaction_hints: tuple[TemporalClimateVizInteractionHint, ...], binding_status: str, binding_posture: str, binding_policy: str, created_by_lane: str, authority_ref: dict | None) -> TemporalClimateAALVizProjectionBinding:
    draft = TemporalClimateAALVizProjectionBinding(SCHEMA_VERSION, binding_id, input_refs, panels, widgets, badges, alert_surfaces, interaction_hints, binding_status, binding_posture, binding_policy, created_by_lane, authority_ref, True, False, False, False, False, False, False, False, False, False, False, "PENDING")
    return replace(draft, binding_hash=temporal_climate_aal_viz_projection_binding_hash(draft))


def derive_temporal_climate_aal_viz_projection_binding(dashboard_packets: Sequence[Mapping[str, Any]], input_refs: Sequence[Mapping[str, Any]] | None = None) -> TemporalClimateAALVizProjectionBinding:
    refs = tuple(TemporalClimateVizInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    badges = (
        TemporalClimateVizBadge("b-proj", "PROJECTION_ONLY", "Projection Only", "PASS", True),
        TemporalClimateVizBadge("b-na", "NON_AUTHORITATIVE", "Non Authoritative", "PASS", True),
        TemporalClimateVizBadge("b-noexec", "NO_EXECUTION", "No Execution", "PASS", True),
        TemporalClimateVizBadge("b-nomut", "NO_MUTATION", "No Mutation", "PASS", True),
        TemporalClimateVizBadge("b-noroute", "NO_ROUTING", "No Routing", "PASS", True),
    )
    if not dashboard_packets:
        return build_temporal_climate_aal_viz_projection_binding("binding-1", refs, tuple(), tuple(), badges, (TemporalClimateVizAlertSurface("a-ins", "INSUFFICIENT_INPUTS", "WARN", 1, tuple(), True, False),), (TemporalClimateVizInteractionHint("h-1", "REQUEST_OPERATOR_REVIEW", "No dashboard packet available.", True, False, False, False),), "NOT_COMPUTABLE", "NOT_COMPUTABLE", "PROJECTION_ONLY", "PROJECTION", None)

    p = dashboard_packets[-1]
    summary = p.get("climate_summary", {})
    status = str(p.get("packet_status", "NOT_COMPUTABLE"))
    posture = str(p.get("packet_posture", "NOT_COMPUTABLE"))

    panels = (
        TemporalClimateVizPanel("p-sum", "CLIMATE_SUMMARY", "Climate Summary", "BLOCKED" if posture == "UNSTABLE" else "WARN" if posture in {"REGIME_RISK", "FRACTURE_RISK", "PRESSURE"} else "WATCH" if posture == "WATCH" else "PASS", tuple(), True, False),
        TemporalClimateVizPanel("p-reg", "REGIME_STATE", "Regime State", "WARN" if summary.get("regime_state") in {"REGIME_RISK", "FRACTURE_RISK"} else "BLOCKED" if summary.get("regime_state") == "UNSTABLE" else "PASS", tuple(), True, False),
        TemporalClimateVizPanel("p-prs", "PRESSURE_SURFACE", "Pressure Surface", "WATCH" if summary.get("pressure_state") in {"PRESSURE_BUILDING", "PRESSURE_WAVE_DETECTED"} else "WARN" if summary.get("pressure_state") in {"REGIME_TRANSITION_RISK", "FRACTURE_ESCALATION_RISK"} else "PASS", tuple(), True, False),
    )
    widgets = []
    for i, t in enumerate(p.get("status_tiles", ()), start=1):
        tv = str(t.get("tile_type", "NOT_COMPUTABLE"))
        tp = str(t.get("tile_posture", "NOT_COMPUTABLE"))
        wtype = "STATUS_TILE" if tv not in {"BLOCKED_HISTORY", "NONDETERMINISM"} else "HOTSPOT_MARKER"
        widgets.append(TemporalClimateVizWidget(f"w-{i}", wtype, str(t.get("tile_label", tv)), str(t.get("tile_value", "")), tp if tp in {"PASS", "WATCH", "WARN", "BLOCKED", "NOT_COMPUTABLE"} else "NOT_COMPUTABLE", tuple(t.get("source_ref_ids", ())), True, False))
    for tr in p.get("trend_indicators", ()):
        widgets.append(TemporalClimateVizWidget(f"w-tr-{len(widgets)+1}", "TREND_INDICATOR", str(tr.get("trend_type", "TREND")), str(tr.get("trend_direction", "")), "WATCH" if tr.get("trend_direction") in {"WORSENING", "VOLATILE"} else "PASS", tuple(tr.get("source_ref_ids", ())), True, False))

    alerts = []
    for i, a in enumerate(p.get("alerts", ()), start=1):
        alerts.append(TemporalClimateVizAlertSurface(f"as-{i}", str(a.get("alert_type", "NOT_COMPUTABLE")), str(a.get("severity", "NOT_COMPUTABLE")), i, tuple(a.get("affected_ref_ids", ())), bool(a.get("operator_review_required", False)), False))

    blocked_visible = any(a.alert_type == "BLOCKED_HISTORY_PRESENT" for a in alerts)
    nondet_visible = any(a.alert_type == "NONDETERMINISM_PRESENT" for a in alerts)
    if blocked_visible:
        widgets.append(TemporalClimateVizWidget(f"w-b-{len(widgets)+1}", "HOTSPOT_MARKER", "Blocked History", "VISIBLE", "BLOCKED", tuple(), True, False))
    if nondet_visible:
        widgets.append(TemporalClimateVizWidget(f"w-n-{len(widgets)+1}", "HOTSPOT_MARKER", "Nondeterminism", "VISIBLE", "BLOCKED", tuple(), True, False))

    hints = (TemporalClimateVizInteractionHint("h-review", "REQUEST_OPERATOR_REVIEW" if status in {"CLIMATE_UNSTABLE", "OPERATOR_REVIEW_REQUIRED"} else "REVIEW_ONLY", "Projection-only interaction hint.", True, False, False, False),)

    bpost = compute_temporal_climate_viz_binding_posture([asdict(x) for x in panels], [asdict(x) for x in widgets], [asdict(x) for x in alerts])
    if bpost == "UNSTABLE":
        bstatus = "OPERATOR_REVIEW_REQUIRED" if any(h.operator_review_required for h in hints) else "VIZ_UNSTABLE"
    elif bpost == "FRACTURE_RISK":
        bstatus = "VIZ_FRACTURE_RISK"
    elif bpost == "REGIME_RISK":
        bstatus = "VIZ_REGIME_RISK"
    elif bpost == "PRESSURE":
        bstatus = "VIZ_PRESSURE"
    elif bpost == "WATCH":
        bstatus = "VIZ_WATCH"
    else:
        bstatus = "VIZ_STABLE"

    return build_temporal_climate_aal_viz_projection_binding("binding-1", refs, panels, tuple(widgets), badges, tuple(alerts), hints, bstatus, bpost, "PROJECTION_ONLY", "PROJECTION", None)


def write_temporal_climate_aal_viz_projection_binding_contract_audit(base_dir: Path | str = ".") -> str:
    b = derive_temporal_climate_aal_viz_projection_binding([
        {"packet_status": "CLIMATE_PRESSURE", "packet_posture": "PRESSURE", "climate_summary": {"regime_state": "WATCH", "pressure_state": "PRESSURE_BUILDING"}, "status_tiles": ({"tile_type": "PRESSURE", "tile_label": "Pressure", "tile_value": "PRESSURE_BUILDING", "tile_posture": "WATCH", "source_ref_ids": ()},), "trend_indicators": ({"trend_type": "PRESSURE_TREND", "trend_direction": "WORSENING", "source_ref_ids": ()},), "alerts": ({"alert_type": "PRESSURE_BUILDING", "severity": "WATCH", "affected_ref_ids": (), "operator_review_required": True},)}
    ], [{"source_type": "TEMPORAL_CLIMATE_DASHBOARD_PACKET", "source_id": "p1", "source_hash": "h1"}])
    report = validate_temporal_climate_aal_viz_projection_binding(b)
    payload = {"status": report.status, "binding_hash": b.binding_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": b.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/temporal_climate_aal_viz_projection_binding_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
