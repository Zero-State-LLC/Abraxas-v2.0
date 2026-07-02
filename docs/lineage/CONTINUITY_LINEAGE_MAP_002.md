# Continuity Lineage Map 002

Abraxas Codex v2.7 - respecting custom instructions + surfaces + governance loop + Notion mirror

Status: `CONTINUITY_LINEAGE_MAP_REFRESH_READY_ADVISORY_ONLY`
Brier Score: 0.10

This page is the current D3 continuity navigation route. It compresses the repo-native temporal continuity spine into active navigation groups, blocked edges, and historical references. It does not repair evidence, regenerate sources, grant authorization, or activate any runtime path.

## Why this matters

Brier Score: 0.10

- New contributors need one continuity route instead of reading every P71-P102G surface in raw order.
- The repo already contains continuity evidence, but it spans receipts, plans, and historical audits with mixed current and blocked posture.
- This page keeps blocked and `NOT_COMPUTABLE` edges explicit so readers do not confuse planning receipts with repaired or executable state.

## Next action

Brier Score: 0.10

- Start with [`../status/continuity-spine.json`](../status/continuity-spine.json) for the observed lane inventory.
- Use [`../../out/audit/continuity_lineage_map_refresh_001.latest.json`](../../out/audit/continuity_lineage_map_refresh_001.latest.json) for the current continuity routing receipt.
- Follow the route groups below in order; when a chain is blocked, use the listed next lane and stop rather than inventing repair authority.

## Current continuity route groups

Brier Score: 0.10

| Route group | Span | Class | Current posture | Primary route | Why this matters | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| Binder / evidence / restoration chain | P71-P76 | `ACTIVE NAVIGATION` | `RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE` | [`P74_temporal_continuity_missing_evidence_restoration_plan.md`](../plans/P74_temporal_continuity_missing_evidence_restoration_plan.md) | This is the earliest repo-native route for missing temporal evidence. | Route to `P75_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN` before downstream continuity work. |
| Upstream regeneration / authorization planning chain | P77-P85 | `ACTIVE NAVIGATION` | `NOT_COMPUTABLE / BLOCKED` | [`P81_temporal_continuity_authorization_record_plan_source_status_audit.md`](../plans/P81_temporal_continuity_authorization_record_plan_source_status_audit.md) | This chain explains why the P80 authorization record plan route is missing from generated evidence and why regeneration planning remains fail-closed. | Review [`P80_temporal_continuity_upstream_input_regeneration_authorization_record_plan.md`](../plans/P80_temporal_continuity_upstream_input_regeneration_authorization_record_plan.md) as the intended source lane, then use P81 and P84/P85 findings; do not create authorization artifacts. |
| Regeneration / readiness planning chain | P86-P101 | `HISTORICAL REFERENCE` | `REFERENCE CHAIN PRESENT` | [`../../PLANS.md`](../../PLANS.md) | These plans preserve downstream repair and readiness logic after the first blocked edges appear. | Use as reference context after earlier missing or blocked routes are understood. |
| Repair router / historical recovery chain | P102-P102G | `ACTIVE NAVIGATION` | `HISTORICAL_RECOVERY_AUDIT_COMPLETE_WITH_BLOCKERS` | [`P102G_temporal_continuity_historical_recovery_audit.md`](../plans/P102G_temporal_continuity_historical_recovery_audit.md) | This chain preserves disputed late continuity as explicit audit evidence. | Treat as historical interpretation only; downstream remains `NOT_COMPUTABLE`. |

## Blocked and degraded edges

Brier Score: 0.10

| Edge | Current posture | Observed issue | Advisory route |
| --- | --- | --- | --- |
| P74 restoration edge | `RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE` | Earliest restoration route still reports missing evidence. | `P75_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN` |
| P80 source edge | `MISSING` | `out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json` is absent. | `P80_AUTHORIZATION_RECORD_PLAN_REGENERATION` via P81 |
| P84 regeneration-plan edge | `NOT_COMPUTABLE` | P80 regeneration plan is not ready and routes backward to status repair. | `P83_STATUS_REPAIR_PLAN_REGENERATION` |
| P85 execution-plan edge | `P80_REGENERATION_EXECUTION_PLAN_BLOCKED` | Execution planning remains blocked because the upstream regeneration plan is not ready. | `P84_REGENERATION_PLAN_REGENERATION` |
| P102G historical recovery edge | `HISTORICAL_RECOVERY_AUDIT_COMPLETE_WITH_BLOCKERS` | Historical recovery remains held and keeps downstream continuity not computable. | `NOT_COMPUTABLE` / operator evidence only |

## Reader routing table

Brier Score: 0.10

| If you need to understand... | Start here | Then drill into |
| --- | --- | --- |
| The current observed continuity inventory | [`../status/continuity-spine.json`](../status/continuity-spine.json) | [`../../out/audit/continuity_lineage_map_refresh_001.latest.json`](../../out/audit/continuity_lineage_map_refresh_001.latest.json) |
| Missing evidence in the earliest continuity route | [`P74_temporal_continuity_missing_evidence_restoration_plan.md`](../plans/P74_temporal_continuity_missing_evidence_restoration_plan.md) | `out/temporal_continuity_missing_evidence_restoration_plan/latest.json` |
| Why the authorization record planning chain is blocked | [`P80_temporal_continuity_upstream_input_regeneration_authorization_record_plan.md`](../plans/P80_temporal_continuity_upstream_input_regeneration_authorization_record_plan.md) | [`P81_temporal_continuity_authorization_record_plan_source_status_audit.md`](../plans/P81_temporal_continuity_authorization_record_plan_source_status_audit.md), `out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json`, `P84`, and `P85` |
| Downstream regeneration and readiness plans | [`../../PLANS.md`](../../PLANS.md) | `P86` through `P101` reference chain |
| Disputed historical continuity and late repair routing | [`P102G_temporal_continuity_historical_recovery_audit.md`](../plans/P102G_temporal_continuity_historical_recovery_audit.md) | `out/temporal_continuity_historical_recovery_audit/latest.json` |
| Receipt-backed artifact routing for continuity files | [`../artifacts/ARTIFACT_INDEX.md`](../artifacts/ARTIFACT_INDEX.md) | [`../../core/generated_artifact_registry.py`](../../core/generated_artifact_registry.py) |

## Boundary and preservation notes

Brier Score: 0.10

- This page refreshes an existing lineage surface; it does not supersede or delete raw continuity artifacts.
- [`../status/continuity-spine.json`](../status/continuity-spine.json) remains the repo-native continuity inventory.
- Historical plans under `docs/plans/` and raw `out/temporal_continuity_*` evidence remain preserved reference surfaces.
- No repair execution, no source regeneration, no authorization creation, no sandbox probe, and no runtime activation are granted here.

## Provenance

Brier Score: 0.10

- Current source spine: [`../status/continuity-spine.json`](../status/continuity-spine.json)
- Current D3 receipt: [`../../out/audit/continuity_lineage_map_refresh_001.latest.json`](../../out/audit/continuity_lineage_map_refresh_001.latest.json)
- Historical precursor: [`../audits/CONTINUITY_LINEAGE_MAP_001.md`](../audits/CONTINUITY_LINEAGE_MAP_001.md)
- Board mirror: [Notion Sprint 001 Hub](https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254)
- Boundary: projection/navigation only; no governance, repair, authorization, or activation authority
