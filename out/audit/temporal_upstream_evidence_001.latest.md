# Temporal Upstream Evidence Receipt

- receipt_id: `temporal_upstream_evidence_001`
- final_evidence_status: `NOT_READY`

## Checked Artifacts

- `temporal_state_diff` → `MISSING` (required)
- `cross_run_topology_fusion` → `MISSING` (required)
- `live_projection_refresh` → `AVAILABLE` (required)

## Lineage Assertions
- live_projection_refresh_consumed_by_temporal_state_diff: `True`
