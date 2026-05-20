from __future__ import annotations

import json
import stat
from pathlib import Path

import pytest

from core.temporal_continuity_generator_discovery_plan import (
    build_temporal_continuity_generator_discovery_plan,
    write_temporal_continuity_generator_discovery_plan,
)
from scripts import run_temporal_continuity_generator_discovery_plan


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _seed_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_p74(
    root: Path,
    *,
    restoration_plan_status: str = "RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE",
    restoration_items: list[dict[str, object]] | None = None,
    degraded_evidence_inputs: list[str] | None = None,
    inherited_blockers: list[str] | None = None,
    inherited_drift_flags: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
    recommended_next_lane: str = "P75_TEMPORAL_CONTINUITY_GENERATOR_DISCOVERY_PLAN",
) -> None:
    default_items: list[dict[str, object]] = [
        {
            "path": "out/projections/missing_surface_001.latest.json",
            "group_id": "temporal_coherence_chain",
            "source_category": "projection",
            "evidence_role": "missing_path",
            "inherited_status": "PARTIAL",
            "observed": False,
            "readable": False,
            "malformed_json": False,
            "restoration_strategy": "SCRIPT_DISCOVERY_REQUIRED",
            "likely_generator_script": "NOT_COMPUTABLE",
            "prerequisite_paths": [],
            "blocking_reason": "NO_DIRECT_GENERATOR_SCRIPT_INFERENCE_P74_PLANNING_ONLY",
            "safe_to_restore": False,
        }
    ]
    _write_json(
        root / "out" / "temporal_continuity_missing_evidence_restoration_plan" / "latest.json",
        {
            "artifact_type": "TemporalContinuityMissingEvidenceRestorationPlan.v1",
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
            "restoration_execution_authority": False,
            "spine_implementation_authority": False,
            "source_evidence_index_path": "out/temporal_continuity_evidence_index/latest.json",
            "source_evidence_index_observed": True,
            "source_evidence_index_hash": "x" * 64,
            "source_evidence_index_status": "MISSING_EVIDENCE_INDEXED",
            "source_recommended_next_lane": "P74_TEMPORAL_CONTINUITY_MISSING_EVIDENCE_RESTORATION_PLAN",
            "restoration_plan_status": restoration_plan_status,
            "restoration_items": restoration_items if restoration_items is not None else default_items,
            "missing_evidence_paths": ["out/projections/missing_surface_001.latest.json"],
            "unreadable_evidence_paths": [],
            "degraded_evidence_inputs": (
                degraded_evidence_inputs
                if degraded_evidence_inputs is not None
                else ["archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"]
            ),
            "inherited_blockers": (
                inherited_blockers
                if inherited_blockers is not None
                else ["temporal_coherence_chain:missing:out/projections/missing_surface_001.latest.json"]
            ),
            "inherited_drift_flags": (
                inherited_drift_flags
                if inherited_drift_flags is not None
                else ["GROUP_TEMPORAL_COHERENCE_CHAIN_PARTIAL"]
            ),
            "semantic_overlap_flags": (
                semantic_overlap_flags
                if semantic_overlap_flags is not None
                else ["SEMANTIC_OVERLAP_LATEST_JSON:out/projections/missing_surface_001.latest.json"]
            ),
            "restoration_strategy_summary": {
                "SCRIPT_DISCOVERY_REQUIRED": 1,
                "GENERATOR_EXISTS_REGENERATION_PLAN": 0,
                "UPSTREAM_INPUT_REQUIRED": 0,
                "UNREADABLE_SOURCE_REPAIR_PLAN": 0,
                "RESTORATION_NOT_REQUIRED": 0,
                "NOT_COMPUTABLE": 0,
            },
            "recommended_next_lane": recommended_next_lane,
            "recommended_next_lane_reason": "test seed",
            "denied_authority": [],
            "packet_hash": "f" * 64,
        },
    )


# 1. Missing P74 source returns NOT_COMPUTABLE

