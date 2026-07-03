from __future__ import annotations

import json
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
    execute_artifact_regeneration,
    list_ci_drift_artifact_paths,
)
from scripts import run_artifact_regeneration


REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER_FRONTIER_RECEIPT = (
    "out/audit/abx_ledger_frontier_reconcile_denial_001.latest.json"
)
LEDGER_FRONTIER_HASH = (
    "0b28044325cad08cad70e89f895f4a45729b68f6240fcd7c40b2331e45d77066"
)
SLICE49_TEMPORAL_RECEIPT = (
    "out/audit/temporal_coherence_evidence_restoration_planning_001.latest.json"
)
SLICE50_TEMPORAL_AUTHORIZATION_RECEIPT = (
    "out/audit/temporal_continuity_authorization_source_status_audit_001.latest.json"
)
SLICE51_P80_REGENERATION_RECEIPT = (
    "out/audit/temporal_continuity_p80_authorization_record_regeneration_receipt_001.latest.json"
)
VIZ01_LIVE_FEED_RECEIPT = "out/audit/viz01_live_feed_enhancement_receipt_001.latest.json"
GEOMETRIC_BINDER_ORCHESTRATOR_RECEIPT = (
    "out/audit/geometric_binder_orchestrator_integration_harness_001.latest.json"
)
HYPERSTITION_BRIER_FIXTURE_RECEIPT = (
    "out/audit/hyperstition_brier_fixture_expansion_receipt_001.latest.json"
)
HYPERSTITION_EVALUATOR_DEEPENING_RECEIPT = (
    "out/audit/hyperstition_evaluator_deepening_receipt_001.latest.json"
)
RUNE_INTEGRITY_SCANNER_GUARDRAILS_RECEIPT = (
    "out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json"
)
RUNE_INTEGRITY_CI_WORKFLOW_WIRING_RECEIPT = (
    "out/audit/rune_integrity_ci_workflow_wiring_001.latest.json"
)
DOCS_NAVIGATION_REFRESH_RECEIPT = (
    "out/audit/docs_navigation_refresh_001.latest.json"
)
SUBSYSTEM_OWNERSHIP_MATRIX_REFRESH_RECEIPT = (
    "out/audit/subsystem_ownership_matrix_refresh_001.latest.json"
)
ARTIFACT_REGISTRY_CLASSIFIER_RECEIPT = (
    "out/audit/artifact_registry_classifier_001.latest.json"
)
SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT = (
    "out/audit/subsystem_health_dashboard_001.latest.json"
)
CONTINUITY_NAMESPACE_MIGRATION_TOOLING_REFRESH_RECEIPT = (
    "out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json"
)
CONTINUITY_NAMESPACE_MIGRATION_RUN_RECEIPT = (
    "out/audit/continuity_namespace_migration_run_001.latest.json"
)
LIVE_CONSOLE_MIGRATION_RUNNER_POSTURE_RECEIPT = (
    "out/audit/live_console_migration_runner_posture_001.latest.json"
)
LIVE_PROJECTION_HEALTH_MIGRATION_ARTIFACT_RECEIPT = (
    "out/audit/live_projection_health_migration_artifact_001.latest.json"
)
LIVE_CONSOLE_WEBSOCKET_HARDENING_RECEIPT = (
    "out/audit/live_console_websocket_hardening_001.latest.json"
)
LIVE_CONSOLE_UI_POLISH_RECEIPT = "out/audit/live_console_ui_polish_001.latest.json"
PRIORITY2_LIVE_CONSOLE_MIGRATION_CLOSEOUT_RECEIPT = (
    "out/audit/priority2_live_console_migration_closeout_001.latest.json"
)


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


def test_abx_ledger_frontier_reconcile_denial_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == LEDGER_FRONTIER_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "scripts/run_abx_ledger_frontier_reconcile_denial.py"
    )
    assert entry.final_status == "managed"
    assert entry.tracked is True
    assert entry.determinism_class == "BUILD_CANONICAL"
    assert entry.artifact_kind == "json"
    assert entry.artifact_path in list_ci_drift_artifact_paths(registry)


