"""Tests for HollerSportsTicketOperatorPacket.v0 (Track B)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from core.holler.ticket_operator_packet import (
    build_ticket_operator_packet,
    build_ticket_operator_packet_from_ticket,
)

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "contracts" / "holler" / "ticket_operator_packet.v0.schema.json"


def test_seeded_ticket_operator_packet_schema():
    pack = build_ticket_operator_packet(
        ticket_id="t_nba_001",
        sport="NBA",
        event_ref="nba:2026-07-31:LAL-BOS",
        market_class="moneyline",
        model_ref="holler_shadow_v0",
        probability=0.62,
        register="INFERRED",
        expected_outcome="home_win",
    )
    assert pack["schema_version"] == "HollerSportsTicketOperatorPacket.v0"
    assert pack["pipeline_id"] == "hollersports_ticket"
    assert pack["lane"] == "FORECAST_GATED"
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"
    assert pack["forecast_routing_blocked"] is True
    assert pack["live_odds_execution_blocked"] is True
    assert pack["authority"]["forecast_routing_authorized"] is False
    assert pack["authority"]["execution_authority"] is False
    assert pack["forecast_proof"]["proof_status"] == "PROOF_SEEDED"
    assert pack["forecast_proof"]["brier_ready"] is True
    assert pack["outcome_binding"]["binding_status"] == "unresolved"
    assert pack["outcome_binding"]["forecast_outcome_binding_hint"] == (
        "ForecastOutcomeBindingPacket.v1"
    )
    assert len(pack["canonical_hash"]) == 64

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(pack)


def test_missing_event_not_computable():
    pack = build_ticket_operator_packet(
        ticket_id="t_x",
        sport="NBA",
        event_ref="",
        probability=0.5,
        register="INFERRED",
    )
    assert pack["readiness"] == "NOT_COMPUTABLE"
    assert pack["forecast_proof"]["proof_status"] == "NOT_COMPUTABLE"
    assert "MISSING_EVENT_REF" in pack["blocked_by"]


def test_incomplete_proof():
    pack = build_ticket_operator_packet(
        ticket_id="t_y",
        sport="NFL",
        event_ref="nfl:g1",
        probability=None,
        register="NOT_COMPUTABLE",
    )
    assert pack["forecast_proof"]["proof_status"] == "PROOF_INCOMPLETE"
    assert pack["forecast_proof"]["brier_ready"] is False
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"
    assert "FORECAST_PROOF_INCOMPLETE" in pack["blocked_by"]


def test_matched_outcome_binding():
    pack = build_ticket_operator_packet(
        ticket_id="t_z",
        sport="NBA",
        event_ref="nba:g2",
        market_class="spread",
        probability=0.55,
        register="INFERRED",
        expected_outcome="cover",
        observed_outcome="cover",
    )
    assert pack["outcome_binding"]["binding_status"] == "matched"
    assert pack["outcome_binding"]["observed_outcome_hash"] == pack["outcome_binding"][
        "expected_outcome_hash"
    ]


def test_deterministic():
    kwargs = dict(
        ticket_id="t_det",
        sport="MLB",
        event_ref="mlb:g9",
        market_class="total",
        probability=0.48,
        register="SPECULATIVE",
        expected_outcome="over",
    )
    a = build_ticket_operator_packet(**kwargs)
    b = build_ticket_operator_packet(**kwargs)
    assert a == b


def test_from_ticket_dict():
    ticket = {
        "ticket_id": "t_dict",
        "sport": "NHL",
        "event_id": "nhl:g3",
        "market": "moneyline",
        "forecast": {"probability": 0.51, "register": "INFERRED", "model_ref": "m1"},
        "expected_outcome": "away_win",
    }
    pack = build_ticket_operator_packet_from_ticket(ticket)
    assert pack["ticket_id"] == "t_dict"
    assert pack["event_ref"] == "nhl:g3"
    assert pack["forecast_proof"]["probability"] == 0.51
    assert pack["forecast_proof"]["proof_status"] == "PROOF_SEEDED"
