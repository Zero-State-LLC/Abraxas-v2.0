# ADR-0018 — Artifact Classification (State Influence)

## Status

Accepted (enforcement active for classified writer API) — 2026-07-26

## Context

`out/` currently mixes runtime state, audit evidence, workflow control, development history, governance decisions, generated plans, and canonical domain output. Treating all of these as equal canonical state increases coupling and agent confusion.

## Decision

Formalize artifact classes:

| Class | Influences current canonical state |
| --- | --- |
| `CANONICAL_DOMAIN_ARTIFACT` | yes |
| `GOVERNANCE_DECISION` | yes (requires valid authority locks) |
| `AUDIT_EVIDENCE` | no |
| `BUILD_EVIDENCE` | no |
| `RUNTIME_EVENT` | no |
| `GENERATED_PLAN` | no |
| `HISTORICAL_RECEIPT` | no |

A receipt may prove an action occurred; it must not automatically become domain state.

### Runtime API

- Policy module: `core/canonical/artifact_classification.py`
- Classified writer: `core/canonical.json.write_canonical_artifact` / `prepare_canonical_artifact`
- Legacy `write_canonical_json` remains for migration compatibility
- Advisory bypass scanner: `scripts/readiness/run_canonical_writer_bypass_check.py`

`GOVERNANCE_DECISION` writes must include `authority_locks` with promotion/canon/forecast flags locked `false`.

Supported product surfaces (CLI analyze/replay outputs, convergence package) use the classified writer. Mass migration of historical runners is deferred.

## Consequences

- New governed product writes should call `write_canonical_artifact`.
- Advisory spine results remain `AUDIT_EVIDENCE` with `influences_current_state: false`.
- Fail-closed CI on bypasses is not enabled yet (advisory report only).
