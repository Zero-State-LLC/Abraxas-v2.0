from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p83_regeneration_authorization_record_creation_plan import (
    build_temporal_continuity_p83_regeneration_authorization_record_creation_plan,
    write_temporal_continuity_p83_regeneration_authorization_record_creation_plan,
)
from scripts.temporal import (
    run_temporal_continuity_p83_regeneration_authorization_record_creation_plan,
)

P90_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_plan/latest.json"
)
ELIGIBLE_COMMAND = (
    "python scripts/temporal/run_temporal_continuity_p79_authorization_gate_status_repair_plan.py"
)
ELIGIBLE_OUTPUT_PATH = (
    "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p90(
    root: Path,
    *,
    status: str = "P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_READY",
    record_required: bool = True,
    record_creation_allowed: bool = False,
    authorization_record_created: bool = False,
    authorization_granted: bool = False,
    authorization_token_created: bool = False,
    recommended_next_lane: str = "P91_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN",
    eligible_command: str = ELIGIBLE_COMMAND,
    eligible_output_path: str = ELIGIBLE_OUTPUT_PATH,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    payload = {
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecordPlan.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_record_plan_only": True,
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
        "authorization_granted": authorization_granted,
        "authorization_token_created": authorization_token_created,
        "authorization_record_creation_authority": False,
        "authorization_record_created": authorization_record_created,
        "spine_implementation_authority": False,
        "p83_regeneration_record_plan_status": status,
        "p83_regeneration_record_required": record_required,
        "p83_regeneration_record_creation_allowed": record_creation_allowed,
        "record_plan_items": [],
        "eligible_future_command": eligible_command,
        "eligible_expected_output_path": eligible_output_path,
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
        "record_strategy_summary": {},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": "test seed",
        "denied_authority": [],
        "packet_hash": "f" * 64,
    }
    _write_json(root / P90_PATH, payload)


def test_missing_p90_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_record_creation_plan_status"] == "NOT_COMPUTABLE"
    assert packet["p83_regeneration_record_creation_required"] is False
    assert (
        packet["recommended_next_lane"] == "P90_AUTHORIZATION_RECORD_PLAN_REGENERATION"
    )


def test_malformed_p90_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P90_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_record_creation_plan_status"] == "NOT_COMPUTABLE"


def test_p90_denied_or_not_computable_denies_creation_planning(
    tmp_path: Path,
) -> None:
    _seed_p90(tmp_path, status="NOT_COMPUTABLE")
    packet_not_computable = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert (
        packet_not_computable["p83_regeneration_record_creation_plan_status"]
        == "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED"
    )

    _seed_p90(tmp_path, status="P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_DENIED")
    packet_denied = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert (
        packet_denied["p83_regeneration_record_creation_plan_status"]
        == "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED"
    )


def test_p90_not_required_maps_to_creation_not_required(tmp_path: Path) -> None:
    _seed_p90(
        tmp_path,
        status="P83_REGENERATION_AUTHORIZATION_RECORD_NOT_REQUIRED",
        record_required=False,
    )
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert (
        packet["p83_regeneration_record_creation_plan_status"]
        == "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_NOT_REQUIRED"
    )
    assert (
        packet["recommended_next_lane"]
        == "P92_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
    )


def test_p90_ready_with_locks_false_maps_to_creation_plan_ready(
    tmp_path: Path,
) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert (
        packet["p83_regeneration_record_creation_plan_status"]
        == "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY"
    )
    assert packet["p83_regeneration_record_creation_required"] is True
    assert packet["p83_regeneration_record_creation_allowed"] is False
    assert (
        packet["recommended_next_lane"]
        == "P92_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE"
    )


def test_p90_ready_but_record_already_created_returns_not_computable_or_denied(
    tmp_path: Path,
) -> None:
    _seed_p90(tmp_path, authorization_record_created=True)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_record_creation_plan_status"] in {
        "NOT_COMPUTABLE",
        "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED",
    }


def test_p90_ready_but_authorization_granted_returns_not_computable_or_denied(
    tmp_path: Path,
) -> None:
    _seed_p90(tmp_path, authorization_granted=True)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_record_creation_plan_status"] in {
        "NOT_COMPUTABLE",
        "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED",
    }


def test_p90_ready_but_token_created_returns_not_computable_or_denied(
    tmp_path: Path,
) -> None:
    _seed_p90(tmp_path, authorization_token_created=True)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_record_creation_plan_status"] in {
        "NOT_COMPUTABLE",
        "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED",
    }


