# P82 — Temporal Continuity P79 Authorization Gate Source Repair Plan (Advisory)

## Scope

P82 is a deterministic advisory-only source repair planning lane for P79 authorization gate progression.
It reads:

- `out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json` (P81)

P82 inspects `source_chain_items` and `not_computable_reasons`, explains why P79 blocks P80/P81 progression, and emits a deterministic repair plan without performing the repair.

This lane does **not**:

- repair P79 directly
- regenerate P79 directly
- regenerate P80 directly
- create authorization tokens
- grant authorization
- execute commands
- mutate canon/runtime/scheduler/forecast state
- activate runtime spine behavior

## Required outputs

- `core/temporal_continuity_p79_authorization_gate_source_repair_plan.py`
- `scripts/run_temporal_continuity_p79_authorization_gate_source_repair_plan.py`
- `contracts/canon/temporal_continuity_p79_authorization_gate_source_repair_plan.v1.schema.json`
- `tests/test_temporal_continuity_p79_authorization_gate_source_repair_plan.py`
- `out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityP79AuthorizationGateSourceRepairPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- `source_repair_plan_only = true`

All authority and mutation fields are hard-locked to `false`, including:

- repair authority
- repair execution authority
- execution authority
- authorization authority
- authorization record creation authority
- regeneration authority
- runtime/spine implementation authority

## Status semantics

`p79_source_repair_plan_status` enum:

- `NOT_COMPUTABLE`
- `P79_REPAIR_PLAN_READY`
- `P79_REPAIR_PLAN_BLOCKED_BY_P78`
- `P79_REPAIR_NOT_REQUIRED`

Routing highlights:

- Missing/unreadable/malformed P81 source → `NOT_COMPUTABLE` → `P81_SOURCE_STATUS_AUDIT_REGENERATION`
- P81 source chain not blocked → `P79_REPAIR_NOT_REQUIRED`
- P78 source missing / P78 status not computable → `P79_REPAIR_PLAN_BLOCKED_BY_P78`
- P79 source missing → `P79_REPAIR_PLAN_READY` → `P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN`
- P79 unreadable or malformed → `P79_REPAIR_PLAN_READY` → `P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_SOURCE_REPAIR_EXECUTION_PLAN`
- P79 status not computable → `P79_REPAIR_PLAN_READY` → `P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_STATUS_REPAIR_PLAN`
- P79 not authorization eligible → `P79_REPAIR_PLAN_READY` → `P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_ELIGIBILITY_REPAIR_PLAN`

## Determinism requirements

- Canonical JSON with sorted keys and final newline
- Stable `packet_hash` excluding `packet_hash` itself
- Deterministic `repair_items` ordering by `repair_item_id`, `lane`, `path`
- Deterministic `p79_failure_modes` ordering
- Deterministic `blocked_repair_reasons` ordering
- Missing/weak signal fails closed (`NOT_COMPUTABLE` pathing)
- Preserve inherited degraded evidence, blockers, drift flags, and semantic overlap flags exactly when present in P81

## Handoff

After P81 source-status audit routes to P79 source repair, run:

```bash
python scripts/run_temporal_continuity_p79_authorization_gate_source_repair_plan.py
```

This emits:

`out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json`

Use `p79_source_repair_plan_status` and `recommended_next_lane` before attempting P79/P80 regeneration or template work.
