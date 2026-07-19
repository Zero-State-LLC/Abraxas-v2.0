from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_validation_dry_run import (
    build_temporal_continuity_operator_authorization_record_approval_validation_dry_run,
    write_temporal_continuity_operator_authorization_record_approval_validation_dry_run,
)
from scripts.temporal import run_temporal_continuity_operator_authorization_record_approval_validation_dry_run

SOURCE = "out/temporal_continuity_operator_authorization_record_approval_validation_plan/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p87(root: Path, status: str) -> None:
    _write_json(
        root / SOURCE,
        {
            "approval_validation_plan_status": status,
            "approval_validation_plan_hash": "abc123",
            "source_approval_dry_run_path": "out/temporal_continuity_operator_authorization_record_approval_dry_run/latest.json",
            "approval_invariant_validation_requirements": ["invariant_a", "invariant_b"],
            "operator_acknowledgement_validation_requirements": ["ack_a"],
            "approval_constraint_validation_requirements": ["constraint_a"],
            "approval_provenance_validation_requirements": ["prov_a"],
            "approval_hash_validation_requirements": ["hash_a"],
            "approval_blocker_validation_requirements": ["blocker_a"],
            "allowed_target_candidates": ["out/a.json"],
            "denied_target_candidates": ["canon://*"],
            "allowed_command_candidates": ["python scripts/run_x.py"],
            "denied_command_candidates": ["rm -rf /"],
            "planned_authorization_scope": ["scope_a"],
            "planned_expected_outputs": ["out/a.json"],
            "advisory_only": True,
            "projection_only": True,
            "approval_validation_plan_only": True,
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
    packet = build_temporal_continuity_operator_authorization_record_approval_validation_dry_run(repo_root=tmp_path)
    assert packet["approval_validation_dry_run_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P87_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN"


def test_ready_source_produces_ready(tmp_path: Path) -> None:
    _seed_p87(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_validation_dry_run(repo_root=tmp_path)
    assert packet["approval_validation_dry_run_status"] == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY"
    assert packet["recommended_next_lane"] == "P89_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN"


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p87(tmp_path, "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_DRY_RUN")
    packet = build_temporal_continuity_operator_authorization_record_approval_validation_dry_run(repo_root=tmp_path)
    assert packet["approval_validation_dry_run_status"] == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN"


def test_failed_checks_produce_failed_status(tmp_path: Path) -> None:
    _seed_p87(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN_READY")
    source = tmp_path / SOURCE
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["approval_granted"] = True
    _write_json(source, payload)
    packet = build_temporal_continuity_operator_authorization_record_approval_validation_dry_run(repo_root=tmp_path)
    assert packet["approval_validation_dry_run_status"] == "APPROVAL_VALIDATION_DRY_RUN_FAILED"


def test_validation_groups_present(tmp_path: Path) -> None:
    _seed_p87(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_validation_dry_run(repo_root=tmp_path)
    assert packet["executed_approval_invariant_validation_checks"]
    assert packet["operator_acknowledgement_validation_results"]
    assert packet["approval_constraint_validation_results"]
    assert packet["approval_provenance_validation_results"]
    assert packet["approval_hash_validation_results"]
    assert packet["approval_blocker_validation_results"]
    assert packet["authority_invariant_results"]


def test_authority_locks_false(tmp_path: Path) -> None:
    _seed_p87(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_validation_dry_run(repo_root=tmp_path)
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["authorization_authority"] is False
    assert packet["authorization_record_creation_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["valid_for_execution"] is False


def test_hash_stable(tmp_path: Path) -> None:
    _seed_p87(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN_READY")
    a = build_temporal_continuity_operator_authorization_record_approval_validation_dry_run(repo_root=tmp_path)
    b = build_temporal_continuity_operator_authorization_record_approval_validation_dry_run(repo_root=tmp_path)
    assert a["approval_validation_dry_run_hash"] == b["approval_validation_dry_run_hash"]


def test_runner_deterministic_write(tmp_path: Path) -> None:
    _seed_p87(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN_READY")
    out_path = tmp_path / "out/temporal_continuity_operator_authorization_record_approval_validation_dry_run/latest.json"
    first = run_temporal_continuity_operator_authorization_record_approval_validation_dry_run.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_approval_validation_dry_run.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["approval_validation_dry_run_hash"] == second["approval_validation_dry_run_hash"]
    assert first_text == second_text


def test_registry_includes_artifact() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/temporal_continuity_operator_authorization_record_approval_validation_dry_run/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS


def test_writer_final_newline(tmp_path: Path) -> None:
    _seed_p87(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_validation_dry_run(repo_root=tmp_path)
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_approval_validation_dry_run(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
