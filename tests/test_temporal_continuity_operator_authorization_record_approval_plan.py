from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_plan import (
    build_temporal_continuity_operator_authorization_record_approval_plan,
    write_temporal_continuity_operator_authorization_record_approval_plan,
)
from scripts.temporal import run_temporal_continuity_operator_authorization_record_approval_plan

SOURCE = "out/temporal_continuity_operator_authorization_record_validation_dry_run/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p84(root: Path, status: str, *, validation_passed: bool = True) -> None:
    payload: dict[str, object] = {
        "validation_dry_run_status": status,
        "validation_passed": validation_passed,
        "allowed_target_candidates": ["out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"],
        "denied_target_candidates": ["canon://*"],
        "allowed_command_candidates": ["python scripts/temporal/run_temporal_continuity_upstream_input_regeneration_execution_plan.py"],
        "denied_command_candidates": ["rm *"],
        "planned_authorization_scope": ["scope1"],
        "planned_expected_outputs": ["out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"],
    }
    _write_json(root / SOURCE, payload)


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_approval_plan(repo_root=tmp_path)
    assert packet["approval_plan_status"] == "NOT_COMPUTABLE"


def test_ready_source_produces_ready(tmp_path: Path) -> None:
    _seed_p84(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN_READY", validation_passed=True)
    packet = build_temporal_continuity_operator_authorization_record_approval_plan(repo_root=tmp_path)
    assert packet["approval_plan_status"] == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN_READY"
    assert packet["recommended_next_lane"] == "P86_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_DRY_RUN"


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p84(tmp_path, "VALIDATION_DRY_RUN_FAILED")
    packet = build_temporal_continuity_operator_authorization_record_approval_plan(repo_root=tmp_path)
    assert packet["approval_plan_status"] == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN"


def test_validation_failed_blocks(tmp_path: Path) -> None:
    _seed_p84(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN_READY", validation_passed=False)
    packet = build_temporal_continuity_operator_authorization_record_approval_plan(repo_root=tmp_path)
    assert packet["approval_plan_status"] == "BLOCKED_BY_FAILED_VALIDATION_DRY_RUN"


def test_governance_and_requirements_present(tmp_path: Path) -> None:
    _seed_p84(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_plan(repo_root=tmp_path)
    assert packet["required_operator_acknowledgements"]
    assert packet["required_operator_approval_fields"]
    assert packet["approval_constraints"]
    assert packet["approval_provenance_requirements"]
    assert packet["approval_hash_requirements"]
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False


def test_hash_stable(tmp_path: Path) -> None:
    _seed_p84(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN_READY")
    a = build_temporal_continuity_operator_authorization_record_approval_plan(repo_root=tmp_path)
    b = build_temporal_continuity_operator_authorization_record_approval_plan(repo_root=tmp_path)
    assert a["approval_plan_hash"] == b["approval_plan_hash"]


def test_runner_deterministic_write(tmp_path: Path) -> None:
    _seed_p84(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN_READY")
    out_path = tmp_path / "out/temporal_continuity_operator_authorization_record_approval_plan/latest.json"
    first = run_temporal_continuity_operator_authorization_record_approval_plan.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_approval_plan.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["approval_plan_hash"] == second["approval_plan_hash"]
    assert first_text == second_text


def test_registry_includes_artifact() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/temporal_continuity_operator_authorization_record_approval_plan/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS


def test_writer_final_newline(tmp_path: Path) -> None:
    _seed_p84(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_plan(repo_root=tmp_path)
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_approval_plan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
