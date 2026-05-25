from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate import (
    build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate,
    write_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate,
)
from scripts import (
    run_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate,
)

P91_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_plan/latest.json"
)
EXPECTED_P91_NEXT_LANE = (
    "P92_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p91(
    root: Path,
    *,
    status: str = "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY",
    record_creation_required: bool = True,
    record_creation_allowed: bool = False,
    authorization_record_created: bool = False,
    authorization_granted: bool = False,
    authorization_token_created: bool = False,
    recommended_next_lane: str = EXPECTED_P91_NEXT_LANE,
    include_planned_record_output: bool = True,
    planned_output_creation_allowed: bool = False,
    planned_output_creation_authority: bool = False,
    authority_overrides: dict[str, bool] | None = None,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    payload: dict[str, object] = {
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecordCreationPlan.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_record_creation_plan_only": True,
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
        "source_p90_record_plan_path": "out/temporal_continuity_p83_regeneration_authorization_record_plan/latest.json",
        "source_p90_record_plan_observed": True,
        "source_p90_record_plan_readable": True,
        "source_p90_record_plan_hash": "a" * 64,
        "source_p90_record_plan_status": "P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_READY",
        "source_p90_recommended_next_lane": "P91_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN",
        "p83_regeneration_record_creation_plan_status": status,
        "p83_regeneration_record_creation_required": record_creation_required,
        "p83_regeneration_record_creation_allowed": record_creation_allowed,
        "creation_plan_items": [],
        "pre_creation_checks": [],
        "rollback_policy": {},
        "fail_closed_policy": {},
        "replay_validation_requirements": [],
        "creation_denial_propagation_rules": [],
        "eligible_future_command": "python scripts/run_future_authorized_record_creation.py",
        "eligible_expected_output_path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
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
        "creation_strategy_summary": {},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": "test seed",
        "denied_authority": [],
        "packet_hash": "f" * 64,
    }

    if include_planned_record_output:
        payload["planned_record_output"] = {
            "path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
            "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
            "overwrite_policy": "DENY_UNLESS_AUTHORIZED_BY_FUTURE_GATE",
            "creation_allowed": planned_output_creation_allowed,
            "creation_authority": planned_output_creation_authority,
        }

    if authority_overrides:
        for field, value in authority_overrides.items():
            payload[field] = value

    _write_json(root / P91_PATH, payload)


def test_missing_p91_source_returns_not_computable(tmp_path: Path) -> None:
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_authorization_gate_status"] == "NOT_COMPUTABLE"
    assert packet["p83_record_creation_authorization_eligible"] is False
    assert packet["denial_reasons"] == ["P91_SOURCE_MISSING"]


def test_malformed_p91_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P91_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_authorization_gate_status"] == "NOT_COMPUTABLE"
    assert packet["denial_reasons"] == ["P91_SOURCE_MALFORMED_JSON"]


def test_p91_denied_or_not_computable_denies_record_creation_eligibility(
    tmp_path: Path,
) -> None:
    _seed_p91(tmp_path, status="NOT_COMPUTABLE")
    packet_not_computable = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert (
        packet_not_computable["p83_record_creation_authorization_gate_status"]
        == "P83_RECORD_CREATION_AUTHORIZATION_DENIED"
    )
    assert packet_not_computable["denial_reasons"] == ["P91_NOT_COMPUTABLE"]

    _seed_p91(
        tmp_path,
        status="P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED",
    )
    packet_denied = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert (
        packet_denied["p83_record_creation_authorization_gate_status"]
        == "P83_RECORD_CREATION_AUTHORIZATION_DENIED"
    )
    assert packet_denied["denial_reasons"] == ["P91_CREATION_PLAN_DENIED"]


def test_p91_not_required_maps_to_not_required(tmp_path: Path) -> None:
    _seed_p91(
        tmp_path,
        status="P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_NOT_REQUIRED",
        record_creation_required=False,
    )
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert (
        packet["p83_record_creation_authorization_gate_status"]
        == "P83_RECORD_CREATION_AUTHORIZATION_NOT_REQUIRED"
    )
    assert packet["p83_record_creation_authorization_eligible"] is False
    assert (
        packet["recommended_next_lane"]
        == "P93_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
    )


def test_p91_ready_plus_locks_false_maps_to_eligible(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert (
        packet["p83_record_creation_authorization_gate_status"]
        == "P83_RECORD_CREATION_AUTHORIZATION_ELIGIBLE"
    )
    assert packet["p83_record_creation_authorization_eligible"] is True
    assert (
        packet["recommended_next_lane"]
        == "P93_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN"
    )


def test_eligible_does_not_grant_creation_authorization(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_authorization_eligible"] is True
    assert packet["p83_record_creation_authorization_granted"] is False
    assert packet["p83_record_creation_allowed"] is False


def test_authorization_record_created_is_always_false(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_record_created"] is False
    assert all(item["record_created"] is False for item in packet["gate_items"])


def test_authorization_record_creation_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_record_creation_authority"] is False


def test_p83_record_creation_authorization_granted_is_always_false(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_authorization_granted"] is False


def test_p83_record_creation_allowed_is_always_false(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_allowed"] is False
    assert all(item["record_creation_allowed"] is False for item in packet["gate_items"])


def test_authorization_granted_is_always_false(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_granted"] is False
    assert all(item["authorization_granted"] is False for item in packet["gate_items"])


def test_authorization_token_created_is_always_false(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["authorization_token_created"] is False
    assert all(item["token_created"] is False for item in packet["gate_items"])


def test_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["execution_authority"] is False


def test_regeneration_execution_authority_is_always_false(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["regeneration_execution_authority"] is False


def test_wrong_recommended_next_lane_returns_not_computable_or_denied(
    tmp_path: Path,
) -> None:
    _seed_p91(tmp_path, recommended_next_lane="P00_INVALID")
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_authorization_gate_status"] in {
        "NOT_COMPUTABLE",
        "P83_RECORD_CREATION_AUTHORIZATION_DENIED",
    }
    assert packet["p83_record_creation_authorization_eligible"] is False
    assert "P91_RECOMMENDED_LANE_MISMATCH" in packet["denial_reasons"]


def test_missing_planned_record_output_denies_eligibility(tmp_path: Path) -> None:
    _seed_p91(tmp_path, include_planned_record_output=False)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_authorization_eligible"] is False
    assert "P91_RECORD_OUTPUT_MISSING" in packet["denial_reasons"]


def test_planned_record_output_creation_allowed_true_denies_eligibility(
    tmp_path: Path,
) -> None:
    _seed_p91(tmp_path, planned_output_creation_allowed=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_authorization_eligible"] is False
    assert "P91_CREATION_LOCK_VIOLATION" in packet["denial_reasons"]


def test_planned_record_output_creation_authority_true_denies_eligibility(
    tmp_path: Path,
) -> None:
    _seed_p91(tmp_path, planned_output_creation_authority=True)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_authorization_eligible"] is False
    assert "P91_CREATION_LOCK_VIOLATION" in packet["denial_reasons"]


def test_authority_lock_violation_denies_eligibility(tmp_path: Path) -> None:
    _seed_p91(tmp_path, authority_overrides={"execution_authority": True})
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["p83_record_creation_authorization_eligible"] is False
    assert "P91_AUTHORITY_LOCK_VIOLATION" in packet["denial_reasons"]


def test_eligibility_reasons_deterministic(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert first["eligibility_reasons"] == second["eligibility_reasons"]
    assert first["eligibility_reasons"] == [
        "P91_CREATION_PLAN_READY",
        "P91_RECOMMENDS_P92_GATE",
        "P91_RECORD_OUTPUT_DEFINED",
        "P91_CREATION_LOCKS_FALSE",
        "P91_AUTHORITY_LOCKS_FALSE",
        "RECORD_CREATION_ELIGIBLE_BUT_NOT_GRANTED",
    ]


def test_denial_reasons_deterministic(tmp_path: Path) -> None:
    _seed_p91(
        tmp_path,
        recommended_next_lane="P00_INVALID",
        include_planned_record_output=False,
        authority_overrides={"runtime_authority": True},
    )
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert first["denial_reasons"] == second["denial_reasons"]
    assert first["denial_reasons"] == [
        "P91_RECOMMENDED_LANE_MISMATCH",
        "P91_RECORD_OUTPUT_MISSING",
        "P91_CREATION_LOCK_VIOLATION",
        "P91_AUTHORITY_LOCK_VIOLATION",
    ]


def test_prerequisite_checks_deterministic(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
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
        "prerequisite_005_creation_locks_false",
        "prerequisite_006_authority_locks_false",
    ]


def test_gate_items_deterministic(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert first["gate_items"] == second["gate_items"]
    assert first["gate_items"] == [
        {
            "gate_item_id": "gate_item_001",
            "lane": "P83",
            "source_creation_plan_path": P91_PATH,
            "planned_record_output_path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
            "planned_record_artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
            "authorization_eligible": True,
            "authorization_granted": False,
            "record_creation_allowed": False,
            "record_created": False,
            "token_created": False,
            "execution_allowed": False,
            "blocking_reason": "CREATION_AUTHORIZATION_GRANT_NOT_PERMITTED_IN_P92",
        }
    ]


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p91(tmp_path, degraded_evidence_inputs=["e2", "e1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p91(tmp_path, inherited_blockers=["b2", "b1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p91(tmp_path, inherited_drift_flags=["d2", "d1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p91(tmp_path, semantic_overlap_flags=["s2", "s1"])
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate.v1.schema.json"
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
        "p83_record_creation_authorization_granted",
        "p83_record_creation_allowed",
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
        schema["properties"]["gate_items"]["items"]["properties"][
            "record_creation_allowed"
        ]["const"]
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


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    first = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    second = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    packet = (
        build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
            repo_root=tmp_path
        )
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate"
        / "latest.json"
    )
    write_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
        out_path, packet
    )
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p91(tmp_path)
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate"
        / "latest.json"
    )
    first = run_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate.run(
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

    artifact = "out/temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate/latest.json"
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
