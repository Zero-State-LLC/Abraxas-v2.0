# SettlementVerdict.v1 Canonical Layer

This package defines deterministic settlement-verdict ontology between evidence collection and scoring.

Scope in this layer:
- Canonical immutable settlement models.
- Deterministic serialization and hashing.
- Contract validation and posture reporting.
- Contract audit artifact generation.

Out of scope in this layer:
- Brier scoring execution.
- Calibration mutation.
- Live resolver execution and domain adapters.

Future convergence work should map resolution outputs into `SettlementVerdict.v1` before score computation and calibration flows are activated.
