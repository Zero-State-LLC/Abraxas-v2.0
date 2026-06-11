# ABRAXAS

```text
   ██████ ██████ ██████  █████ ██   ██ █████ ███████
  ███████ ███████ ███████ ███████ ███████ ███████
  ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██
  ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██
  ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██
   █████  ██████  ██████   █████  ██   ██  █████  ███████
```

**Governed Symbolic Intelligence**

Deterministic • Observable • Recursive

![Version](https://img.shields.io/badge/version-2.1.0-0A66C2)

---

<details>
<summary><strong>Table of Contents</strong> (click to expand)</summary>

- [Repository Status](#repository-status)
- [Developer Workflow](#developer-workflow)
- [01. Architecture](#01-architecture)
- [02. Governance](#02-governance)
- [03. Continuity Spine](#03-continuity-spine)
- [04. Evidence Surfaces](#04-evidence-surfaces)
- [05. Routing and Rune Binding](#05-routing-and-rune-binding)
- [06. Repository Signal Surface](#06-repository-signal-surface)
- [07. System Atlas](#07-system-atlas)
- [08. Architecture Diagrams](#08-architecture-diagrams)
- [09. Repository Topology](#09-repository-topology)
- [10. Repo ↔ Notion Reconciliation](#10-repo--notion-reconciliation)
- [11. Roadmap](#11-roadmap)
- [12. Operator Paths](#12-operator-paths)
- [13. Research Domains](#13-research-domains)
- [Optimization](#optimization)
- [14. Shields / GitHub Pages](#14-shields--github-pages)
- [15. Footer](#15-footer)

</details>

---

## Repository Status

| Area                        | Status          | Last Major Change                              | Notes |
|-----------------------------|-----------------|------------------------------------------------|-------|
| CI/CD Stability             | Excellent       | Reusable workflows + cleanup of temp flags     | Very clean and efficient |
| Governance                  | Strong          | PR/Issue templates + CODEOWNERS                | Good foundation |
| Automation & Tooling        | Excellent       | organize_scripts.py + completions + release wf | Full modern DX |
| Security Posture            | Strong          | CodeQL + Dependency Review blocking            | Proper gates |
| Documentation               | Good            | Status table + STATUS.md + ToC                 | Well maintained |
| Release Process             | Started         | Reusable create-release workflow               | Foundation ready |

---

## Developer Workflow

This repo uses a governed **CLI Operator Layer** for token-efficient, evidence-first AI-assisted development across GitHub, Notion, and CLI agents (Grok, Codex, and compatible tools).

**Primary rule:** Send the AI the smallest complete evidence packet — never a full repo dump.

Full specification, operator map, Abraxas-specific command recipes, evidence-packet template, and drift-watch rules:
[`docs/workflows/cli-operator-layer.md`](docs/workflows/cli-operator-layer.md)

**Key operators include:** `rg` / `jq` / `gh` / `repomix` / `fd` / `yq` / `fzf` and others for precise scoping.

**Minimal evidence packet example:**

```bash
rg "recommended_next_lane|governance_status|canon_status|NOT_COMPUTABLE|P102G"
jq '{lane_count, highest_observed_lane, governance_status, canon_status}' docs/status/continuity-spine.json
gh pr view <PR_NUMBER> --json number,title,mergeable,headRefName,statusCheckRollup
git diff --stat
```

See also: Notion reconciliation surfaces and the full invocation order in the workflow document.

---

## 01. Architecture

Abraxas is a governed symbolic intelligence architecture for deterministic execution. It encodes computation as contract-bound artifacts, route decisions, and replay-safe evidence chains. Every meaningful surface points back to observable files, schemas, and receipts.

**Execution posture:** fail-closed.  
**Governance posture:** advisory-first, evidence-gated.  
**Routing posture:** deterministic, replayable, formalized advisory surface.

No implied authority escalation from status pages, projections, or research overlays.

```
Operator
  ↓
Oracle Signal Layer      — intake, normalization, replay-safe signal attachment
  ↓
YGGDRASIL Routing        — deterministic symbolic path control
  ↓
ABX-Runes                — contract-bound symbolic operators (24 observed)
  ↓
Governance Engine        — promotion gates, receipts, stabilization windows
  ↓
Temporal Continuity      — lane evidence, progression tracking, holds
  ↓
Artifact Registry        — deterministic evidence snapshots
```

Evidence paths:
- `contracts/runes/catalog.v1.json` — rune catalog
- `contracts/yggdrasil/routes/*.route.v1.json` — route graphs
- `contracts/pipelines/*.v1_1.json` — pipeline contracts
- `core/yggdrasil_geometric_route_metadata.py` — route metadata
- `out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json` — formalized advisory binding surface

---

## 02. Governance

![Governance Promotion](docs/media/governance-promotion.svg)

```
SEED → SHADOW → CANARY → PROMOTION → CANON
```

- **SEED:** candidate framing only; no execution authority.
- **ABX-Core:** symbolic runtime constrained by contract gates.
- **Shadow vs Forecast:** shadow is observational execution; forecast authority remains denied unless explicitly promoted.
- **Promotion Gates:** evidence, replay, and governance receipts required before lane transition.
- **Stabilization Windows:** convergence windows gate progression readiness.
- **12-Run Invariance:** maintain deterministic replay consistency across repeated runs.
- **Complexity Rent:** uncontrolled complexity blocks promotion readiness.

Governance evidence: `out/audit/governance_freeze_baseline_001.latest.json`  
Governance status (observed): `FROZEN` (source: `docs/status/badges.json#signals.governance_status`)  
Canon status (observed): `ADVISORY_ONLY` (source: `docs/status/badges.json#signals.canon_status`)

---

## 03. Continuity Spine

Source: `docs/status/continuity-spine.json`  
Schema: `continuity_spine_surface.v1`

| Signal | Value |
|---|---|
| Observed lane count | `58` |
| Highest observed lane | `P102G` |
| Source | `docs/status/continuity-spine.json` |

Lane progression (observed):
```
P0 • P1 • P1A • P1C • P2 • P2A • P2C • P40 • P42 • P43 • P44 • P46 • P47 •
P48 • P52 • P58 • P60 • P61 • P63 • P71 • P72 • P73 • P74 • P75 • P76 • P77 •
P78 • P79 • P80 • P81 • P82 • P83 • P84 • P85 • P86 • P87 • P88 • P89 • P90 •
P91 • P92 • P93 • P94 • P95 • P96 • P97 • P98 • P99 • P100 • P101 • P102 •
P102A • P102B • P102C • P102D • P102E • P102F • P102G
```

If continuity data is unavailable: `NOT_COMPUTABLE`.

Documentation alignment invariant (repo-visible, advisory-only):
- Continuity spine baseline remains `lane_count=58` and `highest_observed_lane=P102G`; do not merge the research-canary P103→P130 chain into the temporal-continuity lane count unless the continuity status surface explicitly changes.
- Downstream remains `NOT_COMPUTABLE` wherever explicit operator-decision evidence is missing.
- P102G remains audit-only and creates no approval record, authorization record, execution path, or downstream continuity lane.

Research canary advisory chain (separate from the temporal-continuity status baseline):
- PLANS records a repo-visible post-P130 implementation edge with advisory research-canary continuity from `P103` through `P130`.
- P130 routes to operator hold and does not authorize activation, runtime execution, scheduler mutation, canon promotion, forecast influence, or token minting.
- No P131 is introduced by the current documentation/status alignment pass.

Active handoff (P102F → P102G):
- Source lane: `operator_authorization_record_decision_reconciliation_receipt`
- Governance directives: `SEAL_RECURSIVE_AUTHORIZATION_CHAIN`, `COMPRESS_TO_GENERIC_TEMPLATE`
- Follow-up routes: `run_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt.py`, `run_temporal_continuity_historical_recovery_audit.py`
- Current terminal audit: `P102G_TEMPORAL_CONTINUITY_HISTORICAL_RECOVERY_AUDIT`
- Current downstream lane: `NOT_COMPUTABLE`; explicit operator decision evidence remains required

Recursive authorization chain handoff references:
- `python scripts/run_temporal_continuity_recursive_authorization_chain_compression_audit.py`
- `out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json`
- `python scripts/run_temporal_continuity_repair_execution_plan_router.py`
- `out/temporal_continuity_repair_execution_plan_router/latest.json`
- `python scripts/run_temporal_continuity_selected_repair_execution_plan.py`
- `out/temporal_continuity_selected_repair_execution_plan/latest.json`
- do not add another hand-written recursive authorization lane after `SEAL_RECURSIVE_AUTHORIZATION_CHAIN` or `COMPRESS_TO_GENERIC_TEMPLATE`; route to the recommended post-P102 lane instead.

---

## 04. Evidence Surfaces

Generated observational surfaces — these are read-only, advisory-only outputs:

| Surface | Path | Status |
|---|---|---|
| Repository signal badges | `docs/status/badges.json` | OBSERVED |
| Continuity spine | `docs/status/continuity-spine.json` | OBSERVED |
| Repo ↔ Notion reconciliation | `docs/audits/ABRAXAS_REPO_NOTION_DIFF_001.md` | OBSERVED |
| Binding matrix audit | `docs/audits/ABRAXAS_BINDING_MATRIX_AND_COUPLING_MAP_AUDIT_001.md` | OBSERVED |
| Rune/route binding matrix | `out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json` | OBSERVED |
| Coupling map | `out/audit/yggdrasil_coupling_map_001.latest.json` | OBSERVED |
| Governance receipt | `out/audit/governance_freeze_baseline_001.latest.json` | OBSERVED |
| Temporal continuity artifact | `out/temporal_continuity_evidence_index/latest.json` | OBSERVED |
| Controlled ingest governance audit | `out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json` | OBSERVED |
| Oracle intake queue | `out/ingest/oracle_intake_queue_001.latest.json` | OBSERVED |
| Notion spec completion queue | `out/sync/notion_spec_completion_queue/latest.json` | `COMPLETION_QUEUE_EMITTED_ADVISORY_ONLY` |
| Operator decision backlog | `out/sync/notion_operator_decision_backlog/latest.json` | `OPERATOR_DECISION_BACKLOG_EMITTED_ADVISORY_ONLY` |
| Global Ingest Adapter Spine alignment plan | `out/sync/global_ingest_adapter_spine_alignment_plan/latest.json` | `ALIGNMENT_PLAN_EMITTED_ADVISORY_ONLY` |
| Oracle Signal Intake Boundary implementation plan | `out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json` | `IMPLEMENTATION_PLAN_EMITTED_ADVISORY_ONLY` |
| Oracle Signal shadow intake receipt | `out/oracle/oracle_signal_intake_receipt.latest.json` | `ORACLE_SIGNAL_INTAKE_RECEIPT_EMITTED_ADVISORY_ONLY` |
| Oracle Signal shadow intake operator review request | `out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json` | `ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_REQUEST_HELD` |
| Oracle Signal shadow intake operator review decision record | `out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json` | `ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_COMPLETION_APPROVED` |
| Oracle Confidence Calibration contract dry run | `out/sync/oracle_confidence_calibration_contract_dry_run/latest.json` | `ORACLE_CONFIDENCE_CALIBRATION_CONTRACT_DRY_RUN_READY` |
| Artifact lineage direct repair validation plan | `out/sync/abx_artifact_lineage_registry_direct_repair_validation_plan/latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_PLAN_READY` |
| Documentation alignment receipt | `out/sync/documentation_alignment_receipt_001.latest.json` | `DOCUMENTATION_ALIGNMENT_RECEIPT_EMITTED_ADVISORY_ONLY` |
| Status regeneration receipt | `out/sync/status_regeneration_receipt_001.latest.json` | `STATUS_REGENERATION_RECEIPT_EMITTED_ADVISORY_ONLY` |
| Artifact-lineage direct repair operator decision record | `out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_APPROVED_FOR_SEPARATE_EXECUTION_SPEC` |
| Artifact-lineage direct repair separate execution spec plan | `out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_READY` |
| Artifact-lineage direct repair execution authorization gate | `out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| Artifact-lineage direct repair execution authorization record | `out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR` |
| Artifact-lineage direct repair scoped execution receipt | `out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED` |
| Artifact-lineage Notion mapping evidence request | `out/operator_review/abx_artifact_lineage_notion_mapping_evidence_request_001.latest.json` | `ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_HELD` |
| Artifact-lineage runner casing policy review request | `out/operator_review/abx_artifact_lineage_runner_casing_policy_review_request_001.latest.json` | `ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_REVIEW_REQUEST_HELD` |
| Artifact-lineage Notion mapping scope resolution record | `out/operator_review/abx_artifact_lineage_notion_mapping_scope_resolution_record_001.latest.json` | `ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_SCOPE_RESOLUTION_RECORD_ACCEPTED` |
| Artifact-lineage runner casing policy decision record | `out/operator_review/abx_artifact_lineage_runner_casing_policy_decision_record_001.latest.json` | `ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_DECISION_RECORD_ACCEPTED` |
| Belief Graph Engine advisory spec plan | `out/audit/belief_graph_engine_advisory_spec_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_SPEC_PLAN_READY` |
| Belief Graph Engine advisory receipt contract plan | `out/audit/belief_graph_engine_advisory_receipt_contract_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CONTRACT_PLAN_READY` |
| Belief Graph Engine advisory receipt implementation plan | `out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_PLAN_READY` |
| Belief Graph Engine advisory receipt implementation authorization gate | `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_gate_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| Belief Graph Engine advisory receipt implementation authorization record plan | `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_READY` |
| Belief Graph Engine advisory receipt implementation authorization record creation plan | `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY` |
| Belief Graph Engine advisory receipt implementation authorization record creation authorization gate | `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| Belief Graph Engine advisory receipt implementation authorization record creation record plan | `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN_READY` |
| Belief Graph Engine advisory receipt authorization chain compression audit | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_READY` |
| Belief Graph Engine advisory receipt authorization chain seal receipt plan | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_PLAN_READY` |
| Belief Graph Engine advisory receipt authorization chain seal receipt dry run | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN_READY` |
| Operator authorization seal review | `out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json` | `OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_REVIEW_HELD_FOR_OPERATOR` |

These surfaces do not grant authority, do not promote canon, and do not alter runtime behavior.

Current operator-sync/planning states:
- **Namespace/status stabilization:** repository badges and continuity spine are observational deterministic surfaces; `governance_status=FROZEN`, `canon_status=ADVISORY_ONLY`, `lane_count=58`, and `highest_observed_lane=P102G` are preserved.
- **Operator sync:** Notion queue/backlog surfaces are advisory-only, deny Notion/GitHub writeback, and deny auto-continuation. The Oracle Signal shadow intake review decision record accepts the shadow receipt as review-only evidence without opening downstream authority.
- **Oracle planning:** Oracle Signal Intake Boundary and Oracle Confidence Calibration surfaces are planning/dry-run evidence only. The additive Oracle Signal shadow receipt is reviewed evidence only; it grants no forecast, runtime, queue, canon, scheduler, route, writeback, token, or execution authority.
- **Authorization seal state:** P81-P95 operator authorization record planning surfaces are present, but the seal review is held for operator review. Approval, authorization, token minting, and execution authority remain false.
- **Artifact-lineage repair planning:** Direct repair has an advisory-only separate execution spec plan and scoped execution receipt. Registry repairs, markdown/JSON pairing repairs, docs-reference repairs, runner casing discovery, and Notion mapping scope are classified by explicit advisory records; live Notion/GitHub writeback, runner path normalization, runtime/canon/queue mutation, and unscoped execution remain denied. Unsupported downstream execution claims remain `NOT_COMPUTABLE`.

---

## 05. Routing and Rune Binding

Route/rune binding is now a formalized advisory surface sourced from repository contracts.

**Binding matrix summary** (source: `out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json`):
- Total runes in catalog: `24`
- Bound runes (present in at least one pipeline): `20`
- Unbound runes: `4` (`RUNE.PIPELINE.OPERATOR_REVIEW`, `RUNE.PIPELINE.STABILIZATION_DECIDE`, `RUNE.YGGDRASIL.ROUTE_RECEIPT`, `RUNE.YGGDRASIL.UNKNOWN_NODE_GATE`)
- Pipelines: `7`
- Route-reachable pipelines: `7`
- Required mapping rows: `89`
- Binding classification: `PARTIAL` (route rune nodes observed without explicit `rune_id` field linkage)
- Advisory status: `BINDING_SURFACE_FORMALIZED_ADVISORY_ONLY`

**Coupling map** (source: `out/audit/yggdrasil_coupling_map_001.latest.json`):
- Derived from: pipeline contracts + route graphs
- Authority locks: all `false` (deny-by-default across all rune/pipeline/route surfaces)

This surface is advisory-only. It describes observed binding topology; it does not grant routing authority.

---

## 06. Repository Signal Surface

Status values generated automatically from repository scans. Badge endpoint availability is conditional: treat Pages-backed badges as live only when `ENABLE_STATUS_PAGES_DEPLOY=true` and GitHub Pages is configured.

| Signal | Observed Value | Source | Badge (deployment-dependent) |
|---|---|---|---|
| Build Status | `NOT_COMPUTABLE` | `badges.json#signals.build_status` | ![Build](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/build.json) |
| Test Status | `NOT_COMPUTABLE` | `badges.json#signals.test_status` | ![Tests](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/tests.json) |
| Coverage Status | `NOT_COMPUTABLE` | `badges.json#signals.coverage_status` | ![Coverage](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/coverage.json) |
| Contracts | `362` | `badges.json#signals.contract_count` | ![Contracts](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/contracts.json) |
| Schemas | `342` | `badges.json#signals.schema_count` | ![Schemas](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/schemas.json) |
| Runes | `24` | `badges.json#signals.rune_count` | ![Runes](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/runes.json) |
| Continuity Lanes | `58` | `badges.json#signals.continuity_lane_count` | ![Continuity](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/continuity.json) |
| Governance Status | `FROZEN` | `badges.json#signals.governance_status` | ![Governance](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/governance.json) |
| Canon Status | `ADVISORY_ONLY` | `badges.json#signals.canon_status` | ![Canon](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/canon.json) |

Extended observed counts (source: `docs/status/badges.json#live_status`):
- Observed Tests: `750`
- Observed Artifacts: `561`
- Last Observed Commit: `NOT_COMPUTABLE`
- Last Scan Time: `NOT_COMPUTABLE`

---

## 07. System Atlas

Master atlas: [`docs/atlas/ABRAXAS_ATLAS.md`](docs/atlas/ABRAXAS_ATLAS.md)

| Surface | Atlas Card | Status |
|---|---|---|
| Oracle Signal Layer | [`docs/atlas/oracle-signal-layer.md`](docs/atlas/oracle-signal-layer.md) | OBSERVED |
| YGGDRASIL Routing | [`docs/atlas/yggdrasil-routing.md`](docs/atlas/yggdrasil-routing.md) | OBSERVED |
| ABX-Runes | [`docs/atlas/abx-runes.md`](docs/atlas/abx-runes.md) | OBSERVED |
| Governance Engine | [`docs/atlas/governance-engine.md`](docs/atlas/governance-engine.md) | OBSERVED |
| Temporal Continuity Spine | [`docs/atlas/temporal-continuity-spine.md`](docs/atlas/temporal-continuity-spine.md) | OBSERVED |
| Research Canary | [`docs/atlas/research-canary.md`](docs/atlas/research-canary.md) | OBSERVED |
| AAL-Viz | [`docs/atlas/aal-viz.md`](docs/atlas/aal-viz.md) | OBSERVED |
| Artifact Registry | [`docs/atlas/artifact-registry.md`](docs/atlas/artifact-registry.md) | OBSERVED |

---

## 08. Architecture Diagrams

- ![Oracle Signal Layer](docs/media/oracle-signal-layer.svg)
- ![Governance Promotion](docs/media/governance-promotion.svg)
- ![Temporal Continuity Spine](docs/media/temporal-continuity-spine.svg)
- ![YGGDRASIL Routing](docs/media/yggdrasil-routing.svg)
- ![ABX-Runes](docs/media/abx-runes.svg)
- ![AAL Core](docs/media/aal-core.svg)

Visual system specification: [`docs/media/README_VISUAL_SYSTEM.md`](docs/media/README_VISUAL_SYSTEM.md)

---

## 09. Repository Topology

```text
apps/         read-only API and service entrypoints
core/         deterministic symbolic/gov/runtime logic
  core/optimization/  — Bayesian meta-optimization & Optuna backend (Sprint 4)
contracts/    schemas and contract-bound architecture surfaces
docs/         atlas, audits, plans, visual system, status surfaces
fixtures/     replay fixtures and static verification data
input/        operator-provided runtime inputs and decisions
out/          generated artifacts and governance evidence
scripts/      deterministic generator and replay entrypoints
tests/        replay-stable validation suites
```

---

## 10. Repo ↔ Notion Reconciliation

Source: `docs/audits/ABRAXAS_REPO_NOTION_DIFF_001.md`

Post-refresh note: the repo/Notion advisory sync artifacts were refreshed after the P95 authorization seal review merge. The refreshed queue/backlog still denies Notion writeback, GitHub writeback, auto-continuation, runtime mutation, scheduler mutation, canon mutation, activation, and execution authority.

| Surface | Status | Evidence |
|---|---|---|
| YGGDRASIL ABX-Runes Full Stack Binding | PARTIAL | binding matrix emitted; route rune_id linkage partial |
| Tier-1 Subsystem Registry | OBSERVED | `core/pipelines/registry.py` |
| Runtime Integration Gate | PARTIAL | runtime spine skeleton present |
| Global Ingest Adapter Spine | PARTIAL | scheduler, handoff executor, ingest queue, additive Oracle Signal shadow receipt, review request, and review-only decision record observed; execution remains advisory-only |
| Belief Graph Engine | ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN_READY | seal receipt dry run emitted; seal creation, receipt code, and engine implementation remain blocked |
| Research Shadow Replay Engine | OBSERVED | `core/research_shadow_replay_audit.py` |
| Phase Percolation Engine | PARTIAL | partial temporal surfaces only |
| AAL-Viz Projection Spine | OBSERVED | `core/aal_viz_runtime_projection.py` |
| Situation Runtime Engine | PARTIAL | advisory console observed |
| ABX Codegen Intelligence Spine | MISSING | `NOT_COMPUTABLE` — no modules/contracts |

Overall reconciliation status: `PARTIAL`

Current sync frontier: `Global Ingest Adapter Spine` has reached an additive Oracle Signal shadow intake receipt and review-only decision record. It remains blocked before any Oracle Signal implementation, ingest runner mutation, queue mutation, or route/runtime integration work.

---

## 11. Roadmap

Roadmap items included only where evidence is observable in-repo.

| Item | Status | Evidence |
|---|---|---|
| Route/Rune Binding | `FORMALIZED_ADVISORY` | `out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json` |
| Belief Graph | `ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN_READY` | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.json`; seal creation, receipt code, and engine implementation remain blocked |
| Global Ingest | `PARTIAL` | `Scripts/run_ingest_scheduler.py`, `Scripts/run_ingest_handoff_executor.py`, `out/ingest/oracle_intake_queue_001.latest.json`, `out/oracle/oracle_signal_intake_receipt.latest.json`, `out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json`, `out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json` |
| Research Shadow Replay | `OBSERVED` | `scripts/run_research_shadow_replay_audit.py` |
| Phase Percolation | `NOT_COMPUTABLE` | partial only |
| AAL-Viz Projection | `OBSERVED` | `scripts/run_aal_viz_runtime_projection.py` |
| Codegen Intelligence Spine | `NOT_COMPUTABLE` | no implementation surface found |
| Situation Runtime | `OBSERVED` | `scripts/run_operator_runtime_console.py` |

---

## 12. Operator Paths

- **NEW OPERATOR:** [`docs/operators/new-operator.md`](docs/operators/new-operator.md)
- **RESEARCHER:** [`docs/operators/researcher.md`](docs/operators/researcher.md)
- **ARCHITECT:** [`docs/operators/architect.md`](docs/operators/architect.md)
- **CONTRIBUTOR:** [`docs/operators/contributor.md`](docs/operators/contributor.md)

---

## 13. Research Domains

- [Symbolic Compression](docs/audits/REPO_AUDIT_CHAMFER_EXPECTED_DISTANCE_POLICY_PLAN_v0_1.md)
- [Temporal Resonance](scripts/run_temporal_resonance_coherence.py)
- [Governance Systems](docs/generated_artifact_policy_v1.md)
- [Coherence Fields](scripts/run_coherence_field_operator_surface.py)
- [Forecast Architecture](scripts/run_forecast_candidates.py)
- [Persistence Geometry](scripts/run_temporal_persistence_memory.py)
- [Topology Research](scripts/run_temporal_topology_cartography.py)
- [Research Canary](docs/atlas/research-canary.md)

---

## Optimization

Meta-optimization and Bayesian hyperparameter tuning infrastructure (Sprint 4).

- Location: `core/optimization/`
- Optuna backend wrapper for provenance-aware tuning: `core/optimization/optuna_backend.py`
- Module README: `core/optimization/README.md`

Supports higher-order calibration of prediction engines, rune/route parameters, governance surfaces, and forecast pipelines. All optimization runs remain under the same governance, evidence, and replay rules as the rest of the system.

Status: OBSERVED

---

## 14. Shields / GitHub Pages

Badge endpoints are available after a successful GitHub Pages deployment (`ENABLE_STATUS_PAGES_DEPLOY=true`, Pages configured).

Treat all endpoints as deployment-dependent until Pages has completed successfully:
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges.json`
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/contracts.json`
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/schemas.json`
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/tests.json`
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/continuity.json`
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/governance.json`

---

## 15. Footer

```
README_STATUS_SURFACE_UPDATED=true
CANON_MUTATION=false
RUNTIME_MUTATION=false
FORECAST_ROUTING=false
EXECUTION_AUTHORITY=false
```

**ABRAXAS**  
A governed symbolic intelligence architecture.  
Built within the Applied Alchemy Labs ecosystem.  
Structure before narrative.  
Evidence before authority.  
Governance before autonomy.
