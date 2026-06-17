# ABX Codegen Phase 1 Operator Decision Evidence Collection Plan

- `status`: `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY`
- `source_review_ready`: `True`
- `recommended_default_decision`: `HOLD_FOR_OPERATOR_REVIEW`
- `recommended_next_patch`: `NOT_COMPUTABLE`
- `decision_record_created`: `False`
- `implementation_unblocked`: `False`

## Required Review Artifacts

- `out/operator_review/abx_codegen_phase1_operator_decision_record_review_001.latest.json`
- `out/operator_review/abx_codegen_phase1_operator_decision_record_dry_run_001.latest.json`
- `out/operator_review/abx_codegen_phase1_operator_decision_record_plan_001.latest.json`
- `out/operator_review/abx_codegen_phase1_operator_review_request_001.latest.json`
- `out/audit/abx_codegen_intelligence_spine_phase1_operator_evidence_packet_001.latest.json`

## Evidence Bundle Groups

- `operator_identity`
  - `operator_id`
  - `operator_name`
  - `operator_role`
  - `decision_timestamp_utc`
- `operator_decision`
  - `selected_decision`
  - `decision_rationale`
  - `decision_scope_acknowledged`
  - `phase1_scope_reviewed`
  - `review_only_progression_acknowledged`
  - `separate_authorization_record_lane_required_if_approved`
- `authority_acknowledgements`
  - `advisory_only_acknowledged`
  - `projection_only_acknowledged`
  - `non_authoritative_acknowledged`
  - `implementation_authority_denied_acknowledged`
  - `execution_authority_denied_acknowledged`
  - `shadow_replay_execution_denied_acknowledged`
  - `authorization_record_creation_denied_acknowledged`
  - `notion_writeback_denied_acknowledged`
  - `github_writeback_denied_acknowledged`
  - `runtime_mutation_denied_acknowledged`
  - `canon_mutation_denied_acknowledged`
- `provenance_evidence`
  - `reviewed_phase1_operator_decision_record_review_id`
  - `reviewed_phase1_operator_decision_record_review_hash`
  - `reviewed_phase1_operator_decision_record_dry_run_hash`
  - `reviewed_phase1_operator_decision_record_plan_hash`
  - `reviewed_phase1_operator_evidence_packet_hash`
  - `reviewed_validation_blockers`
- `evidence_outputs`
  - `operator_evidence_bundle_id`
  - `operator_evidence_bundle_hash`
  - `evidence_collection_outcome_summary`
  - `terminal_authority_summary`
