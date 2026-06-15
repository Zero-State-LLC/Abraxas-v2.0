# v2.0 Hygiene Schema Contract Evidence Dry Run

- dry_run_id: v2_hygiene_schema_contract_evidence_dry_run_001
- status: V2_HYGIENE_SCHEMA_CONTRACT_EVIDENCE_DRY_RUN_READY
- source_evidence_plan_ready: True
- simulated_only: True
- required_group_count: 5
- required_field_count: 36
- attested_group_count: 0
- source_missing_contract_count: 5
- valid_for_authorization_record: False
- valid_for_execution: False
- recommended_next_lane: NOT_COMPUTABLE

## Evaluation Blockers
- operator_identity_not_attested
- review_scope_acknowledgement_not_attested
- authority_acknowledgements_not_attested
- schema_contract_disposition_not_attested
- terminal_output_controls_not_attested

## Simulated Evidence Bundle
- artifact_type: V2HygieneSchemaContractEvidenceBundle.v1.simulated
- evidence_bundle_id: v2_hygiene_schema_contract_evidence_bundle_001.simulated
- operator_identity: 5 required fields (attested=False)
- review_scope_acknowledgement: 5 required fields (attested=False)
- authority_acknowledgements: 17 required fields (attested=False)
- schema_contract_disposition: 5 required fields (attested=False)
- terminal_output_controls: 4 required fields (attested=False)

## Source Missing Schema Contracts
- loop_dynamics
- v2_output
- v2_hygiene_rune_base
- hygiene_mode
- individual_hygiene_rune_contracts
