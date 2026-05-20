# P71 — Temporal Continuity Spine Binder Contract (Advisory Planning Layer)

## Scope

P71 is a deterministic advisory contract/binder layer fed by `out/temporal_continuity_spine_precheck/latest.json`.

This lane does **not** implement runtime temporal continuity spine behavior and does **not** perform evidence repair.

## Required outputs

- `core/temporal_continuity_spine_binder_contract.py`
- `scripts/run_temporal_continuity_spine_binder_contract.py`
- `contracts/canon/temporal_continuity_spine_binder_contract.v1.schema.json`
- `out/temporal_continuity_spine_binder_contract/latest.json`
- `tests/test_temporal_continuity_spine_binder_contract.py`

## Binder contract requirements

- `artifact_type = TemporalContinuitySpineBinderContract.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- `production_activation = false`
- `canon_promotion = false`
- `forecast_influence = false`
- `scheduler_mutation = false`
- `runtime_authority = false`
- `repair_authority = false`
- `spine_implementation_authority = false`
- Include source precheck linkage and hash fields
- Include continuity grouping, binder inputs, degraded inputs, missing/not-computable inputs
- Preserve semantic overlap and drift/blocker reporting from precheck evidence

## Status semantics

- `NOT_COMPUTABLE`: P70 precheck missing/unreadable
- `BLOCKED`: precheck recommends `P69_CANON_RESUME_STATE_REPAIR` or `P71_TEMPORAL_CONTINUITY_EVIDENCE_REPAIR_INDEX`
- `CONTRACT_READY_WITH_DEGRADED_EVIDENCE`: binder lane recommended and degraded/missing inputs exist
- `CONTRACT_READY`: binder lane recommended and no degraded/missing inputs exist

## Governance invariants

P71 remains advisory-only and non-authoritative. It must not mutate canon/runtime/scheduler/forecast state and must not activate production or promote lanes.
