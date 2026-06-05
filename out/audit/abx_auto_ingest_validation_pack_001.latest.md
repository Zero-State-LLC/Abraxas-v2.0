# ABX Auto Ingest Validation Pack

- validation_id: `abx_auto_ingest_full_stack_validation_v1`
- authority: `VALIDATION_ONLY`
- final_status: `PASS`

## Checks

- `schema_validation`: `PASS`
- `canonical_json_hashing`: `PASS`
- `12_run_invariance`: `PASS_12_OF_12`
- `authority_leakage_scan`: `PASS_NO_FORBIDDEN_FIELDS`
- `not_computable_behavior`: `PASS`
- `empty_queue_behavior`: `PASS`
- `operator_window_gate`: `PASS`
- `cooldown_gate`: `PASS`
- `viz_projection_only`: `PASS_PROJECTION_ONLY`
