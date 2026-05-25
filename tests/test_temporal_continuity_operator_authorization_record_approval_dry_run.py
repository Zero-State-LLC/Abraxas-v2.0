from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_dry_run import (
    build_temporal_continuity_operator_authorization_record_approval_dry_run,
    write_temporal_continuity_operator_authorization_record_approval_dry_run,
)
from scripts import run_temporal_continuity_operator_authorization_record_approval_dry_run

SOURCE = "out/temporal_continuity_operator_authorization_record_approval_plan/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p85(root: Path, status: str) -> None:
    _write_json(
        root / SOURCE,
        {
            "approval_plan_status": status,
            "approval_plan_hash": "abc123",
            "source_validation_dry_run_path": "out/temporal_continuity_operator_authorization_record_validation_dry_run/latest.json",
            "required_operator_acknowledgements": ["ack_a", "ack_b"],
            "approval_constraints": ["constraint_a", "constraint_b"],
            "allowed_target_candidates": ["out/a.json"],
            "denied_target_candidates": ["canon://*"],
            "allowed_command_candidates": ["python scripts/run_x.py"],
            "denied_command_candidates": ["rm -rf /"],
            "planned_authorization_scope": ["scope_a"],
            "planned_expected_outputs": ["out/a.json"],
            "advisory_only": True,
            "projection_only": True,
            "approval_plan_only": True,
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
        },
    )


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_approval_dry_run(repo_root=tmp_path)
    assert packet["approval_dry_run_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P85_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN"


def test_ready_source_produces_ready(tmp_path: Path) -> None:
    _seed_p85(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_dry_run(repo_root=tmp_path)
    assert packet["approval_dry_run_status"] == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_DRY_RUN_READY"
    assert packet["recommended_next_lane"] == "P87_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN"


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p85(tmp_path, "BLOCKED_BY_FAILED_VALIDATION_DRY_RUN")
    packet = build_temporal_continuity_operator_authorization_record_approval_dry_run(repo_root=tmp_path)
    assert packet["approval_dry_run_status"] == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN"


def test_simulated_groups_and_evaluations_present(tmp_path: Path) -> None:
    _seed_p85(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_dry_run(repo_root=tmp_path)
    assert packet["simulated_operator_acknowledgements"]
    assert packet["simulated_approval_evaluation"]
    assert packet["approval_constraints_evaluation"]
    assert packet["approval_provenance_evaluation"]
    assert packet["approval_hash_evaluation"]

def test_source_governance_drift_blocks(tmp_path: Path) -> None:
    _seed_p85(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN_READY")
    source = tmp_path / SOURCE
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["execution_authority"] = True
    _write_json(source, payload)
    packet = build_temporal_continuity_operator_authorization_record_approval_dry_run(repo_root=tmp_path)
    assert packet["approval_dry_run_status"] == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN"
    assert any(str(b).startswith("governance_invariant_failed:") for b in packet["approval_blockers"])


def test_authority_invariants_locked_false(tmp_path: Path) -> None:
    _seed_p85(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_dry_run(repo_root=tmp_path)
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["authorization_authority"] is False
    assert packet["authorization_record_creation_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["valid_for_execution"] is False


def test_hash_stable(tmp_path: Path) -> None:
    _seed_p85(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN_READY")
    a = build_temporal_continuity_operator_authorization_record_approval_dry_run(repo_root=tmp_path)
    b = build_temporal_continuity_operator_authorization_record_approval_dry_run(repo_root=tmp_path)
    assert a["approval_dry_run_hash"] == b["approval_dry_run_hash"]


def test_runner_deterministic_write(tmp_path: Path) -> None:
    _seed_p85(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN_READY")
    out_path = tmp_path / "out/temporal_continuity_operator_authorization_record_approval_dry_run/latest.json"
    first = run_temporal_continuity_operator_authorization_record_approval_dry_run.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_approval_dry_run.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["approval_dry_run_hash"] == second["approval_dry_run_hash"]
    assert first_text == second_text


def test_registry_includes_artifact() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/temporal_continuity_operator_authorization_record_approval_dry_run/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS


def test_writer_final_newline(tmp_path: Path) -> None:
    _seed_p85(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_dry_run(repo_root=tmp_path)
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_approval_dry_run(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
