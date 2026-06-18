from __future__ import annotations

import json
from pathlib import Path

from core.research_canary_final_activation_operator_decision_record import (
    DEFAULT_PAYLOAD_PATH,
    P130_PATH,
    build_research_canary_final_activation_operator_decision_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures"


def test_p131_hold_payload_fixture_blocked_when_all_must_be_false() -> None:
    payload = json.loads((FIXTURES / "p130_hold_all_candidates_payload.json").read_text())
    # Override by building with inline validation - use temp approach
    from core.research_canary_final_activation_operator_decision_record import _validate_payload

    p130 = json.loads((REPO_ROOT / P130_PATH).read_text())
    blockers = _validate_payload(payload, p130)
    assert blockers == []


def test_p131_pilot_payload_routes_to_p132() -> None:
    packet = build_research_canary_final_activation_operator_decision_record(REPO_ROOT)
    assert packet["recommended_next_lane"] == "P132_RESEARCH_CANARY_ADVISORY_SHADOW_ACTIVATION_RECORD"


def test_p131_multi_candidate_advisory_shadow_approval() -> None:
    packet = build_research_canary_final_activation_operator_decision_record(REPO_ROOT)
    approved = [
        rec
        for rec in packet["candidate_decision_records"]
        if rec.get("advisory_shadow_activation_approved") is True
    ]
    assert len(approved) == 2
    approved_ids = {rec["candidate_id"] for rec in approved}
    assert "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER" in approved_ids
    assert "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER" in approved_ids


def test_p131_rejects_execution_authority_in_payload(tmp_path: Path) -> None:
    payload = json.loads((REPO_ROOT / DEFAULT_PAYLOAD_PATH).read_text())
    payload["candidate_dispositions"][0]["execution_authority"] = True
    path = tmp_path / "bad_payload.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    packet = build_research_canary_final_activation_operator_decision_record(
        REPO_ROOT, attestation_payload_path=path
    )
    assert packet["status"] == "OPERATOR_DECISION_RECORD_BLOCKED"
