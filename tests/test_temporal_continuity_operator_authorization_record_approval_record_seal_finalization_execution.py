from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution import (
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution,
    _FINALIZATION_CHAIN_SOURCES,
)

_STATUS_SIMULATED_COMPLETE = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION_SIMULATED_COMPLETE"
)
_STATUS_BLOCKED = (
    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN"
)
_STATUS_FAILED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION_FAILED"
)
_STATUS_NOT_COMPUTABLE = "NOT_COMPUTABLE"

_NEXT_P103 = (
    "P103_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_REVIEW"
)
_NEXT_P101 = (
    "P101_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN"
)

_P101_SOURCE = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan/latest.json"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


def _seed_chain_artifacts(root: Path) -> None:
    artifacts = {
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision/latest.json": {
            "approval_record_seal_operator_decision_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD",
            "authorization_granted": False, "approval_granted": False,
            "approval_record_sealed": False, "execution_authority": False,
            "token_minting_allowed": False, "valid_for_execution": False,
            "finalization_authorized": False,
        },
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan/latest.json": {
            "approval_record_seal_execution_plan_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY",
            "authorization_granted": False, "approval_granted": False,
            "approval_record_sealed": False, "execution_authority": False,
            "token_minting_allowed": False, "valid_for_execution": False,
            "finalization_authorized": False,
        },
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution/latest.json": {
            "approval_record_seal_execution_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_SIMULATED_COMPLETE",
            "authorization_granted": False, "approval_granted": False,
            "approval_record_sealed": False, "execution_authority": False,
            "token_minting_allowed": False, "valid_for_execution": False,
            "finalization_authorized": False,
        },
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization/latest.json": {
            "finalization_authorization_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_ELIGIBLE",
            "authorization_granted": False, "approval_granted": False,
            "approval_record_sealed": False, "execution_authority": False,
            "token_minting_allowed": False, "valid_for_execution": False,
            "finalization_authorized": False,
        },
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record/latest.json": {
            "finalization_authorization_record_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_AUTHORIZED_RECORD",
            "authorization_granted": False, "approval_granted": False,
            "approval_record_sealed": False, "execution_authority": False,
            "token_minting_allowed": False, "valid_for_execution": False,
            "finalization_authorized": False,
        },
    }
    for rel_path, payload in artifacts.items():
        _write_json(root / rel_path, payload)


def _seed_p101(
    root: Path,
    *,
    status: str = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN_READY",
    plan_ready: bool = True,
    inject: dict[str, object] | None = None,
) -> Path:
    p101_path = root / _P101_SOURCE
    base: dict[str, object] = {
        "finalization_plan_status": status,
        "plan_ready": plan_ready,
        "approval_record_seal_finalization_plan_hash": (
            "cb02017477114ba8534def93b779995d6f127eb231061b9bf6e86d6e849c967f"
        ),
        "p100_authorization_record_hash_anchor": (
            "22fa2e3d8ed1c4e9decbfe5cbbb3e78e612ab11d4749693a462cc84534ae3afc"
        ),
        "p100_authorization_id_anchor": "P100_FINALIZATION_AUTHORIZATION_2026_05_28_001",
        "p100_operator_id_anchor": "Daniel Meyer",
        "p100_authorization_value_anchor": "authorize_finalization_record",
        "p96_decision_provenance_reanchor": {
            "autonomous_approval": False,
            "decision_id": "P96_OPERATOR_DECISION_2026_05_28_001",
            "decision_value": "approve_seal_record",
            "operator_id": "Daniel Meyer",
            "p96_decision_hash": "1d9fb64f294609748f75eefb6510731041f43c982e0922c20cb6ade64dfa1d73",
            "p97_execution_plan_hash": "8a7894653c3382c4f7026425bc98712fa309fef53761222a20f7cea8daeeb8b1",
            "p98_execution_hash": "459fed62649b15e3887ce1a1999de4e10f5d838e25a60f01dbd9bb16eb2f2d62",
            "provenance_anchor_valid": True,
        },
        "finalization_plan_summary": {
            "all_steps_advisory": True,
            "finalization_authority_required_externally": True,
            "finalization_plan_only": True,
            "seal_not_executed": True,
            "finalization_not_executed": True,
            "step_count": 5,
        },
        "plan_only_attestation": {
            "no_finalization_executed": True,
            "no_execution_authority_created": True,
            "no_seal_executed": True,
            "plan_preparation_only": True,
        },
        "advisory_only": True,
        "projection_only": True,
        "finalization_plan_only": True,
        "approval_record_seal_finalization_plan_only": True,
        "operator_approval_required": True,
        "approval_record_sealed": False,
        "approval_record_created": False,
        "approval_granted": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "execution_authority": False,
        "authorization_authority": False,
        "plan_creation_authority": False,
        "mutation_allowed": False,
        "forecast_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "baseline_mutation": False,
        "runtime_mutation": False,
        "governance_authority_mutation": False,
        "plan_blockers": [],
    }
    if inject:
        for k, v in inject.items():
            base[k] = v
    _write_json(p101_path, base)
    return p101_path


