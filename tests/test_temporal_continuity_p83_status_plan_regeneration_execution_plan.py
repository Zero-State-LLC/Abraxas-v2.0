from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p83_status_plan_regeneration_execution_plan import (
    build_temporal_continuity_p83_status_plan_regeneration_execution_plan,
    write_temporal_continuity_p83_status_plan_regeneration_execution_plan,
)
from scripts import run_temporal_continuity_p83_status_plan_regeneration_execution_plan

P87_PATH = "out/temporal_continuity_p83_status_plan_regeneration_plan/latest.json"
ALLOWED_COMMAND = (
    "python scripts/run_temporal_continuity_p79_authorization_gate_status_repair_plan.py"
)
EXPECTED_OUTPUT_PATH = (
    "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p87(
    root: Path,
    *,
    status: str = "P83_REGENERATION_PLAN_READY",
    future_runner_command: str = ALLOWED_COMMAND,
    expected_output_path: str = EXPECTED_OUTPUT_PATH,
    production_activation: bool = False,
    p83_regeneration_allowed: bool = False,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    _write_json(
        root / P87_PATH,
        {
            "artifact_type": "TemporalContinuityP83StatusPlanRegenerationPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "regeneration_plan_only": True,
            "meta_regeneration_plan_only": True,
            "production_activation": production_activation,
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
            "source_p86_plan_path": "out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json",
            "source_p86_plan_observed": True,
            "source_p86_plan_readable": True,
            "source_p86_plan_hash": "a" * 64,
            "source_p86_plan_status": "P84_REGENERATION_PLAN_BLOCKED",
            "source_p86_recommended_next_lane": "P87_TEMPORAL_CONTINUITY_P83_STATUS_PLAN_REGENERATION_PLAN",
            "source_p83_status_plan_path": EXPECTED_OUTPUT_PATH,
            "source_p83_status_plan_observed": False,
            "source_p83_status_plan_readable": False,
            "source_p83_status_plan_hash": "NOT_COMPUTABLE",
            "source_p83_status_plan_status": "NOT_COMPUTABLE",
            "source_p82_repair_plan_path": "out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json",
            "source_p82_repair_plan_observed": True,
            "source_p82_repair_plan_readable": True,
            "source_p82_repair_plan_hash": "b" * 64,
            "source_p82_repair_plan_status": "P79_REPAIR_NOT_REQUIRED",
            "p83_regeneration_plan_status": status,
            "p83_regeneration_required": status == "P83_REGENERATION_PLAN_READY",
            "p83_regeneration_allowed": p83_regeneration_allowed,
            "regeneration_reasons": [],
            "regeneration_items": [],
            "future_runner_command": future_runner_command,
            "expected_output_path": expected_output_path,
            "prerequisite_sources": [],
            "validation_requirements": [],
            "blocked_regeneration_reasons": [],
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
            "regeneration_strategy_summary": {},
            "recommended_next_lane": "P88_TEMPORAL_CONTINUITY_P83_STATUS_PLAN_REGENERATION_EXECUTION_PLAN",
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "f" * 64,
        },
    )


def test_missing_p87_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_execution_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P87_REGENERATION_PLAN_REGENERATION"


def test_malformed_p87_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P87_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_execution_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P87_REGENERATION_PLAN_REGENERATION"


def test_p87_blocked_or_not_computable_blocks_p88(tmp_path: Path) -> None:
    _seed_p87(tmp_path, status="NOT_COMPUTABLE")
    packet_not_computable = (
        build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
            repo_root=tmp_path
        )
    )
    assert (
        packet_not_computable["p83_regeneration_execution_plan_status"]
        == "P83_REGENERATION_EXECUTION_PLAN_BLOCKED"
    )

    _seed_p87(tmp_path, status="P83_REGENERATION_PLAN_BLOCKED")
    packet_blocked = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert (
        packet_blocked["p83_regeneration_execution_plan_status"]
        == "P83_REGENERATION_EXECUTION_PLAN_BLOCKED"
    )
    assert packet_blocked["recommended_next_lane"] == "P87_REGENERATION_PLAN_REGENERATION"


def test_p87_not_required_maps_to_execution_not_required(tmp_path: Path) -> None:
    _seed_p87(tmp_path, status="P83_REGENERATION_NOT_REQUIRED")
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert (
        packet["p83_regeneration_execution_plan_status"]
        == "P83_REGENERATION_EXECUTION_NOT_REQUIRED"
    )
    assert (
        packet["recommended_next_lane"]
        == "P89_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
    )


