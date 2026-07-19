from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_missing_evidence_restoration_plan import (
    build_temporal_continuity_missing_evidence_restoration_plan,
    write_temporal_continuity_missing_evidence_restoration_plan,
)
from scripts.temporal import run_temporal_continuity_missing_evidence_restoration_plan


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
    observed_paths: list[str] | None = None,
    evidence_items: list[dict[str, object]] | None = None,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    default_missing = ["out/projections/missing_surface_001.latest.json"]
    default_observed = ["scripts/run_missing_surface.py"]
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
            "source_readiness_audit_hash": "x" * 64,
            "source_readiness_status": "READY_WITH_DEGRADED_EVIDENCE",
            "source_recommended_next_lane": "P73_TEMPORAL_CONTINUITY_EVIDENCE_INDEX",
            "evidence_index_status": "MISSING_EVIDENCE_INDEXED",
            "evidence_items": evidence_items
            if evidence_items is not None
            else [
                {
                    "path": "out/projections/missing_surface_001.latest.json",
                    "group_id": "temporal_coherence_chain",
                    "evidence_role": "missing_path",
                    "observed": False,
                    "readable": False,
                    "malformed_json": False,
                    "source_category": "projection",
                    "inherited_status": "PARTIAL",
                    "evidence_hash": "NOT_COMPUTABLE",
                },
                {
                    "path": "scripts/run_missing_surface.py",
                    "group_id": "temporal_coherence_chain",
                    "evidence_role": "observed_path",
                    "observed": True,
                    "readable": True,
                    "malformed_json": False,
                    "source_category": "script",
                    "inherited_status": "PARTIAL",
                    "evidence_hash": "abc",
                },
            ],
            "observed_evidence_paths": observed_paths if observed_paths is not None else default_observed,
            "missing_evidence_paths": missing_paths if missing_paths is not None else default_missing,
            "unreadable_evidence_paths": unreadable_paths if unreadable_paths is not None else [],
            "degraded_evidence_inputs": degraded_evidence_inputs
            if degraded_evidence_inputs is not None
            else ["archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"],
            "inherited_blockers": inherited_blockers
            if inherited_blockers is not None
            else ["temporal_coherence_chain:missing:out/projections/missing_surface_001.latest.json"],
            "inherited_drift_flags": inherited_drift_flags
            if inherited_drift_flags is not None
            else ["GROUP_TEMPORAL_COHERENCE_CHAIN_PARTIAL"],
            "semantic_overlap_flags": semantic_overlap_flags
            if semantic_overlap_flags is not None
            else ["SEMANTIC_OVERLAP_LATEST_JSON:out/projections/missing_surface_001.latest.json"],
            "group_evidence_summary": [],
            "recommended_next_lane": "P74_TEMPORAL_CONTINUITY_MISSING_EVIDENCE_RESTORATION_PLAN",
            "recommended_next_lane_reason": "missing evidence indexed",
            "denied_authority": [],
            "packet_hash": "f" * 64,
        },
    )


# 1. Missing P73 source returns NOT_COMPUTABLE

def test_missing_p73_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["restoration_plan_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P73_EVIDENCE_INDEX_REGENERATION"


# 2. Malformed P73 source returns NOT_COMPUTABLE

def test_malformed_p73_source_returns_not_computable(tmp_path: Path) -> None:
    target = tmp_path / "out" / "temporal_continuity_evidence_index" / "latest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{ bad json", encoding="utf-8")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["restoration_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_evidence_index_hash"] == "NOT_COMPUTABLE"


# 3. Missing evidence paths become restoration_items

