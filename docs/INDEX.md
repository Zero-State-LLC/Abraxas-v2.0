# Abraxas Documentation Index

Abraxas Codex v2.7 - respecting custom instructions + surfaces + governance loop + Notion mirror

Status: `D1_PRIORITY3_NAVIGATION_AND_OWNERSHIP_REFRESH_READY_ADVISORY_ONLY`
Brier Score: 0.10

This master index routes contributors by surface role. It is a navigation/projection surface only and does not create governance, canon, MCP, runtime, sandbox, or writeback authority.

## Primary Hubs

| Need | Route | Why this matters | Next action |
|------|-------|------------------|-------------|
| New contributor path | [`START_HERE.md`](START_HERE.md) | Gives the 5-minute route through the repo. | Start there before editing. |
| Repo identity/status | [`../README.md`](../README.md), [`../STATUS.md`](../STATUS.md) | Establishes current system posture. | Check current state. |
| Production readiness | [`../out/production_readiness/README.md`](../out/production_readiness/README.md), [`production_readiness/INDEX.md`](production_readiness/INDEX.md) | Candidate track: freeze gates, release decision, deploy NO_GO, activation DENIED (evidence-gated). | Read readiness README before claiming production readiness. |
| Production readiness guidebook | [`production_readiness/ENGINEERING_GUIDEBOOK.md`](production_readiness/ENGINEERING_GUIDEBOOK.md) | Engineering/governance/ops guide for the readiness package. | Use for WP semantics and authority fail-closed rules. |
| Architecture | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | Shows subsystem shape and boundaries. | Locate the subsystem. |
| Governance/instructions | [`../GOVERNANCE_V3.md`](../GOVERNANCE_V3.md), [`../AGENTS.md`](../AGENTS.md) | Defines authority locks and operator control. | Read before changing behavior. |
| Continuation plans | [`../PLANS.md`](../PLANS.md) | Lists active lanes and receipts. | Confirm current frontier. |
| Task mirror | [Notion Sprint 001 Hub](https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254) | Living board/source mirror. | Use for alignment; no autonomous writeback. |
| Subsystem routing | [`status/SUBSYSTEM_OWNERSHIP_MATRIX.md`](status/SUBSYSTEM_OWNERSHIP_MATRIX.md) | Repo-native ownership routes | Clarifies which observed pipelines anchor each subsystem. | Check here before reassigning or extending subsystem surfaces. |
| Subsystem health | [`status/SUBSYSTEM_HEALTH_DASHBOARD.md`](status/SUBSYSTEM_HEALTH_DASHBOARD.md) | Repo-native health projection | Aggregates ownership, artifact lifecycle, continuity, migration-runner, and VIZ posture into one phase-2 health surface. | Use this before selecting a health, migration, or UI follow-on lane. |
| Migration tooling | [`status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md`](status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md) | Migration/status projection | Packages the existing continuity namespace tooling stack into one contributor-facing route. | Use this after the health dashboard flags continuity migration follow-up. |
| Migration runner | [`status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md) | Migration simulation / runbook | Adds the first receipt-driven run-layer over the continuity namespace stack without opening execution authority. | Use this to understand staged migration scaffolding and blocked authority. |
| Migration preflight | [`../out/audit/continuity_namespace_migration_preflight_001.latest.json`](../out/audit/continuity_namespace_migration_preflight_001.latest.json) | Migration safety preflight | Checks migration runner, alias design, health dashboard, and closeout receipts before future consumers rely on them. | Use this before scoping migration-runner UI or additive design follow-ons. |
| Live console migration preflight projection | [`../out/audit/live_console_migration_preflight_projection_001.latest.json`](../out/audit/live_console_migration_preflight_projection_001.latest.json) | Display-only live console projection | Exposes migration preflight pass/held checks and blocked authority in the AAL-Viz bundle. | Use this before live-console follow-ons that depend on migration preflight posture. |

## Surface Role Routes

| Surface role | Current route | Why this matters | Next action |
|--------------|---------------|------------------|-------------|
| Identity/status | [`../README.md`](../README.md), [`../STATUS.md`](../STATUS.md) | Defines what the repo is and how healthy it is. | Use for orientation. |
| Governance | [`../GOVERNANCE_V3.md`](../GOVERNANCE_V3.md), [`../AGENTS.md`](../AGENTS.md) | Authority, locks, and operator rules. | Treat as protected. |
| Architecture | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | System shape and technical maps. | Follow existing subsystem boundaries. |
| Code/module maps | [`../core/`](../core/), [`../scripts/`](../scripts/), [`../scripts/`](../scripts/) | Engineering surfaces and runners. | Prefer no-arg receipt runners for generated artifacts. |
| Generated artifacts | [`artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md), [`../core/generated_artifact_registry.py`](../core/generated_artifact_registry.py) | Artifact lifecycle and regeneration policy. | Verify canonical generator before editing outputs. |
| Audit history | [`audits/AUDIT_INDEX.md`](audits/AUDIT_INDEX.md) | Current and historical evidence. | Classify rather than delete. |
| Releases | [`releases/RELEASE_INDEX.md`](releases/RELEASE_INDEX.md) | Continuation/release baseline. | Start from the active baseline. |
| Runtime docs | [`runtime/`](runtime/) | Planning and readiness surfaces. | Keep execution authority separate. |
| Oracle docs | [`oracle/`](oracle/) | Oracle planning/intake surfaces. | Keep live gates explicit. |
| Visualization docs | [`visualization/`](visualization/) | VIZ and projection surfaces. | Keep UI projection read-only unless gated. |

