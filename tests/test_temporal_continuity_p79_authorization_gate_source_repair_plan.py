from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_p79_authorization_gate_source_repair_plan import (
    build_temporal_continuity_p79_authorization_gate_source_repair_plan,
    write_temporal_continuity_p79_authorization_gate_source_repair_plan,
)
from scripts import run_temporal_continuity_p79_authorization_gate_source_repair_plan

P81_PATH = "out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p81(
    root: Path,
    *,
    source_chain_status: str = "SOURCE_CHAIN_BLOCKED",
    recommended_next_lane: str = "P79_AUTHORIZATION_GATE_SOURCE_REPAIR_PLAN",
    not_computable_reasons: list[str] | None = None,
    p78_status: str = "EXECUTION_PLAN_READY",
    p78_observed: bool = True,
    p78_readable: bool = True,
    p78_malformed_json: bool = False,
    p78_blocking_reason: str = "",
    p79_status: str = "NOT_COMPUTABLE",
    p79_observed: bool = True,
    p79_readable: bool = True,
    p79_malformed_json: bool = False,
    p79_blocking_reason: str = "P79_STATUS_NOT_COMPUTABLE",
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    reasons = (
        not_computable_reasons
        if not_computable_reasons is not None
        else ["P79_STATUS_NOT_COMPUTABLE"]
    )
    _write_json(
        root / P81_PATH,
        {
            "artifact_type": "TemporalContinuityAuthorizationRecordPlanSourceStatusAudit.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "source_status_audit_only": True,
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
            "artifact_regeneration_authority": False,
            "execution_authority": False,
            "authorization_authority": False,
            "authorization_record_creation_authority": False,
            "spine_implementation_authority": False,
            "source_p80_path": "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json",
            "source_p80_observed": True,
            "source_p80_readable": True,
            "source_p80_hash": "6" * 64,
            "source_p80_status": "NOT_COMPUTABLE",
            "source_p79_path": "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json",
            "source_p79_observed": p79_observed,
            "source_p79_readable": p79_readable,
            "source_p79_hash": "7" * 64 if p79_observed else "NOT_COMPUTABLE",
            "source_p79_status": p79_status,
            "source_p78_path": "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json",
            "source_p78_observed": p78_observed,
            "source_p78_readable": p78_readable,
            "source_p78_hash": "8" * 64 if p78_observed else "NOT_COMPUTABLE",
            "source_p78_status": p78_status,
            "source_chain_status": source_chain_status,
            "not_computable_reasons": reasons,
            "source_chain_items": [
                {
                    "lane": "P78",
                    "path": "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json",
                    "observed": p78_observed,
                    "readable": p78_readable,
                    "malformed_json": p78_malformed_json,
                    "packet_hash": "8" * 64 if p78_observed else "NOT_COMPUTABLE",
                    "status_field": "execution_plan_status",
                    "status_value": p78_status,
                    "recommended_next_lane": "P79_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_GATE",
                    "blocking_reason": p78_blocking_reason,
                },
                {
                    "lane": "P79",
                    "path": "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json",
                    "observed": p79_observed,
                    "readable": p79_readable,
                    "malformed_json": p79_malformed_json,
                    "packet_hash": "7" * 64 if p79_observed else "NOT_COMPUTABLE",
                    "status_field": "authorization_gate_status",
                    "status_value": p79_status,
                    "recommended_next_lane": "P80_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_RECORD_PLAN",
                    "blocking_reason": p79_blocking_reason,
                },
                {
                    "lane": "P80",
                    "path": "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json",
                    "observed": True,
                    "readable": True,
                    "malformed_json": False,
                    "packet_hash": "6" * 64,
                    "status_field": "authorization_record_plan_status",
                    "status_value": "NOT_COMPUTABLE",
                    "recommended_next_lane": recommended_next_lane,
                    "blocking_reason": "P80_STATUS_NOT_COMPUTABLE",
                },
            ],
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
            "source_status_summary": {
                "source_chain_status": source_chain_status,
                "source_p78_status": p78_status,
                "source_p79_status": p79_status,
                "source_p80_status": "NOT_COMPUTABLE",
                "not_computable_reasons_count": len(reasons),
            },
            "recommended_next_lane": recommended_next_lane,
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "9" * 64,
        },
    )


def test_missing_p81_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_source_repair_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P81_SOURCE_STATUS_AUDIT_REGENERATION"


def test_malformed_p81_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / P81_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_source_repair_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P81_SOURCE_STATUS_AUDIT_REGENERATION"


def test_source_chain_not_blocked_returns_p79_repair_not_required(
    tmp_path: Path,
) -> None:
    _seed_p81(
        tmp_path,
        source_chain_status="SOURCE_CHAIN_READY_FOR_P81_TEMPLATE",
        recommended_next_lane="P81_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE",
        not_computable_reasons=[],
        p79_status="AUTHORIZATION_ELIGIBLE",
        p79_blocking_reason="",
    )
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_source_repair_plan_status"] == "P79_REPAIR_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P81_RECOMMENDED_NEXT_LANE_PASSTHROUGH"


def test_p78_blocking_reasons_route_to_p83_p78_source_repair_plan(
    tmp_path: Path,
) -> None:
    _seed_p81(
        tmp_path,
        not_computable_reasons=["P78_SOURCE_MISSING", "P79_STATUS_NOT_COMPUTABLE"],
        p78_status="NOT_COMPUTABLE",
        p78_observed=False,
        p78_readable=False,
        p78_blocking_reason="P78_SOURCE_MISSING",
    )
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_source_repair_plan_status"] == "P79_REPAIR_PLAN_BLOCKED_BY_P78"
    assert (
        packet["recommended_next_lane"]
        == "P83_TEMPORAL_CONTINUITY_P78_EXECUTION_PLAN_SOURCE_REPAIR_PLAN"
    )


