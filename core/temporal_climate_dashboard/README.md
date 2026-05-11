# Temporal Climate Dashboard Packet v1

Canonical projection-only packet contract for summarizing temporal climate diagnostics.

Constraints:
- projection-only
- non-authoritative
- no action authorization
- no auto-transition
- no rewrite/mutation/collapse/selection/execution/routing

This layer aggregates continuity, topology, pressure forecast, and regime detector outputs into deterministic operator-facing packet diagnostics.

## Future convergence

If additional dashboard/AAL-Viz projection modules exist, this contract is canonical for `TemporalClimateDashboardPacket.v1`; future work should converge upstream projection surfaces into this schema while preserving projection-only and non-authoritative guarantees.
