# P75 — Temporal Continuity Generator Discovery Plan (Advisory)

## Scope

P75 is a deterministic advisory-only generator **discovery** plan driven strictly by:
`out/temporal_continuity_missing_evidence_restoration_plan/latest.json` (P74 output).

This lane **does not**:
- run generator scripts
- regenerate artifacts
- repair evidence
- create missing outputs
- mutate canon/runtime/scheduler/forecast state
- implement runtime temporal continuity spine behavior
- promote lanes or activate production

## Required outputs

- `core/temporal_continuity_generator_discovery_plan.py`
- `scripts/temporal/run_temporal_continuity_generator_discovery_plan.py`
- `contracts/canon/temporal_continuity_generator_discovery_plan.v1.schema.json`
- `tests/test_temporal_continuity_generator_discovery_plan.py`
- `out/temporal_continuity_generator_discovery_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityGeneratorDiscoveryPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- all authority flags locked false, including generator-execution/restoration/evidence-generation/spine authority

## Generator binding status enum

| Value | Meaning |
|---|---|
| `GENERATOR_OBSERVED` | Script exists and is readable |
| `GENERATOR_MISSING` | Script path inferred but file not found |
| `GENERATOR_UNREADABLE` | Script file exists but cannot be read |
| `GENERATOR_NOT_COMPUTABLE` | No script path could be inferred (`likely_generator_script = NOT_COMPUTABLE`) |
| `GENERATOR_AMBIGUOUS` | Multiple output paths share the same inferred generator script |

## Generator discovery status semantics

| Condition | generator_discovery_status |
|---|---|
| P74 missing/unreadable/malformed | `NOT_COMPUTABLE` |
| P74 restoration_plan_status = RESTORATION_NOT_REQUIRED | `GENERATOR_DISCOVERY_NOT_REQUIRED` |
| At least one GENERATOR_MISSING/NOT_COMPUTABLE, no observed | `GENERATORS_MISSING` |
| Mixed observed + missing/unreadable/not-computable | `GENERATORS_PARTIAL` |
| All generators observed but prerequisites missing | `GENERATORS_OBSERVED_WITH_MISSING_PREREQUISITES` |
| All generators observed and prerequisites present | `GENERATORS_OBSERVED` |
| No items require generator discovery | `GENERATOR_DISCOVERY_NOT_REQUIRED` |

## Callable hint

`generator_callable_hint` is determined by static text inspection only — scripts are never executed.
It is `true` when the script is readable and contains any of:
- `if __name__ == "__main__"`
- `def main(`
- `def run(`

## Recommended next-lane logic

| Condition | recommended_next_lane |
|---|---|
| P74 missing/unreadable/malformed | `P74_RESTORATION_PLAN_REGENERATION` |
| `generator_discovery_status = NOT_COMPUTABLE` | `P74_RESTORATION_PLAN_REGENERATION` |
| Any `GENERATOR_MISSING` or `GENERATOR_NOT_COMPUTABLE` | `P76_TEMPORAL_CONTINUITY_GENERATOR_IMPLEMENTATION_PLAN` |
| Any `GENERATOR_UNREADABLE` | `P76_TEMPORAL_CONTINUITY_GENERATOR_REPAIR_PLAN` |
| Any `GENERATOR_AMBIGUOUS` | `P76_TEMPORAL_CONTINUITY_GENERATOR_BINDING_DISAMBIGUATION_PLAN` |
| All generators observed + missing prerequisites | `P76_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN` |
| All generators observed + prerequisites present | `P76_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN` |
| Discovery not required + degraded evidence remains | `P76_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN` |
| Discovery not required + no degraded evidence | `P76_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE` |

## Governance invariants

P75 remains non-authoritative and fail-closed:
- advisory-only
- projection-only
- no mutation authority
- no repair authority
- no evidence generation authority
- no restoration execution authority
- no generator execution authority
- no runtime spine implementation authority
- `safe_to_execute = false` on all generator items

Do not claim runtime spine readiness unless:
- `generator_discovery_status = GENERATORS_OBSERVED`
- all prerequisites are present
- `recommended_next_lane = P76_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN`
  or `recommended_next_lane = P76_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`

## Handoff

After P74 missing evidence restoration plan, run:

```bash
python scripts/temporal/run_temporal_continuity_generator_discovery_plan.py
```

This emits `out/temporal_continuity_generator_discovery_plan/latest.json`.
