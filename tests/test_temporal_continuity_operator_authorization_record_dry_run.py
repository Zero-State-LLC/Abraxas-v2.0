from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_dry_run import (
    build_temporal_continuity_operator_authorization_record_dry_run,
    write_temporal_continuity_operator_authorization_record_dry_run,
)
from scripts.temporal import run_temporal_continuity_operator_authorization_record_dry_run


SOURCE = "out/temporal_continuity_operator_authorization_record_template/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p81(root: Path, status: str) -> None:
    _write_json(
        root / SOURCE,
        {
            "template_status": status,
            "required_operator_fields": ["operator_id", "operator_name"],
            "required_authorization_fields": ["authorization_scope"],
            "required_command_fields": ["authorized_commands"],
            "required_provenance_fields": ["source_authorization_record_plan_path"],
            "required_hash_fields": ["template_hash"],
            "allowed_target_candidates": ["out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"],
            "denied_target_candidates": ["canon://*"],
            "allowed_command_candidates": ["python scripts/temporal/run_temporal_continuity_upstream_input_regeneration_execution_plan.py"],
            "denied_command_candidates": ["rm *"],
            "planned_authorization_scope": ["upstream_input_regeneration_authorization_record_creation_only"],
            "planned_expected_outputs": ["out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"],
        },
    )


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_dry_run(repo_root=tmp_path)
    assert packet["dry_run_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P81_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE"


def test_ready_source_produces_dry_run_ready(tmp_path: Path) -> None:
    _seed_p81(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY")
    packet = build_temporal_continuity_operator_authorization_record_dry_run(repo_root=tmp_path)
    assert packet["dry_run_status"] == "OPERATOR_AUTHORIZATION_RECORD_DRY_RUN_READY"
    assert packet["recommended_next_lane"] == "P83_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_VALIDATION_PLAN"


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p81(tmp_path, "NOT_COMPUTABLE")
    packet = build_temporal_continuity_operator_authorization_record_dry_run(repo_root=tmp_path)
    assert packet["dry_run_status"] == "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE"
    assert packet["recommended_next_lane"] == "P81_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE"


def test_simulated_record_and_invariants(tmp_path: Path) -> None:
    _seed_p81(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY")
    packet = build_temporal_continuity_operator_authorization_record_dry_run(repo_root=tmp_path)
    sim = packet["simulated_authorization_record"]
    assert sim["simulated_only"] is True
    assert sim["valid_for_execution"] is False
    assert sim["authorization_granted"] is False
    assert sim["execution_authority"] is False
    assert sim["token_minting_allowed"] is False
    assert sim["record_creation_authority"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["operator_approval_required"] is True
    assert packet["valid_for_execution"] is False


def test_required_fields_present(tmp_path: Path) -> None:
    _seed_p81(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY")
    packet = build_temporal_continuity_operator_authorization_record_dry_run(repo_root=tmp_path)
    for key in [
        "schema_version", "dry_run_id", "source_template_path", "source_template_hash", "dry_run_status",
        "simulated_authorization_record", "simulated_record_validation", "required_operator_fields",
        "required_authorization_fields", "required_command_fields", "required_provenance_fields",
        "required_hash_fields", "allowed_target_candidates", "denied_target_candidates", "allowed_command_candidates",
        "denied_command_candidates", "planned_authorization_scope", "planned_expected_outputs", "validation_blockers",
        "recommended_next_lane", "blockers", "dry_run_hash",
    ]:
        assert key in packet


def test_dry_run_hash_stable(tmp_path: Path) -> None:
    _seed_p81(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY")
    a = build_temporal_continuity_operator_authorization_record_dry_run(repo_root=tmp_path)
    b = build_temporal_continuity_operator_authorization_record_dry_run(repo_root=tmp_path)
    assert a["dry_run_hash"] == b["dry_run_hash"]


def test_runner_deterministic_write(tmp_path: Path) -> None:
    _seed_p81(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY")
    out_path = tmp_path / "out/temporal_continuity_operator_authorization_record_dry_run/latest.json"
    first = run_temporal_continuity_operator_authorization_record_dry_run.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_dry_run.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["dry_run_hash"] == second["dry_run_hash"]
    assert first_text == second_text


def test_writer_final_newline(tmp_path: Path) -> None:
    _seed_p81(tmp_path, "OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY")
    packet = build_temporal_continuity_operator_authorization_record_dry_run(repo_root=tmp_path)
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_dry_run(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")


def test_registry_includes_artifact() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/temporal_continuity_operator_authorization_record_dry_run/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
