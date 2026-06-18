# Post–Merge #738 Codegen Attestation Continuation Plan

Advisory-only routing after PR #738 landed on `main` (2026-06-18). **Phase 1 complete via PR #739 merge.**

## Validation baseline (post-#739 merge)

| Check | Command | Result |
|-------|---------|--------|
| Fast CI | `python scripts/run_fast_ci.py` | **PASS** |
| Codegen attestation payload | `operator_input/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json` | **CLEARED** (`OPERATOR_ATTESTATION_INTAKE_CLEARED`) |
| Intake gate | `python scripts/run_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate.py` | **VALIDATED** (`INTAKE_CLEARED_ONLY`) |
| Bulk disposition | `out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json` | `authority_grant_count=0` |

## Completed on `main`

| PR / Lane | Deliverable |
|-----------|-------------|
| #738 | Post-merge #736–#737 audit closure |
| #739 | Operator payload cleared; intake gate **VALIDATED** |

Prior chain (#735–#737): Notion 6/6 stale-spec refresh, audit refresh, codegen attestation template.

## Current posture

- Payload status: `OPERATOR_ATTESTATION_INTAKE_CLEARED`
- `attestation.external_attestation_received`: **true**
- `attestation.operator_acceptance`: **ACCEPTED**
- Intake gate: **VALIDATED**; `downstream`: **INTAKE_CLEARED_ONLY**
- ODR review: **stale** — bridge to intake gate pending (#741)
- P130 production hold: **UNCHANGED**
- Harness implementation: **denied** (`harness_implementation_authorized=false`)

---

## Phase 1 — Operator external attestation fill — **COMPLETE (#739)**

Operator envelope cleared at `operator_input/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json`. Intake gate validates with `INTAKE_CLEARED_ONLY` downstream. Harness implementation remains denied.

---

## Phase 2 — Operator manual Notion sync (priority #1)

Unchanged from [`POST_MERGE_735_CONTINUATION_PLAN.md`](POST_MERGE_735_CONTINUATION_PLAN.md). Copy `stale_lane_records` from `out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json` into Notion Canon Spine (manual copy-paste only).

---

## Phase 3 — Future repo lanes

| Lane | Trigger |
|------|---------|
| ODR review intake bridge | Wire ODR review to validated intake gate (#741) |
| Harness implementation | Separate authorization record required; not auto-unlocked |

See [`POST_MERGE_739_INTAKE_CLEARED_CONTINUATION_PLAN.md`](POST_MERGE_739_INTAKE_CLEARED_CONTINUATION_PLAN.md) for routing detail.

---

## Deferred / forbidden

| Lane | Status |
|------|--------|
| P133 production activation | Deferred — separate governed design |
| P128→P130 spine regeneration | **Forbidden** |
| Harness implementation from payload alone | **Forbidden** |
| Notion API writeback | **Forbidden** |

---

## Explicit non-goals

- Auto-create operator decision records from draft payload
- Enable shadow replay execution without separate authorization
- Treat draft envelope as harness implementation authorization
- Regenerate `out/research_canary_*` artifacts
