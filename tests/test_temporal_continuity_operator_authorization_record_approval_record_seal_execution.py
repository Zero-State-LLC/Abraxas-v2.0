from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_execution import (
    _SIMULATED_SENTINEL_FIELDS,
    _check_simulated_sentinels,
    build_temporal_continuity_operator_authorization_record_approval_record_seal_execution,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_execution,
)

SOURCE = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan/latest.json"
)
P93_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json"
P94_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"
P95_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_review/latest.json"
P96_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


def _seed_p97(
    root: Path,
    status: str = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY",
    plan_ready: bool = True,
    seal_not_executed: bool = True,
    all_steps_advisory: bool = True,
    *,
    inject_violations: dict[str, object] | None = None,
) -> None:
    base: dict[str, object] = {
        "approval_record_seal_execution_plan_status": status,
        "approval_record_seal_execution_plan_hash": (
            "8a7894653c3382c4f7026425bc98712fa309fef53761222a20f7cea8daeeb8b1"
        ),
        "approval_record_seal_execution_plan_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan_001"
        ),
        "plan_ready": plan_ready,
        "seal_execution_plan_summary": {
            "step_count": 5,
            "all_steps_advisory": all_steps_advisory,
            "execution_authority_required_externally": True,
            "execution_plan_only": True,
            "seal_not_executed": seal_not_executed,
        },
        "plan_only_attestation": {
            "no_seal_executed": seal_not_executed,
            "no_approval_granted": True,
            "no_execution_authority_created": True,
            "plan_preparation_only": True,
        },
        "decision_provenance_anchor": {
            "decision_hash": "1d9fb64f294609748f75eefb6510731041f43c982e0922c20cb6ade64dfa1d73",
            "decision_id": "P96_OPERATOR_DECISION_2026_05_28_001",
            "operator_id": "Daniel Meyer",
            "decision_value": "approve_seal_record",
            "review_hash": "7fc8305273ae3b849741efd1dd6c01f4eb7f532cf3d92f4e8cb6c337b5192e0d",
            "review_file_hash": "1d9b7157742c2c8eee8fc98f507f5ab826a1d496e4e0093da17612e533479bdc",
            "autonomous_approval": False,
        },
        "advisory_only": True,
        "projection_only": True,
        "execution_plan_only": True,
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


def _build(root: Path) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_execution(
        repo_root=root
    )


