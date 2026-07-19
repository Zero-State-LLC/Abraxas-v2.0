from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_upstream_input_restoration_plan import (
    build_temporal_continuity_upstream_input_restoration_plan,
    write_temporal_continuity_upstream_input_restoration_plan,
)
from scripts.temporal import run_temporal_continuity_upstream_input_restoration_plan


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _seed_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_p75(
    root: Path,
    *,
    generator_items: list[dict[str, object]] | None = None,
    missing_prerequisite_paths: list[str] | None = None,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    default_prereq = "out/projections/temporal_state_diff_001.latest.json"
    default_items: list[dict[str, object]] = [
        {
            "output_path": "out/projections/temporal_resonance_coherence_001.latest.json",
            "group_id": "temporal_coherence_chain",
            "source_category": "projection",
            "evidence_role": "missing_path",
            "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
            "likely_generator_script": "scripts/temporal/run_temporal_resonance_coherence.py",
            "generator_observed": True,
            "generator_readable": True,
            "generator_callable_hint": True,
            "generator_binding_status": "GENERATOR_OBSERVED",
            "prerequisite_paths": [default_prereq],
            "missing_prerequisite_paths": [default_prereq],
            "blocking_reason": "test seed",
            "safe_to_execute": False,
        }
    ]

    _write_json(
        root / "out" / "temporal_continuity_generator_discovery_plan" / "latest.json",
        {
            "artifact_type": "TemporalContinuityGeneratorDiscoveryPlan.v1",
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
            "spine_implementation_authority": False,
            "source_restoration_plan_path": "out/temporal_continuity_missing_evidence_restoration_plan/latest.json",
            "source_restoration_plan_observed": True,
            "source_restoration_plan_hash": "1" * 64,
            "source_restoration_plan_status": "RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE",
            "source_recommended_next_lane": "P75_TEMPORAL_CONTINUITY_GENERATOR_DISCOVERY_PLAN",
            "generator_discovery_status": "GENERATORS_OBSERVED_WITH_MISSING_PREREQUISITES",
            "generator_items": generator_items if generator_items is not None else default_items,
            "missing_generator_scripts": [],
            "observed_generator_scripts": ["scripts/temporal/run_temporal_resonance_coherence.py"],
            "unreadable_generator_scripts": [],
            "ambiguous_generator_bindings": [],
            "missing_prerequisite_paths": (
                missing_prerequisite_paths if missing_prerequisite_paths is not None else [default_prereq]
            ),
            "degraded_evidence_inputs": (
                degraded_evidence_inputs
                if degraded_evidence_inputs is not None
                else ["archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"]
            ),
            "inherited_blockers": (
                inherited_blockers
                if inherited_blockers is not None
                else ["temporal_coherence_chain:missing:out/projections/temporal_state_diff_001.latest.json"]
            ),
            "inherited_drift_flags": (
                inherited_drift_flags
                if inherited_drift_flags is not None
                else ["GROUP_TEMPORAL_COHERENCE_CHAIN_PARTIAL"]
            ),
            "semantic_overlap_flags": (
                semantic_overlap_flags
                if semantic_overlap_flags is not None
                else [
                    "SEMANTIC_OVERLAP_LATEST_JSON:out/projections/temporal_state_diff_001.latest.json"
                ]
            ),
            "generator_strategy_summary": {
                "GENERATOR_OBSERVED": 1,
                "GENERATOR_MISSING": 0,
                "GENERATOR_UNREADABLE": 0,
                "GENERATOR_NOT_COMPUTABLE": 0,
                "GENERATOR_AMBIGUOUS": 0,
            },
            "recommended_next_lane": "P76_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN",
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "2" * 64,
        },
    )


def _single_item(*, output_path: str = "out/projections/target.latest.json", prereq: str) -> list[dict[str, object]]:
    return [
        {
            "output_path": output_path,
            "group_id": "g",
            "source_category": "projection",
            "evidence_role": "missing_path",
            "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
            "likely_generator_script": "scripts/run_target.py",
            "generator_observed": True,
            "generator_readable": True,
            "generator_callable_hint": True,
            "generator_binding_status": "GENERATOR_OBSERVED",
            "prerequisite_paths": [prereq],
            "missing_prerequisite_paths": [prereq],
            "blocking_reason": "test seed",
            "safe_to_execute": False,
        }
    ]


# 1. Missing P75 source returns NOT_COMPUTABLE

def test_missing_p75_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["upstream_restoration_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P75_GENERATOR_DISCOVERY_PLAN_REGENERATION"


# 2. Malformed P75 source returns NOT_COMPUTABLE

def test_malformed_p75_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / "out" / "temporal_continuity_generator_discovery_plan" / "latest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["upstream_restoration_plan_status"] == "NOT_COMPUTABLE"


# 3. No missing_prerequisite_paths returns UPSTREAM_RESTORATION_NOT_REQUIRED

def test_no_missing_prerequisite_paths_returns_not_required(tmp_path: Path) -> None:
    prereq = "out/audit/ready_001.latest.json"
    _seed_file(tmp_path / prereq, '{"ok":true}\n')
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["upstream_restoration_plan_status"] == "UPSTREAM_RESTORATION_NOT_REQUIRED"


# 4. Missing prerequisites become upstream_input_items

def test_missing_prerequisites_become_upstream_input_items(tmp_path: Path) -> None:
    prereq = "out/projections/missing_input_001.latest.json"
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert any(item["path"] == prereq for item in packet["upstream_input_items"])


# 5. Existing/readable prerequisite input is observed/readable with hash

def test_existing_readable_prerequisite_has_hash(tmp_path: Path) -> None:
    prereq = "out/projections/input_001.latest.json"
    _seed_file(tmp_path / prereq, '{"ok":true}\n')
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    item = next(it for it in packet["upstream_input_items"] if it["path"] == prereq)
    assert item["input_observed"] is True
    assert item["input_readable"] is True
    assert item["input_hash"] != "NOT_COMPUTABLE"


# 6. Malformed JSON prerequisite is unreadable/malformed

def test_malformed_json_prerequisite_marked_unreadable(tmp_path: Path) -> None:
    prereq = "out/projections/bad_input_001.latest.json"
    _seed_file(tmp_path / prereq, "{bad")
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    item = next(it for it in packet["upstream_input_items"] if it["path"] == prereq)
    assert item["input_observed"] is True
    assert item["input_readable"] is False
    assert item["malformed_json"] is True


# 7. Missing prerequisite with no inferred generator becomes UPSTREAM_GENERATORS_MISSING

def test_missing_prerequisite_without_inference_is_generators_missing(tmp_path: Path) -> None:
    prereq = "out/projections/no_generator_001.latest.json"
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["upstream_restoration_plan_status"] == "UPSTREAM_GENERATORS_MISSING"


# 8. Missing prerequisite with observed generator becomes UPSTREAM_INPUTS_MISSING

def test_missing_prerequisite_with_observed_generator_is_inputs_missing(tmp_path: Path) -> None:
    prereq = "out/projections/temporal_state_diff_001.latest.json"
    _seed_file(tmp_path / "scripts" / "temporal" / "run_temporal_state_diff.py", "def main():\n    pass\n")
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["upstream_restoration_plan_status"] == "UPSTREAM_INPUTS_MISSING"


# 9. Unreadable prerequisite returns UPSTREAM_INPUTS_UNREADABLE

def test_unreadable_prerequisite_returns_inputs_unreadable(tmp_path: Path) -> None:
    prereq = "out/projections/unreadable_001.latest.json"
    _seed_file(tmp_path / prereq, "{bad")
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["upstream_restoration_plan_status"] == "UPSTREAM_INPUTS_UNREADABLE"


# 10. All prerequisites observed/readable returns UPSTREAM_INPUTS_READY

def test_all_prerequisites_observed_readable_returns_ready(tmp_path: Path) -> None:
    prereq = "out/audit/input_001.latest.json"
    _seed_file(tmp_path / prereq, '{"ok":true}\n')
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["upstream_restoration_plan_status"] == "UPSTREAM_INPUTS_READY"


# 11. likely_upstream_generator_script inference uses only existing script paths

def test_generator_inference_uses_only_existing_scripts(tmp_path: Path) -> None:
    prereq_a = "out/projections/temporal_state_diff_001.latest.json"
    prereq_b = "out/projections/cross_run_topology_fusion_001.latest.json"
    _seed_file(tmp_path / "scripts" / "temporal" / "run_temporal_state_diff.py", "def main():\n    pass\n")
    _seed_p75(
        tmp_path,
        generator_items=[
            *_single_item(prereq=prereq_a),
            *_single_item(output_path="out/projections/other.latest.json", prereq=prereq_b),
        ],
        missing_prerequisite_paths=[prereq_a, prereq_b],
    )
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    inferred = {it["path"]: it["likely_upstream_generator_script"] for it in packet["upstream_input_items"]}
    assert inferred[prereq_a] == "scripts/temporal/run_temporal_state_diff.py"
    assert inferred[prereq_b] == "NOT_COMPUTABLE"


# 12. safe_to_restore is always false

def test_safe_to_restore_always_false(tmp_path: Path) -> None:
    _seed_p75(tmp_path)
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert all(item["safe_to_restore"] is False for item in packet["upstream_input_items"])


# 13. degraded_evidence_inputs are preserved exactly

def test_degraded_evidence_inputs_preserved_exactly(tmp_path: Path) -> None:
    marker = "archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"
    _seed_p75(tmp_path, degraded_evidence_inputs=[marker])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["degraded_evidence_inputs"] == [marker]


# 14. inherited_blockers are preserved exactly

def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    marker = "temporal_coherence_chain:missing:out/projections/x.latest.json"
    _seed_p75(tmp_path, inherited_blockers=[marker])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["inherited_blockers"] == [marker]


# 15. inherited_drift_flags are preserved exactly

def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    marker = "GROUP_TEMPORAL_COHERENCE_CHAIN_PARTIAL"
    _seed_p75(tmp_path, inherited_drift_flags=[marker])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["inherited_drift_flags"] == [marker]


# 16. semantic_overlap_flags are preserved exactly

def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    marker = "SEMANTIC_OVERLAP_LATEST_JSON:out/projections/x.latest.json"
    _seed_p75(tmp_path, semantic_overlap_flags=[marker])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["semantic_overlap_flags"] == [marker]


# 17. outputs_blocked_by_upstream_inputs is deterministic

def test_outputs_blocked_by_upstream_inputs_is_deterministic(tmp_path: Path) -> None:
    prereq = "out/projections/blocked_001.latest.json"
    _seed_p75(
        tmp_path,
        generator_items=[
            *_single_item(output_path="out/projections/b.latest.json", prereq=prereq),
            *_single_item(output_path="out/projections/a.latest.json", prereq=prereq),
        ],
        missing_prerequisite_paths=[prereq],
    )
    first = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    second = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert first["outputs_blocked_by_upstream_inputs"] == second["outputs_blocked_by_upstream_inputs"]


# 18. upstream_input_items are sorted deterministically

def test_upstream_input_items_sorted_deterministically(tmp_path: Path) -> None:
    prereq_a = "out/projections/a_001.latest.json"
    prereq_b = "out/projections/b_001.latest.json"
    _seed_p75(
        tmp_path,
        generator_items=[
            *_single_item(output_path="out/projections/z.latest.json", prereq=prereq_b),
            *_single_item(output_path="out/projections/y.latest.json", prereq=prereq_a),
        ],
        missing_prerequisite_paths=[prereq_b, prereq_a],
    )
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    ordering = [(it["path"], it["owning_output_path"], it["group_id"]) for it in packet["upstream_input_items"]]
    assert ordering == sorted(ordering)


# 19. upstream_strategy_summary is deterministic

def test_upstream_strategy_summary_is_deterministic(tmp_path: Path) -> None:
    _seed_p75(tmp_path)
    first = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    second = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert first["upstream_strategy_summary"] == second["upstream_strategy_summary"]


# 20. UPSTREAM_GENERATORS_MISSING recommends upstream generator discovery plan

def test_generators_missing_recommends_upstream_generator_discovery_plan(tmp_path: Path) -> None:
    prereq = "out/projections/missing_001.latest.json"
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P77_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN"


# 21. UPSTREAM_INPUTS_UNREADABLE recommends upstream input repair plan

def test_inputs_unreadable_recommends_upstream_input_repair_plan(tmp_path: Path) -> None:
    prereq = "out/projections/bad_001.latest.json"
    _seed_file(tmp_path / prereq, "{bad")
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P77_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REPAIR_PLAN"


# 22. UPSTREAM_INPUTS_MISSING recommends upstream input regeneration dry-run plan

def test_inputs_missing_recommends_upstream_input_regeneration_dry_run_plan(tmp_path: Path) -> None:
    prereq = "out/projections/temporal_state_diff_001.latest.json"
    _seed_file(tmp_path / "scripts" / "temporal" / "run_temporal_state_diff.py", "def main():\n    pass\n")
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert (
        packet["recommended_next_lane"]
        == "P77_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN"
    )


# 23. UPSTREAM_INPUTS_READY recommends artifact regeneration dry-run plan

def test_inputs_ready_recommends_artifact_regeneration_dry_run_plan(tmp_path: Path) -> None:
    prereq = "out/projections/ready_001.latest.json"
    _seed_file(tmp_path / prereq, '{"ok":true}\n')
    _seed_p75(tmp_path, generator_items=_single_item(prereq=prereq), missing_prerequisite_paths=[prereq])
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P77_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN"


# 24. UPSTREAM_RESTORATION_NOT_REQUIRED with degraded evidence recommends degraded evidence repair plan

def test_not_required_with_degraded_recommends_degraded_repair_plan(tmp_path: Path) -> None:
    prereq = "out/audit/ready_001.latest.json"
    _seed_file(tmp_path / prereq, '{"ok":true}\n')
    _seed_p75(
        tmp_path,
        generator_items=_single_item(prereq=prereq),
        missing_prerequisite_paths=[],
        degraded_evidence_inputs=["degraded:marker"],
    )
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P77_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"


# 25. UPSTREAM_RESTORATION_NOT_REQUIRED without degraded evidence recommends spine implementation planning gate

def test_not_required_without_degraded_recommends_spine_gate(tmp_path: Path) -> None:
    prereq = "out/audit/ready_001.latest.json"
    _seed_file(tmp_path / prereq, '{"ok":true}\n')
    _seed_p75(
        tmp_path,
        generator_items=_single_item(prereq=prereq),
        missing_prerequisite_paths=[],
        degraded_evidence_inputs=[],
    )
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P77_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE"


# 26. Authority fields are schema-locked / escalation denied

def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path(
            "contracts/canon/temporal_continuity_upstream_input_restoration_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
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
        "spine_implementation_authority",
    ):
        assert schema["properties"][field]["const"] is False


def test_runtime_authority_fields_false(tmp_path: Path) -> None:
    _seed_p75(tmp_path)
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
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
        "spine_implementation_authority",
    ):
        assert packet[field] is False


# 27. Packet hash is deterministic

def test_packet_hash_is_deterministic(tmp_path: Path) -> None:
    _seed_p75(tmp_path)
    first = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    second = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]


# 28. Writer emits canonical JSON with final newline

def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p75(tmp_path)
    packet = build_temporal_continuity_upstream_input_restoration_plan(repo_root=tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_upstream_input_restoration_plan" / "latest.json"
    write_temporal_continuity_upstream_input_restoration_plan(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


# 29. Runner writes expected output path

def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p75(tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_upstream_input_restoration_plan" / "latest.json"
    first = run_temporal_continuity_upstream_input_restoration_plan.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_upstream_input_restoration_plan.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


# 30. Artifact registry classifies output as DERIVED_OPTIONAL and not CI drift enforced

def test_artifact_registry_classifies_output_as_derived_optional() -> None:
    from core.generated_artifact_registry import (  # type: ignore[attr-defined]
        _DERIVED_OPTIONAL_ARTIFACTS,
        build_generated_artifact_registry,
        list_ci_drift_artifact_paths,
    )

    artifact = "out/temporal_continuity_upstream_input_restoration_plan/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
