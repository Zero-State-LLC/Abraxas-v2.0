"""Tests for MemeticFuturecastOperatorPacket.v0 (Track B)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from core.memetic.futurecast_operator_packet import (
    build_futurecast_operator_packet,
    build_futurecast_operator_packet_from_forecast,
)

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "contracts" / "memetic" / "futurecast_operator_packet.v0.schema.json"


def test_seeded_futurecast_packet_schema():
    pack = build_futurecast_operator_packet(
        forecast_id="fc_ase_001",
        topic="agent skill packaging patterns",
        selected_horizon="30d",
        probability=0.7,
        register="INFERRED",
        evidence_density=0.55,
        claim_text="Skill-OS packaging will remain a high-signal research topic.",
    )
    assert pack["schema_version"] == "MemeticFuturecastOperatorPacket.v0"
    assert pack["pipeline_id"] == "memetic_futurecast"
    assert pack["lane"] == "SHADOW_FORECAST_GATED"
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"
    assert pack["forecast_routing_blocked"] is True
    assert pack["authority"]["forecast_routing_authorized"] is False
    assert pack["horizon_policy"]["policy_status"] == "ALLOWED"
    assert pack["horizon_policy"]["horizon_days"] == 30
    assert pack["validation_gates"]["overall"] == "PASS"
    assert pack["brier_bridge"]["bridge_status"] == "BRIDGE_SEEDED"
    assert pack["brier_bridge"]["brier_ready"] is True
    assert pack["brier_bridge"]["ledger_hint"] == "BrierLedgerEntry.v1"
    assert pack["brier_bridge"]["provisional_brier"] is None
    assert len(pack["canonical_hash"]) == 64

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(pack)


def test_provisional_brier_when_outcome_present():
    pack = build_futurecast_operator_packet(
        forecast_id="fc_brier",
        topic="test claim",
        selected_horizon="7d",
        probability=0.8,
        register="INFERRED",
        evidence_density=0.5,
        outcome_value=1.0,
    )
    assert pack["brier_bridge"]["provisional_brier"] == 0.04
    assert pack["brier_bridge"]["bridge_status"] == "BRIDGE_SEEDED"


def test_disallowed_horizon_blocks():
    pack = build_futurecast_operator_packet(
        forecast_id="fc_bad_h",
        topic="x",
        selected_horizon="9999d",
        probability=0.5,
        register="INFERRED",
        evidence_density=0.5,
    )
    assert pack["horizon_policy"]["policy_status"] == "DISALLOWED"
    assert pack["readiness"] == "BLOCKED"
    assert "HORIZON_POLICY_DISALLOWED" in pack["blocked_by"]
    assert pack["brier_bridge"]["bridge_status"] == "BRIDGE_BLOCKED"


def test_unspecified_horizon_partial():
    pack = build_futurecast_operator_packet(
        forecast_id="fc_no_h",
        topic="y",
        selected_horizon="",
        probability=0.4,
        register="INFERRED",
        evidence_density=0.4,
    )
    assert pack["horizon_policy"]["policy_status"] == "UNSPECIFIED"
    assert pack["validation_gates"]["horizon_gate"] == "PARTIAL"
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"


def test_low_evidence_fails_gate():
    pack = build_futurecast_operator_packet(
        forecast_id="fc_low",
        topic="z",
        selected_horizon="14d",
        probability=0.6,
        register="INFERRED",
        evidence_density=0.05,
    )
    assert pack["validation_gates"]["evidence_gate"] == "FAIL"
    assert pack["validation_gates"]["overall"] == "FAIL"
    assert pack["readiness"] == "BLOCKED"


def test_deterministic():
    kwargs = dict(
        forecast_id="fc_det",
        topic="det topic",
        selected_horizon="90d",
        probability=0.33,
        register="SPECULATIVE",
        evidence_density=0.3,
    )
    a = build_futurecast_operator_packet(**kwargs)
    b = build_futurecast_operator_packet(**kwargs)
    assert a == b


def test_from_forecast_dict():
    forecast = {
        "forecast_id": "fc_dict",
        "topic": "memetic compression",
        "horizon": "30",
        "probability": 0.61,
        "register": "INFERRED",
        "evidence_density": 0.7,
    }
    pack = build_futurecast_operator_packet_from_forecast(forecast)
    assert pack["forecast_id"] == "fc_dict"
    assert pack["horizon_policy"]["selected_horizon"] == "30d"
    assert pack["horizon_policy"]["policy_status"] == "ALLOWED"
    assert pack["brier_bridge"]["probability"] == 0.61
