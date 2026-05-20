from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_upstream_input_regeneration_dry_run_plan import (
    build_temporal_continuity_upstream_input_regeneration_dry_run_plan,
    write_temporal_continuity_upstream_input_regeneration_dry_run_plan,
)
from scripts import run_temporal_continuity_upstream_input_regeneration_dry_run_plan


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _seed_p76(
    root: Path,
    *,
    status: str = "UPSTREAM_INPUTS_MISSING",
    source_recommended_next_lane: str = "P77_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
    missing_upstream_input_paths: list[str] | None = None,
    upstream_input_items: list[dict[str, object]] | None = None,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    default_input = "out/projections/temporal_state_diff_001.latest.json"
    default_item: dict[str, object] = {
        "path": default_input,
        "owning_output_path": "out/projections/temporal_resonance_coherence_001.latest.json",
        "group_id": "temporal_coherence_chain",
        "source_category": "projection",
        "prerequisite_role": "temporal_diff_input",
        "input_observed": False,
        "input_readable": False,
        "malformed_json": False,
        "input_hash": "NOT_COMPUTABLE",
        "likely_upstream_generator_script": "scripts/run_temporal_state_diff.py",
        "upstream_generator_observed": True,
        "upstream_generator_readable": True,
        "restoration_strategy": "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
        "blocking_reason": "UPSTREAM_INPUT_MISSING_GENERATOR_OBSERVED_P76_PLANNING_ONLY",
        "safe_to_restore": False,
    }

    _write_json(
        root / "out" / "temporal_continuity_upstream_input_restoration_plan" / "latest.json",
        {
            "artifact_type": "TemporalContinuityUpstreamInputRestorationPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
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
            "spine_implementation_authority": False,
            "source_generator_discovery_path": "out/temporal_continuity_generator_discovery_plan/latest.json",
            "source_generator_discovery_observed": True,
            "source_generator_discovery_hash": "1" * 64,
            "source_generator_discovery_status": "GENERATORS_OBSERVED_WITH_MISSING_PREREQUISITES",
            "source_recommended_next_lane": "P76_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN",
            "upstream_restoration_plan_status": status,
            "upstream_input_items": upstream_input_items if upstream_input_items is not None else [default_item],
            "missing_upstream_input_paths": (
                missing_upstream_input_paths
                if missing_upstream_input_paths is not None
                else [default_input]
            ),
            "observed_upstream_input_paths": [],
            "unreadable_upstream_input_paths": [],
            "outputs_blocked_by_upstream_inputs": [
                {
                    "path": default_input,
                    "blocked_output_paths": [
                        "out/projections/temporal_resonance_coherence_001.latest.json"
                    ],
                }
            ],
            "missing_upstream_generator_scripts": [],
            "observed_upstream_generator_scripts": ["scripts/run_temporal_state_diff.py"],
            "degraded_evidence_inputs": degraded_evidence_inputs
            if degraded_evidence_inputs is not None
            else ["archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"],
            "inherited_blockers": inherited_blockers
            if inherited_blockers is not None
            else ["temporal_coherence_chain:missing:out/projections/temporal_state_diff_001.latest.json"],
            "inherited_drift_flags": inherited_drift_flags
            if inherited_drift_flags is not None
            else ["GROUP_TEMPORAL_COHERENCE_CHAIN_PARTIAL"],
            "semantic_overlap_flags": semantic_overlap_flags
            if semantic_overlap_flags is not None
            else [
                "SEMANTIC_OVERLAP_LATEST_JSON:out/projections/temporal_state_diff_001.latest.json"
            ],
            "upstream_strategy_summary": {
                "UPSTREAM_GENERATOR_DISCOVERY_REQUIRED": 0,
                "UPSTREAM_GENERATOR_IMPLEMENTATION_PLAN": 0,
                "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN": 1,
                "UPSTREAM_INPUT_REPAIR_PLAN": 0,
                "UPSTREAM_INPUT_NOT_REQUIRED": 0,
                "NOT_COMPUTABLE": 0,
            },
            "recommended_next_lane": source_recommended_next_lane,
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "2" * 64,
        },
    )


def test_missing_p76_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P76_UPSTREAM_INPUT_RESTORATION_PLAN_REGENERATION"


def test_malformed_p76_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / "out" / "temporal_continuity_upstream_input_restoration_plan" / "latest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_plan_status"] == "NOT_COMPUTABLE"


