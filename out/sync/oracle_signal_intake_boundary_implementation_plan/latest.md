# Oracle Signal Intake Boundary Implementation Plan

- plan_id: ORACLE_SIGNAL_INTAKE_BOUNDARY_IMPLEMENTATION_PLAN_001
- plan_status: IMPLEMENTATION_PLAN_BOUNDARY_OBSERVED_ADVISORY_ONLY
- patch_id: PATCH-ABX-ORACLE-SIGNAL-INTAKE-BOUNDARY-001
- recommended_next_patch: NOT_COMPUTABLE
- recommended_next_action: hold; oracle intake boundary implementation paths are already repo-observed as advisory-only evidence
- safe_to_prepare_planning_pr: False
- safe_to_prepare_implementation_pr: False
- implementation_allowed: False
- valid_for_execution: False

## Planned Contract Paths
- contracts/oracle/oracle_candidate_signal_packet.v1.schema.json
- contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json
- contracts/oracle/oracle_signal_intake_receipt.v1.schema.json

## Planned Runner Paths
- scripts/ingest/run_oracle_signal_intake_boundary.py

## Missing Boundary Paths

## Implemented Boundary Paths
- contracts/oracle/oracle_candidate_signal_packet.v1.schema.json
- contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json
- contracts/oracle/oracle_signal_intake_receipt.v1.schema.json
- scripts/ingest/run_oracle_signal_intake_boundary.py

## Preserved Legacy Surfaces
- scripts/ingest/run_oracle_intake.py
- core/oracle/runtime.py
- core/oracle/intake.py
- contracts/ingest/oracle_intake_queue.v1.schema.json
- out/ingest/oracle_intake_queue_001.latest.json

## Implementation Phases
- ORACLE-PLAN-001: Candidate contract formalization
- ORACLE-PLAN-002: Candidate boundary runner
- ORACLE-PLAN-003: Boundary verification

## Acceptance Gates
- ORACLE-IMPL-GATE-001: PLANNING_ONLY before candidate boundary implementation PR
- ORACLE-IMPL-GATE-002: PRESERVE_AS_OBSERVED before legacy oracle runtime mutation
- ORACLE-IMPL-GATE-003: AUTHORITY_DENIED before forecast, canon, runtime, queue, or execution authority
