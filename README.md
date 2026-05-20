# ABRAXAS v2.0.1

Deterministic governed symbolic execution substrate.

Core principles:
- governance first
- replayability
- deterministic execution
- fail-closed authority
- projection-only visualization
- shadow-only execution

Current milestone:
v2.0.9-governed-weight-drift-simulation

## Getting Started

### Install

```bash
python -m pip install .
python -m pip install pytest pytest-cov ruff pyright httpx anyio
```

### Regenerate managed artifacts

```bash
python scripts/run_artifact_regeneration.py --full
```

Managed artifacts are derived surfaces. Regenerate them deterministically and use drift detection to fail closed on stale outputs.

### Validate the repository

```bash
python scripts/run_artifact_regeneration.py --full --validation-only
python scripts/run_artifact_regeneration.py --check-drift
pytest -q
ruff check .
pyright
```

### Run the doctrine validator

```bash
python scripts/run_doctrine_validator.py
```

This writes the latest validation summary to `out/validation/latest.json`, updates projection outputs under `out/projections/`, and refreshes the milestone spine artifacts under `out/spine/`.

## Read-only API

ABRAXAS exposes a fail-closed FastAPI surface for health, registry, validation, and projection reads.

```bash
ABRAXAS_API_PUBLIC_READONLY=true python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
```

Available routes:

- `GET /health` returns a basic system status payload.
- `GET /registry` returns the pipeline registry from `out/registry/latest.json` or builds it from contracts on demand.
- `GET /validation` returns the latest doctrine validation packet from `out/validation/latest.json`.
- `GET /projection` returns the latest AAL-VIZ projection packet from `out/projections/aal_viz.latest.json`.

## Repository Layout

- `apps/api/` contains the read-only FastAPI application.
- `core/` contains the governed execution, projection, overlay, and audit logic.
- `contracts/` contains deterministic pipeline, rune, and route contracts.
- `scripts/` contains the operational entrypoints used to regenerate artifacts and produce governance outputs.
- `out/` contains derived artifacts and latest snapshots written by validation and projection scripts.

## v2.0.4 Governed State Engine

- Governed state engine overview with deterministic, authority-locked state snapshots.
- Deterministic state reduction via ordered transition hashing.
- Stabilization windows driven by replay match/failure counts.
- State lineage semantics with cycle detection and fail-closed behavior.
- Replay-safe state evolution through replay packet validation and rollback gating.
- Rollback doctrine encoded as deterministic rollback packets.
- Operator-reviewed state transitions with explicit pending actions and rollback visibility.

## v2.0.5 Governed Adaptive Sandbox

ABRAXAS v2.0.5 introduces governed adaptive sandboxing for isolated, replay-safe experimentation.

- Isolated branch doctrine: sandbox branches are detached from production and canon mutation authority.
- Replay-safe adaptation: all mutation proposals are deterministic and operator-reviewed.
- Convergence semantics: stabilization quality depends on deterministic replay convergence.
- Sandbox rollback doctrine: rollback readiness is explicit and hash-governed.
- Non-authoritative execution: sandbox outputs are simulated artifacts only, never production mutation.

## v2.0.6 Governed Oracle Intake

- Governed Oracle intake overview with deterministic intake envelopes.
- Deterministic intake normalization and replay-safe ingestion.
- Provenance doctrine: all evidence packets require deterministic provenance chains.
- Conflict semantics with severe unresolved conflicts blocking approval.
- Stabilization-gated approval and operator-reviewed intake flow.
- Oracle intake remains non-authoritative and evidence-bound.

## v2.0.7 Governed Forecast Candidate Layer

- Governed forecast candidate overview with candidate-only doctrine.
- Replay-safe probability packets with calibration-gated scoring.
- Forecast lineage and outcome-binding doctrine for deterministic candidate tracking.
- Stabilization-gated forecast review with explicit unresolved-binding controls.
- Forecast routing remains sandbox-scoped, operator-reviewed, and non-authoritative.

## v2.0.8 Governed Brier Ledger Layer

- Governed Brier ledger overview with deterministic scoring doctrine.
- Replay-safe reliability aggregation and calibration history semantics.
- Deterministic lineage and stabilization-gated scoring review.
- Candidate-only, sandbox-scoped scoring remains non-authoritative.

## v2.0.9 Governed Weight Drift Simulation

- Governed weight drift overview with sandbox-scoped overlay doctrine.
- Replay-safe drift simulation with calibration-bound overlay generation.
- Reliability-aware overlay scoring and stabilization-gated drift review.
- Drift remains non-authoritative and simulated-only.


## Milestone Metadata Spine

- Active milestone is derived from deterministic artifact discovery, not hardcoded labels.
- Stale hardcoded milestone labels fail doctrine milestone validation.
- Milestone lineage and registry hashing are deterministic and authority-locked.
- This prevents silent milestone drift before v2.1.0 governance activation.


## v2.1.0 Governed Canary Overlay Layer

- Governed canary overlays are shadow-scoped, replay-safe, and non-authoritative.
- Overlay influence remains bounded and calibration-gated before any stabilization signal.
- Routing is replay-safe with explicit blocked production routes.
- Rollback semantics are deterministic, reversible, and operator-gated.
- Overlay review is operator-mediated; no autonomous promotion or authority escalation is permitted.


## v2.1.1 Governed Overlay Observability Fusion

- Overlay observability fuses canary, drift, forecast, and Brier signals into diagnostic-only telemetry.
- Replay-safe overlay telemetry is deterministic and projection-only.
- Stability scoring is deterministic and degrades under replay failures and critical diagnostics.
- Critical diagnostics are surfaced for operator action and never mutate runtime state.
- Overlay observability remains non-authoritative, fail-closed, and operator-reviewed.


## v2.1.2 Governed Canary Policy Scheduler

- Governed scheduler proposes replay-safe observation windows for canary overlays.
- Eligibility is deterministic across stability, replay failures, rollback readiness, and critical diagnostics.
- Blocked schedule reasons are explicit and operator-reviewable.
- Schedule replay validation is deterministic and fail-closed on mismatches.
- Scheduler remains non-authoritative and never activates production mutation.

## v2.1.4 Governed Overlay Governance Ledger

- Introduces an append-only governed overlay governance ledger for audit-only event semantics.
- Adds deterministic continuity scoring across expected vs observed governance events.
- Adds replay-safe governance audit packets and deterministic replay sealing checks.
- Adds critical diagnostic handling that blocks governance seal when unresolved.
- Remains non-authoritative: no promotion, no traffic routing, no Canon/runtime mutation authority.
