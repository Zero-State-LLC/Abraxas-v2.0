# CalibrationLedger.v1 Canonical Layer

This package defines deterministic calibration observability snapshots from immutable Brier ledger entries.

Scope in this layer:
- Canonical immutable calibration models.
- Deterministic aggregation (decile buckets) and hashing.
- Contract validation and audit artifact generation.

Out of scope in this layer:
- Weight updates, source reliability mutation, promotion/adaptation.
- Live adapters and runtime activation.

Future convergence work should consume `CalibrationLedger.v1` as read-only observability input.
