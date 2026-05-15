from __future__ import annotations

from pathlib import Path

import pytest

from core.generated_artifact_registry import (
    GENERATED_ARTIFACT_POLICY_V1,
    ArtifactRegenerationPlan,
    GeneratedArtifactEntry,
    GeneratedArtifactRegistry,
    build_generated_artifact_registry,
    build_artifact_regeneration_plan,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _registry_for(entries: list[GeneratedArtifactEntry]) -> GeneratedArtifactRegistry:
    return GeneratedArtifactRegistry(
        entries=entries,
        dependency_edges=[],
        artifact_source_map={entry.artifact_path: {} for entry in entries},
        regeneration_capability={},
        orphaned_artifacts=[],
        stale_artifact_tests=[],
        derived_vs_canonical_ratio={"derived_artifact_count": len(entries), "canonical_generator_count": 1, "ratio": 1.0},
        giant_artifact_churn_zones=[],
        dirty_pr_paths=[],
        downstream_impact_summary={},
        final_status="PASS",
    )


def test_registry_audit_fields_present() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    assert registry.policy_id == GENERATED_ARTIFACT_POLICY_V1["policy_id"]
    assert "out/contracts/artifact_contract_p2c_d5_human_approval.latest.json" in registry.artifact_source_map
    assert registry.regeneration_capability["managed_artifact_count"] > 0
    assert registry.derived_vs_canonical_ratio["ratio"] > 0
    assert registry.stale_artifact_tests


def test_registry_maps_known_generator_and_downstream_dependencies() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == "out/projections/projection_bus_001.latest.json"
    )
    assert entry.canonical_generator == "scripts/run_projection_bus.py"
    assert entry.canonical_schema
    d5_entry = next(
        item
        for item in registry.entries
        if item.artifact_path == "out/contracts/artifact_contract_p2c_d5_human_approval.latest.json"
    )
    assert "scripts/run_artifact_contract_global_closure_audit.py" in d5_entry.downstream_dependencies


def test_missing_generator_fails_closed() -> None:
    registry = _registry_for(
        [
            GeneratedArtifactEntry(
                artifact_path="out/contracts/example.latest.json",
                canonical_generator=None,
                canonical_schema="Example.v1",
                deterministic_inputs=[],
                regeneration_required=True,
                committed_policy="tracked-derived",
                downstream_dependencies=[],
                final_status="managed",
                artifact_kind="json",
                tracked=False,
            )
        ]
    )
    with pytest.raises(ValueError, match="missing generator"):
        build_artifact_regeneration_plan(registry, selected_artifacts=["out/contracts/example.latest.json"])


def test_missing_schema_fails_closed() -> None:
    registry = _registry_for(
        [
            GeneratedArtifactEntry(
                artifact_path="out/contracts/example.latest.json",
                canonical_generator="scripts/run_example.py",
                canonical_schema=None,
                deterministic_inputs=[],
                regeneration_required=True,
                committed_policy="tracked-derived",
                downstream_dependencies=[],
                final_status="managed",
                artifact_kind="json",
                tracked=False,
            )
        ]
    )
    with pytest.raises(ValueError, match="missing schema"):
        build_artifact_regeneration_plan(registry, selected_artifacts=["out/contracts/example.latest.json"])


def test_registry_models_preserve_authority_locks() -> None:
    plan = ArtifactRegenerationPlan(final_status="PASS")
    assert plan.advisory_only is True
    assert plan.mutation_allowed is False
    assert plan.authority_granted is False
    assert plan.auto_execute is False
    assert plan.auto_approve is False
