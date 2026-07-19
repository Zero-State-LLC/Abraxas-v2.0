# Global Ingest Operator Decision Request

- `status`: `GLOBAL_INGEST_OPERATOR_DECISION_REQUEST_EMITTED`
- `decision_scope`: `IMPLEMENTATION_SPEC_DECISION_REQUIRED`
- `target_pipeline_id`: `oracle_signal`
- `recommended_decision`: `HOLD`
- `recommended_next_action`: `review the fresh oracle intake boundary implementation plan, the Oracle confidence calibration plan, the Oracle confidence calibration contract plan, and collect explicit operator decision evidence before any implementation path can exist`

## Decision Question

Should Abraxas approve a separate governed implementation spec for the Global Ingest Adapter Spine before any oracle_signal implementation work?

## Required Inputs

- oracle_signal_physical_implementation_authorization_record_001

## Observed Paths

- `contracts/oracle/oracle_candidate_signal_packet.v1.schema.json`
- `contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json`
- `contracts/oracle/oracle_signal_intake_receipt.v1.schema.json`
- `scripts/ingest/run_oracle_signal_intake_boundary.py`
- `scripts/ingest/run_ingest_once.py`
- `scripts/ingest/run_oracle_intake.py`
- `core/oracle_signal.py`

## Decision Record Template Candidates

- `out/operator_review/global_ingest_operator_decision_record_template_001.latest.json`
- `out/operator_review/global_ingest_operator_decision_record_template_001.latest.md`

## Implementation Plan Candidates

- `out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json`
- `out/sync/oracle_signal_intake_boundary_implementation_plan/latest.md`
- `out/sync/oracle_confidence_calibration_plan/latest.json`
- `out/sync/oracle_confidence_calibration_plan/latest.md`
- `out/sync/oracle_confidence_calibration_contract_plan/latest.json`
- `out/sync/oracle_confidence_calibration_contract_plan/latest.md`

## Missing Paths

