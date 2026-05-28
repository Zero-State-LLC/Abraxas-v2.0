from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan import (
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan,
)

SOURCE = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record/latest.json"
)

_STATUS_PLAN_READY = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN_READY"
)
_STATUS_BLOCKED = (
    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD"
)
_STATUS_FAILED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN_FAILED"
)
_STATUS_NOT_COMPUTABLE = "NOT_COMPUTABLE"

_NEXT_P102 = (
    "P102_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION"
)
_NEXT_P100 = (
    "P100_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


def _seed_p100(
    root: Path,
    *,
    status: str = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_AUTHORIZED_RECORD",
    authorization_recorded: bool = True,
    autonomous_approval: bool = False,
    inject: dict[str, object] | None = None,
) -> Path:
    p100_path = root / SOURCE
    base: dict[str, object] = {
        "finalization_authorization_record_status": status,
        "authorization_recorded": authorization_recorded,
        "authorization_value": "authorize_finalization_record",
        "authorization_id": "P100_FINALIZATION_AUTHORIZATION_2026_05_28_001",
        "authorization_scope": "P100 finalization authorization record only",
        "operator_id": "Daniel Meyer",
        "finalization_authorization_record_hash": (
            "22fa2e3d8ed1c4e9decbfe5cbbb3e78e612ab11d4749693a462cc84534ae3afc"
        ),
        "p96_decision_provenance_reanchor": {
            "autonomous_approval": autonomous_approval,
            "decision_id": "P96_OPERATOR_DECISION_2026_05_28_001",
            "decision_value": "approve_seal_record",
            "operator_id": "Daniel Meyer",
            "p96_decision_hash": "1d9fb64f294609748f75eefb6510731041f43c982e0922c20cb6ade64dfa1d73",
            "p97_execution_plan_hash": "8a7894653c3382c4f7026425bc98712fa309fef53761222a20f7cea8daeeb8b1",
            "p98_execution_hash": "459fed62649b15e3887ce1a1999de4e10f5d838e25a60f01dbd9bb16eb2f2d62",
            "provenance_anchor_valid": True,
        },
        "advisory_only": True,
        "projection_only": True,
        "authorization_record_only": True,
        "finalization_authorization_record_only": True,
        "operator_approval_required": True,
        "approval_record_sealed": False,
        "approval_record_created": False,
        "approval_granted": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "execution_authority": False,
        "authorization_authority": False,
        "mutation_allowed": False,
        "forecast_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
    }
    if inject:
        for k, v in inject.items():
            base[k] = v
    _write_json(p100_path, base)
    return p100_path


def _build(root: Path) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan(
        repo_root=root,
    )


def test_missing_p100_not_computable(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    assert packet["finalization_plan_status"] == _STATUS_NOT_COMPUTABLE
    assert packet["plan_ready"] is False
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["advisory_only"] is True
    assert packet["finalization_plan_only"] is True
    assert packet["approval_record_seal_finalization_plan_only"] is True
    assert _NEXT_P100 in packet["recommended_next_lane"]
    h = packet["approval_record_seal_finalization_plan_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_plan_ready_valid_p100(tmp_path: Path) -> None:
    _seed_p100(tmp_path)
    packet = _build(tmp_path)
    assert packet["finalization_plan_status"] == _STATUS_PLAN_READY
    assert packet["plan_ready"] is True
    assert packet["plan_blockers"] == []
    assert _NEXT_P102 in packet["recommended_next_lane"]
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["mutation_allowed"] is False
    assert packet["production_activation"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["finalization_plan_only"] is True
    assert packet["approval_record_seal_finalization_plan_only"] is True


def test_plan_only_attestation_all_true(tmp_path: Path) -> None:
    _seed_p100(tmp_path)
    packet = _build(tmp_path)
    att = packet["plan_only_attestation"]
    assert att["no_finalization_executed"] is True
    assert att["no_execution_authority_created"] is True
    assert att["no_seal_executed"] is True
    assert att["plan_preparation_only"] is True


def test_finalization_plan_summary_fields(tmp_path: Path) -> None:
    _seed_p100(tmp_path)
    packet = _build(tmp_path)
    s = packet["finalization_plan_summary"]
    assert s["all_steps_advisory"] is True
    assert s["finalization_authority_required_externally"] is True
    assert s["finalization_plan_only"] is True
    assert s["seal_not_executed"] is True
    assert s["finalization_not_executed"] is True
    assert s["step_count"] == 5


def test_p100_anchors_embedded(tmp_path: Path) -> None:
    _seed_p100(tmp_path)
    packet = _build(tmp_path)
    assert packet["p100_authorization_record_hash_anchor"] == (
        "22fa2e3d8ed1c4e9decbfe5cbbb3e78e612ab11d4749693a462cc84534ae3afc"
    )
    assert packet["p100_authorization_id_anchor"] == "P100_FINALIZATION_AUTHORIZATION_2026_05_28_001"
    assert packet["p100_operator_id_anchor"] == "Daniel Meyer"
    assert packet["p100_authorization_value_anchor"] == "authorize_finalization_record"


def test_p96_provenance_reanchor_embedded(tmp_path: Path) -> None:
    _seed_p100(tmp_path)
    packet = _build(tmp_path)
    reanchor = packet["p96_decision_provenance_reanchor"]
    assert reanchor["decision_value"] == "approve_seal_record"
    assert reanchor["autonomous_approval"] is False
    assert reanchor["operator_id"] == "Daniel Meyer"
    assert "p96_decision_hash" in reanchor
    assert "p97_execution_plan_hash" in reanchor
    assert "p98_execution_hash" in reanchor


def test_blocked_wrong_status(tmp_path: Path) -> None:
    _seed_p100(
        tmp_path,
        status="OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_PENDING",
        authorization_recorded=False,
    )
    packet = _build(tmp_path)
    assert packet["finalization_plan_status"] == _STATUS_BLOCKED
    assert packet["plan_ready"] is False
    assert _NEXT_P100 in packet["recommended_next_lane"]


def test_blocked_authorization_not_recorded(tmp_path: Path) -> None:
    _seed_p100(
        tmp_path,
        status="OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_AUTHORIZED_RECORD",
        authorization_recorded=False,
    )
    packet = _build(tmp_path)
    assert packet["finalization_plan_status"] == _STATUS_BLOCKED
    assert packet["plan_ready"] is False
    assert any("authorization_recorded" in b for b in packet["plan_blockers"])


def test_blocked_autonomous_approval(tmp_path: Path) -> None:
    _seed_p100(tmp_path, autonomous_approval=True)
    packet = _build(tmp_path)
    assert packet["finalization_plan_status"] == _STATUS_BLOCKED
    assert packet["plan_ready"] is False
    assert any("autonomous" in b for b in packet["plan_blockers"])
    assert _NEXT_P100 in packet["recommended_next_lane"]


def test_failed_authorization_granted_lock(tmp_path: Path) -> None:
    _seed_p100(tmp_path, inject={"authorization_granted": True})
    packet = _build(tmp_path)
    assert packet["finalization_plan_status"] == _STATUS_FAILED
    assert packet["plan_ready"] is False
    assert packet["authorization_granted"] is False


def test_failed_finalization_authorized_lock(tmp_path: Path) -> None:
    _seed_p100(tmp_path, inject={"finalization_authorized": True})
    packet = _build(tmp_path)
    assert packet["finalization_plan_status"] == _STATUS_FAILED
    assert packet["plan_ready"] is False
    assert packet["finalization_authorized"] is False


def test_failed_approval_record_sealed_lock(tmp_path: Path) -> None:
    _seed_p100(tmp_path, inject={"approval_record_sealed": True})
    packet = _build(tmp_path)
    assert packet["finalization_plan_status"] == _STATUS_FAILED
    assert packet["plan_ready"] is False
    assert packet["approval_record_sealed"] is False


def test_failed_valid_for_execution_lock(tmp_path: Path) -> None:
    _seed_p100(tmp_path, inject={"valid_for_execution": True})
    packet = _build(tmp_path)
    assert packet["finalization_plan_status"] == _STATUS_FAILED
    assert packet["valid_for_execution"] is False


def test_authority_locks_hardcoded_regardless_of_source(tmp_path: Path) -> None:
    _seed_p100(
        tmp_path,
        inject={
            "authorization_granted": True,
            "finalization_authorized": True,
            "approval_record_sealed": True,
            "valid_for_execution": True,
            "execution_authority": True,
            "token_minting_allowed": True,
        },
    )
    packet = _build(tmp_path)
    assert packet["finalization_plan_status"] == _STATUS_FAILED
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["mutation_allowed"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["production_activation"] is False
    assert packet["canon_promotion"] is False


def test_schema_and_id(tmp_path: Path) -> None:
    _seed_p100(tmp_path)
    packet = _build(tmp_path)
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationPlan.v1"
    )
    assert packet["approval_record_seal_finalization_plan_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan_001"
    )


def test_hash_validation(tmp_path: Path) -> None:
    _seed_p100(tmp_path)
    packet = _build(tmp_path)
    h = packet["approval_record_seal_finalization_plan_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)

    from core.canonical.json import canonical_hash
    packet_base = {k: v for k, v in packet.items() if k != "approval_record_seal_finalization_plan_hash"}
    assert canonical_hash(packet_base) == h


def test_determinism(tmp_path: Path) -> None:
    _seed_p100(tmp_path)
    p1 = _build(tmp_path)
    p2 = _build(tmp_path)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert p1["approval_record_seal_finalization_plan_hash"] == p2["approval_record_seal_finalization_plan_hash"]


def test_write_function(tmp_path: Path) -> None:
    _seed_p100(tmp_path)
    packet = _build(tmp_path)
    out = (
        tmp_path
        / "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan/latest.json"
    )
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan(
        out, packet
    )
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["approval_record_seal_finalization_plan_hash"] == packet["approval_record_seal_finalization_plan_hash"]
    assert loaded["finalization_plan_status"] == packet["finalization_plan_status"]


def test_doctrine_validator_nonregression() -> None:
    import subprocess
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "seal" in result.stdout
