from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.temporal_continuity_missing_evidence_restoration_plan import (
    build_temporal_continuity_missing_evidence_restoration_plan,
    write_temporal_continuity_missing_evidence_restoration_plan,
)
from scripts import run_temporal_continuity_missing_evidence_restoration_plan


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _seed_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_p73(
    root: Path,
    *,
    missing_paths: list[str] | None = None,
    unreadable_paths: list[str] | None = None,
    degraded_inputs: list[str] | None = None,
    blockers: list[str] | None = None,
    drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
    evidence_items: list[dict[str, object]] | None = None,
    evidence_index_status: str = "MISSING_EVIDENCE_INDEXED",
) -> None:
    default_evidence_items = [
        {
            "path": "out/audit/temporal_coherence_chain_001.latest.json",
            "group_id": "temporal_coherence_chain",
            "evidence_role": "missing_path",
            "inherited_status": "PARTIAL",
            "observed": False,
            "readable": False,
            "malformed_json": False,
            "source_category": "audit",
        },
        {
            "path": "out/projections/coherence_field_operator_surface_001.latest.json",
            "group_id": "temporal_coherence_chain",
            "evidence_role": "missing_path",
            "inherited_status": "PARTIAL",
            "observed": False,
            "readable": False,
            "malformed_json": False,
            "source_category": "projection",
        },
        {
            "path": "scripts/run_temporal_coherence_chain.py",
            "group_id": "temporal_coherence_chain",
            "evidence_role": "observed_path",
            "inherited_status": "PARTIAL",
            "observed": True,
            "readable": True,
            "malformed_json": False,
            "source_category": "script",
        },
        {
            "path": "out/projections/temporal_topology_cartography_001.latest.json",
            "group_id": "temporal_coherence_chain",
            "evidence_role": "observed_path",
            "inherited_status": "PARTIAL",
            "observed": True,
            "readable": True,
            "malformed_json": False,
            "source_category": "projection",
        },
        {
            "path": "out/audit/archive_ready.json",
            "group_id": "archive_chain",
            "evidence_role": "observed_path",
            "inherited_status": "DEGRADED",
            "observed": True,
            "readable": True,
            "malformed_json": False,
            "source_category": "audit",
        },
    ]

    _write_json(
        root / "out" / "temporal_continuity_evidence_index" / "latest.json",
        {
            "artifact_type": "TemporalContinuityEvidenceIndex.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "production_activation": False,
            "canon_promotion": False,
            "forecast_influence": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "repair_authority": False,
            "evidence_generation_authority": False,
            "spine_implementation_authority": False,
            "source_readiness_audit_path": "out/temporal_continuity_binder_readiness_audit/latest.json",
            "source_readiness_audit_observed": True,
            "source_readiness_audit_hash": "abc",
            "source_readiness_status": "READY_WITH_DEGRADED_EVIDENCE",
            "source_recommended_next_lane": "P73_TEMPORAL_CONTINUITY_EVIDENCE_INDEX",
            "evidence_index_status": evidence_index_status,
            "evidence_items": evidence_items if evidence_items is not None else default_evidence_items,
            "observed_evidence_paths": [
                "scripts/run_temporal_coherence_chain.py",
                "out/projections/temporal_topology_cartography_001.latest.json",
                "out/audit/archive_ready.json",
            ],
            "missing_evidence_paths": missing_paths
            if missing_paths is not None
            else [
                "out/audit/temporal_coherence_chain_001.latest.json",
                "out/projections/coherence_field_operator_surface_001.latest.json",
            ],
            "unreadable_evidence_paths": unreadable_paths if unreadable_paths is not None else [],
            "degraded_evidence_inputs": degraded_inputs
            if degraded_inputs is not None
            else ["archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"],
            "inherited_blockers": blockers
            if blockers is not None
            else ["temporal_coherence_chain:missing:out/audit/temporal_coherence_chain_001.latest.json"],
            "inherited_drift_flags": drift_flags
            if drift_flags is not None
            else ["GROUP_TEMPORAL_COHERENCE_CHAIN_PARTIAL"],
            "semantic_overlap_flags": semantic_overlap_flags
            if semantic_overlap_flags is not None
            else ["SEMANTIC_OVERLAP_LATEST_JSON:out/audit/archive_ready.json|out/projections/temporal_topology_cartography_001.latest.json"],
            "group_evidence_summary": [],
            "recommended_next_lane": "P74_TEMPORAL_CONTINUITY_MISSING_EVIDENCE_RESTORATION_PLAN",
            "recommended_next_lane_reason": "missing indexed",
            "denied_authority": [],
            "packet_hash": "0" * 64,
        },
    )


