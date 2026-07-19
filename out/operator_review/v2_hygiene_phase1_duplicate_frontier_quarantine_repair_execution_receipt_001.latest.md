# v2.0 Hygiene Phase 1 Duplicate Frontier Quarantine Repair Execution Receipt

- receipt_id: v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001
- status: V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_REPAIR_EXECUTION_RECEIPT_READY
- source_readiness: SOURCE_ARTIFACTS_READY
- repair_attempted: False
- repair_performed: True
- repair_already_complete_before_run: True
- scoped_duplicate_deletion_authorized: True
- ready_for_subsystem_implementation_authorization_gate: False
- recommended_next_lane: NOT_COMPUTABLE
- downstream: NOT_COMPUTABLE
- valid_for_implementation: False
- valid_for_execution: False

## Repair Summary
- source_manifest_count: 466
- preflight_eligible_count: 466
- preflight_blocked_count: 0
- deleted_path_count: 466
- held_path_count: 0
- post_duplicate_remaining_count: 0
- canonical_counterparts_remaining_count: 466
- by_classification: {'CODEGEN_FIXTURE_BLOCKER': 1, 'GENERATED_OUTPUT_DUPLICATE': 83, 'PYTEST_COLLECTION_BLOCKER': 112, 'SAFE_DUPLICATE_CANDIDATE': 270}

## Validation Plan
- python -m pytest tests/test_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt.py tests/test_generated_artifact_registry.py::test_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_artifacts_classification_stable -q (required=True)
- python scripts/artifact/run_artifact_regeneration.py --artifact out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.json --artifact out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.md --validation-only (required=True)
- python scripts/artifact/run_artifact_regeneration.py --check-drift (required=True)
- python scripts/run_fast_ci.py (required=True)

## Source Blockers
- none

## Preflight Blockers
- none
