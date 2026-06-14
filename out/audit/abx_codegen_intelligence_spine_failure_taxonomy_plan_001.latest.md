# ABX Codegen Intelligence Spine Failure Taxonomy Plan

- plan_id: ABX_CODEGEN_INTELLIGENCE_SPINE_FAILURE_TAXONOMY_PLAN_001
- failure_taxonomy_plan_status: ABX_CODEGEN_FAILURE_TAXONOMY_PLAN_READY
- recommended_next_lane: NOT_COMPUTABLE
- safe_to_auto_continue: False
- execution_authority: False
- valid_for_implementation: False

## Top-Level Categories
- Validation (VAL-): PLANNING_ONLY
- Replay (RPL-): PLANNING_ONLY
- Governance (GOV-): PLANNING_ONLY
- Meta-Gate (META-): PLANNING_ONLY
- Integration (INT-): PLANNING_ONLY
- Internal (INTL-): PLANNING_ONLY

## Promotion Blocker Mapping
- RPL-001 -> replay_hash_divergence (receipt_mutation_authorized=False)
- GOV-003 -> governance_compliance_failed (receipt_mutation_authorized=False)
- GOV-002 -> self_modification_detected (receipt_mutation_authorized=False)
