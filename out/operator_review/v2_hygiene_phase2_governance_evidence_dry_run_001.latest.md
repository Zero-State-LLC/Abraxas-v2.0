# v2.0 Hygiene Phase 2 Governance Evidence Dry Run

- dry_run_id: v2_hygiene_phase2_governance_evidence_dry_run_001
- status: V2_HYGIENE_PHASE2_GOVERNANCE_EVIDENCE_DRY_RUN_READY
- source_evidence_plan_ready: True
- simulated_only: True
- required_group_count: 5
- required_field_count: 36
- attested_group_count: 0
- source_missing_control_count: 6
- valid_for_authorization_record: False
- valid_for_execution: False
- recommended_next_lane: NOT_COMPUTABLE

## Evaluation Blockers
- operator_identity_not_attested
- review_scope_acknowledgement_not_attested
- authority_acknowledgements_not_attested
- phase2_governance_control_disposition_not_attested
- terminal_output_controls_not_attested

## Simulated Evidence Bundle
- artifact_type: V2HygienePhase2GovernanceEvidenceBundle.v1.simulated
- evidence_bundle_id: v2_hygiene_phase2_governance_evidence_bundle_001.simulated
- operator_identity: 5 required fields (attested=False)
- review_scope_acknowledgement: 5 required fields (attested=False)
- authority_acknowledgements: 17 required fields (attested=False)
- phase2_governance_control_disposition: 5 required fields (attested=False)
- terminal_output_controls: 4 required fields (attested=False)

## Source Missing Governance Controls
- default_advisory_mode
- no_output_mutation_without_configuration
- metadata_version_owner_posture
- hygiene_pipeline_interaction
- promotion_governance_review
- module_boundary_tests
