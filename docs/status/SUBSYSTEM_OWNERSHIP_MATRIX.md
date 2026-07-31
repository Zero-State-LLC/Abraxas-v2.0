# Subsystem Ownership Matrix

Status: `SUBSYSTEM_OWNERSHIP_MATRIX_REFRESH_READY_ADVISORY_ONLY`
Brier Score: 0.10

This is a repo-native registry projection derived from pipeline inventory and observed pipeline contracts. It documents subsystem ownership without granting governance, runtime, sandbox, MCP, canon, or writeback authority.

## Current Summary

- Subsystems observed: `18`
- Pipelines observed: `18`
- Contract-aligned subsystems: `10`
- Missing contract paths: `8`

## Repo-Native Ownership Routes

| Subsystem | Pipelines | Tier(s) | Lane(s) | Contract alignment | Next action |
| --- | --- | --- | --- | --- | --- |
| AAL-Viz | aal_viz_projection | 1 | PROJECTION | ALIGNED | enforce projection-only packet contract globally |
| BeatOven / PsyFi | beatoven_psyfi_integration | 3 | SHADOW_ARTIFACT | MISSING_CONTRACT | define shared runic core pipeline contract |
| Canon Governance | canon_sync | 1 | GOVERNANCE | ALIGNED | formalize canon sync receipts and repo execution boundaries |
| Governance / Drift Detection | drift_scan | 2 | SHADOW_GOVERNANCE | ALIGNED | standardize drift scan outputs as pipeline receipts |
| HollerSports | hollersports_ticket | 2 | FORECAST_GATED | MISSING_CONTRACT | add forecast proof, outcome binding, and operator packet chain |
| Level 99 | level99_content | 3 | SHADOW_MEDIA | MISSING_CONTRACT | add virality scoring boundaries and operator review |
| Neon Genie | neon_genie_ideation | 3 | SHADOW_PRODUCT | CONTRACT_V0 | IdeationOperatorPacket.v0 (`core/neon_genie/ideation_operator_packet.py`); next: wire skill package stage; Hermes packaging remains external |
| Noctis | noctis_dream | 3 | SHADOW_SYMBOLIC | MISSING_CONTRACT | convert dream analysis to receipt plus IR plus review pipeline |
| Operator Governance | operator_review_queue | 2 | GOVERNANCE | ALIGNED | bind operator review queue to doctrine validation and canon sync receipt surfaces |
| Oracle / ASE / Memetic Futurecast | memetic_futurecast | 2 | SHADOW_FORECAST_GATED | MISSING_CONTRACT | add horizon policy, validation gates, and Brier bridge |
| Oracle Signal Layer | oracle_signal | 2 | SHADOW | ALIGNED | bind Oracle packets to global pipeline envelope |
| Outcome Binding / Brier Ledger | outcome_brier | 1 | FORECAST_GOVERNANCE | ALIGNED | add doctrine-compatible operator review and canon sync receipts |
| PSE Forecast Engine | pse_forecast | 1 | FORECAST_GATED | ALIGNED | add positive and negative proof packets before forecast influence |
| Phonomicon | phonomicon_artifact | 3 | ARTIFACT_GOVERNANCE | MISSING_CONTRACT | bind provenance and artifact proof chain |
| Research Intake Automation | research_intake | 1 | GOVERNANCE_SHADOW | ALIGNED | implement one-shot automator from AUTOMATE_RESEARCH_INTAKE_TO_VALIDATION_PIPELINE_001 |
| Research Validation | research_drop_validation | 1 | GOVERNANCE_SHADOW | ALIGNED | bind validation harness to global pipeline spine |
| Universal Ingest | universal_ingest | 1 | GOVERNANCE_SHADOW | ALIGNED | convert ingest source to global pipeline contract |
| abx-familiar | familiar_ingestion | 2 | SHADOW | RECEIPT_V0 | EvidencePack → FamiliarIngestionReceipt.v0 (`core/ingest/familiar_ingestion_receipt.py`); next: oracle/belief shadow bridge |

## Why This Matters

The repo previously preserved this surface only as a partial Notion mirror. Slice58 replaces that placeholder posture with repo-observed ownership evidence so contributors can route architecture, contracts, tests, and receipts without depending on an embedded database view.

## Next Action

- Verify the receipt: [`../out/audit/subsystem_ownership_matrix_refresh_001.latest.json`](../out/audit/subsystem_ownership_matrix_refresh_001.latest.json)
- Use [`../core/pipelines/registry.py`](../core/pipelines/registry.py) when extending subsystem routes.
- Keep `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` unissued unless the operator explicitly provides it in a future gate.

## Boundary Note

Projection and registry routing only. No sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous Notion/GitHub writeback is authorized.

Provenance: Notion Sprint 001 Hub + Loop 805 Slice58 + Hash: receipt canonical_hash