## Active Receipt Routes

| Receipt | Runner | Status |
|---------|--------|--------|
| [`../out/audit/docs_navigation_refresh_001.latest.json`](../out/audit/docs_navigation_refresh_001.latest.json) | [`../scripts/run_docs_navigation_refresh_receipt.py`](../scripts/run_docs_navigation_refresh_receipt.py) | `DOCS_NAVIGATION_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/subsystem_ownership_matrix_refresh_001.latest.json`](../out/audit/subsystem_ownership_matrix_refresh_001.latest.json) | [`../scripts/run_subsystem_ownership_matrix_refresh_receipt.py`](../scripts/run_subsystem_ownership_matrix_refresh_receipt.py) | `SUBSYSTEM_OWNERSHIP_MATRIX_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/artifact_registry_classifier_001.latest.json`](../out/audit/artifact_registry_classifier_001.latest.json) | [`../scripts/artifact/run_artifact_registry_classifier_receipt.py`](../scripts/artifact/run_artifact_registry_classifier_receipt.py) | `ARTIFACT_REGISTRY_CLASSIFIER_READY_ADVISORY_ONLY` |
| [`../out/audit/canon_code_binding_audit_001.latest.json`](../out/audit/canon_code_binding_audit_001.latest.json) | [`../scripts/run_canon_code_binding_audit_receipt.py`](../scripts/run_canon_code_binding_audit_receipt.py) | `CANON_CODE_BINDING_AUDIT_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_restoration_route_refresh_001.latest.json`](../out/audit/temporal_upstream_restoration_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_restoration_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_restoration_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_RESTORATION_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_dry_run_route_refresh_001.latest.json`](../out/audit/temporal_upstream_dry_run_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_dry_run_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_dry_run_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_DRY_RUN_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_execution_route_refresh_001.latest.json`](../out/audit/temporal_upstream_execution_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_execution_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_execution_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_EXECUTION_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_authorization_gate_route_refresh_001.latest.json`](../out/audit/temporal_upstream_authorization_gate_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_authorization_gate_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_authorization_gate_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_AUTHORIZATION_GATE_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json`](../out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_authorization_record_regeneration_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_authorization_record_regeneration_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_AUTHORIZATION_RECORD_REGENERATION_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json`](../out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_status_repair_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_status_repair_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_STATUS_REPAIR_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_regeneration_plan_route_refresh_001.latest.json`](../out/audit/temporal_upstream_regeneration_plan_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_regeneration_plan_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_regeneration_plan_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_REGENERATION_PLAN_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_regeneration_execution_route_refresh_001.latest.json`](../out/audit/temporal_upstream_regeneration_execution_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_regeneration_execution_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_regeneration_execution_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_REGENERATION_EXECUTION_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json`](../out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_regeneration_plan_regeneration_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_regeneration_plan_regeneration_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json`](../out/audit/temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_status_plan_regeneration_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_status_plan_regeneration_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_STATUS_PLAN_REGENERATION_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json`](../out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json`](../out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_BRIDGE_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/temporal_upstream_p83_regeneration_authorization_gate_route_refresh_001.latest.json`](../out/audit/temporal_upstream_p83_regeneration_authorization_gate_route_refresh_001.latest.json) | [`../scripts/temporal/run_temporal_upstream_p83_regeneration_authorization_gate_route_refresh_receipt.py`](../scripts/temporal/run_temporal_upstream_p83_regeneration_authorization_gate_route_refresh_receipt.py) | `TEMPORAL_UPSTREAM_P83_REGENERATION_AUTHORIZATION_GATE_ROUTE_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/subsystem_health_dashboard_001.latest.json`](../out/audit/subsystem_health_dashboard_001.latest.json) | [`../scripts/run_subsystem_health_dashboard_receipt.py`](../scripts/run_subsystem_health_dashboard_receipt.py) | `SUBSYSTEM_HEALTH_DASHBOARD_READY_ADVISORY_ONLY` |
| [`../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json`](../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json) | [`../scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py`](../scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py) | `CONTINUITY_NAMESPACE_MIGRATION_TOOLING_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/continuity_namespace_migration_run_001.latest.json`](../out/audit/continuity_namespace_migration_run_001.latest.json) | [`../scripts/run_continuity_namespace_migration_runner.py`](../scripts/run_continuity_namespace_migration_runner.py) | `CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY` |
| [`../out/audit/continuity_namespace_migration_preflight_001.latest.json`](../out/audit/continuity_namespace_migration_preflight_001.latest.json) | [`../scripts/run_continuity_namespace_migration_preflight_receipt.py`](../scripts/run_continuity_namespace_migration_preflight_receipt.py) | `CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_READY_ADVISORY_ONLY` |
| [`../out/audit/live_console_migration_preflight_projection_001.latest.json`](../out/audit/live_console_migration_preflight_projection_001.latest.json) | [`../scripts/run_live_console_migration_preflight_projection_receipt.py`](../scripts/run_live_console_migration_preflight_projection_receipt.py) | `LIVE_CONSOLE_MIGRATION_PREFLIGHT_PROJECTION_READY_ADVISORY_ONLY` |
| [`../out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json`](../out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json) | [`../scripts/run_rune_integrity_scanner_guardrails_receipt.py`](../scripts/run_rune_integrity_scanner_guardrails_receipt.py) | Advisory scanner/guardrails |
| [`../out/audit/hyperstition_evaluator_deepening_receipt_001.latest.json`](../out/audit/hyperstition_evaluator_deepening_receipt_001.latest.json) | [`../scripts/run_hyperstition_evaluator_deepening_receipt.py`](../scripts/run_hyperstition_evaluator_deepening_receipt.py) | Advisory evaluator projection |
| [`../out/audit/viz01_live_feed_enhancement_receipt_001.latest.json`](../out/audit/viz01_live_feed_enhancement_receipt_001.latest.json) | Registered no-arg runner | VIZ-01 read-only projection feed |

