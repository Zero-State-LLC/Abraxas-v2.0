# Post–Merge #747 Spec Stack Routing Closure Continuation Plan

Advisory-only closure after PR #747 landed `POST_MERGE_746` routing on `main` (2026-06-19). Operator priorities unchanged; this doc confirms canonical routing only.

## Validation baseline (post-#747)

| Check | Command | Result |
|-------|---------|--------|
| Fast CI | `python scripts/run_fast_ci.py` | **PASS** |
| Schema audit orchestrator | `python scripts/codegen/run_abraxas_spec_stack_schema_audit_receipt.py` | **PASS** |
| Notion sync receipt | `python scripts/codegen/run_abraxas_spec_stack_schema_audit_notion_sync_receipt.py` | **PASS** |
| Governance envelope (7 JSON artifacts) | Programmatic check | **PASS** |
| `POST_MERGE_746` on `main` | File presence | **CONFIRMED** |
| RELEASE_INDEX routing | `docs/releases/RELEASE_INDEX.md` | Points to POST_MERGE_746 as reference routing body |

## Completed on `main`

| PR | Scope |
|----|-------|
| #747 | Routing alignment — POST_MERGE_746 + RELEASE_INDEX + POST_2_5_0 + START_HERE |

Prior chain (#744–#746): spec-stack schema audit, Notion sync receipt, handoff template and carry-forward.

## Current posture (unchanged from POST_MERGE_746)

- Spec-stack audit: **live**, advisory-only
- Notion handoff: **repo-ready**, operator copy-paste **pending**
- Harness implementation: **denied** until separate authorization payload
- P130 hold: **unchanged**
- Shadow binding gaps: **documented** — 6 of 7 cross-spine refs missing; not repaired

---

## Phase 1 — Operator manual Notion sync (priority #1, unchanged)

Carry forward dual workstreams from [`POST_MERGE_746_SPEC_STACK_SCHEMA_AUDIT_NOTION_HANDOFF_CONTINUATION_PLAN.md`](POST_MERGE_746_SPEC_STACK_SCHEMA_AUDIT_NOTION_HANDOFF_CONTINUATION_PLAN.md):

### 1a. Spec-stack schema audit (six surfaces)

- Source: `out/sync/abraxas_spec_stack_schema_audit_notion_sync_receipt_001.latest.json`
- Handoff: [`operator_input/templates/abraxas_spec_stack_schema_audit_notion_sync_handoff.md`](../../operator_input/templates/abraxas_spec_stack_schema_audit_notion_sync_handoff.md)
- Checklist: [`docs/notion/GOVERNANCE_V3_NOTION_SYNC.md`](../notion/GOVERNANCE_V3_NOTION_SYNC.md) step 7

### 1b. P131–P133 stale-spec reconciliation packet

- Source: `out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json`
- Checklist: [`docs/notion/GOVERNANCE_V3_NOTION_SYNC.md`](../notion/GOVERNANCE_V3_NOTION_SYNC.md) steps 1–6 context

---

## Phase 2 — Harness implementation authorization (deferred)

Same payload requirement as POST_MERGE_746:

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
| **#745** | Notion sync receipt source | **merged** (feature branch) |
| **#746** | Notion handoff carry-forward + routing docs | **merged** |
| **#747** | POST_MERGE_746 routing alignment on `main` | **merged** |

---

## Explicit non-goals

- New implementation lanes
- Notion API writeback
- Shadow binding repair or promotion
- P128→P130 canary spine regeneration
- Harness implementation without separate authorization payload
