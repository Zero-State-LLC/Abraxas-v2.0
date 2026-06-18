# Post–Merge #738 Codegen Attestation Continuation Plan

Advisory-only routing after PR #738 landed on `main` (2026-06-18).

## Validation baseline (post-merge)

| Check | Command | Result |
|-------|---------|--------|
| Fast CI | `python scripts/run_fast_ci.py` | **PASS** (expected on branch) |
| Codegen attestation payload | `operator_input/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json` | **OBSERVED** (`DRAFT_PENDING_EXTERNAL_ATTESTATION`) |
| Intake gate | `python scripts/run_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate.py` | **BLOCKED** (`ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE_BLOCKED`) |
| Bulk disposition | `out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json` | `authority_grant_count=0` |

## Completed on `main`

| PR / Lane | Deliverable |
|-----------|-------------|
| #738 | Post-merge #736–#737 audit closure |
| Payload intake | Draft operator envelope saved; intake gate emitted BLOCKED |

Prior chain (#735–#737): Notion 6/6 stale-spec refresh, audit refresh, codegen attestation template.

## Current posture

- Payload status: `OPERATOR_ATTESTATION_INTAKE_CLEARED`
- `attestation.external_attestation_received`: **true**
- `attestation.operator_acceptance`: **ACCEPTED**
- Intake gate: **VALIDATED**; `downstream`: **INTAKE_CLEARED_ONLY**
- P130 production hold: **UNCHANGED**
- Harness implementation: **denied** (`harness_implementation_authorized=false`)

---

## Phase 1 — Operator external attestation fill (priority #2)

**Target:** Complete the draft envelope at `operator_input/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json`.

**Operator fill checklist:**

| Field | Current | Required for intake validation |
|-------|---------|--------------------------------|
| `attestation.external_attestation_received` | `false` | `true` |
| `attestation.external_attestation_source` | `NOT_PROVIDED` | External source identifier |
| `attestation.external_attestation_reference` | `NOT_PROVIDED` | Reference link or hash |
| `attestation.external_attestation_summary` | `NOT_PROVIDED` | Human summary |
| `attestation.operator_review_complete` | `false` | `true` |
| `attestation.operator_acceptance` | `PENDING` | Non-PENDING acceptance value |
| `seal.payload_status` | `DRAFT_PENDING_EXTERNAL_ATTESTATION` | Updated when complete |

**Preflight envelope shape:**

```bash
python scripts/preflight_abx_codegen_shadow_replay_harness_operator_attestation_payload.py
```

**Re-run intake gate after fill:**

```bash
python scripts/run_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate.py
```

Passing intake validation does **not** auto-authorize harness implementation or grant execution authority.

---

## Phase 2 — Operator manual Notion sync (priority #1)

Unchanged from [`POST_MERGE_735_CONTINUATION_PLAN.md`](POST_MERGE_735_CONTINUATION_PLAN.md). Copy `stale_lane_records` from `out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json` into Notion Canon Spine (manual copy-paste only).

---

## Phase 3 — Future repo lanes (after external attestation)

| Lane | Trigger |
|------|---------|
| Intake gate re-observation | Operator fills payload; re-run intake gate |
| ODR review re-observation | Only after intake gate VALIDATED (future governed lane) |
| Harness implementation | Separate authorization record required; not auto-unlocked |

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