## Deep History Routes

Why this matters: historical chains are evidence, not clutter. Keep them discoverable without making new contributors parse every old receipt first.

Next action:
- Audit history: [`audits/AUDIT_INDEX.md`](audits/AUDIT_INDEX.md)
- Release/continuation history: [`releases/RELEASE_INDEX.md`](releases/RELEASE_INDEX.md)
- Generated artifact lifecycle: [`artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md)
- Full artifact registry: [`../core/generated_artifact_registry.py`](../core/generated_artifact_registry.py)

## D1.1 Refresh Status

Why this matters: Slice57 implements the Priority 3 documentation-debt route from the Notion board without opening any execution gate.

Next action:
- Verify `python scripts/run_docs_navigation_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/docs_navigation_refresh_001.latest.json`
- Keep `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` unissued unless the operator explicitly provides it in a future gate.

## Slice58 Ownership Refresh

Why this matters: Priority 3 now includes a real ownership route instead of a partial mirror note, which makes architecture and contract navigation materially faster for new contributors.

Next action:
- Verify `python scripts/run_subsystem_ownership_matrix_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/subsystem_ownership_matrix_refresh_001.latest.json`
- Use [`status/SUBSYSTEM_OWNERSHIP_MATRIX.md`](status/SUBSYSTEM_OWNERSHIP_MATRIX.md) before changing subsystem boundaries or module routing assumptions.

## Slice59 Artifact Classifier

Why this matters: D2 adds a deterministic artifact lifecycle/discoverability receipt so contributors can see managed vs orphaned vs historical-heavy groups without treating `docs/artifacts/ARTIFACT_INDEX.md` as the source of truth.

Next action:
- Verify `python scripts/artifact/run_artifact_registry_classifier_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/artifact_registry_classifier_001.latest.json`
- Use [`artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md) for navigation and [`../core/generated_artifact_registry.py`](../core/generated_artifact_registry.py) as canonical registry truth.

