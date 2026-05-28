from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record import (
    SOURCE_FINALIZATION_DECISION_PATH,
    _STATUS_BLOCKED,
    _STATUS_FAILED,
    _STATUS_NOT_COMPUTABLE,
    _STATUS_RECORD_READY,
    _NEXT_LANE_ON_READY,
    _NEXT_LANE_FALLBACK,
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record,
)

_APPROVED_STATUS = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_APPROVED_RECORD"
)

_AUTHORITY_LOCK_FIELDS = [
    "authorization_granted",
    "finalization_authorized",
    "approval_record_sealed",
    "actual_finalization_executed",
    "valid_for_execution",
    "execution_authority",
    "canon_promotion",
    "production_activation",
    "scheduler_mutation",
    "baseline_mutation",
    "runtime_mutation",
    "governance_authority_mutation",
    "autonomous_approval",
]


def _make_valid_odr() -> dict:
    return {
        "decision_value": "approve_finalization_review_record",
        "decision_id": "P104_FINALIZATION_DECISION_2026_05_28_001",
        "operator_id": "Daniel Meyer",
        "decision_scope": "advisory_operator_finalization_decision_record_only",
        "upstream_review_hash_match": True,
        "advisory_only_acknowledged": True,
        "no_execution_authority_granted_acknowledged": True,
        "no_seal_executed_acknowledged": True,
        "finalization_not_executed_acknowledged": True,
        "finalization_decision_record_only_acknowledged": True,
        "autonomous_approval": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "approval_record_sealed": False,
        "execution_authority": False,
        "actual_finalization_executed": False,
    }


def _make_valid_upstream_provenance() -> dict:
    return {
        "finalization_review_hash": "aaaa1111",
        "finalization_review_file_hash": "bbbb2222",
        "finalization_review_id": "review_id_001",
        "review_passed": True,
        "p102_finalization_execution_hash_anchor": "cccc3333",
        "finalization_check_summary": {"total": 54, "passed": 54},
    }


def _make_valid_p104(*, decision_hash: str = "deadbeef1234") -> dict:
    return {
        "approval_record_seal_finalization_decision_status": _APPROVED_STATUS,
        "approval_record_seal_finalization_decision_hash": decision_hash,
        "decision_recorded": True,
        "advisory_only": True,
        "decision_record_only": True,
        "autonomous_approval": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "approval_record_sealed": False,
        "actual_finalization_executed": False,
        "valid_for_execution": False,
        "execution_authority": False,
        "canon_promotion": False,
        "production_activation": False,
        "scheduler_mutation": False,
        "baseline_mutation": False,
        "runtime_mutation": False,
        "governance_authority_mutation": False,
        "token_minting_allowed": False,
        "operator_decision_record": _make_valid_odr(),
        "upstream_provenance": _make_valid_upstream_provenance(),
    }


def _seed_p104(tmp_path: Path, payload: dict | None = None) -> tuple[Path, str]:
    data = payload if payload is not None else _make_valid_p104()
    out_dir = tmp_path / "out" / "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision"
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "latest.json"
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    p.write_text(raw, encoding="utf-8")
    file_hash = hashlib.sha256(raw.encode()).hexdigest()
    return p, file_hash


def _build(tmp_path: Path) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record(
        repo_root=tmp_path,
    )


class TestMissingSource:
    def test_not_computable_when_p104_absent(self, tmp_path):
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_NOT_COMPUTABLE
        assert result["decision_record_ready"] is False
        assert any("source_decision_missing_or_unreadable" in b for b in result["record_blockers"])

    def test_all_authority_locks_false_when_not_computable(self, tmp_path):
        result = _build(tmp_path)
        for field in _AUTHORITY_LOCK_FIELDS:
            assert result[field] is False, f"{field} must be False"


class TestBlockedByUpstreamStatus:
    def test_blocked_when_p104_pending(self, tmp_path):
        payload = _make_valid_p104()
        payload["approval_record_seal_finalization_decision_status"] = (
            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_PENDING"
        )
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_BLOCKED
        assert result["decision_record_ready"] is False
        assert result["recommended_next_lane"] == _NEXT_LANE_FALLBACK

    def test_blocked_when_p104_rejected_record(self, tmp_path):
        payload = _make_valid_p104()
        payload["approval_record_seal_finalization_decision_status"] = (
            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_REJECTED_RECORD"
        )
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_BLOCKED

    def test_blocked_when_p104_failed(self, tmp_path):
        payload = _make_valid_p104()
        payload["approval_record_seal_finalization_decision_status"] = (
            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_FAILED"
        )
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_BLOCKED

    def test_blocked_when_p104_not_computable(self, tmp_path):
        payload = _make_valid_p104()
        payload["approval_record_seal_finalization_decision_status"] = "NOT_COMPUTABLE"
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_BLOCKED


class TestAuthorityLockViolations:
    @pytest.mark.parametrize("field", [
        "authorization_granted",
        "finalization_authorized",
        "approval_record_sealed",
        "actual_finalization_executed",
        "valid_for_execution",
        "execution_authority",
        "canon_promotion",
        "production_activation",
        "scheduler_mutation",
        "baseline_mutation",
        "runtime_mutation",
        "governance_authority_mutation",
    ])
    def test_failed_when_p104_authority_lock_true(self, tmp_path, field):
        payload = _make_valid_p104()
        payload[field] = True
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_FAILED
        assert result["decision_record_ready"] is False

    def test_failed_when_p104_autonomous_approval_true(self, tmp_path):
        payload = _make_valid_p104()
        payload["autonomous_approval"] = True
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_FAILED
        assert result["decision_record_ready"] is False

    def test_failed_when_odr_autonomous_approval_true(self, tmp_path):
        payload = _make_valid_p104()
        payload["operator_decision_record"]["autonomous_approval"] = True
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_FAILED


