# Temporal Climate AAL-Viz Projection Binding v1

Canonical projection binding contract for converting temporal climate dashboard packets into deterministic AAL-Viz UI projection payloads.

Constraints:
- projection-only
- non-authoritative
- no inference authority
- no action authorization
- no auto-transition
- no rewrite/mutation/collapse/selection/execution/routing

## Future convergence

If other AAL-Viz projection binders exist, this contract is canonical for `TemporalClimateAALVizProjectionBinding.v1`; future convergence should preserve projection-only and zero-authority guarantees.
