# ABX Artifact Lineage Registry Direct Repair Operator Decision Record

- `status`: `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_HELD`
- `selected_decision`: `HOLD`
- `decision_scope`: `DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED`
- `execution_authority`: `False`
- `valid_for_repair`: `False`
- `recommended_next_patch`: `NOT_COMPUTABLE`

## Decision Boundary

Direct repair remains held. No separate execution spec, repo-local repair mutation, runner casing policy change, or Notion completeness claim is authorized.

## Unresolved Hold Reasons

- `FINAL_OPERATOR_DECISION_RECORD_MISSING_BEFORE_THIS_RECORD`
- `RUNNER_CASING_POLICY_REMAINS_OPERATOR_HELD`
- `NOTION_MAPPING_EVIDENCE_REMAINS_NOT_COMPUTABLE`
- `DIRECT_REPAIR_EXECUTION_AUTHORITY_REMAINS_DENIED`

## Blocked Actions

- `DIRECT_REGISTRY_COVERAGE_REPAIR_EXECUTION`
- `DIRECT_OUTPUT_PAIRING_REPAIR_EXECUTION`
- `DIRECT_DOCS_REFERENCE_REPAIR_EXECUTION`
- `RUNNER_CASING_POLICY_OVERRIDE`
- `NOTION_MAPPING_COMPLETENESS_ASSERTION`
