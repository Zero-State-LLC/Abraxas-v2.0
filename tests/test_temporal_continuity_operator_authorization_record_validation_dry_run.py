from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_validation_dry_run import (
    build_temporal_continuity_operator_authorization_record_validation_dry_run,
    write_temporal_continuity_operator_authorization_record_validation_dry_run,
)
from scripts import run_temporal_continuity_operator_authorization_record_validation_dry_run

SOURCE = "out/temporal_continuity_operator_authorization_record_validation_plan/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p83(root: Path, status: str, *, mutate: dict[str, object] | None = None) -> None:
    payload: dict[str, object] = {
        "validation_plan_status": status,
        "validation_checks": [{"check_id": "c1", "passed": True}],
        "required_operator_field_checks": [{"check_id": "o1", "field": "operator_id", "present": True}],
        "required_authorization_field_checks": [{"check_id": "a1", "field": "authorization_scope", "present": True}],
        "required_command_field_checks": [{"check_id": "c1", "field": "authorized_commands", "present": True}],
        "required_provenance_field_checks": [{"check_id": "p1", "field": "source_path", "present": True}],
        "required_hash_field_checks": [{"check_id": "h1", "field": "template_hash", "present": True}],
        "authority_invariant_checks": [{"check_id": "inv1", "passed": True}],
        "simulated_record_validation": {"shape_valid": True, "validation_blockers": []},
        "allowed_target_candidates": ["out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"],
        "denied_target_candidates": ["canon://*"],
        "allowed_command_candidates": ["python scripts/run_temporal_continuity_upstream_input_regeneration_execution_plan.py"],
        "denied_command_candidates": ["rm *"],
        "planned_authorization_scope": ["scope1"],
        "planned_expected_outputs": ["out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"],
        "simulated_only": True,
        "valid_for_execution": False,
        "authorization_granted": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "operator_approval_required": True,
    }
    if mutate:
        payload.update(mutate)
    _write_json(root / SOURCE, payload)


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_validation_dry_run(repo_root=tmp_path)
    assert packet["validation_dry_run_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P83_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN"


def test_ready_source_produces_ready(tmp_path: Path) -> None:
    _seed_p83(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_validation_dry_run(repo_root=tmp_path)
    assert packet["validation_dry_run_status"] == "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_DRY_RUN_READY"
    assert packet["recommended_next_lane"] == "P85_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN"
    assert packet["validation_passed"] is True


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p83(tmp_path, "NOT_COMPUTABLE")
    packet = build_temporal_continuity_operator_authorization_record_validation_dry_run(repo_root=tmp_path)
    assert packet["validation_dry_run_status"] == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN"


def test_failed_checks_produce_failed_status(tmp_path: Path) -> None:
    _seed_p83(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN_READY", mutate={"simulated_record_validation": {"shape_valid": False, "validation_blockers": ["bad"]}})
    packet = build_temporal_continuity_operator_authorization_record_validation_dry_run(repo_root=tmp_path)
    assert packet["validation_dry_run_status"] == "VALIDATION_DRY_RUN_FAILED"
    assert packet["validation_passed"] is False


def test_all_check_groups_present(tmp_path: Path) -> None:
    _seed_p83(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_validation_dry_run(repo_root=tmp_path)
    for key in [
        "executed_validation_checks", "operator_field_results", "authorization_field_results", "command_field_results",
        "provenance_field_results", "hash_field_results", "authority_invariant_results", "simulated_record_validation_result",
    ]:
        assert key in packet


def test_authority_results_present_and_pass(tmp_path: Path) -> None:
    _seed_p83(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_validation_dry_run(repo_root=tmp_path)
    assert packet["authority_invariant_results"]
    assert all(i.get("passed") for i in packet["authority_invariant_results"])
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False


def test_hash_stable(tmp_path: Path) -> None:
    _seed_p83(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN_READY")
    a = build_temporal_continuity_operator_authorization_record_validation_dry_run(repo_root=tmp_path)
    b = build_temporal_continuity_operator_authorization_record_validation_dry_run(repo_root=tmp_path)
    assert a["validation_dry_run_hash"] == b["validation_dry_run_hash"]


def test_runner_deterministic_write(tmp_path: Path) -> None:
    _seed_p83(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN_READY")
    out_path = tmp_path / "out/temporal_continuity_operator_authorization_record_validation_dry_run/latest.json"
    first = run_temporal_continuity_operator_authorization_record_validation_dry_run.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_validation_dry_run.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["validation_dry_run_hash"] == second["validation_dry_run_hash"]
    assert first_text == second_text


def test_registry_includes_artifact() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/temporal_continuity_operator_authorization_record_validation_dry_run/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS


def test_writer_final_newline(tmp_path: Path) -> None:
    _seed_p83(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_validation_dry_run(repo_root=tmp_path)
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_validation_dry_run(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
