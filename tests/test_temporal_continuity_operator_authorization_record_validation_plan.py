from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_validation_plan import (
    build_temporal_continuity_operator_authorization_record_validation_plan,
    write_temporal_continuity_operator_authorization_record_validation_plan,
)
from scripts import run_temporal_continuity_operator_authorization_record_validation_plan


SOURCE = "out/temporal_continuity_operator_authorization_record_dry_run/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p82(root: Path, status: str, *, mutate_flags: dict[str, object] | None = None, shape_valid: bool = True) -> None:
    payload: dict[str, object] = {
        "dry_run_status": status,
        "required_operator_fields": ["operator_id"],
        "required_authorization_fields": ["authorization_scope"],
        "required_command_fields": ["authorized_commands"],
        "required_provenance_fields": ["source_authorization_record_plan_path"],
        "required_hash_fields": ["template_hash"],
        "allowed_target_candidates": ["out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"],
        "denied_target_candidates": ["canon://*"],
        "allowed_command_candidates": ["python scripts/run_temporal_continuity_upstream_input_regeneration_execution_plan.py"],
        "denied_command_candidates": ["rm *"],
        "planned_authorization_scope": ["upstream_input_regeneration_authorization_record_creation_only"],
        "planned_expected_outputs": ["out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"],
        "simulated_authorization_record": {"artifact_type": "OperatorAuthorizationRecord.v1.simulated"},
        "simulated_only": True,
        "authorization_granted": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "operator_approval_required": True,
        "valid_for_execution": False,
        "simulated_record_validation": {"shape_valid": shape_valid, "validation_blockers": [] if shape_valid else ["bad_shape"]},
    }
    if mutate_flags:
        payload.update(mutate_flags)
    _write_json(root / SOURCE, payload)


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_validation_plan(repo_root=tmp_path)
    assert packet["validation_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P82_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_DRY_RUN"


def test_ready_source_produces_validation_plan_ready(tmp_path: Path) -> None:
    _seed_p82(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_validation_plan(repo_root=tmp_path)
    assert packet["validation_plan_status"] == "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN_READY"
    assert packet["recommended_next_lane"] == "P84_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN"


def test_not_ready_source_blocks_plan(tmp_path: Path) -> None:
    _seed_p82(tmp_path, "NOT_COMPUTABLE")
    packet = build_temporal_continuity_operator_authorization_record_validation_plan(repo_root=tmp_path)
    assert packet["validation_plan_status"] == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_DRY_RUN"


def test_malformed_simulated_record_blocks_plan(tmp_path: Path) -> None:
    _seed_p82(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_DRY_RUN_READY", shape_valid=False)
    packet = build_temporal_continuity_operator_authorization_record_validation_plan(repo_root=tmp_path)
    assert packet["validation_plan_status"] == "VALIDATION_PLAN_BLOCKED_BY_SIMULATED_RECORD"


def test_required_check_groups_present(tmp_path: Path) -> None:
    _seed_p82(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_validation_plan(repo_root=tmp_path)
    for key in [
        "validation_checks", "required_operator_field_checks", "required_authorization_field_checks",
        "required_command_field_checks", "required_provenance_field_checks", "required_hash_field_checks",
        "authority_invariant_checks", "simulated_record_validation", "validation_plan_hash",
    ]:
        assert key in packet


def test_authority_checks_fail_when_forbidden_flag_true(tmp_path: Path) -> None:
    _seed_p82(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_DRY_RUN_READY", mutate_flags={"execution_authority": True})
    packet = build_temporal_continuity_operator_authorization_record_validation_plan(repo_root=tmp_path)
    assert packet["validation_plan_status"] == "VALIDATION_PLAN_BLOCKED_BY_SIMULATED_RECORD"
    failed = [c for c in packet["authority_invariant_checks"] if not c["passed"]]
    assert any(c["field"] == "execution_authority" for c in failed)


def test_validation_plan_hash_stable(tmp_path: Path) -> None:
    _seed_p82(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_DRY_RUN_READY")
    a = build_temporal_continuity_operator_authorization_record_validation_plan(repo_root=tmp_path)
    b = build_temporal_continuity_operator_authorization_record_validation_plan(repo_root=tmp_path)
    assert a["validation_plan_hash"] == b["validation_plan_hash"]


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    _seed_p82(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_DRY_RUN_READY")
    out_path = tmp_path / "out/temporal_continuity_operator_authorization_record_validation_plan/latest.json"
    first = run_temporal_continuity_operator_authorization_record_validation_plan.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_validation_plan.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["validation_plan_hash"] == second["validation_plan_hash"]
    assert first_text == second_text


def test_writer_final_newline(tmp_path: Path) -> None:
    _seed_p82(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_DRY_RUN_READY")
    packet = build_temporal_continuity_operator_authorization_record_validation_plan(repo_root=tmp_path)
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_validation_plan(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")


def test_registry_includes_artifact() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/temporal_continuity_operator_authorization_record_validation_plan/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
