from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p80_authorization_record_plan_regeneration_plan import (
    build_temporal_continuity_p80_authorization_record_plan_regeneration_plan,
    write_temporal_continuity_p80_authorization_record_plan_regeneration_plan,
)
from scripts.temporal import run_temporal_continuity_p80_authorization_record_plan_regeneration_plan

P83_PATH = "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
P79_PATH = "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json"
P80_PATH = "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p83(
    root: Path,
    *,
    status: str = "P79_STATUS_REPAIR_NOT_REQUIRED",
    recommended_next_lane: str = "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    _write_json(
        root / P83_PATH,
        {
            "artifact_type": "TemporalContinuityP79AuthorizationGateStatusRepairPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "status_repair_plan_only": True,
            "production_activation": False,
            "canon_promotion": False,
            "forecast_influence": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "repair_authority": False,
            "repair_execution_authority": False,
            "evidence_generation_authority": False,
            "restoration_execution_authority": False,
            "generator_execution_authority": False,
            "upstream_input_generation_authority": False,
            "artifact_regeneration_authority": False,
            "execution_authority": False,
            "authorization_authority": False,
            "authorization_record_creation_authority": False,
            "spine_implementation_authority": False,
            "source_p82_repair_plan_path": "out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json",
            "source_p82_repair_plan_observed": True,
            "source_p82_repair_plan_readable": True,
            "source_p82_repair_plan_hash": "a" * 64,
            "source_p82_repair_plan_status": "P79_REPAIR_NOT_REQUIRED",
            "source_p82_recommended_next_lane": "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "p79_status_repair_plan_status": status,
            "p79_source_path": P79_PATH,
            "p79_source_status": "NOT_COMPUTABLE",
            "p79_failure_modes": [],
            "status_repair_items": [],
            "status_field_expectations": [],
            "corrected_status_relationship": {
                "source_p78_status": "NOT_COMPUTABLE",
                "expected_p79_status_if_ready": "NOT_COMPUTABLE",
                "expected_p79_status_if_blocked": "NOT_COMPUTABLE",
                "expected_p80_status_after_p79_repair": "NOT_COMPUTABLE",
                "rerun_sequence": [],
            },
            "blocked_status_repair_reasons": [],
            "prerequisite_sources": [],
            "degraded_evidence_inputs": degraded_evidence_inputs
            if degraded_evidence_inputs is not None
            else ["e2", "e1"],
            "inherited_blockers": inherited_blockers
            if inherited_blockers is not None
            else ["b2", "b1"],
            "inherited_drift_flags": inherited_drift_flags
            if inherited_drift_flags is not None
            else ["d2", "d1"],
            "semantic_overlap_flags": semantic_overlap_flags
            if semantic_overlap_flags is not None
            else ["s2", "s1"],
            "status_repair_strategy_summary": {
                "p82_repair_plan_status": "P79_REPAIR_NOT_REQUIRED",
                "status_repair_items_count": 0,
                "status_repair_strategies": [],
                "blocked_status_repair_reasons_count": 0,
                "prerequisite_sources_count": 0,
            },
            "recommended_next_lane": recommended_next_lane,
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "b" * 64,
        },
    )


def _seed_p79(root: Path, *, status: str = "AUTHORIZATION_ELIGIBLE") -> None:
    _write_json(
        root / P79_PATH,
        {
            "artifact_type": "TemporalContinuityUpstreamInputRegenerationAuthorizationGate.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "authorization_gate_only": True,
            "authorization_gate_status": status,
            "source_execution_plan_path": "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json",
            "source_execution_plan_observed": True,
            "source_execution_plan_hash": "c" * 64,
            "source_execution_plan_status": "EXECUTION_PLAN_READY",
            "source_recommended_next_lane": "P79_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "authorization_eligible": status == "AUTHORIZATION_ELIGIBLE",
            "authorization_required_record": {
                "required": False,
                "required_record_path": "NOT_COMPUTABLE",
                "required_record_type": "NOT_REQUIRED",
                "authorization_token_observed": False,
                "authorization_token_hash": "NOT_COMPUTABLE",
                "required_fields": [],
            },
            "eligible_execution_steps": [],
            "blocked_execution_steps": [],
            "eligible_commands": [],
            "blocked_commands": [],
            "preflight_review_requirements": [],
            "operator_review_requirements": [],
            "post_authorization_requirements": [],
            "degraded_evidence_inputs": [],
            "inherited_blockers": [],
            "inherited_drift_flags": [],
            "semantic_overlap_flags": [],
            "authorization_strategy_summary": {
                "source_execution_steps_count": 0,
                "eligible_execution_steps_count": 0,
                "blocked_execution_steps_count": 0,
                "eligible_commands_count": 0,
                "blocked_commands_count": 0,
                "preflight_review_requirements_count": 0,
                "operator_review_requirements_count": 0,
                "post_authorization_requirements_count": 0,
                "authorization_required": False,
            },
            "recommended_next_lane": "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "recommended_next_lane_reason": "test seed",
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
            "denied_authority": [],
            "packet_hash": "d" * 64,
            "authorization_granted": False,
        },
    )


