from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate import (
    build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate,
    write_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate,
)
from scripts.temporal import (
    run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate,
)

P94_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_record_creation_plan/latest.json"
)
EXPECTED_P94_NEXT_LANE = (
    "P95_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p94(
    root: Path,
    *,
    status: str = "P83_RECORD_CREATION_SEQUENCE_PLAN_READY",
    sequence_required: bool = True,
    sequence_allowed: bool = False,
    authorization_record_created: bool = False,
    authorization_granted: bool = False,
    authorization_token_created: bool = False,
    recommended_next_lane: str = EXPECTED_P94_NEXT_LANE,
    include_planned_record_output: bool = True,
    planned_output_creation_allowed: bool = False,
    planned_output_creation_authority: bool = False,
    planned_output_record_created: bool = False,
    planned_output_authorization_granted: bool = False,
    planned_output_authorization_token_created: bool = False,
    planned_output_execution_allowed: bool = False,
    authority_overrides: dict[str, bool] | None = None,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    payload: dict[str, object] = {
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecordCreationRecordCreationPlan.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_record_creation_sequence_plan_only": True,
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
        "source_p93_record_plan_path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_record_plan/latest.json",
        "source_p93_record_plan_observed": True,
        "source_p93_record_plan_readable": True,
        "source_p93_record_plan_hash": "a" * 64,
        "source_p93_record_plan_status": "P83_RECORD_CREATION_RECORD_PLAN_READY",
        "source_p93_recommended_next_lane": "P94_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_RECORD_CREATION_PLAN",
        "p83_record_creation_sequence_plan_status": status,
        "p83_record_creation_sequence_required": sequence_required,
        "p83_record_creation_sequence_allowed": sequence_allowed,
        "creation_sequence_steps": [],
        "pre_creation_checks": [],
        "planned_record_output": {
            "path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
            "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
            "overwrite_policy": "WRITE_ON_AUTHORIZED_FUTURE_LANE_ONLY",
            "creation_allowed": planned_output_creation_allowed,
            "creation_authority": planned_output_creation_authority,
            "record_created": planned_output_record_created,
            "authorization_granted": planned_output_authorization_granted,
            "authorization_token_created": planned_output_authorization_token_created,
            "execution_allowed": planned_output_execution_allowed,
        },
        "replay_validation_requirements": [],
        "expiration_policy": {},
        "revocation_policy": {},
        "rollback_policy": {},
        "denial_propagation_rules": [],
        "downstream_routing_rules": [],
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
        "sequence_strategy_summary": {},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": "test seed",
        "denied_authority": [],
        "packet_hash": "f" * 64,
    }

    if not include_planned_record_output:
        payload.pop("planned_record_output", None)

    if authority_overrides:
        for field, value in authority_overrides.items():
            payload[field] = value

    _write_json(root / P94_PATH, payload)


# 1

def test_missing_p94_source_returns_not_computable(tmp_path: Path) -> None:
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_gate_status"] == "NOT_COMPUTABLE"
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert packet["denial_reasons"] == ["P94_SOURCE_MISSING"]


# 2

def test_malformed_p94_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P94_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_gate_status"] == "NOT_COMPUTABLE"
    assert packet["denial_reasons"] == ["P94_SOURCE_MALFORMED_JSON"]


# 3

def test_p94_denied_or_not_computable_denies_sequence_eligibility(
    tmp_path: Path,
) -> None:
    _seed_p94(tmp_path, status="NOT_COMPUTABLE")
    packet_not_computable = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert (
        packet_not_computable["p83_record_creation_sequence_authorization_gate_status"]
        == "P83_RECORD_CREATION_SEQUENCE_AUTHORIZATION_DENIED"
    )
    assert packet_not_computable["denial_reasons"] == ["P94_NOT_COMPUTABLE"]

    _seed_p94(tmp_path, status="P83_RECORD_CREATION_SEQUENCE_PLAN_DENIED")
    packet_denied = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert (
        packet_denied["p83_record_creation_sequence_authorization_gate_status"]
        == "P83_RECORD_CREATION_SEQUENCE_AUTHORIZATION_DENIED"
    )
    assert packet_denied["denial_reasons"] == ["P94_SEQUENCE_PLAN_DENIED"]


# 4

def test_p94_not_required_maps_to_not_required(tmp_path: Path) -> None:
    _seed_p94(
        tmp_path,
        status="P83_RECORD_CREATION_SEQUENCE_NOT_REQUIRED",
        sequence_required=False,
    )
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert (
        packet["p83_record_creation_sequence_authorization_gate_status"]
        == "P83_RECORD_CREATION_SEQUENCE_AUTHORIZATION_NOT_REQUIRED"
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert (
        packet["recommended_next_lane"]
        == "P96_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
    )


# 5

def test_p94_ready_plus_locks_false_maps_to_eligible(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert (
        packet["p83_record_creation_sequence_authorization_gate_status"]
        == "P83_RECORD_CREATION_SEQUENCE_AUTHORIZATION_ELIGIBLE"
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is True
    assert (
        packet["recommended_next_lane"]
        == "P96_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_PLAN"
    )


# 6

def test_eligible_does_not_grant_sequence_authorization(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is True
    assert packet["p83_record_creation_sequence_authorization_granted"] is False
    assert packet["p83_record_creation_sequence_allowed"] is False


# 7

def test_authorization_record_created_is_always_false(tmp_path: Path) -> None:
    _seed_p94(tmp_path, authorization_record_created=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_record_created"] is False


# 8

def test_authorization_record_creation_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_record_creation_authority"] is False


# 9

def test_p83_record_creation_sequence_authorization_granted_is_always_false(
    tmp_path: Path,
) -> None:
    _seed_p94(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_granted"] is False


# 10

def test_p83_record_creation_sequence_allowed_is_always_false(tmp_path: Path) -> None:
    _seed_p94(tmp_path, sequence_allowed=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_allowed"] is False
    assert all(item["sequence_allowed"] is False for item in packet["gate_items"])


# 11

def test_p83_record_created_is_always_false(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_created"] is False
    assert all(item["record_created"] is False for item in packet["gate_items"])


# 12

def test_authorization_granted_is_always_false(tmp_path: Path) -> None:
    _seed_p94(tmp_path, authorization_granted=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_granted"] is False


# 13

def test_authorization_token_created_is_always_false(tmp_path: Path) -> None:
    _seed_p94(tmp_path, authorization_token_created=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_token_created"] is False


# 14

def test_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["execution_authority"] is False


# 15

def test_regeneration_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["regeneration_execution_authority"] is False


# 16

def test_wrong_recommended_next_lane_returns_not_computable_or_denied(
    tmp_path: Path,
) -> None:
    _seed_p94(tmp_path, recommended_next_lane="P00_INVALID")
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_gate_status"] in {
        "NOT_COMPUTABLE",
        "P83_RECORD_CREATION_SEQUENCE_AUTHORIZATION_DENIED",
    }
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert "P94_RECOMMENDED_LANE_MISMATCH" in packet["denial_reasons"]


# 17

def test_missing_planned_record_output_denies_eligibility(tmp_path: Path) -> None:
    _seed_p94(tmp_path, include_planned_record_output=False)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert "P94_RECORD_OUTPUT_MISSING" in packet["denial_reasons"]


# 18

def test_planned_record_output_creation_allowed_true_denies_eligibility(
    tmp_path: Path,
) -> None:
    _seed_p94(tmp_path, planned_output_creation_allowed=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert "P94_SEQUENCE_LOCK_VIOLATION" in packet["denial_reasons"]


# 19

def test_planned_record_output_creation_authority_true_denies_eligibility(
    tmp_path: Path,
) -> None:
    _seed_p94(tmp_path, planned_output_creation_authority=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert "P94_SEQUENCE_LOCK_VIOLATION" in packet["denial_reasons"]


# 20

def test_planned_record_output_record_created_true_denies_eligibility(
    tmp_path: Path,
) -> None:
    _seed_p94(tmp_path, planned_output_record_created=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert "P94_SEQUENCE_LOCK_VIOLATION" in packet["denial_reasons"]


# 21

def test_planned_record_output_authorization_granted_true_denies_eligibility(
    tmp_path: Path,
) -> None:
    _seed_p94(tmp_path, planned_output_authorization_granted=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert "P94_SEQUENCE_LOCK_VIOLATION" in packet["denial_reasons"]


# 22

def test_planned_record_output_authorization_token_created_true_denies_eligibility(
    tmp_path: Path,
) -> None:
    _seed_p94(tmp_path, planned_output_authorization_token_created=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert "P94_SEQUENCE_LOCK_VIOLATION" in packet["denial_reasons"]


# 23

def test_planned_record_output_execution_allowed_true_denies_eligibility(
    tmp_path: Path,
) -> None:
    _seed_p94(tmp_path, planned_output_execution_allowed=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert "P94_SEQUENCE_LOCK_VIOLATION" in packet["denial_reasons"]


# 24

def test_authority_lock_violation_denies_eligibility(tmp_path: Path) -> None:
    _seed_p94(tmp_path, authority_overrides={"execution_authority": True})
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_sequence_authorization_eligible"] is False
    assert "P94_AUTHORITY_LOCK_VIOLATION" in packet["denial_reasons"]


# 25

def test_eligibility_reasons_deterministic(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert first["eligibility_reasons"] == second["eligibility_reasons"]
    assert first["eligibility_reasons"] == [
        "P94_SEQUENCE_PLAN_READY",
        "P94_RECOMMENDS_P95_GATE",
        "P94_RECORD_OUTPUT_DEFINED",
        "P94_SEQUENCE_LOCKS_FALSE",
        "P94_AUTHORITY_LOCKS_FALSE",
        "SEQUENCE_ELIGIBLE_BUT_NOT_GRANTED",
    ]


# 26

def test_denial_reasons_deterministic(tmp_path: Path) -> None:
    _seed_p94(
        tmp_path,
        recommended_next_lane="P00_INVALID",
        include_planned_record_output=False,
        authority_overrides={"runtime_authority": True},
    )
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert first["denial_reasons"] == second["denial_reasons"]
    assert first["denial_reasons"] == [
        "P94_RECOMMENDED_LANE_MISMATCH",
        "P94_RECORD_OUTPUT_MISSING",
        "P94_SEQUENCE_LOCK_VIOLATION",
        "P94_AUTHORITY_LOCK_VIOLATION",
    ]


# 27

def test_prerequisite_checks_deterministic(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    ids = [item["check_id"] for item in first["prerequisite_checks"]]
    assert first["prerequisite_checks"] == second["prerequisite_checks"]
    assert ids == [
        "prerequisite_001_source_exists_readable",
        "prerequisite_002_source_status_ready",
        "prerequisite_003_source_lane_exact_match",
        "prerequisite_004_record_output_defined",
        "prerequisite_005_sequence_locks_false",
        "prerequisite_006_authority_locks_false",
    ]


# 28

def test_gate_items_deterministic(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert first["gate_items"] == second["gate_items"]
    assert first["gate_items"] == [
        {
            "gate_item_id": "gate_item_001",
            "lane": "P83",
            "source_sequence_plan_path": P94_PATH,
            "planned_record_output_path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
            "planned_record_artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
            "authorization_eligible": True,
            "authorization_granted": False,
            "sequence_allowed": False,
            "record_created": False,
            "token_created": False,
            "execution_allowed": False,
            "blocking_reason": "SEQUENCE_AUTHORIZATION_GRANT_NOT_PERMITTED_IN_P95",
        }
    ]


# 29

def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p94(tmp_path, degraded_evidence_inputs=["e2", "e1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


# 30

def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p94(tmp_path, inherited_blockers=["b2", "b1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


# 31

def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p94(tmp_path, inherited_drift_flags=["d2", "d1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


# 32

def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p94(tmp_path, semantic_overlap_flags=["s2", "s1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


# 33

def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate.v1.schema.json"
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
        "p83_record_creation_sequence_authorization_granted",
        "p83_record_creation_sequence_allowed",
        "p83_record_created",
        "p83_regeneration_execution_allowed",
    ):
        assert schema["properties"][field]["const"] is False, field
    assert (
        schema["properties"]["gate_items"]["items"]["properties"]["authorization_granted"][
            "const"
        ]
        is False
    )
    assert (
        schema["properties"]["gate_items"]["items"]["properties"]["sequence_allowed"][
            "const"
        ]
        is False
    )
    assert (
        schema["properties"]["gate_items"]["items"]["properties"]["record_created"][
            "const"
        ]
        is False
    )
    assert (
        schema["properties"]["gate_items"]["items"]["properties"]["token_created"][
            "const"
        ]
        is False
    )
    assert (
        schema["properties"]["gate_items"]["items"]["properties"]["execution_allowed"][
            "const"
        ]
        is False
    )


# 34

def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


# 35

def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
            repo_root=tmp_path
        )
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate"
        / "latest.json"
    )
    write_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate(
        out_path, packet
    )
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


# 36

def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p94(tmp_path)
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate"
        / "latest.json"
    )
    first = run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


# 37

def test_artifact_registry_classifies_output_as_derived_optional() -> None:
    from core.generated_artifact_registry import (  # type: ignore[attr-defined]
        _DERIVED_OPTIONAL_ARTIFACTS,
        build_generated_artifact_registry,
        list_ci_drift_artifact_paths,
    )

    artifact = "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
