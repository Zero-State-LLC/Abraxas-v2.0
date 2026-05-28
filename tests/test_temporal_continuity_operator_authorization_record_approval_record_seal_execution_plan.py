from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan import (
    build_temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan,
)

SOURCE = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision/latest.json"
)
P93_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json"
P94_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"
P95_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_review/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


def _seed_p96(
    root: Path,
    status: str = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD",
    decision_recorded: bool = True,
    autonomous_approval: bool = False,
    decision_value: str = "approve_seal_record",
    *,
    inject_violations: dict[str, bool] | None = None,
) -> None:
    base: dict[str, object] = {
        "approval_record_seal_operator_decision_status": status,
        "approval_record_seal_operator_decision_hash": (
            "1d9fb64f294609748f75eefb6510731041f43c982e0922c20cb6ade64dfa1d73"
        ),
        "approval_record_seal_operator_decision_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision_001"
        ),
        "decision_recorded": decision_recorded,
        "autonomous_approval": autonomous_approval,
        "operator_decision_record": {
            "decision_value": decision_value,
            "decision_id": "P96_OPERATOR_DECISION_2026_05_28_001",
            "operator_id": "Daniel Meyer",
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "approval_record_sealed": False,
            "autonomous_approval": False,
            "advisory_only_acknowledged": True,
            "no_execution_authority_granted_acknowledged": True,
            "upstream_review_hash_match": True,
        },
        "upstream_provenance": {
            "review_hash": "7fc8305273ae3b849741efd1dd6c01f4eb7f532cf3d92f4e8cb6c337b5192e0d",
            "review_file_hash": "1d9b7157742c2c8eee8fc98f507f5ab826a1d496e4e0093da17612e533479bdc",
            "review_id": "temporal_continuity_operator_authorization_record_approval_record_seal_operator_review_001",
            "review_passed": True,
        },
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
    if inject_violations:
        for k, v in inject_violations.items():
            base[k] = v
    _write_json(root / SOURCE, base)


def _seed_upstream_lanes(root: Path) -> None:
    _write_json(
        root / P93_PATH,
        {
            "approval_record_seal_plan_status": (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY"
            )
        },
    )
    _write_json(
        root / P94_PATH,
        {
            "approval_record_seal_dry_run_status": (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY"
            )
        },
    )
    _write_json(
        root / P95_PATH,
        {
            "approval_record_seal_operator_review_status": (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY"
            )
        },
    )


def _build(root: Path) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan(
        repo_root=root
    )


