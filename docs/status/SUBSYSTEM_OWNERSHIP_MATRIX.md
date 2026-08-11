# Subsystem Ownership Matrix

Status: `SUBSYSTEM_OWNERSHIP_MATRIX_REFRESH_READY_ADVISORY_ONLY`
Brier Score: 0.10

This is a repo-native registry projection derived from pipeline inventory and observed pipeline contracts. It documents subsystem ownership without granting governance, runtime, sandbox, MCP, canon, or writeback authority.

This matrix and the `alembic_spine` block in [`../../PLANS.md`](../../PLANS.md)
are the canonical status truth for current ownership and planning posture.
They are a documentation projection, not a database; no second status DB or
competing status-tracking document is authoritative. Historical plans remain
useful context but must not override these routes.

## Current Summary

- Subsystems observed: `18`
- Pipelines observed: `18`
- Contract-aligned subsystems: `18` (ALIGNED)
- Partial contracts: `0` (CONTRACT_V0 ×0 + REVIEW_V0 ×0)
- Missing contract paths: `0`
- Missing full pipeline v1.1 contracts (optional depth): `0`

Alignment tiers: `ALIGNED` = `contracts/pipelines/*.v1_1.json`; `CONTRACT_V0` = operator packet + builder; `REVIEW_V0` = familiar receipt/bridge/review/dry-run chain; `MISSING_CONTRACT` = neither full nor operator packet observed.

## Repo-Native Ownership Routes

| Subsystem | Pipelines | Tier(s) | Lane(s) | Contract alignment | Next action |
| --- | --- | --- | --- | --- | --- |
| AAL-Viz | aal_viz_projection | 1 | PROJECTION | ALIGNED | enforce projection-only packet contract globally |
| BeatOven / PsyFi | beatoven_psyfi_integration | 3 | SHADOW_ARTIFACT | ALIGNED | BeatOvenPsyFiIntegrationOperatorPacket.v0 landed (shared runic core + sonic plan seed); next: optional graph materialization; plan-only |
| Canon Governance | canon_sync | 1 | GOVERNANCE | ALIGNED | formalize canon sync receipts and repo execution boundaries |
| Governance / Drift Detection | drift_scan | 2 | SHADOW_GOVERNANCE | ALIGNED | standardize drift scan outputs as pipeline receipts |
| HollerSports | hollersports_ticket | 2 | FORECAST_GATED | ALIGNED | CONTRACT_V0 + HollerOutcomeBindingDryRun.v0 landed (projects ForecastOutcomeBindingPacket.v1); no binding write / no live odds; residual: optional live ingest wire under dual-control |
| Level 99 | level99_content | 3 | SHADOW_MEDIA | ALIGNED | Level99ContentOperatorPacket.v0 landed (virality bounds + route + operator review); next: optional performance ingest wire; no auto-publish |
| Neon Genie | neon_genie_ideation | 3 | SHADOW_PRODUCT | ALIGNED | skill package/router wired to IdeationOperatorPacket.v0; optional fixture corpus; Hermes packaging handoff remains external |
| Noctis | noctis_dream | 3 | SHADOW_SYMBOLIC | ALIGNED | CONTRACT_V0 + NoctisOperatorReviewQueueDryRun.v0 landed (queue shape + continuity seed); no queue/memory write; residual: dual-control before any durable history link |
| Operator Governance | operator_review_queue | 2 | GOVERNANCE | ALIGNED | bind operator review queue to doctrine validation and canon sync receipt surfaces |
| Oracle / ASE / Memetic Futurecast | memetic_futurecast | 2 | SHADOW_FORECAST_GATED | ALIGNED | CONTRACT_V0 + MemeticBrierLedgerDryRun.v0 landed (projects BrierLedgerEntry.v1 shape); no out/brier write / no forecast weight; residual: dual-control before ledger publish |
| Oracle Signal Layer | oracle_signal | 2 | SHADOW | ALIGNED | bind Oracle packets to global pipeline envelope |
| Outcome Binding / Brier Ledger | outcome_brier | 1 | FORECAST_GOVERNANCE | ALIGNED | add doctrine-compatible operator review and canon sync receipts |
| PSE Forecast Engine | pse_forecast | 1 | FORECAST_GATED | ALIGNED | add positive and negative proof packets before forecast influence |
| Phonomicon | phonomicon_artifact | 3 | ARTIFACT_GOVERNANCE | ALIGNED | PhonomiconArtifactOperatorPacket.v0 landed (provenance chain + Proof of Resonance); next: optional export candidate wire; mint still blocked |
| Research Intake Automation | research_intake | 1 | GOVERNANCE_SHADOW | ALIGNED | implement one-shot automator from AUTOMATE_RESEARCH_INTAKE_TO_VALIDATION_PIPELINE_001 |
| Research Validation | research_drop_validation | 1 | GOVERNANCE_SHADOW | ALIGNED | bind validation harness to global pipeline spine |
| Universal Ingest | universal_ingest | 1 | GOVERNANCE_SHADOW | ALIGNED | convert ingest source to global pipeline contract |
| abx-familiar | familiar_ingestion | 2 | SHADOW | ALIGNED | REVIEW_V0: receipt + spine + bridge + operator-review seed + queue dry-run (FamiliarOperatorReviewQueueDryRun.v0) landed; no live queue write; residual: dual-control attestation only before any out/operator_review_queue write |

## Why This Matters

The repo previously preserved this surface only as a partial Notion mirror. Slice58 replaces that placeholder posture with repo-observed ownership evidence so contributors can route architecture, contracts, tests, and receipts without depending on an embedded database view.

## Next Action

- Verify the receipt: [`../out/audit/subsystem_ownership_matrix_refresh_001.latest.json`](../out/audit/subsystem_ownership_matrix_refresh_001.latest.json)
- Use [`../core/pipelines/registry.py`](../core/pipelines/registry.py) when extending subsystem routes.
- Keep `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` unissued unless the operator explicitly provides it in a future gate.

## Boundary Note

Projection and registry routing only. No sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous Notion/GitHub writeback is authorized.

Provenance: Notion Sprint 001 Hub + Loop 805 Slice58 + Hash: receipt canonical_hash
