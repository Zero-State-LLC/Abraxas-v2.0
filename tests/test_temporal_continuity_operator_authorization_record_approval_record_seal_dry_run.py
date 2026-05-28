from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_dry_run import (
    build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run,
)
from scripts import run_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run

SOURCE = "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p93(root: Path, status: str, validation_passed: bool = True) -> None:
    _write_json(
        root / SOURCE,
        {
            "approval_record_seal_plan_status": status,
            "approval_record_seal_plan_id": "temporal_continuity_operator_authorization_record_approval_record_seal_plan_001",
            "validation_passed": validation_passed,
            "seal_construction_requirements": [
                "approval_record_seal_plan_must_remain_advisory_only",
                "no_real_approval_record_creation_allowed",
                "no_real_approval_record_sealing_allowed",
            ],
            "seal_provenance_requirements": [
                "source_approval_record_validation_dry_run_hash_must_be_present",
                "source_approval_record_validation_dry_run_path_must_match_expected_lane_output",
                "source_approval_record_validation_dry_run_status_must_be_evaluated",
            ],
            "seal_hash_requirements": [
                "approval_record_seal_plan_hash_must_be_canonical",
                "canonical_json_sha256_source_hash_required",
                "sorted_key_serialization_required",
            ],
            "seal_blocker_requirements": [
                "missing_source_must_fail_closed",
                "non_ready_source_status_must_block",
                "validation_failed_source_must_block",
            ],
            "seal_authority_invariant_requirements": [
                "approval_granted_must_remain_false",
                "authorization_granted_must_remain_false",
                "execution_authority_must_remain_false",
                "token_minting_allowed_must_remain_false",
                "valid_for_execution_must_remain_false",
            ],
            "source_approval_record_validation_dry_run_hash": "a0e88681d9d51f2f8f68d91ab3d4c9d637691c278f45d104015de771a4029b06",
            "source_approval_record_validation_dry_run_path": "out/temporal_continuity_operator_authorization_record_approval_record_validation_dry_run/latest.json",
            "approval_record_seal_plan_hash": "3342df0361c873ae5d675891ef0d6fbf628cf2986dd8e1c929626213f1f58d26",
            "allowed_target_candidates": [
                "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"
            ],
            "denied_target_candidates": ["canon://*"],
            "allowed_command_candidates": [
                "python scripts/run_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run.py"
            ],
            "denied_command_candidates": ["rm -rf /"],
            "planned_authorization_scope": ["approval_record_seal_dry_run_only"],
            "planned_expected_outputs": [
                "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"
            ],
            "approval_record_seal_plan_only": True,
            "approval_record_sealed": False,
            "approval_record_created": False,
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "authorization_authority": False,
            "authorization_record_creation_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
            "advisory_only": True,
            "projection_only": True,
        },
    )


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    assert packet["approval_record_seal_dry_run_status"] == "NOT_COMPUTABLE"
    assert packet["dry_run_passed"] is False
    assert isinstance(packet["approval_record_seal_dry_run_hash"], str)
    assert len(packet["approval_record_seal_dry_run_hash"]) == 64
    assert len(packet["blockers"]) > 0
    assert packet["recommended_next_lane"] == (
        "P93_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN"
    )


def test_ready_source_produces_ready(tmp_path: Path) -> None:
    _seed_p93(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    assert packet["approval_record_seal_dry_run_status"] == (
        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY"
    )
    assert packet["dry_run_passed"] is True
    assert packet["dry_run_blockers"] == []
    assert packet["recommended_next_lane"].startswith("P95_TEMPORAL_CONTINUITY_")
    assert len(packet["seal_construction_dry_run_results"]) > 0
    assert len(packet["seal_provenance_dry_run_results"]) > 0
    assert len(packet["seal_hash_dry_run_results"]) > 0
    assert len(packet["seal_blocker_dry_run_results"]) > 0
    assert len(packet["seal_authority_invariant_dry_run_results"]) > 0
    assert isinstance(packet["simulated_seal_dry_run"], dict)
    assert len(packet["simulated_seal_dry_run"]) > 0


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p93(tmp_path, "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    assert packet["approval_record_seal_dry_run_status"] == (
        "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN"
    )
    assert packet["dry_run_passed"] is False


def test_validation_false_blocks(tmp_path: Path) -> None:
    _seed_p93(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY", False)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    assert packet["approval_record_seal_dry_run_status"] == (
        "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN"
    )
    assert packet["dry_run_passed"] is False
    assert any("validation_passed" in b for b in packet["blockers"])


def test_authority_invariant_failure_triggers_fail_status(tmp_path: Path) -> None:
    _seed_p93(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY", True)
    source_path = tmp_path / SOURCE
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    payload["approval_granted"] = True
    _write_json(source_path, payload)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    assert packet["approval_record_seal_dry_run_status"] == "APPROVAL_RECORD_SEAL_DRY_RUN_FAILED"
    assert packet["dry_run_passed"] is False
    failed = [r for r in packet["seal_authority_invariant_dry_run_results"] if r.get("passed") is False]
    assert len(failed) > 0
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["approval_record_sealed"] is False


def test_authority_locks_hardcoded_regardless_of_input(tmp_path: Path) -> None:
    _seed_p93(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY", True)
    source_path = tmp_path / SOURCE
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    for field in (
        "approval_granted", "authorization_granted", "execution_authority",
        "authorization_authority", "authorization_record_creation_authority",
        "token_minting_allowed", "valid_for_execution", "approval_record_sealed",
        "approval_record_created",
    ):
        payload[field] = True
    _write_json(source_path, payload)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["authorization_authority"] is False
    assert packet["authorization_record_creation_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["approval_record_created"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["simulated_only"] is True
    assert packet["approval_record_seal_dry_run_only"] is True
    assert packet["operator_approval_required"] is True


def test_schema_and_hash_validation(tmp_path: Path) -> None:
    _seed_p93(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealDryRun.v1"
    )
    assert packet["approval_record_seal_dry_run_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_dry_run_001"
    )
    h = packet["approval_record_seal_dry_run_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_determinism(tmp_path: Path) -> None:
    _seed_p93(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY", True)
    p1 = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    p2 = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert p1["approval_record_seal_dry_run_hash"] == p2["approval_record_seal_dry_run_hash"]


def test_write_function(tmp_path: Path) -> None:
    _seed_p93(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    out = tmp_path / "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"
    write_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(out, packet)
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["approval_record_seal_dry_run_hash"] == packet["approval_record_seal_dry_run_hash"]
    assert loaded["approval_record_seal_dry_run_status"] == packet["approval_record_seal_dry_run_status"]


def test_simulated_seal_dry_run_has_sentinel_values(tmp_path: Path) -> None:
    _seed_p93(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(repo_root=tmp_path)
    sim = packet["simulated_seal_dry_run"]
    assert sim["simulated_only"] is True
    assert sim["approval_granted"] is False
    assert sim["authorization_granted"] is False
    assert sim["execution_authority"] is False
    assert sim["token_minting_allowed"] is False
    assert sim["valid_for_execution"] is False
    assert sim["approval_record_sealed"] is False
    assert sim["approval_record_created"] is False
    assert "SIMULATED" in sim["simulated_seal_hash"]
    assert "SIMULATED" in sim["simulated_seal_token"]


def test_doctrine_validator_nonregression() -> None:
    import subprocess
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout
    assert "seal" in output or result.returncode == 0


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
