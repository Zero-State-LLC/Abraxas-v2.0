from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_template import (
    build_temporal_continuity_operator_authorization_record_template,
    write_temporal_continuity_operator_authorization_record_template,
)
from scripts import run_temporal_continuity_operator_authorization_record_template


SOURCE = "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _seed_p80(root: Path, status: str) -> None:
    _write_json(root / SOURCE, {"authorization_record_plan_status": status})


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_temporal_continuity_operator_authorization_record_template(repo_root=tmp_path)
    assert packet["template_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P80_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_RECORD_PLAN"


def test_ready_source_routes_to_p82(tmp_path: Path) -> None:
    _seed_p80(tmp_path, "AUTHORIZATION_RECORD_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_template(repo_root=tmp_path)
    assert packet["template_status"] == "OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY"
    assert packet["recommended_next_lane"] == "P82_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_DRY_RUN"


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_p80(tmp_path, "AUTHORIZATION_RECORD_PLAN_BLOCKED")
    packet = build_temporal_continuity_operator_authorization_record_template(repo_root=tmp_path)
    assert packet["template_status"] == "BLOCKED_BY_AUTHORIZATION_RECORD_PLAN"
    assert packet["recommended_next_lane"] == "P80_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_RECORD_PLAN"


def test_required_fields_and_governance_invariants_present(tmp_path: Path) -> None:
    _seed_p80(tmp_path, "AUTHORIZATION_RECORD_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_template(repo_root=tmp_path)
    for key in [
        "schema_version", "template_id", "source_authorization_record_plan_path", "source_authorization_record_plan_hash",
        "template_status", "required_operator_fields", "required_authorization_fields", "required_command_fields",
        "required_provenance_fields", "required_hash_fields", "allowed_target_candidates", "denied_target_candidates",
        "allowed_command_candidates", "denied_command_candidates", "planned_authorization_scope", "planned_expected_outputs",
        "operator_approval_requirements", "record_creation_requirements", "recommended_next_lane", "blockers", "template_hash",
    ]:
        assert key in packet
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["authorization_authority"] is False
    assert packet["authorization_record_creation_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["operator_approval_required"] is True


def test_template_hash_stable(tmp_path: Path) -> None:
    _seed_p80(tmp_path, "AUTHORIZATION_RECORD_PLAN_READY")
    a = build_temporal_continuity_operator_authorization_record_template(repo_root=tmp_path)
    b = build_temporal_continuity_operator_authorization_record_template(repo_root=tmp_path)
    assert a["template_hash"] == b["template_hash"]


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    _seed_p80(tmp_path, "AUTHORIZATION_RECORD_PLAN_READY")
    out_path = tmp_path / "out/temporal_continuity_operator_authorization_record_template/latest.json"
    first = run_temporal_continuity_operator_authorization_record_template.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_operator_authorization_record_template.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["template_hash"] == second["template_hash"]
    assert first_text == second_text


def test_registry_includes_artifact_as_derived_optional() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/temporal_continuity_operator_authorization_record_template/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS


def test_writer_appends_final_newline(tmp_path: Path) -> None:
    _seed_p80(tmp_path, "AUTHORIZATION_RECORD_PLAN_READY")
    packet = build_temporal_continuity_operator_authorization_record_template(repo_root=tmp_path)
    out_path = tmp_path / "x/latest.json"
    write_temporal_continuity_operator_authorization_record_template(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