def test_missing_p74_source_returns_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert packet["generator_discovery_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P74_RESTORATION_PLAN_REGENERATION"


# 2. Malformed P74 source returns NOT_COMPUTABLE

def test_malformed_p74_source_returns_not_computable(tmp_path: Path) -> None:
    target = (
        tmp_path
        / "out"
        / "temporal_continuity_missing_evidence_restoration_plan"
        / "latest.json"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{ bad json", encoding="utf-8")
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert packet["generator_discovery_status"] == "NOT_COMPUTABLE"
    assert packet["source_restoration_plan_hash"] == "NOT_COMPUTABLE"


# 3. RESTORATION_NOT_REQUIRED returns GENERATOR_DISCOVERY_NOT_REQUIRED

def test_restoration_not_required_returns_discovery_not_required(tmp_path: Path) -> None:
    path = "out/audit/ready_001.latest.json"
    _seed_p74(
        tmp_path,
        restoration_plan_status="RESTORATION_NOT_REQUIRED",
        restoration_items=[
            {
                "path": path,
                "group_id": "archive_chain",
                "source_category": "audit",
                "evidence_role": "observed_path",
                "inherited_status": "READY",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "restoration_strategy": "RESTORATION_NOT_REQUIRED",
                "likely_generator_script": "NOT_COMPUTABLE",
                "prerequisite_paths": [],
                "blocking_reason": "EVIDENCE_PRESENT_AND_READABLE_P74_PLANNING_ONLY",
                "safe_to_restore": False,
            }
        ],
        degraded_evidence_inputs=[],
    )
    _seed_file(tmp_path / path, '{"ok":true}\n')
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert packet["generator_discovery_status"] == "GENERATOR_DISCOVERY_NOT_REQUIRED"


# 4. likely_generator_script = NOT_COMPUTABLE yields GENERATOR_NOT_COMPUTABLE binding

def test_not_computable_generator_script_yields_not_computable_binding(tmp_path: Path) -> None:
    _seed_p74(tmp_path)
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    item = packet["generator_items"][0]
    assert item["generator_binding_status"] == "GENERATOR_NOT_COMPUTABLE"


# 5. Missing generator script yields GENERATOR_MISSING

def test_missing_generator_script_yields_generator_missing(tmp_path: Path) -> None:
    path = "out/projections/missing_surface_001.latest.json"
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "temporal_coherence_chain",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "SCRIPT_DISCOVERY_REQUIRED",
                "likely_generator_script": "scripts/run_missing_surface.py",
                "prerequisite_paths": ["scripts/run_missing_surface.py"],
                "blocking_reason": "NO_DIRECT_GENERATOR_SCRIPT_INFERENCE_P74_PLANNING_ONLY",
                "safe_to_restore": False,
            }
        ],
    )
    # Do NOT create the script — it is missing
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    item = next(it for it in packet["generator_items"] if it["output_path"] == path)
    assert item["generator_binding_status"] == "GENERATOR_MISSING"
    assert "scripts/run_missing_surface.py" in packet["missing_generator_scripts"]


# 6. Existing unreadable generator yields GENERATOR_UNREADABLE (where env permits)

def test_existing_unreadable_generator_yields_unreadable(tmp_path: Path) -> None:
    path = "out/projections/missing_surface_001.latest.json"
    script_path = tmp_path / "scripts" / "run_missing_surface.py"
    _seed_file(script_path, "def main():\n    pass\n")
    # Remove read permissions
    script_path.chmod(0o000)

    # Check whether we can actually be blocked from reading (root bypasses chmod)
    readable_despite_chmod = False
    try:
        script_path.read_bytes()
        readable_despite_chmod = True
    except PermissionError:
        pass

    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "temporal_coherence_chain",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": "scripts/run_missing_surface.py",
                "prerequisite_paths": ["scripts/run_missing_surface.py"],
                "blocking_reason": "GENERATOR_AVAILABLE_BUT_EXECUTION_DENIED_IN_P74",
                "safe_to_restore": False,
            }
        ],
    )

    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    item = next(it for it in packet["generator_items"] if it["output_path"] == path)

    if readable_despite_chmod:
        # Running as root — chmod didn't prevent reads; skip unreadable assertion
        pytest.skip("Running as root: chmod(0o000) does not block reads; skipping GENERATOR_UNREADABLE assertion")
    else:
        assert item["generator_binding_status"] == "GENERATOR_UNREADABLE"
        assert "scripts/run_missing_surface.py" in packet["unreadable_generator_scripts"]

    script_path.chmod(stat.S_IRUSR | stat.S_IWUSR)


# 7. Existing readable generator yields GENERATOR_OBSERVED

