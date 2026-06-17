# v2.0 Hygiene Phase 1 Dependency Hygiene Package-Lock Receipt

- receipt_id: v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_001
- status: V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_HELD_VALIDATION_FAILED
- source_readiness: SOURCE_ARTIFACTS_READY
- dependency_hygiene_receipt_ready: True
- phase8_operator_review_gate_hash_verified: True
- recommended_next_lane: V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_ROOT_CAUSE_RECEIPT_001
- downstream: NOT_COMPUTABLE
- valid_for_package_lock_tracking: False
- valid_for_execution: False

## Package-Lock Diagnostics
- package_json_hash: d1254ddbf125d30b544ebf462dec1ba2faf1cb0858d01dce1af03f4d946c5913
- package_lock_preflight_hash: 8eb8f2117bd4b3d3a52d719b2038f912a4a5e407b198da4397aba6a176443504
- package_lock_post_validation_hash: 8eb8f2117bd4b3d3a52d719b2038f912a4a5e407b198da4397aba6a176443504
- package_lock_hash_unchanged_after_validation_attempt: True
- metadata_consistent_with_package_json: True
- empty_version_entry_count: 0
- package_lock_tracked_in_git: False

## Resolution Contract
- preferred_disposition: COMMIT_AND_TRACK_IF_VALIDATED
- actual_disposition: HOLD_VALIDATION_FAILED
- package_lock_resolution_status: PACKAGE_LOCK_RESOLUTION_HELD_VALIDATION_FAILED
- package_lock_tracking_authorized: False
- fail_closed_blocker: npm_install_package_lock_only_failed_invalid_version

## Root Cause Classification
- classification: TOOLCHAIN_LOCKFILE_DEDUPE_COMPATIBILITY_HOLD
- confidence: MEDIUM
- risk_level: HIGH

## Validation Evidence
- npm install --package-lock-only --ignore-scripts (node v26.0.0 / npm 11.16.0): FAILED_INVALID_VERSION risk=HIGH error=Invalid Version
- npm install --package-lock-only --ignore-scripts --legacy-peer-deps (node v26.0.0 / npm 11.17.0): FAILED_INVALID_VERSION risk=HIGH error=Invalid Version
- npm ci --ignore-scripts (NOT_RUN_AFTER_LOCKFILE_REGENERATION_FAILURE): NOT_COMPUTABLE risk=MEDIUM error=NOT_COMPUTABLE
- npm run typecheck && npm test && npm run build (NOT_RUN_AFTER_NPM_CI_NOT_COMPUTABLE): NOT_COMPUTABLE risk=MEDIUM error=NOT_COMPUTABLE

## Brier Scoring Contract
- telemetry_only: True
- resolution_allowed: False
- promotion_authorized: False
- brier_resolution_authorized: False

## Source Blockers
- none
