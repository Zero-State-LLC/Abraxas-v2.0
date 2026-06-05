# ABX Artifact Lineage Registry Completion Plan

- `plan_id`: `ABX_ARTIFACT_LINEAGE_REGISTRY_COMPLETION_PLAN_001`
- `generated_at`: `2026-06-05T00:00:00Z`
- `source_backlog`: `ABX_NOT_COMPUTABLE_COMPLETION_BACKLOG_001`
- `source_research_application`: `ABX_RESEARCH_COMPLETION_APPLICATION_001`
- `recommended_next_plan`: `ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_001`
- `downstream`: `NOT_COMPUTABLE`
- `canon_status`: `ADVISORY_ONLY`

## Target NOT_COMPUTABLE Clusters
- `runtime_spine_audit_aggregator`: `NOT_COMPUTABLE` via `detect_artifacts_with_outputs_but_no_registry_entry`
- `missing_replay_repair_batch`: `NOT_COMPUTABLE` via `preserve_unresolved_cases_as_NOT_COMPUTABLE`
- `missing_artifact_repair_batch`: `NOT_COMPUTABLE` via `detect_registry_entries_with_no_runner`
- `uppercase_scripts_runner_visibility`: `NOT_COMPUTABLE` via `detect_uppercase_Scripts_runner_discovery_gaps`
- `systemwide_integration_matrix_gaps`: `NOT_COMPUTABLE` via `detect_schemas_with_no_tests`
- `orphaned_subsystem_status`: `NOT_COMPUTABLE` via `detect_docs_references_to_missing_artifacts`
- `dashboard_projection_traceability`: `NOT_COMPUTABLE` via `detect_generated_outputs_with_no_notion_surface`
- `artifact_registry_runner_discovery_gap`: `NOT_COMPUTABLE` via `detect_registry_entries_with_no_runner`

## Required Repo Scans
- `core/generated_artifact_registry.py`
- `scripts/run_*.py`
- `Scripts/run_*.py`
- `contracts/**/*.schema.json`
- `out/**/*.json`
- `out/**/*.md`
- `docs/**/*.md`
- `tests/test_*.py`
- `README.md`
- `AGENTS.md`
- `PLANS.md`

## Forbidden Actions
- `implement_runtime_execution`
- `promote_research_to_canon`
- `create_downstream_lanes`
- `mutate_governance`
- `authorize_operator_decisions`
- `infer_missing_artifacts_as_present`
- `treat_lineage_as_correctness_proof`
- `treat_calibrated_confidence_as_authorization`
- `delete_or_rewrite_existing_artifacts`
- `rename_runner_paths_without_operator_review`

## Governance Locks
- `governance_status`: `FROZEN`
- `canon_status`: `ADVISORY_ONLY`
- `execution_authority`: `False`
- `canon_mutation_allowed`: `False`
- `runtime_mutation_allowed`: `False`
- `research_candidates_canonized`: `False`
- `downstream`: `NOT_COMPUTABLE`
- `operator_review_required`: `True`
