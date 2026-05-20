# P74 — Temporal Continuity Missing Evidence Restoration Plan (Advisory)

## Scope

P74 is a deterministic advisory-only restoration planner driven strictly by:
`out/temporal_continuity_evidence_index/latest.json` (P73 output).

This lane **does not**:
- restore missing evidence
- regenerate artifacts
- repair unreadable evidence
- mutate canon/runtime/scheduler/forecast state
- claim runtime spine readiness
- activate production or promote canon

## Required outputs

- `core/temporal_continuity_missing_evidence_restoration_plan.py`
- `scripts/run_temporal_continuity_missing_evidence_restoration_plan.py`
- `contracts/canon/temporal_continuity_missing_evidence_restoration_plan.v1.schema.json`
- `tests/test_temporal_continuity_missing_evidence_restoration_plan.py`
- `out/temporal_continuity_missing_evidence_restoration_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityMissingEvidenceRestorationPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- all authority/repair/execution fields are const-locked false

## Status semantics

| Condition | restoration_plan_status |
|---|---|
| P73 missing/unreadable/malformed | NOT_COMPUTABLE |
| unreadable evidence exists | RESTORATION_PLAN_READY_WITH_UNREADABLE_EVIDENCE |
| missing evidence exists | RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE |
| no missing/unreadable evidence | RESTORATION_NOT_REQUIRED |

## Recommended next lane

P74 routes into a **P75 family** of advisory planning lanes based on restoration strategy:

- `P73_EVIDENCE_INDEX_REGENERATION` when source P73 is not computable
- `P75_TEMPORAL_CONTINUITY_UNREADABLE_EVIDENCE_REPAIR_PLAN` when unreadable evidence is indexed
- `P75_TEMPORAL_CONTINUITY_GENERATOR_DISCOVERY_PLAN` when any path needs script discovery
- `P75_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN` when upstream inputs are missing/not computable
- `P75_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN` when all missing paths have known generators
- `P75_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN` when restoration is not required but degraded evidence remains
- `P75_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE` only when restoration is not required and degraded evidence is absent

## Handoff

After P73 evidence index, run:

```bash
python scripts/run_temporal_continuity_missing_evidence_restoration_plan.py
```

This emits `out/temporal_continuity_missing_evidence_restoration_plan/latest.json`.

Do not claim runtime spine readiness unless:
- `restoration_plan_status = RESTORATION_NOT_REQUIRED`
- `degraded_evidence_inputs = []`
- `recommended_next_lane = P75_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`
