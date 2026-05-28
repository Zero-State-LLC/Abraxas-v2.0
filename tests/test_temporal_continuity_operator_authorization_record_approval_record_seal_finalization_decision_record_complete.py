from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete import (
    _STATUS_BLOCKED,
    _STATUS_COMPLETE,
    _STATUS_FAILED,
    _STATUS_NOT_COMPUTABLE,
    _NEXT_LANE_ON_COMPLETE,
    _NEXT_LANE_FALLBACK,
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete,
)

_RECORD_READY_STATUS = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_READY"
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

_P105_LOCK_FIELDS = [
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
    "token_minting_allowed",
]


def _make_valid_p105(*, record_hash: str = "p105hash0001") -> dict:
    return {
        "finalization_decision_record_status": _RECORD_READY_STATUS,
        "finalization_decision_record_hash": record_hash,
        "decision_record_ready": True,
        "advisory_only": True,
        "decision_record_only": True,
        "finalization_decision_record_only": True,
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
        "finalization_decision_record": {
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
            "p104_decision_hash_anchor": "27fecdd5b1271531c944960ec6e6d7e419b7f60477d19032ee2d0e1a46feb5cb",
            "autonomous_approval": False,
            "authorization_granted": False,
            "finalization_authorized": False,
            "approval_record_sealed": False,
            "execution_authority": False,
            "actual_finalization_executed": False,
        },
        "finalization_decision_provenance_chain": {
            "p104_decision_hash": "27fecdd5b1271531c944960ec6e6d7e419b7f60477d19032ee2d0e1a46feb5cb",
            "p103_review_hash": "93902e7de368a0a2f18f03d1c4161d900237311ce06dc6fea931de7471f47f92",
            "p103_review_file_hash": "c84c2acec4c0a2bb152a9bdba350b648d545c4156be97632c69838abf8e8c7b3",
            "p103_review_id": "review_001",
            "p103_review_passed": True,
            "p102_execution_hash_anchor": "904c85d365c1c7ca1a348e1f0a5f117d0a87fcd655cbf0e35afcc35f91ee6737",
            "finalization_check_summary": {"total": 54, "passed": 54, "failed": 0},
        },
    }


