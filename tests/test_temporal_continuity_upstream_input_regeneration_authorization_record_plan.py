from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_upstream_input_regeneration_authorization_record_plan import (
    build_temporal_continuity_upstream_input_regeneration_authorization_record_plan,
    write_temporal_continuity_upstream_input_regeneration_authorization_record_plan,
)
from scripts.temporal import (
    run_temporal_continuity_upstream_input_regeneration_authorization_record_plan,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p79(
    root: Path,
    *,
    authorization_gate_status: str = "AUTHORIZATION_ELIGIBLE",
    source_recommended_next_lane: str = "P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_EXECUTION_PLAN",
    eligible_execution_steps: list[dict[str, object]] | None = None,
    eligible_commands: list[dict[str, object]] | None = None,
    authorization_required: bool = True,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    step = {
        "step_id": "step_001",
        "target_input_path": "out/projections/temporal_state_diff_001.latest.json",
        "proposed_command": "python scripts/temporal/run_temporal_state_diff.py",
        "generator_script": "scripts/temporal/run_temporal_state_diff.py",
        "expected_output_path": "out/projections/temporal_state_diff_001.latest.json",
        "owning_output_path": "out/projections/temporal_resonance_coherence_001.latest.json",
        "group_id": "temporal_coherence_chain",
        "prerequisite_role": "temporal_diff_input",
        "preflight_required": True,
        "post_run_validation_required": True,
        "rollback_strategy": "NO_OP_P79_ADVISORY_ONLY",
        "execution_authorized": False,
        "blocking_reason": "FUTURE_AUTHORIZATION_GATE_REQUIRED",
    }
    command = {
        "command": "python scripts/temporal/run_temporal_state_diff.py",
        "generator_script": "scripts/temporal/run_temporal_state_diff.py",
        "expected_output_path": "out/projections/temporal_state_diff_001.latest.json",
        "allowlisted_for_future_execution": True,
        "execution_authorized": False,
    }
    _write_json(
        root
        / "out"
        / "temporal_continuity_upstream_input_regeneration_authorization_gate"
        / "latest.json",
        {
            "artifact_type": "TemporalContinuityUpstreamInputRegenerationAuthorizationGate.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "authorization_gate_only": True,
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
            "authorization_authority": False,
            "spine_implementation_authority": False,
            "source_execution_plan_path": "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json",
            "source_execution_plan_observed": True,
            "source_execution_plan_hash": "1" * 64,
            "source_execution_plan_status": "EXECUTION_PLAN_READY",
            "source_recommended_next_lane": source_recommended_next_lane,
            "authorization_gate_status": authorization_gate_status,
            "authorization_eligible": authorization_gate_status == "AUTHORIZATION_ELIGIBLE",
            "authorization_granted": False,
            "authorization_required_record": {
                "required": authorization_required,
                "required_record_type": "OPERATOR_AUTHORIZATION_TOKEN_V1"
                if authorization_required
                else "NOT_REQUIRED",
                "required_record_path": "out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"
                if authorization_required
                else "NOT_COMPUTABLE",
                "required_fields": [
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
                if authorization_required
                else [],
                "authorization_token_observed": False,
                "authorization_token_hash": "NOT_COMPUTABLE",
            },
            "eligible_execution_steps": eligible_execution_steps
            if eligible_execution_steps is not None
            else [step],
            "blocked_execution_steps": [],
            "eligible_commands": eligible_commands
            if eligible_commands is not None
            else [command],
            "blocked_commands": [],
            "operator_review_requirements": [],
            "preflight_review_requirements": [],
            "post_authorization_requirements": [],
            "degraded_evidence_inputs": degraded_evidence_inputs
            if degraded_evidence_inputs is not None
            else [],
            "inherited_blockers": inherited_blockers
            if inherited_blockers is not None
            else ["b2", "b1"],
            "inherited_drift_flags": inherited_drift_flags
            if inherited_drift_flags is not None
            else ["d2", "d1"],
            "semantic_overlap_flags": semantic_overlap_flags
            if semantic_overlap_flags is not None
            else ["s2", "s1"],
            "authorization_strategy_summary": {
                "source_execution_steps_count": 1,
                "eligible_execution_steps_count": 1,
                "blocked_execution_steps_count": 0,
                "eligible_commands_count": 1,
                "blocked_commands_count": 0,
                "operator_review_requirements_count": 6,
                "preflight_review_requirements_count": 0,
                "post_authorization_requirements_count": 1,
                "authorization_required": authorization_required,
            },
            "recommended_next_lane": "P80_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_RECORD_PLAN",
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "2" * 64,
        },
    )


# ---------------------------------------------------------------------------
# Status routing tests
# ---------------------------------------------------------------------------


def test_missing_p79_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_plan_status"] == "NOT_COMPUTABLE"
    assert packet["authorization_record_required"] is False
    assert packet["authorization_record_creation_allowed"] is False
    assert packet["operator_approved"] is False
    assert packet["authorization_granted"] is False
    assert packet["recommended_next_lane"] == "P79_AUTHORIZATION_GATE_REGENERATION"


def test_malformed_p79_source_returns_not_computable(tmp_path: Path) -> None:
    target = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_authorization_gate"
        / "latest.json"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P79_AUTHORIZATION_GATE_REGENERATION"


def test_authorization_eligible_returns_authorization_record_plan_ready(
    tmp_path: Path,
) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_plan_status"] == "AUTHORIZATION_RECORD_PLAN_READY"
    assert packet["authorization_record_required"] is True
    assert packet["authorization_record_creation_allowed"] is False
    assert packet["operator_approved"] is False
    assert packet["authorization_granted"] is False
    assert (
        packet["recommended_next_lane"]
        == "P81_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE"
    )


def test_authorization_blocked_returns_authorization_record_plan_blocked(
    tmp_path: Path,
) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_BLOCKED",
        authorization_required=False,
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_plan_status"] == "AUTHORIZATION_RECORD_PLAN_BLOCKED"
    assert packet["authorization_record_required"] is False
    assert packet["authorization_record_creation_allowed"] is False
    assert packet["operator_approved"] is False
    assert packet["authorization_granted"] is False
    assert (
        packet["recommended_next_lane"]
        == "P81_TEMPORAL_CONTINUITY_AUTHORIZATION_BLOCKER_REPAIR_PLAN"
    )


def test_authorization_not_required_returns_authorization_record_not_required(
    tmp_path: Path,
) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_NOT_REQUIRED",
        source_recommended_next_lane="P80_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
        authorization_required=False,
        degraded_evidence_inputs=[],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_plan_status"] == "AUTHORIZATION_RECORD_NOT_REQUIRED"
    assert packet["authorization_record_required"] is False
    assert packet["authorization_record_creation_allowed"] is False
    assert (
        packet["recommended_next_lane"]
        == "P81_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE"
    )


# ---------------------------------------------------------------------------
# Governance lock tests
# ---------------------------------------------------------------------------


def test_authorization_record_creation_allowed_always_false(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_creation_allowed"] is False


def test_authorization_record_creation_authority_always_false(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_creation_authority"] is False


def test_authorization_authority_always_false(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_authority"] is False


def test_execution_authority_always_false(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["execution_authority"] is False


def test_operator_approved_always_false(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["operator_approved"] is False


def test_authorization_granted_always_false(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_granted"] is False


# ---------------------------------------------------------------------------
# Planned authorization record shape tests
# ---------------------------------------------------------------------------


def test_planned_authorization_record_is_shape_only_no_token_file(
    tmp_path: Path,
) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    token_path = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_authorization_record"
        / "latest.json"
    )
    assert not token_path.exists()


def test_planned_authorization_record_operator_approved_false(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["planned_authorization_record"]["operator_approved"] is False


def test_planned_authorization_record_authorization_granted_false(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["planned_authorization_record"]["authorization_granted"] is False


def test_planned_authorization_record_execution_authority_false(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["planned_authorization_record"]["execution_authority"] is False


def test_planned_authorization_record_packet_hash_required_true(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["planned_authorization_record"]["packet_hash_required"] is True


def test_planned_authorization_record_operator_approval_required_true(
    tmp_path: Path,
) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["planned_authorization_record"]["operator_approval_required"] is True


# ---------------------------------------------------------------------------
# Scope and candidate derivation tests
# ---------------------------------------------------------------------------


def test_authorization_scope_derives_only_from_eligible_execution_steps(
    tmp_path: Path,
) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_ELIGIBLE",
        eligible_execution_steps=[
            {
                "step_id": "step_001",
                "target_input_path": "out/projections/foo.latest.json",
                "proposed_command": "python scripts/run_foo.py",
                "generator_script": "scripts/run_foo.py",
                "expected_output_path": "out/projections/foo.latest.json",
                "owning_output_path": "out/projections/owner.latest.json",
                "group_id": "g1",
                "prerequisite_role": "role_a",
                "preflight_required": True,
                "post_run_validation_required": True,
                "rollback_strategy": "NO_OP",
                "execution_authorized": False,
                "blocking_reason": "",
            }
        ],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_scope"] == ["out/projections/foo.latest.json"]


def test_authorized_command_candidates_derive_only_from_eligible_commands(
    tmp_path: Path,
) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_ELIGIBLE",
        eligible_commands=[
            {
                "command": "python scripts/run_a.py",
                "generator_script": "scripts/run_a.py",
                "expected_output_path": "out/a.latest.json",
                "allowlisted_for_future_execution": True,
                "execution_authorized": False,
            }
        ],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorized_command_candidates"] == ["python scripts/run_a.py"]


def test_blocked_commands_excluded_from_authorized_candidates(tmp_path: Path) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_BLOCKED",
        eligible_commands=[],
        authorization_required=False,
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorized_command_candidates"] == []
    assert packet["authorization_scope"] == []


def test_authorization_not_eligible_produces_empty_candidates(tmp_path: Path) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_NOT_REQUIRED",
        source_recommended_next_lane="P80_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
        authorization_required=False,
        degraded_evidence_inputs=[],
        eligible_commands=[
            {
                "command": "python scripts/run_a.py",
                "generator_script": "scripts/run_a.py",
                "expected_output_path": "out/a.latest.json",
                "allowlisted_for_future_execution": True,
                "execution_authorized": False,
            }
        ],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorized_command_candidates"] == []
    assert packet["authorization_scope"] == []


# ---------------------------------------------------------------------------
# Provenance binding tests
# ---------------------------------------------------------------------------


def test_provenance_bindings_include_source_authorization_gate_hash(
    tmp_path: Path,
) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    bindings = packet["provenance_bindings"]
    assert "source_authorization_gate_hash" in bindings
    assert bindings["source_authorization_gate_hash"] != "NOT_COMPUTABLE"
    assert len(bindings["source_authorization_gate_hash"]) == 64


# ---------------------------------------------------------------------------
# Operator approval requirements tests
# ---------------------------------------------------------------------------


def test_operator_approval_requirements_include_all_required_review_types(
    tmp_path: Path,
) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    req_types = {item["requirement_type"] for item in packet["operator_approval_requirements"]}
    assert {
        "explicit_operator_approval",
        "command_review",
        "output_path_review",
        "scope_review",
        "source_hash_review",
        "expiration_policy_review",
        "revocation_policy_review",
        "no_op_rollback_review",
        "post_run_validation_review",
        "authority_denial_confirmation",
    } <= req_types


# ---------------------------------------------------------------------------
# Token creation requirement tests
# ---------------------------------------------------------------------------


def test_token_creation_requirements_state_future_lane_only(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    req_types = {item["requirement_type"] for item in packet["token_creation_requirements"]}
    assert "future_lane_only" in req_types
    assert "not_generated_by_p80" in req_types


# ---------------------------------------------------------------------------
# Inherited evidence preservation tests
# ---------------------------------------------------------------------------


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_BLOCKED",
        degraded_evidence_inputs=["e2", "e1"],
        authorization_required=False,
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_BLOCKED",
        inherited_blockers=["b2", "b1"],
        authorization_required=False,
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_BLOCKED",
        inherited_drift_flags=["d2", "d1"],
        authorization_required=False,
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_BLOCKED",
        semantic_overlap_flags=["s2", "s1"],
        authorization_required=False,
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


# ---------------------------------------------------------------------------
# Determinism tests
# ---------------------------------------------------------------------------


def test_authorization_record_strategy_summary_deterministic(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    first = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert (
        first["authorization_record_strategy_summary"]
        == second["authorization_record_strategy_summary"]
    )
    assert first["packet_hash"] == second["packet_hash"]


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    first = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


# ---------------------------------------------------------------------------
# Schema lock tests
# ---------------------------------------------------------------------------


def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_upstream_input_regeneration_authorization_record_plan.v1.schema.json"
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
        "authorization_record_creation_authority",
        "spine_implementation_authority",
    ):
        assert schema["properties"][field]["const"] is False, field


def test_schema_locks_authorization_granted_and_operator_approved_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_upstream_input_regeneration_authorization_record_plan.v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["properties"]["authorization_granted"]["const"] is False
    assert schema["properties"]["operator_approved"]["const"] is False
    assert schema["properties"]["authorization_record_creation_allowed"]["const"] is False
    planned = schema["properties"]["planned_authorization_record"]["properties"]
    assert planned["operator_approved"]["const"] is False
    assert planned["authorization_granted"]["const"] is False
    assert planned["execution_authority"]["const"] is False
    assert planned["packet_hash_required"]["const"] is True


# ---------------------------------------------------------------------------
# Writer and runner tests
# ---------------------------------------------------------------------------


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_authorization_record_plan"
        / "latest.json"
    )
    write_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        out_path, packet
    )
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p79(tmp_path, authorization_gate_status="AUTHORIZATION_ELIGIBLE")
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_authorization_record_plan"
        / "latest.json"
    )
    first = run_temporal_continuity_upstream_input_regeneration_authorization_record_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_upstream_input_regeneration_authorization_record_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


# ---------------------------------------------------------------------------
# Artifact registry classification test
# ---------------------------------------------------------------------------


def test_artifact_registry_classifies_output_as_derived_optional() -> None:
    from core.generated_artifact_registry import (  # type: ignore[attr-defined]
        _DERIVED_OPTIONAL_ARTIFACTS,
        build_generated_artifact_registry,
        list_ci_drift_artifact_paths,
    )

    artifact = "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)


# ---------------------------------------------------------------------------
# AUTHORIZATION_NOT_REQUIRED routing variant tests
# ---------------------------------------------------------------------------


def test_authorization_not_required_with_degraded_evidence_routes_to_repair(
    tmp_path: Path,
) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_NOT_REQUIRED",
        source_recommended_next_lane="P80_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
        authorization_required=False,
        degraded_evidence_inputs=["e1"],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_plan_status"] == "AUTHORIZATION_RECORD_NOT_REQUIRED"
    assert (
        packet["recommended_next_lane"]
        == "P81_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"
    )


def test_authorization_not_required_with_artifact_dry_run_lane(tmp_path: Path) -> None:
    _seed_p79(
        tmp_path,
        authorization_gate_status="AUTHORIZATION_NOT_REQUIRED",
        source_recommended_next_lane="P80_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
        authorization_required=False,
        degraded_evidence_inputs=[],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_plan_status"] == "AUTHORIZATION_RECORD_NOT_REQUIRED"
    assert (
        packet["recommended_next_lane"]
        == "P81_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN"
    )
