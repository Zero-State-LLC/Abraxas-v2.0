# tests/test_forensics_ops_route.py
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from core.forensics.ops_route import (
    build_memetic_ops_route_intent,
    build_memetic_ops_route_intent_from_pack_path,
)
from core.forensics.pipeline import run_forensics_from_pack_path

REPO = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO
    / "skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)
SCHEMA = REPO / "contracts/forensics/memetic_ops_route_intent.v0.schema.json"


def test_fixture_ready_would_route_level99_still_denied():
    intent = build_memetic_ops_route_intent_from_pack_path(FIXTURE, repo_root=REPO)
    assert intent["schema_version"] == "MemeticOpsRouteIntent.v0"
    assert intent["disposition"] == "READY"
    assert intent["route_intent"] == "LEVEL99_CONTENT_SEED"
    assert intent["route_status"] == "WOULD_ROUTE_IF_OPERATOR"
    assert intent["target_pipeline"] == "level99_content"
    assert intent["ops_gate_status"] == "DENIED"
    assert intent["execution_authorized"] is False
    assert intent["publish_authorized"] is False
    assert intent["advisory_only"] is True
    assert intent["lane"] == "SHADOW"
    assert intent["authority"]["execution_authority"] is False
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(intent)


def test_prefer_neon_seed():
    intent = build_memetic_ops_route_intent_from_pack_path(
        FIXTURE, repo_root=REPO, prefer_neon=True
    )
    assert intent["route_intent"] == "NEON_IDEATION_SEED"
    assert intent["target_pipeline"] == "neon_genie_ideation"
    assert intent["ops_gate_status"] == "DENIED"


def test_none_run_blocked():
    intent = build_memetic_ops_route_intent(None)
    assert intent["route_intent"] == "NONE"
    assert intent["route_status"] == "BLOCKED"
    assert intent["ops_gate_status"] == "DENIED"
    assert intent["execution_authorized"] is False
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(intent)


def test_hold_blocked():
    run = run_forensics_from_pack_path(FIXTURE, repo_root=REPO)
    hold = dict(run)
    hold["disposition"] = {**(run.get("disposition") or {}), "disposition": "HOLD"}
    intent = build_memetic_ops_route_intent(hold)
    assert intent["route_intent"] == "NONE"
    assert intent["route_status"] == "BLOCKED"
    assert intent["ops_gate_status"] == "DENIED"


def test_deterministic():
    a = build_memetic_ops_route_intent_from_pack_path(FIXTURE, repo_root=REPO)
    b = build_memetic_ops_route_intent_from_pack_path(FIXTURE, repo_root=REPO)
    assert a == b
