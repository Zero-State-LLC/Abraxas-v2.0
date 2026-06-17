# ABX Codegen Phase 1 Operator Decision Evidence Collection Validation Review Evidence Plan

- `status`: `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_REVIEW_EVIDENCE_PLAN_READY`
- `source_review_ready`: `True`
- `recommended_default_decision`: `HOLD_FOR_OPERATOR_REVIEW`
- `recommended_next_patch`: `NOT_COMPUTABLE`
- `evidence_bundle_created`: `False`
- `decision_record_created`: `False`
- `safe_to_auto_continue`: `False`

## Source Evaluation Blockers

- `operator_identity_not_attested`
- `operator_decision_not_attested`
- `operator_acknowledgements_not_attested`
- `operator_provenance_evidence_not_attested`
- `operator_evidence_output_not_attested`

## Required Review Artifacts

- `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_review_001.latest.json`
- `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_001.latest.json`
- `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_001.latest.json`
- `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_dry_run_001.latest.json`
- `out/audit/abx_codegen_intelligence_spine_phase1_operator_evidence_packet_001.latest.json`

## Evidence Bundle Groups

- `operator_identity`
  - `operator_id`
  - `operator_name`
  - `operator_role`
  - `attestation_timestamp_utc`
- `operator_decision`
  - `selected_decision`
  - `decision_rationale`
  - `reviewed_validation_replay_status`
  - `evidence_collection_scope_acknowledged`
  - `hold_or_escalation_disposition`
  - `no_auto_continuation_acknowledged`
- `authority_acknowledgements`
  - `advisory_only_acknowledged`
  - `projection_only_acknowledged`
  - `non_authoritative_acknowledged`
  - `evidence_bundle_creation_denied_acknowledged`
  - `decision_record_creation_denied_acknowledged`
  - `authorization_record_creation_denied_acknowledged`
  - `implementation_authority_denied_acknowledged`
  - `execution_authority_denied_acknowledged`
  - `shadow_replay_execution_denied_acknowledged`
  - `notion_writeback_denied_acknowledged`
  - `github_writeback_denied_acknowledged`
  - `runtime_mutation_denied_acknowledged`
  - `canon_mutation_denied_acknowledged`
- `provenance_evidence`
  - `reviewed_validation_dry_run_review_id`
  - `reviewed_validation_dry_run_review_hash`
  - `reviewed_validation_dry_run_hash`
  - `reviewed_validation_plan_hash`
  - `reviewed_source_evaluation_blockers`
  - `reviewed_source_review_artifacts`
- `evidence_outputs`
  - `future_operator_evidence_bundle_id`
  - `future_operator_evidence_bundle_hash`
  - `evidence_collection_outcome_summary`
  - `terminal_authority_summary`
