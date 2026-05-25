# P76 — Temporal Continuity Upstream Input Restoration Plan (Advisory)

## Scope

P76 is a deterministic advisory-only upstream input restoration **planning** lane driven strictly by:
`out/temporal_continuity_generator_discovery_plan/latest.json` (P75 output).

This lane **does not**:
- restore upstream inputs
- run generators
- regenerate artifacts
- repair evidence
- create missing outputs
- mutate canon/runtime/scheduler/forecast state
- implement runtime temporal continuity spine behavior
- promote lanes or activate production

## Required outputs

- `core/temporal_continuity_upstream_input_restoration_plan.py`
- `scripts/run_temporal_continuity_upstream_input_restoration_plan.py`
- `contracts/canon/temporal_continuity_upstream_input_restoration_plan.v1.schema.json`
- `tests/test_temporal_continuity_upstream_input_restoration_plan.py`
- `out/temporal_continuity_upstream_input_restoration_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityUpstreamInputRestorationPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- all authority flags hard-locked false, including generator/restoration/upstream-input/spine implementation authority

## Upstream restoration status semantics

| Condition | upstream_restoration_plan_status |
|---|---|
| P75 source missing/unreadable/malformed | `NOT_COMPUTABLE` |
| P75 has no missing prerequisite paths | `UPSTREAM_RESTORATION_NOT_REQUIRED` |
| Missing prerequisites + no inferable upstream generator | `UPSTREAM_GENERATORS_MISSING` |
| Missing prerequisites + inferred script missing/unreadable | `UPSTREAM_GENERATORS_MISSING` |
| Missing prerequisites + inferred upstream generator observed/readable | `UPSTREAM_INPUTS_MISSING` |
| Any unreadable/malformed prerequisite input | `UPSTREAM_INPUTS_UNREADABLE` |
| All prerequisite inputs observed/readable | `UPSTREAM_INPUTS_READY` |

## Recommended next-lane logic

| upstream_restoration_plan_status | recommended_next_lane |
|---|---|
| `NOT_COMPUTABLE` | `P75_GENERATOR_DISCOVERY_PLAN_REGENERATION` |
| `UPSTREAM_GENERATORS_MISSING` | `P77_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN` |
| `UPSTREAM_INPUTS_UNREADABLE` | `P77_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REPAIR_PLAN` |
| `UPSTREAM_INPUTS_MISSING` | `P77_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN` |
| `UPSTREAM_INPUTS_READY` | `P77_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN` |
| `UPSTREAM_RESTORATION_NOT_REQUIRED` + degraded evidence | `P77_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN` |
| `UPSTREAM_RESTORATION_NOT_REQUIRED` + no degraded evidence | `P77_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE` |

## Governance invariants

P76 remains non-authoritative and fail-closed:
- advisory-only
- projection-only
- no mutation authority
- no repair authority
- no evidence generation authority
- no restoration execution authority
- no generator execution authority
- no upstream input generation authority
- no runtime spine implementation authority
- `safe_to_restore = false` on all upstream input items

Do not claim runtime spine readiness unless:
- `upstream_restoration_plan_status` permits the implementation planning gate
- `recommended_next_lane = P77_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`

## Handoff

After P75 generator discovery plan, run:

```bash
python scripts/run_temporal_continuity_upstream_input_restoration_plan.py
```

This emits `out/temporal_continuity_upstream_input_restoration_plan/latest.json`.
