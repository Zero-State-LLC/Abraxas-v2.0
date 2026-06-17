from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from core.generated_artifact_registry import (
    GENERATED_ARTIFACT_POLICY_V1,
    ArtifactRegenerationPlan,
    GeneratedArtifactEntry,
    GeneratedArtifactRegistry,
    build_generated_artifact_registry,
    build_artifact_regeneration_plan,
    detect_ci_artifact_drift_paths,
    list_ci_drift_artifact_paths,
)
from scripts import run_artifact_regeneration


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
    replay_entry = next(
        item
        for item in registry.entries
        if item.artifact_path == "out/audit/replay_consensus_review_contract.latest.json"
    )
    assert replay_entry.canonical_generator == "scripts/run_replay_consensus_review_contract.py"
    assert replay_entry.final_status == "managed"


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


def test_registry_emits_stable_ci_drift_target_list() -> None:
    from core.generated_artifact_registry import _has_git_metadata

    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = list_ci_drift_artifact_paths(registry)
    assert expected == list_ci_drift_artifact_paths(registry)
    assert "out/audit/artifact_regeneration_001.latest.json" not in expected
    assert "out/validation/latest.json" not in expected
    assert "out/projections/aal_viz.latest.json" not in expected
    if _has_git_metadata(REPO_ROOT):
        assert "out/projections/projection_bus_001.latest.json" in expected
    else:
        assert expected == []


def test_temporal_stability_pressure_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path
        == "out/projections/temporal_stability_pressure_001.latest.json"
    )
    assert entry.canonical_generator == "scripts/run_temporal_stability_pressure.py"
    assert entry.final_status == "managed"
    assert entry.tracked is False
    assert entry.determinism_class == "DERIVED_OPTIONAL"
    assert (
        "out/projections/temporal_stability_pressure_001.latest.json"
        not in list_ci_drift_artifact_paths(registry)
    )



def test_temporal_coherence_chain_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == "out/audit/temporal_coherence_chain_001.latest.json"
    )
    assert entry.canonical_generator == "scripts/run_temporal_coherence_chain.py"
    assert entry.final_status == "managed"
    assert entry.determinism_class == "DERIVED_OPTIONAL"
    assert entry.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_temporal_continuity_spine_precheck_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == "out/temporal_continuity_spine_precheck/latest.json"
    )
    assert entry.canonical_generator == "scripts/run_temporal_continuity_spine_precheck.py"
    assert entry.final_status == "managed"
    assert entry.determinism_class == "DERIVED_OPTIONAL"
    assert entry.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_temporal_continuity_spine_binder_contract_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == "out/temporal_continuity_spine_binder_contract/latest.json"
    )
    assert entry.canonical_generator == "scripts/run_temporal_continuity_spine_binder_contract.py"
    assert entry.final_status == "managed"
    assert entry.determinism_class == "DERIVED_OPTIONAL"
    assert entry.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_yggdrasil_binding_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json": "json",
        "out/audit/yggdrasil_rune_route_binding_matrix_001.latest.md": "markdown",
        "out/audit/yggdrasil_coupling_map_001.latest.json": "json",
        "out/audit/yggdrasil_coupling_map_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == "scripts/run_yggdrasil_rune_route_binding_matrix.py"
        assert entry.final_status == "managed"
        assert entry.determinism_class == "BUILD_CANONICAL"
        assert entry.artifact_kind == artifact_kind
        assert artifact_path in list_ci_drift_artifact_paths(registry)


def test_abx_codegen_spine_gap_analysis_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_gap_analysis_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.determinism_class == "BUILD_CANONICAL"
        assert entry.artifact_kind == artifact_kind
        assert artifact_path in list_ci_drift_artifact_paths(registry)


