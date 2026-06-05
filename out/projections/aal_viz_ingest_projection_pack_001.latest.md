# AAL-Viz Ingest Projection Pack

- patch_id: `PATCH-ABX-AUTO-INGEST-005`
- authority: `PROJECTION_ONLY`
- tile_count: `7`
- authority_badges: `DATA, SHADOW, FORECAST_CANDIDATE, PROJECTION_ONLY`

## ingest_scheduler

- status: `ACTIVE`
- lane: `SHADOW`

## adapter_eligibility

- status: `ACTIVE`
- lane: `SHADOW`

## handoff_receipts

- status: `READY`
- lane: `SHADOW`

## oracle_queue

- status: `READY`
- lane: `SHADOW`

## candidate_outcome_binding

- status: `BLOCKED_PENDING_OUTCOME_BINDING`
- lane: `FORECAST_CANDIDATE`

## brier_readiness

- status: `BLOCKED_PENDING_OUTCOME_BINDING`
- lane: `FORECAST_CANDIDATE`

## authority_lock_panel

- status: `LOCKED`
- lane: `PROJECTION_ONLY`