def test_upstream_generators_missing_maps_to_blocked_generators_lane(tmp_path: Path) -> None:
    _seed_p76(tmp_path, status="UPSTREAM_GENERATORS_MISSING")
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_plan_status"] == "DRY_RUN_BLOCKED_GENERATORS_MISSING"
    assert packet["recommended_next_lane"] == "P78_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN"


def test_upstream_inputs_unreadable_maps_to_input_repair_lane(tmp_path: Path) -> None:
    _seed_p76(tmp_path, status="UPSTREAM_INPUTS_UNREADABLE")
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_plan_status"] == "DRY_RUN_BLOCKED_INPUTS_UNREADABLE"
    assert packet["recommended_next_lane"] == "P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REPAIR_PLAN"


def test_upstream_restoration_not_required_with_degraded_evidence(tmp_path: Path) -> None:
    _seed_p76(
        tmp_path,
        status="UPSTREAM_RESTORATION_NOT_REQUIRED",
        missing_upstream_input_paths=[],
        degraded_evidence_inputs=["degraded:marker"],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_plan_status"] == "DRY_RUN_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P78_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"


def test_upstream_restoration_not_required_without_degraded_evidence(tmp_path: Path) -> None:
    _seed_p76(
        tmp_path,
        status="UPSTREAM_RESTORATION_NOT_REQUIRED",
        missing_upstream_input_paths=[],
        degraded_evidence_inputs=[],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_plan_status"] == "DRY_RUN_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P78_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE"


def test_upstream_inputs_ready_maps_to_artifact_regen_dry_run_lane(tmp_path: Path) -> None:
    _seed_p76(tmp_path, status="UPSTREAM_INPUTS_READY")
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_plan_status"] == "DRY_RUN_READY"
    assert packet["recommended_next_lane"] == "P78_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN"


def test_upstream_inputs_missing_with_observed_readable_generators_is_ready(tmp_path: Path) -> None:
    _seed_p76(tmp_path, status="UPSTREAM_INPUTS_MISSING")
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_plan_status"] == "DRY_RUN_READY_WITH_MISSING_INPUTS"
    assert packet["recommended_next_lane"] == "P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_EXECUTION_PLAN"


def test_upstream_inputs_missing_with_unreadable_generator_is_blocked(tmp_path: Path) -> None:
    bad_item = {
        "path": "out/projections/temporal_state_diff_001.latest.json",
        "owning_output_path": "out/projections/temporal_resonance_coherence_001.latest.json",
        "group_id": "temporal_coherence_chain",
        "source_category": "projection",
        "prerequisite_role": "temporal_diff_input",
        "input_observed": False,
        "input_readable": False,
        "malformed_json": False,
        "input_hash": "NOT_COMPUTABLE",
        "likely_upstream_generator_script": "scripts/run_temporal_state_diff.py",
        "upstream_generator_observed": True,
        "upstream_generator_readable": False,
        "restoration_strategy": "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
        "blocking_reason": "UPSTREAM_INPUT_MISSING_GENERATOR_OBSERVED_P76_PLANNING_ONLY",
        "safe_to_restore": False,
    }
    _seed_p76(
        tmp_path,
        status="UPSTREAM_INPUTS_MISSING",
        upstream_input_items=[bad_item],
        missing_upstream_input_paths=["out/projections/temporal_state_diff_001.latest.json"],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_plan_status"] == "DRY_RUN_BLOCKED_GENERATORS_MISSING"


def test_dry_run_item_includes_expected_command_shape(tmp_path: Path) -> None:
    _seed_p76(tmp_path)
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    item = packet["dry_run_items"][0]
    assert item["proposed_command"] == "python scripts/run_temporal_state_diff.py"
    assert item["expected_output_path"] == item["target_input_path"]
    assert packet["dry_run_commands"] == ["python scripts/run_temporal_state_diff.py"]


def test_future_execution_candidate_true_still_forces_safe_to_execute_false(tmp_path: Path) -> None:
    _seed_p76(tmp_path, status="UPSTREAM_INPUTS_MISSING")
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    item = packet["dry_run_items"][0]
    assert item["future_execution_candidate"] is True
    assert item["safe_to_execute"] is False


def test_all_dry_run_items_force_safe_to_execute_false(tmp_path: Path) -> None:
    mixed_items = [
        {
            "path": "out/projections/a.latest.json",
            "owning_output_path": "out/projections/owner_a.latest.json",
            "group_id": "g-a",
            "source_category": "projection",
            "prerequisite_role": "temporal_state_input",
            "input_observed": False,
            "input_readable": False,
            "malformed_json": False,
            "input_hash": "NOT_COMPUTABLE",
            "likely_upstream_generator_script": "scripts/run_a.py",
            "upstream_generator_observed": True,
            "upstream_generator_readable": True,
            "restoration_strategy": "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
            "blocking_reason": "seed",
            "safe_to_restore": False,
        },
        {
            "path": "out/projections/b.latest.json",
            "owning_output_path": "out/projections/owner_b.latest.json",
            "group_id": "g-b",
            "source_category": "projection",
            "prerequisite_role": "temporal_diff_input",
            "input_observed": True,
            "input_readable": True,
            "malformed_json": False,
            "input_hash": "abc",
            "likely_upstream_generator_script": "NOT_COMPUTABLE",
            "upstream_generator_observed": False,
            "upstream_generator_readable": False,
            "restoration_strategy": "UPSTREAM_INPUT_NOT_REQUIRED",
            "blocking_reason": "seed",
            "safe_to_restore": False,
        },
    ]
    _seed_p76(
        tmp_path,
        status="UPSTREAM_INPUTS_MISSING",
        upstream_input_items=mixed_items,
        missing_upstream_input_paths=["out/projections/a.latest.json"],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_items"]
    assert all(item["safe_to_execute"] is False for item in packet["dry_run_items"])


def test_schema_rejects_safe_to_execute_true() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_upstream_input_regeneration_dry_run_plan.v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    safe_to_execute_def = (
        schema["properties"]["dry_run_items"]["items"]["properties"]["safe_to_execute"]
    )
    assert safe_to_execute_def.get("const") is False


def test_inherited_flags_and_blockers_are_preserved_exactly(tmp_path: Path) -> None:
    _seed_p76(
        tmp_path,
        inherited_blockers=["b2", "b1"],
        inherited_drift_flags=["d2", "d1"],
        semantic_overlap_flags=["s2", "s1"],
        degraded_evidence_inputs=["g2", "g1"],
    )
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["inherited_blockers"] == ["b2", "b1"]
    assert packet["inherited_drift_flags"] == ["d2", "d1"]
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]
    assert packet["degraded_evidence_inputs"] == ["g2", "g1"]


def test_authority_fields_are_false_and_dry_run_only_true(tmp_path: Path) -> None:
    _seed_p76(tmp_path)
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert packet["dry_run_only"] is True
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
        "spine_implementation_authority",
    ):
        assert packet[field] is False


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p76(tmp_path)
    first = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    second = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p76(tmp_path)
    packet = build_temporal_continuity_upstream_input_regeneration_dry_run_plan(repo_root=tmp_path)
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_dry_run_plan"
        / "latest.json"
    )
    write_temporal_continuity_upstream_input_regeneration_dry_run_plan(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p76(tmp_path)
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_upstream_input_regeneration_dry_run_plan"
        / "latest.json"
    )
    first = run_temporal_continuity_upstream_input_regeneration_dry_run_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_upstream_input_regeneration_dry_run_plan.run(
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

    artifact = "out/temporal_continuity_upstream_input_regeneration_dry_run_plan/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
