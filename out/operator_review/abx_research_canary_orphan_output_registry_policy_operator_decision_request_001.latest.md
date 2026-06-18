# ABX Research Canary Orphan Output Registry Policy Operator Decision Request 001

- `request_id`: `ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_REQUEST_001`
- `status`: `ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_REQUEST_EMITTED`
- `decision_scope`: `ORPHAN_RESEARCH_OUTPUT_REGISTRY_POLICY_DECISION_REQUIRED`
- `recommended_decision`: `EXCLUDE_FROM_CANONICAL_REPAIR`
- `recommended_next_lane`: `ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_PLAN_001`
- `recommended_next_action`: `review orphan policy options and collect explicit operator decision evidence before any orphan registry inclusion or archive lane`

## Acceptance Gates
- `orphan_policy_operator_decision_required`: `READY_FOR_OPERATOR_DECISION`
- `orphan_policy_operator_review_hold`: `READY_FOR_OPERATOR_DECISION`
- `p130_advisory_hold_preservation_gate`: `ACTIVE`
- `separate_orphan_registry_governance_gate`: `ACTIVE`

## Decision Options
- `EXCLUDE_FROM_CANONICAL_REPAIR`
- `REGISTER_AS_DERIVED_OPTIONAL`
- `ARCHIVE_CANDIDATE`
- `HOLD`
