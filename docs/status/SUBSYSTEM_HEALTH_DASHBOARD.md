# Subsystem Health Dashboard

Status: `SUBSYSTEM_HEALTH_DASHBOARD_READY_ADVISORY_ONLY`
Brier Score: 0.10

This is a repo-native subsystem health projection that aggregates ownership routing, artifact lifecycle posture, continuity routing, continuity namespace migration runner posture, continuity namespace alias implementation design posture, and AAL-Viz projection evidence. It is visibility only: no governance, runtime, sandbox, MCP, canon, or writeback authority is granted.

## Subsystem Overview

| Subsystem | Health posture | Pipelines | Contract alignment | Migration statuses | Evidence note |
| --- | --- | --- | --- | --- | --- |
| AAL-Viz | ACTIVE | 1 | ALIGNED | specified | Slice52 VIZ live-feed receipt observed |
| BeatOven / PsyFi | PARTIAL | 1 | MISSING_CONTRACT | specified | repo-native ownership route observed |
| Canon Governance | ACTIVE | 1 | ALIGNED | specified | repo-native ownership route observed |
| Governance / Drift Detection | ACTIVE | 1 | ALIGNED | specified | repo-native ownership route observed |
| HollerSports | PARTIAL | 1 | MISSING_CONTRACT | specified | repo-native ownership route observed |
| Level 99 | PARTIAL | 1 | MISSING_CONTRACT | specified | repo-native ownership route observed |
| Neon Genie | PARTIAL | 1 | MISSING_CONTRACT | specified | repo-native ownership route observed |
| Noctis | PARTIAL | 1 | MISSING_CONTRACT | specified | repo-native ownership route observed |
| Operator Governance | ACTIVE | 1 | ALIGNED | specified | repo-native ownership route observed |
| Oracle / ASE / Memetic Futurecast | PARTIAL | 1 | MISSING_CONTRACT | specified | repo-native ownership route observed |
| Oracle Signal Layer | ACTIVE | 1 | ALIGNED | specified | repo-native ownership route observed |
| Outcome Binding / Brier Ledger | ACTIVE | 1 | ALIGNED | specified | repo-native ownership route observed |
| PSE Forecast Engine | ACTIVE | 1 | ALIGNED | specified | repo-native ownership route observed |
| Phonomicon | PARTIAL | 1 | MISSING_CONTRACT | specified | repo-native ownership route observed |
| Research Intake Automation | PARTIAL | 1 | ALIGNED | partial | repo-native ownership route observed |
| Research Validation | PARTIAL | 1 | ALIGNED | partial | repo-native ownership route observed |
| Universal Ingest | ACTIVE | 1 | ALIGNED | specified | repo-native ownership route observed |
| abx-familiar | PARTIAL | 1 | MISSING_CONTRACT | specified | repo-native ownership route observed |

## Ownership Coverage Posture

- Subsystems observed: `18`
- Pipelines observed: `18`
- Contract-aligned subsystems: `10`
- Missing contract routes: `8`

## Artifact Lifecycle / Regeneration Posture

- Managed artifacts: `645`
- Orphaned artifacts: `735`
- No-arg regenerable artifacts: `645`

| Family | Route class | Artifact count | Managed | No-arg regenerable |
| --- | --- | --- | --- | --- |
| audit/ | ACTIVE | 456 | 139 | 139 |
| operator_review/ | ACTIVE | 413 | 249 | 249 |
| projections/ | ACTIVE | 132 | 75 | 75 |
| sync/ | ACTIVE | 103 | 28 | 28 |
| metric_operator/ | REVIEW | 87 | 30 | 30 |
| contracts/ | ACTIVE | 79 | 56 | 56 |

## Continuity Health / Blocked-Chain Posture

- Highest observed continuity lane: `P102G`
- Continuity lane count: `58`
- Blocked continuity edges: `5`

| Route group | Current posture | Recommended next lane | Why this matters |
| --- | --- | --- | --- |
| P71-P76 binder/evidence/restoration chain | RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE | P75_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN | This is the earliest repo-native restoration route for missing temporal evidence. |
| P77-P85 upstream regeneration and authorization chain | `DRY_RUN_READY_WITH_MISSING_INPUTS` then `EXECUTION_PLAN_READY` then `AUTHORIZATION_ELIGIBLE` then downstream `NOT_COMPUTABLE` with emitted P83 pass-through | P80_AUTHORIZATION_RECORD_PLAN_REGENERATION | Slice74-Slice78 now surface the tracked P77/P78/P79 posture, the blocked P80 follow-on, and the emitted P83 status-repair packet directly; downstream authorization-record planning remains advisory-only and fail-closed. |
| P86-P101 regeneration and readiness planning chain | HISTORICAL_REFERENCE_CHAIN_PRESENT | REFERENCE_ONLY | This planning chain preserves the downstream regeneration and readiness logic after the first blocked edges appear. |
| P102-P102G repair router and historical recovery chain | HISTORICAL_RECOVERY_AUDIT_COMPLETE_WITH_BLOCKERS | NOT_COMPUTABLE | This chain compresses the late-stage repair router and preserves disputed historical continuity as explicit audit evidence. |

