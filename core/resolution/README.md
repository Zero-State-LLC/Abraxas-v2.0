# ResolutionEvidence.v1 Canonical Layer

This package defines deterministic evidence-packet ontology for outcome binding settlement readiness before any resolver/scoring runtime activation.

Scope in this layer:
- Canonical immutable evidence models.
- Deterministic serialization and hashing.
- Contract validation and posture reporting.
- Contract audit artifact generation.

Out of scope in this layer:
- Live evidence fetch and settlement execution.
- Brier scoring and calibration mutation.
- Domain-specific adapters.

Future convergence work should map domain evidence collectors into `ResolutionEvidence.v1` before settlement and scoring pipelines are activated.
