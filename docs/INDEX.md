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
| Architecture | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | Shows subsystem shape and boundaries. | Locate the subsystem. |
| Governance/instructions | [`../GOVERNANCE_V3.md`](../GOVERNANCE_V3.md), [`../AGENTS.md`](../AGENTS.md) | Defines authority locks and operator control. | Read before changing behavior. |
| Continuation plans | [`../PLANS.md`](../PLANS.md) | Lists active lanes and receipts. | Confirm current frontier. |
| Task mirror | [Notion Sprint 001 Hub](https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254) | Living board/source mirror. | Use for alignment; no autonomous writeback. |
| Subsystem routing | [`status/SUBSYSTEM_OWNERSHIP_MATRIX.md`](status/SUBSYSTEM_OWNERSHIP_MATRIX.md) | Repo-native ownership routes | Clarifies which observed pipelines anchor each subsystem. | Check here before reassigning or extending subsystem surfaces. |
| Subsystem health | [`status/SUBSYSTEM_HEALTH_DASHBOARD.md`](status/SUBSYSTEM_HEALTH_DASHBOARD.md) | Repo-native health projection | Aggregates ownership, artifact lifecycle, continuity, and VIZ posture into one phase-2 health surface. | Use this before selecting a health, migration, or UI follow-on lane. |
| Migration tooling | [`status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md`](status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md) | Migration/status projection | Packages the existing continuity namespace tooling stack into one contributor-facing route. | Use this after the health dashboard flags continuity migration follow-up. |

## Surface Role Routes

| Surface role | Current route | Why this matters | Next action |
|--------------|---------------|------------------|-------------|
| Identity/status | [`../README.md`](../README.md), [`../STATUS.md`](../STATUS.md) | Defines what the repo is and how healthy it is. | Use for orientation. |
| Governance | [`../GOVERNANCE_V3.md`](../GOVERNANCE_V3.md), [`../AGENTS.md`](../AGENTS.md) | Authority, locks, and operator rules. | Treat as protected. |
| Architecture | [`../ARCHITECTURE.md`](../ARCHITECTURE.md), [`architecture/`](architecture/) | System shape and technical maps. | Follow existing subsystem boundaries. |
| Code/module maps | [`../core/`](../core/), [`../Scripts/`](../Scripts/), [`../scripts/`](../scripts/) | Engineering surfaces and runners. | Prefer no-arg receipt runners for generated artifacts. |
| Generated artifacts | [`artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md), [`../core/generated_artifact_registry.py`](../core/generated_artifact_registry.py) | Artifact lifecycle and regeneration policy. | Verify canonical generator before editing outputs. |
| Audit history | [`audits/AUDIT_INDEX.md`](audits/AUDIT_INDEX.md) | Current and historical evidence. | Classify rather than delete. |
| Releases | [`releases/RELEASE_INDEX.md`](releases/RELEASE_INDEX.md) | Continuation/release baseline. | Start from the active baseline. |
| Runtime docs | [`runtime/`](runtime/) | Planning and readiness surfaces. | Keep execution authority separate. |
| Oracle docs | [`oracle/`](oracle/) | Oracle planning/intake surfaces. | Keep live gates explicit. |
| Visualization docs | [`visualization/`](visualization/) | VIZ and projection surfaces. | Keep UI projection read-only unless gated. |

## Active Receipt Routes

| Receipt | Runner | Status |
|---------|--------|--------|
| [`../out/audit/docs_navigation_refresh_001.latest.json`](../out/audit/docs_navigation_refresh_001.latest.json) | [`../Scripts/run_docs_navigation_refresh_receipt.py`](../Scripts/run_docs_navigation_refresh_receipt.py) | `DOCS_NAVIGATION_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/subsystem_ownership_matrix_refresh_001.latest.json`](../out/audit/subsystem_ownership_matrix_refresh_001.latest.json) | [`../Scripts/run_subsystem_ownership_matrix_refresh_receipt.py`](../Scripts/run_subsystem_ownership_matrix_refresh_receipt.py) | `SUBSYSTEM_OWNERSHIP_MATRIX_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/artifact_registry_classifier_001.latest.json`](../out/audit/artifact_registry_classifier_001.latest.json) | [`../Scripts/run_artifact_registry_classifier_receipt.py`](../Scripts/run_artifact_registry_classifier_receipt.py) | `ARTIFACT_REGISTRY_CLASSIFIER_READY_ADVISORY_ONLY` |
| [`../out/audit/subsystem_health_dashboard_001.latest.json`](../out/audit/subsystem_health_dashboard_001.latest.json) | [`../Scripts/run_subsystem_health_dashboard_receipt.py`](../Scripts/run_subsystem_health_dashboard_receipt.py) | `SUBSYSTEM_HEALTH_DASHBOARD_READY_ADVISORY_ONLY` |
| [`../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json`](../out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json) | [`../Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py`](../Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py) | `CONTINUITY_NAMESPACE_MIGRATION_TOOLING_REFRESH_READY_ADVISORY_ONLY` |
| [`../out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json`](../out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json) | [`../Scripts/run_rune_integrity_scanner_guardrails_receipt.py`](../Scripts/run_rune_integrity_scanner_guardrails_receipt.py) | Advisory scanner/guardrails |
| [`../out/audit/hyperstition_evaluator_deepening_receipt_001.latest.json`](../out/audit/hyperstition_evaluator_deepening_receipt_001.latest.json) | [`../Scripts/run_hyperstition_evaluator_deepening_receipt.py`](../Scripts/run_hyperstition_evaluator_deepening_receipt.py) | Advisory evaluator projection |
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
- Verify `python Scripts/run_docs_navigation_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/docs_navigation_refresh_001.latest.json`
- Keep `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` unissued unless the operator explicitly provides it in a future gate.

## Slice58 Ownership Refresh

Why this matters: Priority 3 now includes a real ownership route instead of a partial mirror note, which makes architecture and contract navigation materially faster for new contributors.

Next action:
- Verify `python Scripts/run_subsystem_ownership_matrix_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/subsystem_ownership_matrix_refresh_001.latest.json`
- Use [`status/SUBSYSTEM_OWNERSHIP_MATRIX.md`](status/SUBSYSTEM_OWNERSHIP_MATRIX.md) before changing subsystem boundaries or module routing assumptions.

## Slice59 Artifact Classifier

Why this matters: D2 adds a deterministic artifact lifecycle/discoverability receipt so contributors can see managed vs orphaned vs historical-heavy groups without treating `docs/artifacts/ARTIFACT_INDEX.md` as the source of truth.

Next action:
- Verify `python Scripts/run_artifact_registry_classifier_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/artifact_registry_classifier_001.latest.json`
- Use [`artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md) for navigation and [`../core/generated_artifact_registry.py`](../core/generated_artifact_registry.py) as canonical registry truth.

