from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan import (
    build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan,
    write_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan,
)
from scripts import (
    run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan,
)

P95_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate/latest.json"
)
EXPECTED_P95_NEXT_LANE = (
    "P96_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_PLAN"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p95(
    root: Path,
    *,
    status: str = "P83_RECORD_CREATION_SEQUENCE_AUTHORIZATION_ELIGIBLE",
    eligible: bool = True,
    sequence_granted: bool = False,
    sequence_allowed: bool = False,
    p83_record_created: bool = False,
    authorization_record_created: bool = False,
    authorization_granted: bool = False,
    authorization_token_created: bool = False,
    recommended_next_lane: str = EXPECTED_P95_NEXT_LANE,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    payload: dict[str, object] = {
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecordCreationSequenceAuthorizationGate.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_gate_only": True,
        "authorization_record_creation_sequence_gate_only": True,
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
        "source_p94_sequence_plan_path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_record_creation_plan/latest.json",
        "source_p94_sequence_plan_observed": True,
        "source_p94_sequence_plan_readable": True,
        "source_p94_sequence_plan_hash": "a" * 64,
        "source_p94_sequence_plan_status": "P83_RECORD_CREATION_SEQUENCE_PLAN_READY",
        "source_p94_recommended_next_lane": "P95_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE",
        "p83_record_creation_sequence_authorization_gate_status": status,
        "p83_record_creation_sequence_authorization_eligible": eligible,
        "p83_record_creation_sequence_authorization_granted": sequence_granted,
        "p83_record_creation_sequence_allowed": sequence_allowed,
        "p83_record_created": p83_record_created,
        "p83_regeneration_execution_allowed": False,
        "eligibility_reasons": [],
        "denial_reasons": [],
        "prerequisite_checks": [],
        "gate_items": [],
        "planned_record_output_path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
        "planned_record_artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
        "eligible_future_command": "NOT_COMPUTABLE",
        "eligible_expected_output_path": "NOT_COMPUTABLE",
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
    _write_json(root / P95_PATH, payload)


# 1

def test_missing_p95_source_returns_not_computable(tmp_path: Path) -> None:
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_sequence_record_plan_status"] == "NOT_COMPUTABLE"


# 2

def test_malformed_p95_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P95_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_sequence_record_plan_status"] == "NOT_COMPUTABLE"


# 3

def test_p95_denied_or_not_computable_denies_sequence_record_planning(
    tmp_path: Path,
) -> None:
    _seed_p95(tmp_path, status="NOT_COMPUTABLE", eligible=False)
    not_computable = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert not_computable["p83_sequence_record_plan_status"] == "P83_SEQUENCE_RECORD_PLAN_DENIED"

    _seed_p95(
        tmp_path,
        status="P83_RECORD_CREATION_SEQUENCE_AUTHORIZATION_DENIED",
        eligible=False,
    )
    denied = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert denied["p83_sequence_record_plan_status"] == "P83_SEQUENCE_RECORD_PLAN_DENIED"


# 4

def test_p95_not_required_maps_to_p83_sequence_record_not_required(
    tmp_path: Path,
) -> None:
    _seed_p95(
        tmp_path,
        status="P83_RECORD_CREATION_SEQUENCE_AUTHORIZATION_NOT_REQUIRED",
        eligible=False,
    )
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_sequence_record_plan_status"] == "P83_SEQUENCE_RECORD_NOT_REQUIRED"
    assert (
        packet["recommended_next_lane"]
        == "P97_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
    )


# 5

def test_p95_eligible_plus_locks_false_maps_to_plan_ready(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_sequence_record_plan_status"] == "P83_SEQUENCE_RECORD_PLAN_READY"
    assert packet["p83_sequence_record_required"] is True
    assert packet["p83_sequence_record_allowed"] is False


# 6

def test_eligible_does_not_create_record(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_record_created"] is False


# 7

def test_authorization_record_created_is_always_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path, authorization_record_created=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_record_created"] is False


# 8

def test_authorization_record_creation_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_record_creation_authority"] is False


# 9

def test_authorization_granted_is_always_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path, authorization_granted=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_granted"] is False


# 10

def test_authorization_token_created_is_always_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path, authorization_token_created=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_token_created"] is False


# 11

def test_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["execution_authority"] is False


# 12

def test_regeneration_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["regeneration_execution_authority"] is False


# 13

def test_p83_sequence_record_allowed_is_always_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path, sequence_allowed=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_sequence_record_allowed"] is False


# 14

def test_planned_sequence_record_sequence_record_allowed_is_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["planned_sequence_record"]["sequence_record_allowed"] is False


# 15

def test_planned_sequence_record_record_created_is_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["planned_sequence_record"]["record_created"] is False


# 16

def test_planned_sequence_record_authorization_granted_is_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["planned_sequence_record"]["authorization_granted"] is False


# 17

def test_planned_sequence_record_authorization_token_created_is_false(
    tmp_path: Path,
) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["planned_sequence_record"]["authorization_token_created"] is False


# 18

def test_planned_sequence_record_execution_allowed_is_false(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["planned_sequence_record"]["execution_allowed"] is False


# 19

def test_wrong_recommended_next_lane_returns_not_computable(tmp_path: Path) -> None:
    _seed_p95(tmp_path, recommended_next_lane="P00_INVALID")
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["p83_sequence_record_plan_status"] == "NOT_COMPUTABLE"


# 20

def test_planned_sequence_record_fields_deterministic(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["planned_sequence_record_fields"] == second["planned_sequence_record_fields"]


# 21

def test_provenance_links_deterministic(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["provenance_links"] == second["provenance_links"]


# 22

def test_replay_validation_requirements_deterministic(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["replay_validation_requirements"] == second[
        "replay_validation_requirements"
    ]


# 23

def test_expiration_policy_present_and_deterministic(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["expiration_policy"] == second["expiration_policy"]


# 24

def test_revocation_policy_present_and_deterministic(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["revocation_policy"] == second["revocation_policy"]


# 25

def test_rollback_policy_present_and_deterministic(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["rollback_policy"] == second["rollback_policy"]


# 26

def test_denial_propagation_rules_deterministic(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["denial_propagation_rules"] == second["denial_propagation_rules"]


# 27

def test_downstream_routing_rules_deterministic(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["downstream_routing_rules"] == second["downstream_routing_rules"]


# 28

def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p95(tmp_path, degraded_evidence_inputs=["e2", "e1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


# 29

def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p95(tmp_path, inherited_blockers=["b2", "b1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


# 30

def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p95(tmp_path, inherited_drift_flags=["d2", "d1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


# 31

def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p95(tmp_path, semantic_overlap_flags=["s2", "s1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


# 32

def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan.v1.schema.json"
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
        "p83_sequence_record_allowed",
    ):
        assert schema["properties"][field]["const"] is False, field
    for field in (
        "sequence_record_allowed",
        "record_created",
        "authorization_granted",
        "authorization_token_created",
        "execution_allowed",
    ):
        assert (
            schema["properties"]["planned_sequence_record"]["properties"][field]["const"]
            is False
        )


# 33

def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


# 34

def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
            repo_root=tmp_path
        )
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan"
        / "latest.json"
    )
    write_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan(
        out_path, packet
    )
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


# 35

def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p95(tmp_path)
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan"
        / "latest.json"
    )
    first = (
        run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan.run(
            repo_root=tmp_path,
            out_path=out_path,
        )
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = (
        run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan.run(
            repo_root=tmp_path,
            out_path=out_path,
        )
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


# 36

def test_artifact_registry_classifies_output_as_derived_optional() -> None:
    from core.generated_artifact_registry import (  # type: ignore[attr-defined]
        _DERIVED_OPTIONAL_ARTIFACTS,
        build_generated_artifact_registry,
        list_ci_drift_artifact_paths,
    )

    artifact = "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
