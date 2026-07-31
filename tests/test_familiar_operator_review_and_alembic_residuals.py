"""Tests for residual tighten-up: familiar operator-review + Alembic Track C inventory."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from abraxas.cli import main
from core.alembic.residual_inventory import build_alembic_residual_inventory
from core.signal.familiar_operator_review import (
    build_familiar_operator_review_packet,
    build_operator_review_from_pack_path,
)
from core.signal.familiar_oracle_belief_bridge import build_bridge_from_pack_path
from core.signal.spine_bridge import build_ai_os_kernel_status

REPO = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO
    / "skills"
    / "abx-familiar-signal-forager"
    / "fixtures"
    / "evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)
REVIEW_SCHEMA = (
    REPO / "contracts" / "signal" / "familiar_operator_review_packet.v0.schema.json"
)
INV_SCHEMA = REPO / "contracts" / "alembic" / "residual_inventory.v0.schema.json"


def test_operator_review_ready_from_fixture():
    review = build_operator_review_from_pack_path(FIXTURE, repo_root=REPO)
    assert review["schema_version"] == "FamiliarOperatorReviewPacket.v0"
    assert review["disposition"] == "READY_FOR_REVIEW"
    assert review["recommended_action"] in {
        "REVIEW_ORACLE_SHADOW_INTAKE",
        "REVIEW_BELIEF_SEEDS",
    }
    assert review["review_queue_hint"] == "operator_review_queue"
    assert review["authority"]["queue_write_authorized"] is False
    assert "QUEUE_WRITE_BLOCKED" in review["blocked_by"]
    assert review["belief_seed_count"] >= 1
    Draft7Validator(json.loads(REVIEW_SCHEMA.read_text(encoding="utf-8"))).validate(
        review
    )


def test_operator_review_from_bridge_abstain():
    review = build_familiar_operator_review_packet(
        {
            "status": "BRIDGE_ABSTAINED",
            "route": "ABSTAIN_INVALID",
            "bridge_id": "b1",
            "pack_id": "",
            "touchpoint_id": "t1",
            "belief_candidate_seeds": [],
            "oracle_shadow_intake": {},
            "blocked_by": [],
        }
    )
    assert review["disposition"] == "ABSTAIN"
    assert review["recommended_action"] == "ABSTAIN_NO_ACTION"


def test_operator_review_none_bridge():
    review = build_familiar_operator_review_packet(None)
    assert review["disposition"] == "NOT_COMPUTABLE"


def test_operator_review_deterministic():
    a = build_operator_review_from_pack_path(FIXTURE, repo_root=REPO)
    b = build_operator_review_from_pack_path(FIXTURE, repo_root=REPO)
    assert a == b
    # bridge consistency
    bridge = build_bridge_from_pack_path(FIXTURE, repo_root=REPO)
    assert a["bridge_id"] == bridge["bridge_id"]


def test_cli_forage_operator_review(capsys):
    code = main(["forage", "operator-review", "--pack", str(FIXTURE)])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["disposition"] == "READY_FOR_REVIEW"


def test_alembic_residual_inventory():
    inv = build_alembic_residual_inventory()
    assert inv["schema_version"] == "AlembicResidualInventory.v0"
    assert inv["spine_status"] == "ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS"
    assert inv["authority"]["unstub_authorized"] is False
    assert inv["counts"]["total"] >= 1
    assert inv["counts"]["stub_or_unavailable"] >= 1
    residual_ids = {r["residual_id"] for r in inv["residuals"]}
    assert "live_rune_architecture_deferred" in residual_ids
    assert any(r["kind"] == "ADAPTER_STUB" for r in inv["residuals"])
    Draft7Validator(json.loads(INV_SCHEMA.read_text(encoding="utf-8"))).validate(inv)


def test_alembic_inventory_deterministic():
    assert build_alembic_residual_inventory() == build_alembic_residual_inventory()


def test_cli_os_alembic_residuals(capsys):
    code = main(["os", "alembic-residuals"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["counts"]["stub_or_unavailable"] >= 1


def test_kernel_status_surfaces():
    status = build_ai_os_kernel_status(REPO)
    assert status["surfaces"]["operator_review_core"] is True
    assert status["surfaces"]["alembic_residual_inventory_core"] is True
    assert "operator-review" in status["commands"]["operator_review"]
    assert "alembic-residuals" in status["commands"]["alembic_residuals"]
