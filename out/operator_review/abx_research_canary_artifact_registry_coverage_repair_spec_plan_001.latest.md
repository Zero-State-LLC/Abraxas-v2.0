# ABX Research Canary Artifact Registry Coverage Repair Spec Plan 001

- `spec_plan_id`: `ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_001`
- `spec_plan_status`: `RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_READY`
- `recommended_next_lane`: `ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_001`
- `downstream_status`: `READY_FOR_OPERATOR_DECISION_REQUEST`
- `registry_mutation_performed`: `False`
- `research_canary_spine_refresh_performed`: `False`

## Source Audit
- `source_audit_hash`: `905a9061ac3e4415095e100ec96bd6c2b1e974c98f223767288f5aafe88e4319`
- `source_audit_id`: `ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_001`
- `source_audit_observed`: `True`
- `source_audit_path`: `out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json`
- `source_audit_status`: `RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_GAP_CONFIRMED`
- `source_recommended_next_lane`: `ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_001`

## Repair Batches
- `CANONICAL_LANE_OUTPUT_PATH_REGISTRY_BATCH`: `ACTIVE` via `REPO_LOCAL_DIRECT_REPAIR_CANDIDATE` (26 impacted)
- `LANE_ID_TRACEABILITY_METADATA_BATCH`: `ACTIVE` via `REPO_LOCAL_DIRECT_REPAIR_CANDIDATE` (28 impacted)
- `PARTIAL_SCOPE_PREFIX_NORMALIZATION_BATCH`: `ACTIVE` via `OPERATOR_REVIEW_REQUIRED` (26 impacted)
- `ORPHAN_RESEARCH_OUTPUT_POLICY_BATCH`: `ACTIVE` via `OPERATOR_REVIEW_REQUIRED` (10 impacted)
- `P130_ADVISORY_HOLD_PRESERVATION_BATCH`: `ACTIVE` via `GOVERNANCE_BOUNDARY` (1 impacted)
- `P102G_NAMESPACE_COLLISION_BATCH`: `ACTIVE` via `GOVERNANCE_BOUNDARY` (1 impacted)

## Proposed Phases
- `REPAIR_SPEC_PHASE_001`: `classify_canonical_lane_output_path_gaps`
- `REPAIR_SPEC_PHASE_002`: `classify_lane_id_traceability_gaps`
- `REPAIR_SPEC_PHASE_003`: `resolve_scope_prefix_vs_derived_optional_policy`
- `REPAIR_SPEC_PHASE_004`: `orphan_output_exclusion_policy`
- `REPAIR_SPEC_PHASE_005`: `future_operator_authorization_gate_before_registry_mutation`

## Blocked Actions
- `DIRECT_REGISTRY_REPAIR`
- `REGISTRY_ENTRY_MUTATION`
- `RESEARCH_CANARY_SPINE_REFRESH`
- `RESEARCH_CANARY_ARTIFACT_REGENERATION`
- `RUNTIME_MUTATION`
- `CANON_MUTATION`
- `QUEUE_MUTATION`
- `SCHEDULER_MUTATION`
- `NOTION_WRITEBACK`
- `GITHUB_WRITEBACK`
- `P130_ACTIVATION`
- `TEMPORAL_CONTINUITY_PROMOTION`
- `EXECUTION_AUTHORITY_GRANT`
- `TOKEN_MINTING`
- `REPAIR_SPEC_EXECUTION`
- `SCOPE_PREFIX_MUTATION_WITHOUT_OPERATOR_DECISION`

## Blocked Delivery Surfaces
- `core/generated_artifact_registry.py direct repair mutations`
- `scripts/run_research_canary_artifact_spine_refresh.py spine-refresh runners`
- `out/research_canary_final_activation_authorization_review_hold/ P130 hold surfaces`
- `out/research_canary_*/latest.json research-canary artifact regeneration targets`
- `runtime route or scheduler mutations`
