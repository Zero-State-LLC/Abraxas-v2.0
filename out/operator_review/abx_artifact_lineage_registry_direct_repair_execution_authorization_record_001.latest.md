# ABX Artifact Lineage Registry Direct Repair Execution Authorization Record

- `status`: `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR`
- `artifact_id`: `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD`
- `authorization_scope`: `SCOPED_DIRECT_ARTIFACT_LINEAGE_REPAIR_EXECUTION_PR_ONLY`
- `authorization_granted`: `True`
- `execution_authority`: `True`
- `execution_allowed`: `False`
- `repair_execution_performed`: `False`
- `safe_to_prepare_execution_pr`: `True`
- `downstream_status`: `READY_FOR_SCOPED_EXECUTION_PR_PREPARATION`
- `recommended_next_lane`: `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_PR`

## Scoped Repair Actions

- `DIRECT_REGISTRY_REPAIR_EXECUTION_PR_PREPARATION`
- `OUTPUT_PAIRING_REPAIR_EXECUTION_PR_PREPARATION`
- `DOCS_REFERENCE_REPAIR_EXECUTION_PR_PREPARATION`

## Blocked Actions

- `RUNNER_CASING_POLICY_OVERRIDE`
- `NOTION_MAPPING_COMPLETENESS_CLAIM`
- `RUNTIME_MUTATION`
- `CANON_MUTATION`
- `QUEUE_MUTATION`
- `LIVE_NOTION_WRITEBACK`
- `GITHUB_WRITEBACK_AUTOMATION`
- `UNSCOPED_REPAIR_EXECUTION`
- `REPAIR_EXECUTION_WITHOUT_VALIDATION_PR`

## Required Pre-Execution Validation

- `pre_repair_registry_gap_snapshot`
- `pre_repair_output_pairing_gap_snapshot`
- `pre_repair_docs_reference_gap_snapshot`
- `scoped_repair_diff_review`
- `post_repair_validation_plan`
- `fast_ci_before_pr`
