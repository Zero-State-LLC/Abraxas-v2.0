# ABX Codegen Intelligence Spine Governance Decision Vocabulary Plan

- plan_id: ABX_CODEGEN_INTELLIGENCE_SPINE_GOVERNANCE_DECISION_VOCABULARY_PLAN_001
- governance_decision_vocabulary_plan_status: ABX_CODEGEN_GOVERNANCE_DECISION_VOCABULARY_PLAN_HELD_FOR_OPERATOR
- recommended_next_lane: NOT_COMPUTABLE
- safe_to_auto_continue: False
- execution_authority: False
- valid_for_implementation: False

## Decision Enum
- PROMOTE_TO_CANARY: promotion_candidate (promotion_blockers_required=False)
- HOLD_FOR_OPERATOR: temporary_hold (promotion_blockers_required=True)
- HOLD_FOR_META_GATE: self_improvement_hold (promotion_blockers_required=True)
- BLOCK_POLICY_VIOLATION: hard_block (promotion_blockers_required=True)
- BLOCK_REPLAY_FAILURE: hard_block (promotion_blockers_required=True)
- REJECT: terminal_rejection (promotion_blockers_required=True)
- REFINE_PROPOSAL: revision_request (promotion_blockers_required=True)

## HOLD vs BLOCK
- HOLD_FOR_OPERATOR: temporary_pause_pending_operator_review_or_additional_evidence (routing_authorized=False)
- HOLD_FOR_META_GATE: specialized_hold_for_self_modification_or_core_governance_change (routing_authorized=False)
- BLOCK_POLICY_VIOLATION: hard_stop_for_policy_or_authority_boundary_violation (routing_authorized=False)
- BLOCK_REPLAY_FAILURE: hard_stop_for_replay_failure_or_unmet_replay_proofs (routing_authorized=False)

## Implementation Blockers
- shadow_replay_integration_exploration_plan_held_for_operator
- receipt_schema_mutation_denied
- recommendation_routing_denied
- promotion_blocker_population_denied
- operator_decision_record_creation_denied
- meta_gate_chain_creation_denied
- artifact_registry_registration_denied
- notion_writeback_denied
- github_writeback_denied
