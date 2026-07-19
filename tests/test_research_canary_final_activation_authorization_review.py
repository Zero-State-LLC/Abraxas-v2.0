from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import write_canonical_json
from core.research_canary_final_activation_authorization_review import (
    build_research_canary_final_activation_authorization_review,
)
from scripts import run_research_canary_final_activation_authorization_review


VALID_P129 = json.loads(Path("out/research_canary_activation_readiness_evidence_record/latest.json").read_text())


def _schema() -> dict:
    return json.loads(Path("contracts/canon/research_canary_final_activation_authorization_review.v1.schema.json").read_text())


def test_missing_input_not_computable() -> None:
    packet = build_research_canary_final_activation_authorization_review(p129_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_invalid_status_not_computable() -> None:
    packet = build_research_canary_final_activation_authorization_review(
        p129_packet={**VALID_P129, "status": "NOT_COMPUTABLE"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"


def test_recommendation_mismatch_not_computable() -> None:
    packet = build_research_canary_final_activation_authorization_review(
        p129_packet={**VALID_P129, "recommended_next_lane": "WRONG"}
    )
    assert packet["status"] == "NOT_COMPUTABLE"


def test_authority_drift_rejected() -> None:
    p129 = {**VALID_P129, "authority_locks": {**VALID_P129["authority_locks"], "production_activation": True}}
    packet = build_research_canary_final_activation_authorization_review(p129_packet=p129)
    assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_valid_emits_held_review_no_authority() -> None:
    packet = build_research_canary_final_activation_authorization_review(p129_packet=VALID_P129)
    assert packet["status"] == "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_RECORD_EMITTED"
    assert packet["lane_status"] == "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HELD_FOR_OPERATOR"
    assert packet["recommended_next_lane"] == "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HOLD"
    assert len(packet["final_review_records"]) == len(packet["analyzed_candidates"])
    assert all(not v for v in packet["authority_locks"].values())
    for rec in packet["final_review_records"]:
        assert rec["activation_approved"] is False
        assert rec["authorization_granted"] is False
        assert rec["valid_for_execution"] is False


def test_deterministic_hash_stability() -> None:
    first = build_research_canary_final_activation_authorization_review(p129_packet=VALID_P129)
    second = build_research_canary_final_activation_authorization_review(p129_packet=VALID_P129)
    assert first == second


def test_schema_validation() -> None:
    validate(build_research_canary_final_activation_authorization_review(p129_packet=VALID_P129), _schema())


def test_runner_writes_output(tmp_path: Path) -> None:
    out = tmp_path / "out" / "latest.json"
    packet = run_research_canary_final_activation_authorization_review.run(p129_packet=VALID_P129, out_path=out)
    assert out.exists()
    assert json.loads(out.read_text()) == packet


def test_writer_writes() -> None:
    packet = build_research_canary_final_activation_authorization_review(p129_packet=VALID_P129)
    out_path = Path("/tmp/p130_packet.json")
    write_canonical_json(out_path, packet)
    assert json.loads(out_path.read_text()) == packet
