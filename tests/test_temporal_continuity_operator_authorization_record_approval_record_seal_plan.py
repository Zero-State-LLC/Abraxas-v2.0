from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_plan import (
    build_temporal_continuity_operator_authorization_record_approval_record_seal_plan,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_plan,
)
from scripts.temporal import run_temporal_continuity_operator_authorization_record_approval_record_seal_plan

SOURCE = "out/temporal_continuity_operator_authorization_record_approval_record_validation_dry_run/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p92(root: Path, status: str, validation_passed: bool = True) -> None:
    _write_json(
        root / SOURCE,
        {
            "approval_record_validation_dry_run_status": status,
            "validation_passed": validation_passed,
            "allowed_target_candidates": ["out/future.json"],
            "denied_target_candidates": ["canon://*"],
            "allowed_command_candidates": ["python scripts/temporal/run_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run.py"],
            "denied_command_candidates": ["rm -rf /"],
            "planned_authorization_scope": ["approval_record_seal_dry_run_only"],
            "planned_expected_outputs": ["out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"],
            "approval_record_validation_dry_run_only": True,
            "approval_record_created": False,
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "authorization_authority": False,
            "authorization_record_creation_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
        },
    )


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_plan(repo_root=tmp_path)
    assert packet["approval_record_seal_plan_status"] == "NOT_COMPUTABLE"


def test_ready_source_produces_ready(tmp_path: Path) -> None:
    _seed_p92(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_plan(repo_root=tmp_path)
    assert packet["approval_record_seal_plan_status"] == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY"
    assert packet["recommended_next_lane"] == "P94_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p92(tmp_path, "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_PLAN", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_plan(repo_root=tmp_path)
    assert packet["approval_record_seal_plan_status"] == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN"


def test_validation_false_blocks(tmp_path: Path) -> None:
    _seed_p92(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN_READY", False)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_plan(repo_root=tmp_path)
    assert packet["approval_record_seal_plan_status"] == "BLOCKED_BY_FAILED_APPROVAL_RECORD_VALIDATION_DRY_RUN"


def test_requirement_groups_present(tmp_path: Path) -> None:
    _seed_p92(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_plan(repo_root=tmp_path)
    assert packet["seal_construction_requirements"]
    assert packet["seal_provenance_requirements"]
    assert packet["seal_hash_requirements"]
    assert packet["seal_blocker_requirements"]
    assert packet["seal_authority_invariant_requirements"]


def test_authority_invariants_hard_locked(tmp_path: Path) -> None:
    _seed_p92(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_plan(repo_root=tmp_path)
    assert packet["approval_record_sealed"] is False
    assert packet["approval_record_created"] is False
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["valid_for_execution"] is False


def test_hash_stable(tmp_path: Path) -> None:
    _seed_p92(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN_READY", True)
    a = build_temporal_continuity_operator_authorization_record_approval_record_seal_plan(repo_root=tmp_path)
    b = build_temporal_continuity_operator_authorization_record_approval_record_seal_plan(repo_root=tmp_path)
    assert a["approval_record_seal_plan_hash"] == b["approval_record_seal_plan_hash"]


def test_runner_deterministic_write(tmp_path: Path) -> None:
    _seed_p92(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN_READY", True)
    out_path = tmp_path / "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json"
    first = run_temporal_continuity_operator_authorization_record_approval_record_seal_plan.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_approval_record_seal_plan.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["approval_record_seal_plan_hash"] == second["approval_record_seal_plan_hash"]
    assert first_text == second_text


def test_registry_includes_artifact() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS


def test_writer_final_newline(tmp_path: Path) -> None:
    _seed_p92(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN_READY", True)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_seal_plan(repo_root=tmp_path)
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_approval_record_seal_plan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
