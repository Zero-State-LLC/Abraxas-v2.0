# ABRAXAS ATLAS

## Identity
- **What it is:** A governed symbolic intelligence architecture with deterministic, evidence-bound execution surfaces.
- **What it is not:** An autonomous runtime, agent swarm, or authority-escalating orchestration layer.
- **Evidence paths:** `README.md`, `ARCHITECTURE.md`, `contracts/`, `out/`.
- **Governance posture:** Advisory-only boundaries, fail-closed defaults, no implicit promotion.
- **Status vocabulary:** OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE / FORMALIZED_ADVISORY.

## Core Surfaces
- **What it is:** The observable repository signals, continuity spine, contracts, tests, and artifacts.
- **What it is not:** A canon mutation endpoint or runtime authority switch.
- **Evidence paths:** `docs/status/badges.json`, `docs/status/continuity-spine.json`, `contracts/`, `tests/`, `out/`.
- **Governance posture:** Observational only; no authority grants.

## Oracle Signal Layer
- **What it is:** Intake, normalization, and replay-safe signal attachment surfaces.
- **What it is not:** A free-form ingest channel or production activation path.
- **Evidence paths:** `scripts/run_oracle_intake.py`, `core/oracle_geometric_signal_attachment.py`, `core/oracle_geometric_attachment_replay_receipt.py`.
- **Governance posture:** Intake remains bounded by deterministic schemas and operator review.

## YGGDRASIL
- **What it is:** Deterministic routing topology for governed symbolic flow.
- **What it is not:** Dynamic authority escalation or autonomous dispatch.
- **Evidence paths:** `scripts/run_yggdrasil_runtime.py`, `core/yggdrasil_geometric_route_metadata.py`, `docs/audits/REPO_AUDIT_YGGDRASIL_GEOMETRIC_ROUTE_STABILIZATION_WINDOW_v0_1.md`.
- **Governance posture:** Route selection is observable, replayable, and fail-closed.

## ABX-Runes
- **What it is:** Explicit symbolic operators and contract-bound rune catalog (24 runes observed).
- **What it is not:** Free-form prompt wrappers or unconstrained LLM tools.
- **Evidence paths:** `contracts/runes/catalog.v1.json`, `scripts/run_rune_replay.py`.
- **Governance posture:** Rune authority flags are deny-by-default.

## Route/Rune Binding Surface
- **What it is:** A formalized advisory surface describing the observed binding topology between ABX-Runes, pipelines, and YGGDRASIL routes. Generated deterministically from repository contracts.
- **What it is not:** A routing authority grant, a canon promotion surface, or an execution dispatch mechanism.
- **Evidence paths:** `out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json`, `out/audit/yggdrasil_coupling_map_001.latest.json`, `docs/audits/ABRAXAS_BINDING_MATRIX_AND_COUPLING_MAP_AUDIT_001.md`.
- **Governance posture:** `BINDING_SURFACE_FORMALIZED_ADVISORY_ONLY`. All authority locks are `false` (deny-by-default). Classification: `PARTIAL` — route rune nodes observed without explicit `rune_id` field linkage.
- **Binding summary:** 24 runes total; 20 bound; 4 unbound; 7 pipelines; 89 required mapping rows.

## Governance
- **What it is:** Promotion gates, audit artifacts, and stabilization windows.
- **What it is not:** Automatic canon promotion or runtime mutation authority.
- **Evidence paths:** `out/audit/governance_freeze_baseline_001.latest.json`, `scripts/run_doctrine_validator.py`, `docs/generated_artifact_policy_v1.md`.
- **Governance posture:** Authority remains explicitly constrained. Observed status: `FROZEN`.

## Temporal Continuity
- **What it is:** Continuity lane evidence and deterministic spine progression (54 lanes observed, highest P102C).
- **What it is not:** Hardcoded milestone claims or speculative lane advancement.
- **Evidence paths:** `docs/status/continuity-spine.json`, `scripts/run_temporal_continuity_*.py`, `out/temporal_continuity_*/latest.json`.
- **Governance posture:** Continuity is observational and evidence-gated.

## Research Canary
- **What it is:** Controlled research surfaces held behind advisory boundaries.
- **What it is not:** Operational activation or production authority.
- **Evidence paths:** `scripts/run_research_canary_*.py`, `out/research_*`, `docs/audits/REPO_FINAL_SEAL_P101_P130_research_canary_evidence_chain_closed.md`.
- **Governance posture:** Hold routing and authorization constraints remain in force.

## AAL-Viz
- **What it is:** Projection and visualization surfaces for observational overlays.
- **What it is not:** Runtime control authority or canon mutation logic.
- **Evidence paths:** `scripts/run_aal_viz_*.py`, `out/projections/`, `docs/audits/REPO_AUDIT_AAL_VIZ_GEOMETRIC_RENDERER_PLANNING_v0_1.md`.
- **Governance posture:** Projection-only and non-authoritative.

## Artifact Registry
- **What it is:** Deterministic artifact inventory, regeneration, and drift validation (488 artifacts observed).
- **What it is not:** A mutable source of authority.
- **Evidence paths:** `scripts/run_artifact_regeneration.py`, `scripts/run_artifact_contract_inventory.py`, `out/`.
- **Governance posture:** Artifact presence informs observation, not promotion.

## Repo ↔ Notion Reconciliation
- **What it is:** An audit surface comparing canonical architecture intent against observed repository reality.
- **What it is not:** A deployment gate or canon promotion trigger.
- **Evidence paths:** `docs/audits/ABRAXAS_REPO_NOTION_DIFF_001.md`.
- **Status:** PARTIAL — strong implementation exists for YGGDRASIL, ABX-Runes, Tier-1 registry, research shadow replay; Runtime Integration Gate now has an advisory receipt, Belief Graph remains planning-only, and Codegen Intelligence Spine has an advisory gap-analysis plan.

## Not-Computable Surfaces
- **Belief Graph Engine:** `NOT_COMPUTABLE` — no module, contract, runner, or artifact observed.
- **ABX Codegen Intelligence Spine:** `GAP_ANALYSIS_PLAN_READY` — `out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json`; implementation, code generation, code mutation, file writeback, and execution remain blocked.
- **Phase Percolation Engine:** `NOT_COMPUTABLE` (partial temporal surfaces only).

## Final Seal
```
CANON_MUTATION=false
RUNTIME_MUTATION=false
FORECAST_ROUTING=false
EXECUTION_AUTHORITY=false
```
