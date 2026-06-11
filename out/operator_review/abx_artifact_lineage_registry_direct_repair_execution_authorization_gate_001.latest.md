# ABX Artifact Lineage Registry Direct Repair Execution Authorization Gate

- `status`: `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR`
- `artifact_id`: `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE`
- `authorization_scope`: `DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_ONLY`
- `operator_authorization_required`: `True`
- `operator_authorization_observed`: `False`
- `authorization_granted`: `False`
- `execution_authority`: `False`
- `execution_allowed`: `False`
- `repair_execution_performed`: `False`
- `downstream_status`: `NOT_COMPUTABLE`
- `recommended_next_lane`: `NOT_COMPUTABLE`

## Required Operator Authorization Fields

- `operator_id`
- `operator_name`
- `operator_role`
- `authorization_timestamp_utc`
- `authorization_scope_acknowledged`
- `execution_rationale`
- `runner_casing_policy_decision`
- `notion_mapping_evidence_disposition`

## Blocked Actions

- `DIRECT_REGISTRY_REPAIR_EXECUTION`
- `OUTPUT_PAIRING_REPAIR_EXECUTION`
- `DOCS_REFERENCE_REPAIR_EXECUTION`
- `RUNNER_CASING_POLICY_OVERRIDE`
- `NOTION_MAPPING_COMPLETENESS_CLAIM`
- `RUNTIME_MUTATION`
- `CANON_MUTATION`
- `QUEUE_MUTATION`
- `EXECUTION_AUTHORITY_GRANT_WITHOUT_OPERATOR_RECORD`

## Required Evidence

- `final_operator_authorization_for_direct_repair_execution`
- `runner_casing_policy_decision`
- `notion_mapping_evidence_or_explicit_notion_scope_exclusion`
- `pre_repair_registry_gap_snapshot`
- `pre_repair_output_pairing_gap_snapshot`
- `pre_repair_docs_reference_gap_snapshot`
- `post_repair_validation_plan`
