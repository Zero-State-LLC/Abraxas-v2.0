"""Holler ticket → outcome binding dry-run (no binding write)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from abraxas.cli import main
from core.holler.outcome_binding_dry_run import (
    build_holler_outcome_binding_dry_run,
    build_outcome_binding_dry_run_from_ticket,
)
from core.holler.ticket_operator_packet import build_ticket_operator_packet

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "contracts" / "holler" / "outcome_binding_dry_run.v0.schema.json"


def test_unresolved_binding_dry_run():
    pack = build_ticket_operator_packet(
        ticket_id="t_nba_001",
        sport="NBA",
        event_ref="nba:2026-07-31:LAL-BOS",
        market_class="moneyline",
        probability=0.62,
        register="INFERRED",
        expected_outcome="home_win",
    )
    dry = build_holler_outcome_binding_dry_run(pack)
    assert dry["schema_version"] == "HollerOutcomeBindingDryRun.v0"
    assert dry["dry_run"] is True
    assert dry["binding_write_performed"] is False
    assert dry["binding_write_authorized"] is False
    assert dry["projection_status"] == "UNRESOLVED"
    entry = dry["projected_binding"]
    assert entry["schema_version"] == "ForecastOutcomeBindingPacket.v1"
    assert entry["status"] == "dry_run_awaiting_outcome"
    assert entry["authority"]["forecast_weight_allowed"] is False
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(dry)


def test_matched_binding_dry_run():
    dry = build_outcome_binding_dry_run_from_ticket(
        {
            "ticket_id": "t_z",
            "sport": "NBA",
            "event_ref": "nba:g1",
            "market_class": "spread",
            "probability": 0.55,
            "register": "INFERRED",
            "expected_outcome": "home_cover",
            "observed_outcome": "home_cover",
        }
    )
    assert dry["projection_status"] == "MATCHED"
    assert dry["projected_binding"]["binding_status"] == "matched"
    assert dry["binding_write_performed"] is False


def test_mismatched_binding_dry_run():
    pack = build_ticket_operator_packet(
        ticket_id="t_m",
        sport="NBA",
        event_ref="nba:g2",
        probability=0.5,
        register="INFERRED",
        expected_outcome="home_win",
        observed_outcome="away_win",
    )
    dry = build_holler_outcome_binding_dry_run(pack)
    assert dry["projection_status"] == "MISMATCHED"


def test_missing_event_blocked():
    pack = build_ticket_operator_packet(
        ticket_id="t_x",
        sport="NBA",
        event_ref="",
        probability=0.5,
        register="INFERRED",
    )
    dry = build_holler_outcome_binding_dry_run(pack)
    assert dry["projection_status"] == "BLOCKED"
    assert dry["source_readiness"] == "NOT_COMPUTABLE"


def test_dry_run_deterministic():
    ticket = {
        "ticket_id": "t_det",
        "sport": "NFL",
        "event_ref": "nfl:g9",
        "probability": 0.7,
        "register": "INFERRED",
        "expected_outcome": "over",
        "observed_outcome": "over",
    }
    assert build_outcome_binding_dry_run_from_ticket(
        ticket
    ) == build_outcome_binding_dry_run_from_ticket(ticket)


def test_cli_os_holler_outcome_dry_run(capsys):
    code = main(
        [
            "os",
            "holler-outcome-dry-run",
            "--ticket-id",
            "t_cli",
            "--sport",
            "NBA",
            "--event-ref",
            "nba:cli",
            "--probability",
            "0.6",
            "--expected-outcome",
            "home_win",
            "--observed-outcome",
            "home_win",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["binding_write_performed"] is False
    assert payload["projection_status"] == "MATCHED"
