# START HERE

Abraxas Codex v2.7 - respecting custom instructions + surfaces + governance loop + Notion mirror

Status: `D1_PRIORITY3_NAVIGATION_AND_OWNERSHIP_REFRESH_READY_ADVISORY_ONLY`
Brier Score: 0.10

This is the contributor front door for Abraxas v2.7. It is a projection/navigation surface only: it does not govern, activate, mutate canon, expose MCP, run sandboxes, or grant runtime authority.

## 5-Minute Contributor Path

| Minute | Route | Why this matters | Next action |
|--------|-------|------------------|-------------|
| 0-1 | [`README.md`](../README.md) | Establishes repo status, current advisory posture, and broad subsystem map. | Confirm you are on the right repo and branch. |
| 1-2 | [`STATUS.md`](../STATUS.md) | Shows current health and high-level operating state. | Check for active holds or degraded surfaces. |
| 2-3 | [`ARCHITECTURE.md`](../ARCHITECTURE.md) | Explains the system shape before you touch implementation surfaces. | Identify the subsystem you need. |
| 3-4 | [`docs/START_HERE.md`](START_HERE.md) -> [`docs/INDEX.md`](INDEX.md) | Routes by surface role so you do not confuse identity, registry, projection, and execution surfaces. | Pick the correct route below. |
| 4-5 | [`out/audit/`](../out/audit/) receipts + [`core/generated_artifact_registry.py`](../core/generated_artifact_registry.py) | Receipts are the evidence trail; registry mapping explains what is regenerable. | Verify provenance before editing. |

## Repository Navigation Map

| Surface | Primary route | Role | Why this matters | Next action |
|---------|---------------|------|------------------|-------------|
| Identity | [`README.md`](../README.md) | Identity/status | Gives the top-level system frame. | Read before proposing scope. |
| Status | [`STATUS.md`](../STATUS.md) | Status | Summarizes current repo posture. | Check current holds and readiness. |
| Architecture | [`ARCHITECTURE.md`](../ARCHITECTURE.md) | Architecture | Prevents local edits from drifting away from system design. | Follow subsystem ownership. |
| Subsystem routing | [`status/SUBSYSTEM_OWNERSHIP_MATRIX.md`](status/SUBSYSTEM_OWNERSHIP_MATRIX.md) | Registry/projection | Shows which repo-native pipelines currently anchor each subsystem. | Check the matrix before changing module ownership assumptions. |
| Subsystem health | [`status/SUBSYSTEM_HEALTH_DASHBOARD.md`](status/SUBSYSTEM_HEALTH_DASHBOARD.md) | Projection/status | Aggregates ownership, artifact, continuity, migration-runner, and VIZ posture into one contributor-facing health route. | Check here before choosing a Phase 2 follow-on lane. |
| Governance | [`GOVERNANCE_V3.md`](../GOVERNANCE_V3.md), [`AGENTS.md`](../AGENTS.md) | Governance/instructions | Defines authority boundaries and operator control. | Treat as read-only unless explicitly gated. |
| Task board | [Notion Sprint 001 Hub](https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254) | Planning mirror | Living task source of truth. | Mirror via receipts; do not auto-write back. |
| Code modules | [`docs/INDEX.md`](INDEX.md) | Module routing | Connects code areas to supporting docs and receipts. | Navigate by surface role. |
| Generated artifacts | [`docs/artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md) | Registry/artifacts | Explains generated artifact lifecycle and active receipts. | Use no-arg runners where registered. |
| Audits | [`docs/audits/AUDIT_INDEX.md`](audits/AUDIT_INDEX.md) | Audit history | Preserves historical evidence without making it current authority. | Classify, do not delete. |
| Releases | [`docs/releases/RELEASE_INDEX.md`](releases/RELEASE_INDEX.md) | Release/continuation | Shows continuation baselines and historical release chains. | Start from the current baseline. |
| Receipts | [`out/audit/`](../out/audit/) | Evidence | Canonical hashes and provenance for slices. | Verify receipt before merge. |

## Active Work Route

Why this matters: recent Loop 805 work is receipt-first. A contributor should find active evidence without scrolling through every historical chain.

Next action:
- Start with [`docs/INDEX.md`](INDEX.md) for the compact master route.
- Use [`docs/artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md) for generated receipts and regeneration policy.
- Use [`PLANS.md`](../PLANS.md) for active continuation lanes.
- Use the Notion Sprint 001 Hub only as a mirror/source-of-truth reference; do not write back unless the operator explicitly gates it.

## Contributor Guardrails

Why this matters: Abraxas keeps planning, governance, registry, projection, and execution roles separate.

Next action:
- Preserve `CANON_MUTATION=false`, `RUNTIME_MUTATION=false`, `EXECUTION_AUTHORITY=false`, `MCP_EXPOSURE=false`, and `NOTION_WRITEBACK=false` unless an explicit operator gate says otherwise.
- Prefer receipt-backed changes under `out/audit/*.latest.json`.
- Register deterministic generated artifacts in [`core/generated_artifact_registry.py`](../core/generated_artifact_registry.py).
- Keep docs navigation changes concise; do not delete historical audit/release/artifact chains.

