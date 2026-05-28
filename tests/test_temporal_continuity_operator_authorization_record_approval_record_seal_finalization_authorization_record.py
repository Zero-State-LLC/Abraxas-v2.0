from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record import (
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record,
)

SOURCE = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization/latest.json"
)

_STATUS_PENDING = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_PENDING"
)
_STATUS_AUTHORIZED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_AUTHORIZED_RECORD"
)
_STATUS_REJECTED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_REJECTED_RECORD"
)
_STATUS_FAILED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_FAILED"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


def _seed_p99(
    root: Path,
    status: str = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_ELIGIBLE",
    eligible: bool = True,
    *,
    inject: dict[str, object] | None = None,
) -> Path:
    p99_path = root / SOURCE
    base: dict[str, object] = {
        "finalization_authorization_status": status,
        "finalization_authorization_eligible": eligible,
        "finalization_authorization_gate_only": True,
        "finalization_authorization_hash": (
            "f5ac6365d8f5dc9c39d7b75155459848e50cb64672dd7fc6a0ac3e93ceee1ec4"
        ),
        "decision_provenance_reanchor": {
            "decision_value": "approve_seal_record",
            "autonomous_approval": False,
            "decision_id": "P96_OPERATOR_DECISION_2026_05_28_001",
            "operator_id": "Daniel Meyer",
            "p96_decision_hash": "1d9fb64f294609748f75eefb6510731041f43c982e0922c20cb6ade64dfa1d73",
            "p97_execution_plan_hash": "8a7894653c3382c4f7026425bc98712fa309fef53761222a20f7cea8daeeb8b1",
            "p98_execution_hash": "459fed62649b15e3887ce1a1999de4e10f5d838e25a60f01dbd9bb16eb2f2d62",
            "provenance_anchor_valid": True,
        },
        "advisory_only": True,
        "projection_only": True,
        "approval_granted": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "execution_authority": False,
        "approval_record_sealed": False,
        "valid_for_execution": False,
        "token_minting_allowed": False,
        "operator_approval_required": True,
    }
    if inject:
        for k, v in inject.items():
            base[k] = v
    _write_json(p99_path, base)
    return p99_path


def _p99_file_hash(root: Path) -> str:
    return hashlib.sha256((root / SOURCE).read_bytes()).hexdigest()


def _seed_human_artifact(
    root: Path,
    *,
    authorization: str = "authorize_finalization_record",
    upstream_gate_hash: str | None = None,
    advisory_only_acknowledged: bool = True,
    no_execution_authority_granted_acknowledged: bool = True,
    no_seal_executed_acknowledged: bool = True,
    finalization_not_executed_acknowledged: bool = True,
    inject: dict[str, object] | None = None,
) -> str:
    if upstream_gate_hash is None:
        upstream_gate_hash = _p99_file_hash(root)
    artifact_path = (
        root / "input/operator_authorization_record_approval_record_seal_finalization_authorization.json"
    )
    base: dict[str, object] = {
        "authorization": authorization,
        "authorization_id": "P100_FINALIZATION_AUTHORIZATION_DECISION_2026_05_28_001",
        "authorization_scope": "P100 finalization authorization record only",
        "operator_id": "Daniel Meyer",
        "upstream_gate_hash": upstream_gate_hash,
        "advisory_only_acknowledged": advisory_only_acknowledged,
        "no_execution_authority_granted_acknowledged": no_execution_authority_granted_acknowledged,
        "no_seal_executed_acknowledged": no_seal_executed_acknowledged,
        "finalization_not_executed_acknowledged": finalization_not_executed_acknowledged,
        "approval_record_sealed": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "valid_for_execution": False,
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "runtime_mutation": False,
        "baseline_mutation": False,
        "governance_authority_mutation": False,
        "note": "Operator authorizes recording finalization authorization posture only.",
    }
    if inject:
        for k, v in inject.items():
            base[k] = v
    _write_json(artifact_path, base)
    return str(artifact_path)


def _build(
    root: Path,
    human_authorization_path: str | None = None,
    human_authorization_packet: dict | None = None,
) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record(
        repo_root=root,
        human_authorization_artifact_path=human_authorization_path,
        human_authorization_packet=human_authorization_packet,
    )


