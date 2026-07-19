# P102B — Temporal Continuity Repair Execution Plan Router (Advisory)

## Scope

P102B is an advisory-only, deterministic **repair execution plan router** that consumes P102A and selects one execution-plan surface without running any command.

P102B is **execution-plan-router-only** and does **not**:

- regenerate P99/P100/P101
- rerun P102
- create records or tokens
- grant authorization
- execute command sequences
- mutate canon/runtime/scheduler/forecast state

## Required outputs

- `core/temporal_continuity_repair_execution_plan_router.py`
- `scripts/temporal/run_temporal_continuity_repair_execution_plan_router.py`
- `contracts/canon/temporal_continuity_repair_execution_plan_router.v1.schema.json`
- `tests/test_temporal_continuity_repair_execution_plan_router.py`
- `out/temporal_continuity_repair_execution_plan_router/latest.json`

## Artifact posture

- `artifact_type = TemporalContinuityRepairExecutionPlanRouter.v1`
- `canonical_status = ADVISORY_ONLY`
- `execution_plan_router_only = true`
- `repair_execution_plan_router_only = true`
- all authority fields remain hard-locked to `false`
- all `execution_allowed` fields remain hard-locked to `false`
- inherited degraded evidence, blockers, drift flags, and semantic overlap flags are preserved exactly when available

## Source read

- `out/temporal_continuity_p101_readiness_repair_plan/latest.json`

## Router status semantics

1. Missing/unreadable/malformed P102A source → `NOT_COMPUTABLE`, lane `NOT_COMPUTABLE`, route `P102A_READINESS_REPAIR_PLAN_REGENERATION`
2. P102A `p101_readiness_repair_status = NOT_COMPUTABLE` → `REPAIR_EXECUTION_PLAN_ROUTER_BLOCKED`, lane `NOT_COMPUTABLE`
3. P102A `p101_readiness_repair_status = P101_READINESS_REPAIR_NOT_REQUIRED` → `REPAIR_EXECUTION_PLAN_NOT_REQUIRED`, lane `NO_REPAIR_REQUIRED`
4. P102A `p101_readiness_repair_status = P101_READINESS_REPAIR_BLOCKED` → `REPAIR_EXECUTION_PLAN_ROUTER_BLOCKED`, lane `NOT_COMPUTABLE`, route `P101_GATE_ARTIFACT_REGENERATION_PLAN`
5. P102A `...PLAN_READY` + `P102B_P101_GATE_REGENERATION_EXECUTION_PLAN` → ready router, route `P102C_P101_GATE_REGENERATION_EXECUTION_PLAN`
6. P102A `...PLAN_READY` + `P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN` → ready router, route `P102C_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN`
7. P102A `...PLAN_READY` + `P102B_COMPRESSION_AUDIT_RERUN_EXECUTION_PLAN` → ready router, route `P102C_COMPRESSION_AUDIT_RERUN_EXECUTION_PLAN`
8. Otherwise → `NOT_COMPUTABLE`, lane `NOT_COMPUTABLE`, route `P102A_READINESS_REPAIR_PLAN_REGENERATION`

## Command policy

Planned command allowlist is exactly:

1. `python scripts/temporal/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan.py`
2. `python scripts/temporal/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan.py`
3. `python scripts/temporal/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate.py`
4. `python scripts/temporal/run_temporal_continuity_recursive_authorization_chain_compression_audit.py`

No shell chaining, flags, dynamic command construction, environment mutation, or execution is allowed in P102B.

## Handoff

After P102A emits a readiness repair plan, run:

```bash
python scripts/temporal/run_temporal_continuity_repair_execution_plan_router.py
```

This emits:

`out/temporal_continuity_repair_execution_plan_router/latest.json`

Use:

- `p102b_router_status`
- `selected_execution_plan_lane`
- `selected_command_sequence`
- `recommended_next_lane`

before creating any execution-plan-specific P102C lane.
