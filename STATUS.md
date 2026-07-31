# ABRAXAS Repository Status

> **Last Updated:** 2026-07-31 (AI OS kernel audit + unification plan 002 navigation; primitives map #1050; Phase 0–14 + multi-agent loop complete; CLEAR dual-control pending)

This document provides a high-level operational status of the Abraxas v2.0 repository. It is intended to be human- and agent-readable.

## Current-state block (replace, do not append)

| Field | Value | Evidence |
|-------|--------|----------|
| HEAD / branch tip | see git; tip after **#1046** operator-loop gh/CI gatherer | `git log -1 --oneline` |
| Governance | **Governance V3 ACTIVE** · lane-based activation | `GOVERNANCE_V3.md`, `core/governance/activation_policy.py` |
| Activation | LOCAL_DEV/SANDBOX allowed · INTERNAL_CANARY conditional · EXTERNAL_PRODUCTION operator-gated | ADR-0017 |
| Production readiness | **NOT_READY** · deploy held · activation **DENIED** | `out/production_readiness/ws8/*` |
| Scripts organization | **COMPLETE** · domain `scripts/<domain>/run_*.py` | `python scripts/organize_scripts.py status` · #972–#975 |
| AAL-Viz visual pack | **COMPLETE** batches 0–4 + operator-loop 0.5 · projection-only | `design-system/aal-viz/` · #1028 · #1033 |
| Agent artifact metadata | **AgentArtifactMetadata.v1** on main | `contracts/engineering/agent_artifact_metadata.v1.schema.json` · #1029 |
| Operator loop contracts | **WorkPacket.v1 + HandoffEnvelope.v1** · projection adapter | `core/operator_loop.py` · `contracts/engineering/work_packet.v1.schema.json` · #1034 |
| Operator loop (seq 1–10) | **COMPLETE** · glyphs, skills, truth surfaces, gh/CI glance | #1033–#1046 · `scripts/viz/gather_operator_loop_github_ci_evidence.py` |
| CFAR | **Construct-first reasoning gate** on main (advisory) | `core/cfar.py` · #1030 |
| Supported interfaces | WS1 set + activation_policy + advisory_spine + `abraxas` CLI/client + `create_app` | `out/production_convergence/interface_inventory.v1.json` |
| Product CLI | `python -m abraxas` analyze/validate/replay/status/**os**/forage | `abraxas/cli.py` · project env (`jsonschema`) |
| AI OS kernel | **`ACTIVE_SHADOW`** (syscall path live; not EXTERNAL_PRODUCTION) | `python -m abraxas os status` · [`docs/architecture/AI_OS_KERNEL_AUDIT_001.md`](docs/architecture/AI_OS_KERNEL_AUDIT_001.md) |
| AI OS unification | Tracks A–D front door | [`docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md`](docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md) |

| Service factory | `apps.api.create_app` · `/analyze` `/ready` `/version` | `apps/api/main.py` |
| Classified writer | `write_canonical_artifact` · ADR-0018 enforcement API | `core/canonical/json.py` |
| Runtime settings | `core.settings.RuntimeSettings` + `RuntimeContext` ports | `core/settings.py`, `core/runtime_context.py` |
| Service hardening | request-id/headers · sanitized 500 · authn/rate-limit seams | `apps/api/middleware.py`, `apps/api/boundaries.py` |
| Provider port | `DeniedProvider` default · `FixtureProvider` + `gated_invoke` | `core/ports/provider.py` |
| OpenAPI freeze | supported surface contract | `contracts/api/openapi_supported_surface.v1.json` |
| Alembic Spine | **ADVISORY_COMPLETE_WITH_RESIDUALS** · optional golden-path specialist | `docs/alembic/ALEMBIC_SPINE.md` |
| Convergence audit | Phase 0–14 slice | `docs/architecture/PRODUCTION_CONVERGENCE_AUDIT_001.md` |
| CLEAR analysis | advisory-only · `mass_deletion_authorized: false` | `out/production_convergence/clear_reference_analysis.v1.json` |
| Issue backlog | open issues **0** · prior closed advisarily | `docs/status/ISSUE_BACKLOG_CLOSURE_001.md` |
| Phase 10 writers | viz overlay `*_replay.py` + WP-D/canary research companions | `out/production_convergence/phase10_writer_migration.v1.json` |
| Phase 11 writers | doctrine/fusion/shadow + proposal/review spine residuals | `out/production_convergence/phase11_writer_migration.v1.json` |
| Phase 12 writers | **Landed** · residual operator/spine/audit companions + CLEAR review packet | `out/production_convergence/phase12_writer_migration.v1.json` · #1035 |
| Phase 13 writers | **Landed** · artifact-contract inventory/repair/triage runners (27) | `out/production_convergence/phase13_writer_migration.v1.json` · #1037 |
| Phase 14 CLEAR/canary | **Landed** · disposition draft + canary writer import-only | `out/production_convergence/phase14_clear_disposition_and_canary_writer.v1.json` · #1039 |
| CLEAR disposition draft | engineering `DRAFT_ISSUED` · dual-control `PENDING` · no deletion | `out/production_convergence/clear_disposition_draft.v1.json` |
| CLEAR operator review | advisory · `PENDING_OPERATOR` · no deletion | `out/production_convergence/clear_operator_review.v1.json` |
| CLEAR dual-control checklist | **Operator procedure ready** · no attestations recorded | `docs/status/CLEAR_DUAL_CONTROL_OPERATOR_CHECKLIST_001.md` |
| Debug plan | **DEBUG_PLAN.v3 COMPLETE** (eng ranks 1–4) | `out/production_readiness/DEBUG_PLAN.v3.md` · #976–#980 |
| Active objective | CLEAR dual-control attestations · live providers only when authorized | `PLANS.md` · CONTINUATION_PLAN.v16 |
| AI OS primitives map | **ADVISORY PROJECTION** · deterministic symbolic OS framing | [`docs/architecture/AI_OS_PRIMITIVES_MAP_001.md`](docs/architecture/AI_OS_PRIMITIVES_MAP_001.md) · #1050 |

## Session closeout surfaces (2026-07-23)

| Surface | Status | Evidence |
|---------|--------|----------|
| Soft Facades (`core/hygiene/`) | **MERGED** · opt-in only | PRs #990–#994 |
| YGGDRASIL scan Option B (full catalog IDs) | **MERGED** | PR #993 |
| YGGDRASIL scan Option C pilot (`universal_ingest`) | **MERGED** pilot | PR #995 |
| ConflictReport.v1 builder | **MERGED** · detection only | PR #996 · `core/conflict_scan.py` |
| Oracle intake conflict population | **MERGED** · no auto-resolve | PR #997 |
| Research cross-drop dimension checks | **MERGED** · advisory | PR #998 |
| AtlasSyncReceipt.v1 schema | **ADVISORY** contract | `contracts/receipts/atlas_sync_receipt.v1.schema.json` |
| Production activation | **EXTERNAL_PRODUCTION operator-gated / HELD** | LOCAL_DEV+SANDBOX allowed under V3 |

**Doctrine (conflicts):** Detect → Classify → Operator disposition. Never auto-resolve.

**Atlas protocol:** Notion governs architecture/registered state; GitHub governs implementation/merge evidence. Master Index is navigation/ownership only. Sync receipts do not grant execution or canon authority.

## Production-candidate readiness (evidence-gated)

| Field | Value | Evidence |
|-------|--------|----------|
| Track docs | [`out/production_readiness/README.md`](out/production_readiness/README.md) | Package overview |
| Guidebook | [`docs/production_readiness/ENGINEERING_GUIDEBOOK.md`](docs/production_readiness/ENGINEERING_GUIDEBOOK.md) | Engineering guide |
| Release decision | `CANDIDATE_APPROVED` · deploy held | [`out/production_readiness/ws8/release_decision.v1.json`](out/production_readiness/ws8/release_decision.v1.json) |
| Readiness state | `CANDIDATE_HELD_FOR_OPERATOR_DEPLOY` | same |
| Production activation | **DENIED** | [`out/production_readiness/ws8/production_activation_authority_gate.v1.json`](out/production_readiness/ws8/production_activation_authority_gate.v1.json) |
| Deploy readiness | **NO_GO** | [`out/production_readiness/ws8/candidate_deploy_readiness.v1.json`](out/production_readiness/ws8/candidate_deploy_readiness.v1.json) |
| Freeze scorecard | 8/8 PASS | [`out/production_readiness/ws8/freeze_gate_scorecard.v1.json`](out/production_readiness/ws8/freeze_gate_scorecard.v1.json) |
| Baseline evidence | **Partial** (package COMPLETE) | [`out/production_readiness/baseline/baseline_receipt.v1.json`](out/production_readiness/baseline/baseline_receipt.v1.json) |
| Active plan | CONTINUATION_PLAN.v16 (draft) | [`out/production_readiness/CONTINUATION_PLAN.v16.md`](out/production_readiness/CONTINUATION_PLAN.v16.md) |
| Unauthorized sole-writer findings | **0** | [`out/production_readiness/ws1/sole_writer_advisory_report.v1.json`](out/production_readiness/ws1/sole_writer_advisory_report.v1.json) |
| Notion Verified DoD | **Scoped** (6 rows; overall NOT_READY) | [`out/production_readiness/ws8/notion_operator_verified_dod_receipt.v1.json`](out/production_readiness/ws8/notion_operator_verified_dod_receipt.v1.json) |
| Visual Operating System | tokens + system icons/runes | [`design-system/`](design-system/) · [showcase](design-system/docs/showcase.html) |
| AAL-Viz projection pack | batches **0–4 + operator-loop 0.5 COMPLETE** | [`design-system/aal-viz/`](design-system/aal-viz/) · #1027–#1028 · #1033 |
| Recent landings (2026-07-26) | **#1027–#1046 MERGED** | docs · visual pack · CFAR · operator-loop · Phase 12–14 · gh/CI glance |
| Debug plan | **DEBUG_PLAN.v3 COMPLETE** | [`out/production_readiness/DEBUG_PLAN.v3.md`](out/production_readiness/DEBUG_PLAN.v3.md) |
| RISK-008 fail-closed | **OFF** · criteria drafted | [`out/production_readiness/ws2/risk_008_fail_closed_criteria.v1.md`](out/production_readiness/ws2/risk_008_fail_closed_criteria.v1.md) |

**Do not claim production ready.** Candidate ≠ activation. Merge ≠ go-live.

## Current Development State (Governance V3)

| Area | Status | Notes |
|------|--------|-------|
| Governance model | **Governance V3 — ACTIVE** | Implementation-first development |
| Workflow | Feature → Code → Test → Commit → PR → Merge → Notion Update | See [`GOVERNANCE_V3.md`](GOVERNANCE_V3.md) |
| Preserved controls | Provenance, lineage, schema validation, testing, changelog | Mandatory for all changes |
| CI/CD | Excellent | Fast CI passes on `main` |
| Product version | **2.5.0** | PR #710–#727 merged; shadow wiring hooks (#726) + canary P132 pilot (#727) on `main` |
| Documentation | Updated | Production readiness package docs + migration receipt: [`GOVERNANCE_SIMPLIFICATION_001.md`](GOVERNANCE_SIMPLIFICATION_001.md) |
| Alembic Spine | **`ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS`** | Advisory multi-architecture orchestration under `core/alembic/`; YGGDRASIL `alembic_spine` route/pipeline + read-only Oracle bridge landed; live Alembic-native runes still deferred. Docs: [`docs/alembic/ALEMBIC_SPINE.md`](docs/alembic/ALEMBIC_SPINE.md) |

## v2.0 Hygiene Compliance (Product 2.5.0)

This repository implements the v2 hygiene foundation under `abraxas/v2/` with advisory-only posture.

- **Registers:** OBSERVED, INFERRED, SPECULATIVE output tiers on high-signal surfaces
- **Loop dynamics:** `loop_dynamics` assessment with `loop_dynamics_assessment_complete` coverage in hygiene runes
- **Hyperstitional charge:** `hyperstitional_charge` metadata with `hyperstitional_charge_evaluated` tagging via `RUNE.HYPERSTITION_TAG`
- **v2 modules registered:** Retrocausal Hygiene, Output Schema Enforcer, Self-Adversarial Loop, Hyperstition Evaluator (see `V2_MODULE_REGISTRY` in `core/pipelines/registry.py`)
- **v2 runes documented:** `RUNE.LOOP_AWARENESS`, `RUNE.HYPERSTITION_TAG`, `RUNE.PROVENANCE_ENFORCE`, `RUNE.ADVERSARIAL_AUDIT`, `RUNE.OUTPUT_REGISTER_ENFORCE` in `contracts/runes/catalog.v1.json`
- **Soft Facades:** optional observability composites under `core/hygiene/` (OutputHygieneReceipt, YggdrasilScanReceipt, CommonPipelineReceipt, ProofPair) — never required gates
- **Core Directive:** [Abraxas v2.0 Core Directive](https://www.notion.so/) linked from projection surfaces
- **Projection notes:** v2.0 compliance and freshness sync documented on STATUS and README
- **Authority:** advisory-only; no execution authority, canon mutation, or forecast routing

**Development model:**

```yaml
development_model: implementation_first
governance_mode: DEVELOPMENT_ACCELERATION
status: active
```

Routine engineering work does **not** require authorization packets, approval chains, execution eligibility gates, or operator decision artifacts before implementation.

## CI Health Summary

Fast CI (`run_fast_ci.py`) passes on `main` for filtered pytest, drift, ruff, and pyright. Full unfiltered pytest runs green after writer-test isolation (post-#706). P57 global verification hash drift and P64 manifest gate remain historical archive blockers documented below — they do not block routine development under Governance V3.

## Current Overall State

| Area                    | Status          | Last Major Change                              | Notes |
|-------------------------|-----------------|------------------------------------------------|-------|
| CI/CD Stability         | Excellent       | Reusable workflows + cleanup of all temp flags | Very clean and efficient |
| Governance              | Governance V3   | GOVERNANCE_SIMPLIFICATION_001                  | Implementation-first |
| Automation & Tooling    | Excellent       | organize_scripts.py + completions + benchmarks | Strong tooling + performance testing |
| Security Posture        | Strong          | CodeQL + Dependency Review blocking            | Proper gates |
| Documentation           | Excellent       | Governance V3 migration + 2026-07-23 STATUS refresh | See GOVERNANCE_V3.md |
| Release Process         | Excellent       | Full semantic-release with release.config.js   | Fully automated |

## Priority 2 Lane Closeout - Migration Tooling + Live Console

This summary closes the current Priority 2 cycle in advisory-only form. It is a
navigation and status projection only: no migration execution, live console
control surface, sandbox probe, runtime activation, canon mutation, MCP
exposure, or writeback authority is granted.

| Route | Status | Delivered | Next action |
|------|--------|-----------|-------------|
| Subsystem health | `SUBSYSTEM_HEALTH_DASHBOARD_READY_ADVISORY_ONLY` | Slice61 and Slice64 compress ownership, artifact lifecycle, continuity posture, and migration runner posture into one repo-native health route. | Start at [`docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md`](docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md). |
| Migration tooling | `CONTINUITY_NAMESPACE_MIGRATION_TOOLING_REFRESH_READY_ADVISORY_ONLY` | Slice62 packages the continuity namespace stack and Slice63 adds a blocked, rollback-aware migration simulation runbook. | Follow [`docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md`](docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md) then [`docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md). |
| Live console | `LIVE_CONSOLE_UI_POLISH_READY_ADVISORY_ONLY` | Slice65-Slice68 surface migration posture, combined health/migration/artifact posture, transport hardening, and UI polish in the AAL-Viz console. | Use [`apps/aal-viz-live-console/README.md`](apps/aal-viz-live-console/README.md) plus the Priority 2 receipts before reopening the lane. |
| Lane closeout | `PRIORITY2_LIVE_CONSOLE_MIGRATION_CLOSEOUT_READY_ADVISORY_ONLY` | This closeout consolidates the route so contributors can find the health, migration, and live-console surfaces without deep searching. | Verify [`out/audit/priority2_live_console_migration_closeout_001.latest.json`](out/audit/priority2_live_console_migration_closeout_001.latest.json). |

## Priority 1 Follow-On - Rune Integrity CI Visibility

This follow-on keeps CI/CD guardrails advisory-only. It documents that the rune
integrity scanner is now surfaced inside fast CI as a report-only step while
all authority locks remain closed.

| Route | Status | Delivered | Next action |
|------|--------|-----------|-------------|
| Rune scanner guardrails | `RUNE_INTEGRITY_SCANNER_GUARDRAILS_READY_ADVISORY_ONLY` | Slice56 inventories repo-real rune posture and workflow visibility findings. | Review [`out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json`](out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json). |
| CI workflow wiring | `RUNE_INTEGRITY_CI_WORKFLOW_WIRING_READY_ADVISORY_ONLY` | Slice70 adds a nonblocking, continue-on-error fast-CI step and packages the wiring as advisory provenance only. | Review [`out/audit/rune_integrity_ci_workflow_wiring_001.latest.json`](out/audit/rune_integrity_ci_workflow_wiring_001.latest.json). |

## Continuity Namespace Alias Design Follow-On

This follow-on stays inside the migration-tooling lane and keeps the additive
alias route explicit without opening any implementation authority.

| Route | Status | Delivered | Next action |
|------|--------|-----------|-------------|
| Alias implementation design | `CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN_READY_ADVISORY_ONLY` | Slice71 packages the additive alias implementation route as a design-only held surface grounded in the alias plan, migration runner, and subsystem health dashboard; Slice72 refreshes the dashboard so it now reflects that held route directly. | Review [`out/audit/continuity_namespace_alias_implementation_design_001.latest.json`](out/audit/continuity_namespace_alias_implementation_design_001.latest.json) and [`docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md`](docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md). |

## Temporal Continuity Upstream Restoration Route

This route keeps the older temporal continuity P75/P76 planning outputs visible
through the newer receipt/status/navigation spine. It does not regenerate
temporal evidence, run generators, or grant restoration authority.

See historical Priority 2 / temporal route tables in git history prior to 2026-07-23 for full Slice73–Slice85 route inventory. Authority remains false on all temporal upstream regeneration paths.

## Governance & Process

- Implementation-first development under Governance V3
- Preserved: determinism, schema validation, artifact lineage, testing, changelog
- Strong tooling ecosystem and CLI operator layer
- Fully automated semantic release process
- Atlas sync: emit `AtlasSyncReceipt.v1`-shaped Notion receipts under Master Index after material merges; STATUS.md refreshed from live evidence

## How Releases Work

Pushes to `main` following Conventional Commits will automatically:
- Analyze commits and determine next version
- Update CHANGELOG.md
- Commit the changelog back to the repository
- Create Git tag and GitHub Release

---

## Historical Governance Archive

*Archived reference — not required for routine development.*

The P70–P130 continuity chain and related operator review surfaces are preserved as project history under `out/`. They document the prior procedural governance model (FROZEN / ADVISORY_ONLY pre-implementation gates).

```yaml
P70-P130:
  status: HISTORICAL
  purpose: governance_research_archive
```

### Prior governance boundary (archived)

The repo previously maintained an advisory-only continuation state with operator hold frontiers. Historical artifacts remain at their original paths under `out/`.

### Archive technical debt (observation-only)

- P55/P56/P67/P68 narrative archive degradation persists (`GLOBAL_VERIFICATION_FAIL`)
- Missing `out/audit/temporal_coherence_chain_001.latest.json` remains a blocking upstream input for historical P77/P78 lanes
- P64 manifest gate runs with `continue-on-error` until atomic P52→P57→P64 re-seal
- Archive repair and `run_temporal_coherence_chain.py` execution were not performed under the prior governance model and remain historical observation surfaces

## How to Update This File

Update when major changes occur. Prefer pairing STATUS refresh with an Atlas Sync Receipt under the Notion Master Index.
