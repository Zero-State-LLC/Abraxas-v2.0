# Oracle Signal Intake Boundary Alignment Plan

- plan_id: ORACLE_SIGNAL_INTAKE_BOUNDARY_ALIGNMENT_PLAN_001
- plan_status: ALIGNMENT_PLAN_BOUNDARY_OBSERVED_ADVISORY_ONLY
- patch_id: PATCH-ABX-ORACLE-SIGNAL-INTAKE-BOUNDARY-001
- target_surface: Oracle Signal Intake Boundary
- recommended_next_patch: NOT_COMPUTABLE
- recommended_next_action: hold; oracle intake boundary paths are already repo-observed as advisory-only evidence
- safe_to_prepare_planning_pr: False
- implementation_allowed: False

## Observed Surfaces
- scripts/ingest/run_oracle_intake.py - legacy oracle intake runner
- core/oracle/runtime.py - legacy oracle intake packet emitter
- core/oracle/intake.py - legacy oracle intake envelope model
- contracts/ingest/oracle_intake_queue.v1.schema.json - governed ingest queue contract
- out/ingest/oracle_intake_queue_001.latest.json - governed ingest queue artifact

## Missing Boundary Paths

## Implemented Boundary Paths
- contracts/oracle/oracle_candidate_signal_packet.v1.schema.json
- contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json
- contracts/oracle/oracle_signal_intake_receipt.v1.schema.json
- scripts/ingest/run_oracle_signal_intake_boundary.py

## Alignment Steps
- ORACLE-ALIGN-001: Audit and preserve legacy oracle intake surfaces before introducing candidate-only boundary artifacts.
- ORACLE-ALIGN-002: Define candidate packet, envelope reference, and intake receipt surfaces as additive boundary contracts.
- ORACLE-ALIGN-003: Align future boundary runner with governed ingest queue inputs rather than rebuilding Oracle Signal Layer v2.

## Acceptance Gates
- ORACLE-GATE-001: AUDIT_REQUIRED before legacy oracle runtime mutation
- ORACLE-GATE-002: IMPLEMENTATION_PLAN_ONLY before candidate boundary implementation
- ORACLE-GATE-003: AUTHORITY_DENIED before forecast, canon, runtime, or execution authority
