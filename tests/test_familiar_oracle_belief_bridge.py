"""Tests for FamiliarOracleBeliefBridge.v0 (abx-familiar residual)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from abraxas.cli import main
from core.ingest.familiar_ingestion_receipt import (
    build_familiar_ingestion_receipt_from_path,
)
from core.signal.familiar_oracle_belief_bridge import (
    build_bridge_from_pack_path,
    build_bridge_from_receipt,
    build_familiar_oracle_belief_bridge,
)
from core.signal.spine_bridge import (
    build_ai_os_kernel_status,
    build_familiar_spine_touchpoint,
)

REPO = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO
    / "skills"
    / "abx-familiar-signal-forager"
    / "fixtures"
    / "evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)
SCHEMA = (
    REPO / "contracts" / "signal" / "familiar_oracle_belief_bridge.v0.schema.json"
)


def test_bridge_from_fixture_pack_schema_valid():
    bridge = build_bridge_from_pack_path(FIXTURE, repo_root=REPO)
    assert bridge["schema_version"] == "FamiliarOracleBeliefBridge.v0"
    assert bridge["status"] == "BRIDGED_SHADOW"
    assert bridge["route"] == "ORACLE_SHADOW_CANDIDATE"
    assert bridge["pipeline_id"] == "familiar_ingestion"
    assert bridge["advisory_only"] is True
    assert bridge["authority"]["execution_authority"] is False
    assert bridge["authority"]["promotion_authorized"] is False
    assert bridge["authority"]["forecast_routing_authorized"] is False
    assert bridge["authority"]["canon_mutation_allowed"] is False

    intake = bridge["oracle_shadow_intake"]
    assert intake["source_type"] == "receipt"
    assert intake["queue_write_authorized"] is False
    assert intake["runtime_invoke_authorized"] is False
    assert intake["forecast_authority"] is False
    assert "familiar:" in intake["source_id"]
    assert len(intake["raw_payload_hash"]) == 64

    seeds = bridge["belief_candidate_seeds"]
    assert isinstance(seeds, list)
    assert len(seeds) >= 1
    assert all(s.get("truth_assignment") is False for s in seeds)
    assert all(s.get("belief_promotion") is False for s in seeds)

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(bridge)


def test_bridge_deterministic():
    a = build_bridge_from_pack_path(FIXTURE, repo_root=REPO)
    b = build_bridge_from_pack_path(FIXTURE, repo_root=REPO)
    assert a == b
    assert a["bridge_hash"] == b["bridge_hash"]


def test_bridge_from_receipt_matches_pack_path():
    receipt = build_familiar_ingestion_receipt_from_path(FIXTURE, repo_root=REPO)
    via_receipt = build_bridge_from_receipt(receipt)
    via_pack = build_bridge_from_pack_path(FIXTURE, repo_root=REPO)
    assert via_receipt["status"] == via_pack["status"]
    assert via_receipt["pack_id"] == via_pack["pack_id"]
    assert via_receipt["bridge_hash"] == via_pack["bridge_hash"]


def test_bridge_abstain_invalid():
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
    bridge = build_familiar_oracle_belief_bridge(tp)
    assert bridge["status"] == "BRIDGE_ABSTAINED"
    assert bridge["route"] == "ABSTAIN_INVALID"
    assert bridge["oracle_shadow_intake"] == {}
    assert bridge["belief_candidate_seeds"] == []


def test_bridge_no_input():
    bridge = build_familiar_oracle_belief_bridge(None)
    assert bridge["status"] == "BRIDGE_NO_INPUT"
    assert bridge["route"] == "ABSTAIN_NO_INPUT"


def test_kernel_status_includes_bridge_surface():
    status = build_ai_os_kernel_status(REPO)
    assert status["ai_os_kernel"] == "ACTIVE_SHADOW"
    assert status["surfaces"]["oracle_belief_bridge_schema"] is True
    assert status["surfaces"]["oracle_belief_bridge_core"] is True
    assert status["syscall"]["oracle_belief_bridge"] == "FamiliarOracleBeliefBridge.v0"
    assert "oracle-belief-bridge" in status["commands"]["oracle_belief_bridge"]


def test_cli_forage_oracle_belief_bridge(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["forage", "oracle-belief-bridge", "--pack", str(FIXTURE)])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["status"] == "BRIDGED_SHADOW"
    assert payload["belief_seed_count"] >= 1
    assert payload["authority"]["execution_authority"] is False
