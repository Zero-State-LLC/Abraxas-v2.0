# P74 — Temporal Continuity Missing Evidence Restoration Plan (Advisory)

## Scope

P74 is a deterministic advisory-only restoration **plan** driven strictly by:
`out/temporal_continuity_evidence_index/latest.json` (P73 output).

This lane **does not**:
- restore, regenerate, or repair evidence
- create missing temporal coherence artifacts
- mutate canon/runtime/scheduler/forecast state
- implement runtime temporal continuity spine behavior
- promote lanes or activate production

## Required outputs

- `core/temporal_continuity_missing_evidence_restoration_plan.py`
- `scripts/temporal/run_temporal_continuity_missing_evidence_restoration_plan.py`
- `contracts/canon/temporal_continuity_missing_evidence_restoration_plan.v1.schema.json`
- `tests/test_temporal_continuity_missing_evidence_restoration_plan.py`
- `out/temporal_continuity_missing_evidence_restoration_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityMissingEvidenceRestorationPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- all authority flags locked false, including restoration/evidence-generation/spine authority

## Restoration strategy enum

- `SCRIPT_DISCOVERY_REQUIRED`
- `GENERATOR_EXISTS_REGENERATION_PLAN`
- `UPSTREAM_INPUT_REQUIRED`
- `UNREADABLE_SOURCE_REPAIR_PLAN`
- `RESTORATION_NOT_REQUIRED`
- `NOT_COMPUTABLE`

## Restoration plan status semantics

| Condition | restoration_plan_status |
|---|---|
| P73 missing/unreadable/malformed | NOT_COMPUTABLE |
| Any unreadable/malformed evidence path | RESTORATION_PLAN_READY_WITH_UNREADABLE_EVIDENCE |
| Any missing evidence path (and none unreadable) | RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE |
| No missing/unreadable evidence | RESTORATION_NOT_REQUIRED |

## Recommended next-lane logic

| Condition | recommended_next_lane |
|---|---|
| P73 missing/unreadable/malformed | P73_EVIDENCE_INDEX_REGENERATION |
| Any SCRIPT_DISCOVERY_REQUIRED item | P75_TEMPORAL_CONTINUITY_GENERATOR_DISCOVERY_PLAN |
| Any UPSTREAM_INPUT_REQUIRED item | P75_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN |
| All missing items are GENERATOR_EXISTS_REGENERATION_PLAN | P75_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN |
| Any unreadable evidence path | P75_TEMPORAL_CONTINUITY_UNREADABLE_EVIDENCE_REPAIR_PLAN |
| No restoration required + degraded evidence remains | P75_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN |
| No restoration required + no degraded evidence | P75_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE |

## Governance invariants

P74 remains non-authoritative and fail-closed:
- advisory-only
- projection-only
- no mutation authority
- no repair authority
- no evidence generation authority
- no restoration execution authority
- no runtime spine implementation authority

Do not claim runtime spine readiness unless:
- `restoration_plan_status = RESTORATION_NOT_REQUIRED`
- `degraded_evidence_inputs` is empty
- `recommended_next_lane = P75_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`

## Handoff

After P73 evidence index, run:

```bash
python scripts/temporal/run_temporal_continuity_missing_evidence_restoration_plan.py
```

This emits `out/temporal_continuity_missing_evidence_restoration_plan/latest.json`.
