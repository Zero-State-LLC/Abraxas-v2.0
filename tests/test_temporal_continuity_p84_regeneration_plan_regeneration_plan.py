from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p84_regeneration_plan_regeneration_plan import (
    build_temporal_continuity_p84_regeneration_plan_regeneration_plan,
    write_temporal_continuity_p84_regeneration_plan_regeneration_plan,
)
from scripts.temporal import run_temporal_continuity_p84_regeneration_plan_regeneration_plan

P85_PATH = "out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json"
P84_PATH = "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json"
P83_PATH = "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
ALLOWED_COMMAND = (
    "python scripts/temporal/run_temporal_continuity_p80_authorization_record_plan_regeneration_plan.py"
)
EXPECTED_OUTPUT_PATH = (
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p85(
    root: Path,
    *,
    status: str = "P80_REGENERATION_EXECUTION_PLAN_BLOCKED",
    recommended_next_lane: str = "P84_REGENERATION_PLAN_REGENERATION",
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    _write_json(
        root / P85_PATH,
        {
            "artifact_type": "TemporalContinuityP80AuthorizationRecordPlanRegenerationExecutionPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "execution_plan_only": True,
            "regeneration_execution_plan_only": True,
            "production_activation": False,
            "canon_promotion": False,
            "forecast_influence": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "repair_authority": False,
            "repair_execution_authority": False,
            "regeneration_authority": False,
            "regeneration_execution_authority": False,
            "evidence_generation_authority": False,
            "restoration_execution_authority": False,
            "generator_execution_authority": False,
            "upstream_input_generation_authority": False,
            "artifact_regeneration_authority": False,
            "execution_authority": False,
            "authorization_authority": False,
            "authorization_record_creation_authority": False,
            "spine_implementation_authority": False,
            "source_p84_regeneration_plan_path": P84_PATH,
            "source_p84_regeneration_plan_observed": True,
            "source_p84_regeneration_plan_readable": True,
            "source_p84_regeneration_plan_hash": "a" * 64,
            "source_p84_regeneration_plan_status": "NOT_COMPUTABLE",
            "source_p84_recommended_next_lane": "P83_STATUS_REPAIR_PLAN_REGENERATION",
            "p80_regeneration_execution_plan_status": status,
            "p80_regeneration_execution_required": False,
            "p80_regeneration_execution_allowed": False,
            "execution_steps": [],
            "command_allowlist": [],
            "expected_outputs": [],
            "preflight_checks": [],
            "post_run_validations": [],
            "blocked_execution_reasons": [],
            "future_runner_command": "NOT_COMPUTABLE",
            "expected_output_path": "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json",
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
            "execution_strategy_summary": {},
            "recommended_next_lane": recommended_next_lane,
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "f" * 64,
        },
    )


def _seed_p84(root: Path, *, status: str = "NOT_COMPUTABLE") -> None:
    _write_json(
        root / P84_PATH,
        {
            "artifact_type": "TemporalContinuityP80AuthorizationRecordPlanRegenerationPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "regeneration_plan_only": True,
            "production_activation": False,
            "canon_promotion": False,
            "forecast_influence": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "repair_authority": False,
            "repair_execution_authority": False,
            "regeneration_authority": False,
            "evidence_generation_authority": False,
            "restoration_execution_authority": False,
            "generator_execution_authority": False,
            "upstream_input_generation_authority": False,
            "artifact_regeneration_authority": False,
            "execution_authority": False,
            "authorization_authority": False,
            "authorization_record_creation_authority": False,
            "spine_implementation_authority": False,
            "source_p83_status_plan_path": P83_PATH,
            "source_p83_status_plan_observed": True,
            "source_p83_status_plan_readable": True,
            "source_p83_status_plan_hash": "b" * 64,
            "source_p83_status_plan_status": "P79_STATUS_REPAIR_NOT_REQUIRED",
            "source_p83_recommended_next_lane": "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "source_p79_gate_path": "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json",
            "source_p79_gate_observed": True,
            "source_p79_gate_readable": True,
            "source_p79_gate_hash": "c" * 64,
            "source_p79_gate_status": "NOT_COMPUTABLE",
            "source_p80_record_plan_path": "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json",
            "source_p80_record_plan_observed": False,
            "source_p80_record_plan_readable": False,
            "source_p80_record_plan_hash": "NOT_COMPUTABLE",
            "source_p80_record_plan_status": "NOT_COMPUTABLE",
            "p80_regeneration_plan_status": status,
            "p80_regeneration_required": status == "P80_REGENERATION_PLAN_READY",
            "p80_regeneration_allowed": False,
            "regeneration_reasons": [],
            "regeneration_items": [],
            "future_runner_command": "NOT_COMPUTABLE",
            "expected_output_path": EXPECTED_OUTPUT_PATH,
            "prerequisite_sources": [],
            "validation_requirements": [],
            "blocked_regeneration_reasons": [],
            "degraded_evidence_inputs": [],
            "inherited_blockers": [],
            "inherited_drift_flags": [],
            "semantic_overlap_flags": [],
            "regeneration_strategy_summary": {},
            "recommended_next_lane": "P85_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN",
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "d" * 64,
        },
    )


def _seed_p83(root: Path, *, status: str = "P79_STATUS_REPAIR_NOT_REQUIRED") -> None:
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
            "source_p82_repair_plan_hash": "e" * 64,
            "source_p82_repair_plan_status": "P79_REPAIR_NOT_REQUIRED",
            "source_p82_recommended_next_lane": "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "p79_status_repair_plan_status": status,
            "p79_source_path": "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json",
            "p79_source_status": "NOT_COMPUTABLE",
            "p79_failure_modes": [],
            "status_repair_items": [],
            "status_field_expectations": [],
            "corrected_status_relationship": {},
            "blocked_status_repair_reasons": [],
            "prerequisite_sources": [],
            "degraded_evidence_inputs": [],
            "inherited_blockers": [],
            "inherited_drift_flags": [],
            "semantic_overlap_flags": [],
            "status_repair_strategy_summary": {},
            "recommended_next_lane": "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "a" * 64,
        },
    )


