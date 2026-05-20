from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_upstream_input_regeneration_authorization_gate import (
    build_temporal_continuity_upstream_input_regeneration_authorization_gate,
    write_temporal_continuity_upstream_input_regeneration_authorization_gate,
)
from scripts import run_temporal_continuity_upstream_input_regeneration_authorization_gate


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p78(
    root: Path,
    *,
    execution_plan_status: str = "EXECUTION_PLAN_READY",
    recommended_next_lane: str = "P79_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_GATE",
    execution_steps: list[dict[str, object]] | None = None,
    command_allowlist: list[dict[str, object]] | None = None,
    preflight_checks: list[dict[str, object]] | None = None,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    step = {
        "step_id": "step_001",
        "target_input_path": "out/projections/temporal_state_diff_001.latest.json",
        "proposed_command": "python scripts/run_temporal_state_diff.py",
        "generator_script": "scripts/run_temporal_state_diff.py",
        "expected_output_path": "out/projections/temporal_state_diff_001.latest.json",
        "owning_output_path": "out/projections/temporal_resonance_coherence_001.latest.json",
        "group_id": "temporal_coherence_chain",
        "prerequisite_role": "temporal_diff_input",
        "preflight_required": True,
        "post_run_validation_required": True,
        "rollback_strategy": "NO_OP_P78_ADVISORY_ONLY_EXECUTION_NOT_PERMITTED",
        "execution_authorized": False,
        "blocking_reason": "FUTURE_AUTHORIZATION_GATE_REQUIRED_P78_EXECUTION_PLAN_ONLY",
    }
    allowlist = {
        "command": "python scripts/run_temporal_state_diff.py",
        "generator_script": "scripts/run_temporal_state_diff.py",
        "expected_output_path": "out/projections/temporal_state_diff_001.latest.json",
        "allowlisted_for_future_execution": True,
        "execution_authorized": False,
    }
    preflight = {
        "check_id": "preflight_001_generator_readable",
        "check_type": "generator_script_readable",
        "path": "scripts/run_temporal_state_diff.py",
        "required_status": "READABLE",
        "failure_action": "FAIL_CLOSED_REQUIRE_GENERATOR_DISCOVERY_OR_REPAIR_PLAN",
    }
    _write_json(
        root
        / "out"
        / "temporal_continuity_upstream_input_regeneration_execution_plan"
        / "latest.json",
        {
            "artifact_type": "TemporalContinuityUpstreamInputRegenerationExecutionPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "execution_plan_only": True,
            "production_activation": False,
            "canon_promotion": False,
            "forecast_influence": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "repair_authority": False,
            "evidence_generation_authority": False,
            "restoration_execution_authority": False,
            "generator_execution_authority": False,
            "upstream_input_generation_authority": False,
            "artifact_regeneration_authority": False,
            "execution_authority": False,
            "spine_implementation_authority": False,
            "source_dry_run_plan_path": "out/temporal_continuity_upstream_input_regeneration_dry_run_plan/latest.json",
            "source_dry_run_plan_observed": True,
            "source_dry_run_plan_hash": "1" * 64,
            "source_dry_run_plan_status": "DRY_RUN_READY_WITH_MISSING_INPUTS",
            "source_recommended_next_lane": "P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_EXECUTION_PLAN",
            "execution_plan_status": execution_plan_status,
            "execution_steps": execution_steps if execution_steps is not None else [step],
            "command_allowlist": command_allowlist if command_allowlist is not None else [allowlist],
            "expected_outputs": [],
            "preflight_checks": preflight_checks if preflight_checks is not None else [preflight],
            "post_run_validations": [],
            "still_blocked_inputs": ["out/projections/temporal_state_diff_001.latest.json"],
            "executable_future_candidates": ["out/projections/temporal_state_diff_001.latest.json"],
            "inherited_dry_run_commands": ["python scripts/run_temporal_state_diff.py"],
            "degraded_evidence_inputs": degraded_evidence_inputs
            if degraded_evidence_inputs is not None
            else ["g2", "g1"],
            "inherited_blockers": inherited_blockers if inherited_blockers is not None else ["b2", "b1"],
            "inherited_drift_flags": inherited_drift_flags
            if inherited_drift_flags is not None
            else ["d2", "d1"],
            "semantic_overlap_flags": semantic_overlap_flags
            if semantic_overlap_flags is not None
            else ["s2", "s1"],
            "execution_strategy_summary": {
                "total_candidates": 1,
                "allowlisted_commands": 1,
                "blocked_candidates": 0,
                "execution_steps_planned": 1,
            },
            "recommended_next_lane": recommended_next_lane,
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "2" * 64,
        },
    )


def test_missing_p78_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["authorization_gate_status"] == "NOT_COMPUTABLE"
    assert packet["authorization_eligible"] is False
    assert packet["authorization_granted"] is False
    assert packet["recommended_next_lane"] == "P78_EXECUTION_PLAN_REGENERATION"


def test_malformed_p78_source_returns_not_computable(tmp_path: Path) -> None:
    target = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_execution_plan"
        / "latest.json"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["authorization_gate_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P78_EXECUTION_PLAN_REGENERATION"


def test_execution_plan_ready_with_allowlisted_command_is_authorization_eligible(
    tmp_path: Path,
) -> None:
    _seed_p78(tmp_path, degraded_evidence_inputs=[])
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["authorization_gate_status"] == "AUTHORIZATION_ELIGIBLE"
    assert packet["authorization_eligible"] is True
    assert packet["authorization_granted"] is False
    assert packet["recommended_next_lane"] == (
        "P80_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_RECORD_PLAN"
    )


def test_execution_plan_ready_without_allowlisted_command_fails_closed(tmp_path: Path) -> None:
    _seed_p78(
        tmp_path,
        command_allowlist=[
            {
                "command": "python scripts/run_temporal_state_diff.py",
                "generator_script": "scripts/run_temporal_state_diff.py",
                "expected_output_path": "out/projections/temporal_state_diff_001.latest.json",
                "allowlisted_for_future_execution": False,
                "execution_authorized": False,
            }
        ],
        degraded_evidence_inputs=[],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["authorization_gate_status"] == "AUTHORIZATION_BLOCKED"
    assert packet["authorization_eligible"] is False


def test_execution_plan_blocked_returns_authorization_blocked(tmp_path: Path) -> None:
    _seed_p78(
        tmp_path,
        execution_plan_status="EXECUTION_PLAN_BLOCKED",
        recommended_next_lane="P79_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REPAIR_PLAN",
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["authorization_gate_status"] == "AUTHORIZATION_BLOCKED"
    assert packet["authorization_eligible"] is False
    assert packet["recommended_next_lane"] == "P80_TEMPORAL_CONTINUITY_EXECUTION_BLOCKER_REPAIR_PLAN"


def test_execution_plan_not_required_returns_authorization_not_required(tmp_path: Path) -> None:
    _seed_p78(
        tmp_path,
        execution_plan_status="EXECUTION_PLAN_NOT_REQUIRED",
        recommended_next_lane="P79_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
        degraded_evidence_inputs=[],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["authorization_gate_status"] == "AUTHORIZATION_NOT_REQUIRED"
    assert packet["authorization_granted"] is False
    assert packet["recommended_next_lane"] == "P80_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE"


def test_authorization_granted_authority_and_execution_authority_always_false(
    tmp_path: Path,
) -> None:
    _seed_p78(tmp_path, degraded_evidence_inputs=[])
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["authorization_granted"] is False
    assert packet["authorization_authority"] is False
    assert packet["execution_authority"] is False


def test_execution_authorized_always_false_in_eligible_execution_steps(tmp_path: Path) -> None:
    _seed_p78(tmp_path, degraded_evidence_inputs=[])
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["eligible_execution_steps"]
    assert all(step["execution_authorized"] is False for step in packet["eligible_execution_steps"])


def test_authorization_required_record_is_present_when_eligible(tmp_path: Path) -> None:
    _seed_p78(tmp_path, degraded_evidence_inputs=[])
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    record = packet["authorization_required_record"]
    assert record["required"] is True
    assert record["required_record_type"] == "OPERATOR_AUTHORIZATION_TOKEN_V1"
    assert record["required_record_path"] == (
        "out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"
    )
    assert record["required_fields"] == [
        "artifact_type",
        "authorization_scope",
        "authorized_commands",
        "authorized_expected_outputs",
        "source_authorization_gate_hash",
        "operator_approval_required",
        "operator_approved",
        "authorization_granted",
        "execution_authority",
        "packet_hash",
    ]


def test_p79_never_observes_or_creates_authorization_token(tmp_path: Path) -> None:
    _seed_p78(tmp_path, degraded_evidence_inputs=[])
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    record = packet["authorization_required_record"]
    assert record["authorization_token_observed"] is False
    assert record["authorization_token_hash"] == "NOT_COMPUTABLE"
    assert not (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_authorization_record"
        / "latest.json"
    ).exists()


def test_eligible_commands_derive_only_from_allowlisted_entries(tmp_path: Path) -> None:
    _seed_p78(
        tmp_path,
        command_allowlist=[
            {
                "command": "python scripts/run_b.py",
                "generator_script": "scripts/run_b.py",
                "expected_output_path": "out/b.latest.json",
                "allowlisted_for_future_execution": False,
                "execution_authorized": False,
            },
            {
                "command": "python scripts/run_a.py",
                "generator_script": "scripts/run_a.py",
                "expected_output_path": "out/a.latest.json",
                "allowlisted_for_future_execution": True,
                "execution_authorized": False,
            },
        ],
        execution_steps=[
            {
                "step_id": "step_002",
                "target_input_path": "out/b.latest.json",
                "proposed_command": "python scripts/run_b.py",
                "generator_script": "scripts/run_b.py",
                "expected_output_path": "out/b.latest.json",
                "owning_output_path": "out/owner_b.latest.json",
                "group_id": "g2",
                "prerequisite_role": "role_b",
                "preflight_required": True,
                "post_run_validation_required": True,
                "rollback_strategy": "NO_OP",
                "execution_authorized": False,
                "blocking_reason": "BLOCKED",
            },
            {
                "step_id": "step_001",
                "target_input_path": "out/a.latest.json",
                "proposed_command": "python scripts/run_a.py",
                "generator_script": "scripts/run_a.py",
                "expected_output_path": "out/a.latest.json",
                "owning_output_path": "out/owner_a.latest.json",
                "group_id": "g1",
                "prerequisite_role": "role_a",
                "preflight_required": True,
                "post_run_validation_required": True,
                "rollback_strategy": "NO_OP",
                "execution_authorized": False,
                "blocking_reason": "ALLOWLISTED",
            },
        ],
        degraded_evidence_inputs=[],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert [item["command"] for item in packet["eligible_commands"]] == [
        "python scripts/run_a.py"
    ]
    assert [item["command"] for item in packet["blocked_commands"]] == [
        "python scripts/run_b.py"
    ]
    assert [step["step_id"] for step in packet["eligible_execution_steps"]] == ["step_001"]
    assert [step["step_id"] for step in packet["blocked_execution_steps"]] == ["step_002"]


def test_operator_review_requirements_cover_required_checks(tmp_path: Path) -> None:
    _seed_p78(tmp_path, degraded_evidence_inputs=[])
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    types = {item["requirement_type"] for item in packet["operator_review_requirements"]}
    assert {
        "operator_approval",
        "authorization_scope",
        "command_review",
        "expected_output_review",
        "rollback_no_op_review",
        "validation_check_review",
    } <= types


def test_preflight_review_requirements_preserve_p78_preflight_checks(tmp_path: Path) -> None:
    preflight_checks = [
        {
            "check_id": "preflight_002_command_allowlisted",
            "check_type": "command_allowlist_compliance",
            "path": "python scripts/run_temporal_state_diff.py",
            "required_status": "ALLOWLISTED",
            "failure_action": "BLOCK_EXECUTION_AND_RETURN_TO_P78_PLANNING",
        },
        {
            "check_id": "preflight_001_generator_readable",
            "check_type": "generator_script_readable",
            "path": "scripts/run_temporal_state_diff.py",
            "required_status": "READABLE",
            "failure_action": "FAIL_CLOSED_REQUIRE_GENERATOR_DISCOVERY_OR_REPAIR_PLAN",
        },
    ]
    _seed_p78(tmp_path, degraded_evidence_inputs=[], preflight_checks=preflight_checks)
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["preflight_review_requirements"] == sorted(
        preflight_checks, key=lambda item: item["check_id"]
    )


def test_post_authorization_requirements_are_future_token_generation_only(
    tmp_path: Path,
) -> None:
    _seed_p78(tmp_path, degraded_evidence_inputs=[])
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["post_authorization_requirements"] == [
        {
            "artifact_regeneration_authority": False,
            "execution_authority": False,
            "generator_execution_authority": False,
            "requirement": "Only a future operator authorization record may be generated after P79; P79 itself never grants execution authority or executes commands.",
            "requirement_id": "post_authorization_001_future_record_only",
            "requirement_type": "future_authorization_record_generation",
            "target_record_path": "out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json",
        }
    ]


def test_inherited_lists_are_preserved_exactly(tmp_path: Path) -> None:
    _seed_p78(
        tmp_path,
        degraded_evidence_inputs=["g2", "g1"],
        inherited_blockers=["b2", "b1"],
        inherited_drift_flags=["d2", "d1"],
        semantic_overlap_flags=["s2", "s1"],
        execution_plan_status="EXECUTION_PLAN_BLOCKED",
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["degraded_evidence_inputs"] == ["g2", "g1"]
    assert packet["inherited_blockers"] == ["b2", "b1"]
    assert packet["inherited_drift_flags"] == ["d2", "d1"]
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


def test_authorization_strategy_summary_is_deterministic(tmp_path: Path) -> None:
    _seed_p78(tmp_path, degraded_evidence_inputs=[])
    first = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    assert first["authorization_strategy_summary"] == second["authorization_strategy_summary"]
    assert first["packet_hash"] == second["packet_hash"]


def test_schema_locks_authority_and_execution_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_upstream_input_regeneration_authorization_gate.v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    for field in (
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "evidence_generation_authority",
        "restoration_execution_authority",
        "generator_execution_authority",
        "upstream_input_generation_authority",
        "artifact_regeneration_authority",
        "execution_authority",
        "authorization_authority",
        "spine_implementation_authority",
    ):
        assert schema["properties"][field]["const"] is False
    assert schema["properties"]["authorization_granted"]["const"] is False
    eligible_step_exec = schema["properties"]["eligible_execution_steps"]["items"]["properties"][
        "execution_authorized"
    ]
    blocked_step_exec = schema["properties"]["blocked_execution_steps"]["items"]["properties"][
        "execution_authorized"
    ]
    assert eligible_step_exec["const"] is False
    assert blocked_step_exec["const"] is False


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p78(tmp_path, degraded_evidence_inputs=[])
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_gate(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_authorization_gate"
        / "latest.json"
    )
    write_temporal_continuity_upstream_input_regeneration_authorization_gate(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p78(tmp_path, degraded_evidence_inputs=[])
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_authorization_gate"
        / "latest.json"
    )
    first = run_temporal_continuity_upstream_input_regeneration_authorization_gate.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_upstream_input_regeneration_authorization_gate.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_artifact_registry_classifies_output_as_derived_optional() -> None:
    from core.generated_artifact_registry import (  # type: ignore[attr-defined]
        _DERIVED_OPTIONAL_ARTIFACTS,
        build_generated_artifact_registry,
        list_ci_drift_artifact_paths,
    )

    artifact = "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
