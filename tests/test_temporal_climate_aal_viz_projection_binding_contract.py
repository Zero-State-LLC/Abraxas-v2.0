import hashlib
import json
from dataclasses import asdict, replace

from core.temporal_climate_viz import *


def _packet(status="CLIMATE_STABLE", posture="STABLE", alerts=(), tiles=(), trends=(), summary=None):
    return {
        "packet_status": status,
        "packet_posture": posture,
        "climate_summary": summary or {"regime_state": "CALM", "pressure_state": "LOW_PRESSURE"},
        "alerts": alerts,
        "status_tiles": tiles,
        "trend_indicators": trends,
    }


def test_viz_binding_derivation_rules():
    assert derive_temporal_climate_aal_viz_projection_binding([]).binding_status in {"NOT_COMPUTABLE", "INSUFFICIENT_DASHBOARD_INPUTS"}
    stable = derive_temporal_climate_aal_viz_projection_binding([_packet()])
    assert stable.binding_status == "VIZ_STABLE"
    watch = derive_temporal_climate_aal_viz_projection_binding([_packet("CLIMATE_WATCH", "WATCH", alerts=({"alert_type": "PRESSURE_BUILDING", "severity": "WATCH", "affected_ref_ids": (), "operator_review_required": True},))])
    assert watch.binding_status in {"VIZ_WATCH", "VIZ_PRESSURE", "OPERATOR_REVIEW_REQUIRED"}
    regime = derive_temporal_climate_aal_viz_projection_binding([_packet("CLIMATE_REGIME_RISK", "REGIME_RISK", alerts=({"alert_type": "REGIME_TRANSITION_RISK", "severity": "WARN", "affected_ref_ids": (), "operator_review_required": True},), summary={"regime_state": "REGIME_RISK", "pressure_state": "REGIME_TRANSITION_RISK"})])
    assert regime.binding_status == "VIZ_REGIME_RISK"
    fracture = derive_temporal_climate_aal_viz_projection_binding([_packet("CLIMATE_FRACTURE_RISK", "FRACTURE_RISK", alerts=({"alert_type": "FRACTURE_ESCALATION", "severity": "WARN", "affected_ref_ids": (), "operator_review_required": True},), summary={"regime_state": "FRACTURE_RISK", "pressure_state": "FRACTURE_ESCALATION_RISK"})])
    assert fracture.binding_status == "VIZ_FRACTURE_RISK"
    unstable = derive_temporal_climate_aal_viz_projection_binding([_packet("CLIMATE_UNSTABLE", "UNSTABLE", alerts=({"alert_type": "BLOCKED_HISTORY_PRESENT", "severity": "BLOCKED", "affected_ref_ids": (), "operator_review_required": True},))])
    assert unstable.binding_status in {"VIZ_UNSTABLE", "OPERATOR_REVIEW_REQUIRED"}
    blocked = derive_temporal_climate_aal_viz_projection_binding([_packet("OPERATOR_REVIEW_REQUIRED", "UNSTABLE", alerts=({"alert_type": "BLOCKED_HISTORY_PRESENT", "severity": "BLOCKED", "affected_ref_ids": (), "operator_review_required": True},), tiles=({"tile_type": "BLOCKED_HISTORY", "tile_label": "Blocked", "tile_value": "VISIBLE", "tile_posture": "BLOCKED", "source_ref_ids": ()},))])
    assert any(w.widget_label == "Blocked" or w.widget_label == "Blocked History" for w in blocked.widgets)
    nondet = derive_temporal_climate_aal_viz_projection_binding([_packet("OPERATOR_REVIEW_REQUIRED", "UNSTABLE", alerts=({"alert_type": "NONDETERMINISM_PRESENT", "severity": "BLOCKED", "affected_ref_ids": (), "operator_review_required": True},), tiles=({"tile_type": "NONDETERMINISM", "tile_label": "Nondeterminism", "tile_value": "VISIBLE", "tile_posture": "BLOCKED", "source_ref_ids": ()},))])
    assert any("Nondeterminism" in w.widget_label for w in nondet.widgets)


def test_viz_binding_validation_hash_schema_and_audit():
    base = derive_temporal_climate_aal_viz_projection_binding([_packet(tiles=({"tile_type":"PRESSURE","tile_label":"Pressure","tile_value":"LOW","tile_posture":"PASS","source_ref_ids":()},), trends=({"trend_type":"PRESSURE_TREND","trend_direction":"STABLE","source_ref_ids":()},))])
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, projection_only=False)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, binding_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, inference_authority_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, action_authorization_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, auto_transition_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, history_rewrite_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, ledger_mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, timeline_collapse_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, canonical_selection_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, live_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bp = replace(base, panels=(replace(base.panels[0], projection_only=False),) + base.panels[1:])
    assert validate_temporal_climate_aal_viz_projection_binding(bp).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bw = replace(base, widgets=(replace(base.widgets[0], action_authorization_allowed=True),) + base.widgets[1:])
    assert validate_temporal_climate_aal_viz_projection_binding(bw).status in {"BLOCKED", "NOT_COMPUTABLE"}
    ba = replace(base, alert_surfaces=(replace(base.alert_surfaces[0], action_authorization_allowed=True),) if base.alert_surfaces else (TemporalClimateVizAlertSurface("a","INSUFFICIENT_INPUTS","WARN",1,tuple(),True,True),))
    assert validate_temporal_climate_aal_viz_projection_binding(ba).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bh = replace(base, interaction_hints=(replace(base.interaction_hints[0], live_execution_allowed=True),))
    assert validate_temporal_climate_aal_viz_projection_binding(bh).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_aal_viz_projection_binding(replace(base, created_by_lane="PROJECTION", binding_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(base)); alt["binding_hash"] = "x"
    assert temporal_climate_aal_viz_projection_binding_hash(base) == temporal_climate_aal_viz_projection_binding_hash(alt)
    assert canonical_temporal_climate_aal_viz_projection_binding_json(base) == canonical_temporal_climate_aal_viz_projection_binding_json(base)
    s = json.loads(open("contracts/temporal_climate_viz/temporal_climate_aal_viz_projection_binding.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(base).keys()))
    d = dict(asdict(base)); d.pop("binding_id")
    assert "binding_id" in s["required"] and "binding_id" not in d

    h = write_temporal_climate_aal_viz_projection_binding_contract_audit(".")
    t = open("out/audit/temporal_climate_aal_viz_projection_binding_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
