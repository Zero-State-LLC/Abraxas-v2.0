# P45 Oracle Geometric Attachment Replay Receipt

- receipt_id: `oracle_geometric_attachment_replay_receipt_001`
- receipt_type: `ORACLE_GEOMETRIC_ATTACHMENT_REPLAY_RECEIPT`
- schema_version: `OracleGeometricAttachmentReplayReceipt.v1`
- canonical_hash: `b66469ddf4348d4181d2de79ef0db6bdcb5b36f6bdc16e6cbef97f2d3b6e2465`
- created_at_utc: `2026-05-29T00:00:00Z`

## Replay Scope
- surface_type: `ORACLE_GEOMETRIC_SIGNAL_ATTACHMENT`
- replay_mode: `METADATA_REPLAY`
- intended_lane: `OBSERVATION_ONLY`

## Replay Observations (3)
### obs-001-attachment-shape
- type: `ATTACHMENT_SHAPE_OBSERVATION`
- status: `METADATA_ONLY`
- description: Attachment metadata shape remains replay-declarative only.

### obs-002-hash-stability
- type: `HASH_STABILITY_OBSERVATION`
- status: `DECLARED_ONLY`
- description: Canonical hash is deterministic and excludes canonical_hash field.

### obs-003-governance-lock
- type: `GOVERNANCE_LOCK_OBSERVATION`
- status: `METADATA_ONLY`
- description: Governance locks remain advisory-only and non-authoritative.

## Governance
- production_activation: `false`
- valid_for_execution: `false`
- advisory_only: `true` (metadata replay gate only)
