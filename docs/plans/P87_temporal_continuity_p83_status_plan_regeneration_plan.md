# P87 — Temporal Continuity P83 Status Plan Regeneration Plan (Advisory)

## Scope

P87 is a deterministic advisory-only regeneration-planning lane for regenerating the P83 status repair plan surface.
It reads:

- `out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json` (P86)

P87 also inspects source context only (without execution):

- `out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json` (P83)
- `out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json` (P82)

This lane does **not**:

- run P83 regeneration
- regenerate P83
- regenerate P84
- regenerate P85
- regenerate P80
- create authorization records/tokens
- grant authorization
- execute commands
- activate runtime behavior
- mutate canon/runtime/scheduler/forecast state

## Required outputs

- `core/temporal_continuity_p83_status_plan_regeneration_plan.py`
- `scripts/run_temporal_continuity_p83_status_plan_regeneration_plan.py`
- `contracts/canon/temporal_continuity_p83_status_plan_regeneration_plan.v1.schema.json`
- `tests/test_temporal_continuity_p83_status_plan_regeneration_plan.py`
- `out/temporal_continuity_p83_status_plan_regeneration_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityP83StatusPlanRegenerationPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- `regeneration_plan_only = true`
- `meta_regeneration_plan_only = true`
- `p83_regeneration_allowed = false`

All authority and mutation fields are hard-locked to `false`, and all regeneration items hard-lock `regeneration_execution_allowed = false`.

## Status semantics

`p83_regeneration_plan_status` enum:

- `NOT_COMPUTABLE`
- `P83_REGENERATION_PLAN_READY`
- `P83_REGENERATION_PLAN_BLOCKED`
- `P83_REGENERATION_NOT_REQUIRED`

Routing highlights:

- Missing/unreadable/malformed P86 source → `NOT_COMPUTABLE` → `P86_P84_REGENERATION_PLAN_REGENERATION`
- P86 recommended lane not `P87_TEMPORAL_CONTINUITY_P83_STATUS_PLAN_REGENERATION_PLAN` → `P83_REGENERATION_NOT_REQUIRED` → `P86_RECOMMENDED_NEXT_LANE_PASSTHROUGH`
- P82 missing/unreadable/malformed/NOT_COMPUTABLE → `P83_REGENERATION_PLAN_BLOCKED` → `P88_TEMPORAL_CONTINUITY_P82_SOURCE_REPAIR_PLAN_REGENERATION_PLAN`
- P83 already observed/readable/computable → `P83_REGENERATION_NOT_REQUIRED` → `P88_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN`
- P86 routes to P87 and P82 is computable → `P83_REGENERATION_PLAN_READY` → `P88_TEMPORAL_CONTINUITY_P83_STATUS_PLAN_REGENERATION_EXECUTION_PLAN`

## Determinism requirements

- Canonical JSON with sorted keys and final newline
- Stable `packet_hash` excluding `packet_hash` itself
- Deterministic ordering for `regeneration_items`, `regeneration_reasons`, `prerequisite_sources`, `validation_requirements`, and `blocked_regeneration_reasons`
- Missing/weak signal fails closed (`NOT_COMPUTABLE` pathing)
- Preserve inherited degraded evidence, blockers, drift flags, and semantic overlap flags exactly when available

## Handoff

After P86 routes to P83 status plan regeneration, run:

```bash
python scripts/run_temporal_continuity_p83_status_plan_regeneration_plan.py
```

This emits:

`out/temporal_continuity_p83_status_plan_regeneration_plan/latest.json`

Use `p83_regeneration_plan_status` and `recommended_next_lane` before attempting P83 regeneration execution planning.
