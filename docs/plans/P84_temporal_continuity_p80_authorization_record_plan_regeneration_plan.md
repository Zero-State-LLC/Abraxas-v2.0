# P84 — Temporal Continuity P80 Authorization Record Plan Regeneration Plan (Advisory)

## Scope

P84 is a deterministic advisory-only regeneration planning lane for P80 authorization record plan progression.
It reads:

- `out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json` (P83)

P84 also inspects source context only (without executing regeneration):

- `out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json` (P79)
- `out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json` (P80)

This lane does **not**:

- regenerate P80
- run P80
- create authorization tokens
- grant authorization
- execute commands
- mutate canon/runtime/scheduler/forecast state
- activate runtime spine behavior

## Required outputs

- `core/temporal_continuity_p80_authorization_record_plan_regeneration_plan.py`
- `scripts/run_temporal_continuity_p80_authorization_record_plan_regeneration_plan.py`
- `contracts/canon/temporal_continuity_p80_authorization_record_plan_regeneration_plan.v1.schema.json`
- `tests/test_temporal_continuity_p80_authorization_record_plan_regeneration_plan.py`
- `out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityP80AuthorizationRecordPlanRegenerationPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- `regeneration_plan_only = true`

All authority and mutation fields are hard-locked to `false`, including:

- repair authority
- repair execution authority
- regeneration authority
- execution authority
- authorization authority
- authorization record creation authority
- runtime/spine implementation authority

## Status semantics

`p80_regeneration_plan_status` enum:

- `NOT_COMPUTABLE`
- `P80_REGENERATION_PLAN_READY`
- `P80_REGENERATION_PLAN_BLOCKED`
- `P80_REGENERATION_NOT_REQUIRED`

Routing highlights:

- Missing/unreadable/malformed P83 source → `NOT_COMPUTABLE` → `P83_STATUS_REPAIR_PLAN_REGENERATION`
- P83 blocked/NOT_COMPUTABLE → `P80_REGENERATION_PLAN_BLOCKED` → `P83_STATUS_REPAIR_PLAN_REGENERATION`
- P83 recommended lane not P80 regeneration → `P80_REGENERATION_NOT_REQUIRED` → `P83_RECOMMENDED_NEXT_LANE_PASSTHROUGH`
- P79 source missing/unreadable/malformed or status NOT_COMPUTABLE → `P80_REGENERATION_PLAN_BLOCKED` → `P85_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN`
- P80 already `AUTHORIZATION_RECORD_PLAN_READY` → `P80_REGENERATION_NOT_REQUIRED` → `P85_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_PLAN`
- P83 recommends P80 regeneration + P79 computable → `P80_REGENERATION_PLAN_READY` → `P85_TEMPORAL_CONTINUITY_P80_AUTHORIZATION_RECORD_PLAN_REGENERATION_EXECUTION_PLAN`

## Determinism requirements

- Canonical JSON with sorted keys and final newline
- Stable `packet_hash` excluding `packet_hash` itself
- Deterministic `regeneration_items` ordering by `regeneration_item_id`, `lane`, `target_artifact_path`
- Deterministic `regeneration_reasons` ordering
- Deterministic `prerequisite_sources` ordering
- Deterministic `validation_requirements` ordering
- Deterministic `blocked_regeneration_reasons` ordering
- Missing/weak signal fails closed (`NOT_COMPUTABLE` pathing)
- Preserve inherited degraded evidence, blockers, drift flags, and semantic overlap flags exactly from P83 when available

## Handoff

After P83 routes to P80 authorization record plan regeneration, run:

```bash
python scripts/run_temporal_continuity_p80_authorization_record_plan_regeneration_plan.py
```

This emits:

`out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json`

Use `p80_regeneration_plan_status` and `recommended_next_lane` before attempting any P80 regeneration execution planning.
