from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from core.research_canary_final_activation_authorization_review_hold import (
    HOLD_REASON,
    LANE_ID,
    RECOMMENDED_NEXT_LANE,
    build_research_canary_final_activation_authorization_review_hold,
    write_research_canary_final_activation_authorization_review_hold,
)
from scripts import run_research_canary_final_activation_authorization_review_hold

VALID_P130 = json.loads(
    Path("out/research_canary_final_activation_authorization_review/latest.json").read_text()
)

_SCHEMA_PATH = Path(
    "contracts/canon/research_canary_final_activation_authorization_review_hold.v1.schema.json"
)


def _schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text())


def _build(p130: dict[str, Any] | None = None) -> dict[str, Any]:
    return build_research_canary_final_activation_authorization_review_hold(
        p130_packet=p130 if p130 is not None else VALID_P130
    )


class TestMissingOrInvalidInput:
    def test_none_input_not_computable(self) -> None:
        packet = build_research_canary_final_activation_authorization_review_hold(p130_packet=None)
        assert packet["status"] == "NOT_COMPUTABLE"
        assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
        assert "p130_packet_missing" in packet["missing_or_invalid_inputs"]

    def test_wrong_status_not_computable(self) -> None:
        packet = _build({**VALID_P130, "status": "NOT_COMPUTABLE"})
        assert packet["status"] == "NOT_COMPUTABLE"
        assert "p130_status_not_emitted" in packet["missing_or_invalid_inputs"]

    def test_wrong_lane_status_not_computable(self) -> None:
        packet = _build({**VALID_P130, "lane_status": "NOT_COMPUTABLE"})
        assert packet["status"] == "NOT_COMPUTABLE"
        assert "p130_lane_status_not_held" in packet["missing_or_invalid_inputs"]

    def test_wrong_lane_id_not_computable(self) -> None:
        packet = _build({**VALID_P130, "lane_id": "WRONG_LANE"})
        assert packet["status"] == "NOT_COMPUTABLE"
        assert "p130_lane_id_mismatch" in packet["missing_or_invalid_inputs"]

    def test_recommendation_mismatch_not_computable(self) -> None:
        packet = _build({**VALID_P130, "recommended_next_lane": "WRONG"})
        assert packet["status"] == "NOT_COMPUTABLE"
        assert "p130_recommended_next_lane_mismatch" in packet["missing_or_invalid_inputs"]

    def test_malformed_candidates_not_computable(self) -> None:
        packet = _build({**VALID_P130, "analyzed_candidates": "not_a_list"})
        assert packet["status"] == "NOT_COMPUTABLE"
        assert "p130_candidates_malformed" in packet["missing_or_invalid_inputs"]


class TestAuthorityDrift:
    def test_authority_drift_rejected(self) -> None:
        drifted = {
            **VALID_P130,
            "authority_locks": {**VALID_P130["authority_locks"], "production_activation": True},
        }
        packet = _build(drifted)
        assert packet["status"] == "REJECTED_AUTHORITY_DRIFT"
        assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
        assert any("production_activation" in f for f in packet["missing_or_invalid_inputs"])

    def test_all_locks_false_no_drift(self) -> None:
        packet = _build()
        assert packet["status"] != "REJECTED_AUTHORITY_DRIFT"