def test_abx_ledger_frontier_reconcile_denial_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[LEDGER_FRONTIER_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "scripts/run_abx_ledger_frontier_reconcile_denial.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_abx_ledger_frontier_reconcile_denial_round_trip_hash_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    receipt_path = REPO_ROOT / LEDGER_FRONTIER_RECEIPT

    for _ in range(2):
        plan = execute_artifact_regeneration(
            registry,
            repo_root=REPO_ROOT,
            selected_artifacts=[LEDGER_FRONTIER_RECEIPT],
        )
        assert plan.final_status == "PASS"
        assert plan.statuses[0].drift_detected is False
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert receipt["canonical_hash"] == LEDGER_FRONTIER_HASH


def test_slice49_temporal_coherence_planning_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == SLICE49_TEMPORAL_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_temporal_coherence_evidence_restoration_planning.py"
    )
    assert entry.final_status == "managed"
    assert entry.artifact_kind == "json"
    if entry.tracked:
        assert entry.determinism_class == "BUILD_CANONICAL"
        assert entry.artifact_path in list_ci_drift_artifact_paths(registry)
    else:
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert entry.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_slice50_temporal_authorization_source_status_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == SLICE50_TEMPORAL_AUTHORIZATION_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_temporal_continuity_authorization_source_status_audit_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.artifact_kind == "json"
    if entry.tracked:
        assert entry.determinism_class == "BUILD_CANONICAL"
        assert entry.artifact_path in list_ci_drift_artifact_paths(registry)
    else:
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert entry.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_slice50_temporal_authorization_source_status_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[SLICE50_TEMPORAL_AUTHORIZATION_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_temporal_continuity_authorization_source_status_audit_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_slice51_p80_authorization_record_regeneration_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == SLICE51_P80_REGENERATION_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_temporal_continuity_p80_authorization_record_regeneration_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.artifact_kind == "json"
    if entry.tracked:
        assert entry.determinism_class == "BUILD_CANONICAL"
        assert entry.artifact_path in list_ci_drift_artifact_paths(registry)
    else:
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert entry.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_slice53_geometric_binder_orchestrator_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == GEOMETRIC_BINDER_ORCHESTRATOR_RECEIPT
    )
    assert entry.canonical_generator == (
        "Scripts/run_geometric_binder_orchestrator_integration_harness.py"
    )
    assert entry.final_status == "managed"
    assert entry.artifact_kind == "json"
    if entry.tracked:
        assert entry.determinism_class == "BUILD_CANONICAL"