## D1.1 Navigation Refresh

Why this matters: Slice57 consolidates the new-contributor path without creating governance or runtime authority.

Next action:
- Receipt: [`out/audit/docs_navigation_refresh_001.latest.json`](../out/audit/docs_navigation_refresh_001.latest.json)
- Runner: [`Scripts/run_docs_navigation_refresh_receipt.py`](../Scripts/run_docs_navigation_refresh_receipt.py)
- Registry: [`core/generated_artifact_registry.py`](../core/generated_artifact_registry.py)
- Claimed card: `D1.1 - Master INDEX.md + START_HERE.md Consolidation + Navigation System`

## Slice58 Ownership Refresh

Why this matters: the old ownership mirror was a placeholder. Slice58 replaces it with repo-observed subsystem routing derived from pipeline inventory and observed contracts.

Next action:
- Ownership matrix: [`status/SUBSYSTEM_OWNERSHIP_MATRIX.md`](status/SUBSYSTEM_OWNERSHIP_MATRIX.md)
- Receipt: [`../out/audit/subsystem_ownership_matrix_refresh_001.latest.json`](../out/audit/subsystem_ownership_matrix_refresh_001.latest.json)
- Runner: [`../Scripts/run_subsystem_ownership_matrix_refresh_receipt.py`](../Scripts/run_subsystem_ownership_matrix_refresh_receipt.py)

## Slice59 Artifact Classifier

Why this matters: D2 shifts artifact debt from broad `out/` sprawl into a receipt-backed lifecycle view that tells contributors which artifacts are active, historical, CI-regenerated, or discoverability-heavy without changing authority.

Next action:
- Classifier receipt: [`../out/audit/artifact_registry_classifier_001.latest.json`](../out/audit/artifact_registry_classifier_001.latest.json)
- Runner: [`../Scripts/run_artifact_registry_classifier_receipt.py`](../Scripts/run_artifact_registry_classifier_receipt.py)
- Artifact routes: [`artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md)

## Slice60 Continuity Lineage Refresh

Why this matters: D3 compresses the repo-native temporal continuity spine into one contributor route while keeping blocked and historical edges explicit instead of burying them across P71-P102G.

Next action:
- Lineage map: [`lineage/CONTINUITY_LINEAGE_MAP_002.md`](lineage/CONTINUITY_LINEAGE_MAP_002.md)
- Receipt: [`../out/audit/continuity_lineage_map_refresh_001.latest.json`](../out/audit/continuity_lineage_map_refresh_001.latest.json)
- Runner: [`../Scripts/run_continuity_lineage_map_refresh_receipt.py`](../Scripts/run_continuity_lineage_map_refresh_receipt.py)
- Root evidence: [`status/continuity-spine.json`](status/continuity-spine.json)

## Slice61 Subsystem Health Dashboard

Why this matters: Priority 2 starts with a repo-native health surface that compresses the ownership, artifact, continuity, migration-runner, and VIZ receipts created in the prior slices.

Next action:
- Health dashboard: [`status/SUBSYSTEM_HEALTH_DASHBOARD.md`](status/SUBSYSTEM_HEALTH_DASHBOARD.md)
- Receipt: [`../out/audit/subsystem_health_dashboard_001.latest.json`](../out/audit/subsystem_health_dashboard_001.latest.json)
- Runner: [`../Scripts/run_subsystem_health_dashboard_receipt.py`](../Scripts/run_subsystem_health_dashboard_receipt.py)
- Migration runner route surfaced inside the dashboard: [`status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md)

## Slice62 Continuity Namespace Migration Tooling Refresh

Why this matters: the continuity namespace migration stack already exists, but it was spread across several continuity namespace outputs. Slice62 packages those sources into one contributor-friendly migration route without reimplementing the stack or opening authority.

Next action:
- Status page: [`status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md`](status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md)
- Receipt: [`../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json`](../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json)
- Runner: [`../Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py`](../Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py)
- Safe next surface: `CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY`

## Slice63 Continuity Namespace Migration Runner

Why this matters: Slice63 adds the first run-layer over the continuity namespace stack, but keeps it fully advisory and receipt-first. Contributors can now understand the migration sequence, blocked authority, and rollback posture without confusing simulation with execution.

Next action:
- Runbook: [`status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md)
- Receipt: [`../out/audit/continuity_namespace_migration_run_001.latest.json`](../out/audit/continuity_namespace_migration_run_001.latest.json)
- Runner: [`../Scripts/run_continuity_namespace_migration_runner.py`](../Scripts/run_continuity_namespace_migration_runner.py)
- Safe next surface: `CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY`

Provenance: Notion Sprint 001 Hub + Loop 805 Slice60 + Hash: receipt canonical_hash