def test_missing_p85_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p84_regeneration_plan_regeneration_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P85_EXECUTION_PLAN_REGENERATION"


def test_malformed_p85_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P85_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p84_regeneration_plan_regeneration_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P85_EXECUTION_PLAN_REGENERATION"


def test_p85_not_routing_to_p84_returns_not_required(tmp_path: Path) -> None:
    _seed_p85(tmp_path, recommended_next_lane="P86_DIFFERENT_ROUTE")
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p84_regeneration_plan_regeneration_status"] == "P84_REGENERATION_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P85_RECOMMENDED_NEXT_LANE_PASSTHROUGH"


def test_p83_missing_blocks_p86(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p84_regeneration_plan_regeneration_status"] == "P84_REGENERATION_PLAN_BLOCKED"
    assert (
        packet["recommended_next_lane"]
        == "P87_TEMPORAL_CONTINUITY_P83_STATUS_PLAN_REGENERATION_PLAN"
    )


def test_p83_malformed_blocks_p86(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    target = tmp_path / P83_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p84_regeneration_plan_regeneration_status"] == "P84_REGENERATION_PLAN_BLOCKED"


def test_p83_not_computable_blocks_p86(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path, status="NOT_COMPUTABLE")
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p84_regeneration_plan_regeneration_status"] == "P84_REGENERATION_PLAN_BLOCKED"


def test_p85_routes_to_p84_and_p83_computable_returns_ready(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path, status="P80_REGENERATION_PLAN_BLOCKED")
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p84_regeneration_plan_regeneration_status"] == "P84_REGENERATION_PLAN_READY"
    assert packet["p84_regeneration_required"] is True
    assert packet["p84_regeneration_allowed"] is False


def test_p84_already_ready_returns_not_required(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path, status="P80_REGENERATION_PLAN_READY")
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p84_regeneration_plan_regeneration_status"] == "P84_REGENERATION_NOT_REQUIRED"
    assert (
        packet["recommended_next_lane"]
        == "P87_TEMPORAL_CONTINUITY_P85_REGENERATION_EXECUTION_PLAN_REGENERATION_PLAN"
    )


def test_p84_regeneration_allowed_always_false(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["p84_regeneration_allowed"] is False


def test_regeneration_execution_allowed_always_false(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert all(
        item["regeneration_execution_allowed"] is False
        for item in packet["regeneration_items"]
    )


def test_regeneration_authority_always_false(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["regeneration_authority"] is False


def test_artifact_regeneration_authority_always_false(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["artifact_regeneration_authority"] is False


def test_future_runner_command_exact_when_ready(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["future_runner_command"] == ALLOWED_COMMAND


def test_future_runner_command_not_computable_when_blocked(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["future_runner_command"] == "NOT_COMPUTABLE"


def test_expected_output_path_exact(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["expected_output_path"] == EXPECTED_OUTPUT_PATH


def test_validation_requirements_include_required_checks(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    ids = [item["validation_id"] for item in packet["validation_requirements"]]
    assert ids == [
        "validation_001_p83_source_exists",
        "validation_002_p83_source_readable",
        "validation_003_p83_status_not_not_computable",
        "validation_004_future_command_exact_match",
        "validation_005_expected_output_path_exact_match",
        "validation_006_p84_exists_after_regeneration",
        "validation_007_p84_readable_after_regeneration",
        "validation_008_p84_status_not_not_computable_after_regeneration",
        "validation_009_all_authority_fields_false",
    ]


def test_regeneration_items_deterministic(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    first = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert first["regeneration_items"] == second["regeneration_items"]


def test_regeneration_reasons_deterministic(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    first = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert first["regeneration_reasons"] == second["regeneration_reasons"]


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p85(tmp_path, degraded_evidence_inputs=["e2", "e1"])
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p85(tmp_path, inherited_blockers=["b2", "b1"])
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p85(tmp_path, inherited_drift_flags=["d2", "d1"])
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p85(tmp_path, semantic_overlap_flags=["s2", "s1"])
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p84_regeneration_plan_regeneration_plan.v1.schema.json"
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
        "regeneration_execution_authority",
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
    assert schema["properties"]["p84_regeneration_allowed"]["const"] is False
    assert (
        schema["properties"]["regeneration_items"]["items"]["properties"][
            "regeneration_execution_allowed"
        ]["const"]
        is False
    )


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    first = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    packet = build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p84_regeneration_plan_regeneration_plan"
        / "latest.json"
    )
    write_temporal_continuity_p84_regeneration_plan_regeneration_plan(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p85(tmp_path)
    _seed_p84(tmp_path)
    _seed_p83(tmp_path)
    first = run_temporal_continuity_p84_regeneration_plan_regeneration_plan.run(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p84_regeneration_plan_regeneration_plan"
        / "latest.json"
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_p84_regeneration_plan_regeneration_plan.run(
        repo_root=tmp_path
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

    artifact = "out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
