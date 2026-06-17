# ABX Research Canary Artifact Registry Coverage Audit 001

- `audit_id`: `ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_001`
- `audit_status`: `RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_GAP_CONFIRMED`
- `recommended_next_lane`: `ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_001`
- `downstream_status`: `READY_FOR_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN`
- `registry_mutation_performed`: `False`
- `research_canary_spine_refresh_performed`: `False`

## Coverage Summary
- `canonical_lane_count`: `28`
- `direct_registry_lane_id_coverage`: `False`
- `discovered_research_output_count`: `38`
- `implemented_artifacts_present`: `True`
- `lane_id_gap_count`: `28`
- `orphan_research_output_count`: `10`
- `output_artifacts_present`: `True`
- `output_path_gap_count`: `28`
- `schemas_present`: `True`
- `tests_present`: `True`

## Lane Records
- `P103_RESEARCH_SHADOW_REPLAY_AUDIT`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P105_RESEARCH_PROMOTION_BLOCKER_LEDGER`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P107_RESEARCH_CANARY_REVIEW_PACKET`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P108_RESEARCH_CANARY_DECISION_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P109_RESEARCH_CANARY_PLAN_DRAFT`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P111_RESEARCH_CANARY_AUTHORIZATION_DRAFT`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P112_RESEARCH_CANARY_AUTHORIZATION_REVIEW_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P113_RESEARCH_CANARY_FINAL_PRECHECK_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=True)
- `P114_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_DRAFT`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P119_RESEARCH_CANARY_RUNTIME_OBSERVATION_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P120_RESEARCH_CANARY_ROLLBACK_TERMINATION_GOVERNANCE`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P121_RESEARCH_CANARY_OPERATOR_GO_NO_GO_REVIEW`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P122_RESEARCH_CANARY_ACTIVATION_PACKAGE_DRAFT`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P123_RESEARCH_CANARY_ACTIVATION_PACKAGE_REVIEW_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P124_RESEARCH_CANARY_ACTIVATION_DECISION_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P125_RESEARCH_CANARY_ACTIVATION_DECISION_REVIEW_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P126_RESEARCH_CANARY_ACTIVATION_DENIAL_HOLD_ROUTING`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P127_RESEARCH_CANARY_ACTIVATION_ENVELOPE_DRAFT`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P128_RESEARCH_CANARY_ACTIVATION_ENVELOPE_REVIEW_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P129_RESEARCH_CANARY_ACTIVATION_READINESS_EVIDENCE_RECORD`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=False)
- `P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW`: GAP_CONFIRMED (lane_id_in_registry=False, output_in_registry=True)

## Orphan Research Outputs
- `out/research_canary_artifact_spine_refresh/latest.json`: `RESEARCH_CANARY_ARTIFACT_SPINE_REFRESH`
- `out/research_cross_drop_conflict_scan/latest.json`: `P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN`
- `out/research_derived_subsystem_candidate_ledger/latest.json`: `P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER`
- `out/research_fold_canon_alignment_plan/latest.json`: `P94_RESEARCH_FOLD_CANON_ALIGNMENT_PLAN`
- `out/research_fold_drop_spec_builder/latest.json`: `P95_RESEARCH_FOLD_DROP_SPEC_BUILDER`
- `out/research_fold_validation_plan/latest.json`: `P96_RESEARCH_FOLD_VALIDATION_PLAN`
- `out/research_operator_stabilization_decision_record/latest.json`: `P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD`
- `out/research_shadow_stabilization_proof_plan/latest.json`: `P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN`
- `out/research_shadow_stabilization_receipt/latest.json`: `P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT`
- `out/research_stabilization_window_monitor/latest.json`: `P102_RESEARCH_STABILIZATION_WINDOW_MONITOR`

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
