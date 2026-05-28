from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete_acknowledged import (
    _STATUS_ACKNOWLEDGED,
    _STATUS_BLOCKED,
    _STATUS_FAILED,
    _STATUS_NOT_COMPUTABLE,
    _NEXT_LANE_ON_ACKNOWLEDGED,
    _NEXT_LANE_FALLBACK,
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete_acknowledged,
)

_COMPLETE_STATUS = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE"
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

_P106_LOCK_FIELDS = [
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


def _make_valid_p106(*, complete_hash: str = "p106hash0001") -> dict:
    return {
        "finalization_decision_record_complete_status": _COMPLETE_STATUS,
        "finalization_decision_record_complete_hash": complete_hash,
        "completion_acknowledged": True,
        "receipt_issued": True,
        "advisory_only": True,
        "completion_receipt_only": True,
        "finalization_decision_record_complete_only": True,
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
        "completion_receipt": {
            "p105_record_hash": "3ca320be169551c6ca7a775c6206b1344062657e6c5fa25dda16abc8258cc1dd",
            "p105_record_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_READY",
            "p105_decision_record_ready": True,
            "p104_decision_hash_anchor": "27fecdd5b1271531c944960ec6e6d7e419b7f60477d19032ee2d0e1a46feb5cb",
            "decision_value": "approve_finalization_review_record",
            "decision_id": "P104_FINALIZATION_DECISION_2026_05_28_001",
            "operator_id": "Daniel Meyer",
            "advisory_only_confirmed": True,
            "decision_record_only_confirmed": True,
            "autonomous_approval": False,
            "authorization_granted": False,
            "finalization_authorized": False,
            "approval_record_sealed": False,
            "execution_authority": False,
            "actual_finalization_executed": False,
        },
        "completion_provenance_reanchor": {
            "p105_record_hash": "3ca320be169551c6ca7a775c6206b1344062657e6c5fa25dda16abc8258cc1dd",
            "p104_decision_hash": "27fecdd5b1271531c944960ec6e6d7e419b7f60477d19032ee2d0e1a46feb5cb",
            "p103_review_hash": "93902e7de368a0a2f18f03d1c4161d900237311ce06dc6fea931de7471f47f92",
            "p103_review_file_hash": "c84c2acec4c0a2bb152a9bdba350b648d545c4156be97632c69838abf8e8c7b3",
            "p103_review_id": "review_001",
            "p103_review_passed": True,
            "p102_execution_hash_anchor": "904c85d365c1c7ca1a348e1f0a5f117d0a87fcd655cbf0e35afcc35f91ee6737",
            "finalization_check_summary": {"total": 54, "passed": 54, "failed": 0},
        },
    }


def _seed_p106(tmp_path: Path, payload: dict | None = None) -> Path:
    data = payload if payload is not None else _make_valid_p106()
    out_dir = (
        tmp_path
        / "out"
        / "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "latest.json"
    p.write_text(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
        encoding="utf-8",
    )
    return p


def _build(tmp_path: Path) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete_acknowledged(
        repo_root=tmp_path,
    )


class TestMissingSource:
    def test_not_computable_when_p106_absent(self, tmp_path):
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_acknowledged_status"] == _STATUS_NOT_COMPUTABLE
        assert result["acknowledgment_issued"] is False
        assert result["segment_closed"] is False
        assert any(
            "source_complete_missing_or_unreadable" in b
            for b in result["acknowledgment_blockers"]
        )

    def test_all_authority_locks_false_when_not_computable(self, tmp_path):
        result = _build(tmp_path)
        for field in _AUTHORITY_LOCK_FIELDS:
            assert result[field] is False, f"{field} must be False"


class TestBlockedByUpstreamStatus:
    @pytest.mark.parametrize("bad_status", [
        "NOT_COMPUTABLE",
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE_ACKNOWLEDGED_FAILED",
        "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD",
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_READY",
    ])
    def test_blocked_when_p106_not_complete(self, tmp_path, bad_status):
        payload = _make_valid_p106()
        payload["finalization_decision_record_complete_status"] = bad_status
        _seed_p106(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_acknowledged_status"] == _STATUS_BLOCKED
        assert result["acknowledgment_issued"] is False
        assert result["segment_closed"] is False
        assert result["recommended_next_lane"] == _NEXT_LANE_FALLBACK


class TestAuthorityLockViolations:
    @pytest.mark.parametrize("field", _P106_LOCK_FIELDS)
    def test_failed_when_p106_authority_lock_true(self, tmp_path, field):
        payload = _make_valid_p106()
        payload[field] = True
        _seed_p106(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_acknowledged_status"] == _STATUS_FAILED
        assert result["acknowledgment_issued"] is False
        assert result["segment_closed"] is False

    def test_failed_when_p106_autonomous_approval_true(self, tmp_path):
        payload = _make_valid_p106()
        payload["autonomous_approval"] = True
        _seed_p106(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_acknowledged_status"] == _STATUS_FAILED
        assert result["acknowledgment_issued"] is False


class TestAcknowledgmentCheckFailures:
    def test_failed_when_completion_acknowledged_false(self, tmp_path):
        payload = _make_valid_p106()
        payload["completion_acknowledged"] = False
        _seed_p106(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_acknowledged_status"] == _STATUS_FAILED
        assert any("source_completion_acknowledged_true" in b for b in result["acknowledgment_blockers"])

    def test_failed_when_receipt_issued_false(self, tmp_path):
        payload = _make_valid_p106()
        payload["receipt_issued"] = False
        _seed_p106(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_acknowledged_status"] == _STATUS_FAILED

    def test_failed_when_complete_hash_empty(self, tmp_path):
        payload = _make_valid_p106()
        payload["finalization_decision_record_complete_hash"] = ""
        _seed_p106(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_acknowledged_status"] == _STATUS_FAILED
        assert any("source_complete_hash_present" in b for b in result["acknowledgment_blockers"])

    def test_failed_when_advisory_only_false(self, tmp_path):
        payload = _make_valid_p106()
        payload["advisory_only"] = False
        _seed_p106(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_acknowledged_status"] == _STATUS_FAILED
        assert any("source_advisory_posture_confirmed" in b for b in result["acknowledgment_blockers"])

    def test_failed_when_decision_value_wrong(self, tmp_path):
        payload = _make_valid_p106()
        payload["completion_receipt"]["decision_value"] = "hold_pending_further_review"
        _seed_p106(tmp_path, payload)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_acknowledged_status"] == _STATUS_FAILED
        assert any("source_decision_value_is_approve" in b for b in result["acknowledgment_blockers"])


class TestAcknowledged:
    def test_acknowledged_on_valid_p106(self, tmp_path):
        _seed_p106(tmp_path)
        result = _build(tmp_path)
        assert result["finalization_decision_record_complete_acknowledged_status"] == _STATUS_ACKNOWLEDGED
        assert result["acknowledgment_issued"] is True
        assert result["segment_closed"] is True
        assert result["acknowledgment_blockers"] == []
        assert result["recommended_next_lane"] == _NEXT_LANE_ON_ACKNOWLEDGED

    def test_terminal_routing(self, tmp_path):
        _seed_p106(tmp_path)
        result = _build(tmp_path)
        assert result["recommended_next_lane"] == "FINALIZATION_DECISION_RECORD_SEGMENT_CLOSED"

    def test_segment_terminal_flag(self, tmp_path):
        _seed_p106(tmp_path)
        result = _build(tmp_path)
        assert result["segment_terminal"] is True

    def test_all_authority_locks_false_on_acknowledged(self, tmp_path):
        _seed_p106(tmp_path)
        result = _build(tmp_path)
        for field in _AUTHORITY_LOCK_FIELDS:
            assert result[field] is False, f"{field} must be False in output"

    def test_advisory_posture_flags(self, tmp_path):
        _seed_p106(tmp_path)
        result = _build(tmp_path)
        assert result["advisory_only"] is True
        assert result["projection_only"] is True
        assert result["acknowledgment_receipt_only"] is True
        assert result["finalization_decision_record_complete_acknowledged_only"] is True
        assert result["decision_record_only"] is True

    def test_acknowledgment_checks_count(self, tmp_path):
        _seed_p106(tmp_path)
        result = _build(tmp_path)
        assert len(result["acknowledgment_checks"]) == 7

    def test_all_acknowledgment_checks_pass(self, tmp_path):
        _seed_p106(tmp_path)
        result = _build(tmp_path)
        for check in result["acknowledgment_checks"]:
            assert check["passed"] is True, f"check {check['check_id']} failed"

    def test_acknowledgment_receipt_populated(self, tmp_path):
        _seed_p106(tmp_path, _make_valid_p106(complete_hash="testhash106"))
        result = _build(tmp_path)
        ar = result["acknowledgment_receipt"]
        assert ar["p106_complete_hash"] == "testhash106"
        assert ar["p106_completion_acknowledged"] is True
        assert ar["p106_receipt_issued"] is True
        assert ar["p105_record_hash"] == "3ca320be169551c6ca7a775c6206b1344062657e6c5fa25dda16abc8258cc1dd"
        assert ar["decision_value"] == "approve_finalization_review_record"
        assert ar["decision_id"] == "P104_FINALIZATION_DECISION_2026_05_28_001"
        assert ar["operator_id"] == "Daniel Meyer"
        assert ar["advisory_only_confirmed"] is True
        assert ar["completion_receipt_only_confirmed"] is True
        assert ar["segment_acknowledged"] is True
        assert ar["autonomous_approval"] is False
        assert ar["authorization_granted"] is False
        assert ar["finalization_authorized"] is False
        assert ar["approval_record_sealed"] is False
        assert ar["execution_authority"] is False
        assert ar["actual_finalization_executed"] is False

    def test_terminal_provenance_snapshot_populated(self, tmp_path):
        _seed_p106(tmp_path, _make_valid_p106(complete_hash="anchorseed"))
        result = _build(tmp_path)
        tps = result["terminal_provenance_snapshot"]
        assert tps["p106_complete_hash"] == "anchorseed"
        assert tps["p105_record_hash"] == "3ca320be169551c6ca7a775c6206b1344062657e6c5fa25dda16abc8258cc1dd"
        assert tps["p104_decision_hash"] == "27fecdd5b1271531c944960ec6e6d7e419b7f60477d19032ee2d0e1a46feb5cb"
        assert tps["p103_review_hash"] == "93902e7de368a0a2f18f03d1c4161d900237311ce06dc6fea931de7471f47f92"
        assert tps["p103_review_passed"] is True
        assert tps["p102_execution_hash_anchor"] == "904c85d365c1c7ca1a348e1f0a5f117d0a87fcd655cbf0e35afcc35f91ee6737"

    def test_self_referential_hash(self, tmp_path):
        _seed_p106(tmp_path)
        result = _build(tmp_path)
        top_hash = result["finalization_decision_record_complete_acknowledged_hash"]
        snap_hash = result["terminal_provenance_snapshot"]["p107_acknowledged_hash"]
        assert top_hash == snap_hash
        assert top_hash != "SELF"
        assert top_hash != "NOT_COMPUTABLE"
        assert bool(top_hash)


class TestDeterminism:
    def test_identical_inputs_produce_identical_output(self, tmp_path):
        _seed_p106(tmp_path)
        r1 = _build(tmp_path)
        r2 = _build(tmp_path)
        assert r1 == r2

    def test_hash_stable_across_runs(self, tmp_path):
        _seed_p106(tmp_path)
        r1 = _build(tmp_path)
        r2 = _build(tmp_path)
        h = r1["finalization_decision_record_complete_acknowledged_hash"]
        assert h and h != "NOT_COMPUTABLE" and h != "SELF"
        assert r1["finalization_decision_record_complete_acknowledged_hash"] == r2["finalization_decision_record_complete_acknowledged_hash"]
