# P46 Yggdrasil Geometric Route Replay Receipt

- receipt_id: `yggdrasil_geometric_route_replay_receipt_001`
- receipt_type: `YGGDRASIL_GEOMETRIC_ROUTE_REPLAY_RECEIPT`
- schema_version: `YggdrasilGeometricRouteReplayReceipt.v1`
- canonical_hash: `787e178b2dfc0d4ef1d28663c1b8c64ea2175197ddf434e2e6361a0b7c5795b3`
- created_at_utc: `2026-05-29T00:00:00Z`

## Replay Scope
- surface_type: `YGGDRASIL_GEOMETRIC_ROUTE_METADATA`
- replay_mode: `METADATA_REPLAY`
- intended_lane: `OBSERVATION_ONLY`

## Replay Observations (3)
### obs-001-metadata-shape
- type: `METADATA_SHAPE_OBSERVATION`
- status: `METADATA_ONLY`
- description: Route metadata shape remains advisory metadata only.

### obs-002-hash-stability
- type: `HASH_STABILITY_OBSERVATION`
- status: `DECLARED_ONLY`
- description: Canonical hash is deterministic with canonical_hash excluded from preimage.

### obs-003-route-lock
- type: `ROUTE_EFFECT_LOCK_OBSERVATION`
- status: `METADATA_ONLY`
- description: Route effects remain false-locked and non-authoritative.

## Governance
- production_activation: `false`
- valid_for_execution: `false`
- advisory_only: `true` (metadata replay gate only)