def test_p79_source_missing_routes_to_regeneration_plan(tmp_path: Path) -> None:
    _seed_p81(
        tmp_path,
        not_computable_reasons=["P79_SOURCE_MISSING"],
        p79_status="NOT_COMPUTABLE",
        p79_observed=False,
        p79_readable=False,
        p79_blocking_reason="P79_SOURCE_MISSING",
    )
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["p79_source_repair_plan_status"] == "P79_REPAIR_PLAN_READY"
    assert (
        packet["recommended_next_lane"]
        == "P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN"
    )


def test_p79_source_unreadable_routes_to_source_repair_execution_plan(
    tmp_path: Path,
) -> None:
    _seed_p81(
        tmp_path,
        not_computable_reasons=["P79_SOURCE_UNREADABLE"],
        p79_readable=False,
        p79_blocking_reason="P79_SOURCE_UNREADABLE",
    )
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert (
        packet["recommended_next_lane"]
        == "P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_SOURCE_REPAIR_EXECUTION_PLAN"
    )


def test_p79_source_malformed_json_routes_to_source_repair_execution_plan(
    tmp_path: Path,
) -> None:
    _seed_p81(
        tmp_path,
        not_computable_reasons=["P79_SOURCE_MALFORMED_JSON"],
        p79_malformed_json=True,
        p79_blocking_reason="P79_SOURCE_MALFORMED_JSON",
    )
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert (
        packet["recommended_next_lane"]
        == "P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_SOURCE_REPAIR_EXECUTION_PLAN"
    )


def test_p79_status_not_computable_routes_to_status_repair_plan(
    tmp_path: Path,
) -> None:
    _seed_p81(tmp_path, not_computable_reasons=["P79_STATUS_NOT_COMPUTABLE"])
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert (
        packet["recommended_next_lane"]
        == "P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_STATUS_REPAIR_PLAN"
    )


def test_p79_not_authorization_eligible_routes_to_eligibility_repair_plan(
    tmp_path: Path,
) -> None:
    _seed_p81(
        tmp_path,
        not_computable_reasons=["P79_NOT_AUTHORIZATION_ELIGIBLE"],
        p79_status="AUTHORIZATION_BLOCKED",
        p79_blocking_reason="P79_NOT_AUTHORIZATION_ELIGIBLE",
    )
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert (
        packet["recommended_next_lane"]
        == "P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_ELIGIBILITY_REPAIR_PLAN"
    )


def test_repair_execution_allowed_always_false(tmp_path: Path) -> None:
    _seed_p81(tmp_path, not_computable_reasons=["P79_STATUS_NOT_COMPUTABLE"])
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert all(item["repair_execution_allowed"] is False for item in packet["repair_items"])


def test_repair_authority_always_false(tmp_path: Path) -> None:
    _seed_p81(tmp_path, not_computable_reasons=["P79_STATUS_NOT_COMPUTABLE"])
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["repair_authority"] is False


def test_repair_execution_authority_always_false(tmp_path: Path) -> None:
    _seed_p81(tmp_path, not_computable_reasons=["P79_STATUS_NOT_COMPUTABLE"])
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["repair_execution_authority"] is False


def test_repair_items_are_deterministic(tmp_path: Path) -> None:
    _seed_p81(
        tmp_path,
        not_computable_reasons=[
            "P79_STATUS_NOT_COMPUTABLE",
            "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
        ],
    )
    first = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert first["repair_items"] == second["repair_items"]


def test_p79_failure_modes_are_deterministic(tmp_path: Path) -> None:
    _seed_p81(
        tmp_path,
        not_computable_reasons=[
            "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
            "P79_NOT_AUTHORIZATION_ELIGIBLE",
        ],
        p79_status="AUTHORIZATION_BLOCKED",
        p79_blocking_reason="P79_NOT_AUTHORIZATION_ELIGIBLE",
    )
    first = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert first["p79_failure_modes"] == second["p79_failure_modes"]


def test_blocked_repair_reasons_are_deterministic(tmp_path: Path) -> None:
    _seed_p81(
        tmp_path,
        not_computable_reasons=[
            "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
            "P79_STATUS_NOT_COMPUTABLE",
        ],
    )
    first = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert first["blocked_repair_reasons"] == second["blocked_repair_reasons"]


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p81(tmp_path, degraded_evidence_inputs=["e2", "e1"])
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p81(tmp_path, inherited_blockers=["b2", "b1"])
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p81(tmp_path, inherited_drift_flags=["d2", "d1"])
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p81(tmp_path, semantic_overlap_flags=["s2", "s1"])
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_p79_authorization_gate_source_repair_plan.v1.schema.json"
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
        schema["properties"]["repair_items"]["items"]["properties"]["repair_execution_allowed"]["const"]
        is False
    )


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p81(tmp_path, not_computable_reasons=["P79_STATUS_NOT_COMPUTABLE"])
    first = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p81(tmp_path, not_computable_reasons=["P79_STATUS_NOT_COMPUTABLE"])
    packet = build_temporal_continuity_p79_authorization_gate_source_repair_plan(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p79_authorization_gate_source_repair_plan"
        / "latest.json"
    )
    write_temporal_continuity_p79_authorization_gate_source_repair_plan(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p81(tmp_path, not_computable_reasons=["P79_STATUS_NOT_COMPUTABLE"])
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_p79_authorization_gate_source_repair_plan"
        / "latest.json"
    )
    first = run_temporal_continuity_p79_authorization_gate_source_repair_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_p79_authorization_gate_source_repair_plan.run(
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

    artifact = (
        "out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json"
    )
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
