# P86 — Temporal Continuity P84 Regeneration Plan Regeneration Plan (Advisory)

## Scope

P86 is a deterministic advisory-only regeneration-planning lane for regenerating the P84 regeneration plan surface.
It reads:

- `out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json` (P85)

P86 also inspects source context only (without execution):

- `out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json` (P84)
- `out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json` (P83)

This lane does **not**:

- run P84 regeneration
- regenerate P84
- regenerate P85
- regenerate P80
- create authorization records/tokens
- grant authorization
- execute commands
- activate runtime behavior
- mutate canon/runtime/scheduler/forecast state

## Required outputs

- `core/temporal_continuity_p84_regeneration_plan_regeneration_plan.py`
- `scripts/run_temporal_continuity_p84_regeneration_plan_regeneration_plan.py`
- `contracts/canon/temporal_continuity_p84_regeneration_plan_regeneration_plan.v1.schema.json`
- `tests/test_temporal_continuity_p84_regeneration_plan_regeneration_plan.py`
- `out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityP84RegenerationPlanRegenerationPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- `regeneration_plan_only = true`
- `meta_regeneration_plan_only = true`
- `p84_regeneration_allowed = false`

All authority and mutation fields are hard-locked to `false`, and all regeneration items hard-lock `regeneration_execution_allowed = false`.

## Status semantics

`p84_regeneration_plan_regeneration_status` enum:

- `NOT_COMPUTABLE`
- `P84_REGENERATION_PLAN_READY`
- `P84_REGENERATION_PLAN_BLOCKED`
- `P84_REGENERATION_NOT_REQUIRED`

Routing highlights:

- Missing/unreadable/malformed P85 source → `NOT_COMPUTABLE` → `P85_EXECUTION_PLAN_REGENERATION`
- P85 recommended lane not `P84_REGENERATION_PLAN_REGENERATION` → `P84_REGENERATION_NOT_REQUIRED` → `P85_RECOMMENDED_NEXT_LANE_PASSTHROUGH`
- P83 missing/unreadable/malformed/NOT_COMPUTABLE → `P84_REGENERATION_PLAN_BLOCKED` → `P87_TEMPORAL_CONTINUITY_P83_STATUS_PLAN_REGENERATION_PLAN`
- P84 already `P80_REGENERATION_PLAN_READY` → `P84_REGENERATION_NOT_REQUIRED` → `P87_TEMPORAL_CONTINUITY_P85_REGENERATION_EXECUTION_PLAN_REGENERATION_PLAN`
- P85 routes to P84 regeneration and P83 is computable → `P84_REGENERATION_PLAN_READY` → `P87_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_EXECUTION_PLAN`

## Determinism requirements

- Canonical JSON with sorted keys and final newline
- Stable `packet_hash` excluding `packet_hash` itself
- Deterministic ordering for `regeneration_items`, `regeneration_reasons`, `prerequisite_sources`, `validation_requirements`, and `blocked_regeneration_reasons`
- Missing/weak signal fails closed (`NOT_COMPUTABLE` pathing)
- Preserve inherited degraded evidence, blockers, drift flags, and semantic overlap flags exactly when available

## Handoff

After P85 routes back to P84 regeneration planning, run:

```bash
python scripts/run_temporal_continuity_p84_regeneration_plan_regeneration_plan.py
```

This emits:

`out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json`

Use `p84_regeneration_plan_regeneration_status` and `recommended_next_lane` before attempting P84 execution planning.