def _seed_p80(root: Path, *, status: str = "NOT_COMPUTABLE") -> None:
    _write_json(
        root / P80_PATH,
        {
            "artifact_type": "TemporalContinuityUpstreamInputRegenerationAuthorizationRecordPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "authorization_record_plan_only": True,
            "source_authorization_gate_path": P79_PATH,
            "source_authorization_gate_observed": True,
            "source_authorization_gate_hash": "e" * 64,
            "source_authorization_gate_status": "AUTHORIZATION_ELIGIBLE",
            "source_recommended_next_lane": "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "authorization_record_plan_status": status,
            "authorization_record_required": status == "AUTHORIZATION_RECORD_PLAN_READY",
            "authorization_record_creation_allowed": False,
            "operator_approved": False,
            "authorization_granted": False,
            "planned_authorization_record": {
                "artifact_type": "OperatorAuthorizationToken.v1",
                "authorization_scope": [],
                "authorized_commands": [],
                "authorized_expected_outputs": [],
                "source_authorization_gate_hash": "e" * 64,
                "source_authorization_gate_path": P79_PATH,
                "operator_approval_required": True,
                "operator_approved": False,
                "authorization_granted": False,
                "execution_authority": False,
                "authorization_created_by": "NOT_CREATED_BY_P80",
                "authorization_created_at": "NOT_CREATED_BY_P80",
                "expiration_policy": {},
                "revocation_policy": {},
                "validation_requirements": [],
                "packet_hash_required": True,
            },
            "authorization_scope": [],
            "authorized_command_candidates": [],
            "authorized_expected_output_candidates": [],
            "provenance_bindings": {
                "source_authorization_gate_path": P79_PATH,
                "source_authorization_gate_hash": "e" * 64,
                "eligible_step_ids": [],
                "eligible_command_hashes": [],
                "expected_output_paths": [],
                "inherited_degraded_evidence_count": 0,
                "inherited_blocker_count": 0,
                "inherited_drift_flag_count": 0,
            },
            "operator_approval_requirements": [],
            "token_creation_requirements": [],
            "blocked_authorization_reasons": [],
            "degraded_evidence_inputs": [],
            "inherited_blockers": [],
            "inherited_drift_flags": [],
            "semantic_overlap_flags": [],
            "authorization_record_strategy_summary": {
                "source_gate_status": "AUTHORIZATION_ELIGIBLE",
                "authorization_scope_count": 0,
                "authorized_command_candidates_count": 0,
                "authorized_expected_output_candidates_count": 0,
                "provenance_bindings_count": 0,
                "operator_approval_requirements_count": 0,
                "token_creation_requirements_count": 0,
                "blocked_authorization_reasons_count": 0,
                "authorization_record_required": False,
                "authorization_record_creation_allowed": False,
            },
            "recommended_next_lane": "P81_SOURCE_STATUS_AUDIT",
            "recommended_next_lane_reason": "test seed",
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
            "authorization_record_creation_authority": False,
            "spine_implementation_authority": False,
            "denied_authority": [],
            "packet_hash": "f" * 64,
        },
    )


def test_missing_p83_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P83_STATUS_REPAIR_PLAN_REGENERATION"


def test_malformed_p83_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P83_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad json", encoding="utf-8")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P83_STATUS_REPAIR_PLAN_REGENERATION"


def test_p83_blocked_states_block_p84_and_recommend_p83_regeneration(tmp_path: Path) -> None:
    _seed_p83(tmp_path, status="P79_STATUS_REPAIR_BLOCKED_BY_P82")
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_plan_status"] == "P80_REGENERATION_PLAN_BLOCKED"
    assert packet["recommended_next_lane"] == "P83_STATUS_REPAIR_PLAN_REGENERATION"


def test_p83_recommended_next_lane_not_p80_regeneration_returns_not_required(
    tmp_path: Path,
) -> None:
    _seed_p83(tmp_path, recommended_next_lane="P84_DIFFERENT_LANE")
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_plan_status"] == "P80_REGENERATION_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P83_RECOMMENDED_NEXT_LANE_PASSTHROUGH"