def _seed_p105(tmp_path: Path, payload: dict | None = None) -> Path:
    data = payload if payload is not None else _make_valid_p105()
    out_dir = (
        tmp_path
        / "out"
        / "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "latest.json"
    p.write_text(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
        encoding="utf-8",
    )
    return p


def _build(tmp_path: Path) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete(
        repo_root=tmp_path,
    )


class TestMissingSource:
    def test_not_computable_when_p105_absent(self, tmp_path):
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_status"] == _STATUS_NOT_COMPUTABLE
        assert result["completion_acknowledged"] is False
        assert result["receipt_issued"] is False
        assert any(
            "source_decision_record_missing_or_unreadable" in b
            for b in result["completion_blockers"]
        )

    def test_all_authority_locks_false_when_not_computable(self, tmp_path):
        result = _build(tmp_path)
        for field in _AUTHORITY_LOCK_FIELDS:
            assert result[field] is False, f"{field} must be False"


class TestBlockedByUpstreamStatus:
    @pytest.mark.parametrize("bad_status", [
        "NOT_COMPUTABLE",
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_FAILED",
        "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION",
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_PENDING",
    ])
    def test_blocked_when_p105_not_record_ready(self, tmp_path, bad_status):
        payload = _make_valid_p105()
        payload["finalization_decision_record_status"] = bad_status
        _seed_p105(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_status"] == _STATUS_BLOCKED
        assert result["completion_acknowledged"] is False
        assert result["receipt_issued"] is False
        assert result["recommended_next_lane"] == _NEXT_LANE_FALLBACK


class TestAuthorityLockViolations:
    @pytest.mark.parametrize("field", _P105_LOCK_FIELDS)
    def test_failed_when_p105_authority_lock_true(self, tmp_path, field):
        payload = _make_valid_p105()
        payload[field] = True
        _seed_p105(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_status"] == _STATUS_FAILED
        assert result["completion_acknowledged"] is False
        assert result["receipt_issued"] is False

    def test_failed_when_p105_autonomous_approval_true(self, tmp_path):
        payload = _make_valid_p105()
        payload["autonomous_approval"] = True
        _seed_p105(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_status"] == _STATUS_FAILED
        assert result["completion_acknowledged"] is False


class TestCompletionCheckFailures:
    def test_failed_when_decision_record_ready_false(self, tmp_path):
        payload = _make_valid_p105()
        payload["decision_record_ready"] = False
        _seed_p105(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_status"] == _STATUS_FAILED
        assert any("source_decision_record_ready_true" in b for b in result["completion_blockers"])

    def test_failed_when_record_hash_empty(self, tmp_path):
        payload = _make_valid_p105()
        payload["finalization_decision_record_hash"] = ""
        _seed_p105(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_status"] == _STATUS_FAILED
        assert any("source_record_hash_present" in b for b in result["completion_blockers"])

    def test_failed_when_advisory_only_false(self, tmp_path):
        payload = _make_valid_p105()
        payload["advisory_only"] = False
        _seed_p105(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_status"] == _STATUS_FAILED
        assert any("source_advisory_only_true" in b for b in result["completion_blockers"])

    def test_failed_when_decision_record_only_false(self, tmp_path):
        payload = _make_valid_p105()
        payload["decision_record_only"] = False
        _seed_p105(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_status"] == _STATUS_FAILED

    def test_failed_when_decision_value_wrong(self, tmp_path):
        payload = _make_valid_p105()
        payload["finalization_decision_record"]["decision_value"] = "hold_pending_further_review"
        _seed_p105(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_status"] == _STATUS_FAILED
        assert any("source_decision_value_is_approve" in b for b in result["completion_blockers"])


class TestComplete:
    def test_complete_on_valid_p105(self, tmp_path):
        _seed_p105(tmp_path)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_status"] == _STATUS_COMPLETE
        assert result["completion_acknowledged"] is True
        assert result["receipt_issued"] is True
        assert result["completion_blockers"] == []
        assert result["recommended_next_lane"] == _NEXT_LANE_ON_COMPLETE

    def test_all_authority_locks_false_on_complete(self, tmp_path):
        _seed_p105(tmp_path)
        result = _build(tmp_path)
        for field in _AUTHORITY_LOCK_FIELDS:
            assert result[field] is False, f"{field} must be False in output"

    def test_advisory_posture_flags_on_complete(self, tmp_path):
        _seed_p105(tmp_path)
        result = _build(tmp_path)
        assert result["advisory_only"] is True
        assert result["projection_only"] is True
        assert result["completion_receipt_only"] is True
        assert result["finalization_decision_record_complete_only"] is True
        assert result["decision_record_only"] is True

    def test_completion_checks_count(self, tmp_path):
        _seed_p105(tmp_path)
        result = _build(tmp_path)
        assert len(result["completion_checks"]) == 7

    def test_all_completion_checks_pass_on_valid_p105(self, tmp_path):
        _seed_p105(tmp_path)
        result = _build(tmp_path)
        for check in result["completion_checks"]:
            assert check["passed"] is True, f"check {check['check_id']} failed"

    def test_completion_receipt_struct_populated(self, tmp_path):
        _seed_p105(tmp_path, _make_valid_p105(record_hash="testhash001"))
        result = _build(tmp_path)
        cr = result["completion_receipt"]
        assert cr["p105_record_hash"] == "testhash001"
        assert cr["p105_decision_record_ready"] is True
        assert cr["decision_value"] == "approve_finalization_review_record"
        assert cr["decision_id"] == "P104_FINALIZATION_DECISION_2026_05_28_001"
        assert cr["operator_id"] == "Daniel Meyer"
        assert cr["advisory_only_confirmed"] is True
        assert cr["decision_record_only_confirmed"] is True
        assert cr["autonomous_approval"] is False
        assert cr["authorization_granted"] is False
        assert cr["finalization_authorized"] is False
        assert cr["approval_record_sealed"] is False
        assert cr["execution_authority"] is False
        assert cr["actual_finalization_executed"] is False

    def test_provenance_reanchor_populated(self, tmp_path):
        _seed_p105(tmp_path, _make_valid_p105(record_hash="anchortesthash"))
        result = _build(tmp_path)
        pr = result["completion_provenance_reanchor"]
        assert pr["p105_record_hash"] == "anchortesthash"
        assert pr["p104_decision_hash"] == "27fecdd5b1271531c944960ec6e6d7e419b7f60477d19032ee2d0e1a46feb5cb"
        assert pr["p103_review_hash"] == "93902e7de368a0a2f18f03d1c4161d900237311ce06dc6fea931de7471f47f92"
        assert pr["p103_review_file_hash"] == "c84c2acec4c0a2bb152a9bdba350b648d545c4156be97632c69838abf8e8c7b3"
        assert pr["p103_review_id"] == "review_001"
        assert pr["p103_review_passed"] is True
        assert pr["p102_execution_hash_anchor"] == "904c85d365c1c7ca1a348e1f0a5f117d0a87fcd655cbf0e35afcc35f91ee6737"

    def test_p104_hash_anchor_in_receipt(self, tmp_path):
        _seed_p105(tmp_path)
        result = _build(tmp_path)
        assert result["completion_receipt"]["p104_decision_hash_anchor"] == (
            "27fecdd5b1271531c944960ec6e6d7e419b7f60477d19032ee2d0e1a46feb5cb"
        )


class TestDeterminism:
    def test_identical_inputs_produce_identical_output(self, tmp_path):
        _seed_p105(tmp_path)
        r1 = _build(tmp_path)
        r2 = _build(tmp_path)
        assert r1 == r2

    def test_hash_field_present_and_stable(self, tmp_path):
        _seed_p105(tmp_path)
        r1 = _build(tmp_path)
        r2 = _build(tmp_path)
        h = r1["finalization_decision_record_complete_hash"]
        assert h and h != "NOT_COMPUTABLE"
        assert r1["finalization_decision_record_complete_hash"] == r2["finalization_decision_record_complete_hash"]
