from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_plan import (
    build_temporal_continuity_operator_authorization_record_approval_record_plan,
    write_temporal_continuity_operator_authorization_record_approval_record_plan,
)
from scripts import run_temporal_continuity_operator_authorization_record_approval_record_plan

SOURCE = "out/temporal_continuity_operator_authorization_record_approval_validation_dry_run/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p88(root: Path, status: str, *, validation_passed: bool = True) -> None:
    _write_json(
        root / SOURCE,
        {
            "approval_validation_dry_run_status": status,
            "validation_passed": validation_passed,
            "allowed_target_candidates": ["out/future_approval_record.json"],
            "denied_target_candidates": ["canon://*"],
            "allowed_command_candidates": ["python scripts/run_temporal_continuity_operator_authorization_record_approval_record_dry_run.py"],
            "denied_command_candidates": ["rm -rf /"],
            "planned_authorization_scope": ["operator_authorization_record_approval_pathway"],
            "planned_expected_outputs": ["out/temporal_continuity_operator_authorization_record_approval_record_dry_run/latest.json"],
            "advisory_only": True,
            "projection_only": True,
            "approval_validation_dry_run_only": True,
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
    packet = build_temporal_continuity_operator_authorization_record_approval_record_plan(repo_root=tmp_path)
    assert packet["approval_record_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P88_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN"


def test_ready_source_produces_ready(tmp_path: Path) -> None:
    _seed_p88(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_plan(repo_root=tmp_path)
    assert packet["approval_record_plan_status"] == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN_READY"
    assert packet["recommended_next_lane"] == "P90_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_DRY_RUN"


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p88(tmp_path, "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_plan(repo_root=tmp_path)
    assert packet["approval_record_plan_status"] == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN"


def test_validation_false_blocks(tmp_path: Path) -> None:
    _seed_p88(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY", validation_passed=False)
    packet = build_temporal_continuity_operator_authorization_record_approval_record_plan(repo_root=tmp_path)
    assert packet["approval_record_plan_status"] == "BLOCKED_BY_FAILED_APPROVAL_VALIDATION_DRY_RUN"


def test_required_groups_present(tmp_path: Path) -> None:
    _seed_p88(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_plan(repo_root=tmp_path)
    assert sorted(packet["required_approval_record_fields"].keys()) == sorted(
        ["identity_fields", "source_fields", "operator_fields", "authority_lock_fields", "integrity_fields"]
    )
    assert packet["approval_record_construction_requirements"]
    assert packet["operator_approval_provenance_requirements"]
    assert packet["approval_record_hash_requirements"]
    assert packet["approval_record_seal_requirements"]


def test_authority_locks_false(tmp_path: Path) -> None:
    _seed_p88(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_plan(repo_root=tmp_path)
    for key in (
        "approval_record_creation_authority",
        "approval_record_created",
        "approval_granted",
        "authorization_granted",
        "execution_authority",
        "authorization_authority",
        "authorization_record_creation_authority",
        "token_minting_allowed",
        "valid_for_execution",
    ):
        assert packet[key] is False


def test_hash_stable(tmp_path: Path) -> None:
    _seed_p88(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY")
    a = build_temporal_continuity_operator_authorization_record_approval_record_plan(repo_root=tmp_path)
    b = build_temporal_continuity_operator_authorization_record_approval_record_plan(repo_root=tmp_path)
    assert a["approval_record_plan_hash"] == b["approval_record_plan_hash"]


def test_runner_deterministic_write(tmp_path: Path) -> None:
    _seed_p88(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY")
    out_path = tmp_path / "out/temporal_continuity_operator_authorization_record_approval_record_plan/latest.json"
    first = run_temporal_continuity_operator_authorization_record_approval_record_plan.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_approval_record_plan.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["approval_record_plan_hash"] == second["approval_record_plan_hash"]
    assert first_text == second_text


def test_registry_includes_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/temporal_continuity_operator_authorization_record_approval_record_plan/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/temporal_continuity_operator_authorization_record_approval_record_plan/latest.md" in _DERIVED_OPTIONAL_ARTIFACTS


def test_writer_final_newline(tmp_path: Path) -> None:
    _seed_p88(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_plan(repo_root=tmp_path)
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_approval_record_plan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")


def test_no_real_record_created(tmp_path: Path) -> None:
    _seed_p88(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_plan(repo_root=tmp_path)
    assert packet["approval_record_created"] is False
