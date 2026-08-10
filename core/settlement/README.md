# SettlementVerdict.v1 Canonical Layer

This package defines deterministic settlement-verdict ontology between evidence collection and scoring.

Scope in this layer:
- Canonical immutable settlement models.
- Deterministic serialization and hashing.
- Contract validation and posture reporting.
- Contract audit artifact generation.
- Resolution → verdict mapping (`binding_bridge.py`): pure, fail-closed
  conversion of `ForecastOutcomeBindingPacket.v1` into `SettlementVerdict.v1`,
  plus the `is_score_ready` / `observed_outcome_from_verdict` gate that score
  computation consumes. Without an explicit `authority_ref` the mapping never
  emits `SETTLED`; non-score-ready verdicts raise instead of scoring.

Out of scope in this layer:
- Brier scoring execution.
- Calibration mutation.
- Live resolver execution and domain adapters.

Convergence status: `core.brier.runtime.build_brier_ledger` accepts an optional
score-ready settlement verdict and derives the observed outcome from it
(fail-closed). The legacy direct binding-status path remains for callers without
settlement coverage; retiring it is a future step once resolver flows produce
verdicts everywhere. Brier scoring remains telemetry-only.
