# Artifact Index

## Current Artifact Routes

| Route | Purpose | Next action |
|-------|---------|-------------|
| [`../../core/generated_artifact_registry.py`](../../core/generated_artifact_registry.py) | Canonical generated artifact registry | Check whether an artifact has a no-arg generator. |
| [`../../out/audit/docs_navigation_refresh_001.latest.json`](../../out/audit/docs_navigation_refresh_001.latest.json) | Slice57 D1.1 navigation refresh receipt | Verify docs navigation provenance. |
| [`../../out/audit/artifact_registry_classifier_001.latest.json`](../../out/audit/artifact_registry_classifier_001.latest.json) | Slice59 artifact lifecycle/discoverability classifier receipt | Review managed vs orphaned vs historical-heavy groups before touching `out/`. |
| [`../../out/audit/canon_code_binding_audit_001.latest.json`](../../out/audit/canon_code_binding_audit_001.latest.json) | Canon-to-code binding audit scaffold receipt | Verify repo-visible subsystem bindings from canonical source to module, validator, proof artifact, freshness marker, authority status, and operator surface. |
| [`../../out/audit/continuity_lineage_map_refresh_001.latest.json`](../../out/audit/continuity_lineage_map_refresh_001.latest.json) | Slice60 continuity lineage refresh receipt | Review active, blocked, and historical temporal continuity routes before navigating P71-P102G. |
| [`../../out/audit/temporal_upstream_restoration_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_restoration_route_refresh_001.latest.json) | Slice73 temporal upstream restoration route refresh receipt | Review the current P75/P76 route from generator discovery to upstream dry-run planning before touching historical temporal continuity lanes. |
| [`../../out/audit/temporal_upstream_dry_run_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_dry_run_route_refresh_001.latest.json) | Slice74 temporal upstream dry-run route refresh receipt | Review the tracked P77 dry-run lane and its safe P78 planning handoff before proposing execution-plan packaging. |
| [`../../out/audit/temporal_upstream_execution_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_execution_route_refresh_001.latest.json) | Slice75 temporal upstream execution route refresh receipt | Review the tracked P78 execution-planning lane and its safe P79 authorization-gate handoff before proposing authorization packaging. |
| [`../../out/audit/temporal_upstream_authorization_gate_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_authorization_gate_route_refresh_001.latest.json) | Slice76 temporal upstream authorization-gate route refresh receipt | Review the tracked P79 authorization-gate lane and its safe P80 authorization-record-planning handoff before proposing P80 packaging. |
| [`../../out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json) | Slice77 temporal upstream authorization-record regeneration route refresh receipt | Review the explicit Slice50/Slice51 blocked-P80 route and its safe P83 status-repair follow-on before proposing any deeper regeneration packaging. |
| [`../../out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json) | Slice78 temporal upstream status-repair route refresh receipt | Review the emitted P83 status-repair packet and its safe P80 regeneration handoff before proposing any deeper P84 packaging. |
| [`../../out/audit/temporal_upstream_regeneration_plan_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_regeneration_plan_route_refresh_001.latest.json) | Slice79 temporal upstream regeneration-plan route refresh receipt | Review the emitted P84 regeneration-plan packet and its safe P85 execution-planning handoff before proposing any deeper regeneration execution packaging. |
| [`../../out/audit/temporal_upstream_regeneration_execution_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_regeneration_execution_route_refresh_001.latest.json) | Slice80 temporal upstream regeneration-execution route refresh receipt | Review the emitted P85 execution-planning packet and its safe P86 regeneration-planning handoff before proposing any deeper regeneration execution or authorization work. |
| [`../../out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json) | Slice81 temporal upstream regeneration-plan-regeneration route refresh receipt | Review the refreshed emitted P86 regeneration-plan-regeneration packet and its explicit downstream P87 handoff before proposing any deeper downstream packaging. |
| [`../../out/audit/temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json) | Slice82 temporal upstream status-plan regeneration route refresh receipt | Review the repo-real downstream P87 packet family, keep the P87-to-p83 naming bridge explicit, and preserve the safe P88 handoff before proposing any deeper downstream packaging. |
| [`../../out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json) | Slice83 temporal upstream status-plan regeneration execution route refresh receipt | Review the repo-real downstream P88 execution-planning packet family and preserve the observed P89-labelled P84 regeneration-plan handoff before proposing any deeper downstream bridge packaging. |
| [`../../out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json) | Slice84 temporal upstream status-plan regeneration execution bridge route refresh receipt | Review the explicit bridge from the observed P89-labelled downstream handoff into the existing P84 regeneration-plan family before proposing any deeper downstream continuity packaging. |
| [`../../out/audit/temporal_upstream_p83_regeneration_authorization_gate_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_p83_regeneration_authorization_gate_route_refresh_001.latest.json) | Slice85 temporal upstream P83 regeneration authorization-gate route refresh receipt | Review the existing repo-native P89-to-P90 downstream stack as historical/reference continuity evidence while keeping the Slice84 bridge as the active current-route context. |
| [`../../out/audit/subsystem_health_dashboard_001.latest.json`](../../out/audit/subsystem_health_dashboard_001.latest.json) | Slice61/Slice64/Slice72 subsystem health dashboard receipt | Review ownership, artifact lifecycle, continuity, migration-runner, alias-design, and VIZ posture before choosing a Phase 2 follow-on lane. |
| [`../../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json`](../../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json) | Slice62 continuity namespace migration tooling packaging receipt | Review the existing continuity namespace audit/plan/readiness/alias stack through one migration-tooling route. |
| [`../../out/audit/continuity_namespace_migration_run_001.latest.json`](../../out/audit/continuity_namespace_migration_run_001.latest.json) | Slice63 continuity namespace migration run receipt | Review staged advisory migration scaffolding, blocked authority, and rollback posture. |
| [`../../out/audit/continuity_namespace_migration_preflight_001.latest.json`](../../out/audit/continuity_namespace_migration_preflight_001.latest.json) | Priority 2 continuity namespace migration preflight receipt | Confirm migration runner, alias design, health dashboard, and closeout receipts are safe to use before any future UI consumer or additive design refresh. |
| [`../../out/audit/continuity_namespace_alias_implementation_design_001.latest.json`](../../out/audit/continuity_namespace_alias_implementation_design_001.latest.json) | Slice71 continuity namespace alias implementation design receipt | Review the held additive alias implementation route without opening alias materialization authority. |
| [`../../out/audit/live_console_migration_runner_posture_001.latest.json`](../../out/audit/live_console_migration_runner_posture_001.latest.json) | Slice65 live console migration runner posture receipt | Confirm the live console is projecting the dashboard-backed migration posture without introducing execution authority. |
| [`../../out/audit/live_console_migration_preflight_projection_001.latest.json`](../../out/audit/live_console_migration_preflight_projection_001.latest.json) | Priority 2 live console migration preflight projection receipt | Confirm the live console is projecting migration preflight checks and held authority without opening execution paths. |
| [`../../out/audit/live_projection_health_migration_artifact_001.latest.json`](../../out/audit/live_projection_health_migration_artifact_001.latest.json) | Slice66 combined live projection posture receipt | Review one live-console surface that summarizes subsystem health, migration posture, and artifact lifecycle findings. |
| [`../../out/audit/live_console_websocket_hardening_001.latest.json`](../../out/audit/live_console_websocket_hardening_001.latest.json) | Slice67 live-feed transport hardening receipt | Review deterministic reconnect, polling fallback, and fail-closed transport posture for the live console. |
| [`../../out/audit/live_console_ui_polish_001.latest.json`](../../out/audit/live_console_ui_polish_001.latest.json) | Slice68 live-console UI polish receipt | Review the small presentational consistency pass for posture badges, advisory notes, and feed diagnostics. |
| [`../../Scripts/run_artifact_registry_classifier_receipt.py`](../../Scripts/run_artifact_registry_classifier_receipt.py) | No-arg classifier runner | Regenerate the artifact lifecycle classifier receipt. |
| [`../../scripts/run_canon_code_binding_audit_receipt.py`](../../scripts/run_canon_code_binding_audit_receipt.py) | No-arg canon-to-code binding audit runner | Regenerate the advisory canon-to-code binding audit scaffold receipt. |
| [`../../Scripts/run_continuity_lineage_map_refresh_receipt.py`](../../Scripts/run_continuity_lineage_map_refresh_receipt.py) | No-arg continuity lineage runner | Regenerate the D3 continuity routing receipt. |
| [`../../Scripts/run_temporal_upstream_restoration_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_restoration_route_refresh_receipt.py) | No-arg upstream restoration route runner | Regenerate the Slice73 continuity route refresh receipt. |
| [`../../Scripts/run_temporal_upstream_dry_run_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_dry_run_route_refresh_receipt.py) | No-arg upstream dry-run route runner | Regenerate the Slice74 continuity dry-run route refresh receipt. |
| [`../../Scripts/run_temporal_upstream_execution_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_execution_route_refresh_receipt.py) | No-arg upstream execution route runner | Regenerate the Slice75 continuity execution-route refresh receipt. |
| [`../../Scripts/run_temporal_upstream_authorization_gate_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_authorization_gate_route_refresh_receipt.py) | No-arg upstream authorization-gate route runner | Regenerate the Slice76 continuity authorization-gate route refresh receipt. |
| [`../../Scripts/run_subsystem_health_dashboard_receipt.py`](../../Scripts/run_subsystem_health_dashboard_receipt.py) | No-arg subsystem health runner | Regenerate the Priority 2 subsystem health dashboard receipt. |
| [`../../Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py`](../../Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py) | No-arg continuity namespace migration runner | Regenerate the Slice62 migration-tooling packaging receipt. |
| [`../../Scripts/run_continuity_namespace_migration_runner.py`](../../Scripts/run_continuity_namespace_migration_runner.py) | No-arg continuity namespace migration simulation runner | Regenerate the Slice63 advisory migration run receipt. |
| [`../../scripts/run_continuity_namespace_migration_preflight_receipt.py`](../../scripts/run_continuity_namespace_migration_preflight_receipt.py) | No-arg continuity namespace migration preflight runner | Regenerate the Priority 2 migration preflight receipt before future migration-runner consumers. |
| [`../../Scripts/run_continuity_namespace_alias_implementation_design_receipt.py`](../../Scripts/run_continuity_namespace_alias_implementation_design_receipt.py) | No-arg continuity namespace alias implementation design runner | Regenerate the Slice71 held implementation-design receipt. |
| [`../../Scripts/run_live_console_migration_runner_posture_receipt.py`](../../Scripts/run_live_console_migration_runner_posture_receipt.py) | No-arg live console migration posture runner | Regenerate the Slice65 live-console visibility receipt. |
| [`../../Scripts/run_live_console_migration_preflight_projection_receipt.py`](../../Scripts/run_live_console_migration_preflight_projection_receipt.py) | No-arg live console migration preflight projection runner | Regenerate the Priority 2 live-console preflight visibility receipt. |
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

## Slice73 temporal upstream restoration route

Why this matters: Slice73 narrows the older continuity chain to the currently observed P75/P76 route, making it clear that generators are observed, upstream inputs remain missing, and the next safe surface is P77 dry-run planning only.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_restoration_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_restoration_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_restoration_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_restoration_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_RESTORATION_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_RESTORATION_ROUTE.md)

## Slice74 temporal upstream dry-run route

Why this matters: Slice74 makes the emitted P77 dry-run packet discoverable as an active contributor route, so the transition from dry-run planning to P78 execution planning stays visible and fail-closed.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_dry_run_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_dry_run_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_dry_run_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_dry_run_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_DRY_RUN_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_DRY_RUN_ROUTE.md)

## Slice75 temporal upstream execution route

Why this matters: Slice75 makes the emitted P78 execution-planning packet discoverable as an active contributor route, so the transition from execution planning to P79 authorization-gate planning stays visible and fail-closed.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_execution_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_execution_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_execution_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_execution_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_EXECUTION_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_EXECUTION_ROUTE.md)

## Slice76 temporal upstream authorization-gate route

Why this matters: Slice76 makes the emitted P79 authorization-gate packet discoverable as an active contributor route, so the transition from authorization-gate review to P80 authorization-record planning stays visible and fail-closed.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_authorization_gate_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_authorization_gate_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_authorization_gate_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_authorization_gate_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_GATE_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_GATE_ROUTE.md)

## Slice77 temporal upstream authorization-record regeneration route

Why this matters: Slice77 makes the blocked P80 follow-on discoverable as an explicit contributor route by packaging the existing Slice50/Slice51 missing-source and regeneration evidence into one status/receipt pair with a safe P83 handoff.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_authorization_record_regeneration_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_authorization_record_regeneration_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_RECORD_REGENERATION_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_RECORD_REGENERATION_ROUTE.md)

## Slice78 temporal upstream status-repair route

Why this matters: Slice78 makes the emitted P83 status-repair packet discoverable as an explicit contributor route, so the transition from the blocked P80 handoff back into downstream regeneration planning stays visible and fail-closed.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_status_repair_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_status_repair_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_REPAIR_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_REPAIR_ROUTE.md)

## Slice79 temporal upstream regeneration-plan route

Why this matters: Slice79 makes the emitted P84 regeneration-plan packet discoverable as an explicit contributor route, so the transition from the emitted P83 packet into the downstream P85 execution-planning handoff stays visible and fail-closed.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_regeneration_plan_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_regeneration_plan_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_regeneration_plan_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_regeneration_plan_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_ROUTE.md)

## Slice80 temporal upstream regeneration-execution route

Why this matters: Slice80 makes the emitted P85 execution-planning packet discoverable as an explicit contributor route, so the blocked-yet-observed execution posture and downstream P86 planning handoff stay visible and fail-closed.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_regeneration_execution_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_regeneration_execution_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_regeneration_execution_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_regeneration_execution_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_EXECUTION_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_EXECUTION_ROUTE.md)

## Slice81 temporal upstream regeneration-plan-regeneration route

Why this matters: Slice81 makes the refreshed emitted P86 regeneration-plan-regeneration packet discoverable as an explicit contributor route, so the current `P84_REGENERATION_NOT_REQUIRED` posture and downstream P87 handoff stay visible and fail-closed.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_regeneration_plan_regeneration_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_regeneration_plan_regeneration_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE.md)

## Slice82 temporal upstream status-plan regeneration route

Why this matters: Slice82 makes the repo-real downstream P87 packet family discoverable as an explicit contributor route, so the historical P87 lane id and the emitted `p83_status_plan_regeneration` packet family stay visible together and fail-closed.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_status_plan_regeneration_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_status_plan_regeneration_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_ROUTE.md)

## Slice83 temporal upstream status-plan regeneration execution route

Why this matters: Slice83 makes the repo-real downstream P88 execution-planning packet discoverable as an explicit contributor route, so the current execution-not-required posture and downstream P89-labelled P84 regeneration-plan handoff stay visible and fail-closed.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_ROUTE.md)

## Slice84 temporal upstream status-plan regeneration execution bridge route

Why this matters: Slice84 makes the literal observed P89-labelled downstream handoff discoverable as an explicit contributor bridge, so contributors can route from the repo-real P88 packet family into the existing P84 regeneration-plan family without inventing a separate implementation lane.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_BRIDGE_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_BRIDGE_ROUTE.md)

## Slice85 temporal upstream P83 regeneration authorization-gate route

Why this matters: Slice85 surfaces the already-present repo-native P89 authorization-gate
and P90 authorization-record-plan packets so contributors can review that downstream stack
from the route spine without mistaking it for active authorization, token, or record-creation work.

Next action:
- Receipt: [`../../out/audit/temporal_upstream_p83_regeneration_authorization_gate_route_refresh_001.latest.json`](../../out/audit/temporal_upstream_p83_regeneration_authorization_gate_route_refresh_001.latest.json)
- Runner: [`../../Scripts/run_temporal_upstream_p83_regeneration_authorization_gate_route_refresh_receipt.py`](../../Scripts/run_temporal_upstream_p83_regeneration_authorization_gate_route_refresh_receipt.py)
- Status page: [`../status/TEMPORAL_CONTINUITY_UPSTREAM_P83_REGENERATION_AUTHORIZATION_GATE_ROUTE.md`](../status/TEMPORAL_CONTINUITY_UPSTREAM_P83_REGENERATION_AUTHORIZATION_GATE_ROUTE.md)

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

## Priority 2 continuity namespace migration preflight route

Why this matters: future UI consumers and additive-design refreshes should not consume the migration runner blindly. The preflight receipt checks the migration runner, alias implementation design, subsystem health dashboard, and Priority 2 closeout receipts while keeping alias materialization, path renames, execution, runtime/canon mutation, and queue/scheduler mutation closed.

Next action:
- Receipt: [`../../out/audit/continuity_namespace_migration_preflight_001.latest.json`](../../out/audit/continuity_namespace_migration_preflight_001.latest.json)
- Runner: [`../../scripts/run_continuity_namespace_migration_preflight_receipt.py`](../../scripts/run_continuity_namespace_migration_preflight_receipt.py)
- Runbook: [`../status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](../status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md)

