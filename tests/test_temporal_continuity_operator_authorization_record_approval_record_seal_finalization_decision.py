from __future__ import annotations

import json
import subprocess
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision import (
    ALLOWED_DECISIONS,
    FORBIDDEN_DECISIONS,
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision,
)

_STATUS_APPROVED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_APPROVED_RECORD"
)
_STATUS_REJECTED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_REJECTED_RECORD"
)
_STATUS_FAILED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_FAILED"
)
_STATUS_PENDING = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_PENDING"
)
_STATUS_BLOCKED = (
    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_REVIEW"
)
_STATUS_NOT_COMPUTABLE = "NOT_COMPUTABLE"

_NEXT_P105 = (
    "P105_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD"
)
_NEXT_P104 = (
    "P104_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION"
)
_NEXT_P103 = (
    "P103_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_REVIEW"
)
_NEXT_P102 = (
    "P102_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION"
)

_P103_SOURCE = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review/latest.json"
)

_ALL_AUTHORITY_LOCK_FIELDS = (
    "authorization_granted",
    "finalization_authorized",
    "approval_record_sealed",
    "valid_for_execution",
    "execution_authority",
    "token_minting_allowed",
    "actual_finalization_executed",
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "baseline_mutation",
    "runtime_mutation",
    "governance_authority_mutation",
    "approval_granted",
    "mutation_allowed",
    "forecast_authority",
    "canon_mutation_allowed",
    "runtime_mutation_allowed",
    "authorization_authority",
    "authorization_record_creation_authority",
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


_P103_REVIEW_READY_STATUS = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_REVIEW_READY"
)


def _seed_p103(root: Path, *, status: str = _P103_REVIEW_READY_STATUS, review_passed: bool = True) -> Path:
    p103_path = root / _P103_SOURCE
    payload = {
        "finalization_review_status": status,
        "review_passed": review_passed,
        "approval_record_seal_finalization_review_hash": "93902e7de368a0a2f18f03d1c4161d900237311ce06dc6fea931de7471f47f92",
        "approval_record_seal_finalization_review_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review_001"
        ),
        "finalization_check_summary": {"total": 54, "passed": 54, "failed": 0},
        "p102_finalization_execution_hash_anchor": (
            "904c85d365c1c7ca1a348e1f0a5f117d0a87fcd655cbf0e35afcc35f91ee6737"
        ),
        "advisory_only": True,
        "review_only": True,
    }
    _write_json(p103_path, payload)
    return p103_path


def _p103_file_hash(root: Path) -> str:
    import hashlib
    p103_path = root / _P103_SOURCE
    return hashlib.sha256(p103_path.read_bytes()).hexdigest()


def _make_valid_human_artifact(p103_file_hash: str, decision: str = "approve_finalization_review_record") -> dict:
    return {
        "decision_id": "P104_FINALIZATION_DECISION_2026_05_28_001",
        "operator_id": "Daniel Meyer",
        "decision": decision,
        "decision_scope": "P104 finalization decision record only",
        "upstream_review_hash": p103_file_hash,
        "advisory_only": True,
        "advisory_only_acknowledged": True,
        "no_execution_authority_granted_acknowledged": True,
        "no_seal_executed_acknowledged": True,
        "finalization_not_executed_acknowledged": True,
        "finalization_decision_record_only_acknowledged": True,
        "authorization_granted": False,
        "finalization_authorized": False,
        "approval_record_sealed": False,
        "valid_for_execution": False,
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "baseline_mutation": False,
        "runtime_mutation": False,
        "governance_authority_mutation": False,
        "note": "Operator approves recording finalization decision posture only.",
    }


def _build(root: Path, human_packet: dict | None = None, path: str | None = None) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision(
        repo_root=root,
        human_decision_packet=human_packet,
        human_decision_artifact_path=path,
    )


