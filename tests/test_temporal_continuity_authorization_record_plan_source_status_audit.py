from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_authorization_record_plan_source_status_audit import (
    build_temporal_continuity_authorization_record_plan_source_status_audit,
    write_temporal_continuity_authorization_record_plan_source_status_audit,
)
from scripts.temporal import run_temporal_continuity_authorization_record_plan_source_status_audit


P78_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json"
)
P79_PATH = "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json"
P80_PATH = "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p78(root: Path, *, status: str = "EXECUTION_PLAN_READY") -> None:
    _write_json(
        root / P78_PATH,
        {
            "artifact_type": "TemporalContinuityUpstreamInputRegenerationExecutionPlan.v1",
            "execution_plan_status": status,
            "recommended_next_lane": "P79_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_GATE",
            "packet_hash": "8" * 64,
        },
    )


def _seed_p79(root: Path, *, status: str = "AUTHORIZATION_ELIGIBLE") -> None:
    _write_json(
        root / P79_PATH,
        {
            "artifact_type": "TemporalContinuityUpstreamInputRegenerationAuthorizationGate.v1",
            "authorization_gate_status": status,
            "recommended_next_lane": "P80_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_RECORD_PLAN",
            "packet_hash": "7" * 64,
        },
    )


def _seed_p80(
    root: Path,
    *,
    status: str = "NOT_COMPUTABLE",
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    _write_json(
        root / P80_PATH,
        {
            "artifact_type": "TemporalContinuityUpstreamInputRegenerationAuthorizationRecordPlan.v1",
            "authorization_record_plan_status": status,
            "recommended_next_lane": "P81_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE",
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
            "packet_hash": "6" * 64,
        },
    )


def test_missing_p80_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["source_chain_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION"
    assert "P80_SOURCE_MISSING" in packet["not_computable_reasons"]


def test_malformed_p80_source_returns_not_computable(tmp_path: Path) -> None:
    p80_path = tmp_path / P80_PATH
    p80_path.parent.mkdir(parents=True, exist_ok=True)
    p80_path.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["source_chain_status"] == "NOT_COMPUTABLE"
    assert "P80_SOURCE_MALFORMED_JSON" in packet["not_computable_reasons"]


def test_missing_p79_source_produces_source_chain_blocked(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="NOT_COMPUTABLE")
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["source_chain_status"] == "SOURCE_CHAIN_BLOCKED"
    assert packet["recommended_next_lane"] == "P79_AUTHORIZATION_GATE_REGENERATION"


def test_malformed_p79_source_produces_source_chain_blocked(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="NOT_COMPUTABLE")
    p79_path = tmp_path / P79_PATH
    p79_path.parent.mkdir(parents=True, exist_ok=True)
    p79_path.write_text("{bad", encoding="utf-8")
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["source_chain_status"] == "SOURCE_CHAIN_BLOCKED"
    assert "P79_SOURCE_MALFORMED_JSON" in packet["not_computable_reasons"]


def test_p79_status_not_computable_produces_source_chain_blocked(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="NOT_COMPUTABLE")
    _seed_p79(tmp_path, status="NOT_COMPUTABLE")
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["source_chain_status"] == "SOURCE_CHAIN_BLOCKED"
    assert (
        packet["recommended_next_lane"] == "P79_AUTHORIZATION_GATE_SOURCE_REPAIR_PLAN"
    )


def test_p79_eligible_plus_p80_not_computable_recommends_p80_regeneration(
    tmp_path: Path,
) -> None:
    _seed_p79(tmp_path, status="AUTHORIZATION_ELIGIBLE")
    _seed_p80(tmp_path, status="NOT_COMPUTABLE")
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["source_chain_status"] == "SOURCE_CHAIN_READY_FOR_P80_REGENERATION"
    assert packet["recommended_next_lane"] == "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION"


def test_p80_ready_recommends_operator_template_lane(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="AUTHORIZATION_RECORD_PLAN_READY")
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["source_chain_status"] == "SOURCE_CHAIN_READY_FOR_P81_TEMPLATE"
    assert (
        packet["recommended_next_lane"]
        == "P81_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE"
    )


def test_p80_blocked_recommends_blocker_repair_lane(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="AUTHORIZATION_RECORD_PLAN_BLOCKED")
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["source_chain_status"] == "SOURCE_CHAIN_BLOCKED"
    assert (
        packet["recommended_next_lane"]
        == "P81_TEMPORAL_CONTINUITY_AUTHORIZATION_BLOCKER_REPAIR_PLAN"
    )


def test_p80_not_required_recommends_not_required_routing_audit(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="AUTHORIZATION_RECORD_NOT_REQUIRED")
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["source_chain_status"] == "SOURCE_CHAIN_READY_FOR_P81_TEMPLATE"
    assert (
        packet["recommended_next_lane"]
        == "P81_TEMPORAL_CONTINUITY_AUTHORIZATION_NOT_REQUIRED_ROUTING_AUDIT"
    )


def test_source_chain_items_are_in_deterministic_order(tmp_path: Path) -> None:
    _seed_p78(tmp_path, status="EXECUTION_PLAN_READY")
    _seed_p79(tmp_path, status="AUTHORIZATION_ELIGIBLE")
    _seed_p80(tmp_path, status="NOT_COMPUTABLE")
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert [item["lane"] for item in packet["source_chain_items"]] == ["P78", "P79", "P80"]


def test_not_computable_reasons_are_deterministic(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="NOT_COMPUTABLE")
    _seed_p79(tmp_path, status="NOT_COMPUTABLE")
    first = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert first["not_computable_reasons"] == second["not_computable_reasons"]


def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="AUTHORIZATION_RECORD_PLAN_BLOCKED", degraded_evidence_inputs=["e2", "e1"])
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["degraded_evidence_inputs"] == ["e2", "e1"]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="AUTHORIZATION_RECORD_PLAN_BLOCKED", inherited_blockers=["b2", "b1"])
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["inherited_blockers"] == ["b2", "b1"]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="AUTHORIZATION_RECORD_PLAN_BLOCKED", inherited_drift_flags=["d2", "d1"])
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["inherited_drift_flags"] == ["d2", "d1"]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="AUTHORIZATION_RECORD_PLAN_BLOCKED", semantic_overlap_flags=["s2", "s1"])
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert packet["semantic_overlap_flags"] == ["s2", "s1"]