def test_wrong_recommended_next_lane_returns_not_computable(tmp_path: Path) -> None:
    _seed_p90(tmp_path, recommended_next_lane="P00_INVALID")
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["p83_regeneration_record_creation_plan_status"] == "NOT_COMPUTABLE"


def test_authorization_record_created_is_always_false(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_created"] is False
    assert all(
        item["authorization_record_created"] is False
        for item in packet["creation_plan_items"]
    )


def test_authorization_record_creation_allowed_is_always_false(
    tmp_path: Path,
) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert all(
        item["authorization_record_creation_allowed"] is False
        for item in packet["creation_plan_items"]
    )
    assert packet["p83_regeneration_record_creation_allowed"] is False


def test_authorization_record_creation_authority_is_always_false(
    tmp_path: Path,
) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_record_creation_authority"] is False


def test_authorization_granted_is_always_false(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_granted"] is False
    assert all(
        item["authorization_granted"] is False for item in packet["creation_plan_items"]
    )


def test_authorization_token_created_is_always_false(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["authorization_token_created"] is False
    assert all(
        item["authorization_token_created"] is False
        for item in packet["creation_plan_items"]
    )


def test_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["execution_authority"] is False


def test_regeneration_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["regeneration_execution_authority"] is False


def test_planned_record_output_creation_allowed_is_false(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["planned_record_output"]["creation_allowed"] is False


def test_planned_record_output_creation_authority_is_false(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["planned_record_output"]["creation_authority"] is False


def test_creation_plan_items_deterministic(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    first = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert first["creation_plan_items"] == second["creation_plan_items"]


def test_pre_creation_checks_deterministic(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    first = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert first["pre_creation_checks"] == second["pre_creation_checks"]


def test_rollback_policy_present_and_deterministic(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    first = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert first["rollback_policy"] == second["rollback_policy"]
    assert first["rollback_policy"]["rollback_supported"] is True


def test_fail_closed_policy_present_and_deterministic(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    first = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert first["fail_closed_policy"] == second["fail_closed_policy"]
    assert first["fail_closed_policy"]["fail_closed_required"] is True


def test_replay_validation_requirements_deterministic(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    first = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert first["replay_validation_requirements"] == second[
        "replay_validation_requirements"
    ]


def test_creation_denial_propagation_rules_deterministic(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    first = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert first["creation_denial_propagation_rules"] == second[
        "creation_denial_propagation_rules"
    ]


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p90(tmp_path, degraded_evidence_inputs=["e2", "e1"])
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p90(tmp_path, inherited_blockers=["b2", "b1"])
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p90(tmp_path, inherited_drift_flags=["d2", "d1"])
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p90(tmp_path, semantic_overlap_flags=["s2", "s1"])
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_plan.v1.schema.json"
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
        "authorization_granted",
        "authorization_token_created",
        "authorization_record_creation_authority",
        "authorization_record_created",
        "spine_implementation_authority",
        "p83_regeneration_record_creation_allowed",
    ):
        assert schema["properties"][field]["const"] is False, field
    assert (
        schema["properties"]["creation_plan_items"]["items"]["properties"][
            "authorization_record_creation_allowed"
        ]["const"]
        is False
    )
    assert (
        schema["properties"]["creation_plan_items"]["items"]["properties"][
            "authorization_record_created"
        ]["const"]
        is False
    )
    assert (
        schema["properties"]["creation_plan_items"]["items"]["properties"][
            "authorization_granted"
        ]["const"]
        is False
    )
    assert (
        schema["properties"]["creation_plan_items"]["items"]["properties"][
            "authorization_token_created"
        ]["const"]
        is False
    )
    assert (
        schema["properties"]["creation_plan_items"]["items"]["properties"][
            "execution_allowed"
        ]["const"]
        is False
    )
    assert (
        schema["properties"]["planned_record_output"]["properties"]["creation_allowed"][
            "const"
        ]
        is False
    )
    assert (
        schema["properties"]["planned_record_output"]["properties"][
            "creation_authority"
        ]["const"]
        is False
    )


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    first = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    packet = build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_plan"
        / "latest.json"
    )
    write_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
        out_path, packet
    )
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p90(tmp_path)
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_plan"
        / "latest.json"
    )
    first = run_temporal_continuity_p83_regeneration_authorization_record_creation_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_p83_regeneration_authorization_record_creation_plan.run(
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

    artifact = "out/temporal_continuity_p83_regeneration_authorization_record_creation_plan/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