## Slice71 continuity namespace alias implementation design route

Why this matters: this route keeps additive alias implementation planning discoverable as a managed advisory artifact instead of leaving it implicit in the earlier migration stack.

Next action:
- Receipt: [`../../out/audit/continuity_namespace_alias_implementation_design_001.latest.json`](../../out/audit/continuity_namespace_alias_implementation_design_001.latest.json)
- Runner: [`../../Scripts/run_continuity_namespace_alias_implementation_design_receipt.py`](../../Scripts/run_continuity_namespace_alias_implementation_design_receipt.py)
- Status page: [`../status/CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md`](../status/CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md)

## Slice72 subsystem health dashboard alignment route

Why this matters: Slice72 keeps the health dashboard receipt aligned with the merged alias-design route, so artifact and status navigation no longer point at Slice71 as unimplemented future work.

Next action:
- Receipt: [`../../out/audit/subsystem_health_dashboard_001.latest.json`](../../out/audit/subsystem_health_dashboard_001.latest.json)
- Runner: [`../../Scripts/run_subsystem_health_dashboard_receipt.py`](../../Scripts/run_subsystem_health_dashboard_receipt.py)
- Status page: [`../status/SUBSYSTEM_HEALTH_DASHBOARD.md`](../status/SUBSYSTEM_HEALTH_DASHBOARD.md)

