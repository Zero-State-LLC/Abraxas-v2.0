# Temporal Continuity Index v1

Canonical temporal continuity metric contract layer for replay governance epochs.

This module is additive-only and policy-constrained:
- no history rewrite
- no ledger mutation
- no timeline collapse
- no canonical timeline selection
- no live execution
- no routing change

It computes continuity health diagnostics across replay consensus windows and preserves blocked/nondeterminism signals.

## Future convergence

If other continuity/stability modules exist, this contract is canonical for `TemporalContinuityIndex.v1`; future work should converge upstream metrics into this schema while preserving non-mutating/non-normalizing guarantees.