def test_missing_p99_not_computable(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    assert packet["finalization_authorization_record_status"] == "NOT_COMPUTABLE"
    assert packet["authorization_recorded"] is False
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["advisory_only"] is True
    assert "P99_TEMPORAL_CONTINUITY_" in packet["recommended_next_lane"]
    h = packet["finalization_authorization_record_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_not_eligible_p99_blocks(tmp_path: Path) -> None:
    _seed_p99(
        tmp_path,
        status="BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION",
        eligible=False,
    )
    packet = _build(tmp_path)
    assert packet["finalization_authorization_record_status"].startswith("BLOCKED_BY_")
    assert packet["authorization_recorded"] is False
    assert packet["authorization_granted"] is False
    assert "P99_TEMPORAL_CONTINUITY_" in packet["recommended_next_lane"]


def test_missing_human_artifact_pending(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    packet = _build(tmp_path)
    assert packet["finalization_authorization_record_status"] == _STATUS_PENDING
    assert packet["authorization_recorded"] is False
    assert packet["human_authorization_artifact_present"] is False
    assert packet["authorization_value"] == "PENDING_OPERATOR_INPUT"
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert "P100_TEMPORAL_CONTINUITY_" in packet["recommended_next_lane"]


def test_missing_human_artifact_via_path_pending(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    absent_path = str(tmp_path / "input/nonexistent.json")
    packet = _build(tmp_path, human_authorization_path=absent_path)
    assert packet["finalization_authorization_record_status"] == _STATUS_PENDING
    assert packet["authorization_recorded"] is False
    assert packet["authorization_value"] == "PENDING_OPERATOR_INPUT"


def test_valid_artifact_authorized_record(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    artifact_path = _seed_human_artifact(tmp_path)
    packet = _build(tmp_path, human_authorization_path=artifact_path)
    assert packet["finalization_authorization_record_status"] == _STATUS_AUTHORIZED
    assert packet["authorization_recorded"] is True
    assert packet["human_authorization_artifact_present"] is True
    assert packet["authorization_value"] == "authorize_finalization_record"
    assert packet["upstream_gate_hash_match"] is True
    assert packet["advisory_only_acknowledged"] is True
    assert packet["no_execution_authority_granted_acknowledged"] is True
    assert packet["no_seal_executed_acknowledged"] is True
    assert packet["finalization_not_executed_acknowledged"] is True
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["authorization_record_only"] is True
    assert packet["finalization_authorization_record_only"] is True
    assert "P101_TEMPORAL_CONTINUITY_" in packet["recommended_next_lane"]
    assert packet["blockers"] == []
    rec = packet["finalization_authorization_record"]
    assert rec["authorization_value"] == "authorize_finalization_record"
    assert rec["authorization_granted"] is False
    assert rec["finalization_authorized"] is False
    assert rec["approval_record_sealed"] is False
    assert all(c["passed"] is True for c in packet["decision_audit"])


def test_rejected_authorization_recorded(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    artifact_path = _seed_human_artifact(
        tmp_path, authorization="reject_finalization_authorization"
    )
    packet = _build(tmp_path, human_authorization_path=artifact_path)
    assert packet["finalization_authorization_record_status"] == _STATUS_REJECTED
    assert packet["authorization_recorded"] is True
    assert packet["authorization_value"] == "reject_finalization_authorization"
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert "P99_TEMPORAL_CONTINUITY_" in packet["recommended_next_lane"]


def test_wrong_upstream_gate_hash_blocks(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    artifact_path = _seed_human_artifact(tmp_path, upstream_gate_hash="aabbcc0011223344deadbeef")
    packet = _build(tmp_path, human_authorization_path=artifact_path)
    assert packet["finalization_authorization_record_status"].startswith("BLOCKED_BY_") or \
           packet["finalization_authorization_record_status"].endswith("_FAILED")
    assert packet["upstream_gate_hash_match"] is False
    assert packet["authorization_recorded"] is False


def test_missing_acknowledgement_blocks(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    artifact_path = _seed_human_artifact(tmp_path, advisory_only_acknowledged=False)
    packet = _build(tmp_path, human_authorization_path=artifact_path)
    assert packet["finalization_authorization_record_status"].startswith("BLOCKED_BY_") or \
           packet["finalization_authorization_record_status"].endswith("_FAILED")
    assert packet["authorization_recorded"] is False
    assert packet["advisory_only_acknowledged"] is False


def test_missing_no_seal_executed_acknowledged_blocks(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    artifact_path = _seed_human_artifact(tmp_path, no_seal_executed_acknowledged=False)
    packet = _build(tmp_path, human_authorization_path=artifact_path)
    assert packet["authorization_recorded"] is False


def test_missing_finalization_not_executed_acknowledged_blocks(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    artifact_path = _seed_human_artifact(tmp_path, finalization_not_executed_acknowledged=False)
    packet = _build(tmp_path, human_authorization_path=artifact_path)
    assert packet["authorization_recorded"] is False


def test_unrecognized_authorization_value_blocks(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    artifact_path = _seed_human_artifact(tmp_path, authorization="approve_everything")
    packet = _build(tmp_path, human_authorization_path=artifact_path)
    assert packet["finalization_authorization_record_status"].startswith("BLOCKED_BY_") or \
           packet["finalization_authorization_record_status"].endswith("_FAILED")
    assert packet["authorization_recorded"] is False


def test_human_artifact_authority_lock_violation_fails(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    artifact_path = _seed_human_artifact(
        tmp_path, inject={"authorization_granted": True}
    )
    packet = _build(tmp_path, human_authorization_path=artifact_path)
    assert packet["finalization_authorization_record_status"] == _STATUS_FAILED
    assert packet["authorization_recorded"] is False
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False


def test_finalization_authorized_always_false(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    artifact_path = _seed_human_artifact(
        tmp_path, inject={"finalization_authorized": True}
    )
    packet = _build(tmp_path, human_authorization_path=artifact_path)
    assert packet["finalization_authorized"] is False
    assert packet["finalization_authorization_record_status"] == _STATUS_FAILED


def test_authority_locks_hardcoded_regardless_of_p99_input(tmp_path: Path) -> None:
    _seed_p99(
        tmp_path,
        inject={
            "authorization_granted": True,
            "approval_record_sealed": True,
            "valid_for_execution": True,
            "execution_authority": True,
            "token_minting_allowed": True,
        },
    )
    packet = _build(tmp_path)
    assert packet["finalization_authorization_record_status"] == _STATUS_FAILED
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False


def test_p96_decision_provenance_reanchor_embedded(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    packet = _build(tmp_path)
    reanchor = packet["p96_decision_provenance_reanchor"]
    assert reanchor["decision_value"] == "approve_seal_record"
    assert reanchor["autonomous_approval"] is False
    assert reanchor["operator_id"] == "Daniel Meyer"


def test_p99_gate_hash_anchor_embedded(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    packet = _build(tmp_path)
    assert packet["p99_gate_hash_anchor"] == (
        "f5ac6365d8f5dc9c39d7b75155459848e50cb64672dd7fc6a0ac3e93ceee1ec4"
    )


def test_schema_and_hash_validation(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    packet = _build(tmp_path)
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationAuthorizationRecord.v1"
    )
    assert packet["finalization_authorization_record_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record_001"
    )
    h = packet["finalization_authorization_record_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_determinism(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    artifact_path = _seed_human_artifact(tmp_path)
    p1 = _build(tmp_path, human_authorization_path=artifact_path)
    p2 = _build(tmp_path, human_authorization_path=artifact_path)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert p1["finalization_authorization_record_hash"] == p2["finalization_authorization_record_hash"]


def test_write_function(tmp_path: Path) -> None:
    _seed_p99(tmp_path)
    packet = _build(tmp_path)
    out = (
        tmp_path
        / "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record/latest.json"
    )
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record(
        out, packet
    )
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["finalization_authorization_record_hash"] == packet["finalization_authorization_record_hash"]
    assert loaded["finalization_authorization_record_status"] == packet["finalization_authorization_record_status"]


def test_doctrine_validator_nonregression() -> None:
    import subprocess
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "seal" in result.stdout
