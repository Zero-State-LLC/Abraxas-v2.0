# Global Ingest Operator Decision Request

- `status`: `GLOBAL_INGEST_OPERATOR_DECISION_REQUEST_EMITTED`
- `decision_scope`: `IMPLEMENTATION_SPEC_DECISION_REQUIRED`
- `target_pipeline_id`: `oracle_signal`
- `recommended_decision`: `HOLD`
- `recommended_next_action`: `hold for explicit governed operator decision before any Oracle Signal Layer pipeline contract or implementation work`

## Decision Question

Should Abraxas approve a separate governed implementation spec for the Global Ingest Adapter Spine before any oracle_signal implementation work?

## Required Inputs

- explicit governed operator decision approving a separate implementation spec is required before creating core/oracle_signal.py or mutating ingest runners

## Observed Paths

- `scripts/run_ingest_once.py`
- `scripts/run_oracle_intake.py`

## Missing Paths

- `core/oracle_signal.py`