## VIZ Projection Posture

- Slice52 posture: `VIZ01_LIVE_FEED_ENHANCEMENT_READY_ADVISORY_ONLY`
- Implemented surfaces observed: `5`
- Connection states: `CONNECTING, LIVE_STREAM, POLLING_FALLBACK, SAMPLE_FALLBACK, FAIL_CLOSED`

## Continuity Namespace Migration Runner Posture

- Slice63 posture: `CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY`
- Requested execution posture: `READY`
- Safe next surface: `CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY`
- Blocked action classes: `8`
- Live console visibility route: `out/audit/live_console_migration_runner_posture_001.latest.json`

| Signal | Value |
| --- | --- |
| Migration run id | `CONTINUITY_NAMESPACE_MIGRATION_RUN_001` |
| Requested execution reason | Runner is operating as a deterministic advisory migration simulation only. |
| Recommended next engineering move | Additive alias implementation design slice |
| Blocked action sample | RENAME_FILES, MOVE_FILES, REWRITE_IDS, MATERIALIZE_ALIAS_MANIFEST |
| Stage posture summary | READY:3, SCAFFOLD_ONLY:3, ROLLBACK_DEFINED:1 |

## Continuity Namespace Alias Implementation Design Posture

- Slice71 posture: `CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN_READY_ADVISORY_ONLY`
- Implementation state: `DESIGN_ONLY_HELD`
- Safe next surface: `CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY`
- Valid for implementation: `false`

| Signal | Value |
| --- | --- |
| Required stabilization status | `ALIAS_PLAN_STABILIZED_ADVISORY_ONLY` |
| Recommended next engineering move | Keep additive alias implementation at design-only posture until a future stabilization receipt explicitly lifts the implementation hold. |
| Blocked action sample | RENAME_FILES, MOVE_FILES, REWRITE_IDS, MATERIALIZE_ALIAS_MANIFEST |

## Top Advisory Findings

- `OWNERSHIP_CONTRACT_GAPS` (MEDIUM): 8 subsystem contract routes remain missing, so ownership posture is only partial.
- `ORPHANED_ARTIFACTS_PRESENT` (MEDIUM): 735 orphaned artifacts remain in the registry view.
- `AMBIGUOUS_GENERATORS_PRESENT` (MEDIUM): 2 artifacts still resolve to ambiguous generators.
- `LARGE_HISTORICAL_FAMILY` (LOW): metric_operator/ contains 87 artifacts and should stay discoverable without becoming a routine regeneration target.
- `CONTINUITY_BLOCKED_EDGE` (MEDIUM): P74_RESTORATION_PENDING remains RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE and routes to P75_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN.
- `ALIAS_IMPLEMENTATION_HELD` (MEDIUM): Continuity namespace alias implementation remains design-only held and still requires a future stabilization receipt before any additive implementation review lane can open.

## Why This Matters

Priority 3 created the routing, ownership, artifact, and continuity inputs needed for a repo-native health surface. Slice61 compresses those inputs into one deterministic dashboard so contributors can evaluate subsystem posture without conflating visibility with authority. Slice64 extends that surface so the continuity namespace migration run-layer is visible in the same advisory dashboard instead of living as a disconnected migration-only receipt, Slice66 carries the same posture into the live console as one grouped observational panel, Slice67 hardens the live-feed transport so those projections stay visible through deterministic reconnect and fallback posture, and Slice72 keeps the migration route current by surfacing the merged alias implementation design posture instead of pointing to it as future work.

## Next Action

- Receipt: [`../../out/audit/subsystem_health_dashboard_001.latest.json`](../../out/audit/subsystem_health_dashboard_001.latest.json)
- Runner: [`../../Scripts/run_subsystem_health_dashboard_receipt.py`](../../Scripts/run_subsystem_health_dashboard_receipt.py)
- Migration runbook: [`CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md)
- Alias implementation design route: [`CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md`](CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md)
- Live console combined posture receipt: [`../../out/audit/live_projection_health_migration_artifact_001.latest.json`](../../out/audit/live_projection_health_migration_artifact_001.latest.json)
- Live feed transport receipt: [`../../out/audit/live_console_websocket_hardening_001.latest.json`](../../out/audit/live_console_websocket_hardening_001.latest.json)
- Recommended next lane: `Hold continuity namespace alias lane at design-only posture`
- Keep `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` unissued unless the operator explicitly provides it in a future gate.

## Boundary Note

Projection and status routing only. No sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous Notion/GitHub writeback is authorized.

Provenance: Notion Sprint 001 Hub + Loop 805 Slice72 + Hash: receipt canonical_hash
