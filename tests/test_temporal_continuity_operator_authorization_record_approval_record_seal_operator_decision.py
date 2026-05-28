from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision import (
    ALLOWED_DECISIONS,
    FORBIDDEN_DECISIONS,
    build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision,
)

SOURCE = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_review/latest.json"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


def _seed_p95(root: Path, status: str, review_passed: bool = True) -> Path:
    p = root / SOURCE
    _write_json(
        p,
        {
            "approval_record_seal_operator_review_status": status,
            "approval_record_seal_operator_review_id": (
                "temporal_continuity_operator_authorization_record_approval_record_seal_operator_review_001"
            ),
            "approval_record_seal_operator_review_hash": (
                "aaabbbcccdddeeefff0001112223334445556667778889990001112223334445"
            ),
            "review_passed": review_passed,
            "dry_run_check_summary": {"total": 30, "passed": 30, "failed": 0},
            "advisory_only": True,
            "projection_only": True,
            "approval_record_sealed": False,
            "approval_record_created": False,
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "valid_for_execution": False,
            "operator_approval_required": True,
        },
    )
    return p


def _p95_file_sha256(root: Path) -> str:
    p = root / SOURCE
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _make_decision_artifact(
    decision: str,
    file_hash: str,
    *,
    advisory_ack: bool = True,
    no_exec_ack: bool = True,
    decision_id: str = "test_decision_001",
    operator_id: str = "test_operator",
) -> dict[str, object]:
    return {
        "decision": decision,
        "decision_id": decision_id,
        "operator_id": operator_id,
        "operator_attestation": "attested",
        "decision_rationale": "test rationale",
        "upstream_review_hash": file_hash,
        "advisory_only_acknowledged": advisory_ack,
        "no_execution_authority_granted_acknowledged": no_exec_ack,
    }


def _build(root: Path, human_decision_packet: dict | None = None) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision(
        repo_root=root,
        human_decision_packet=human_decision_packet,
    )


