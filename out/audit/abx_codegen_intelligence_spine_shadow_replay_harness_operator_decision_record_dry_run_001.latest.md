# ABX Codegen Shadow Replay Harness Operator Decision Record Dry Run

- dry_run_id: ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_DRY_RUN_001
- operator_decision_record_dry_run_status: ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_DRY_RUN_READY
- validation_passed: True
- simulated_only: True
- operator_input_required: True
- operator_approved: False
- decision_record_created: False
- implementation_authorization_granted: False
- meta_gate_authorization_granted: False
- recommended_next_lane: ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW
- execution_authority: False
- valid_for_execution: False
- valid_for_implementation: False

## Validation Results
- allowed_decisions_present: True
- codex_attestation_denied: True
- decision_record_creation_denied: True
- execution_denied: True
- human_operator_attestation_required: True
- implementation_authorization_denied: True
- lineage_requirements_present: True
- meta_gate_self_authorization_denied: True
- required_attachments_present: True
- required_record_fields_present: True
- source_ready: True

## Validation Blockers
- operator_identity_not_attested
- operator_decision_not_attested
- operator_rationale_not_attested
- operator_signature_not_attested
- operator_evidence_bundle_not_attested

## Simulated Decision Record
- artifact_type: CodegenOperatorDecisionRecord.v1.simulated
- selected_decision: DEFER
- decision_record_created: False
- implementation_authorization_granted: False
