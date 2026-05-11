# Temporal Pressure Forecast Surface v1

Canonical temporal pressure forecast contract surface for deterministic advisory propagation modeling.

Policy guarantees:
- advisory-only and non-authoritative
- no history rewrite
- no ledger mutation
- no timeline collapse
- no canonical timeline selection
- no live execution
- no routing changes

This module projects pressure vectors, waves, and regime-transition risk over topology outputs while preserving blocked/nondeterminism visibility.

## Future convergence

If additional pressure/forecast/regime modules exist, this contract is canonical for `TemporalPressureForecastSurface.v1`; future work should converge upstream projection logic into this schema while preserving non-authoritative, non-mutating, non-normalizing, and non-routing guarantees.
