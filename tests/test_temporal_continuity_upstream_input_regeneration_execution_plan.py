from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_upstream_input_regeneration_execution_plan import (
    build_temporal_continuity_upstream_input_regeneration_execution_plan,
    write_temporal_continuity_upstream_input_regeneration_execution_plan,
)
from scripts import run_temporal_continuity_upstream_input_regeneration_execution_plan


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _seed_script(root: Path, script_path: str) -> None:
    path = root / script_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("from __future__ import annotations\n", encoding="utf-8")


def _seed_p77(
    root: Path,
    *,
    dry_run_plan_status: str = "DRY_RUN_READY_WITH_MISSING_INPUTS",
    executable_future_candidates: list[str] | None = None,
    dry_run_commands: list[str] | None = None,
    dry_run_items: list[dict[str, object]] | None = None,
    degraded_evidence_inputs: list[str] | None = None,
    still_blocked_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    target = "out/projections/temporal_state_diff_001.latest.json"
    command = "python scripts/run_temporal_state_diff.py"
    item = {
        "target_input_path": target,
        "owning_output_path": "out/projections/temporal_resonance_coherence_001.latest.json",
        "group_id": "temporal_coherence_chain",
        "source_category": "projection",
        "prerequisite_role": "temporal_diff_input",
        "restoration_strategy": "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
        "generator_script": "scripts/run_temporal_state_diff.py",
        "generator_observed": True,
        "generator_readable": True,
        "proposed_command": command,
        "expected_output_path": target,
        "blocked_by_paths": [target],
        "future_execution_candidate": True,
        "blocking_reason": "FUTURE_EXECUTION_LANE_REQUIRED_P77_DRY_RUN_ONLY",
        "safe_to_execute": False,
    }
    _write_json(
        root / "out" / "temporal_continuity_upstream_input_regeneration_dry_run_plan" / "latest.json",
        {
            "artifact_type": "TemporalContinuityUpstreamInputRegenerationDryRunPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "dry_run_only": True,
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
            "spine_implementation_authority": False,
            "source_upstream_restoration_plan_path": "out/temporal_continuity_upstream_input_restoration_plan/latest.json",
            "source_upstream_restoration_plan_observed": True,
            "source_upstream_restoration_plan_hash": "1" * 64,
            "source_upstream_restoration_plan_status": "UPSTREAM_INPUTS_MISSING",
            "source_recommended_next_lane": "P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_EXECUTION_PLAN",
            "dry_run_plan_status": dry_run_plan_status,
            "dry_run_items": dry_run_items if dry_run_items is not None else [item],
            "dry_run_commands": dry_run_commands if dry_run_commands is not None else [command],
            "missing_upstream_input_paths": [target],
            "observed_generator_scripts": ["scripts/run_temporal_state_diff.py"],
            "missing_generator_scripts": [],
            "outputs_blocked_by_upstream_inputs": [],
            "still_blocked_inputs": still_blocked_inputs if still_blocked_inputs is not None else [target],
            "executable_future_candidates": (
                executable_future_candidates
                if executable_future_candidates is not None
                else [target]
            ),
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
            "dry_run_strategy_summary": {
                "UPSTREAM_GENERATOR_DISCOVERY_REQUIRED": 0,
                "UPSTREAM_GENERATOR_IMPLEMENTATION_PLAN": 0,
                "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN": 1,
                "UPSTREAM_INPUT_REPAIR_PLAN": 0,
                "UPSTREAM_INPUT_NOT_REQUIRED": 0,
                "NOT_COMPUTABLE": 0,
            },
            "recommended_next_lane": "P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_EXECUTION_PLAN",
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "2" * 64,
        },
    )


def test_missing_p77_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["execution_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P77_DRY_RUN_PLAN_REGENERATION"


def test_malformed_p77_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / "out" / "temporal_continuity_upstream_input_regeneration_dry_run_plan" / "latest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["execution_plan_status"] == "NOT_COMPUTABLE"


def test_ready_with_candidates_maps_to_authorization_gate(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(tmp_path)
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["execution_plan_status"] == "EXECUTION_PLAN_READY"
    assert packet["recommended_next_lane"] == "P79_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_GATE"


def test_blocked_generator_status_maps_to_generator_discovery_lane(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(tmp_path, dry_run_plan_status="DRY_RUN_BLOCKED_GENERATORS_MISSING")
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["execution_plan_status"] == "EXECUTION_PLAN_BLOCKED"
    assert packet["recommended_next_lane"] == "P79_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN"


def test_blocked_inputs_status_maps_to_input_repair_lane(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(tmp_path, dry_run_plan_status="DRY_RUN_BLOCKED_INPUTS_UNREADABLE")
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["execution_plan_status"] == "EXECUTION_PLAN_BLOCKED"
    assert packet["recommended_next_lane"] == "P79_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REPAIR_PLAN"


def test_dry_run_ready_maps_to_execution_plan_not_required(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(tmp_path, dry_run_plan_status="DRY_RUN_READY")
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["execution_plan_status"] == "EXECUTION_PLAN_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P79_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN"


def test_dry_run_not_required_with_degraded_evidence_maps_to_repair_plan(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(
        tmp_path,
        dry_run_plan_status="DRY_RUN_NOT_REQUIRED",
        degraded_evidence_inputs=["degraded:marker"],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["execution_plan_status"] == "EXECUTION_PLAN_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P79_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"


def test_dry_run_not_required_without_degraded_evidence_maps_to_spine_gate(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(
        tmp_path,
        dry_run_plan_status="DRY_RUN_NOT_REQUIRED",
        degraded_evidence_inputs=[],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["execution_plan_status"] == "EXECUTION_PLAN_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P79_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE"


def test_allowlist_is_true_only_when_all_rules_pass(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(tmp_path)
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    allowlist_item = packet["command_allowlist"][0]
    step = packet["execution_steps"][0]
    assert allowlist_item["allowlisted_for_future_execution"] is True
    assert allowlist_item["execution_authorized"] is False
    assert step["execution_authorized"] is False


def test_nonmatching_command_shape_is_not_allowlisted(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    bad_item = {
        "target_input_path": "out/projections/temporal_state_diff_001.latest.json",
        "owning_output_path": "out/projections/temporal_resonance_coherence_001.latest.json",
        "group_id": "temporal_coherence_chain",
        "source_category": "projection",
        "prerequisite_role": "temporal_diff_input",
        "restoration_strategy": "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
        "generator_script": "scripts/run_temporal_state_diff.py",
        "generator_observed": True,
        "generator_readable": True,
        "proposed_command": "python scripts/run_temporal_state_diff.py && echo x",
        "expected_output_path": "out/projections/temporal_state_diff_001.latest.json",
        "blocked_by_paths": [],
        "future_execution_candidate": True,
        "blocking_reason": "seed",
        "safe_to_execute": False,
    }
    _seed_p77(
        tmp_path,
        dry_run_commands=["python scripts/run_temporal_state_diff.py && echo x"],
        dry_run_items=[bad_item],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["command_allowlist"][0]["allowlisted_for_future_execution"] is False


def test_inherited_fields_preserved_exactly(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(
        tmp_path,
        inherited_blockers=["b2", "b1"],
        inherited_drift_flags=["d2", "d1"],
        semantic_overlap_flags=["s2", "s1"],
        degraded_evidence_inputs=["g2", "g1"],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["inherited_blockers"] == ["b2", "b1"]
    assert packet["inherited_drift_flags"] == ["d2", "d1"]
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]
    assert packet["degraded_evidence_inputs"] == ["g2", "g1"]


def test_authority_fields_are_false_and_execution_plan_only_true(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(tmp_path)
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert packet["execution_plan_only"] is True
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
        "spine_implementation_authority",
    ):
        assert packet[field] is False


def test_schema_locks_execution_authorized_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_upstream_input_regeneration_execution_plan.v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    step_exec = schema["properties"]["execution_steps"]["items"]["properties"]["execution_authorized"]
    allow_exec = schema["properties"]["command_allowlist"]["items"]["properties"]["execution_authorized"]
    assert step_exec.get("const") is False
    assert allow_exec.get("const") is False


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(tmp_path)
    first = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    second = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(tmp_path)
    packet = build_temporal_continuity_upstream_input_regeneration_execution_plan(repo_root=tmp_path)
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_execution_plan"
        / "latest.json"
    )
    write_temporal_continuity_upstream_input_regeneration_execution_plan(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_script(tmp_path, "scripts/run_temporal_state_diff.py")
    _seed_p77(tmp_path)
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_execution_plan"
        / "latest.json"
    )
    first = run_temporal_continuity_upstream_input_regeneration_execution_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_upstream_input_regeneration_execution_plan.run(
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

    artifact = "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
