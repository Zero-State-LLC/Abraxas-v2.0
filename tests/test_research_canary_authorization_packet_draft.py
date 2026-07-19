from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.research_canary_authorization_packet_draft import (
    build_research_canary_authorization_packet_draft,
    write_research_canary_authorization_packet_draft,
)
from scripts.research import run_research_canary_authorization_packet_draft
from scripts.research.run_research_canary_authorization_packet_draft import _load_p100_packet

_VALID_P100_PACKET: dict[str, object] = {
    "lane_id": "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD",
    "artifact_type": "ResearchOperatorStabilizationDecisionRecord.v1",
    "stabilization_decision_status": "PASS",
    "decision_record_ready": True,
    "decision_record": {
        "decision_id": "DROP006_DROP007_RESEARCH_STABILIZATION_DECISION_RECORD",
        "operator_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "stabilization_recommendation": "READY_FOR_OPERATOR_REVIEW_NOT_ACTIVATION",
    },
    "authority_locks": {
        "activation_approved": False,
        "authorization_granted": False,
        "execution_authority": False,
        "runtime_authority": False,
    },
}


def test_missing_p100_returns_not_computable() -> None:
    packet = build_research_canary_authorization_packet_draft(p100_packet=None)
    assert packet["authorization_packet_draft_status"] == "NOT_COMPUTABLE"
    assert packet["authorization_packet_draft_ready"] is False
    assert (
        packet["recommended_next_lane"]
        == "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD_REGENERATION"
    )
    assert "p100_artifact_missing" in packet["missing_or_invalid_inputs"]


def test_invalid_p100_returns_not_computable() -> None:
    packet = build_research_canary_authorization_packet_draft(
        p100_packet={**_VALID_P100_PACKET, "stabilization_decision_status": "NOT_COMPUTABLE"}
    )
    assert packet["authorization_packet_draft_status"] == "NOT_COMPUTABLE"
    assert packet["authorization_packet_draft_ready"] is False


def test_authority_grant_in_p100_returns_not_computable() -> None:
    invalid = dict(_VALID_P100_PACKET)
    invalid["authority_locks"] = {
        "activation_approved": True,
        "authorization_granted": False,
        "execution_authority": False,
        "runtime_authority": False,
    }
    packet = build_research_canary_authorization_packet_draft(p100_packet=invalid)
    assert packet["authorization_packet_draft_status"] == "NOT_COMPUTABLE"
    assert packet["authorization_packet_draft_ready"] is False


def test_valid_p100_returns_pass() -> None:
    packet = build_research_canary_authorization_packet_draft(p100_packet=_VALID_P100_PACKET)
    assert packet["authorization_packet_draft_status"] == "PASS"
    assert packet["authorization_packet_draft_ready"] is True
    assert packet["recommended_next_lane"] == "P102_RESEARCH_CANARY_AUTHORIZATION_PACKET_REVIEW_RECORD"


def test_posture_and_review_required() -> None:
    draft = build_research_canary_authorization_packet_draft(p100_packet=_VALID_P100_PACKET)[
        "authorization_packet_draft"
    ]
    assert draft["authorization_posture"] == "DRAFT_ONLY_NOT_GRANTED"
    assert draft["review_required"] is True


def test_activation_and_authorization_false_in_draft_and_locks() -> None:
    packet = build_research_canary_authorization_packet_draft(p100_packet=_VALID_P100_PACKET)
    draft = packet["authorization_packet_draft"]
    assert draft["activation_approved"] is False
    assert draft["authorization_granted"] is False
    assert packet["authority_locks"]["activation_approved"] is False
    assert packet["authority_locks"]["authorization_granted"] is False


def test_repeated_input_produces_identical_packet_hash() -> None:
    first = build_research_canary_authorization_packet_draft(p100_packet=_VALID_P100_PACKET)
    second = build_research_canary_authorization_packet_draft(p100_packet=_VALID_P100_PACKET)
    assert first["packet_hash"] == second["packet_hash"]
    assert first == second


def test_authority_locks_are_non_authoritative() -> None:
    packet = build_research_canary_authorization_packet_draft(p100_packet=_VALID_P100_PACKET)
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["projection_only"] is True
    assert locks["planning_only"] is True
    assert locks["evidence_only"] is True
    assert locks["draft_only"] is True
    assert locks["operator_review_required"] is True
    assert locks["shadow_only"] is True
    assert locks["production_activation"] is False
    assert locks["canon_promotion"] is False
    assert locks["scheduler_mutation"] is False
    assert locks["runtime_authority"] is False
    assert locks["forecast_influence"] is False
    assert locks["execution_authority"] is False
    assert locks["repair_execution_authority"] is False
    assert locks["regeneration_execution_authority"] is False
    assert locks["token_minting_allowed"] is False
    assert locks["valid_for_execution"] is False


def test_runner_writes_latest_json(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_canary_authorization_packet_draft" / "latest.json"
    run_research_canary_authorization_packet_draft.run(
        p100_packet=_VALID_P100_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert out_path.exists()


def test_schema_validates_generated_output() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/canon/research_canary_authorization_packet_draft.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = build_research_canary_authorization_packet_draft(p100_packet=_VALID_P100_PACKET)
    jsonschema.validate(packet, schema)


def test_load_p100_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p100_packet(tmp_path / "missing.json") is None


def test_write_includes_final_newline(tmp_path: Path) -> None:
    packet = build_research_canary_authorization_packet_draft(p100_packet=_VALID_P100_PACKET)
    out_path = tmp_path / "packet.json"
    write_research_canary_authorization_packet_draft(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
