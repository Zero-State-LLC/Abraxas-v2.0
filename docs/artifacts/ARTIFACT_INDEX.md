# Artifact Index

## Current Artifact Routes

| Route | Purpose | Next action |
|-------|---------|-------------|
| [`../../core/generated_artifact_registry.py`](../../core/generated_artifact_registry.py) | Canonical generated artifact registry | Check whether an artifact has a no-arg generator. |
| [`../../out/audit/docs_navigation_refresh_001.latest.json`](../../out/audit/docs_navigation_refresh_001.latest.json) | Slice57 D1.1 navigation refresh receipt | Verify docs navigation provenance. |
| [`../../out/audit/artifact_registry_classifier_001.latest.json`](../../out/audit/artifact_registry_classifier_001.latest.json) | Slice59 artifact lifecycle/discoverability classifier receipt | Review managed vs orphaned vs historical-heavy groups before touching `out/`. |
| [`../../out/audit/continuity_lineage_map_refresh_001.latest.json`](../../out/audit/continuity_lineage_map_refresh_001.latest.json) | Slice60 continuity lineage refresh receipt | Review active, blocked, and historical temporal continuity routes before navigating P71-P102G. |
| [`../../out/audit/subsystem_health_dashboard_001.latest.json`](../../out/audit/subsystem_health_dashboard_001.latest.json) | Slice61/Slice64 subsystem health dashboard receipt | Review ownership, artifact lifecycle, continuity, migration-runner, and VIZ posture before choosing a Phase 2 follow-on lane. |
| [`../../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json`](../../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json) | Slice62 continuity namespace migration tooling packaging receipt | Review the existing continuity namespace audit/plan/readiness/alias stack through one migration-tooling route. |
| [`../../out/audit/continuity_namespace_migration_run_001.latest.json`](../../out/audit/continuity_namespace_migration_run_001.latest.json) | Slice63 continuity namespace migration run receipt | Review staged advisory migration scaffolding, blocked authority, and rollback posture. |
| [`../../out/audit/live_console_migration_runner_posture_001.latest.json`](../../out/audit/live_console_migration_runner_posture_001.latest.json) | Slice65 live console migration runner posture receipt | Confirm the live console is projecting the dashboard-backed migration posture without introducing execution authority. |
| [`../../out/audit/live_projection_health_migration_artifact_001.latest.json`](../../out/audit/live_projection_health_migration_artifact_001.latest.json) | Slice66 combined live projection posture receipt | Review one live-console surface that summarizes subsystem health, migration posture, and artifact lifecycle findings. |
| [`../../out/audit/live_console_websocket_hardening_001.latest.json`](../../out/audit/live_console_websocket_hardening_001.latest.json) | Slice67 live-feed transport hardening receipt | Review deterministic reconnect, polling fallback, and fail-closed transport posture for the live console. |
| [`../../out/audit/live_console_ui_polish_001.latest.json`](../../out/audit/live_console_ui_polish_001.latest.json) | Slice68 live-console UI polish receipt | Review the small presentational consistency pass for posture badges, advisory notes, and feed diagnostics. |
| [`../../Scripts/run_artifact_registry_classifier_receipt.py`](../../Scripts/run_artifact_registry_classifier_receipt.py) | No-arg classifier runner | Regenerate the artifact lifecycle classifier receipt. |
| [`../../Scripts/run_continuity_lineage_map_refresh_receipt.py`](../../Scripts/run_continuity_lineage_map_refresh_receipt.py) | No-arg continuity lineage runner | Regenerate the D3 continuity routing receipt. |
| [`../../Scripts/run_subsystem_health_dashboard_receipt.py`](../../Scripts/run_subsystem_health_dashboard_receipt.py) | No-arg subsystem health runner | Regenerate the Priority 2 subsystem health dashboard receipt. |
| [`../../Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py`](../../Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py) | No-arg continuity namespace migration runner | Regenerate the Slice62 migration-tooling packaging receipt. |
| [`../../Scripts/run_continuity_namespace_migration_runner.py`](../../Scripts/run_continuity_namespace_migration_runner.py) | No-arg continuity namespace migration simulation runner | Regenerate the Slice63 advisory migration run receipt. |
| [`../../Scripts/run_live_console_migration_runner_posture_receipt.py`](../../Scripts/run_live_console_migration_runner_posture_receipt.py) | No-arg live console migration posture runner | Regenerate the Slice65 live-console visibility receipt. |
| [`../../Scripts/run_live_projection_health_migration_artifact_receipt.py`](../../Scripts/run_live_projection_health_migration_artifact_receipt.py) | No-arg combined live posture runner | Regenerate the Slice66 combined live-console posture receipt. |
| [`../../Scripts/run_live_console_websocket_hardening_receipt.py`](../../Scripts/run_live_console_websocket_hardening_receipt.py) | No-arg live-feed transport hardening runner | Regenerate the Slice67 transport-hardening receipt. |
| [`../../Scripts/run_live_console_ui_polish_receipt.py`](../../Scripts/run_live_console_ui_polish_receipt.py) | No-arg live-console UI polish runner | Regenerate the Slice68 UI polish receipt. |

