# ABX Codegen Intelligence Spine Packet Validation Receipt

- receipt_id: ABX_CODEGEN_INTELLIGENCE_SPINE_PACKET_VALIDATION_RECEIPT_001
- receipt_status: ABX_CODEGEN_INTELLIGENCE_SPINE_PACKET_VALIDATION_RECEIPT_READY
- target_surface: ABX_CODEGEN_INTELLIGENCE_SPINE_001
- target_surface_status: PACKET_SCHEMA_FIXTURE_VALIDATION_OBSERVED_ADVISORY_ONLY
- recommended_next_lane: ABX_CODEGEN_INTELLIGENCE_SPINE_PHASE1_OPERATOR_AUTHORIZATION_REQUEST_PLAN
- valid_for_implementation: False
- valid_for_execution: False
- shadow_replay_execution_performed: False

## Fixture Validation Summary
- fixture_count: 9
- valid_fixture_pass_count: 4
- negative_fixture_expected_rejection_count: 5
- validation_mode: SCHEMA_AND_SEMANTIC_RULES_ONLY
- wall_clock_used: False

## Fixture Records
- gap_diagnosis_golden.v1.json: PASS (VALID)
- improvement_proposal_golden.v1.json: PASS (VALID)
- invalid_gap_diagnosis_missing_hash.v1.json: EXPECTED_REJECTION (NEGATIVE)
- invalid_improvement_proposal_canon_jump.v1.json: EXPECTED_REJECTION (NEGATIVE)
- invalid_improvement_proposal_missing_operator_decision.v1.json: EXPECTED_REJECTION (NEGATIVE)
- invalid_improvement_proposal_missing_provenance.v1.json: EXPECTED_REJECTION (NEGATIVE)
- invalid_shadow_receipt_promote_failure.v1.json: EXPECTED_REJECTION (NEGATIVE)
- self_improvement_meta_gate_receipt.v1.json: PASS (VALID)
- shadow_receipt_golden.v1.json: PASS (VALID)

## Schema Contracts
- contracts/canon/gap_diagnosis_packet.v1.schema.json: OBSERVED
- contracts/canon/improvement_proposal.v1.schema.json: OBSERVED
- contracts/canon/shadow_improvement_receipt.v1.schema.json: OBSERVED

## Blocked Actions
- activation_or_execution
- artifact_registry_mutation
- authorization_record_creation
- auto_approval
- canon_mutation
- code_generation
- code_mutation
- codegen_engine_implementation
- file_writeback
- fixture_mutation
- forecast_routing
- github_writeback
- harness_implementation
- notion_writeback
- operator_attestation_creation
- queue_mutation
- receipt_promotion
- runtime_dispatch_mutation
- scheduler_mutation
- schema_mutation
- self_authorization
- shadow_replay_execution
- shadow_replay_receipt_creation