def test_missing_p97_fails_closed(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_status"] == "NOT_COMPUTABLE"
    assert packet["execution_recorded"] is False
    assert packet["simulated_seal_execution_record"] == {}
    assert packet["actual_seal_executed"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["simulated_only"] is True
    assert packet["recommended_next_lane"].startswith("P97_TEMPORAL_CONTINUITY_")
    h = packet["approval_record_seal_execution_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_not_ready_p97_blocks(tmp_path: Path) -> None:
    _seed_p97(
        tmp_path,
        status="BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION",
        plan_ready=False,
    )
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_status"].startswith("BLOCKED_BY_")
    assert packet["execution_recorded"] is False
    assert packet["simulated_seal_execution_record"] == {}
    assert packet["approval_granted"] is False
    assert packet["recommended_next_lane"].startswith("P97_TEMPORAL_CONTINUITY_")


def test_plan_ready_false_blocks(tmp_path: Path) -> None:
    _seed_p97(tmp_path, plan_ready=False)
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_status"].startswith("BLOCKED_BY_")
    assert packet["execution_recorded"] is False


def test_p97_seal_not_executed_false_fails(tmp_path: Path) -> None:
    _seed_p97(tmp_path, seal_not_executed=False)
    packet = _build(tmp_path)
    status = packet["approval_record_seal_execution_status"]
    assert status.startswith("BLOCKED_BY_") or status.endswith("_FAILED")
    assert packet["execution_recorded"] is False
    assert packet["approval_record_sealed"] is False


def test_execution_classification_is_simulated_only(tmp_path: Path) -> None:
    _seed_p97(tmp_path)
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_SIMULATED_COMPLETE"
    )
    assert packet["simulated_only"] is True
    assert packet["actual_seal_executed"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["execution_recorded"] is True
    rec = packet["simulated_seal_execution_record"]
    assert isinstance(rec, dict) and len(rec) >= 12
    for field in _SIMULATED_SENTINEL_FIELDS:
        val = rec.get(field, "")
        assert isinstance(val, str) and "SIMULATED" in val, (
            f"Sentinel field {field!r} must contain 'SIMULATED', got {val!r}"
        )
    assert rec["approval_record_sealed"] is False
    assert rec["actual_seal_executed"] is False
    assert rec["simulated_only"] is True
    assert rec["approval_granted"] is False
    assert rec["execution_authority"] is False
    summary = packet["simulated_execution_summary"]
    assert summary["simulated_only"] is True
    assert summary["actual_seal_executed"] is False
    assert summary["approval_record_sealed"] is False
    assert summary["execution_authority_granted"] is False
    assert packet["recommended_next_lane"].startswith("P99_TEMPORAL_CONTINUITY_")
    assert packet["execution_blockers"] == []
    assert packet["advisory_only"] is True
    assert packet["simulated_execution_only"] is True


def test_simulated_execution_record_sentinels(tmp_path: Path) -> None:
    _seed_p97(tmp_path)
    packet = _build(tmp_path)
    rec = packet["simulated_seal_execution_record"]
    sentinel_check = _check_simulated_sentinels(rec)
    assert sentinel_check["check_passed"] is True
    assert sentinel_check["sentinel_strings_all_contain_simulated_marker"] is True
    assert sentinel_check["simulated_only_flag_set"] is True
    assert sentinel_check["actual_seal_executed_is_false"] is True
    assert sentinel_check["approval_record_sealed_is_false"] is True
    for field in _SIMULATED_SENTINEL_FIELDS:
        val = str(rec.get(field, ""))
        assert not all(c in "0123456789abcdef" for c in val) or len(val) != 64, (
            f"Sentinel field {field!r} must not be a real 64-char hex hash"
        )
    assert packet["simulated_sentinel_check"]["check_passed"] is True


def test_5_lane_execution_chain_verification(tmp_path: Path) -> None:
    _seed_p97(tmp_path)
    _seed_all_upstreams(tmp_path)
    packet = _build(tmp_path)
    checks = packet["execution_chain_verification"]
    assert len(checks) == 5
    assert all(c["passed"] is True for c in checks)
    assert packet["simulated_execution_summary"]["step_count_verified"] == 5


def test_chain_verification_with_missing_upstreams(tmp_path: Path) -> None:
    _seed_p97(tmp_path)
    packet = _build(tmp_path)
    assert packet["approval_record_seal_execution_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_SIMULATED_COMPLETE"
    )
    checks = packet["execution_chain_verification"]
    assert len(checks) == 5
    missing = [c for c in checks if not c["passed"]]
    assert len(missing) >= 4
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False


def test_authority_locks_hardcoded_regardless_of_input(tmp_path: Path) -> None:
    _seed_p97(
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
    assert packet["approval_record_seal_execution_status"].endswith("_FAILED")
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["actual_seal_executed"] is False
    assert packet["simulated_only"] is True
    assert packet["advisory_only"] is True
    assert packet["operator_approval_required"] is True
    assert len(packet["execution_blockers"]) > 0


def test_authority_invariant_checks_populated(tmp_path: Path) -> None:
    _seed_p97(tmp_path)
    _seed_all_upstreams(tmp_path)
    packet = _build(tmp_path)
    inv = packet["execution_authority_invariant_checks"]
    assert len(inv) > 0
    assert all(c["passed"] is True for c in inv)


def test_full_provenance_chain(tmp_path: Path) -> None:
    _seed_p97(tmp_path)
    packet = _build(tmp_path)
    chain = packet["full_provenance_chain"]
    assert "p97_seal_execution_plan_hash" in chain
    assert "p96_seal_operator_decision_hash" in chain
    assert "p95_seal_operator_review_hash" in chain
    assert chain["autonomous_approval"] is False
    assert chain["decision_value"] == "approve_seal_record"
    assert chain["operator_id"] == "Daniel Meyer"


def test_schema_and_hash_validation(tmp_path: Path) -> None:
    _seed_p97(tmp_path)
    packet = _build(tmp_path)
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealExecution.v1"
    )
    assert packet["approval_record_seal_execution_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_execution_001"
    )
    h = packet["approval_record_seal_execution_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_determinism(tmp_path: Path) -> None:
    _seed_p97(tmp_path)
    _seed_all_upstreams(tmp_path)
    p1 = _build(tmp_path)
    p2 = _build(tmp_path)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert p1["approval_record_seal_execution_hash"] == p2["approval_record_seal_execution_hash"]


def test_write_function(tmp_path: Path) -> None:
    _seed_p97(tmp_path)
    packet = _build(tmp_path)
    out = (
        tmp_path
        / "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution/latest.json"
    )
    write_temporal_continuity_operator_authorization_record_approval_record_seal_execution(
        out, packet
    )
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["approval_record_seal_execution_hash"] == packet["approval_record_seal_execution_hash"]
    assert loaded["approval_record_seal_execution_status"] == packet["approval_record_seal_execution_status"]


def test_doctrine_validator_nonregression() -> None:
    import subprocess
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "seal" in result.stdout