def test_missing_p95_fails_closed(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    assert packet["approval_record_seal_operator_decision_status"] == "NOT_COMPUTABLE"
    assert packet["decision_recorded"] is False
    assert packet["autonomous_approval"] is False
    assert packet["approval_granted"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["recommended_next_lane"] == (
        "P95_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW"
    )
    h = packet["approval_record_seal_operator_decision_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_not_ready_p95_blocks(tmp_path: Path) -> None:
    _seed_p95(tmp_path, "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN")
    packet = _build(tmp_path)
    assert packet["approval_record_seal_operator_decision_status"] == (
        "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW"
    )
    assert packet["decision_recorded"] is False
    assert packet["approval_granted"] is False
    assert packet["recommended_next_lane"] == (
        "P95_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW"
    )


def test_p95_review_passed_false_blocks(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
        review_passed=False,
    )
    packet = _build(tmp_path)
    assert packet["approval_record_seal_operator_decision_status"] == (
        "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW"
    )
    assert packet["decision_recorded"] is False


def test_no_decision_artifact_yields_pending(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    packet = _build(tmp_path)
    assert packet["approval_record_seal_operator_decision_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_PENDING"
    )
    assert packet["decision_recorded"] is True
    assert packet["human_decision_artifact_present"] is False
    assert packet["operator_decision_record"]["decision_value"] == "PENDING_OPERATOR_INPUT"
    assert packet["operator_decision_record"]["autonomous_approval"] is False
    assert packet["autonomous_approval"] is False
    assert packet["recommended_next_lane"] == (
        "P96_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION"
    )
    assert packet["approval_granted"] is False
    assert packet["valid_for_execution"] is False
    assert packet["approval_record_sealed"] is False


def test_approved_decision_record(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    file_hash = _p95_file_sha256(tmp_path)
    artifact = _make_decision_artifact("approve_seal_record", file_hash)
    packet = _build(tmp_path, artifact)
    assert packet["approval_record_seal_operator_decision_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD"
    )
    assert packet["human_decision_artifact_present"] is True
    assert packet["operator_decision_record"]["decision_value"] == "approve_seal_record"
    assert packet["operator_decision_record"]["upstream_review_hash_match"] is True
    assert packet["operator_decision_record"]["approval_granted"] is False
    assert packet["operator_decision_record"]["authorization_granted"] is False
    assert packet["operator_decision_record"]["execution_authority"] is False
    assert packet["operator_decision_record"]["approval_record_sealed"] is False
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["valid_for_execution"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["autonomous_approval"] is False
    assert packet["recommended_next_lane"] == (
        "P97_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN"
    )
    assert packet["decision_recorded"] is True
    assert packet["decision_blockers"] == []
    assert all(item.get("passed") is True for item in packet["decision_posture_audit"])


def test_rejected_decision_record(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    file_hash = _p95_file_sha256(tmp_path)
    artifact = _make_decision_artifact("reject_seal_record", file_hash)
    packet = _build(tmp_path, artifact)
    assert packet["approval_record_seal_operator_decision_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_REJECTED_RECORD"
    )
    assert packet["approval_granted"] is False
    assert packet["valid_for_execution"] is False
    assert packet["decision_recorded"] is True
    assert packet["recommended_next_lane"].startswith(
        "P95_TEMPORAL_CONTINUITY_"
    )


def test_hold_decision_record(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    file_hash = _p95_file_sha256(tmp_path)
    artifact = _make_decision_artifact("hold_pending_further_review", file_hash)
    packet = _build(tmp_path, artifact)
    assert packet["approval_record_seal_operator_decision_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_REJECTED_RECORD"
    )
    assert packet["approval_granted"] is False
    assert packet["decision_recorded"] is True


def test_request_repair_decision_record(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    file_hash = _p95_file_sha256(tmp_path)
    artifact = _make_decision_artifact("request_repair", file_hash)
    packet = _build(tmp_path, artifact)
    assert packet["approval_record_seal_operator_decision_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_REJECTED_RECORD"
    )
    assert packet["recommended_next_lane"].startswith("P94_TEMPORAL_CONTINUITY_")
    assert packet["approval_granted"] is False


def test_forbidden_decision_triggers_fail(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    file_hash = _p95_file_sha256(tmp_path)
    for forbidden in FORBIDDEN_DECISIONS:
        artifact = _make_decision_artifact(forbidden, file_hash)
        packet = _build(tmp_path, artifact)
        assert packet["approval_record_seal_operator_decision_status"] == (
            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_FAILED"
        ), f"Expected FAILED for forbidden decision {forbidden!r}"
        assert packet["approval_granted"] is False
        assert packet["valid_for_execution"] is False
        failed = [a for a in packet["decision_posture_audit"] if not a.get("passed")]
        assert len(failed) > 0


def test_malformed_decision_artifact_fields(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    file_hash = _p95_file_sha256(tmp_path)
    artifact = _make_decision_artifact(
        "approve_seal_record",
        file_hash,
        advisory_ack=False,
        no_exec_ack=False,
        decision_id="",
        operator_id="",
    )
    packet = _build(tmp_path, artifact)
    assert packet["approval_record_seal_operator_decision_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_FAILED"
    )
    assert packet["approval_granted"] is False
    assert packet["valid_for_execution"] is False


def test_hash_mismatch_triggers_fail(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    artifact = _make_decision_artifact("approve_seal_record", "a" * 64)
    packet = _build(tmp_path, artifact)
    assert packet["approval_record_seal_operator_decision_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_FAILED"
    )
    assert packet["operator_decision_record"]["upstream_review_hash_match"] is False
    assert packet["approval_granted"] is False


def test_authority_locks_hardcoded_regardless_of_input(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    file_hash = _p95_file_sha256(tmp_path)
    artifact = _make_decision_artifact("approve_seal_record", file_hash)
    for elevated_field in (
        "approval_granted",
        "authorization_granted",
        "execution_authority",
        "valid_for_execution",
        "approval_record_sealed",
        "token_minting_allowed",
        "mutation_allowed",
    ):
        artifact[elevated_field] = True  # type: ignore[assignment]
    packet = _build(tmp_path, artifact)
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["mutation_allowed"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["operator_approval_required"] is True
    assert packet["approval_record_seal_operator_decision_only"] is True
    assert packet["operator_decision_record_only"] is True
    assert packet["operator_decision_record"]["approval_granted"] is False
    assert packet["operator_decision_record"]["authorization_granted"] is False
    assert packet["operator_decision_record"]["execution_authority"] is False
    assert packet["operator_decision_record"]["approval_record_sealed"] is False


def test_schema_and_hash_validation(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    packet = _build(tmp_path)
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealOperatorDecision.v1"
    )
    assert packet["approval_record_seal_operator_decision_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision_001"
    )
    h = packet["approval_record_seal_operator_decision_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_determinism(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    p1 = _build(tmp_path)
    p2 = _build(tmp_path)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert (
        p1["approval_record_seal_operator_decision_hash"]
        == p2["approval_record_seal_operator_decision_hash"]
    )
    file_hash = _p95_file_sha256(tmp_path)
    artifact = _make_decision_artifact("approve_seal_record", file_hash)
    p3 = _build(tmp_path, artifact)
    p4 = _build(tmp_path, artifact)
    assert json.dumps(p3, sort_keys=True) == json.dumps(p4, sort_keys=True)
    assert (
        p3["approval_record_seal_operator_decision_hash"]
        == p4["approval_record_seal_operator_decision_hash"]
    )


def test_write_function(tmp_path: Path) -> None:
    _seed_p95(
        tmp_path,
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    )
    packet = _build(tmp_path)
    out = tmp_path / "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision/latest.json"
    write_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision(
        out, packet
    )
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert (
        loaded["approval_record_seal_operator_decision_hash"]
        == packet["approval_record_seal_operator_decision_hash"]
    )
    assert (
        loaded["approval_record_seal_operator_decision_status"]
        == packet["approval_record_seal_operator_decision_status"]
    )


def test_allowed_decisions_constants() -> None:
    assert "approve_seal_record" in ALLOWED_DECISIONS
    assert "reject_seal_record" in ALLOWED_DECISIONS
    for f in FORBIDDEN_DECISIONS:
        assert f not in ALLOWED_DECISIONS, f"Forbidden decision {f!r} found in ALLOWED_DECISIONS"


def test_doctrine_validator_nonregression() -> None:
    import subprocess
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "seal" in result.stdout
