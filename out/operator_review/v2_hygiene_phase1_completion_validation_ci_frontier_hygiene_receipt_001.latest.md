# v2.0 Hygiene Phase 1 Completion-Validation CI Frontier Hygiene Receipt

- receipt_id: v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_001
- status: V2_HYGIENE_PHASE1_COMPLETION_VALIDATION_CI_FRONTIER_HYGIENE_RECEIPT_BLOCKED_BY_UNQUARANTINED_FRONTIER_DRIFT
- source_readiness: SOURCE_ARTIFACTS_READY
- ready_for_subsystem_implementation_authorization_gate: False
- recommended_next_lane: NOT_COMPUTABLE
- downstream: NOT_COMPUTABLE
- safe_to_auto_continue: False
- valid_for_implementation: False
- valid_for_execution: False

## Duplicate Frontier Inventory
- duplicate_frontier_count: 466
- duplicate_pytest_collection_candidate_count: 112
- deletion_authorized: False
- cleanup_authorized: False

## Codegen Fixture Drift
- total_fixture_count: 10
- canonical_fixture_count: 9
- duplicate_fixture_count: 1
- codegen_fixture_count_delta_source: duplicate_2_json_fixture
- extra_fixture_decision: DUPLICATE_DERIVED_NOT_CANONICAL

## Package-Lock Hygiene Finding
- path: apps/aal-viz-live-console/package-lock.json
- observed: True
- classification: SEPARATE_DEPENDENCY_HYGIENE_FINDING
- package_lock_mutation_authorized: False

## Source Blockers
- codegen_duplicate_fixture_unquarantined
- duplicate_pytest_collection_candidates_unquarantined