## Canon-To-Code Binding Audit

Why this matters: `WO-ABX-CANON-CODE-BINDING-v1` creates a proof-bearing baseline from canonical source to repo module, validator, proof artifact, freshness marker, authority status, and operator surface.

Next action:
- Verify `python scripts/run_canon_code_binding_audit_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/canon_code_binding_audit_001.latest.json`
- Keep the route advisory-only; it does not grant canon mutation, runtime activation, queue/scheduler mutation, external calls, or writeback authority.

## Slice60 Continuity Lineage Refresh

Why this matters: D3 turns the repo-native temporal continuity spine into a compact route for contributors, preserving historical context while making blocked and missing-chain edges easy to find.

Next action:
- Verify `python scripts/run_continuity_lineage_map_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/continuity_lineage_map_refresh_001.latest.json`
- Use [`lineage/CONTINUITY_LINEAGE_MAP_002.md`](lineage/CONTINUITY_LINEAGE_MAP_002.md) for continuity routing and [`status/continuity-spine.json`](status/continuity-spine.json) as the source spine surface.

## Slice73 Temporal Upstream Restoration Route

Why this matters: Slice73 takes the rehydrated P75/P76 planning outputs and packages them into one current contributor route. It makes the move from missing-evidence restoration to upstream dry-run planning explicit without adding any generator execution or repair authority.

Next action:
- Verify `python scripts/temporal/run_temporal_upstream_restoration_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_restoration_route_refresh_001.latest.json`
- Use [`status/TEMPORAL_CONTINUITY_UPSTREAM_RESTORATION_ROUTE.md`](status/TEMPORAL_CONTINUITY_UPSTREAM_RESTORATION_ROUTE.md) before proposing any P77 dry-run follow-on.

## Slice74 Temporal Upstream Dry-Run Route

Why this matters: Slice74 keeps the emitted P77 dry-run packet on the current navigation spine so contributors can see the real dry-run posture and route safely into P78 planning without treating raw outputs as hidden implementation detail.

Next action:
- Verify `python scripts/temporal/run_temporal_upstream_dry_run_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_dry_run_route_refresh_001.latest.json`
- Use [`status/TEMPORAL_CONTINUITY_UPSTREAM_DRY_RUN_ROUTE.md`](status/TEMPORAL_CONTINUITY_UPSTREAM_DRY_RUN_ROUTE.md) before proposing any P78 execution-plan follow-on.

## Slice75 Temporal Upstream Execution Route