def _build(root: Path) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution(
        repo_root=root,
    )


def test_missing_p101_not_computable(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_NOT_COMPUTABLE
    assert packet["finalization_recorded"] is False
    assert packet["actual_finalization_executed"] is False
    assert packet["simulated_finalization_only"] is True
    assert packet["finalization_authorized"] is False
    assert packet["authorization_granted"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["advisory_only"] is True
    assert _NEXT_P101 in packet["recommended_next_lane"]
    h = packet["approval_record_seal_finalization_execution_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_blocked_wrong_status(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(
        tmp_path,
        status="OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN_BLOCKED",
        plan_ready=False,
    )
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_BLOCKED
    assert packet["finalization_recorded"] is False
    assert _NEXT_P101 in packet["recommended_next_lane"]


def test_blocked_plan_ready_false(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(
        tmp_path,
        status="OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN_READY",
        plan_ready=False,
    )
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_BLOCKED
    assert packet["finalization_recorded"] is False
    assert any("plan_ready" in b for b in packet["execution_blockers"])


def test_simulated_complete_valid_inputs(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_SIMULATED_COMPLETE
    assert packet["finalization_recorded"] is True
    assert packet["simulated_finalization_only"] is True
    assert packet["actual_finalization_executed"] is False
    assert packet["finalization_authorized"] is False
    assert packet["authorization_granted"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["mutation_allowed"] is False
    assert packet["production_activation"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["finalization_execution_only"] is True
    assert packet["approval_record_seal_finalization_execution_only"] is True
    assert packet["execution_blockers"] == []
    assert _NEXT_P103 in packet["recommended_next_lane"]


def test_simulated_finalization_record_sentinels(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    rec = packet["simulated_finalization_record"]
    assert rec["simulated_only"] is True
    assert rec["actual_finalization_executed"] is False
    assert rec["approval_record_sealed"] is False
    assert rec["finalization_authorized"] is False
    assert rec["authorization_granted"] is False
    assert rec["valid_for_execution"] is False
    for field in ("simulated_finalization_id", "simulated_finalization_hash",
                  "simulated_finalization_token", "simulated_finalization_signature",
                  "simulated_finalization_completed_at"):
        assert "SIMULATED" in rec[field], f"{field} must contain SIMULATED"
    sc = packet["simulated_sentinel_check"]
    assert sc["check_passed"] is True
    assert sc["sentinel_strings_all_contain_simulated_marker"] is True
    assert sc["actual_finalization_executed_is_false"] is True
    assert sc["approval_record_sealed_is_false"] is True
    assert sc["finalization_authorized_is_false"] is True


def test_finalization_chain_verification_all_passed(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    chain = packet["finalization_chain_verification"]
    assert len(chain) == 6
    assert all(c["passed"] is True for c in chain)
    check_ids = [c["check_id"] for c in chain]
    assert "p96_seal_operator_decision_approved" in check_ids
    assert "p97_seal_execution_plan_ready" in check_ids
    assert "p98_seal_execution_simulated_complete" in check_ids
    assert "p99_finalization_authorization_eligible" in check_ids
    assert "p100_finalization_authorization_record_authorized" in check_ids
    assert "p101_finalization_plan_ready" in check_ids


def test_finalization_chain_step_count_verified(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    assert packet["simulated_finalization_summary"]["step_count_verified"] == 6
    assert packet["simulated_finalization_summary"]["actual_finalization_executed"] is False
    assert packet["simulated_finalization_summary"]["simulated_only"] is True
    assert packet["simulated_finalization_summary"]["finalization_authority_granted"] is False


def test_authority_invariant_checks_all_passed(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    inv = packet["finalization_authority_invariant_checks"]
    assert len(inv) == len(_FINALIZATION_CHAIN_SOURCES) * 7
    assert all(c["passed"] is True for c in inv)


def test_finalization_provenance_chain_embedded(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    chain = packet["finalization_provenance_chain"]
    assert chain["p96_seal_operator_decision_hash"] == (
        "1d9fb64f294609748f75eefb6510731041f43c982e0922c20cb6ade64dfa1d73"
    )
    assert chain["p97_seal_execution_plan_hash"] == (
        "8a7894653c3382c4f7026425bc98712fa309fef53761222a20f7cea8daeeb8b1"
    )
    assert chain["p98_seal_execution_hash"] == (
        "459fed62649b15e3887ce1a1999de4e10f5d838e25a60f01dbd9bb16eb2f2d62"
    )
    assert chain["p100_authorization_record_hash"] == (
        "22fa2e3d8ed1c4e9decbfe5cbbb3e78e612ab11d4749693a462cc84534ae3afc"
    )
    assert chain["autonomous_approval"] is False
    assert chain["operator_id"] == "Daniel Meyer"


def test_failed_p101_posture_authority_lock(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path, inject={"authorization_granted": True})
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_FAILED
    assert packet["finalization_recorded"] is False
    assert packet["authorization_granted"] is False


def test_failed_p101_posture_finalization_authorized(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path, inject={"finalization_authorized": True})
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_FAILED
    assert packet["finalization_authorized"] is False


def test_failed_p101_posture_summary_malformed(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path, inject={"finalization_plan_summary": {"all_steps_advisory": False}})
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_FAILED
    assert packet["finalization_recorded"] is False


def test_failed_p101_attestation_no_finalization_executed_missing(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path, inject={
        "plan_only_attestation": {
            "no_finalization_executed": False,
            "no_seal_executed": True,
            "plan_preparation_only": True,
        }
    })
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_FAILED


def test_failed_chain_artifact_lock_violation(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    corrupt = {
        "approval_record_seal_operator_decision_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD",
        "authorization_granted": True,
        "approval_granted": False, "approval_record_sealed": False,
        "execution_authority": False, "token_minting_allowed": False,
        "valid_for_execution": False, "finalization_authorized": False,
    }
    _write_json(
        tmp_path / "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision/latest.json",
        corrupt,
    )
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_FAILED
    assert packet["authorization_granted"] is False
    assert packet["finalization_recorded"] is False


def test_failed_chain_status_mismatch(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _write_json(
        tmp_path / "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution/latest.json",
        {
            "approval_record_seal_execution_status": "BLOCKED_BY_SOMETHING",
            "authorization_granted": False, "approval_granted": False,
            "approval_record_sealed": False, "execution_authority": False,
            "token_minting_allowed": False, "valid_for_execution": False,
            "finalization_authorized": False,
        },
    )
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_FAILED
    chain = packet["finalization_chain_verification"]
    p98_check = next(c for c in chain if c["check_id"] == "p98_seal_execution_simulated_complete")
    assert p98_check["passed"] is False


def test_authority_locks_hardcoded_on_all_paths(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path, inject={
        "authorization_granted": True,
        "finalization_authorized": True,
        "approval_record_sealed": True,
        "valid_for_execution": True,
        "execution_authority": True,
        "token_minting_allowed": True,
    })
    packet = _build(tmp_path)
    assert packet["finalization_execution_status"] == _STATUS_FAILED
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["actual_finalization_executed"] is False
    assert packet["simulated_finalization_only"] is True
    assert packet["production_activation"] is False
    assert packet["canon_promotion"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["baseline_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["governance_authority_mutation"] is False


def test_schema_and_id(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationExecution.v1"
    )
    assert packet["approval_record_seal_finalization_execution_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution_001"
    )


def test_hash_validation(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    h = packet["approval_record_seal_finalization_execution_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)
    from core.canonical.json import canonical_hash
    packet_base = {k: v for k, v in packet.items() if k != "approval_record_seal_finalization_execution_hash"}
    assert canonical_hash(packet_base) == h


def test_determinism(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path)
    p1 = _build(tmp_path)
    p2 = _build(tmp_path)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert p1["approval_record_seal_finalization_execution_hash"] == p2["approval_record_seal_finalization_execution_hash"]


def test_write_function(tmp_path: Path) -> None:
    _seed_chain_artifacts(tmp_path)
    _seed_p101(tmp_path)
    packet = _build(tmp_path)
    out = (
        tmp_path
        / "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution/latest.json"
    )
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution(
        out, packet
    )
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["approval_record_seal_finalization_execution_hash"] == packet["approval_record_seal_finalization_execution_hash"]
    assert loaded["finalization_execution_status"] == packet["finalization_execution_status"]


def test_doctrine_validator_nonregression() -> None:
    import subprocess
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "seal" in result.stdout