def test_existing_readable_generator_yields_observed(tmp_path: Path) -> None:
    path = "out/projections/cross_run_topology_fusion_001.latest.json"
    script = "scripts/run_cross_run_topology_fusion.py"
    _seed_file(tmp_path / script, 'def main():\n    pass\n\nif __name__ == "__main__":\n    main()\n')
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "temporal_coherence_chain",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [script],
                "blocking_reason": "GENERATOR_AVAILABLE_BUT_EXECUTION_DENIED_IN_P74",
                "safe_to_restore": False,
            }
        ],
    )
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    item = next(it for it in packet["generator_items"] if it["output_path"] == path)
    assert item["generator_binding_status"] == "GENERATOR_OBSERVED"
    assert script in packet["observed_generator_scripts"]


# 8. Callable hint detects entrypoint patterns by static text inspection

def test_callable_hint_detects_main_entrypoint(tmp_path: Path) -> None:
    path = "out/projections/surface_001.latest.json"
    script = "scripts/run_surface.py"

    # Script with def main(
    _seed_file(tmp_path / script, "def main():\n    pass\n")
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "g",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            }
        ],
    )
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    item = next(it for it in packet["generator_items"] if it["output_path"] == path)
    assert item["generator_callable_hint"] is True


def test_callable_hint_detects_name_main_pattern(tmp_path: Path) -> None:
    path = "out/projections/surface_001.latest.json"
    script = "scripts/run_surface.py"
    _seed_file(tmp_path / script, 'print("x")\nif __name__ == "__main__":\n    pass\n')
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "g",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            }
        ],
    )
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    item = next(it for it in packet["generator_items"] if it["output_path"] == path)
    assert item["generator_callable_hint"] is True


def test_callable_hint_false_when_no_entrypoint(tmp_path: Path) -> None:
    path = "out/projections/surface_001.latest.json"
    script = "scripts/run_surface.py"
    _seed_file(tmp_path / script, "x = 1\n")
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "g",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            }
        ],
    )
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    item = next(it for it in packet["generator_items"] if it["output_path"] == path)
    assert item["generator_callable_hint"] is False


# 9. safe_to_execute is always false

def test_safe_to_execute_always_false(tmp_path: Path) -> None:
    _seed_p74(tmp_path)
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert all(item["safe_to_execute"] is False for item in packet["generator_items"])


# 10. Missing prerequisites are detected from prerequisite_paths

def test_missing_prerequisites_detected(tmp_path: Path) -> None:
    path = "out/projections/surface_001.latest.json"
    script = "scripts/run_surface.py"
    prereq = "out/audit/upstream_001.latest.json"
    _seed_file(tmp_path / script, "def run():\n    pass\n")
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "g",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [script, prereq],
                "blocking_reason": "x",
                "safe_to_restore": False,
            }
        ],
    )
    # script exists but prereq does NOT exist
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    item = next(it for it in packet["generator_items"] if it["output_path"] == path)
    assert prereq in item["missing_prerequisite_paths"]
    assert prereq in packet["missing_prerequisite_paths"]


# 11. Ambiguous generator bindings are deterministically reported

def test_ambiguous_generator_bindings_reported(tmp_path: Path) -> None:
    script = "scripts/run_shared.py"
    path_a = "out/projections/surface_a_001.latest.json"
    path_b = "out/projections/surface_b_001.latest.json"
    _seed_file(tmp_path / script, "def main():\n    pass\n")
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path_a,
                "group_id": "g1",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            },
            {
                "path": path_b,
                "group_id": "g2",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            },
        ],
    )
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert script in packet["ambiguous_generator_bindings"]
    for item in packet["generator_items"]:
        assert item["generator_binding_status"] == "GENERATOR_AMBIGUOUS"


# 12. degraded_evidence_inputs preserved exactly

def test_degraded_evidence_inputs_preserved_exactly(tmp_path: Path) -> None:
    marker = "archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"
    _seed_p74(tmp_path, degraded_evidence_inputs=[marker])
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert packet["degraded_evidence_inputs"] == [marker]


# 13. inherited_blockers preserved exactly

def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    marker = "temporal_coherence_chain:missing:out/projections/missing_surface_001.latest.json"
    _seed_p74(tmp_path, inherited_blockers=[marker])
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert packet["inherited_blockers"] == [marker]


# 14. inherited_drift_flags preserved exactly

def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    marker = "GROUP_TEMPORAL_COHERENCE_CHAIN_PARTIAL"
    _seed_p74(tmp_path, inherited_drift_flags=[marker])
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert packet["inherited_drift_flags"] == [marker]


# 15. semantic_overlap_flags preserved exactly

def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    marker = "SEMANTIC_OVERLAP_LATEST_JSON:out/projections/missing_surface_001.latest.json"
    _seed_p74(tmp_path, semantic_overlap_flags=[marker])
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert packet["semantic_overlap_flags"] == [marker]