## Slice60 Continuity Lineage Refresh

Why this matters: D3 turns the repo-native temporal continuity spine into a compact route for contributors, preserving historical context while making blocked and missing-chain edges easy to find.

Next action:
- Verify `python Scripts/run_continuity_lineage_map_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/continuity_lineage_map_refresh_001.latest.json`
- Use [`lineage/CONTINUITY_LINEAGE_MAP_002.md`](lineage/CONTINUITY_LINEAGE_MAP_002.md) for continuity routing and [`status/continuity-spine.json`](status/continuity-spine.json) as the source spine surface.

## Slice61 Subsystem Health Dashboard

Why this matters: Priority 2 starts with a deterministic dashboard packet that compresses the key Priority 3 routes into one health and discoverability surface.

Next action:
- Verify `python Scripts/run_subsystem_health_dashboard_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/subsystem_health_dashboard_001.latest.json`
- Use [`status/SUBSYSTEM_HEALTH_DASHBOARD.md`](status/SUBSYSTEM_HEALTH_DASHBOARD.md) before choosing between migration tooling and Live Console follow-ons.

## Slice62 Continuity Namespace Migration Tooling Refresh

Why this matters: Slice61 identified migration tooling as the strongest next Priority 2 route. Slice62 packages the existing continuity namespace stack into one deterministic status and receipt pair so contributors can understand current migration posture without reopening or rewriting the original continuity namespace artifacts.

Next action:
- Verify `python Scripts/run_continuity_namespace_migration_tooling_refresh_receipt.py`
- Verify `python scripts/run_artifact_regeneration.py --artifact out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json`
- Use [`status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md`](status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md) before scoping any future additive alias implementation design work.

Provenance: Notion Sprint 001 Hub + Loop 805 Slice60 + Hash: receipt canonical_hash