def test_p87_ready_plus_exact_command_and_path_maps_to_ready(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert (
        packet["p83_regeneration_execution_plan_status"]
        == "P83_REGENERATION_EXECUTION_PLAN_READY"
    )
    assert packet["p83_regeneration_execution_required"] is True
    assert packet["p83_regeneration_execution_allowed"] is False
    assert (
        packet["recommended_next_lane"]
        == "P89_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_GATE"
    )


def test_wrong_future_runner_command_returns_not_computable(tmp_path: Path) -> None:
    _seed_p87(tmp_path, future_runner_command=f"{ALLOWED_COMMAND} && echo x")
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_execution_plan_status"] == "NOT_COMPUTABLE"
    assert "P87_COMMAND_MISMATCH" in packet["blocked_execution_reasons"]


def test_wrong_expected_output_path_returns_not_computable(tmp_path: Path) -> None:
    _seed_p87(tmp_path, expected_output_path="out/other/latest.json")
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_execution_plan_status"] == "NOT_COMPUTABLE"
    assert "P87_EXPECTED_OUTPUT_PATH_MISMATCH" in packet["blocked_execution_reasons"]


def test_p83_regeneration_execution_allowed_is_always_false(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_execution_allowed"] is False


def test_execution_authorized_is_always_false(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    for step in packet["execution_steps"]:
        assert step["execution_authorized"] is False
    for item in packet["command_allowlist"]:
        assert item["execution_authorized"] is False


def test_execution_allowed_is_always_false(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    for step in packet["execution_steps"]:
        assert step["execution_allowed"] is False
    for item in packet["command_allowlist"]:
        assert item["execution_allowed"] is False


def test_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["execution_authority"] is False


def test_regeneration_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["regeneration_execution_authority"] is False


def test_command_allowlist_only_contains_exact_command_when_ready(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["command_allowlist"] == [
        {
            "command": ALLOWED_COMMAND,
            "allowlisted_for_future_execution": True,
            "execution_authorized": False,
            "execution_allowed": False,
            "blocking_reason": "AUTHORIZATION_REQUIRED_EXECUTION_DENIED_IN_P88",
        }
    ]


def test_no_shell_chaining_or_flags_accepted(tmp_path: Path) -> None:
    _seed_p87(tmp_path, future_runner_command=f"{ALLOWED_COMMAND} --dry-run")
    packet_flag = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet_flag["p83_regeneration_execution_plan_status"] == "NOT_COMPUTABLE"

    _seed_p87(tmp_path, future_runner_command=f"{ALLOWED_COMMAND} && echo nope")
    packet_chain = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet_chain["p83_regeneration_execution_plan_status"] == "NOT_COMPUTABLE"


def test_expected_output_path_is_exact(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["expected_output_path"] == EXPECTED_OUTPUT_PATH


def test_preflight_checks_include_required_checks(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    ids = [item["check_id"] for item in packet["preflight_checks"]]
    assert ids == [
        "preflight_001_source_p87_exists_readable",
        "preflight_002_source_p87_status_ready",
        "preflight_003_future_runner_command_exact_match",
        "preflight_004_expected_output_path_exact_match",
        "preflight_005_source_authority_fields_false",
        "preflight_006_p83_regeneration_execution_allowed_false",
    ]


def test_post_run_validations_include_required_checks(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    ids = [item["validation_id"] for item in packet["post_run_validations"]]
    assert ids == [
        "postrun_001_p83_output_exists",
        "postrun_002_p83_output_readable",
        "postrun_003_p83_artifact_type_expected",
        "postrun_004_p83_status_not_not_computable",
        "postrun_005_p83_authority_flags_false",
        "postrun_006_p83_packet_hash_valid",
    ]


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p87(tmp_path, degraded_evidence_inputs=["e2", "e1"])
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p87(tmp_path, inherited_blockers=["b2", "b1"])
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p87(tmp_path, inherited_drift_flags=["d2", "d1"])
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p87(tmp_path, semantic_overlap_flags=["s2", "s1"])
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p83_status_plan_regeneration_execution_plan.v1.schema.json"
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
    assert schema["properties"]["p83_regeneration_execution_allowed"]["const"] is False
    assert (
        schema["properties"]["execution_steps"]["items"]["properties"][
            "execution_authorized"
        ]["const"]
        is False
    )
    assert (
        schema["properties"]["execution_steps"]["items"]["properties"][
            "execution_allowed"
        ]["const"]
        is False
    )
    assert (
        schema["properties"]["command_allowlist"]["items"]["properties"][
            "execution_authorized"
        ]["const"]
        is False
    )
    assert (
        schema["properties"]["command_allowlist"]["items"]["properties"][
            "execution_allowed"
        ]["const"]
        is False
    )


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    first = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    packet = build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_status_plan_regeneration_execution_plan"
        / "latest.json"
    )
    write_temporal_continuity_p83_status_plan_regeneration_execution_plan(
        out_path,
        packet,
    )
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p87(tmp_path)
    first = run_temporal_continuity_p83_status_plan_regeneration_execution_plan.run(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_status_plan_regeneration_execution_plan"
        / "latest.json"
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_p83_status_plan_regeneration_execution_plan.run(
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

    artifact = (
        "out/temporal_continuity_p83_status_plan_regeneration_execution_plan/latest.json"
    )
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
