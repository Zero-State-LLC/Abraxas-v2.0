# ABX Artifact Lineage Registry Direct Repair Separate Execution Spec Plan

- `status`: `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_READY`
- `artifact_id`: `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN`
- `authorization_scope`: `SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC_AUTHORING_ONLY`
- `execution_allowed`: `False`
- `repair_execution_performed`: `False`
- `downstream_status`: `NOT_COMPUTABLE`
- `recommended_next_lane`: `NOT_COMPUTABLE`

## Proposed Phases

- `DIRECT_REPAIR_SPEC_PHASE_001`: `registry_gap_classification`
- `DIRECT_REPAIR_SPEC_PHASE_002`: `output_pairing_gap_classification`
- `DIRECT_REPAIR_SPEC_PHASE_003`: `docs_reference_gap_classification`
- `DIRECT_REPAIR_SPEC_PHASE_004`: `future_operator_authorization_gate`

## Blocked Actions

- `DIRECT_REGISTRY_REPAIR_EXECUTION`
- `OUTPUT_PAIRING_REPAIR_EXECUTION`
- `DOCS_REFERENCE_REPAIR_EXECUTION`
- `RUNNER_CASING_POLICY_OVERRIDE`
- `NOTION_MAPPING_COMPLETENESS_CLAIM`
- `RUNTIME_MUTATION`
- `CANON_MUTATION`
- `QUEUE_MUTATION`

## Required Evidence

- `final_operator_authorization_for_direct_repair_execution`
- `runner_casing_policy_decision`
- `notion_mapping_evidence_or_explicit_notion_scope_exclusion`
- `pre_repair_registry_gap_snapshot`
- `pre_repair_output_pairing_gap_snapshot`
- `pre_repair_docs_reference_gap_snapshot`
- `post_repair_validation_plan`
