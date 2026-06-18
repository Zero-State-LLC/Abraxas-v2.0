# Post–Merge #744 Spec Stack Schema Audit Continuation Plan

Advisory-only routing after PR #744 and Notion sync receipt lane landed on `main` (2026-06-18).

## Validation baseline (post-#744/#745 merge)

| Check | Command | Result |
|-------|---------|--------|
| Schema audit orchestrator | `python scripts/run_abraxas_spec_stack_schema_audit_receipt.py` | **PASS** |
| Notion sync receipt | `python scripts/run_abraxas_spec_stack_schema_audit_notion_sync_receipt.py` | **PASS** |
| Schema audit tests | `python -m pytest tests/test_abraxas_spec_stack_schema_audit.py -q` | **PASS** |
| Notion sync receipt tests | `python -m pytest tests/test_abraxas_spec_stack_schema_audit_notion_sync_receipt.py -q` | **PASS** |
| Fast CI | `python scripts/run_fast_ci.py` | **PASS** |
| Governance envelope (7 JSON artifacts) | Programmatic check | **PASS** |

## Completed on `main`

| PR | Lane | Deliverable |
|----|------|-------------|
| #744 | Spec stack schema audit | Five domain audits + composite receipt + schemas/runners/tests |
| #745 | Notion sync receipt | `out/sync/abraxas_spec_stack_schema_audit_notion_sync_receipt_001.latest.json` (merged to feature branch; landed on `main` via post-merge PR) |

Prior chain (#735–#742): Notion 6/6 refresh, codegen attestation intake/ODR bridge, repository organization sweep.

## Current posture

- Spec-stack schema audit: **live** — advisory-only, `downstream_status: NOT_COMPUTABLE`
- Shadow binding gaps: **documented** — 6 of 7 cross-spine refs missing; not repaired
- Codegen chain: intake **VALIDATED**; ODR **INTAKE_CLEARED_OBSERVED**; harness impl **denied**
- P130 production hold: **UNCHANGED**
- Runtime/governance: **UNCHANGED**

---

## Phase 1 — Operator manual Notion sync (priority #1)

Copy `notion_sync_surfaces` from `out/sync/abraxas_spec_stack_schema_audit_notion_sync_receipt_001.latest.json` into Notion integration surfaces (manual copy-paste only).

Handoff: [`operator_input/templates/abraxas_spec_stack_schema_audit_notion_sync_handoff.md`](../../operator_input/templates/abraxas_spec_stack_schema_audit_notion_sync_handoff.md)

Checklist: [`docs/notion/GOVERNANCE_V3_NOTION_SYNC.md`](../notion/GOVERNANCE_V3_NOTION_SYNC.md) step 7.

Also pending from #742: P131–P133 stale-spec reconciliation packet.

---

## Phase 2 — Harness implementation authorization (deferred)

Requires separate operator authorization payload:

```yaml
authorize_harness_implementation: true
authorize_harness_execution: false
authorize_production_activation: false
```

Intake clearance (`INTAKE_CLEARED_ONLY`) alone is insufficient.

---

## Phase 3 — Optional doc hygiene (deferred)

- Repair broken links in historical release docs — cataloged in [`DOCUMENTATION_TOPOLOGY_AUDIT_001.md`](../audits/DOCUMENTATION_TOPOLOGY_AUDIT_001.md)
- Close superseded PR #737 manually if still open

---

## Merged PR sequence

| PR | Scope | Status |
|----|-------|--------|
| **#744** | Spec stack schema audit lane | **merged** |
| **#745** | Notion sync receipt | **merged** (feature branch; receipt on `main` via post-merge carry-forward) |

---

## Explicit non-goals

- Runtime implementation of belief graph, ingest, codegen harness, or situation engine
- Creating missing shadow binding JSON files
- Shadow binding promotion or repair execution
- Harness implementation (`core/codegen_shadow_replay_harness.py`)
- P128→P130 canary spine regeneration
- P133 production activation
- Notion API writeback