# 16. generator_items are sorted deterministically

def test_generator_items_sorted_deterministically(tmp_path: Path) -> None:
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": "out/projections/b_surface_001.latest.json",
                "group_id": "g2",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "SCRIPT_DISCOVERY_REQUIRED",
                "likely_generator_script": "NOT_COMPUTABLE",
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            },
            {
                "path": "out/projections/a_surface_001.latest.json",
                "group_id": "g1",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "SCRIPT_DISCOVERY_REQUIRED",
                "likely_generator_script": "NOT_COMPUTABLE",
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            },
        ],
    )
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    ordering = [
        (it["output_path"], it["group_id"], it["likely_generator_script"])
        for it in packet["generator_items"]
    ]
    assert ordering == sorted(ordering)


# 17. generator_strategy_summary is deterministic

def test_generator_strategy_summary_is_deterministic(tmp_path: Path) -> None:
    _seed_p74(tmp_path)
    first = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    second = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert first["generator_strategy_summary"] == second["generator_strategy_summary"]


# 18. Missing generators recommend P76_TEMPORAL_CONTINUITY_GENERATOR_IMPLEMENTATION_PLAN

def test_missing_generators_recommend_implementation_plan(tmp_path: Path) -> None:
    path = "out/projections/surface_001.latest.json"
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "g",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "SCRIPT_DISCOVERY_REQUIRED",
                "likely_generator_script": "scripts/run_surface.py",
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            }
        ],
    )
    # Do NOT create the script
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert packet["recommended_next_lane"] == "P76_TEMPORAL_CONTINUITY_GENERATOR_IMPLEMENTATION_PLAN"


# 19. Unreadable generators recommend P76_TEMPORAL_CONTINUITY_GENERATOR_REPAIR_PLAN

def test_unreadable_generators_recommend_repair_plan(tmp_path: Path) -> None:
    path = "out/projections/surface_001.latest.json"
    script_path = tmp_path / "scripts" / "run_surface.py"
    _seed_file(script_path, "def main():\n    pass\n")
    script_path.chmod(0o000)

    readable_despite_chmod = False
    try:
        script_path.read_bytes()
        readable_despite_chmod = True
    except PermissionError:
        pass

    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "g",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": "scripts/run_surface.py",
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            }
        ],
    )

    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    script_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    if readable_despite_chmod:
        pytest.skip("Running as root: chmod(0o000) does not block reads; skipping GENERATOR_REPAIR_PLAN assertion")
    else:
        assert packet["recommended_next_lane"] == "P76_TEMPORAL_CONTINUITY_GENERATOR_REPAIR_PLAN"


# 20. Ambiguous bindings recommend P76_TEMPORAL_CONTINUITY_GENERATOR_BINDING_DISAMBIGUATION_PLAN

def test_ambiguous_bindings_recommend_disambiguation_plan(tmp_path: Path) -> None:
    script = "scripts/run_shared.py"
    _seed_file(tmp_path / script, "def main():\n    pass\n")
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": "out/projections/surface_a_001.latest.json",
                "group_id": "g1",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            },
            {
                "path": "out/projections/surface_b_001.latest.json",
                "group_id": "g2",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            },
        ],
    )
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert (
        packet["recommended_next_lane"]
        == "P76_TEMPORAL_CONTINUITY_GENERATOR_BINDING_DISAMBIGUATION_PLAN"
    )


# 21. Observed generators with missing prerequisites recommend P76_UPSTREAM_INPUT_RESTORATION_PLAN

def test_observed_generators_with_missing_prerequisites_recommend_upstream_plan(
    tmp_path: Path,
) -> None:
    path = "out/projections/surface_001.latest.json"
    script = "scripts/run_surface.py"
    prereq = "out/audit/upstream_001.latest.json"
    _seed_file(tmp_path / script, "def run():\n    pass\n")
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "g",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [prereq],
                "blocking_reason": "x",
                "safe_to_restore": False,
            }
        ],
        degraded_evidence_inputs=[],
    )
    # prereq does NOT exist
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert (
        packet["recommended_next_lane"]
        == "P76_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN"
    )


# 22. Observed generators with prerequisites present recommend DRY_RUN_PLAN