Why this matters: Slice75 keeps the emitted P78 execution-planning packet on the current navigation spine so contributors can see the real execution-planning posture and route safely into P79 authorization-gate planning without treating raw outputs as hidden implementation detail.

Next action:
- Verify `python scripts/temporal/run_temporal_upstream_execution_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_execution_route_refresh_001.latest.json`
- Use [`status/TEMPORAL_CONTINUITY_UPSTREAM_EXECUTION_ROUTE.md`](status/TEMPORAL_CONTINUITY_UPSTREAM_EXECUTION_ROUTE.md) before proposing any P79 authorization-gate follow-on.

## Slice76 Temporal Upstream Authorization-Gate Route

Why this matters: Slice76 keeps the emitted P79 authorization-gate packet on the current navigation spine so contributors can see the real authorization-review posture and route safely into P80 authorization-record planning without treating raw outputs as hidden implementation detail.

Next action:
- Verify `python scripts/temporal/run_temporal_upstream_authorization_gate_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_authorization_gate_route_refresh_001.latest.json`
- Use [`status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_GATE_ROUTE.md`](status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_GATE_ROUTE.md) before proposing any P80 authorization-record-planning follow-on.

## Slice77 Temporal Upstream Authorization-Record Regeneration Route

Why this matters: Slice77 keeps the blocked P80 follow-on on the current navigation spine by packaging the existing Slice50/Slice51 missing-source and regeneration evidence into one explicit contributor route, so the handoff to P83 remains visible and fail-closed.

Next action:
- Verify `python scripts/temporal/run_temporal_upstream_authorization_record_regeneration_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json`
- Use [`status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_RECORD_REGENERATION_ROUTE.md`](status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_RECORD_REGENERATION_ROUTE.md) before proposing any deeper P80 regeneration or P83 status-repair follow-on.

## Slice78 Temporal Upstream Status-Repair Route

Why this matters: Slice78 keeps the emitted P83 status-repair packet on the current navigation spine so contributors can see the actual emitted status-repair posture and route safely back into downstream P80 regeneration planning without treating raw outputs as hidden implementation detail.

Next action:
- Verify `python scripts/temporal/run_temporal_upstream_status_repair_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json`
- Use [`status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_REPAIR_ROUTE.md`](status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_REPAIR_ROUTE.md) before proposing any deeper P80 regeneration or P84 follow-on.

## Slice79 Temporal Upstream Regeneration-Plan Route

Why this matters: Slice79 keeps the emitted P84 regeneration-plan packet on the current navigation spine so contributors can see the actual `P80_REGENERATION_PLAN_READY` posture and route safely into the downstream P85 execution-planning handoff without treating raw outputs as hidden implementation detail.

Next action:
- Verify `python scripts/temporal/run_temporal_upstream_regeneration_plan_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_regeneration_plan_route_refresh_001.latest.json`
- Use [`status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_ROUTE.md`](status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_ROUTE.md) before proposing any deeper P85 execution-planning packaging or regeneration follow-on.

## Slice80 Temporal Upstream Regeneration-Execution Route

Why this matters: Slice80 keeps the emitted P85 regeneration execution-planning packet on the same navigation spine, so contributors can see the blocked-yet-observed execution posture and route safely into the downstream P86 regeneration-planning follow-on.

Next action:
- Verify `python scripts/temporal/run_temporal_upstream_regeneration_execution_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_regeneration_execution_route_refresh_001.latest.json`
- Use [`status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_EXECUTION_ROUTE.md`](status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_EXECUTION_ROUTE.md) before proposing any deeper P86 regeneration-planning follow-on.

## Slice81 Temporal Upstream Regeneration-Plan-Regeneration Route

Why this matters: Slice81 keeps the refreshed emitted P86 regeneration-plan-regeneration packet on the navigation spine, so contributors can see the current `P84_REGENERATION_NOT_REQUIRED` posture and preserve the explicit downstream P87 handoff without treating stale missing-source evidence as current truth.

