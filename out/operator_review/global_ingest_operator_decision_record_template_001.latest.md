# Global Ingest Operator Decision Record Template

- `status`: `GLOBAL_INGEST_OPERATOR_DECISION_RECORD_TEMPLATE_READY`
- `target_pipeline_id`: `oracle_signal`
- `recommended_default_decision`: `HOLD`
- `recommended_next_patch`: `NOT_COMPUTABLE`

## Required Operator Identity Fields

- `operator_id`
- `operator_name`
- `operator_role`
- `decision_timestamp_utc`

## Required Decision Fields

- `selected_decision`
- `decision_rationale`
- `decision_scope_acknowledged`
- `separate_implementation_spec_required`

## Required Acknowledgement Fields

- `advisory_only_acknowledged`
- `non_authoritative_acknowledged`
- `execution_authority_denied_acknowledged`
- `runtime_mutation_denied_acknowledged`
- `canon_mutation_denied_acknowledged`
- `forecast_weight_denied_acknowledged`

## Future Record Output Candidates

- `out/operator_review/global_ingest_operator_decision_record_001.latest.json`
- `out/operator_review/global_ingest_operator_decision_record_001.latest.md`
