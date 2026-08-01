"""Tests for AI OS Slice C: spine touchpoint + CLI os/forage commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from abraxas.cli import main
from core.ingest.familiar_ingestion_receipt import (
    build_familiar_ingestion_receipt_from_path,
)
from core.signal.spine_bridge import (
    build_ai_os_kernel_status,
    build_familiar_spine_touchpoint,
    build_touchpoint_from_pack_path,
)

REPO = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO
    / "skills"
    / "abx-familiar-signal-forager"
    / "fixtures"
    / "evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)
TOUCH_SCHEMA = (
    REPO / "contracts" / "signal" / "familiar_spine_touchpoint.v0.schema.json"
)


def test_kernel_status_active_shadow():
    status = build_ai_os_kernel_status(REPO)
    assert status["ai_os_kernel"] == "ACTIVE_SHADOW"
    assert status["external_production_authorized"] is False
    assert status["surfaces"]["evidence_pack_core"] is True
    assert status["surfaces"]["familiar_ingestion_core"] is True
    assert status["surfaces"]["spine_bridge_core"] is True
    assert status["missing_required"] == []


def test_spine_touchpoint_from_fixture_receipt():
    receipt = build_familiar_ingestion_receipt_from_path(FIXTURE, repo_root=REPO)
    tp = build_familiar_spine_touchpoint(receipt)
    assert tp["route"] == "ORACLE_SHADOW_CANDIDATE"
    assert tp["advisory_only"] is True
    assert tp["authority"]["execution_authority"] is False
    assert tp["input_payload_seed"]["kind"] == "evidence_pack_shadow"
    assert tp["oracle_candidate_seed"]["source_type"] == "evidence_pack"
    assert "familiar:" in tp["oracle_candidate_seed"]["source_id"]
    schema = json.loads(TOUCH_SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(tp)


def test_spine_touchpoint_abstain_invalid():
    tp = build_familiar_spine_touchpoint(
        {
            "status": "REJECTED_INVALID_PACK",
            "receipt_id": "fir_x",
            "pack_id": "",
            "pack_hash": "",
            "blockers": ["invalid_evidence_pack"],
            "validation_errors": ["bad"],
            "commercial_claims_blocked": True,
            "evidence_density": 0.1,
            "register_counts": {},
        }
    )
    assert tp["route"] == "ABSTAIN_INVALID"


def test_touchpoint_from_pack_path_deterministic():
    a = build_touchpoint_from_pack_path(FIXTURE, repo_root=REPO)
    b = build_touchpoint_from_pack_path(FIXTURE, repo_root=REPO)
    assert a == b
    assert a["route"] == "ORACLE_SHADOW_CANDIDATE"


def test_cli_os_status(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["os", "status"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["ai_os_kernel"] == "ACTIVE_SHADOW"
    assert payload["external_production_authorized"] is False


def test_cli_forage_validate(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["forage", "validate", "--pack", str(FIXTURE)])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["pack_id"] == "ep_20260727_hermes_skill_os_001"


def test_cli_forage_ingest_print_only(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(
        ["forage", "ingest", "--pack", str(FIXTURE), "--print-only"]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["status"] == "INGESTED_SHADOW"
    assert payload["wrote"] is None


def test_cli_forage_spine_touch(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["forage", "spine-touch", "--pack", str(FIXTURE)])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["route"] == "ORACLE_SHADOW_CANDIDATE"
    assert payload["input_payload_seed"]["pack_id"] == "ep_20260727_hermes_skill_os_001"