def test_missing_p103_not_computable(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_NOT_COMPUTABLE
    assert packet["decision_recorded"] is False
    assert packet["human_decision_artifact_present"] is False
    assert packet["autonomous_approval"] is False
    for field in _ALL_AUTHORITY_LOCK_FIELDS:
        assert packet[field] is False, f"expected {field}=False, got {packet[field]}"
    assert packet["advisory_only"] is True
    assert packet["decision_record_only"] is True
    h = packet["approval_record_seal_finalization_decision_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert _NEXT_P103 in packet["recommended_next_lane"]


def test_blocked_wrong_status(tmp_path: Path) -> None:
    _seed_p103(tmp_path, status="BLOCKED_BY_SOMETHING")
    packet = _build(tmp_path)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_BLOCKED
    assert packet["decision_recorded"] is False
    assert _NEXT_P103 in packet["recommended_next_lane"]


def test_blocked_review_passed_false(tmp_path: Path) -> None:
    _seed_p103(tmp_path, review_passed=False)
    packet = _build(tmp_path)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_BLOCKED
    assert packet["decision_recorded"] is False
    assert any("review_passed" in b for b in packet["decision_blockers"])


def test_pending_no_human_artifact(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    packet = _build(tmp_path)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_PENDING
    assert packet["decision_recorded"] is True
    assert packet["human_decision_artifact_present"] is False
    assert packet["operator_decision_record"]["decision_value"] == "PENDING_OPERATOR_INPUT"
    assert _NEXT_P104 in packet["recommended_next_lane"]
    for field in _ALL_AUTHORITY_LOCK_FIELDS:
        assert packet[field] is False


def test_approved_valid_artifact(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    human = _make_valid_human_artifact(fh, "approve_finalization_review_record")
    packet = _build(tmp_path, human_packet=human, path="input/decision.json")
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_APPROVED
    assert packet["decision_recorded"] is True
    assert packet["human_decision_artifact_present"] is True
    assert _NEXT_P105 in packet["recommended_next_lane"]
    audit = packet["decision_posture_audit"]
    assert len(audit) == 11
    assert all(item["passed"] is True for item in audit)
    odr = packet["operator_decision_record"]
    assert odr["decision_value"] == "approve_finalization_review_record"
    assert odr["upstream_review_hash_match"] is True
    assert odr["advisory_only_acknowledged"] is True
    assert odr["no_execution_authority_granted_acknowledged"] is True
    assert odr["no_seal_executed_acknowledged"] is True
    assert odr["finalization_not_executed_acknowledged"] is True
    assert odr["finalization_decision_record_only_acknowledged"] is True
    assert odr["authorization_granted"] is False
    assert odr["finalization_authorized"] is False
    assert odr["approval_record_sealed"] is False
    assert odr["execution_authority"] is False
    assert odr["actual_finalization_executed"] is False
    assert odr["autonomous_approval"] is False
    for field in _ALL_AUTHORITY_LOCK_FIELDS:
        assert packet[field] is False


def test_rejected_valid_artifact(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    human = _make_valid_human_artifact(fh, "reject_finalization_review")
    packet = _build(tmp_path, human_packet=human)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_REJECTED
    assert packet["decision_recorded"] is True
    assert _NEXT_P103 in packet["recommended_next_lane"]


def test_hold_routes_to_p103(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    human = _make_valid_human_artifact(fh, "hold_pending_further_review")
    packet = _build(tmp_path, human_packet=human)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_REJECTED
    assert _NEXT_P103 in packet["recommended_next_lane"]


def test_request_repair_routes_to_p102(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    human = _make_valid_human_artifact(fh, "request_repair")
    packet = _build(tmp_path, human_packet=human)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_REJECTED
    assert _NEXT_P102 in packet["recommended_next_lane"]


def test_failed_wrong_hash(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    human = _make_valid_human_artifact("wrong_hash_value_not_matching")
    packet = _build(tmp_path, human_packet=human)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_FAILED
    assert packet["decision_recorded"] is False
    audit = packet["decision_posture_audit"]
    hash_check = next(c for c in audit if c["check_id"] == "upstream_review_hash_matches_p103_file")
    assert hash_check["passed"] is False
    assert any("upstream_review_hash" in b for b in packet["decision_blockers"])


def test_failed_forbidden_decision(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    human = _make_valid_human_artifact(fh)
    human["decision"] = "grant_execution_authority"
    packet = _build(tmp_path, human_packet=human)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_FAILED
    audit = packet["decision_posture_audit"]
    forbidden_check = next(c for c in audit if c["check_id"] == "decision_not_in_forbidden_list")
    assert forbidden_check["passed"] is False


def test_failed_unknown_decision(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    human = _make_valid_human_artifact(fh)
    human["decision"] = "some_unknown_value"
    packet = _build(tmp_path, human_packet=human)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_FAILED
    assert any("decision_in_allowed_list" in b for b in packet["decision_blockers"])


def test_failed_missing_acknowledgement(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    human = _make_valid_human_artifact(fh)
    del human["finalization_not_executed_acknowledged"]
    packet = _build(tmp_path, human_packet=human)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_FAILED
    audit = packet["decision_posture_audit"]
    ack_check = next(
        c for c in audit if c["check_id"] == "finalization_not_executed_acknowledged_is_true"
    )
    assert ack_check["passed"] is False


def test_failed_authority_lock_in_human_artifact(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    human = _make_valid_human_artifact(fh)
    human["authorization_granted"] = True
    packet = _build(tmp_path, human_packet=human)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_FAILED
    audit = packet["decision_posture_audit"]
    lock_check = next(c for c in audit if c["check_id"] == "human_artifact_authority_locks_clean")
    assert lock_check["passed"] is False
    assert packet["authorization_granted"] is False


def test_authority_locks_hardcoded_regardless_of_source(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    human = _make_valid_human_artifact(fh)
    for field in (
        "authorization_granted", "finalization_authorized", "approval_record_sealed",
        "valid_for_execution", "execution_authority", "production_activation",
    ):
        human[field] = True
    packet = _build(tmp_path, human_packet=human)
    assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_FAILED
    for field in _ALL_AUTHORITY_LOCK_FIELDS:
        assert packet[field] is False, f"expected {field}=False, got {packet[field]}"
    assert packet["autonomous_approval"] is False
    odr = packet["operator_decision_record"]
    assert odr["authorization_granted"] is False
    assert odr["finalization_authorized"] is False
    assert odr["approval_record_sealed"] is False
    assert odr["execution_authority"] is False
    assert odr["actual_finalization_executed"] is False
    assert odr["autonomous_approval"] is False


def test_upstream_provenance_embedded(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    packet = _build(tmp_path)
    prov = packet["upstream_provenance"]
    assert prov["finalization_review_hash"] == (
        "93902e7de368a0a2f18f03d1c4161d900237311ce06dc6fea931de7471f47f92"
    )
    assert prov["finalization_review_file_hash"] == _p103_file_hash(tmp_path)
    assert prov["p102_finalization_execution_hash_anchor"] == (
        "904c85d365c1c7ca1a348e1f0a5f117d0a87fcd655cbf0e35afcc35f91ee6737"
    )
    assert prov["review_passed"] is True
    assert prov["finalization_check_summary"]["failed"] == 0


def test_schema_and_id(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    packet = _build(tmp_path, human_packet=_make_valid_human_artifact(fh))
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationDecision.v1"
    )
    assert packet["approval_record_seal_finalization_decision_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_001"
    )


def test_hash_validation(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    packet = _build(tmp_path, human_packet=_make_valid_human_artifact(fh))
    h = packet["approval_record_seal_finalization_decision_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)
    from core.canonical.json import canonical_hash
    packet_base = {k: v for k, v in packet.items() if k != "approval_record_seal_finalization_decision_hash"}
    assert canonical_hash(packet_base) == h


def test_determinism(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    human = _make_valid_human_artifact(fh)
    p1 = _build(tmp_path, human_packet=human)
    p2 = _build(tmp_path, human_packet=human)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert p1["approval_record_seal_finalization_decision_hash"] == p2["approval_record_seal_finalization_decision_hash"]


def test_write_function(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    packet = _build(tmp_path, human_packet=_make_valid_human_artifact(fh))
    out = (
        tmp_path
        / "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision/latest.json"
    )
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision(
        out, packet
    )
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["approval_record_seal_finalization_decision_hash"] == packet["approval_record_seal_finalization_decision_hash"]
    assert loaded["approval_record_seal_finalization_decision_status"] == packet["approval_record_seal_finalization_decision_status"]


def test_all_allowed_decisions_route_correctly(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    for decision in ALLOWED_DECISIONS:
        human = _make_valid_human_artifact(fh, decision)
        packet = _build(tmp_path, human_packet=human)
        assert packet["approval_record_seal_finalization_decision_status"] in (
            _STATUS_APPROVED, _STATUS_REJECTED
        ), f"unexpected status for decision={decision!r}: {packet['approval_record_seal_finalization_decision_status']}"
        assert packet["decision_recorded"] is True


def test_all_forbidden_decisions_fail(tmp_path: Path) -> None:
    _seed_p103(tmp_path)
    fh = _p103_file_hash(tmp_path)
    for decision in FORBIDDEN_DECISIONS:
        human = _make_valid_human_artifact(fh, decision)
        packet = _build(tmp_path, human_packet=human)
        assert packet["approval_record_seal_finalization_decision_status"] == _STATUS_FAILED, (
            f"expected FAILED for forbidden decision={decision!r}"
        )


def test_doctrine_validator_nonregression() -> None:
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "seal" in result.stdout
