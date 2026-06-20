# Artifact Index

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
