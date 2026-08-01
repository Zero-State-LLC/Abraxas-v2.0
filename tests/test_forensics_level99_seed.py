# tests/test_forensics_level99_seed.py
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from core.forensics.level99_seed import (
    build_forensic_level99_seed,
    build_forensic_level99_seed_from_pack_path,
)
from core.forensics.pipeline import run_forensics_from_pack_path

REPO = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO
    / "skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)
SCHEMA = REPO / "contracts/forensics/forensic_level99_seed.v0.schema.json"
L99_SCHEMA = REPO / "contracts/level99/content_operator_packet.v0.schema.json"


def test_fixture_seeds_level99_still_denied():
    seed = build_forensic_level99_seed_from_pack_path(FIXTURE, repo_root=REPO)
    assert seed["schema_version"] == "ForensicLevel99Seed.v0"
    assert seed["seed_status"] == "SEEDED"
    assert seed["route_intent"] == "LEVEL99_CONTENT_SEED"
    assert seed["disposition"] == "READY"
    assert seed["ops_gate_status"] == "DENIED"
    assert seed["execution_authorized"] is False
    assert seed["publish_authorized"] is False
    assert seed["advisory_only"] is True
    pkt = seed["content_packet"]
    assert isinstance(pkt, dict)
    assert pkt["schema_version"] == "Level99ContentOperatorPacket.v0"
    assert pkt["pipeline_id"] == "level99_content"
    assert pkt["auto_publish_blocked"] is True
    assert pkt["authority"]["auto_publish_allowed"] is False
    assert "FORENSIC_SEED_ONLY" in pkt["blocked_by"]
    assert seed["content_packet_hash"] == pkt["canonical_hash"]
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(seed)
    Draft7Validator(json.loads(L99_SCHEMA.read_text(encoding="utf-8"))).validate(pkt)


def test_hold_blocks_seed():
    run = run_forensics_from_pack_path(FIXTURE, repo_root=REPO)
    hold = dict(run)
    hold["disposition"] = {**(run.get("disposition") or {}), "disposition": "HOLD"}
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    seed = build_forensic_level99_seed(hold, pack)
    assert seed["seed_status"] == "BLOCKED"
    assert seed["content_packet"] is None
    assert seed["ops_gate_status"] == "DENIED"
    assert seed["execution_authorized"] is False


def test_none_blocked():
    seed = build_forensic_level99_seed(None, None)
    assert seed["seed_status"] == "BLOCKED"
    assert seed["ops_gate_status"] == "DENIED"
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(seed)


def test_deterministic():
    a = build_forensic_level99_seed_from_pack_path(FIXTURE, repo_root=REPO)
    b = build_forensic_level99_seed_from_pack_path(FIXTURE, repo_root=REPO)
    assert a == b