def test_p79_source_missing_blocks_p84_and_recommends_p85_p79_regeneration_plan(
    tmp_path: Path,
) -> None:
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_plan_status"] == "P80_REGENERATION_PLAN_BLOCKED"
    assert (
        packet["recommended_next_lane"]
        == "P85_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN"
    )


def test_p79_source_malformed_blocks_p84(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    target = tmp_path / P79_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad json", encoding="utf-8")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_plan_status"] == "P80_REGENERATION_PLAN_BLOCKED"


def test_p79_status_not_computable_blocks_p84(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path, status="NOT_COMPUTABLE")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_plan_status"] == "P80_REGENERATION_PLAN_BLOCKED"


def test_p83_recommends_p80_regeneration_plus_p79_ready_returns_plan_ready(
    tmp_path: Path,
) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path, status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_plan_status"] == "P80_REGENERATION_PLAN_READY"
    assert packet["p80_regeneration_required"] is True
    assert packet["p80_regeneration_allowed"] is False


def test_p80_already_ready_returns_not_required(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path, status="AUTHORIZATION_ELIGIBLE")
    _seed_p80(tmp_path, status="AUTHORIZATION_RECORD_PLAN_READY")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_plan_status"] == "P80_REGENERATION_NOT_REQUIRED"
    assert (
        packet["recommended_next_lane"]
        == "P85_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_PLAN"
    )


def test_p80_regeneration_allowed_always_false(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p80_regeneration_allowed"] is False


def test_regeneration_execution_allowed_always_false(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert all(
        item["regeneration_execution_allowed"] is False
        for item in packet["regeneration_items"]
    )


def test_regeneration_authority_always_false(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["regeneration_authority"] is False


def test_artifact_regeneration_authority_always_false(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["artifact_regeneration_authority"] is False


def test_future_runner_command_exact_allowed_command_when_ready(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path, status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert (
        packet["future_runner_command"]
        == "python scripts/temporal/run_temporal_continuity_upstream_input_regeneration_authorization_record_plan.py"
    )


def test_future_runner_command_not_computable_when_blocked(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path, status="NOT_COMPUTABLE")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["future_runner_command"] == "NOT_COMPUTABLE"


def test_expected_output_path_correct(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert (
        packet["expected_output_path"]
        == "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"
    )


def test_validation_requirements_include_required_checks(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path, status="AUTHORIZATION_ELIGIBLE")
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    ids = [item["validation_id"] for item in packet["validation_requirements"]]
    assert ids == [
        "validation_001_p79_source_exists",
        "validation_002_p79_source_readable",
        "validation_003_p79_status_allowed",
        "validation_004_future_command_exact_match",
        "validation_005_expected_output_path_match",
        "validation_006_p80_exists_after_regeneration",
        "validation_007_p80_readable_after_regeneration",
        "validation_008_p80_status_computable_after_regeneration",
        "validation_009_authority_flags_false_after_regeneration",
    ]


def test_regeneration_items_deterministic(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path)
    first = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert first["regeneration_items"] == second["regeneration_items"]


def test_regeneration_reasons_deterministic(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path)
    first = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert first["regeneration_reasons"] == second["regeneration_reasons"]


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p83(
        tmp_path,
        degraded_evidence_inputs=["e2", "e1"],
    )
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p83(tmp_path, inherited_blockers=["b2", "b1"])
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p83(tmp_path, inherited_drift_flags=["d2", "d1"])
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p83(tmp_path, semantic_overlap_flags=["s2", "s1"])
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p80_authorization_record_plan_regeneration_plan.v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    for field in (
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "repair_execution_authority",
        "regeneration_authority",
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
    assert schema["properties"]["p80_regeneration_allowed"]["const"] is False
    assert (
        schema["properties"]["regeneration_items"]["items"]["properties"][
            "regeneration_execution_allowed"
        ]["const"]
        is False
    )


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path)
    first = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path)
    packet = build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p80_authorization_record_plan_regeneration_plan"
        / "latest.json"
    )
    write_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
        out_path,
        packet,
    )
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p83(tmp_path)
    _seed_p79(tmp_path)
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p80_authorization_record_plan_regeneration_plan"
        / "latest.json"
    )
    first = run_temporal_continuity_p80_authorization_record_plan_regeneration_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_p80_authorization_record_plan_regeneration_plan.run(
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

    artifact = (
        "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json"
    )
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
