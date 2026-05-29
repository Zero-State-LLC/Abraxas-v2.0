from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from core.research_canary_operator_disposition_record import (
    build_research_canary_operator_disposition_record,
    write_research_canary_operator_disposition_record,
)
from scripts import run_research_canary_operator_disposition_record

HOLD_PACKET = json.loads(
    Path("out/research_canary_final_activation_authorization_review_hold/latest.json").read_text()
)
OBSERVATIONS = json.loads(
    Path("input/research_canary_operator_disposition_observations.json").read_text()
)
_SCHEMA_PATH = Path(
    "contracts/canon/research_canary_operator_disposition_record.v1.schema.json"
)


def _schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text())


def _build(
    hold: dict[str, Any] | None = None,
    obs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_research_canary_operator_disposition_record(
        hold_packet=hold if hold is not None else HOLD_PACKET,
        observations=obs if obs is not None else OBSERVATIONS,
    )


class TestMissingOrInvalidInput:
    def test_none_hold_not_computable(self) -> None:
        p = build_research_canary_operator_disposition_record(
            hold_packet=None, observations=OBSERVATIONS
        )
        assert p["status"] == "NOT_COMPUTABLE"
        assert "hold_packet_missing" in p["missing_or_invalid_inputs"]

    def test_none_observations_not_computable(self) -> None:
        p = build_research_canary_operator_disposition_record(
            hold_packet=HOLD_PACKET, observations=None
        )
        assert p["status"] == "NOT_COMPUTABLE"
        assert "observations_missing" in p["missing_or_invalid_inputs"]

    def test_wrong_hold_lane_id(self) -> None:
        p = _build(hold={**HOLD_PACKET, "lane_id": "WRONG"})
        assert p["status"] == "NOT_COMPUTABLE"
        assert "hold_lane_id_mismatch" in p["missing_or_invalid_inputs"]

    def test_wrong_hold_status(self) -> None:
        p = _build(hold={**HOLD_PACKET, "status": "NOT_COMPUTABLE"})
        assert p["status"] == "NOT_COMPUTABLE"
        assert "hold_status_not_emitted" in p["missing_or_invalid_inputs"]

    def test_missing_ack_field(self) -> None:
        obs = {k: v for k, v in OBSERVATIONS.items() if k != "advisory_only_acknowledged"}
        p = _build(obs=obs)
        assert p["status"] == "NOT_COMPUTABLE"
        assert any("advisory_only_acknowledged" in m for m in p["missing_or_invalid_inputs"])

    def test_authority_change_not_none(self) -> None:
        p = _build(obs={**OBSERVATIONS, "authority_change": "mutate"})
        assert p["status"] == "NOT_COMPUTABLE"
        assert "observations_authority_change_not_none" in p["missing_or_invalid_inputs"]

    def test_upstream_hash_mismatch(self) -> None:
        p = _build(obs={**OBSERVATIONS, "upstream_hold_artifact_hash": "badhash"})
        assert p["status"] == "NOT_COMPUTABLE"
        assert "observations_upstream_hash_mismatch" in p["missing_or_invalid_inputs"]

    def test_extra_candidate_in_observations(self) -> None:
        extra = dict(OBSERVATIONS["candidate_dispositions"])
        extra["FAKE_CANDIDATE"] = {
            "candidate_id": "FAKE_CANDIDATE",
            "disposition": "defer_hold_indefinitely",
            "rationale": "fake",
            "activation_approved": False,
            "authorization_granted": False,
            "production_activation": False,
        }
        obs = {**OBSERVATIONS, "candidate_dispositions": extra}
        p = _build(obs=obs)
        assert p["status"] == "NOT_COMPUTABLE"
        assert any("extra_candidate" in m for m in p["missing_or_invalid_inputs"])

    def test_missing_candidate_in_observations(self) -> None:
        short = {k: v for k, v in OBSERVATIONS["candidate_dispositions"].items()
                 if k != "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"}
        obs = {**OBSERVATIONS, "candidate_dispositions": short}
        p = _build(obs=obs)
        assert p["status"] == "NOT_COMPUTABLE"
        assert any("missing_candidate" in m for m in p["missing_or_invalid_inputs"])

    def test_invalid_disposition_value(self) -> None:
        bad = dict(OBSERVATIONS["candidate_dispositions"])
        cid = "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"
        bad[cid] = {**bad[cid], "disposition": "activate_now"}
        p = _build(obs={**OBSERVATIONS, "candidate_dispositions": bad})
        assert p["status"] == "NOT_COMPUTABLE"
        assert any("invalid_disposition" in m for m in p["missing_or_invalid_inputs"])

    def test_candidate_activation_approved_drift(self) -> None:
        bad = dict(OBSERVATIONS["candidate_dispositions"])
        cid = "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"
        bad[cid] = {**bad[cid], "activation_approved": True}
        p = _build(obs={**OBSERVATIONS, "candidate_dispositions": bad})
        assert p["status"] == "NOT_COMPUTABLE"
        assert any("activation_approved_drift" in m for m in p["missing_or_invalid_inputs"])


class TestAuthorityDrift:
    def test_hold_authority_lock_drift_rejected(self) -> None:
        drifted = {
            **HOLD_PACKET,
            "authority_locks": {**HOLD_PACKET["authority_locks"], "production_activation": True},
        }
        p = _build(hold=drifted)
        assert p["status"] == "REJECTED_AUTHORITY_DRIFT"
        assert p["recommended_next_lane"] == "NOT_COMPUTABLE"
        assert any("production_activation" in m for m in p["missing_or_invalid_inputs"])


class TestSuccessfulRecord:
    def test_status_ready(self) -> None:
        assert _build()["status"] == "RESEARCH_CANARY_OPERATOR_DISPOSITION_RECORD_READY"

    def test_lane_status_emitted(self) -> None:
        assert _build()["lane_status"] == "OPERATOR_DISPOSITION_RECORD_EMITTED"

    def test_b002_status_resolved_defer_all(self) -> None:
        assert _build()["b002_status"] == "RESOLVED_BY_OPERATOR_DEFER_ALL"

    def test_recommended_next_lane(self) -> None:
        assert _build()["recommended_next_lane"] == "OPERATOR_DISPOSITION_COMPLETE_ADVISORY_HOLD_CLOSED"

    def test_dispositioned_candidates_all_six(self) -> None:
        p = _build()
        assert len(p["dispositioned_candidates"]) == 6
        assert sorted(p["dispositioned_candidates"]) == sorted(HOLD_PACKET["held_candidates"])

    def test_disposition_records_count(self) -> None:
        p = _build()
        assert len(p["disposition_records"]) == 6

    def test_all_records_defer_hold_indefinitely(self) -> None:
        p = _build()
        for rec in p["disposition_records"]:
            assert rec["disposition"] == "defer_hold_indefinitely"
            assert rec["disposition_status"] == "HOLD_DEFERRED_INDEFINITELY"

    def test_operator_id_and_batch_id(self) -> None:
        p = _build()
        assert p["operator_id"] == "Daniel Meyer"
        assert p["disposition_batch_id"] == "P130_OPERATOR_DISPOSITION_2026_05_28_001"

    def test_upstream_packet_hash(self) -> None:
        assert _build()["upstream_packet_hash"] == HOLD_PACKET["packet_hash"]


class TestAuthorityLocks:
    def test_packet_authority_locks_all_false(self) -> None:
        p = _build()
        for key, val in p["authority_locks"].items():
            assert val is False, f"authority_locks[{key!r}] is not False"

    def test_top_level_authority_fields_false(self) -> None:
        p = _build()
        for field in (
            "activation_approved", "authorization_granted", "production_activation",
            "canon_promotion", "scheduler_mutation", "baseline_mutation",
            "runtime_mutation", "queue_mutation", "governance_authority_mutation",
        ):
            assert p[field] is False, f"top-level {field!r} is not False"

    def test_authority_change_none(self) -> None:
        assert _build()["authority_change"] == "none"

    def test_p131_created_false(self) -> None:
        assert _build()["p131_created"] is False

    def test_advisory_only_true(self) -> None:
        assert _build()["advisory_only"] is True

    def test_projection_only_true(self) -> None:
        assert _build()["projection_only"] is True

    def test_per_record_activation_approved_false(self) -> None:
        for rec in _build()["disposition_records"]:
            assert rec["activation_approved"] is False

    def test_per_record_authorization_granted_false(self) -> None:
        for rec in _build()["disposition_records"]:
            assert rec["authorization_granted"] is False

    def test_per_record_production_activation_false(self) -> None:
        for rec in _build()["disposition_records"]:
            assert rec["production_activation"] is False

    def test_per_record_valid_for_execution_false(self) -> None:
        for rec in _build()["disposition_records"]:
            assert rec["valid_for_execution"] is False


class TestDeterminism:
    def test_same_output_twice(self) -> None:
        assert _build() == _build()

    def test_packet_hash_stable(self) -> None:
        assert _build()["packet_hash"] == _build()["packet_hash"]

    def test_packet_hash_64_hex(self) -> None:
        h = _build()["packet_hash"]
        assert isinstance(h, str) and len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestSchemaValidation:
    def test_valid_packet_validates(self) -> None:
        validate(_build(), _schema())

    def test_not_computable_validates(self) -> None:
        p = build_research_canary_operator_disposition_record(
            hold_packet=None, observations=None
        )
        validate(p, _schema())

    def test_rejected_drift_validates(self) -> None:
        drifted = {
            **HOLD_PACKET,
            "authority_locks": {**HOLD_PACKET["authority_locks"], "execution_authority": True},
        }
        p = _build(hold=drifted)
        validate(p, _schema())


class TestRunnerAndWriter:
    def test_runner_writes_output(self, tmp_path: Path) -> None:
        out = tmp_path / "out" / "latest.json"
        packet = run_research_canary_operator_disposition_record.run(
            hold_packet=HOLD_PACKET,
            observations=OBSERVATIONS,
            out_path=out,
        )
        assert out.exists()
        assert json.loads(out.read_text()) == packet

    def test_writer_roundtrip(self, tmp_path: Path) -> None:
        out = tmp_path / "rec.json"
        p = _build()
        write_research_canary_operator_disposition_record(out, p)
        assert json.loads(out.read_text()) == p
