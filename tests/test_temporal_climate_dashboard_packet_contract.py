import hashlib
import json
from dataclasses import asdict, replace

from core.temporal_climate_dashboard.models import TemporalClimateAlert
from core.temporal_climate_dashboard.packet import canonical_temporal_climate_dashboard_packet_json, derive_temporal_climate_dashboard_packet, temporal_climate_dashboard_packet_hash, write_temporal_climate_dashboard_packet_contract_audit
from core.temporal_climate_dashboard.validator import validate_temporal_climate_dashboard_packet


def _regime(state="CALM"):
    return {"current_regime_state": {"state_type": state}}


def _pressure(status="LOW_PRESSURE", vectors=()):
    return {"forecast_status": status, "pressure_vectors": vectors}


def _topology(status="TOPOLOGY_STABLE", hotspots=()):
    return {"topology_status": status, "pressure_hotspots": hotspots}


def _continuity(status="CONTINUITY_STABLE", findings=()):
    return {"index_status": status, "findings": findings}


def test_climate_packet_derivation_rules():
    assert derive_temporal_climate_dashboard_packet([]).packet_status in {"NOT_COMPUTABLE", "INSUFFICIENT_TEMPORAL_INPUTS"}
    stable = derive_temporal_climate_dashboard_packet([_regime("CALM")], [_pressure("LOW_PRESSURE")], [_topology()], [_continuity()])
    assert stable.packet_status == "CLIMATE_STABLE"
    watch = derive_temporal_climate_dashboard_packet([_regime("WATCH")], [_pressure("PRESSURE_BUILDING")], [_topology("PRESSURE_HOTSPOTS_PRESENT")], [_continuity("CONTINUITY_MIXED")])
    assert watch.packet_status in {"CLIMATE_WATCH", "CLIMATE_PRESSURE", "OPERATOR_REVIEW_REQUIRED"}
    regime = derive_temporal_climate_dashboard_packet([_regime("REGIME_RISK")], [_pressure("REGIME_TRANSITION_RISK")], [_topology()], [_continuity()])
    assert regime.packet_status == "CLIMATE_REGIME_RISK"
    fracture = derive_temporal_climate_dashboard_packet([_regime("FRACTURE_RISK")], [_pressure("FRACTURE_ESCALATION_RISK")], [_topology()], [_continuity()])
    assert fracture.packet_status == "CLIMATE_FRACTURE_RISK"
    unstable = derive_temporal_climate_dashboard_packet([_regime("UNSTABLE")], [_pressure("OPERATOR_REVIEW_REQUIRED")], [_topology()], [_continuity()])
    assert unstable.packet_status in {"CLIMATE_UNSTABLE", "OPERATOR_REVIEW_REQUIRED"}
    blocked = derive_temporal_climate_dashboard_packet([_regime("WATCH")], [_pressure("PRESSURE_BUILDING", ({"vector_type": "BLOCKED_PRESSURE"},))], [_topology("PRESSURE_HOTSPOTS_PRESENT", ({"hotspot_type": "BLOCKED_PRESSURE"},))], [_continuity("CONTINUITY_MIXED", ({"finding_type": "BLOCKED_HISTORY_PRESSURE"},))])
    assert any(t.tile_type == "BLOCKED_HISTORY" for t in blocked.status_tiles) and any(a.alert_type == "BLOCKED_HISTORY_PRESENT" for a in blocked.alerts)
    nondet = derive_temporal_climate_dashboard_packet([_regime("WATCH")], [_pressure("PRESSURE_BUILDING", ({"vector_type": "NONDETERMINISM_PRESSURE"},))], [_topology("PRESSURE_HOTSPOTS_PRESENT", ({"hotspot_type": "NONDETERMINISM_PRESSURE"},))], [_continuity("CONTINUITY_MIXED", ({"finding_type": "NONDETERMINISM_PRESSURE"},))])
    assert any(t.tile_type == "NONDETERMINISM" for t in nondet.status_tiles) and any(a.alert_type == "NONDETERMINISM_PRESENT" for a in nondet.alerts)


def test_climate_packet_validator_hash_schema_and_audit():
    base = derive_temporal_climate_dashboard_packet([_regime("CALM")], [_pressure("LOW_PRESSURE")], [_topology()], [_continuity()])
    assert validate_temporal_climate_dashboard_packet(replace(base, projection_only=False)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_dashboard_packet(replace(base, packet_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_dashboard_packet(replace(base, action_authorization_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_dashboard_packet(replace(base, auto_transition_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_dashboard_packet(replace(base, history_rewrite_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_dashboard_packet(replace(base, ledger_mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_dashboard_packet(replace(base, timeline_collapse_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_dashboard_packet(replace(base, canonical_selection_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_dashboard_packet(replace(base, live_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_dashboard_packet(replace(base, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bs = replace(base, climate_summary=replace(base.climate_summary, projection_only=False))
    assert validate_temporal_climate_dashboard_packet(bs).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bt = replace(base, status_tiles=(replace(base.status_tiles[0], projection_only=False),) + base.status_tiles[1:])
    assert validate_temporal_climate_dashboard_packet(bt).status in {"BLOCKED", "NOT_COMPUTABLE"}
    ba = replace(base, alerts=(TemporalClimateAlert("a", "PRESSURE_BUILDING", "WATCH", "x", tuple(), True, True),))
    assert validate_temporal_climate_dashboard_packet(ba).status in {"BLOCKED", "NOT_COMPUTABLE"}
    btr = replace(base, trend_indicators=(replace(base.trend_indicators[0], projection_only=False),) + base.trend_indicators[1:])
    assert validate_temporal_climate_dashboard_packet(btr).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bo = replace(base, operator_actions=(replace(base.operator_actions[0], live_execution_allowed=True),))
    assert validate_temporal_climate_dashboard_packet(bo).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_climate_dashboard_packet(replace(base, created_by_lane="PROJECTION", packet_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(base))
    alt["packet_hash"] = "x"
    assert temporal_climate_dashboard_packet_hash(base) == temporal_climate_dashboard_packet_hash(alt)
    assert canonical_temporal_climate_dashboard_packet_json(base) == canonical_temporal_climate_dashboard_packet_json(base)
    s = json.loads(open("contracts/temporal_climate_dashboard/temporal_climate_dashboard_packet.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(base).keys()))
    d = dict(asdict(base))
    d.pop("packet_id")
    assert "packet_id" in s["required"] and "packet_id" not in d

    h = write_temporal_climate_dashboard_packet_contract_audit(".")
    t = open("out/audit/temporal_climate_dashboard_packet_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