def test_missing_evidence_paths_become_restoration_items(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    _seed_file(tmp_path / "scripts" / "run_missing_surface.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    entry = next(
        item
        for item in packet["restoration_items"]
        if item["path"] == "out/projections/missing_surface_001.latest.json"
    )
    assert entry["observed"] is False


# 4. Unreadable evidence paths become restoration_items

def test_unreadable_evidence_paths_become_restoration_items(tmp_path: Path) -> None:
    _seed_p73(
        tmp_path,
        missing_paths=[],
        unreadable_paths=["out/audit/bad_source_001.latest.json"],
        observed_paths=["out/audit/bad_source_001.latest.json"],
        evidence_items=[
            {
                "path": "out/audit/bad_source_001.latest.json",
                "group_id": "archive_chain",
                "evidence_role": "observed_path",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "source_category": "audit",
                "inherited_status": "DEGRADED",
                "evidence_hash": "x",
            }
        ],
    )
    _seed_file(tmp_path / "out" / "audit" / "bad_source_001.latest.json", "{bad}")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    entry = packet["restoration_items"][0]
    assert entry["restoration_strategy"] == "UNREADABLE_SOURCE_REPAIR_PLAN"


# 5. Known generator script inference works only when script exists

def test_known_generator_inference_only_when_script_exists(tmp_path: Path) -> None:
    missing_path = "out/projections/cross_run_topology_fusion_001.latest.json"
    _seed_p73(
        tmp_path,
        missing_paths=[missing_path],
        observed_paths=[],
        evidence_items=[
            {
                "path": missing_path,
                "group_id": "temporal_coherence_chain",
                "evidence_role": "missing_path",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "projection",
                "inherited_status": "PARTIAL",
                "evidence_hash": "NOT_COMPUTABLE",
            }
        ],
    )
    _seed_file(tmp_path / "scripts" / "run_cross_run_topology_fusion.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    entry = packet["restoration_items"][0]
    assert entry["likely_generator_script"] == "scripts/run_cross_run_topology_fusion.py"


# 6. Missing generator script becomes SCRIPT_DISCOVERY_REQUIRED

def test_missing_generator_script_becomes_script_discovery_required(tmp_path: Path) -> None:
    missing_path = "out/projections/nonexistent_surface_001.latest.json"
    _seed_p73(
        tmp_path,
        missing_paths=[missing_path],
        observed_paths=[],
        evidence_items=[
            {
                "path": missing_path,
                "group_id": "unknown_group",
                "evidence_role": "missing_path",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "projection",
                "inherited_status": "PARTIAL",
                "evidence_hash": "NOT_COMPUTABLE",
            }
        ],
    )
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    entry = packet["restoration_items"][0]
    assert entry["restoration_strategy"] == "SCRIPT_DISCOVERY_REQUIRED"


# 7. Temporal coherence missing paths can become UPSTREAM_INPUT_REQUIRED

def test_temporal_coherence_missing_paths_can_be_upstream_required(tmp_path: Path) -> None:
    target = "out/projections/cross_run_topology_fusion_001.latest.json"
    upstream = "out/audit/temporal_coherence_chain_001.latest.json"
    _seed_p73(
        tmp_path,
        missing_paths=[target, upstream],
        observed_paths=["scripts/run_cross_run_topology_fusion.py"],
        evidence_items=[
            {
                "path": target,
                "group_id": "temporal_coherence_chain",
                "evidence_role": "missing_path",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "projection",
                "inherited_status": "PARTIAL",
                "evidence_hash": "NOT_COMPUTABLE",
            },
            {
                "path": upstream,
                "group_id": "temporal_coherence_chain",
                "evidence_role": "missing_path",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "audit",
                "inherited_status": "PARTIAL",
                "evidence_hash": "NOT_COMPUTABLE",
            },
            {
                "path": "scripts/run_cross_run_topology_fusion.py",
                "group_id": "temporal_coherence_chain",
                "evidence_role": "observed_path",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "source_category": "script",
                "inherited_status": "PARTIAL",
                "evidence_hash": "x",
            },
        ],
    )
    _seed_file(tmp_path / "scripts" / "run_cross_run_topology_fusion.py", "print('ok')\n")
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")

    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    entry = next(item for item in packet["restoration_items"] if item["path"] == target)
    assert entry["restoration_strategy"] == "UPSTREAM_INPUT_REQUIRED"


# 8. Existing/readable paths become RESTORATION_NOT_REQUIRED if included

def test_existing_readable_path_becomes_restoration_not_required(tmp_path: Path) -> None:
    path = "out/audit/existing_ready_001.latest.json"
    _seed_p73(
        tmp_path,
        missing_paths=[],
        unreadable_paths=[],
        observed_paths=[path],
        evidence_items=[
            {
                "path": path,
                "group_id": "archive_chain",
                "evidence_role": "observed_path",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "source_category": "audit",
                "inherited_status": "READY",
                "evidence_hash": "x",
            }
        ],
    )
    _seed_file(tmp_path / "out" / "audit" / "existing_ready_001.latest.json", '{"ok":true}\n')
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["restoration_items"][0]["restoration_strategy"] == "RESTORATION_NOT_REQUIRED"


# 9. safe_to_restore is always false

def test_safe_to_restore_always_false(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    _seed_file(tmp_path / "scripts" / "run_missing_surface.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert all(item["safe_to_restore"] is False for item in packet["restoration_items"])


# 10-13 preserved inherited fields

def test_degraded_evidence_inputs_preserved_exactly(tmp_path: Path) -> None:
    marker = "archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"
    _seed_p73(tmp_path, degraded_evidence_inputs=[marker])
    _seed_file(tmp_path / "scripts" / "run_missing_surface.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["degraded_evidence_inputs"] == [marker]


def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    marker = "temporal_coherence_chain:missing:out/projections/missing_surface_001.latest.json"
    _seed_p73(tmp_path, inherited_blockers=[marker])
    _seed_file(tmp_path / "scripts" / "run_missing_surface.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["inherited_blockers"] == [marker]


def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    marker = "GROUP_TEMPORAL_COHERENCE_CHAIN_PARTIAL"
    _seed_p73(tmp_path, inherited_drift_flags=[marker])
    _seed_file(tmp_path / "scripts" / "run_missing_surface.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["inherited_drift_flags"] == [marker]


def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    marker = "SEMANTIC_OVERLAP_LATEST_JSON:out/projections/missing_surface_001.latest.json"
    _seed_p73(tmp_path, semantic_overlap_flags=[marker])
    _seed_file(tmp_path / "scripts" / "run_missing_surface.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["semantic_overlap_flags"] == [marker]


# 14. restoration_items are sorted deterministically

def test_restoration_items_sorted_deterministically(tmp_path: Path) -> None:
    _seed_p73(
        tmp_path,
        missing_paths=[
            "out/projections/b_surface_001.latest.json",
            "out/projections/a_surface_001.latest.json",
        ],
        observed_paths=[],
        evidence_items=[
            {
                "path": "out/projections/b_surface_001.latest.json",
                "group_id": "g2",
                "evidence_role": "missing_path",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "projection",
                "inherited_status": "PARTIAL",
                "evidence_hash": "NOT_COMPUTABLE",
            },
            {
                "path": "out/projections/a_surface_001.latest.json",
                "group_id": "g1",
                "evidence_role": "missing_path",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "projection",
                "inherited_status": "PARTIAL",
                "evidence_hash": "NOT_COMPUTABLE",
            },
        ],
    )
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    ordering = [
        (item["path"], item["group_id"], item["restoration_strategy"])
        for item in packet["restoration_items"]
    ]
    assert ordering == sorted(ordering)


# 15. restoration_strategy_summary is deterministic

def test_restoration_strategy_summary_is_deterministic(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    _seed_file(tmp_path / "scripts" / "run_missing_surface.py", "print('ok')\n")
    first = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    second = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert first["restoration_strategy_summary"] == second["restoration_strategy_summary"]


# 16-21 next-lane logic

def test_script_discovery_required_recommends_discovery_plan(tmp_path: Path) -> None:
    _seed_p73(
        tmp_path,
        missing_paths=["out/projections/no_script_surface_001.latest.json"],
        observed_paths=[],
        evidence_items=[
            {
                "path": "out/projections/no_script_surface_001.latest.json",
                "group_id": "unknown_group",
                "evidence_role": "missing_path",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "projection",
                "inherited_status": "PARTIAL",
                "evidence_hash": "NOT_COMPUTABLE",
            }
        ],
    )
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_GENERATOR_DISCOVERY_PLAN"


def test_upstream_required_recommends_upstream_plan(tmp_path: Path) -> None:
    target = "out/projections/cross_run_topology_fusion_001.latest.json"
    upstream = "out/audit/temporal_coherence_chain_001.latest.json"
    _seed_p73(
        tmp_path,
        missing_paths=[target, upstream],
        observed_paths=["scripts/run_cross_run_topology_fusion.py"],
        evidence_items=[
            {
                "path": target,
                "group_id": "temporal_coherence_chain",
                "evidence_role": "missing_path",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "projection",
                "inherited_status": "PARTIAL",
                "evidence_hash": "NOT_COMPUTABLE",
            },
            {
                "path": upstream,
                "group_id": "temporal_coherence_chain",
                "evidence_role": "missing_path",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "audit",
                "inherited_status": "PARTIAL",
                "evidence_hash": "NOT_COMPUTABLE",
            },
            {
                "path": "scripts/run_cross_run_topology_fusion.py",
                "group_id": "temporal_coherence_chain",
                "evidence_role": "observed_path",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "source_category": "script",
                "inherited_status": "PARTIAL",
                "evidence_hash": "x",
            },
        ],
    )
    _seed_file(tmp_path / "scripts" / "run_cross_run_topology_fusion.py", "print('ok')\n")
    _seed_file(tmp_path / "scripts" / "run_temporal_coherence_chain.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN"


def test_all_generator_exists_recommends_regeneration_dry_run_plan(tmp_path: Path) -> None:
    path = "out/projections/cross_run_topology_fusion_001.latest.json"
    _seed_p73(
        tmp_path,
        missing_paths=[path],
        observed_paths=[],
        evidence_items=[
            {
                "path": path,
                "group_id": "single",
                "evidence_role": "missing_path",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "source_category": "projection",
                "inherited_status": "PARTIAL",
                "evidence_hash": "NOT_COMPUTABLE",
            }
        ],
        degraded_evidence_inputs=[],
    )
    _seed_file(tmp_path / "scripts" / "run_cross_run_topology_fusion.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN"


def test_unreadable_evidence_recommends_unreadable_repair_plan(tmp_path: Path) -> None:
    path = "out/audit/bad_source_001.latest.json"
    _seed_p73(
        tmp_path,
        missing_paths=[],
        unreadable_paths=[path],
        observed_paths=[path],
        evidence_items=[
            {
                "path": path,
                "group_id": "archive_chain",
                "evidence_role": "observed_path",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "source_category": "audit",
                "inherited_status": "DEGRADED",
                "evidence_hash": "x",
            }
        ],
        degraded_evidence_inputs=[],
    )
    _seed_file(tmp_path / "out" / "audit" / "bad_source_001.latest.json", "{bad}")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_UNREADABLE_EVIDENCE_REPAIR_PLAN"


def test_no_restoration_required_with_degraded_recommends_degraded_plan(tmp_path: Path) -> None:
    path = "out/audit/ready_001.latest.json"
    _seed_p73(
        tmp_path,
        missing_paths=[],
        unreadable_paths=[],
        observed_paths=[path],
        evidence_items=[
            {
                "path": path,
                "group_id": "archive_chain",
                "evidence_role": "observed_path",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "source_category": "audit",
                "inherited_status": "DEGRADED",
                "evidence_hash": "x",
            }
        ],
        degraded_evidence_inputs=["archive_chain:degraded:out/audit/ready_001.latest.json:ARCHIVE_DEGRADED"],
    )
    _seed_file(tmp_path / "out" / "audit" / "ready_001.latest.json", '{"ok":true}\n')
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"


def test_no_restoration_required_and_no_degraded_recommends_spine_gate(tmp_path: Path) -> None:
    path = "out/audit/ready_001.latest.json"
    _seed_p73(
        tmp_path,
        missing_paths=[],
        unreadable_paths=[],
        observed_paths=[path],
        evidence_items=[
            {
                "path": path,
                "group_id": "archive_chain",
                "evidence_role": "observed_path",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "source_category": "audit",
                "inherited_status": "READY",
                "evidence_hash": "x",
            }
        ],
        degraded_evidence_inputs=[],
    )
    _seed_file(tmp_path / "out" / "audit" / "ready_001.latest.json", '{"ok":true}\n')
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P75_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE"


# 22. Authority fields are schema-locked / escalation denied

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


# 23. Packet hash is deterministic

def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    _seed_file(tmp_path / "scripts" / "run_missing_surface.py", "print('ok')\n")
    first = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    second = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]


# 24. Writer emits canonical JSON with final newline

def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    _seed_file(tmp_path / "scripts" / "run_missing_surface.py", "print('ok')\n")
    packet = build_temporal_continuity_missing_evidence_restoration_plan(repo_root=tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_missing_evidence_restoration_plan" / "latest.json"
    write_temporal_continuity_missing_evidence_restoration_plan(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


# 25. Runner writes expected output path

def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p73(tmp_path)
    _seed_file(tmp_path / "scripts" / "run_missing_surface.py", "print('ok')\n")
    out_path = tmp_path / "out" / "temporal_continuity_missing_evidence_restoration_plan" / "latest.json"
    first = run_temporal_continuity_missing_evidence_restoration_plan.run(
        repo_root=tmp_path, out_path=out_path
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_missing_evidence_restoration_plan.run(
        repo_root=tmp_path, out_path=out_path
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


# 26. Artifact registry classification is DERIVED_OPTIONAL

def test_artifact_registry_classifies_as_derived_optional() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS  # type: ignore[attr-defined]

    assert (
        "out/temporal_continuity_missing_evidence_restoration_plan/latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
