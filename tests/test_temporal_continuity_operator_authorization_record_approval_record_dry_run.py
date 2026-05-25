from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_dry_run import (
    build_temporal_continuity_operator_authorization_record_approval_record_dry_run,
    write_temporal_continuity_operator_authorization_record_approval_record_dry_run,
)
from scripts import run_temporal_continuity_operator_authorization_record_approval_record_dry_run

SOURCE = "out/temporal_continuity_operator_authorization_record_approval_record_plan/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p89(root: Path, status: str) -> None:
    _write_json(
        root / SOURCE,
        {
            "approval_record_plan_status": status,
            "approval_record_plan_hash": "abc123",
            "source_approval_validation_dry_run_path": "out/temporal_continuity_operator_authorization_record_approval_validation_dry_run/latest.json",
            "source_approval_validation_dry_run_hash": "seeded_sha256",
            "source_approval_validation_dry_run_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY",
            "required_approval_record_fields": {"identity_fields": ["approval_record_id"]},
            "advisory_only": True,
            "projection_only": True,
            "approval_record_plan_only": True,
            "approval_record_creation_authority": False,
            "approval_record_created": False,
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
        },
    )


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_approval_record_dry_run(repo_root=tmp_path)
    assert packet["approval_record_dry_run_status"] == "NOT_COMPUTABLE"


def test_ready_source_produces_ready(tmp_path: Path) -> None:
    _seed_p89(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_dry_run(repo_root=tmp_path)
    assert packet["approval_record_dry_run_status"] == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_DRY_RUN_READY"


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p89(tmp_path, "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_dry_run(repo_root=tmp_path)
    assert packet["approval_record_dry_run_status"] == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN"


def test_authority_locks_false(tmp_path: Path) -> None:
    _seed_p89(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_dry_run(repo_root=tmp_path)
    for key in (
        "approval_record_created",
        "approval_record_creation_authority",
        "approval_granted",
        "authorization_granted",
        "execution_authority",
        "token_minting_allowed",
        "valid_for_execution",
    ):
        assert packet[key] is False


def test_hash_stable(tmp_path: Path) -> None:
    _seed_p89(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN_READY")
    a = build_temporal_continuity_operator_authorization_record_approval_record_dry_run(repo_root=tmp_path)
    b = build_temporal_continuity_operator_authorization_record_approval_record_dry_run(repo_root=tmp_path)
    assert a["approval_record_dry_run_hash"] == b["approval_record_dry_run_hash"]


def test_runner_deterministic_write(tmp_path: Path) -> None:
    _seed_p89(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN_READY")
    out_path = tmp_path / "out/temporal_continuity_operator_authorization_record_approval_record_dry_run/latest.json"
    first = run_temporal_continuity_operator_authorization_record_approval_record_dry_run.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_approval_record_dry_run.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["approval_record_dry_run_hash"] == second["approval_record_dry_run_hash"]
    assert first_text == second_text


def test_registry_includes_artifact() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/temporal_continuity_operator_authorization_record_approval_record_dry_run/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS


def test_writer_final_newline(tmp_path: Path) -> None:
    _seed_p89(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_approval_record_dry_run(repo_root=tmp_path)
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_approval_record_dry_run(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
