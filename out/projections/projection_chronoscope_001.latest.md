# Projection Chronoscope — projection_chronoscope_001

**Patch:** `PATCH-P16-TEMPORAL-CHRONOSCOPE-AND-PROJECTION-TIMELINE-001`
**Final Status:** `ADVISORY_ONLY`
**Timeline Point Count:** `1`
**Window Count:** `1`

## Playback Cursor Bounds
- First: `cursor:c50c532db1caabebd7bc`
- Last: `cursor:c50c532db1caabebd7bc`

## Lineage Posture
- Status: `PRESENT`
- Gap count: `0`
- Corrupt count: `0`

## Drift Posture
- Status: `PRESENT`
- Drift events: `0`
- Blocked windows: `0`
- NOT_COMPUTABLE sources: `1`

## Missing/Corrupt Source Blockers
- `missing_artifact:out/projections/live_projection_refresh_001.latest.json`

## Operator Next Actions
- Inspect missing/corrupt projection artifacts and re-run chronoscope.
- Resolve lineage gaps before using timeline windows for inspection.
