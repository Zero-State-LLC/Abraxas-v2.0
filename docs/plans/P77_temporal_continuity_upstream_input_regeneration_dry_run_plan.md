# P77 — Temporal Continuity Upstream Input Regeneration Dry-Run Plan (Advisory)

## Scope

P77 is a deterministic advisory-only upstream input regeneration **dry-run planning** lane driven strictly by:
`out/temporal_continuity_upstream_input_restoration_plan/latest.json` (P76 output).

This lane **does not**:
- run generators
- regenerate upstream inputs
- regenerate artifacts
- repair evidence
- create missing outputs
- mutate canon/runtime/scheduler/forecast state
- claim runtime spine readiness

## Required outputs

- `core/temporal_continuity_upstream_input_regeneration_dry_run_plan.py`
- `scripts/run_temporal_continuity_upstream_input_regeneration_dry_run_plan.py`
- `contracts/canon/temporal_continuity_upstream_input_regeneration_dry_run_plan.v1.schema.json`
- `tests/test_temporal_continuity_upstream_input_regeneration_dry_run_plan.py`
- `out/temporal_continuity_upstream_input_regeneration_dry_run_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityUpstreamInputRegenerationDryRunPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- `dry_run_only = true`
- all authority flags hard-locked false, including execution, generator, upstream-input, artifact-regeneration, and spine implementation authority

## Dry-run status semantics

| Condition | dry_run_plan_status |
|---|---|
| P76 source missing/unreadable/malformed | `NOT_COMPUTABLE` |
| P76 status `UPSTREAM_GENERATORS_MISSING` | `DRY_RUN_BLOCKED_GENERATORS_MISSING` |
| P76 status `UPSTREAM_INPUTS_UNREADABLE` | `DRY_RUN_BLOCKED_INPUTS_UNREADABLE` |
| P76 status `UPSTREAM_RESTORATION_NOT_REQUIRED` | `DRY_RUN_NOT_REQUIRED` |
| P76 status `UPSTREAM_INPUTS_READY` | `DRY_RUN_READY` |
| P76 status `UPSTREAM_INPUTS_MISSING` + all missing inputs have observed/readable generators | `DRY_RUN_READY_WITH_MISSING_INPUTS` |
| P76 status `UPSTREAM_INPUTS_MISSING` + any missing input lacks observed/readable generator | `DRY_RUN_BLOCKED_GENERATORS_MISSING` |

## Recommended next-lane logic

| dry_run_plan_status | recommended_next_lane |
|---|---|
| `NOT_COMPUTABLE` | `P76_UPSTREAM_INPUT_RESTORATION_PLAN_REGENERATION` |
| `DRY_RUN_BLOCKED_GENERATORS_MISSING` | `P78_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN` |
| `DRY_RUN_BLOCKED_INPUTS_UNREADABLE` | `P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REPAIR_PLAN` |
| `DRY_RUN_NOT_REQUIRED` + degraded evidence remains | `P78_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN` |
| `DRY_RUN_NOT_REQUIRED` + no degraded evidence remains | `P78_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE` |
| `DRY_RUN_READY` | `P78_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN` |
| `DRY_RUN_READY_WITH_MISSING_INPUTS` | `P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_EXECUTION_PLAN` |

## Dry-run command rule

For items with observed/readable generator scripts, proposed future command is deterministic:

`python <generator_script>`

P77 only records these commands; it never executes them.

## Governance invariants

P77 remains non-authoritative and fail-closed:
- advisory-only
- projection-only
- dry-run-only
- no mutation authority
- no execution authority
- no repair authority
- no evidence generation authority
- no upstream input regeneration authority
- no artifact regeneration authority
- no runtime spine implementation authority

## Handoff

After P76 upstream input restoration plan, run:

```bash
python scripts/run_temporal_continuity_upstream_input_regeneration_dry_run_plan.py
```

This emits `out/temporal_continuity_upstream_input_regeneration_dry_run_plan/latest.json`.
