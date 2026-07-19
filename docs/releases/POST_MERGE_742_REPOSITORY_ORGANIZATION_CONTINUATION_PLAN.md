# Post–Merge #742 Repository Organization Continuation Plan

Advisory-only routing after PR #742 landed on `main` (2026-06-18).

## Validation baseline (post-#742 merge)

| Check | Command | Result |
|-------|---------|--------|
| Fast CI | `python scripts/run_fast_ci.py` | **PASS** |
| Navigation index links | `python -m pytest tests/test_repository_organization_indexes_001.py -q` | **PASS** |
| Codegen attestation intake gate | `python scripts/codegen/run_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate.py` | **VALIDATED** (`INTAKE_CLEARED_ONLY`) |
| ODR review | `python scripts/codegen/run_abx_codegen_shadow_replay_harness_operator_decision_record_review.py` | **INTAKE_CLEARED_OBSERVED** |
| Bulk disposition | `out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json` | `authority_grant_count=0` |

## Completed on `main`

| PR | Lane | Deliverable |
|----|------|-------------|
| #742 | Repository organization sweep 001 | START_HERE, expanded INDEX, AUDIT/RELEASE/ARTIFACT/TEST indexes, sweep receipt, operator_input README |

Prior chain (#735–#741): Notion 6/6 refresh, codegen attestation intake/ODR bridge, audit closures.

## Current posture

- Navigation layer: **live** — [`docs/START_HERE.md`](../START_HERE.md) is primary entrypoint
- Codegen chain: intake **VALIDATED**; ODR **INTAKE_CLEARED_OBSERVED**; harness impl **denied**
- P130 production hold: **UNCHANGED**
- Runtime/governance: **UNCHANGED**

---

## Phase 1 — Operator manual Notion sync (priority #1)

Copy `stale_lane_records` from `out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json` into Notion Canon Spine (manual copy-paste only).

Checklist: [`docs/notion/GOVERNANCE_V3_NOTION_SYNC.md`](../notion/GOVERNANCE_V3_NOTION_SYNC.md).

---

## Phase 2 — Harness implementation authorization (deferred)

Requires separate operator authorization payload:

```yaml
authorize_harness_implementation: true
authorize_harness_execution: false
authorize_production_activation: false
```

Intake clearance (`INTAKE_CLEARED_ONLY`) alone is insufficient. Optional: replace `FILL_WITH_*` placeholders in codegen payload before harness authorization lane.

---

## Phase 3 — Optional doc hygiene (deferred)

- Repair broken links in historical release docs (FULL_FEATURES, POST_MERGE_724) — cataloged in [`DOCUMENTATION_TOPOLOGY_AUDIT_001.md`](../audits/DOCUMENTATION_TOPOLOGY_AUDIT_001.md)
- Close superseded PR #737 manually if still open

---

## Merged PR sequence

| PR | Scope | Status |
|----|-------|--------|
| **#742** | Repository organization sweep | **merged** |

---

## Explicit non-goals

- Harness implementation (`core/codegen_shadow_replay_harness.py`)
- P128→P130 canary spine regeneration
- P133 production activation
- Notion API writeback
