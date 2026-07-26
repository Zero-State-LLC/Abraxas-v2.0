# ADR-0018 — Artifact Classification (State Influence)

## Status

Accepted (design); enforcement deferred to Phase 5

## Context

`out/` currently mixes runtime state, audit evidence, workflow control, development history, governance decisions, generated plans, and canonical domain output. Treating all of these as equal canonical state increases coupling and agent confusion.

## Decision

Formalize artifact classes:

| Class | Influences current canonical state |
| --- | --- |
| `CANONICAL_DOMAIN_ARTIFACT` | yes |
| `GOVERNANCE_DECISION` | yes (requires valid authority) |
| `AUDIT_EVIDENCE` | no |
| `BUILD_EVIDENCE` | no |
| `RUNTIME_EVENT` | no |
| `GENERATED_PLAN` | no |
| `HISTORICAL_RECEIPT` | no |

A receipt may prove an action occurred; it must not automatically become domain state.

Production Convergence Phase 0–2 advisory spine results are emitted as `AUDIT_EVIDENCE` with `influences_current_state: false`.

## Consequences

- Inventory and target architecture document the taxonomy now.
- Writer consolidation (Phase 5) will enforce classification + retention.
- No mass regeneration or deletion of historical `out/` receipts in this slice.
