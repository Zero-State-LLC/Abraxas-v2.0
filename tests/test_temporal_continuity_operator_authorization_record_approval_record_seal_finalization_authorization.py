from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization import (
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization,
)

SOURCE = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution/latest.json"
)
P93_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json"
P94_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"
P95_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_review/latest.json"
P96_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision/latest.json"
P97_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


def _seed_p98(
    root: Path,
    status: str = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_SIMULATED_COMPLETE",
    simulated_only: bool = True,
    actual_seal_executed: bool = False,
    execution_recorded: bool = True,
    sentinel_check_passed: bool = True,
    step_count_verified: int = 5,
    decision_value: str = "approve_seal_record",
    autonomous_approval: bool = False,
    *,
    inject: dict[str, object] | None = None,
) -> None:
    base: dict[str, object] = {
        "approval_record_seal_execution_status": status,
        "approval_record_seal_execution_hash": (
            "459fed62649b15e3887ce1a1999de4e10f5d838e25a60f01dbd9bb16eb2f2d62"
        ),
        "simulated_only": simulated_only,
        "actual_seal_executed": actual_seal_executed,
        "execution_recorded": execution_recorded,
        "simulated_sentinel_check": {
            "check_passed": sentinel_check_passed,
            "sentinel_strings_all_contain_simulated_marker": sentinel_check_passed,
            "simulated_only_flag_set": sentinel_check_passed,
            "actual_seal_executed_is_false": sentinel_check_passed,
            "approval_record_sealed_is_false": sentinel_check_passed,
        },
        "simulated_execution_summary": {
            "simulated_only": simulated_only,
            "actual_seal_executed": actual_seal_executed,
            "approval_record_sealed": False,
            "execution_authority_granted": False,
            "step_count_verified": step_count_verified,
        },
        "full_provenance_chain": {
            "decision_value": decision_value,
            "autonomous_approval": autonomous_approval,
            "decision_id": "P96_OPERATOR_DECISION_2026_05_28_001",
            "operator_id": "Daniel Meyer",
            "p96_seal_operator_decision_hash": (
                "1d9fb64f294609748f75eefb6510731041f43c982e0922c20cb6ade64dfa1d73"
            ),
            "p97_seal_execution_plan_hash": (
                "8a7894653c3382c4f7026425bc98712fa309fef53761222a20f7cea8daeeb8b1"
            ),
        },
        "source_execution_plan_status": (
            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY"
        ),
        "advisory_only": True,
        "projection_only": True,
        "approval_granted": False,
        "authorization_granted": False,
        "execution_authority": False,
        "approval_record_sealed": False,
        "valid_for_execution": False,
        "token_minting_allowed": False,
        "operator_approval_required": True,
    }
    if inject:
        for k, v in inject.items():
            base[k] = v
    _write_json(root / SOURCE, base)


def _seed_all_upstreams(root: Path) -> None:
    _write_json(
        root / P93_PATH,
        {"approval_record_seal_plan_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY"},
    )
    _write_json(
        root / P94_PATH,
        {"approval_record_seal_dry_run_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY"},
    )
    _write_json(
        root / P95_PATH,
        {"approval_record_seal_operator_review_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY"},
    )
    _write_json(
        root / P96_PATH,
        {
            "approval_record_seal_operator_decision_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD",
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "approval_record_sealed": False,
            "valid_for_execution": False,
            "token_minting_allowed": False,
        },
    )
    _write_json(
        root / P97_PATH,
        {
            "approval_record_seal_execution_plan_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY",
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "approval_record_sealed": False,
            "valid_for_execution": False,
            "token_minting_allowed": False,
        },
    )


def _build(root: Path) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization(
        repo_root=root
    )