Next action:
- Verify `python scripts/temporal/run_temporal_upstream_regeneration_plan_regeneration_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json`
- Verify `python scripts/temporal/run_temporal_upstream_status_plan_regeneration_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json`
- Verify `python scripts/temporal/run_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json`
- Verify `python scripts/temporal/run_temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json`
- Verify `python scripts/temporal/run_temporal_upstream_p83_regeneration_authorization_gate_route_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_p83_regeneration_authorization_gate_route_refresh_001.latest.json`
- Use [`status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE.md`](status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE.md) before proposing any separate downstream P87 packaging follow-on.

## Slice61 Subsystem Health Dashboard

Why this matters: Priority 2 starts with a deterministic dashboard packet that compresses the key Priority 3 routes into one health and discoverability surface. Slice64 extends it so the continuity namespace migration run-layer is visible in the same dashboard, and Slice72 keeps that route current by surfacing the merged alias implementation design posture as the current held follow-on.

Next action:
- Verify `python scripts/run_subsystem_health_dashboard_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/subsystem_health_dashboard_001.latest.json`
- Use [`status/SUBSYSTEM_HEALTH_DASHBOARD.md`](status/SUBSYSTEM_HEALTH_DASHBOARD.md) before choosing between migration tooling and Live Console follow-ons.
- Review the surfaced migration runner and alias-design posture before proposing any future stabilization or dashboard/UI consumption work.

## Slice62 Continuity Namespace Migration Tooling Refresh

Why this matters: Slice61 identified migration tooling as the strongest next Priority 2 route. Slice62 packages the existing continuity namespace stack into one deterministic status and receipt pair so contributors can understand current migration posture without reopening or rewriting the original continuity namespace artifacts.

Next action:
- Verify `python scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json`
- Use [`status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md`](status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md) before scoping any future additive alias implementation design work.

## Slice63 Continuity Namespace Migration Runner

Why this matters: Slice63 turns the continuity namespace package into a contributor-friendly run-layer with staged scaffolding, blocked execution posture, and explicit rollback/no-op routing.

