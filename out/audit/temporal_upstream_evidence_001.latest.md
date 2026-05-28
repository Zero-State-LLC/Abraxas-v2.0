# Temporal Upstream Evidence Receipt

- receipt_id: `temporal_upstream_evidence_001`
- final_evidence_status: `READY`

## Checked Artifacts

- `temporal_state_diff` → `AVAILABLE` (required)
- `cross_run_topology_fusion` → `AVAILABLE` (required)
- `live_projection_refresh` → `AVAILABLE` (required)
- `universal_ingest_receipt` → `MISSING` (optional)
- `universal_ingest_validation_result` → `MISSING` (optional)
- `universal_ingest_conflict_report` → `MISSING` (optional)

## Lineage Assertions
- live_projection_refresh_consumed_by_temporal_state_diff: `True`