class TestHoldRecord:
    def test_status_formal_hold_record_emitted(self) -> None:
        packet = _build()
        assert packet["status"] == "FORMAL_HOLD_RECORD_EMITTED"

    def test_lane_status_hold_formal_record(self) -> None:
        packet = _build()
        assert packet["lane_status"] == "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HOLD_FORMAL_RECORD_EMITTED"

    def test_recommended_next_lane_operator_disposition(self) -> None:
        packet = _build()
        assert packet["recommended_next_lane"] == RECOMMENDED_NEXT_LANE
        assert packet["recommended_next_lane"] == "OPERATOR_DISPOSITION_REQUIRED"

    def test_held_candidates_populated(self) -> None:
        packet = _build()
        assert isinstance(packet["held_candidates"], list)
        assert len(packet["held_candidates"]) == len(VALID_P130["analyzed_candidates"])
        assert sorted(packet["held_candidates"]) == sorted(VALID_P130["analyzed_candidates"])

    def test_hold_records_match_candidates(self) -> None:
        packet = _build()
        assert len(packet["hold_records"]) == len(packet["held_candidates"])
        record_ids = {r["candidate_id"] for r in packet["hold_records"]}
        assert record_ids == set(packet["held_candidates"])

    def test_each_record_formal_hold_status(self) -> None:
        packet = _build()
        for rec in packet["hold_records"]:
            assert rec["hold_status"] == "FORMAL_HOLD_RECORD_EMITTED"

    def test_each_record_operator_disposition_required(self) -> None:
        packet = _build()
        for rec in packet["hold_records"]:
            assert rec["operator_disposition_required"] is True

    def test_hold_reason_present(self) -> None:
        packet = _build()
        assert packet["hold_reason"] == HOLD_REASON
        for rec in packet["hold_records"]:
            assert rec["hold_reason"] == HOLD_REASON


class TestAuthorityLocks:
    def test_packet_authority_locks_all_false(self) -> None:
        packet = _build()
        for key, val in packet["authority_locks"].items():
            assert val is False, f"authority_locks[{key!r}] is not False"

    def test_each_record_activation_approved_false(self) -> None:
        packet = _build()
        for rec in packet["hold_records"]:
            assert rec["activation_approved"] is False

    def test_each_record_authorization_granted_false(self) -> None:
        packet = _build()
        for rec in packet["hold_records"]:
            assert rec["authorization_granted"] is False

    def test_each_record_production_activation_false(self) -> None:
        packet = _build()
        for rec in packet["hold_records"]:
            assert rec["production_activation"] is False

    def test_each_record_execution_authority_false(self) -> None:
        packet = _build()
        for rec in packet["hold_records"]:
            assert rec["execution_authority"] is False

    def test_each_record_valid_for_execution_false(self) -> None:
        packet = _build()
        for rec in packet["hold_records"]:
            assert rec["valid_for_execution"] is False

    def test_p131_created_false(self) -> None:
        packet = _build()
        assert packet["p131_created"] is False


class TestAdvisoryPosture:
    def test_advisory_only(self) -> None:
        packet = _build()
        assert packet["advisory_only"] is True

    def test_projection_only(self) -> None:
        packet = _build()
        assert packet["projection_only"] is True

    def test_governance_posture_advisory_only(self) -> None:
        packet = _build()
        assert packet["governance_posture"] == "ADVISORY_ONLY"

    def test_upstream_lane_id_correct(self) -> None:
        packet = _build()
        assert packet["upstream_lane_id"] == "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW"

    def test_upstream_packet_hash_present(self) -> None:
        packet = _build()
        assert packet["upstream_packet_hash"] == VALID_P130["packet_hash"]

    def test_lane_id_correct(self) -> None:
        packet = _build()
        assert packet["lane_id"] == LANE_ID


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        first = _build()
        second = _build()
        assert first == second

    def test_packet_hash_stable(self) -> None:
        first = _build()
        second = _build()
        assert first["packet_hash"] == second["packet_hash"]

    def test_packet_hash_is_64_hex(self) -> None:
        packet = _build()
        h = packet["packet_hash"]
        assert isinstance(h, str)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestSchemaValidation:
    def test_valid_packet_validates(self) -> None:
        validate(_build(), _schema())

    def test_not_computable_validates(self) -> None:
        packet = build_research_canary_final_activation_authorization_review_hold(p130_packet=None)
        validate(packet, _schema())


class TestRunnerAndWriter:
    def test_runner_writes_output(self, tmp_path: Path) -> None:
        out = tmp_path / "out" / "latest.json"
        packet = run_research_canary_final_activation_authorization_review_hold.run(
            p130_packet=VALID_P130, out_path=out
        )
        assert out.exists()
        assert json.loads(out.read_text()) == packet

    def test_writer_writes(self, tmp_path: Path) -> None:
        out = tmp_path / "hold_packet.json"
        packet = _build()
        write_research_canary_final_activation_authorization_review_hold(out, packet)
        assert json.loads(out.read_text()) == packet
