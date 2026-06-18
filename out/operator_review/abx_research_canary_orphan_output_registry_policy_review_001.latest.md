# ABX Research Canary Orphan Output Registry Policy Review 001

- `status`: `ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_HELD_FOR_OPERATOR`
- `artifact_id`: `ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_001`
- `orphan_count`: `10`
- `recommended_policy`: `EXCLUDE_FROM_CANONICAL_REPAIR`
- `downstream_status`: `ORPHAN_POLICY_REVIEW_HELD_FOR_OPERATOR`
- `recommended_next_lane`: `NOT_COMPUTABLE`

## Orphan Records
- `out/research_canary_artifact_spine_refresh/latest.json`: `RESEARCH_CANARY_ARTIFACT_SPINE_REFRESH` (default `EXCLUDE_FROM_CANONICAL_REPAIR`)
- `out/research_cross_drop_conflict_scan/latest.json`: `P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN` (default `EXCLUDE_FROM_CANONICAL_REPAIR`)
- `out/research_derived_subsystem_candidate_ledger/latest.json`: `P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER` (default `EXCLUDE_FROM_CANONICAL_REPAIR`)
- `out/research_fold_canon_alignment_plan/latest.json`: `P94_RESEARCH_FOLD_CANON_ALIGNMENT_PLAN` (default `EXCLUDE_FROM_CANONICAL_REPAIR`)
- `out/research_fold_drop_spec_builder/latest.json`: `P95_RESEARCH_FOLD_DROP_SPEC_BUILDER` (default `EXCLUDE_FROM_CANONICAL_REPAIR`)
- `out/research_fold_validation_plan/latest.json`: `P96_RESEARCH_FOLD_VALIDATION_PLAN` (default `EXCLUDE_FROM_CANONICAL_REPAIR`)
- `out/research_operator_stabilization_decision_record/latest.json`: `P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD` (default `EXCLUDE_FROM_CANONICAL_REPAIR`)
- `out/research_shadow_stabilization_proof_plan/latest.json`: `P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN` (default `EXCLUDE_FROM_CANONICAL_REPAIR`)
- `out/research_shadow_stabilization_receipt/latest.json`: `P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT` (default `EXCLUDE_FROM_CANONICAL_REPAIR`)
- `out/research_stabilization_window_monitor/latest.json`: `P102_RESEARCH_STABILIZATION_WINDOW_MONITOR` (default `EXCLUDE_FROM_CANONICAL_REPAIR`)

## Policy Options

- `EXCLUDE_FROM_CANONICAL_REPAIR`
- `REGISTER_AS_DERIVED_OPTIONAL`
- `ARCHIVE_CANDIDATE`
- `HOLD`

## Preserved Holds

- `ORPHAN_OUTPUT_REGISTRY_INCLUSION` remains blocked
- `P130_ACTIVATION` remains blocked
- `RESEARCH_CANARY_SPINE_REFRESH` remains blocked
