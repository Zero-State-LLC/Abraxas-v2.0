# Global Ingest Operator Decision Evidence Collection Plan

- `status`: `GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY`
- `target_pipeline_id`: `oracle_signal`
- `recommended_default_decision`: `HOLD`
- `recommended_next_state`: `hold`
- `recommended_next_patch`: `NOT_COMPUTABLE`

## Required Review Artifacts

- `out/operator_review/global_ingest_operator_decision_request_001.latest.json`
- `out/operator_review/global_ingest_operator_decision_record_template_001.latest.json`
- `out/sync/oracle_signal_research_intake_receipt/latest.json`
- `out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json`
- `out/sync/oracle_confidence_calibration_plan/latest.json`
- `out/global_pipeline_doctrine_validation/operator_review_packet.latest.json`

## Evidence Bundle Groups

- `operator_identity`
  - `operator_id`
  - `operator_name`
  - `operator_role`
  - `decision_timestamp_utc`
- `decision`
  - `selected_decision`
  - `decision_rationale`
  - `decision_scope_acknowledged`
  - `separate_implementation_spec_required`
- `acknowledgements`
  - `advisory_only_acknowledged`
  - `non_authoritative_acknowledged`
  - `execution_authority_denied_acknowledged`
  - `runtime_mutation_denied_acknowledged`
  - `canon_mutation_denied_acknowledged`
  - `forecast_weight_denied_acknowledged`
- `provenance_evidence`
  - `reviewed_request_id`
  - `reviewed_request_hash`
  - `reviewed_doctrine_review_hash`
  - `reviewed_gap_backlog_hash`
  - `reviewed_notion_decision_backlog_hash`
  - `reviewed_notion_spec_completion_queue_hash`
- `record_outputs`
  - `decision_record_id`
  - `decision_record_hash`
  - `decision_outcome_summary`
