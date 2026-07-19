# P78 — Temporal Continuity Upstream Input Regeneration Execution Plan (Advisory)

## Scope

P78 is a deterministic advisory-only upstream input regeneration **execution plan** lane driven strictly by:
`out/temporal_continuity_upstream_input_regeneration_dry_run_plan/latest.json` (P77 output).

This lane **does not**:
- run generators
- regenerate upstream inputs
- regenerate artifacts
- repair evidence
- create missing outputs
- mutate canon/runtime/scheduler/forecast state
- activate runtime spine behavior

## Required outputs

- `core/temporal_continuity_upstream_input_regeneration_execution_plan.py`
- `scripts/temporal/run_temporal_continuity_upstream_input_regeneration_execution_plan.py`
- `contracts/canon/temporal_continuity_upstream_input_regeneration_execution_plan.v1.schema.json`
- `tests/test_temporal_continuity_upstream_input_regeneration_execution_plan.py`
- `out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityUpstreamInputRegenerationExecutionPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- `execution_plan_only = true`
- all authority flags hard-locked false, including execution/generator/upstream-input/artifact-regeneration/spine implementation authority

## Execution plan status semantics

| Condition | execution_plan_status |
|---|---|
| P77 source missing/unreadable/malformed | `NOT_COMPUTABLE` |
| P77 `dry_run_plan_status = DRY_RUN_READY_WITH_MISSING_INPUTS` and executable candidates exist | `EXECUTION_PLAN_READY` |
| P77 `dry_run_plan_status = DRY_RUN_BLOCKED_GENERATORS_MISSING` | `EXECUTION_PLAN_BLOCKED` |
| P77 `dry_run_plan_status = DRY_RUN_BLOCKED_INPUTS_UNREADABLE` | `EXECUTION_PLAN_BLOCKED` |
| P77 `dry_run_plan_status = DRY_RUN_READY` | `EXECUTION_PLAN_NOT_REQUIRED` |
| P77 `dry_run_plan_status = DRY_RUN_NOT_REQUIRED` | `EXECUTION_PLAN_NOT_REQUIRED` |
| Any inconsistent status combination | `NOT_COMPUTABLE` |

## Recommended next-lane logic

| execution_plan_status | recommended_next_lane |
|---|---|
| `NOT_COMPUTABLE` | `P77_DRY_RUN_PLAN_REGENERATION` |
| `EXECUTION_PLAN_READY` | `P79_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_GATE` |
| `EXECUTION_PLAN_BLOCKED` + generator blockers | `P79_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN` |
| `EXECUTION_PLAN_BLOCKED` + unreadable input blockers | `P79_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REPAIR_PLAN` |
| `EXECUTION_PLAN_NOT_REQUIRED` from `DRY_RUN_READY` | `P79_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN` |
| `EXECUTION_PLAN_NOT_REQUIRED` from `DRY_RUN_NOT_REQUIRED` + degraded evidence | `P79_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN` |
| `EXECUTION_PLAN_NOT_REQUIRED` from `DRY_RUN_NOT_REQUIRED` + no degraded evidence | `P79_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE` |

## Command allowlist doctrine

Command allowlisting is planning-only and never grants execution authority.

`allowlisted_for_future_execution` may be true only when all criteria hold:
- command originates from P77 `dry_run_commands`
- `generator_script` is observed/readable
- `expected_output_path == target_input_path`
- target is in P77 `executable_future_candidates`
- command shape is restricted to `python scripts/<script>.py` with no chaining/destructive flags

`execution_authorized` is always `false` on execution steps and allowlist items.

## Governance invariants

P78 remains non-authoritative and fail-closed:
- advisory-only
- projection-only
- execution-plan-only
- no mutation authority
- no execution authority
- no repair authority
- no restoration execution authority
- no generator execution authority
- no upstream input generation authority
- no artifact regeneration authority
- no runtime spine implementation authority

## Handoff

After P77 upstream input regeneration dry-run plan, run:

```bash
python scripts/temporal/run_temporal_continuity_upstream_input_regeneration_execution_plan.py
```

This emits `out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json`.
