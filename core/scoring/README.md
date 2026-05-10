# BrierLedgerEntry.v1 Canonical Layer

This package defines deterministic scoring-ledger ontology for immutable measurement receipts before calibration or adaptation flows.

Scope in this layer:
- Canonical immutable Brier ledger models.
- Deterministic scoring computation and serialization.
- Contract validation and posture reporting.
- Contract audit artifact generation.

Out of scope in this layer:
- Calibration mutation and source reliability mutation.
- Model updates and runtime promotion.
- Live resolver execution and domain adapter activation.

Future convergence work should consume `BrierLedgerEntry.v1` as a read-only measurement signal for downstream calibration/promotion systems.
