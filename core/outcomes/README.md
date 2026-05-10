# OutcomeBinding.v1 Canonical Layer

This package defines deterministic outcome-binding ontology for forecast measurability before resolution execution and scoring.

Scope in this layer:
- Canonical immutable outcome binding models.
- Deterministic serialization and hashing.
- Contract validation and posture reporting.
- Contract audit artifact generation.

Out of scope in this layer:
- Live resolver calls and verdict execution.
- Brier scoring and calibration mutation.
- Domain adapters (market/sports/etc.).

Future convergence work should map domain resolver proposals into `OutcomeBinding.v1` before any scoring pipeline activation.