Next action:
- Verify `python scripts/run_continuity_namespace_migration_runner.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/continuity_namespace_migration_run_001.latest.json`
- Use [`status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md) before scoping any future additive alias implementation design or UI consumption slice.

## Slice71 Continuity Namespace Alias Implementation Design

Why this matters: Slice71 makes the future additive alias implementation route explicit and reviewable without granting any implementation authority. It packages the held design posture that was previously implied by upstream migration receipts.

Next action:
- Verify `python scripts/run_continuity_namespace_alias_implementation_design_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/continuity_namespace_alias_implementation_design_001.latest.json`
- Review [`status/CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md`](status/CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md) before proposing alias materialization, path renames, or historical receipt rebinding work.

## Slice72 Dashboard Alias Design Alignment

Why this matters: Slice72 updates the canonical subsystem health dashboard route so it reflects Slice71 as merged held design truth instead of leaving the dashboard pointed at Slice71 as if it were still the next unimplemented card.

Next action:
- Verify `python scripts/run_subsystem_health_dashboard_receipt.py`
- Review [`status/SUBSYSTEM_HEALTH_DASHBOARD.md`](status/SUBSYSTEM_HEALTH_DASHBOARD.md)
- Treat `Hold continuity namespace alias lane at design-only posture` as the current repo-native route until a future stabilization receipt changes that posture.

## Slice65 Live Console Migration Runner Posture

Why this matters: Slice65 makes the continuity namespace migration posture observable inside the AAL-Viz live console by projecting the existing dashboard-backed migration summary into the live bundle rather than creating a second migration authority surface.

Next action:
- Verify `python scripts/build_aal_viz_projection_bundle.py`
- Verify `python scripts/run_live_console_migration_runner_posture_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/live_console_migration_runner_posture_001.latest.json`
- Use the live console projection bundle and receipt before proposing deeper health-plus-migration or websocket-hardening work.

## Slice66 Combined Live Projection Posture

Why this matters: Slice66 adds a dedicated live-console panel that combines subsystem health, continuity namespace migration, and artifact lifecycle posture into one receipt-driven observational surface while leaving all authority locks closed.

Next action:
- Live receipt: [`../out/audit/live_projection_health_migration_artifact_001.latest.json`](../out/audit/live_projection_health_migration_artifact_001.latest.json)
- Receipt runner: [`../scripts/run_live_projection_health_migration_artifact_receipt.py`](../scripts/run_live_projection_health_migration_artifact_receipt.py)
- Projection bundle source: [`../apps/aal-viz-live-console/public/projection-bundle.json`](../apps/aal-viz-live-console/public/projection-bundle.json)
- Use the combined panel before proposing deeper live-console synthesis or websocket-hardening work.

## Slice67 Live Feed Transport Hardening

Why this matters: Slice67 makes the live feed more trustworthy by adding deterministic reconnect scheduling, explicit fallback reasons, and fail-closed transport diagnostics while keeping the projection path read-only.

Next action:
- Transport receipt: [`../out/audit/live_console_websocket_hardening_001.latest.json`](../out/audit/live_console_websocket_hardening_001.latest.json)
- Receipt runner: [`../scripts/run_live_console_websocket_hardening_receipt.py`](../scripts/run_live_console_websocket_hardening_receipt.py)

## Slice68 Live Console UI Polish

Why this matters: Slice68 keeps the live-console lane low-risk by standardizing posture badges, advisory notes, and fail-closed/read-only cues without changing transport logic or receipt sourcing.

Next action:
- UI polish receipt: [`../out/audit/live_console_ui_polish_001.latest.json`](../out/audit/live_console_ui_polish_001.latest.json)
- Receipt runner: [`../scripts/run_live_console_ui_polish_receipt.py`](../scripts/run_live_console_ui_polish_receipt.py)
- Feed transport source: [`../apps/aal-viz-live-console/src/data/liveProjectionFeed.ts`](../apps/aal-viz-live-console/src/data/liveProjectionFeed.ts)
- Use the transport posture route before proposing backend feed changes or new execution surfaces.

## Slice69 Priority 2 Lane Closeout

Why this matters: Slice69 is the lightweight closeout for the current Priority 2 cycle. It keeps migration tooling and live-console work discoverable through one compact route rather than asking contributors to reconstruct Slice61-Slice68 from scattered receipts.

Next action:
- Closeout receipt: [`../out/audit/priority2_live_console_migration_closeout_001.latest.json`](../out/audit/priority2_live_console_migration_closeout_001.latest.json)
- Receipt runner: [`../scripts/run_priority2_live_console_migration_closeout_receipt.py`](../scripts/run_priority2_live_console_migration_closeout_receipt.py)
- Canonical entry route: [`status/SUBSYSTEM_HEALTH_DASHBOARD.md`](status/SUBSYSTEM_HEALTH_DASHBOARD.md) -> [`status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md`](status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md) -> [`status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md) -> [`../apps/aal-viz-live-console/README.md`](../apps/aal-viz-live-console/README.md)

## Slice70 Rune Integrity CI Visibility

Why this matters: Slice70 turns the earlier rune-integrity scanner discovery work into a repo-visible CI route without changing the advisory boundary. Contributors can now find both the report-only workflow hook and the receipt that proves it is nonblocking.

Next action:
- Wiring receipt: [`../out/audit/rune_integrity_ci_workflow_wiring_001.latest.json`](../out/audit/rune_integrity_ci_workflow_wiring_001.latest.json)
- Receipt runner: [`../scripts/run_rune_integrity_ci_workflow_wiring_receipt.py`](../scripts/run_rune_integrity_ci_workflow_wiring_receipt.py)
- Fast CI workflow: [`../.github/workflows/ci.yml`](../.github/workflows/ci.yml)
- Scanner baseline receipt: [`../out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json`](../out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json)

Provenance: Notion Sprint 001 Hub + Loop 805 Slice60 + Hash: receipt canonical_hash
