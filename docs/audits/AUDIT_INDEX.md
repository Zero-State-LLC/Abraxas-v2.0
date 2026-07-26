# Audit Index

## Current Audit Routes

| Route | Purpose | Next action |
|-------|---------|-------------|
| [`DOCUMENTATION_TOPOLOGY_AUDIT_001.md`](DOCUMENTATION_TOPOLOGY_AUDIT_001.md) | D1 documentation topology evidence | Use as historical context for navigation debt. |
| [`REPOSITORY_ORGANIZATION_INVENTORY_001.md`](REPOSITORY_ORGANIZATION_INVENTORY_001.md) | Repository organization inventory | Use for repo-shape evidence. |
| [`codebase-efficiency-2026/18_PHASE5_LINEENDING_PORTABILITY_REPAIR_RECEIPT.md`](codebase-efficiency-2026/18_PHASE5_LINEENDING_PORTABILITY_REPAIR_RECEIPT.md) | Phase 5 CRLF source-hash portability evidence | Pair with [`../workflows/source-hash-line-ending-portability.md`](../workflows/source-hash-line-ending-portability.md) for developer usage. |
| [`../../out/audit/docs_navigation_refresh_001.latest.json`](../../out/audit/docs_navigation_refresh_001.latest.json) | Slice57 D1.1 navigation refresh receipt | Verify current docs navigation consolidation. |

Central index for [`docs/audits/`](.). Do not delete audit files — classify only.

**Legend:** **Current** = active operator/sync/codegen reference · **Historical** = completed arc evidence · **Archived** = explicit seal/archive receipt