def test_schema_locks_all_authority_fields_false() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "canon"
        / "temporal_continuity_authorization_record_plan_source_status_audit.v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
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
        "artifact_regeneration_authority",
        "execution_authority",
        "authorization_authority",
        "authorization_record_creation_authority",
        "spine_implementation_authority",
    ):
        assert schema["properties"][field]["const"] is False, field


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p79(tmp_path, status="AUTHORIZATION_ELIGIBLE")
    _seed_p80(tmp_path, status="NOT_COMPUTABLE")
    first = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    assert first["packet_hash"] == second["packet_hash"]
    assert len(first["packet_hash"]) == 64


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="AUTHORIZATION_RECORD_PLAN_READY")
    packet = build_temporal_continuity_authorization_record_plan_source_status_audit(
        repo_root=tmp_path
    )
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_authorization_record_plan_source_status_audit"
        / "latest.json"
    )
    write_temporal_continuity_authorization_record_plan_source_status_audit(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p80(tmp_path, status="AUTHORIZATION_RECORD_PLAN_READY")
    out_path = (
        tmp_path
        / "out"
        / "temporal_continuity_authorization_record_plan_source_status_audit"
        / "latest.json"
    )
    first = run_temporal_continuity_authorization_record_plan_source_status_audit.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_authorization_record_plan_source_status_audit.run(
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
        "out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json"
    )
    assert artifact in _DERIVED_OPTIONAL_ARTIFACTS
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    assert artifact not in list_ci_drift_artifact_paths(registry)
