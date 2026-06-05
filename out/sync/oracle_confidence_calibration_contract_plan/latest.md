# Oracle Confidence Calibration Contract Plan

- `plan_id`: `ORACLE_CONFIDENCE_CALIBRATION_CONTRACT_PLAN_001`
- `plan_status`: `CONTRACT_PLAN_EMITTED_ADVISORY_ONLY`
- `target_candidate_id`: `ORACLE_CONFIDENCE_CALIBRATION`
- `recommended_next_patch`: `NOT_COMPUTABLE`
- `implementation_patch_id`: `PATCH-ABX-ORACLE-CONFIDENCE-CALIBRATION-001`
- `calibration_plan_ready`: `True`
- `operator_hold_active`: `True`
- `valid_for_execution`: `False`

## Planned Contract Paths
- `contracts/oracle/oracle_confidence_calibration_profile.v1.schema.json`
- `contracts/oracle/oracle_confidence_calibration_bucket_set.v1.schema.json`
- `contracts/oracle/oracle_confidence_calibration_receipt.v1.schema.json`

## Contract Specs
- `ORACLE_CONFIDENCE_CALIBRATION_PROFILE`: Declare deterministic calibration profile metadata, bucket policy, and advisory-only boundary flags.
- `ORACLE_CONFIDENCE_CALIBRATION_BUCKET_SET`: Define deterministic bucket boundaries, uncertainty band labels, and ordering constraints.
- `ORACLE_CONFIDENCE_CALIBRATION_RECEIPT`: Emit advisory-only calibration receipts without treating confidence as truth or authorization.

## Not Computable Reasons
- `EXPLICIT_OPERATOR_DECISION_REQUIRED`
- `CONTRACT_AUTHORING_NOT_APPROVED`
- `CALIBRATION_OUTPUT_CANNOT_GRANT_TRUTH_OR_AUTHORIZATION`
