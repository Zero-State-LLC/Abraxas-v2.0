"""Memetic futurecast → Brier ledger dry-run (no ledger write)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from abraxas.cli import main
from core.memetic.brier_ledger_dry_run import (
    build_brier_ledger_dry_run_from_forecast,
    build_memetic_brier_ledger_dry_run,
)
from core.memetic.futurecast_operator_packet import build_futurecast_operator_packet

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "contracts" / "memetic" / "brier_ledger_dry_run.v0.schema.json"


def test_dry_run_projected_with_outcome():
    pack = build_futurecast_operator_packet(
        forecast_id="fc_brier",
        topic="test claim",
        selected_horizon="7d",
        probability=0.8,
        register="INFERRED",
        evidence_density=0.5,
        outcome_value=1.0,
    )
    dry = build_memetic_brier_ledger_dry_run(pack)
    assert dry["schema_version"] == "MemeticBrierLedgerDryRun.v0"
    assert dry["dry_run"] is True
    assert dry["ledger_write_performed"] is False
    assert dry["ledger_write_authorized"] is False
    assert dry["target_ledger_path"] == "out/brier"
    assert dry["projection_status"] == "PROJECTED"
    entry = dry["projected_ledger_entry"]
    assert entry["schema_version"] == "BrierLedgerEntry.v1"
    assert entry["projection_status"] == "PROJECTED"
    assert entry["brier_score"] == 0.04
    assert entry["ledger_entry_id"]
    assert entry["deterministic_ledger_hash"]
    assert entry["status"] == "dry_run_projected"
    assert entry["authority"]["forecast_weight_allowed"] is False
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(dry)


def test_dry_run_seeded_awaiting_outcome():
    pack = build_futurecast_operator_packet(
        forecast_id="fc_ase_001",
        topic="agent skill packaging patterns",
        selected_horizon="30d",
        probability=0.7,
        register="INFERRED",
        evidence_density=0.55,
    )
    dry = build_memetic_brier_ledger_dry_run(pack)
    assert dry["projection_status"] == "SEEDED_AWAITING_OUTCOME"
    assert dry["projected_ledger_entry"]["ledger_entry_id"] is None
    assert dry["ledger_write_performed"] is False


def test_dry_run_blocked_horizon():
    pack = build_futurecast_operator_packet(
        forecast_id="fc_bad",
        topic="x",
        selected_horizon="9999d",
        probability=0.5,
        register="INFERRED",
        evidence_density=0.5,
        outcome_value=1.0,
    )
    dry = build_memetic_brier_ledger_dry_run(pack)
    assert dry["projection_status"] == "BLOCKED"
    assert dry["projected_ledger_entry"]["status"] == "dry_run_blocked"


def test_dry_run_deterministic():
    forecast = {
        "forecast_id": "fc_det",
        "topic": "determinism",
        "horizon": "14d",
        "probability": 0.6,
        "register": "INFERRED",
        "evidence_density": 0.5,
        "outcome_value": 0.0,
    }
    a = build_brier_ledger_dry_run_from_forecast(forecast)
    b = build_brier_ledger_dry_run_from_forecast(forecast)
    assert a == b
    assert a["projection_status"] == "PROJECTED"


def test_dry_run_never_writes_ledger(tmp_path: Path):
    before = list((REPO / "out" / "brier").glob("*")) if (REPO / "out" / "brier").is_dir() else []
    dry = build_brier_ledger_dry_run_from_forecast(
        {
            "forecast_id": "fc_w",
            "topic": "no write",
            "horizon": "7d",
            "probability": 0.5,
            "register": "INFERRED",
            "evidence_density": 0.5,
            "outcome_value": 1.0,
        }
    )
    after = list((REPO / "out" / "brier").glob("*")) if (REPO / "out" / "brier").is_dir() else []
    assert dry["ledger_write_performed"] is False
    assert before == after
    assert not (tmp_path / "brier").exists()


def test_cli_os_memetic_brier_dry_run(capsys):
    code = main(
        [
            "os",
            "memetic-brier-dry-run",
            "--forecast-id",
            "fc_cli",
            "--topic",
            "cli topic",
            "--horizon",
            "7d",
            "--probability",
            "0.75",
            "--outcome",
            "1.0",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["ledger_write_performed"] is False
    assert payload["projection_status"] == "PROJECTED"