def test_missing_p96_fails_closed(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_plan_status"] == "NOT_COMPUTABLE"
    assert packet["plan_ready"] is False
    assert packet["seal_execution_steps"] == []
    assert packet["approval_granted"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["recommended_next_lane"].startswith("P96_TEMPORAL_CONTINUITY_")
    h = packet["approval_record_seal_execution_plan_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_not_approved_p96_blocks(tmp_path: Path) -> None:
    _seed_p96(
        tmp_path,
        status="OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_PENDING",
    )
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_plan_status"].startswith("BLOCKED_BY_")
    assert packet["plan_ready"] is False
    assert packet["seal_execution_steps"] == []
    assert packet["approval_granted"] is False
    assert packet["recommended_next_lane"].startswith("P96_TEMPORAL_CONTINUITY_")


def test_wrong_decision_value_blocks(tmp_path: Path) -> None:
    _seed_p96(tmp_path, decision_value="reject_seal_record")
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_plan_status"].startswith("BLOCKED_BY_")
    assert packet["plan_ready"] is False
    assert packet["seal_execution_steps"] == []
    assert packet["approval_granted"] is False


def test_decision_not_recorded_blocks(tmp_path: Path) -> None:
    _seed_p96(tmp_path, decision_recorded=False)
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_plan_status"].startswith("BLOCKED_BY_")
    assert packet["plan_ready"] is False


def test_autonomous_approval_blocks(tmp_path: Path) -> None:
    _seed_p96(tmp_path, autonomous_approval=True)
    packet = _build(tmp_path)
    status = packet["approval_record_seal_execution_plan_status"]
    assert status.startswith("BLOCKED_BY_") or status.endswith("_FAILED"), (
        f"Expected BLOCKED or FAILED for autonomous_approval:true, got {status!r}"
    )
    assert packet["plan_ready"] is False
    assert packet["approval_granted"] is False


def test_execution_plan_ready(tmp_path: Path) -> None:
    _seed_p96(tmp_path)
    _seed_upstream_lanes(tmp_path)
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_plan_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY"
    )
    assert packet["plan_ready"] is True
    assert len(packet["seal_execution_steps"]) == 5
    for step in packet["seal_execution_steps"]:
        assert step["execution_plan_only"] is True
    step5 = packet["seal_execution_steps"][4]
    assert step5["step_id"] == "SEAL_EXEC_STEP_05_EXECUTE_APPROVAL_RECORD_SEAL"
    assert step5["requires_separate_operator_authorization"] is True
    assert step5["approval_granted"] is False
    assert step5["approval_record_sealed"] is False
    assert step5["execution_authority"] is False
    assert "ADVISORY_ONLY" in step5["command_advisory"]
    summary = packet["seal_execution_plan_summary"]
    assert summary["step_count"] == 5
    assert summary["all_steps_advisory"] is True
    assert summary["seal_not_executed"] is True
    assert summary["execution_plan_only"] is True
    att = packet["plan_only_attestation"]
    assert att["no_seal_executed"] is True
    assert att["no_approval_granted"] is True
    assert att["no_execution_authority_created"] is True
    assert att["plan_preparation_only"] is True
    anchor = packet["decision_provenance_anchor"]
    assert anchor["decision_value"] == "approve_seal_record"
    assert anchor["autonomous_approval"] is False
    assert anchor["operator_id"] == "Daniel Meyer"
    assert packet["recommended_next_lane"].startswith("P98_TEMPORAL_CONTINUITY_")
    assert packet["plan_blockers"] == []
    checks = packet["seal_execution_readiness_checks"]
    assert len(checks) == 3
    assert all(c["passed"] is True for c in checks)
    assert packet["approval_granted"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["advisory_only"] is True
    assert packet["execution_plan_only"] is True


def test_cross_lane_checks_with_missing_upstreams(tmp_path: Path) -> None:
    _seed_p96(tmp_path)
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_plan_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY"
    )
    assert packet["plan_ready"] is True
    checks = packet["seal_execution_readiness_checks"]
    assert len(checks) == 3
    assert all(c["passed"] is False for c in checks)
    assert packet["approval_granted"] is False
    assert packet["valid_for_execution"] is False


def test_authority_locks_hardcoded_regardless_of_input(tmp_path: Path) -> None:
    _seed_p96(
        tmp_path,
        inject_violations={
            "approval_granted": True,
            "authorization_granted": True,
            "execution_authority": True,
            "approval_record_sealed": True,
            "valid_for_execution": True,
            "token_minting_allowed": True,
        },
    )
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_plan_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_FAILED"
    )
    assert packet["plan_ready"] is False
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["operator_approval_required"] is True
    assert len(packet["plan_blockers"]) > 0


def test_odr_authority_violations_detected(tmp_path: Path) -> None:
    _seed_p96(tmp_path, decision_value="approve_seal_record")
    p = tmp_path / SOURCE
    payload = json.loads(p.read_text(encoding="utf-8"))
    odr = dict(payload["operator_decision_record"])
    odr["approval_granted"] = True
    odr["execution_authority"] = True
    payload["operator_decision_record"] = odr
    _write_json(p, payload)
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_plan_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_FAILED"
    )
    assert packet["approval_granted"] is False


def test_step_5_does_not_execute(tmp_path: Path) -> None:
    _seed_p96(tmp_path)
    target_artifact = (
        tmp_path / "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution/latest.json"
    )
    packet = _build(tmp_path)
    assert packet["plan_ready"] is True
    assert not target_artifact.exists(), "Step 5 must not create the seal execution artifact"
    step5 = packet["seal_execution_steps"][4]
    assert isinstance(step5["command_advisory"], str)
    assert step5["execution_plan_only"] is True
    assert step5["requires_separate_operator_authorization"] is True


def test_schema_and_hash_validation(tmp_path: Path) -> None:
    _seed_p96(tmp_path)
    packet = _build(tmp_path)
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealExecutionPlan.v1"
    )
    assert packet["approval_record_seal_execution_plan_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan_001"
    )
    h = packet["approval_record_seal_execution_plan_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_determinism(tmp_path: Path) -> None:
    _seed_p96(tmp_path)
    _seed_upstream_lanes(tmp_path)
    p1 = _build(tmp_path)
    p2 = _build(tmp_path)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert (
        p1["approval_record_seal_execution_plan_hash"]
        == p2["approval_record_seal_execution_plan_hash"]
    )


def test_write_function(tmp_path: Path) -> None:
    _seed_p96(tmp_path)
    packet = _build(tmp_path)
    out = (
        tmp_path
        / "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan/latest.json"
    )
    write_temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan(
        out, packet
    )
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert (
        loaded["approval_record_seal_execution_plan_hash"]
        == packet["approval_record_seal_execution_plan_hash"]
    )
    assert (
        loaded["approval_record_seal_execution_plan_status"]
        == packet["approval_record_seal_execution_plan_status"]
    )


def test_doctrine_validator_nonregression() -> None:
    import subprocess
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "seal" in result.stdout
