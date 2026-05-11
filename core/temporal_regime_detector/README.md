# Temporal Regime Transition Detector v1

Canonical advisory detector contract for temporal regime-state classification over pressure forecast surfaces.

Policy constraints:
- non-authoritative
- no auto-transition
- no history rewrite
- no ledger mutation
- no timeline collapse
- no canonical timeline selection
- no live execution
- no routing changes

This detector is diagnostics-only and preserves blocked/nondeterminism evidence through triggers and metrics.

## Future convergence

If additional regime-transition modules exist, this contract is canonical for `TemporalRegimeTransitionDetector.v1`; future work should converge into this schema while preserving advisory-only/non-transitioning guarantees.