def test_abx_codegen_spine_advisory_spec_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_advisory_spec_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_advisory_spec_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_advisory_spec_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_fixture_validation_harness_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_fixture_validation_harness_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_fixture_validation_harness_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_fixture_validation_harness_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_packet_validation_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_packet_validation_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_notion_stack_alignment_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_notion_stack_alignment_audit_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_notion_stack_alignment_audit_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_notion_stack_alignment_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_shadow_replay_harness_authorization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_implementation_authorization_gate_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_implementation_authorization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_shadow_replay_harness_implementation_authorization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_shadow_replay_harness_operator_decision_record_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_shadow_replay_harness_operator_decision_record_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_shadow_replay_harness_operator_decision_record_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_dry_run_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_shadow_replay_harness_operator_decision_record_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_shadow_replay_harness_operator_decision_record_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_review_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_shadow_replay_harness_operator_decision_record_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_p102g_plus_operator_decision_surface_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json": "json",
        "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_p102g_plus_operator_decision_surface_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_operator_review_required_items_bulk_disposition_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json": "json",
        "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_operator_review_required_items_bulk_disposition.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_operator_review_terminal_hold_consolidation_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.json": "json",
        "out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_operator_review_terminal_hold_consolidation_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_bulk_approval_reconciliation_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_bulk_approval_reconciliation_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_bulk_approval_reconciliation_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_bulk_approval_reconciliation.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_operator_review_dependency_cycle_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_operator_review_dependency_cycle_audit_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_operator_review_dependency_cycle_audit_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_operator_review_dependency_cycle_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_operator_review_stabilization_strategy_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_planning_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_planning_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_planning_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_planning_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_creation_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_creation_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_creation_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_creation_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_materialization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_materialization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_materialization_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_materialization_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_materialization_authorization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_authorization_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_authorization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_materialization_authorization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_materialization_approval_intake_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_intake_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_intake_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_materialization_approval_intake_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_emission_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_emission_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_emission_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_emission_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_finalization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_finalization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_finalization_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_finalization_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_chain_compression_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_chain_compression_audit_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_chain_compression_audit_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_chain_compression_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_finalization_approval_intake_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_approval_intake_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_approval_intake_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_finalization_approval_intake_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_authorization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_authorization_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_authorization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_authorization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_decision_record_completion_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_decision_record_completion_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_promotion_closure_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_promotion_closure_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_promotion_closure_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_promotion_closure_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase5_controlled_writeback_activation_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase5_controlled_writeback_activation_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase5_controlled_writeback_activation_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase5_controlled_writeback_activation_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase6_execution_surface_promotion_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase6_execution_surface_promotion_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase6_execution_surface_promotion_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase6_execution_surface_promotion_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase13_operator_intelligence_entry_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase13_operator_intelligence_entry_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase13_operator_intelligence_entry_receipt_001.latest.md": "markdown",
        "out/sync/phase13_notion_sync_packet_001.latest.json": "json",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        if artifact_path.startswith("out/sync/"):
            assert entry.canonical_generator == (
                "scripts/run_phase13_notion_sync_packet.py"
            )
        else:
            assert entry.canonical_generator == (
                "scripts/run_v2_hygiene_phase13_operator_intelligence_entry_receipt.py"
            )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase13_operator_intelligence_closure_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase13_operator_intelligence_closure_receipt_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase13_operator_intelligence_closure_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase13_operator_intelligence_closure_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase8_execution_surface_expansion_advisory_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase8_execution_surface_expansion_advisory_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase8_execution_surface_expansion_advisory_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase8_execution_surface_expansion_advisory_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase9_controlled_execution_promotion_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase9_controlled_execution_promotion_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase9_controlled_execution_promotion_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase9_controlled_execution_promotion_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase11_full_operator_execution_autonomy_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase11_full_operator_execution_autonomy_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase11_full_operator_execution_autonomy_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase11_full_operator_execution_autonomy_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase13_autonomy_activation_brier_hardening_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase13_autonomy_activation_brier_hardening_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase14_runtime_execution_surface_activation_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase14_runtime_execution_surface_activation_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase14_runtime_execution_surface_activation_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase14_runtime_execution_surface_activation_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase16_live_runtime_execution_signal_forage_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase16_live_runtime_execution_signal_forage_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase17_full_live_autonomy_self_optimization_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase17_full_live_autonomy_self_optimization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase18_eternal_recursion_hyperstition_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase18_eternal_recursion_hyperstition_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase18_eternal_recursion_hyperstition_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase18_eternal_recursion_hyperstition_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase19_eternal_canon_self_governance_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase19_eternal_canon_self_governance_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase19_eternal_canon_self_governance_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase19_eternal_canon_self_governance_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase21_canon_activation_authorization_review_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase21_canon_activation_authorization_review_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase21_canon_activation_authorization_review_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase21_canon_activation_authorization_review_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_stabilization_review_chain_compression_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_stabilization_review_chain_compression_audit_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_stabilization_review_chain_compression_audit_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_stabilization_review_chain_compression_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_authorization_record_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_authorization_record_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_authorization_record_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_authorization_record_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_authorization_record_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_authorization_record_dry_run_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_review_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_authorization_record_dry_run_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_authorization_record_review_evidence_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_authorization_record_review_evidence_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase2_governance_evidence_request_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase2_governance_evidence_request_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase2_governance_evidence_request_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase2_governance_evidence_request_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_schema_contract_evidence_request_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_schema_contract_evidence_request_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_schema_contract_evidence_request_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_schema_contract_evidence_request_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_schema_contract_evidence_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_001.latest.json": "json",
        "out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_schema_contract_evidence_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_schema_contract_evidence_dry_run_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_review_001.latest.json": "json",
        "out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_schema_contract_evidence_dry_run_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase2_governance_evidence_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase2_governance_evidence_dry_run_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase2_governance_evidence_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase2_governance_evidence_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_authorization_record_review_evidence_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_rune_yggdrasil_integration_needs_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_aal_viz_projection_bindings_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_continuity_lane_conventions_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_continuity_lane_conventions_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_continuity_lane_conventions_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_continuity_lane_conventions_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_artifact_registry_integration_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_artifact_registry_integration_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_artifact_registry_integration_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_artifact_registry_integration_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_failure_taxonomy_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_failure_taxonomy_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_failure_taxonomy_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_failure_taxonomy_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_testing_validation_strategy_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_testing_validation_strategy_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_testing_validation_strategy_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_testing_validation_strategy_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_harness_implementation_roadmap_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_harness_implementation_roadmap_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_harness_implementation_roadmap_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_code_detail_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_phase1_code_detail_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_phase1_code_detail_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_phase1_code_detail_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_harness_interface_spec_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_harness_interface_spec_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_harness_interface_spec_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_harness_interface_spec_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_operator_decision_record_template_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_operator_decision_record_template_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_operator_decision_record_template_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_operator_decision_record_template_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_meta_gate_authorization_record_template_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_self_improvement_boundary_policy_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_shadow_replay_integration_exploration_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_improvement_proposal_shadow_replay_wiring_spec_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_sample_meta_gate_chain_validation_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_sample_fixture_normalization_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_sample_fixture_normalization_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_sample_fixture_normalization_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_sample_fixture_normalization_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_governance_decision_vocabulary_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_canon_shadow_formalization_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_canon_shadow_formalization_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_canon_shadow_formalization_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_canon_shadow_formalization_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_object_model_schema_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_object_model_schema_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_object_model_schema_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_object_model_schema_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_module_surface_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_module_surface_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_module_surface_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_module_surface_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_schema_master_registry_alignment_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_recommended_patch_sequence_precondition_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_merge_anchor_coverage_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_merge_anchor_coverage_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_merge_anchor_coverage_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_merge_anchor_evidence_request_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_merge_anchor_evidence_normalization_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_boundary_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_phase1_implementation_boundary_review_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_phase1_implementation_boundary_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_phase1_implementation_boundary_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_request_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_evidence_packet_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/abx_codegen_intelligence_spine_phase1_operator_evidence_packet_001.latest.json": "json",
        "out/audit/abx_codegen_intelligence_spine_phase1_operator_evidence_packet_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_intelligence_spine_phase1_operator_evidence_packet.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_abx_codegen_merge_anchor_source_selection_request_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_merge_anchor_source_selection_request_001.latest.json": "json",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_request_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_merge_anchor_source_selection_request.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_merge_anchor_source_selection_decision_record_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_plan_001.latest.json": "json",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_merge_anchor_source_selection_decision_record_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_merge_anchor_source_selection_decision_record_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_dry_run_001.latest.json": "json",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_merge_anchor_source_selection_decision_record_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_merge_anchor_source_selection_decision_record_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_review_001.latest.json": "json",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_merge_anchor_source_selection_decision_record_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_record_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_record_plan_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_record_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_record_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_record_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_record_dry_run_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_record_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_record_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_record_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_record_review_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_record_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_record_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_evidence_collection_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_plan_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_evidence_collection_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_evidence_collection_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_dry_run_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_evidence_collection_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_grok_abx_runes_operator_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/grok_abx_runes_reconciliation_plan_001.latest.json": (
            "scripts/run_grok_abx_runes_reconciliation_plan.py",
            "json",
        ),
        "out/operator_review/grok_abx_runes_reconciliation_plan_001.latest.md": (
            "scripts/run_grok_abx_runes_reconciliation_plan.py",
            "markdown",
        ),
        "out/operator_review/grok_abx_runes_operator_decision_record_plan_001.latest.json": (
            "scripts/run_grok_abx_runes_operator_decision_record_plan.py",
            "json",
        ),
        "out/operator_review/grok_abx_runes_operator_decision_record_plan_001.latest.md": (
            "scripts/run_grok_abx_runes_operator_decision_record_plan.py",
            "markdown",
        ),
        "out/operator_review/grok_abx_runes_operator_decision_record_dry_run_001.latest.json": (
            "scripts/run_grok_abx_runes_operator_decision_record_dry_run.py",
            "json",
        ),
        "out/operator_review/grok_abx_runes_operator_decision_record_dry_run_001.latest.md": (
            "scripts/run_grok_abx_runes_operator_decision_record_dry_run.py",
            "markdown",
        ),
        "out/operator_review/grok_abx_runes_operator_decision_record_review_001.latest.json": (
            "scripts/run_grok_abx_runes_operator_decision_record_review.py",
            "json",
        ),
        "out/operator_review/grok_abx_runes_operator_decision_record_review_001.latest.md": (
            "scripts/run_grok_abx_runes_operator_decision_record_review.py",
            "markdown",
        ),
        "out/operator_review/grok_abx_runes_operator_decision_evidence_collection_plan_001.latest.json": (
            "scripts/run_grok_abx_runes_operator_decision_evidence_collection_plan.py",
            "json",
        ),
        "out/operator_review/grok_abx_runes_operator_decision_evidence_collection_plan_001.latest.md": (
            "scripts/run_grok_abx_runes_operator_decision_evidence_collection_plan.py",
            "markdown",
        ),
        "out/operator_review/grok_abx_runes_operator_decision_evidence_collection_dry_run_001.latest.json": (
            "scripts/run_grok_abx_runes_operator_decision_evidence_collection_dry_run.py",
            "json",
        ),
        "out/operator_review/grok_abx_runes_operator_decision_evidence_collection_dry_run_001.latest.md": (
            "scripts/run_grok_abx_runes_operator_decision_evidence_collection_dry_run.py",
            "markdown",
        ),
        "out/operator_review/grok_abx_runes_operator_review_chain_compression_receipt_001.latest.json": (
            "scripts/run_grok_abx_runes_operator_review_chain_compression_receipt.py",
            "json",
        ),
        "out/operator_review/grok_abx_runes_operator_review_chain_compression_receipt_001.latest.md": (
            "scripts/run_grok_abx_runes_operator_review_chain_compression_receipt.py",
            "markdown",
        ),
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, (generator, artifact_kind) in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == generator
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_review_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_001.latest.json": "json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_loop_awareness_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_hygiene_loop_awareness_audit/latest.json": "json",
        "out/sync/v2_hygiene_loop_awareness_audit/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == "scripts/run_v2_hygiene_loop_awareness_audit.py"
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_loop_awareness_alignment_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.json": "json",
        "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == "scripts/run_v2_hygiene_loop_awareness_alignment_plan.py"
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_upgrade_completion_reconciliation_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_upgrade_completion_reconciliation/latest.json": "json",
        "out/sync/v2_upgrade_completion_reconciliation/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == "scripts/run_v2_upgrade_completion_reconciliation.py"
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_live_notion_surface_reconciliation_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_live_notion_surface_reconciliation/latest.json": "json",
        "out/sync/v2_live_notion_surface_reconciliation/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_live_notion_surface_reconciliation.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_registration_readiness_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_hygiene_registration_readiness_audit/latest.json": "json",
        "out/sync/v2_hygiene_registration_readiness_audit/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_registration_readiness_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_loop_awareness_operator_authorization_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_loop_awareness_operator_authorization_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase2_module_skeleton_backlog_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_hygiene_phase2_module_skeleton_backlog_plan/latest.json": "json",
        "out/sync/v2_hygiene_phase2_module_skeleton_backlog_plan/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase2_module_skeleton_backlog_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase2_module_governance_readiness_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_hygiene_phase2_module_governance_readiness_audit/latest.json": "json",
        "out/sync/v2_hygiene_phase2_module_governance_readiness_audit/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase2_module_governance_readiness_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_future_phase_placeholder_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_hygiene_future_phase_placeholder_audit/latest.json": "json",
        "out/sync/v2_hygiene_future_phase_placeholder_audit/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_future_phase_placeholder_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_operator_authorization_evidence_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_operator_authorization_evidence_dry_run_001.latest.json": "json",
        "out/operator_review/v2_hygiene_operator_authorization_evidence_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_operator_authorization_evidence_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_v2_hygiene_operator_authorization_evidence_validation_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_operator_authorization_evidence_validation_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_v2_hygiene_operator_authorization_evidence_validation_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_001.latest.json": "json",
        "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_operator_authorization_evidence_validation_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review_001.latest.json": "json",
        "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_001.latest.json": "json",
        "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        if entry.tracked:
            assert entry.determinism_class == "BUILD_CANONICAL"
            assert artifact_path in ci_drift_paths
        else:
            assert entry.determinism_class == "DERIVED_OPTIONAL"
            assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_review_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_review_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_review_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_review.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_authorization_chain_compression_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_authorization_chain_compression_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_schema_contract_readiness_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_hygiene_schema_contract_readiness_audit/latest.json": "json",
        "out/sync/v2_hygiene_schema_contract_readiness_audit/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_schema_contract_readiness_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_versioning_release_policy_readiness_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_hygiene_versioning_release_policy_readiness_audit/latest.json": "json",
        "out/sync/v2_hygiene_versioning_release_policy_readiness_audit/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_versioning_release_policy_readiness_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase1_acceptance_checklist_readiness_audit_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/sync/v2_hygiene_phase1_acceptance_checklist_readiness_audit/latest.json": "json",
        "out/sync/v2_hygiene_phase1_acceptance_checklist_readiness_audit/latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_v2_hygiene_phase1_acceptance_checklist_readiness_audit.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_runtime_integration_gate_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/runtime_integration_gate_receipt_001.latest.json": "json",
        "out/audit/runtime_integration_gate_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == "scripts/run_runtime_integration_gate_receipt.py"
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind


def test_runtime_integration_gate_operator_review_plan_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/runtime_integration_gate_operator_review_advisory_spec_plan_001.latest.json": "json",
        "out/audit/runtime_integration_gate_operator_review_advisory_spec_plan_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_runtime_integration_gate_operator_review_advisory_spec_plan.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind


def test_continuation_frontier_reconciliation_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/continuation_frontier_reconciliation_001.latest.json": (
            "json",
            "DERIVED_OPTIONAL",
            False,
        ),
        "out/audit/continuation_frontier_reconciliation_001.latest.md": (
            "markdown",
            "BUILD_CANONICAL",
            True,
        ),
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, (artifact_kind, determinism_class, drift_enforced) in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_continuation_frontier_reconciliation.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == determinism_class
        assert (artifact_path in ci_drift_paths) is drift_enforced


def test_notion_repo_sync_audit_writeback_receipt_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/audit/notion_repo_sync_audit_writeback_receipt_001.latest.json": "json",
        "out/audit/notion_repo_sync_audit_writeback_receipt_001.latest.md": "markdown",
    }
    entries = {
        entry.artifact_path: entry
        for entry in registry.entries
        if entry.artifact_path in expected
    }
    assert set(entries) == set(expected)
    ci_drift_paths = list_ci_drift_artifact_paths(registry)
    for artifact_path, artifact_kind in expected.items():
        entry = entries[artifact_path]
        assert entry.canonical_generator == (
            "scripts/run_notion_repo_sync_audit_writeback_receipt.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_validate_only_aliases_are_equivalent() -> None:
    validation_only_args = run_artifact_regeneration._parse_args(["--validation-only"])
    validate_only_args = run_artifact_regeneration._parse_args(["--validate-only"])
    assert validation_only_args.validation_only is True
    assert validate_only_args.validation_only is True
    assert run_artifact_regeneration._resolve_selection(validation_only_args) == (True, None)
    assert run_artifact_regeneration._resolve_selection(validate_only_args) == (True, None)


def test_detect_ci_artifact_drift_paths_ignores_runtime_volatile(tmp_path: Path) -> None:
    repo_root = tmp_path
    tracked = repo_root / "out" / "contracts" / "stable.latest.json"
    runtime = repo_root / "out" / "validation" / "latest.json"
    tracked.parent.mkdir(parents=True, exist_ok=True)
    runtime.parent.mkdir(parents=True, exist_ok=True)
    tracked.write_text('{"stable":true}\n', encoding="utf-8")
    runtime.write_text('{"summary":{"status":"passed"}}\n', encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "ci@example.com"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "CI"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    registry = _registry_for(
        [
            GeneratedArtifactEntry(
                artifact_path="out/contracts/stable.latest.json",
                canonical_generator="scripts/gen.py",
                canonical_schema="Stable.v1",
                deterministic_inputs=[],
                regeneration_required=False,
                committed_policy="tracked-derived",
                downstream_dependencies=[],
                final_status="managed",
                artifact_kind="json",
                tracked=True,
                determinism_class="BUILD_CANONICAL",
            ),
            GeneratedArtifactEntry(
                artifact_path="out/validation/latest.json",
                canonical_generator="scripts/gen_runtime.py",
                canonical_schema="Runtime.v1",
                deterministic_inputs=[],
                regeneration_required=False,
                committed_policy="tracked-derived",
                downstream_dependencies=[],
                final_status="managed",
                artifact_kind="json",
                tracked=True,
                determinism_class="RUNTIME_VOLATILE",
            ),
        ]
    )

    runtime.write_text('{"summary":{"status":"not_computable"}}\n', encoding="utf-8")
    assert detect_ci_artifact_drift_paths(registry, repo_root=repo_root) == []

    tracked.write_text('{"stable":false}\n', encoding="utf-8")
    assert detect_ci_artifact_drift_paths(registry, repo_root=repo_root) == [
        "out/contracts/stable.latest.json"
    ]


def test_tracked_paths_returns_empty_set_outside_git_checkout(tmp_path: Path) -> None:
    from core.generated_artifact_registry import _tracked_paths

    assert _tracked_paths(tmp_path) == set()


def test_tracked_paths_non_git_calls_are_deterministic(tmp_path: Path) -> None:
    from core.generated_artifact_registry import _tracked_paths

    first = _tracked_paths(tmp_path)
    second = _tracked_paths(tmp_path)
    assert first == set()
    assert second == set()
    assert first == second


def test_tracked_paths_preserves_git_stdout_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    from core.generated_artifact_registry import _tracked_paths

    class _Result:
        def __init__(self) -> None:
            self.returncode = 0
            self.stdout = "out/contracts/a.latest.json\n\nout/contracts/b.latest.json\n"

    def _fake_run(*args: object, **kwargs: object) -> _Result:
        return _Result()

    monkeypatch.setattr("core.generated_artifact_registry.subprocess.run", _fake_run)

    assert _tracked_paths(REPO_ROOT) == {
        "out/contracts/a.latest.json",
        "out/contracts/b.latest.json",
    }


def test_detect_ci_artifact_drift_paths_non_git_empty_targets_returns_empty(
    tmp_path: Path,
) -> None:
    registry = _registry_for([])
    assert detect_ci_artifact_drift_paths(registry, repo_root=tmp_path) == []


def test_detect_ci_artifact_drift_paths_non_git_empty_targets_deterministic(
    tmp_path: Path,
) -> None:
    registry = _registry_for([])
    first = detect_ci_artifact_drift_paths(registry, repo_root=tmp_path)
    second = detect_ci_artifact_drift_paths(registry, repo_root=tmp_path)
    assert first == []
    assert second == []
    assert first == second


def test_detect_ci_artifact_drift_paths_git_empty_targets_raises(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    registry = _registry_for([])
    with pytest.raises(ValueError, match="no deterministic CI drift targets declared"):
        detect_ci_artifact_drift_paths(registry, repo_root=tmp_path)