def test_observed_generators_with_prerequisites_recommend_dry_run_plan(tmp_path: Path) -> None:
    path = "out/projections/surface_001.latest.json"
    script = "scripts/run_surface.py"
    prereq = "out/audit/upstream_001.latest.json"
    _seed_file(tmp_path / script, "def run():\n    pass\n")
    _seed_file(tmp_path / prereq, '{"ok":true}\n')
    _seed_p74(
        tmp_path,
        restoration_items=[
            {
                "path": path,
                "group_id": "g",
                "source_category": "projection",
                "evidence_role": "missing_path",
                "inherited_status": "PARTIAL",
                "observed": False,
                "readable": False,
                "malformed_json": False,
                "restoration_strategy": "GENERATOR_EXISTS_REGENERATION_PLAN",
                "likely_generator_script": script,
                "prerequisite_paths": [prereq],
                "blocking_reason": "x",
                "safe_to_restore": False,
            }
        ],
        degraded_evidence_inputs=[],
    )
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert (
        packet["recommended_next_lane"]
        == "P76_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN"
    )


# 23. Generator discovery not required with degraded evidence recommends DEGRADED_EVIDENCE_REPAIR_PLAN

def test_discovery_not_required_with_degraded_recommends_degraded_repair_plan(
    tmp_path: Path,
) -> None:
    path = "out/audit/ready_001.latest.json"
    _seed_p74(
        tmp_path,
        restoration_plan_status="RESTORATION_NOT_REQUIRED",
        restoration_items=[
            {
                "path": path,
                "group_id": "archive_chain",
                "source_category": "audit",
                "evidence_role": "observed_path",
                "inherited_status": "READY",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "restoration_strategy": "RESTORATION_NOT_REQUIRED",
                "likely_generator_script": "NOT_COMPUTABLE",
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            }
        ],
        degraded_evidence_inputs=["archive_chain:degraded:out/audit/archive_ready.json:ARCHIVE_DEGRADED"],
    )
    _seed_file(tmp_path / path, '{"ok":true}\n')
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert (
        packet["recommended_next_lane"]
        == "P76_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"
    )


# 24. Generator discovery not required with no degraded evidence recommends SPINE_IMPLEMENTATION_PLANNING_GATE

def test_discovery_not_required_no_degraded_recommends_spine_gate(tmp_path: Path) -> None:
    path = "out/audit/ready_001.latest.json"
    _seed_p74(
        tmp_path,
        restoration_plan_status="RESTORATION_NOT_REQUIRED",
        restoration_items=[
            {
                "path": path,
                "group_id": "archive_chain",
                "source_category": "audit",
                "evidence_role": "observed_path",
                "inherited_status": "READY",
                "observed": True,
                "readable": True,
                "malformed_json": False,
                "restoration_strategy": "RESTORATION_NOT_REQUIRED",
                "likely_generator_script": "NOT_COMPUTABLE",
                "prerequisite_paths": [],
                "blocking_reason": "x",
                "safe_to_restore": False,
            }
        ],
        degraded_evidence_inputs=[],
    )
    _seed_file(tmp_path / path, '{"ok":true}\n')
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert (
        packet["recommended_next_lane"]
        == "P76_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE"
    )


# 25. Authority fields are schema-locked / escalation denied

def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path(
            "contracts/canon/temporal_continuity_generator_discovery_plan.v1.schema.json"
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
        "generator_execution_authority",
        "spine_implementation_authority",
    ):
        assert schema["properties"][field]["const"] is False, f"Field {field!r} must be const:false"


def test_runtime_packet_authority_fields_false(tmp_path: Path) -> None:
    _seed_p74(tmp_path)
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
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
        "spine_implementation_authority",
    ):
        assert packet[field] is False, f"Field {field!r} must be False"


# 26. Packet hash is deterministic

def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_p74(tmp_path)
    first = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    second = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]


# 27. Writer emits canonical JSON with final newline

def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p74(tmp_path)
    packet = build_temporal_continuity_generator_discovery_plan(repo_root=tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_generator_discovery_plan" / "latest.json"
    write_temporal_continuity_generator_discovery_plan(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


# 28. Runner writes out/temporal_continuity_generator_discovery_plan/latest.json

def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p74(tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_generator_discovery_plan" / "latest.json"
    first = run_temporal_continuity_generator_discovery_plan.run(
        repo_root=tmp_path, out_path=out_path
    )
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_generator_discovery_plan.run(
        repo_root=tmp_path, out_path=out_path
    )
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


# 29. Artifact registry classifies output as DERIVED_OPTIONAL

def test_artifact_registry_classifies_as_derived_optional() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS  # type: ignore[attr-defined]

    assert (
        "out/temporal_continuity_generator_discovery_plan/latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