| File | Tier | Purpose | Date | Relevance | Superseded by |
|------|------|---------|------|-----------|---------------|
| `CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE.md` | Current | Codegen attestation intake procedure | 2026-06 | Active — intake VALIDATED, ODR bridge complete | — |
| `ABRAXAS_REPO_NOTION_DIFF_001.md` | Current | Repo vs Notion diff audit | 2026 | Active reference for manual sync | `out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json` |
| `ABRAXAS_BINDING_MATRIX_AND_COUPLING_MAP_AUDIT_001.md` | Current | Binding/coupling map | 2026 | Architecture reference | — |
| `STATUS_PAGES_DEPLOY_GATE_AUDIT_001.md` | Current | GitHub Pages deploy gate | 2026 | CI/deploy reference | — |
| `REPOSITORY_ORGANIZATION_INVENTORY_001.md` | Current | Repo structure inventory | 2026-06-18 | Navigation sweep | — |
| `DOCUMENTATION_TOPOLOGY_AUDIT_001.md` | Current | Doc entrypoint audit | 2026-06-18 | Navigation sweep | — |
| `REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md` | Current | Sweep closure receipt | 2026-06-18 | Navigation sweep | — |
| `ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_IMPLEMENTATION_PLAN_001.md` | Current | Spec-stack schema audit lane | 2026-06-18 | Five-domain advisory audit | `out/audit/abraxas_spec_stack_schema_audit_receipt_001.latest.json` |
| `codebase-efficiency-2026/18_PHASE5_LINEENDING_PORTABILITY_REPAIR_RECEIPT.md` | Current | CRLF-tolerant hygiene source-hash repair | 2026-07-26 | Windows/Linux portability evidence for Phase 1 completion-validation | [`../workflows/source-hash-line-ending-portability.md`](../workflows/source-hash-line-ending-portability.md) |
| `REPO_EXECUTION_RECEIPT_runtime_shadow_wiring_hooks.md` | Historical | PR #726 shadow wiring | 2026-06 | Evidence | POST_2_5_0 audit |
| `REPO_EXECUTION_RECEIPT_P132_advisory_shadow_activation.md` | Historical | 6/6 advisory shadow pilot | 2026-06 | Evidence | POST_P132 plan |
| `REPO_EXECUTION_RECEIPT_oracle_signal_shadow_physical_implementation.md` | Historical | Oracle shadow impl | 2026-06 | Evidence | POST_2_5_0 audit |
| `REPO_EXECUTION_RECEIPT_P131_final_activation_operator_decision_record.md` | Historical | P131 ODR evidence | 2026-06 | Evidence | P130 hold |
| `REPO_EXECUTION_RECEIPT_P130_final_activation_authorization_review_boundary_held.md` | Historical | P130 hold boundary | 2026-06 | Evidence | P130 hold receipt |
| `2026-05-20_post_p31_repo_audit.md` | Archived | Post-P31 audit | 2026-05 | Historical | Governance V3 / 2.5.0 |
| `REPO_FINAL_SEAL_P101_P130_research_canary_evidence_chain_closed.md` | Archived | Canary chain seal | 2026 | Historical seal | Registry repair closure |
| `REPO_FINAL_ARCHIVE_RECEIPT_GEOMETRIC_INTELLIGENCE_RUNTIME_v0_1.md` | Archived | Geometric runtime archive | v0.1 | Historical | Chamfer arc receipts |
| `REPO_POST_V0_1_BATCH_ARCHIVE_RECEIPT_GEOMETRIC_RUNTIME_PLANNING_ARC.md` | Archived | Batch archive | v0.1 | Historical | — |
| `REPO_CONSOLIDATION_RECEIPT_GEOMETRIC_INTELLIGENCE_RUNTIME_v0_1.md` | Archived | Consolidation | v0.1 | Historical | — |
| `REPO_AUDIT_GEOMETRIC_INTELLIGENCE_RUNTIME_v0_1.md` | Archived | Geometric runtime audit | v0.1 | Historical | — |
| `REPO_AUDIT_GEOMETRIC_RUNTIME_PROMOTION_REVIEW_DOSSIER_v0_1.md` | Archived | Promotion review | v0.1 | Historical | — |
| `REPO_AUDIT_AAL_VIZ_GEOMETRIC_RENDERER_*.md` (2) | Archived | AAL-Viz geometric renderer | v0.1 | Historical | — |
| `REPO_AUDIT_ORACLE_GEOMETRIC_ATTACHMENT_*.md` (2) | Archived | Oracle geometric attachment | v0.1 | Historical | — |
| `REPO_AUDIT_YGGDRASIL_GEOMETRIC_ROUTE_*.md` (2) | Archived | YGGDRASIL geometric routes | v0.1 | Historical | — |
| `REPO_AUDIT_METRIC_OPERATOR_*.md` (2) | Archived | Metric operator planning | v0.1 | Historical | — |
| `REPO_AUDIT_CHAMFER_*.md` (14) | Archived | Chamfer planning/implementation arc | v0.1 | Historical | Archive receipts |
| `REPO_ARCHIVE_RECEIPT_CHAMFER_*.md` (5) | Archived | Chamfer archive seals | v0.1 | Historical | — |
| `abraxas_repo_notion_diff_001.json` | Current | Machine-readable Notion diff | 2026 | Companion to markdown audit | — |
| `abraxas_binding_matrix_and_coupling_map_audit_001.json` | Current | Machine-readable binding audit | 2026 | Companion | — |
| `status_pages_deploy_gate_audit_001.json` | Current | Machine-readable deploy gate | 2026 | Companion | — |

## Sprint 001 Layer

Brier Score: 0.34

Sprint 001 adds a technical-debt navigation overlay on top of the existing audit spine.

- [Continuity Lineage Map 001](./CONTINUITY_LINEAGE_MAP_001.md)
- [Repository Organization Sweep Receipt](../REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md)
- Parent Board ID: `3843e8ba-2f5c-8194-80d0-f2c5ffce6254`
- Sprint Hub ID: `3853e8ba-2f5c-8139-a132-ef1eab0ae237`
- Mirror Status: `PARTIAL_MIRROR_COMPLETE`

For release routing see [`../releases/RELEASE_INDEX.md`](../releases/RELEASE_INDEX.md).
