# v2.0 Hygiene Phase 2 Stabilization Subsystem Selection Operator Review Gate

- receipt_id: v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_001
- status: V2_HYGIENE_PHASE2_STABILIZATION_SUBSYSTEM_SELECTION_OPERATOR_REVIEW_GATE_READY
- source_readiness: SOURCE_ARTIFACTS_READY
- operator_review_gate_ready: True
- phase7_selection_receipt_hash_verified: True
- recommended_next_lane: V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_001
- downstream: NOT_COMPUTABLE
- valid_for_package_lock_tracking: False
- valid_for_execution: False

## Operator Disposition Contract
- recommended_operator_decision: HOLD_FOR_PACKAGE_LOCK_RESOLUTION_REPAIR
- selected_follow_on_lane: V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_001
- package_lock_resolution_selected: True

## Package-Lock Resolution Contract
- package_lock_path: apps/aal-viz-live-console/package-lock.json
- metadata_consistent_with_package_json: True
- preferred_disposition: COMMIT_AND_TRACK_IF_VALIDATED
- actual_disposition: HOLD_VALIDATION_FAILED
- package_lock_resolution_status: PACKAGE_LOCK_RESOLUTION_HELD_VALIDATION_FAILED
- package_lock_tracking_authorized: False
- fail_closed_blocker: npm_ci_failed_invalid_version

## Package-Lock Validation Evidence
- npm ci (default): FAILED_NETWORK risk=MEDIUM error=ENOTFOUND registry.npmjs.org
- npm ci (network_escalated): FAILED_INVALID_VERSION risk=HIGH error=Invalid Version
- npm run typecheck && npm test && npm run build (not_run): NOT_RUN_AFTER_NPM_CI_FAILURE risk=MEDIUM error=NOT_COMPUTABLE

## Brier Scoring Contract
- telemetry_only: True
- resolution_allowed: False
- promotion_authorized: False
- brier_resolution_authorized: False

## Source Blockers
- none
