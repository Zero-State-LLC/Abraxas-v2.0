# v2.0 Hygiene Phase 1 Duplicate Frontier Quarantine Design Receipt

- receipt_id: v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_001
- status: V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_DESIGN_RECEIPT_READY
- source_readiness: SOURCE_ARTIFACTS_READY
- ready_for_subsystem_implementation_authorization_gate: False
- recommended_next_lane: NOT_COMPUTABLE
- downstream: NOT_COMPUTABLE
- safe_to_auto_continue: False
- valid_for_implementation: False
- valid_for_execution: False

## Duplicate Manifest Summary
- duplicate_manifest_count: 466
- pytest_collectable_count: 112
- fixture_impact_count: 1
- byte_equal_to_counterpart_count: 466
- non_byte_equal_or_missing_counterpart_count: 0
- by_classification: {'CODEGEN_FIXTURE_BLOCKER': 1, 'GENERATED_OUTPUT_DUPLICATE': 83, 'PYTEST_COLLECTION_BLOCKER': 112, 'SAFE_DUPLICATE_CANDIDATE': 270}
- by_category: {'codegen_fixture': 1, 'contract': 66, 'core': 78, 'generated_output': 83, 'operator_or_input': 8, 'pytest_candidate': 112, 'script': 118}

## Repair Playbook
- review_manifest_classifications
- hold_non_identical_paths_for_manual_diff_review
- request_separate_operator_repair_authorization
- only_after_authorization_quarantine_or_remove_proven_duplicate_candidates
- rerun_targeted_codegen_tests_and_fast_ci
- emit_separate_repair_validation_receipt

## Brier Telemetry Contract
- telemetry_only: True
- claim_id: duplicate_is_safe_to_quarantine
- brier_score_formula: (forecast_probability - binary_outcome)^2
- resolution_allowed: False
- adaptive_learning_authorized: False
- forecast_routing_authorized: False

## Source Blockers
- none