def test_slice53_geometric_binder_orchestrator_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[GEOMETRIC_BINDER_ORCHESTRATOR_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_geometric_binder_orchestrator_integration_harness.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_slice54_hyperstition_brier_fixture_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == HYPERSTITION_BRIER_FIXTURE_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_hyperstition_brier_fixture_expansion_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.artifact_kind == "json"
    if entry.tracked:
        assert entry.determinism_class == "BUILD_CANONICAL"
        assert entry.artifact_path in list_ci_drift_artifact_paths(registry)
    else:
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert entry.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_slice54_hyperstition_brier_fixture_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[HYPERSTITION_BRIER_FIXTURE_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_hyperstition_brier_fixture_expansion_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_slice55_hyperstition_evaluator_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == HYPERSTITION_EVALUATOR_DEEPENING_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_hyperstition_evaluator_deepening_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.artifact_kind == "json"
    if entry.tracked:
        assert entry.determinism_class == "BUILD_CANONICAL"
        assert entry.artifact_path in list_ci_drift_artifact_paths(registry)
    else:
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert entry.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_slice55_hyperstition_evaluator_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[HYPERSTITION_EVALUATOR_DEEPENING_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_hyperstition_evaluator_deepening_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_slice56_rune_integrity_scanner_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == RUNE_INTEGRITY_SCANNER_GUARDRAILS_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_rune_integrity_scanner_guardrails_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.artifact_kind == "json"
    if entry.tracked:
        assert entry.determinism_class == "BUILD_CANONICAL"
        assert entry.artifact_path in list_ci_drift_artifact_paths(registry)
    else:
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert entry.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_slice56_rune_integrity_scanner_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[RUNE_INTEGRITY_SCANNER_GUARDRAILS_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_rune_integrity_scanner_guardrails_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_slice70_rune_integrity_ci_workflow_wiring_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == RUNE_INTEGRITY_CI_WORKFLOW_WIRING_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_rune_integrity_ci_workflow_wiring_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.artifact_kind == "json"
    if entry.tracked:
        assert entry.determinism_class == "BUILD_CANONICAL"
        assert entry.artifact_path in list_ci_drift_artifact_paths(registry)
    else:
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert entry.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_slice70_rune_integrity_ci_workflow_wiring_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[RUNE_INTEGRITY_CI_WORKFLOW_WIRING_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_rune_integrity_ci_workflow_wiring_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_slice57_docs_navigation_refresh_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == DOCS_NAVIGATION_REFRESH_RECEIPT
    )
    assert entry.canonical_generator == "Scripts/run_docs_navigation_refresh_receipt.py"
    assert entry.final_status == "managed"
    assert entry.artifact_kind == "json"


def test_slice57_docs_navigation_refresh_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[DOCS_NAVIGATION_REFRESH_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == ["Scripts/run_docs_navigation_refresh_receipt.py"]
    assert plan.statuses[0].drift_detected is False


def test_slice58_subsystem_ownership_matrix_refresh_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == SUBSYSTEM_OWNERSHIP_MATRIX_REFRESH_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_subsystem_ownership_matrix_refresh_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.artifact_kind == "json"


def test_slice58_subsystem_ownership_matrix_refresh_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[SUBSYSTEM_OWNERSHIP_MATRIX_REFRESH_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_subsystem_ownership_matrix_refresh_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_slice51_p80_authorization_record_regeneration_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[SLICE51_P80_REGENERATION_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_temporal_continuity_p80_authorization_record_regeneration_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_viz01_live_feed_enhancement_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item for item in registry.entries if item.artifact_path == VIZ01_LIVE_FEED_RECEIPT
    )
    assert entry.canonical_generator == "Scripts/run_viz01_live_feed_enhancement_receipt.py"
    assert entry.final_status == "managed"
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[VIZ01_LIVE_FEED_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.statuses[0].drift_detected is False


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


def test_v2_hygiene_phase23_live_execution_activation_authorization_review_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase23_live_execution_activation_authorization_review_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase23_live_execution_activation_authorization_review_gate_001.latest.md": "markdown",
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
            "scripts/run_v2_hygiene_phase23_live_execution_activation_authorization_review_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate_001.latest.md": "markdown",
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
            "scripts/run_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate.py"
        )
        assert entry.final_status == "managed"
        assert entry.artifact_kind == artifact_kind
        assert entry.determinism_class == "DERIVED_OPTIONAL"
        assert artifact_path not in ci_drift_paths


def test_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate_artifacts_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    expected = {
        "out/operator_review/v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate_001.latest.json": "json",
        "out/operator_review/v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate_001.latest.md": "markdown",
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
            "scripts/run_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate.py"
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


def test_artifact_registry_classifier_receipt_uses_no_arg_wrapper() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == ARTIFACT_REGISTRY_CLASSIFIER_RECEIPT
    )

    assert entry.canonical_generator == "Scripts/run_artifact_registry_classifier_receipt.py"
    assert entry.final_status == "managed"


def test_artifact_registry_classifier_receipt_regenerates_without_extra_args() -> None:
    result = subprocess.run(
        [
            "python",
            "scripts/run_artifact_regeneration.py",
            "--artifact",
            ARTIFACT_REGISTRY_CLASSIFIER_RECEIPT,
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "artifact_registry_classifier_001.latest.json" in result.stdout


def test_continuity_lineage_map_refresh_receipt_uses_no_arg_wrapper() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == "out/audit/continuity_lineage_map_refresh_001.latest.json"
    )

    assert entry.canonical_generator == "Scripts/run_continuity_lineage_map_refresh_receipt.py"
    assert entry.final_status == "managed"


def test_continuity_lineage_map_refresh_receipt_regenerates_without_extra_args() -> None:
    result = subprocess.run(
        [
            "python",
            "scripts/run_artifact_regeneration.py",
            "--artifact",
            "out/audit/continuity_lineage_map_refresh_001.latest.json",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "continuity_lineage_map_refresh_001.latest.json" in result.stdout


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


def test_subsystem_health_dashboard_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_subsystem_health_dashboard_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.tracked is True
    assert entry.determinism_class == "BUILD_CANONICAL"
    assert entry.artifact_kind == "json"
    assert entry.artifact_path in list_ci_drift_artifact_paths(registry)


def test_subsystem_health_dashboard_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[SUBSYSTEM_HEALTH_DASHBOARD_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_subsystem_health_dashboard_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_continuity_namespace_migration_tooling_refresh_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == CONTINUITY_NAMESPACE_MIGRATION_TOOLING_REFRESH_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.tracked is True
    assert entry.determinism_class == "BUILD_CANONICAL"
    assert entry.artifact_kind == "json"
    assert entry.artifact_path in list_ci_drift_artifact_paths(registry)


def test_continuity_namespace_migration_tooling_refresh_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[CONTINUITY_NAMESPACE_MIGRATION_TOOLING_REFRESH_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_continuity_namespace_migration_run_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == CONTINUITY_NAMESPACE_MIGRATION_RUN_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_continuity_namespace_migration_runner.py"
    )
    assert entry.final_status == "managed"
    assert entry.tracked is True
    assert entry.determinism_class == "BUILD_CANONICAL"
    assert entry.artifact_kind == "json"
    assert entry.artifact_path in list_ci_drift_artifact_paths(registry)


def test_continuity_namespace_migration_run_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[CONTINUITY_NAMESPACE_MIGRATION_RUN_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_continuity_namespace_migration_runner.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_live_console_migration_runner_posture_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == LIVE_CONSOLE_MIGRATION_RUNNER_POSTURE_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_live_console_migration_runner_posture_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.tracked is True
    assert entry.determinism_class == "BUILD_CANONICAL"
    assert entry.artifact_kind == "json"
    assert entry.artifact_path in list_ci_drift_artifact_paths(registry)


def test_live_console_migration_runner_posture_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[LIVE_CONSOLE_MIGRATION_RUNNER_POSTURE_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_live_console_migration_runner_posture_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_live_projection_health_migration_artifact_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == LIVE_PROJECTION_HEALTH_MIGRATION_ARTIFACT_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_live_projection_health_migration_artifact_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.tracked is True
    assert entry.determinism_class == "BUILD_CANONICAL"
    assert entry.artifact_kind == "json"
    assert entry.artifact_path in list_ci_drift_artifact_paths(registry)


def test_live_projection_health_migration_artifact_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[LIVE_PROJECTION_HEALTH_MIGRATION_ARTIFACT_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_live_projection_health_migration_artifact_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_live_console_websocket_hardening_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == LIVE_CONSOLE_WEBSOCKET_HARDENING_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_live_console_websocket_hardening_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.tracked is True
    assert entry.determinism_class == "BUILD_CANONICAL"
    assert entry.artifact_kind == "json"
    assert entry.artifact_path in list_ci_drift_artifact_paths(registry)


def test_live_console_websocket_hardening_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[LIVE_CONSOLE_WEBSOCKET_HARDENING_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_live_console_websocket_hardening_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False


def test_live_console_ui_polish_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item for item in registry.entries if item.artifact_path == LIVE_CONSOLE_UI_POLISH_RECEIPT
    )
    assert entry.canonical_generator == "Scripts/run_live_console_ui_polish_receipt.py"
    assert entry.final_status == "managed"
    assert entry.tracked is True
    assert entry.determinism_class == "BUILD_CANONICAL"
    assert entry.artifact_kind == "json"
    assert entry.artifact_path in list_ci_drift_artifact_paths(registry)


def test_live_console_ui_polish_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[LIVE_CONSOLE_UI_POLISH_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == ["Scripts/run_live_console_ui_polish_receipt.py"]
    assert plan.statuses[0].drift_detected is False


def test_priority2_live_console_migration_closeout_artifact_classification_stable() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path == PRIORITY2_LIVE_CONSOLE_MIGRATION_CLOSEOUT_RECEIPT
    )
    assert (
        entry.canonical_generator
        == "Scripts/run_priority2_live_console_migration_closeout_receipt.py"
    )
    assert entry.final_status == "managed"
    assert entry.tracked is True
    assert entry.determinism_class == "BUILD_CANONICAL"
    assert entry.artifact_kind == "json"
    assert entry.artifact_path in list_ci_drift_artifact_paths(registry)


def test_priority2_live_console_migration_closeout_regenerates_without_cli_args() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=REPO_ROOT,
        selected_artifacts=[PRIORITY2_LIVE_CONSOLE_MIGRATION_CLOSEOUT_RECEIPT],
    )
    assert plan.final_status == "PASS"
    assert plan.generator_sequence == [
        "Scripts/run_priority2_live_console_migration_closeout_receipt.py"
    ]
    assert plan.statuses[0].drift_detected is False
