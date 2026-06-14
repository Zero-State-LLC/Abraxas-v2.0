# ABX Artifact Lineage Registry Direct Repair Operator Decision Record

- `status`: `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_CONSUMED_BY_SEPARATE_EXECUTION_SPEC`
- `selected_decision`: `AUTHORIZE_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC`
- `decision_scope`: `DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED`
- `execution_authority`: `False`
- `valid_for_repair`: `False`
- `recommended_next_patch`: `NOT_COMPUTABLE`

## Decision Boundary

Separate direct-repair execution spec authoring is approved. No repo-local repair mutation, runner casing policy change, Notion completeness claim, or execution authority is authorized.

## Unresolved Hold Reasons

- `RUNNER_CASING_POLICY_REMAINS_OPERATOR_HELD`
- `NOTION_MAPPING_EVIDENCE_REMAINS_NOT_COMPUTABLE`
- `DIRECT_REPAIR_EXECUTION_AUTHORITY_REMAINS_DENIED`

## Blocked Actions

- `DIRECT_REGISTRY_COVERAGE_REPAIR_EXECUTION`
- `DIRECT_OUTPUT_PAIRING_REPAIR_EXECUTION`
- `DIRECT_DOCS_REFERENCE_REPAIR_EXECUTION`
- `RUNNER_CASING_POLICY_OVERRIDE`
- `NOTION_MAPPING_COMPLETENESS_ASSERTION`
