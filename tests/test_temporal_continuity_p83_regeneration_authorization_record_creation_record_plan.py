from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p83_regeneration_authorization_record_creation_record_plan import (
    build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan,
    write_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan,
)
from scripts import (
    run_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan,
)

P92_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate/latest.json"
)
EXPECTED_P92_NEXT_LANE = (
    "P93_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN"
)



def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )



def _seed_p92(
    root: Path,
    *,
    status: str = "P83_RECORD_CREATION_AUTHORIZATION_ELIGIBLE",
    eligible: bool = True,
    authorization_granted_field: bool = False,
    p83_record_creation_allowed: bool = False,
    authorization_record_created: bool = False,
    authorization_granted: bool = False,
    authorization_token_created: bool = False,
    recommended_next_lane: str = EXPECTED_P92_NEXT_LANE,
    eligible_future_command: str = "NOT_COMPUTABLE",
    eligible_expected_output_path: str = "NOT_COMPUTABLE",
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    payload: dict[str, object] = {
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecordCreationAuthorizationGate.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_gate_only": True,
        "authorization_record_creation_gate_only": True,
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
        "source_p91_creation_plan_path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_plan/latest.json",
        "source_p91_creation_plan_observed": True,
        "source_p91_creation_plan_readable": True,
        "source_p91_creation_plan_hash": "a" * 64,
        "source_p91_creation_plan_status": "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY",
        "source_p91_recommended_next_lane": "P92_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE",
        "p83_record_creation_authorization_gate_status": status,
        "p83_record_creation_authorization_eligible": eligible,
        "p83_record_creation_authorization_granted": authorization_granted_field,
        "p83_record_creation_allowed": p83_record_creation_allowed,
        "p83_regeneration_execution_allowed": False,
        "eligibility_reasons": [],
        "denial_reasons": [],
        "prerequisite_checks": [],
        "gate_items": [],
        "planned_record_output_path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
        "planned_record_artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
        "eligible_future_command": eligible_future_command,
        "eligible_expected_output_path": eligible_expected_output_path,
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
        "gate_strategy_summary": {},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": "test seed",
        "denied_authority": [],
        "packet_hash": "f" * 64,
    }
    _write_json(root / P92_PATH, payload)



def test_missing_p92_source_returns_not_computable(tmp_path: Path) -> None:
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_record_plan_status"] == "NOT_COMPUTABLE"
    assert packet["p83_record_creation_record_required"] is False
    assert packet["recommended_next_lane"] == "P92_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION"



def test_malformed_p92_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P92_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_record_plan_status"] == "NOT_COMPUTABLE"



def test_p92_denied_or_not_computable_denies_record_planning(tmp_path: Path) -> None:
    _seed_p92(tmp_path, status="NOT_COMPUTABLE", eligible=False)
    packet_not_computable = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert (
        packet_not_computable["p83_record_creation_record_plan_status"]
        == "P83_RECORD_CREATION_RECORD_PLAN_DENIED"
    )

    _seed_p92(tmp_path, status="P83_RECORD_CREATION_AUTHORIZATION_DENIED", eligible=False)
    packet_denied = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert (
        packet_denied["p83_record_creation_record_plan_status"]
        == "P83_RECORD_CREATION_RECORD_PLAN_DENIED"
    )



def test_p92_not_required_maps_to_record_not_required(tmp_path: Path) -> None:
    _seed_p92(
        tmp_path,
        status="P83_RECORD_CREATION_AUTHORIZATION_NOT_REQUIRED",
        eligible=False,
    )
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert (
        packet["p83_record_creation_record_plan_status"]
        == "P83_RECORD_CREATION_RECORD_NOT_REQUIRED"
    )
    assert packet["p83_record_creation_record_required"] is False
    assert (
        packet["recommended_next_lane"]
        == "P94_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
    )



def test_p92_eligible_with_locks_false_maps_to_plan_ready(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert (
        packet["p83_record_creation_record_plan_status"]
        == "P83_RECORD_CREATION_RECORD_PLAN_READY"
    )
    assert packet["p83_record_creation_record_required"] is True
    assert packet["p83_record_creation_record_allowed"] is False
    assert (
        packet["recommended_next_lane"]
        == "P94_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_RECORD_CREATION_PLAN"
    )



def test_eligible_does_not_create_record(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_record_plan_status"] == "P83_RECORD_CREATION_RECORD_PLAN_READY"
    assert packet["authorization_record_created"] is False
    assert packet["planned_record"]["record_created"] is False



def test_authorization_record_created_is_always_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path, authorization_record_created=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_record_created"] is False



def test_authorization_record_creation_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_record_creation_authority"] is False



def test_authorization_granted_is_always_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path, authorization_granted=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_granted"] is False



def test_authorization_token_created_is_always_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path, authorization_token_created=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_token_created"] is False



def test_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["execution_authority"] is False



def test_regeneration_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["regeneration_execution_authority"] is False



def test_p83_record_creation_record_allowed_is_always_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path, p83_record_creation_allowed=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_record_allowed"] is False



def test_planned_record_record_creation_allowed_is_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["planned_record"]["record_creation_allowed"] is False



def test_planned_record_record_created_is_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["planned_record"]["record_created"] is False



def test_planned_record_authorization_granted_is_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["planned_record"]["authorization_granted"] is False



def test_planned_record_authorization_token_created_is_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["planned_record"]["authorization_token_created"] is False



def test_planned_record_execution_allowed_is_false(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["planned_record"]["execution_allowed"] is False



def test_wrong_recommended_next_lane_returns_not_computable(tmp_path: Path) -> None:
    _seed_p92(tmp_path, recommended_next_lane="P00_INVALID")
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_record_plan_status"] == "NOT_COMPUTABLE"



def test_planned_record_fields_deterministic(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["planned_record_fields"] == second["planned_record_fields"]



def test_provenance_links_deterministic(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["provenance_links"] == second["provenance_links"]



def test_replay_validation_requirements_deterministic(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["replay_validation_requirements"] == second[
        "replay_validation_requirements"
    ]



def test_expiration_policy_present_and_deterministic(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["expiration_policy"] == second["expiration_policy"]



def test_revocation_policy_present_and_deterministic(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["revocation_policy"] == second["revocation_policy"]



def test_rollback_policy_present_and_deterministic(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["rollback_policy"] == second["rollback_policy"]



def test_denial_propagation_rules_deterministic(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["denial_propagation_rules"] == second["denial_propagation_rules"]



def test_downstream_routing_rules_deterministic(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["downstream_routing_rules"] == second["downstream_routing_rules"]



def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p92(tmp_path, degraded_evidence_inputs=["e2", "e1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]



def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p92(tmp_path, inherited_blockers=["b2", "b1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]



def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p92(tmp_path, inherited_drift_flags=["d2", "d1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]



def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p92(tmp_path, semantic_overlap_flags=["s2", "s1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]



def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_record_plan.v1.schema.json"
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
        "p83_record_creation_record_allowed",
    ):
        assert schema["properties"][field]["const"] is False, field

    for field in (
        "record_creation_allowed",
        "record_created",
        "authorization_granted",
        "authorization_token_created",
        "execution_allowed",
    ):
        assert schema["properties"]["planned_record"]["properties"][field]["const"] is False



def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64



def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
            repo_root=tmp_path
        )
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_record_plan"
        / "latest.json"
    )
    write_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan(
        out_path, packet
    )
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")



def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p92(tmp_path)
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_record_plan"
        / "latest.json"
    )
    first = run_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan.run(
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

    artifact = "out/temporal_continuity_p83_regeneration_authorization_record_creation_record_plan/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
