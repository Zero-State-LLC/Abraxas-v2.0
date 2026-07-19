from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p79_authorization_gate_status_repair_plan import (
    build_temporal_continuity_p79_authorization_gate_status_repair_plan,
    write_temporal_continuity_p79_authorization_gate_status_repair_plan,
)
from scripts.temporal import run_temporal_continuity_p79_authorization_gate_status_repair_plan

P82_PATH = (
    "out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p82(
    root: Path,
    *,
    p79_source_repair_plan_status: str = "P79_REPAIR_NOT_REQUIRED",
    recommended_next_lane: str = "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
    p79_failure_modes: list[str] | None = None,
    p79_source_path: str = (
        "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json"
    ),
    p79_source_status: str = "NOT_COMPUTABLE",
    repair_items: list[dict[str, object]] | None = None,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    _write_json(
        root / P82_PATH,
        {
            "artifact_type": "TemporalContinuityP79AuthorizationGateSourceRepairPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "source_repair_plan_only": True,
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
            "source_p81_audit_path": "out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json",
            "source_p81_audit_observed": True,
            "source_p81_audit_readable": True,
            "source_p81_audit_hash": "a" * 64,
            "source_p81_chain_status": "SOURCE_CHAIN_BLOCKED",
            "source_p81_recommended_next_lane": recommended_next_lane,
            "p79_source_repair_plan_status": p79_source_repair_plan_status,
            "p79_source_status": p79_source_status,
            "p79_source_path": p79_source_path,
            "p79_failure_modes": p79_failure_modes if p79_failure_modes is not None else [],
            "repair_items": repair_items if repair_items is not None else [],
            "blocked_repair_reasons": [],
            "prerequisite_sources": [],
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
            "repair_strategy_summary": {
                "source_chain_status": "SOURCE_CHAIN_BLOCKED",
                "repair_items_count": 0,
                "repair_strategies": [],
                "blocked_repair_reasons_count": 0,
                "prerequisite_sources_count": 0,
            },
            "recommended_next_lane": recommended_next_lane,
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "b" * 64,
        },
    )


# ---------------------------------------------------------------------------
# Rule 1 — missing / malformed P82 source
# ---------------------------------------------------------------------------


def test_missing_p82_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_status_repair_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P82_P79_SOURCE_REPAIR_PLAN_REGENERATION"


def test_malformed_p82_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P82_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad json", encoding="utf-8")
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_status_repair_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P82_P79_SOURCE_REPAIR_PLAN_REGENERATION"


# ---------------------------------------------------------------------------
# Rule 2 — P82 NOT_COMPUTABLE
# ---------------------------------------------------------------------------


def test_p82_not_computable_blocks_p83_recommends_p82_regeneration(
    tmp_path: Path,
) -> None:
    _seed_p82(tmp_path, p79_source_repair_plan_status="NOT_COMPUTABLE")
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_status_repair_plan_status"] == "P79_STATUS_REPAIR_BLOCKED_BY_P82"
    assert packet["recommended_next_lane"] == "P82_P79_SOURCE_REPAIR_PLAN_REGENERATION"


# ---------------------------------------------------------------------------
# Rule 3 — P82 blocked by P78
# ---------------------------------------------------------------------------


def test_p82_blocked_by_p78_routes_to_p84_p78_source_repair_plan(
    tmp_path: Path,
) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_BLOCKED_BY_P78",
        p79_failure_modes=["P78_SOURCE_BLOCKING_P79"],
        repair_items=[
            {
                "repair_item_id": "repair_item_p78_001",
                "lane": "P78",
                "path": "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "status_field": "execution_plan_status",
                "status_value": "NOT_COMPUTABLE",
                "failure_mode": "P78_SOURCE_BLOCKING_P79",
                "repair_strategy": "REGENERATE_P78_EXECUTION_PLAN_FIRST",
                "prerequisite_paths": [],
                "repair_execution_allowed": False,
                "blocking_reason": "P78_SOURCE_MISSING",
            }
        ],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_status_repair_plan_status"] == "P79_STATUS_REPAIR_BLOCKED_BY_P82"
    assert (
        packet["recommended_next_lane"]
        == "P84_TEMPORAL_CONTINUITY_P78_EXECUTION_PLAN_SOURCE_REPAIR_PLAN"
    )


# ---------------------------------------------------------------------------
# Rule 4 — P79_STATUS_NOT_COMPUTABLE
# ---------------------------------------------------------------------------


def test_p79_status_not_computable_routes_to_p84_status_repair_execution_plan(
    tmp_path: Path,
) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
        p79_source_status="NOT_COMPUTABLE",
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_status_repair_plan_status"] == "P79_STATUS_REPAIR_PLAN_READY"
    assert (
        packet["recommended_next_lane"]
        == "P84_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_STATUS_REPAIR_EXECUTION_PLAN"
    )


# ---------------------------------------------------------------------------
# Rule 5 — P79_NOT_AUTHORIZATION_ELIGIBLE
# ---------------------------------------------------------------------------


def test_p79_not_authorization_eligible_routes_to_p84_eligibility_repair_plan(
    tmp_path: Path,
) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_NOT_AUTHORIZATION_ELIGIBLE"],
        p79_source_status="AUTHORIZATION_BLOCKED",
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_status_repair_plan_status"] == "P79_STATUS_REPAIR_PLAN_READY"
    assert (
        packet["recommended_next_lane"]
        == "P84_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_ELIGIBILITY_REPAIR_PLAN"
    )


# ---------------------------------------------------------------------------
# Rule 6 — P79_SOURCE_MISSING
# ---------------------------------------------------------------------------


def test_p79_source_missing_routes_to_p84_regeneration_plan(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_SOURCE_MISSING"],
        p79_source_status="NOT_COMPUTABLE",
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_status_repair_plan_status"] == "P79_STATUS_REPAIR_BLOCKED_BY_P82"
    assert (
        packet["recommended_next_lane"]
        == "P84_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN"
    )


# ---------------------------------------------------------------------------
# Rule 7 — P79_SOURCE_UNREADABLE / P79_SOURCE_MALFORMED_JSON
# ---------------------------------------------------------------------------


def test_p79_source_unreadable_routes_to_p84_source_repair_execution_plan(
    tmp_path: Path,
) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_SOURCE_UNREADABLE"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_status_repair_plan_status"] == "P79_STATUS_REPAIR_BLOCKED_BY_P82"
    assert (
        packet["recommended_next_lane"]
        == "P84_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_SOURCE_REPAIR_EXECUTION_PLAN"
    )


def test_p79_source_malformed_json_routes_to_p84_source_repair_execution_plan(
    tmp_path: Path,
) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_SOURCE_MALFORMED_JSON"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_status_repair_plan_status"] == "P79_STATUS_REPAIR_BLOCKED_BY_P82"
    assert (
        packet["recommended_next_lane"]
        == "P84_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_SOURCE_REPAIR_EXECUTION_PLAN"
    )


