# ForecastObject.v1 Canonical Layer

This package defines a deterministic canonical forecast ontology (`ForecastObject.v1`) for cross-domain governance consistency.

Scope in this layer:
- Canonical immutable models.
- Deterministic serialization and hashing.
- Contract validation and posture reporting.
- Contract audit artifact generation.

Out of scope in this layer:
- Outcome resolution and binding execution.
- Brier scoring and calibration runtime activation.
- Live market/sports/domain adapters.

Future adapter-convergence work should map domain forecasts into `ForecastObject.v1` before any scoring or live execution path.