def test_missing_p98_not_computable(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    assert packet["finalization_authorization_status"] == "NOT_COMPUTABLE"
    assert packet["finalization_authorization_eligible"] is False
    assert packet["authorization_granted"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["finalization_authorized"] is False
    assert packet["valid_for_execution"] is False
    assert packet["advisory_only"] is True
    assert "P98_TEMPORAL_CONTINUITY_" in packet["recommended_next_lane"]
    h = packet["finalization_authorization_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_not_simulated_complete_p98_blocks(tmp_path: Path) -> None:
    _seed_p98(
        tmp_path,
        status="BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN",
    )
    packet = _build(tmp_path)
    assert packet["finalization_authorization_status"].startswith("BLOCKED_BY_")
    assert packet["finalization_authorization_eligible"] is False
    assert packet["authorization_granted"] is False
    assert packet["approval_record_sealed"] is False
    assert "P98_TEMPORAL_CONTINUITY_" in packet["recommended_next_lane"]


def test_p98_actual_seal_executed_fails(tmp_path: Path) -> None:
    _seed_p98(tmp_path, actual_seal_executed=True)
    packet = _build(tmp_path)
    status = packet["finalization_authorization_status"]
    assert status.endswith("_FAILED") or status.startswith("BLOCKED_BY_")
    assert packet["finalization_authorization_eligible"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["authorization_granted"] is False


def test_p98_simulated_only_false_blocks(tmp_path: Path) -> None:
    _seed_p98(tmp_path, simulated_only=False)
    packet = _build(tmp_path)
    assert packet["finalization_authorization_eligible"] is False
    assert packet["authorization_granted"] is False


def test_p98_execution_not_recorded_blocks(tmp_path: Path) -> None:
    _seed_p98(tmp_path, execution_recorded=False)
    packet = _build(tmp_path)
    assert packet["finalization_authorization_eligible"] is False
    assert packet["authorization_granted"] is False


def test_p98_sentinel_check_failed_blocks(tmp_path: Path) -> None:
    _seed_p98(tmp_path, sentinel_check_passed=False)
    packet = _build(tmp_path)
    assert packet["finalization_authorization_eligible"] is False
    assert packet["authorization_granted"] is False


def test_decision_provenance_reanchor_valid(tmp_path: Path) -> None:
    _seed_p98(tmp_path)
    packet = _build(tmp_path)
    reanchor = packet["decision_provenance_reanchor"]
    assert reanchor["decision_value"] == "approve_seal_record"
    assert reanchor["autonomous_approval"] is False
    assert reanchor["provenance_anchor_valid"] is True
    assert reanchor["operator_id"] == "Daniel Meyer"
    assert reanchor["decision_id"] == "P96_OPERATOR_DECISION_2026_05_28_001"


def test_autonomous_approval_in_provenance_blocks(tmp_path: Path) -> None:
    _seed_p98(tmp_path, autonomous_approval=True)
    packet = _build(tmp_path)
    assert packet["finalization_authorization_eligible"] is False
    assert packet["authorization_granted"] is False
    reanchor = packet["decision_provenance_reanchor"]
    assert reanchor.get("provenance_anchor_valid") is False


def test_wrong_decision_value_blocks(tmp_path: Path) -> None:
    _seed_p98(tmp_path, decision_value="reject_seal_record")
    packet = _build(tmp_path)
    assert packet["finalization_authorization_eligible"] is False
    assert packet["authorization_granted"] is False


def test_finalization_chain_verification_all_pass(tmp_path: Path) -> None:
    _seed_p98(tmp_path)
    _seed_all_upstreams(tmp_path)
    packet = _build(tmp_path)
    checks = packet["finalization_chain_verification"]
    assert len(checks) == 6
    assert all(c["passed"] is True for c in checks)
    assert packet["finalization_authorization_eligibility_summary"]["full_chain_verified_count"] == 6


def test_chain_verification_missing_upstreams(tmp_path: Path) -> None:
    _seed_p98(tmp_path)
    packet = _build(tmp_path)
    assert packet["finalization_authorization_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_ELIGIBLE"
    )
    checks = packet["finalization_chain_verification"]
    assert len(checks) == 6
    missing = [c for c in checks if not c["passed"]]
    assert len(missing) >= 4
    assert packet["approval_record_sealed"] is False
    assert packet["finalization_authorized"] is False


def test_finalization_authorization_eligible(tmp_path: Path) -> None:
    _seed_p98(tmp_path)
    packet = _build(tmp_path)
    assert packet["finalization_authorization_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_ELIGIBLE"
    )
    assert packet["finalization_authorization_eligible"] is True
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["finalization_authorization_gate_only"] is True
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["recommended_next_lane"].startswith("P100_TEMPORAL_CONTINUITY_")
    assert isinstance(packet["eligibility_reasons"], list) and len(packet["eligibility_reasons"]) > 0
    assert packet["blockers"] == []
    assert packet["operator_approval_required"] is True


def test_authority_locks_hardcoded_regardless_of_input(tmp_path: Path) -> None:
    _seed_p98(
        tmp_path,
        inject={
            "approval_granted": True,
            "authorization_granted": True,
            "execution_authority": True,
            "approval_record_sealed": True,
            "valid_for_execution": True,
            "token_minting_allowed": True,
        },
    )
    packet = _build(tmp_path)
    assert packet["finalization_authorization_status"].endswith("_FAILED")
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["finalization_authorized"] is False
    assert packet["finalization_authorization_eligible"] is False
    assert len(packet["blockers"]) > 0


def test_authority_invariant_checks_use_not_true_semantics(tmp_path: Path) -> None:
    _seed_p98(tmp_path)
    _seed_all_upstreams(tmp_path)
    packet = _build(tmp_path)
    inv = packet["finalization_authority_invariant_checks"]
    assert len(inv) > 0
    assert all(c["passed"] is True for c in inv)


def test_eligibility_summary(tmp_path: Path) -> None:
    _seed_p98(tmp_path)
    packet = _build(tmp_path)
    summary = packet["finalization_authorization_eligibility_summary"]
    assert summary["eligible"] is True
    assert summary["gate_only"] is True
    assert summary["authorization_not_granted"] is True
    assert summary["no_authority_elevated"] is True


def test_schema_and_hash_validation(tmp_path: Path) -> None:
    _seed_p98(tmp_path)
    packet = _build(tmp_path)
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationAuthorization.v1"
    )
    assert packet["finalization_authorization_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_001"
    )
    h = packet["finalization_authorization_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_determinism(tmp_path: Path) -> None:
    _seed_p98(tmp_path)
    _seed_all_upstreams(tmp_path)
    p1 = _build(tmp_path)
    p2 = _build(tmp_path)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert p1["finalization_authorization_hash"] == p2["finalization_authorization_hash"]


def test_write_function(tmp_path: Path) -> None:
    _seed_p98(tmp_path)
    packet = _build(tmp_path)
    out = (
        tmp_path
        / "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization/latest.json"
    )
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization(
        out, packet
    )
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["finalization_authorization_hash"] == packet["finalization_authorization_hash"]
    assert loaded["finalization_authorization_status"] == packet["finalization_authorization_status"]


def test_doctrine_validator_nonregression() -> None:
    import subprocess
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "seal" in result.stdout