# ---------------------------------------------------------------------------
# Rule 8 — P79_REPAIR_NOT_REQUIRED passthrough
# ---------------------------------------------------------------------------


def test_p79_repair_not_required_passes_through_p82_recommended_lane(
    tmp_path: Path,
) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_NOT_REQUIRED",
        recommended_next_lane="P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
        p79_failure_modes=[],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_status_repair_plan_status"] == "P79_STATUS_REPAIR_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION"


# ---------------------------------------------------------------------------
# Governance invariants
# ---------------------------------------------------------------------------


def test_repair_execution_allowed_always_false(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert all(
        item["repair_execution_allowed"] is False
        for item in packet["status_repair_items"]
    )


def test_repair_authority_always_false(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["repair_authority"] is False


def test_repair_execution_authority_always_false(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["repair_execution_authority"] is False


# ---------------------------------------------------------------------------
# Corrected status relationship
# ---------------------------------------------------------------------------


def test_corrected_status_relationship_includes_expected_p78_to_p79_mappings(
    tmp_path: Path,
) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
        repair_items=[
            {
                "repair_item_id": "repair_item_p78_001",
                "lane": "P78",
                "path": "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "status_field": "execution_plan_status",
                "status_value": "EXECUTION_PLAN_READY",
                "failure_mode": "P79_STATUS_NOT_COMPUTABLE",
                "repair_strategy": "REPAIR_P79_SOURCE_SCHEMA_OR_STATUS",
                "prerequisite_paths": [],
                "repair_execution_allowed": False,
                "blocking_reason": "P79_STATUS_NOT_COMPUTABLE",
            }
        ],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    rel = packet["corrected_status_relationship"]
    assert rel["source_p78_status"] == "EXECUTION_PLAN_READY"
    assert rel["expected_p79_status_if_ready"] == "AUTHORIZATION_ELIGIBLE"
    assert rel["expected_p80_status_after_p79_repair"] == "AUTHORIZATION_RECORD_PLAN_READY"


def test_corrected_status_relationship_p78_blocked_maps_p79_authorization_blocked(
    tmp_path: Path,
) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
        repair_items=[
            {
                "repair_item_id": "repair_item_p78_001",
                "lane": "P78",
                "path": "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "status_field": "execution_plan_status",
                "status_value": "EXECUTION_PLAN_BLOCKED",
                "failure_mode": "P79_STATUS_NOT_COMPUTABLE",
                "repair_strategy": "REPAIR_P79_SOURCE_SCHEMA_OR_STATUS",
                "prerequisite_paths": [],
                "repair_execution_allowed": False,
                "blocking_reason": "P79_STATUS_NOT_COMPUTABLE",
            }
        ],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    rel = packet["corrected_status_relationship"]
    assert rel["source_p78_status"] == "EXECUTION_PLAN_BLOCKED"
    assert rel["expected_p79_status_if_ready"] == "AUTHORIZATION_BLOCKED"


# ---------------------------------------------------------------------------
# rerun_sequence informational only
# ---------------------------------------------------------------------------


def test_rerun_sequence_present_when_repair_plan_ready(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    rerun_seq = packet["corrected_status_relationship"]["rerun_sequence"]
    assert isinstance(rerun_seq, list)
    assert len(rerun_seq) > 0


def test_rerun_sequence_empty_when_not_repair_plan_ready(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_NOT_REQUIRED",
        p79_failure_modes=[],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    rerun_seq = packet["corrected_status_relationship"]["rerun_sequence"]
    assert rerun_seq == []


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_status_repair_items_deterministic(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
    )
    first = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert first["status_repair_items"] == second["status_repair_items"]


def test_status_field_expectations_deterministic(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
    )
    first = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert first["status_field_expectations"] == second["status_field_expectations"]


# ---------------------------------------------------------------------------
# Inherited flags preserved exactly
# ---------------------------------------------------------------------------


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
        degraded_evidence_inputs=["e2", "e1"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
        inherited_blockers=["b2", "b1"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
        inherited_drift_flags=["d2", "d1"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
        semantic_overlap_flags=["s2", "s1"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


# ---------------------------------------------------------------------------
# Schema locks
# ---------------------------------------------------------------------------


def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p79_authorization_gate_status_repair_plan.v1.schema.json"
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
    assert (
        schema["properties"]["status_repair_items"]["items"]["properties"][
            "repair_execution_allowed"
        ]["const"]
        is False
    )


# ---------------------------------------------------------------------------
# Packet hash determinism
# ---------------------------------------------------------------------------


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
    )
    first = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


# ---------------------------------------------------------------------------
# Writer — canonical JSON with final newline
# ---------------------------------------------------------------------------


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
    )
    packet = build_temporal_continuity_p79_authorization_gate_status_repair_plan(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p79_authorization_gate_status_repair_plan"
        / "latest.json"
    )
    write_temporal_continuity_p79_authorization_gate_status_repair_plan(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


# ---------------------------------------------------------------------------
# Runner writes expected output path
# ---------------------------------------------------------------------------


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p82(
        tmp_path,
        p79_source_repair_plan_status="P79_REPAIR_PLAN_READY",
        p79_failure_modes=["P79_STATUS_NOT_COMPUTABLE"],
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p79_authorization_gate_status_repair_plan"
        / "latest.json"
    )
    first = run_temporal_continuity_p79_authorization_gate_status_repair_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_p79_authorization_gate_status_repair_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


# ---------------------------------------------------------------------------
# Artifact registry
# ---------------------------------------------------------------------------


def test_artifact_registry_classifies_output_as_derived_optional() -> None:
    from core.generated_artifact_registry import (  # type: ignore[attr-defined]
        _DERIVED_OPTIONAL_ARTIFACTS,
        build_generated_artifact_registry,
        list_ci_drift_artifact_paths,
    )

    artifact = (
        "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
    )
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