Artifact lifecycle route: identify the receipt, confirm its registry entry, run the no-arg generator when present, then compare canonical hashes before committing.

Classification of generated artifacts under [`out/`](../../out/). **Do not delete artifacts.** Policy source: [`core/generated_artifact_registry.py`](../../core/generated_artifact_registry.py) (`GENERATED_ARTIFACT_POLICY_V1`).

## Classification legend

| Class | Meaning |
|-------|---------|
| **ACTIVE** | Current continuity, audit, or operator-sync surfaces |
| **REFERENCE** | Historical chain evidence; read-only; may be large |
| **ARCHIVED** | Explicit archive/seal; geometric/chamfer v0.1 arc |

## Critical ACTIVE entrypoints (new contributors)

| Artifact | Runner | Purpose |
|----------|--------|---------|
| `out/canon_resume_state/latest.json` | `run_canon_resume_state.py` | Continuity pointer before new work |
| `out/audit/continuation_frontier_reconciliation_001.latest.json` | `run_continuation_frontier_reconciliation.py` | Frontier classification |
| `out/audit/abx_codegen_shadow_replay_harness_operator_attestation_intake_gate_001.latest.json` | `run_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate.py` | Intake VALIDATED |
| `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_review_001.latest.json` | `run_abx_codegen_shadow_replay_harness_operator_decision_record_review.py` | ODR INTAKE_CLEARED_OBSERVED |
| `out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json` | `run_notion_p131_p133_stale_spec_reconciliation_packet.py` | Manual Notion sync packet |
| `out/research_canary_advisory_shadow_activation_record/latest.json` | `run_research_canary_advisory_shadow_activation_record.py` | 6/6 advisory shadow |
| `out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json` | `run_operator_review_required_items_bulk_disposition.py` | Bulk disposition |

## Registry policy buckets

| Bucket | Examples | Notes |
|--------|----------|-------|
| CI regenerated | `out/projections/projection_bus_001.latest.json` | Regenerated in CI |
| Audit volatile | `out/audit/artifact_regeneration_001.latest.json` | Drift-check surfaces |
| Runtime volatile | `out/validation/latest.json`, `out/projections/aal_viz.latest.json` | Environment-dependent |
| Derived optional | `out/projections/temporal_persistence_memory_001.latest.json` | Optional derived |
| Explicit producers | ~638 paths in registry | Maps artifact -> `scripts/run_*.py` |

## Slice59 classifier route

Why this matters: the artifact index is a navigation surface, not the source of truth. Slice59 adds a deterministic receipt that classifies registry entries by lifecycle bucket, discoverability posture, and no-arg regeneration suitability without changing enforcement.

Next action:
- Receipt: [`../../out/audit/artifact_registry_classifier_001.latest.json`](../../out/audit/artifact_registry_classifier_001.latest.json)
- Runner: [`../../Scripts/run_artifact_registry_classifier_receipt.py`](../../Scripts/run_artifact_registry_classifier_receipt.py)
- Canonical truth: [`../../core/generated_artifact_registry.py`](../../core/generated_artifact_registry.py)

## Slice60 continuity route

Why this matters: continuity lineage is another artifact-discoverability problem. Slice60 adds a deterministic receipt that compresses the current temporal spine into active, blocked, and historical route groups without mutating any temporal evidence.

Next action:
- Receipt: [`../../out/audit/continuity_lineage_map_refresh_001.latest.json`](../../out/audit/continuity_lineage_map_refresh_001.latest.json)
- Runner: [`../../Scripts/run_continuity_lineage_map_refresh_receipt.py`](../../Scripts/run_continuity_lineage_map_refresh_receipt.py)
- Navigation map: [`../lineage/CONTINUITY_LINEAGE_MAP_002.md`](../lineage/CONTINUITY_LINEAGE_MAP_002.md)

## Slice62 continuity namespace migration route

Why this matters: migration tooling is now a distinct artifact-discoverability and contributor-routing problem. Slice62 packages the existing continuity namespace stack into one status/receipt pair without changing any continuity namespace schemas, IDs, or output paths.

Next action:
- Receipt: [`../../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json`](../../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json)
- Runner: [`../../Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py`](../../Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py)
- Status page: [`../status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md`](../status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md)

## Slice63 continuity namespace migration run route

Why this matters: Slice63 adds the first receipt-driven run-layer over the continuity namespace stack. Slice64 then surfaces that posture inside the subsystem health dashboard, so contributors can see migration readiness and blocked authority without leaving the main Phase 2 health route.