## Slice65 live console migration visibility route

Why this matters: Slice65 carries the same migration posture into the AAL-Viz live console bundle, so contributors can observe the dashboard-backed migration state directly in the live view without creating a second source of truth.

Next action:
- Receipt: [`../../out/audit/live_console_migration_runner_posture_001.latest.json`](../../out/audit/live_console_migration_runner_posture_001.latest.json)
- Runner: [`../../Scripts/run_live_console_migration_runner_posture_receipt.py`](../../Scripts/run_live_console_migration_runner_posture_receipt.py)
- Bundle: [`../../apps/aal-viz-live-console/public/projection-bundle.json`](../../apps/aal-viz-live-console/public/projection-bundle.json)

## Priority 2 live console migration preflight projection route

Why this matters: this route carries the receipt-driven migration preflight into the AAL-Viz live console as display-only posture, so operators can see pass/held checks and blocked authority before any future migration UI consumer.

Next action:
- Receipt: [`../../out/audit/live_console_migration_preflight_projection_001.latest.json`](../../out/audit/live_console_migration_preflight_projection_001.latest.json)
- Runner: [`../../Scripts/run_live_console_migration_preflight_projection_receipt.py`](../../Scripts/run_live_console_migration_preflight_projection_receipt.py)
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
## Slice69 Priority 2 closeout route

Why this matters: the Priority 2 lane now has a single advisory closeout receipt that points contributors from health routing to migration tooling and live-console surfaces without adding new authority.

Next action:
- Closeout receipt: [`../../out/audit/priority2_live_console_migration_closeout_001.latest.json`](../../out/audit/priority2_live_console_migration_closeout_001.latest.json)
- Runner: [`../../Scripts/run_priority2_live_console_migration_closeout_receipt.py`](../../Scripts/run_priority2_live_console_migration_closeout_receipt.py)

## Slice70 rune integrity CI visibility route

Why this matters: this route keeps the rune scanner and its CI wiring discoverable as managed advisory artifacts instead of a hidden workflow tweak.

Next action:
- Wiring receipt: [`../../out/audit/rune_integrity_ci_workflow_wiring_001.latest.json`](../../out/audit/rune_integrity_ci_workflow_wiring_001.latest.json)
- Runner: [`../../Scripts/run_rune_integrity_ci_workflow_wiring_receipt.py`](../../Scripts/run_rune_integrity_ci_workflow_wiring_receipt.py)
- Scanner receipt: [`../../out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json`](../../out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json)