def _find_item(packet: dict[str, object], path: str) -> dict[str, object]:
    return next(item for item in packet["restoration_items"] if item["path"] == path)


def test_missing_p73_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["restoration_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P73_EVIDENCE_INDEX_REGENERATION"


def test_malformed_p73_source_returns_not_computable(tmp_path: Path) -> None:
    p73 = tmp_path / "out" / "temporal_continuity_evidence_index" / "latest.json"
    p73.parent.mkdir(parents=True, exist_ok=True)
    p73.write_text("{ bad json", encoding="utf-8")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["restoration_plan_status"] == "NOT_COMPUTABLE"


def test_missing_paths_become_restoration_items(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    paths = {item["path"] for item in packet["restoration_items"]}
    assert "out/audit/temporal_coherence_chain_001.latest.json" in paths


def test_unreadable_paths_become_restoration_items(tmp_path: Path) -> None:
    unreadable = "out/projections/coherence_field_operator_surface_001.latest.json"
    _seed_p73(tmp_path, missing_paths=[], unreadable_paths=[unreadable])
    _seed_file(tmp_path / unreadable, "{bad json")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    item = _find_item(packet, unreadable)
    assert item["restoration_strategy"] == "UNREADABLE_SOURCE_REPAIR_PLAN"


def test_generator_inference_requires_existing_script(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    item = _find_item(packet, "out/audit/temporal_coherence_chain_001.latest.json")
    assert item["likely_generator_script"] == "scripts/run_temporal_coherence_chain.py"


def test_missing_generator_script_becomes_script_discovery(tmp_path: Path) -> None:
    _seed_p73(
        tmp_path,
        missing_paths=["out/audit/no_generator_surface_001.latest.json"],
        evidence_items=[
            {
                "path": "out/audit/no_generator_surface_001.latest.json",
                "group_id": "unknown_chain",
                "evidence_role": "missing_path",
                "inherited_status": "MISSING",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "audit",
            }
        ],
    )
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    item = _find_item(packet, "out/audit/no_generator_surface_001.latest.json")
    assert item["restoration_strategy"] == "SCRIPT_DISCOVERY_REQUIRED"


def test_temporal_coherence_missing_path_can_require_upstream_inputs(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    _seed_file(tmp_path / "scripts" / "run_coherence_field_operator_surface.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    item = _find_item(packet, "out/projections/coherence_field_operator_surface_001.latest.json")
    assert item["restoration_strategy"] == "UPSTREAM_INPUT_REQUIRED"


def test_existing_readable_paths_become_restoration_not_required(tmp_path: Path) -> None:
    _seed_p73(tmp_path, missing_paths=[])
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    item = _find_item(packet, "out/audit/archive_ready.json")
    assert item["restoration_strategy"] == "RESTORATION_NOT_REQUIRED"


def test_safe_to_restore_always_false(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert all(item["safe_to_restore"] is False for item in packet["restoration_items"])


def test_degraded_inputs_preserved_exactly(tmp_path: Path) -> None:
    marker = "archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"
    _seed_p73(tmp_path, degraded_inputs=[marker])
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["degraded_evidence_inputs"] == [marker]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    marker = "temporal_coherence_chain:missing:out/audit/temporal_coherence_chain_001.latest.json"
    _seed_p73(tmp_path, blockers=[marker])
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["inherited_blockers"] == [marker]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    marker = "GROUP_TEMPORAL_COHERENCE_CHAIN_PARTIAL"
    _seed_p73(tmp_path, drift_flags=[marker])
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["inherited_drift_flags"] == [marker]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    marker = "SEMANTIC_OVERLAP_LATEST_JSON:x|y"
    _seed_p73(tmp_path, semantic_overlap_flags=[marker])
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["semantic_overlap_flags"] == [marker]


def test_restoration_items_sorted_deterministically(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    ordering = [(i["path"], i["group_id"], i["restoration_strategy"]) for i in packet["restoration_items"]]
    assert ordering == sorted(ordering, key=lambda item: (item[0], item[1], item[2]))


def test_restoration_strategy_summary_deterministic(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    first = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    second = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert first["restoration_strategy_summary"] == second["restoration_strategy_summary"]


def test_script_discovery_recommends_generator_discovery_lane(tmp_path: Path) -> None:
    _seed_p73(
        tmp_path,
        missing_paths=["out/audit/no_generator_surface_001.latest.json"],
        evidence_items=[
            {
                "path": "out/audit/no_generator_surface_001.latest.json",
                "group_id": "unknown_chain",
                "evidence_role": "missing_path",
                "inherited_status": "MISSING",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "audit",
            }
        ],
        degraded_inputs=[],
    )
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_GENERATOR_DISCOVERY_PLAN"


def test_upstream_required_recommends_upstream_restoration_lane(tmp_path: Path) -> None:
    _seed_p73(tmp_path, degraded_inputs=[])
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")
    _seed_file(tmp_path / "scripts" / "run_coherence_field_operator_surface.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN"


def test_all_generator_exists_recommends_artifact_regeneration_dry_run(tmp_path: Path) -> None:
    _seed_p73(
        tmp_path,
        missing_paths=["out/audit/temporal_coherence_chain_001.latest.json"],
        evidence_items=[
            {
                "path": "out/audit/temporal_coherence_chain_001.latest.json",
                "group_id": "temporal_coherence_chain",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "audit",
            }
        ],
        degraded_inputs=[],
    )
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN"


def test_unreadable_evidence_recommends_unreadable_repair_plan(tmp_path: Path) -> None:
    unreadable = "out/projections/coherence_field_operator_surface_001.latest.json"
    _seed_p73(tmp_path, missing_paths=[], unreadable_paths=[unreadable], degraded_inputs=[])
    _seed_file(tmp_path / unreadable, "{bad json")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_UNREADABLE_EVIDENCE_REPAIR_PLAN"


def test_no_restoration_but_degraded_recommends_degraded_repair(tmp_path: Path) -> None:
    _seed_p73(
        tmp_path,
        missing_paths=[],
        unreadable_paths=[],
        evidence_items=[
            {
                "path": "out/audit/archive_ready.json",
                "group_id": "archive_chain",
                "evidence_role": "observed_path",
                "inherited_status": "DEGRADED",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "source_category": "audit",
            }
        ],
    )
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["restoration_plan_status"] == "RESTORATION_NOT_REQUIRED"
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"


def test_no_restoration_and_no_degraded_recommends_spine_planning_gate(tmp_path: Path) -> None:
    _seed_p73(
        tmp_path,
        missing_paths=[],
        unreadable_paths=[],
        degraded_inputs=[],
        evidence_items=[
            {
                "path": "out/audit/archive_ready.json",
                "group_id": "archive_chain",
                "evidence_role": "observed_path",
                "inherited_status": "READY",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "source_category": "audit",
            }
        ],
    )
    _seed_file(tmp_path / "out" / "audit" / "archive_ready.json", '{"ok":true}\n')
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE"


def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path(
            "contracts/canon/temporal_continuity_missing_evidence_restoration_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    for field in (
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "evidence_generation_authority",
        "restoration_execution_authority",
        "spine_implementation_authority",
    ):
        assert schema["properties"][field]["const"] is False


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    first = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    second = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_missing_evidence_restoration_plan" / "latest.json"
    write_temporal_continuity_missing_evidence_restoration_plan(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_missing_evidence_restoration_plan" / "latest.json"
    first = run_temporal_continuity_missing_evidence_restoration_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_missing_evidence_restoration_plan.run(
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_artifact_registry_classifies_as_derived_optional() -> None:
    from core.generated_artifact_registry import (  # type: ignore[attr-defined]
        _CI_DRIFT_ENFORCED_CLASSES,
        _DERIVED_OPTIONAL_ARTIFACTS,
    )

    assert "out/temporal_continuity_missing_evidence_restoration_plan/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "DERIVED_OPTIONAL" not in _CI_DRIFT_ENFORCED_CLASSES


@pytest.mark.parametrize(
    "field",
    [
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "evidence_generation_authority",
        "restoration_execution_authority",
        "spine_implementation_authority",
    ],
)
def test_governance_fields_false_in_packet(tmp_path: Path, field: str) -> None:
    _seed_p73(tmp_path)
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet[field] is False