Next action:
- Receipt: [`../../out/audit/continuity_namespace_migration_run_001.latest.json`](../../out/audit/continuity_namespace_migration_run_001.latest.json)
- Runner: [`../../Scripts/run_continuity_namespace_migration_runner.py`](../../Scripts/run_continuity_namespace_migration_runner.py)
- Runbook: [`../status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](../status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md)

## Slice65 live console migration visibility route

Why this matters: Slice65 carries the same migration posture into the AAL-Viz live console bundle, so contributors can observe the dashboard-backed migration state directly in the live view without creating a second source of truth.

Next action:
- Receipt: [`../../out/audit/live_console_migration_runner_posture_001.latest.json`](../../out/audit/live_console_migration_runner_posture_001.latest.json)
- Runner: [`../../Scripts/run_live_console_migration_runner_posture_receipt.py`](../../Scripts/run_live_console_migration_runner_posture_receipt.py)
- Bundle: [`../../apps/aal-viz-live-console/public/projection-bundle.json`](../../apps/aal-viz-live-console/public/projection-bundle.json)

## Slice66 combined live posture route

Why this matters: Slice66 compresses subsystem health, migration-runner, and artifact lifecycle evidence into one live-console panel so operators can review high-signal posture without hopping across multiple receipts.

Next action:
- Receipt: [`../../out/audit/live_projection_health_migration_artifact_001.latest.json`](../../out/audit/live_projection_health_migration_artifact_001.latest.json)
- Runner: [`../../Scripts/run_live_projection_health_migration_artifact_receipt.py`](../../Scripts/run_live_projection_health_migration_artifact_receipt.py)
- Bundle: [`../../apps/aal-viz-live-console/public/projection-bundle.json`](../../apps/aal-viz-live-console/public/projection-bundle.json)

## Slice67 live-feed transport hardening route

Why this matters: Slice67 keeps the live console operationally honest by exposing reconnect delay, fallback reason, and last transport error without opening backend or execution paths.

Next action:
- Receipt: [`../../out/audit/live_console_websocket_hardening_001.latest.json`](../../out/audit/live_console_websocket_hardening_001.latest.json)
- Runner: [`../../Scripts/run_live_console_websocket_hardening_receipt.py`](../../Scripts/run_live_console_websocket_hardening_receipt.py)

## Slice68 live-console UI polish route

Why this matters: Slice68 standardizes the visible posture language across the migration panel, combined live posture panel, and transport diagnostics while keeping the same advisory-only receipt sources.

Next action:
- Receipt: [`../../out/audit/live_console_ui_polish_001.latest.json`](../../out/audit/live_console_ui_polish_001.latest.json)
- Runner: [`../../Scripts/run_live_console_ui_polish_receipt.py`](../../Scripts/run_live_console_ui_polish_receipt.py)
- Feed transport source: [`../../apps/aal-viz-live-console/src/data/liveProjectionFeed.ts`](../../apps/aal-viz-live-console/src/data/liveProjectionFeed.ts)

## Out/ lane groups (178 top-level)

| Group | Lanes | Class |
|-------|------:|-------|
| `research_canary*` / `research_*` | 42 | REFERENCE — **do not regenerate** without full P128→P130 replay |
| `temporal_continuity*` | 42 | REFERENCE — P70–P102 procedural archive |
| `chamfer*` | 21 | ARCHIVED — v0.1 planning arc |
| `proposal*` / `overlay*` | 24 | REFERENCE |
| `canary_*` (scheduler/promotion) | 8 | REFERENCE |
| `continuity_namespace*` | 5 | REFERENCE |
| `audit/` | 1 | ACTIVE |
| `operator_review/` | 1 | ACTIVE |
| `sync/` | 1 | ACTIVE |
| `canon_resume_state/` | 1 | ACTIVE |
| `archive/` | 1 | ARCHIVED |
| `ingest/` / `oracle/` | 2 | ACTIVE (shadow/advisory) |

## Forbidden during routine work

- Regenerating `out/research_canary_*` without governed P128→P130 replay
- Treating ingest/scheduler receipts as execution authorization
- Deleting or moving historical `out/temporal_continuity_*` evidence

## Sprint 001 Layer

Brier Score: 0.35

Sprint 001 adds a technical-debt artifact navigation overlay.

- [Artifact Registry](./ARTIFACT_REGISTRY.md)
- Sweep receipt: [`../REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md`](../REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md)
- Parent Board ID: `3843e8ba-2f5c-8194-80d0-f2c5ffce6254`
- Sprint Hub ID: `3853e8ba-2f5c-8139-a132-ef1eab0ae237`
- Mirror Status: `PARTIAL_MIRROR_COMPLETE`

## Related docs

- [`docs/audits/AUDIT_INDEX.md`](../audits/AUDIT_INDEX.md)
- [`docs/releases/POST_2_5_0_CONTINUATION_AUDIT.md`](../releases/POST_2_5_0_CONTINUATION_AUDIT.md)
- [`AGENTS.md`](../../AGENTS.md) — canary spine guardrail
