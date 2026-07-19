from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.research_canary_authorization_packet_review_record import (
    build_research_canary_authorization_packet_review_record,
)
from scripts.research import run_research_canary_authorization_packet_review_record

_VALID_P101_PACKET: dict[str, object] = {
    "lane_id": "P101_RESEARCH_CANARY_AUTHORIZATION_PACKET_DRAFT",
    "artifact_type": "ResearchCanaryAuthorizationPacketDraft.v1",
    "authorization_packet_draft_status": "PASS",
    "authorization_packet_draft_ready": True,
    "authorization_packet_draft": {
        "draft_id": "DROP006_DROP007_RESEARCH_CANARY_AUTHORIZATION_PACKET_DRAFT",
        "authorization_posture": "DRAFT_ONLY_NOT_GRANTED",
        "review_required": True,
        "activation_approved": False,
        "authorization_granted": False,
    },
    "authority_locks": {
        "activation_approved": False,
        "authorization_granted": False,
        "execution_authority": False,
        "runtime_authority": False,
    },
}


def test_missing_p101_returns_not_computable() -> None:
    packet = build_research_canary_authorization_packet_review_record(p101_packet=None)
    assert packet["authorization_packet_review_status"] == "NOT_COMPUTABLE"
    assert packet["authorization_packet_review_ready"] is False
    assert (
        packet["recommended_next_lane"]
        == "P101_RESEARCH_CANARY_AUTHORIZATION_PACKET_DRAFT_REGENERATION"
    )


def test_invalid_p101_returns_not_computable() -> None:
    packet = build_research_canary_authorization_packet_review_record(
        p101_packet={**_VALID_P101_PACKET, "authorization_packet_draft_status": "NOT_COMPUTABLE"}
    )
    assert packet["authorization_packet_review_status"] == "NOT_COMPUTABLE"


def test_authority_grant_in_p101_returns_not_computable() -> None:
    invalid = dict(_VALID_P101_PACKET)
    invalid["authorization_packet_draft"] = {
        **_VALID_P101_PACKET["authorization_packet_draft"],
        "activation_approved": True,
    }
    packet = build_research_canary_authorization_packet_review_record(p101_packet=invalid)
    assert packet["authorization_packet_review_status"] == "NOT_COMPUTABLE"


def test_valid_p101_returns_pass_and_ready() -> None:
    packet = build_research_canary_authorization_packet_review_record(p101_packet=_VALID_P101_PACKET)
    assert packet["authorization_packet_review_status"] == "PASS"
    assert packet["authorization_packet_review_ready"] is True


def test_review_decision_and_recommendation_constants() -> None:
    review = build_research_canary_authorization_packet_review_record(p101_packet=_VALID_P101_PACKET)[
        "review_record"
    ]
    assert review["review_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert review["review_recommendation"] == "READY_FOR_OPERATOR_REVIEW_NOT_AUTHORIZATION"


def test_activation_and_authorization_false_in_review_and_locks() -> None:
    packet = build_research_canary_authorization_packet_review_record(p101_packet=_VALID_P101_PACKET)
    assert packet["review_record"]["activation_approved"] is False
    assert packet["review_record"]["authorization_granted"] is False
    assert packet["authority_locks"]["activation_approved"] is False
    assert packet["authority_locks"]["authorization_granted"] is False


def test_repeated_input_produces_identical_packet_hash() -> None:
    first = build_research_canary_authorization_packet_review_record(p101_packet=_VALID_P101_PACKET)
    second = build_research_canary_authorization_packet_review_record(p101_packet=_VALID_P101_PACKET)
    assert first["packet_hash"] == second["packet_hash"]
    assert first == second


def test_authority_locks_forbidden_fields_false() -> None:
    locks = build_research_canary_authorization_packet_review_record(p101_packet=_VALID_P101_PACKET)[
        "authority_locks"
    ]
    assert locks["advisory_only"] is True
    assert locks["projection_only"] is True
    assert locks["planning_only"] is True
    assert locks["evidence_only"] is True
    assert locks["review_record_only"] is True
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



def test_pass_routes_to_existing_p107_review_packet_surface() -> None:
    packet = build_research_canary_authorization_packet_review_record(p101_packet=_VALID_P101_PACKET)
    assert packet["recommended_next_lane"] == "P107_RESEARCH_CANARY_REVIEW_PACKET"


def test_runner_writes_latest_json(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_canary_authorization_packet_review_record" / "latest.json"
    run_research_canary_authorization_packet_review_record.run(
        p101_packet=_VALID_P101_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert out_path.exists()


def test_schema_validates_generated_output() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path(
            "contracts/canon/research_canary_authorization_packet_review_record.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    packet = build_research_canary_authorization_packet_review_record(p101_packet=_VALID_P101_PACKET)
    jsonschema.validate(packet, schema)