class TestPostureCheckFailures:
    def test_failed_when_odr_decision_value_wrong(self, tmp_path):
        payload = _make_valid_p104()
        payload["operator_decision_record"]["decision_value"] = "hold_pending_further_review"
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_FAILED
        assert result["decision_record_ready"] is False
        assert any("odr_decision_value_is_approve" in b for b in result["record_blockers"])

    def test_failed_when_odr_upstream_review_hash_match_false(self, tmp_path):
        payload = _make_valid_p104()
        payload["operator_decision_record"]["upstream_review_hash_match"] = False
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] in (_STATUS_FAILED, _STATUS_BLOCKED)
        assert result["decision_record_ready"] is False

    def test_failed_when_decision_recorded_false(self, tmp_path):
        payload = _make_valid_p104()
        payload["decision_recorded"] = False
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_FAILED
        assert result["decision_record_ready"] is False

    def test_failed_when_advisory_only_false(self, tmp_path):
        payload = _make_valid_p104()
        payload["advisory_only"] = False
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_FAILED
        assert result["decision_record_ready"] is False

    def test_failed_when_provenance_keys_missing(self, tmp_path):
        payload = _make_valid_p104()
        payload["upstream_provenance"] = {}
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_FAILED
        assert result["decision_record_ready"] is False
        assert any("provenance_chain_complete" in b for b in result["record_blockers"])

    def test_failed_when_decision_hash_missing(self, tmp_path):
        payload = _make_valid_p104()
        payload["approval_record_seal_finalization_decision_hash"] = ""
        _seed_p104(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_FAILED
        assert result["decision_record_ready"] is False


class TestRecordReady:
    def test_record_ready_on_valid_p104(self, tmp_path):
        _seed_p104(tmp_path)
        result = _build(tmp_path)
        assert result["finalization_decision_record_status"] == _STATUS_RECORD_READY
        assert result["decision_record_ready"] is True
        assert result["record_blockers"] == []
        assert result["recommended_next_lane"] == _NEXT_LANE_ON_READY

    def test_all_authority_locks_false_on_record_ready(self, tmp_path):
        _seed_p104(tmp_path)
        result = _build(tmp_path)
        for field in _AUTHORITY_LOCK_FIELDS:
            assert result[field] is False, f"{field} must be False in output"

    def test_advisory_posture_flags_on_record_ready(self, tmp_path):
        _seed_p104(tmp_path)
        result = _build(tmp_path)
        assert result["advisory_only"] is True
        assert result["projection_only"] is True
        assert result["finalization_decision_record_only"] is True
        assert result["decision_record_only"] is True

    def test_posture_checks_count(self, tmp_path):
        _seed_p104(tmp_path)
        result = _build(tmp_path)
        assert len(result["posture_checks"]) == 10

    def test_all_posture_checks_pass_on_valid_p104(self, tmp_path):
        _seed_p104(tmp_path)
        result = _build(tmp_path)
        for check in result["posture_checks"]:
            assert check["passed"] is True, f"check {check['check_id']} failed"

    def test_decision_record_struct_populated(self, tmp_path):
        _seed_p104(tmp_path)
        result = _build(tmp_path)
        dr = result["finalization_decision_record"]
        assert dr["decision_value"] == "approve_finalization_review_record"
        assert dr["decision_id"] == "P104_FINALIZATION_DECISION_2026_05_28_001"
        assert dr["operator_id"] == "Daniel Meyer"
        assert dr["upstream_review_hash_match"] is True
        assert dr["advisory_only_acknowledged"] is True
        assert dr["no_execution_authority_granted_acknowledged"] is True
        assert dr["no_seal_executed_acknowledged"] is True
        assert dr["finalization_not_executed_acknowledged"] is True
        assert dr["finalization_decision_record_only_acknowledged"] is True
        assert dr["autonomous_approval"] is False
        assert dr["authorization_granted"] is False
        assert dr["finalization_authorized"] is False
        assert dr["approval_record_sealed"] is False
        assert dr["execution_authority"] is False
        assert dr["actual_finalization_executed"] is False

    def test_provenance_chain_populated(self, tmp_path):
        _, _ = _seed_p104(tmp_path, _make_valid_p104(decision_hash="deadbeef1234"))
        result = _build(tmp_path)
        pc = result["finalization_decision_provenance_chain"]
        assert pc["p104_decision_hash"] == "deadbeef1234"
        assert pc["p103_review_hash"] == "aaaa1111"
        assert pc["p103_review_file_hash"] == "bbbb2222"
        assert pc["p103_review_id"] == "review_id_001"
        assert pc["p103_review_passed"] is True
        assert pc["p102_execution_hash_anchor"] == "cccc3333"

    def test_p104_hash_anchor_in_decision_record(self, tmp_path):
        _seed_p104(tmp_path, _make_valid_p104(decision_hash="abc123"))
        result = _build(tmp_path)
        assert result["finalization_decision_record"]["p104_decision_hash_anchor"] == "abc123"


class TestDeterminism:
    def test_identical_inputs_produce_identical_output(self, tmp_path):
        _seed_p104(tmp_path)
        r1 = _build(tmp_path)
        r2 = _build(tmp_path)
        assert r1 == r2

    def test_hash_field_present_and_stable(self, tmp_path):
        _seed_p104(tmp_path)
        r1 = _build(tmp_path)
        r2 = _build(tmp_path)
        assert "finalization_decision_record_hash" in r1
        h = r1["finalization_decision_record_hash"]
        assert h and h != "NOT_COMPUTABLE"
        assert r1["finalization_decision_record_hash"] == r2["finalization_decision_record_hash"]
