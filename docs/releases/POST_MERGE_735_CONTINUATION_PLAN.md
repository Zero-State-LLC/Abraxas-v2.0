# Post–Merge #735 Continuation Plan

Advisory-only routing after PR #735 landed on `main` (2026-06-18).

## Validation baseline (post-merge)

| Check | Command | Result |
|-------|---------|--------|
| Fast CI | `python scripts/run_fast_ci.py` | **PASS** |
| Canon resume | `python scripts/run_canon_resume_state.py` | **PASS** |
| Continuation frontier | `python scripts/run_continuation_frontier_reconciliation.py` | **PASS** (`CONTINUATION_FRONTIER_RECONCILIATION_EMITTED_ADVISORY_ONLY`) |
| Notion stale-spec packet | `out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json` | `NOTION_P131_P133_STALE_SPEC_RECONCILIATION_PACKET_READY` |
| Bulk disposition | `out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json` | `authority_grant_count=0` |

## Completed on `main`

| PR | Lane | Deliverable |
|----|------|-------------|
| #735 | Notion P131–P133 stale-spec refresh (6/6 pilot) | P131/P132 `repo_truth` updated; continuation frontier reasons refreshed; operator manual copy-paste packet ready |

Prior chain (#730–#734): 6/6 advisory shadow pilot, P101/P102 research-fold authorization packet.

## Current governance posture

- `recommended_next_lane`: **NOT_COMPUTABLE**
- P130 hold: formal production hold unchanged; advisory shadow **6/6 complete**
- Notion reconciliation: packet refreshed; `notion_writeback_allowed=false`; `STALE_NOTION_SPEC` count unchanged (3)
- Codegen harness: `ABX_CODEGEN_SHADOW_REPLAY_HARNESS_BLOCKED`; operator attestation required
- `out/research_canary_*` regeneration guardrail: **active**

---

## Phase 1 — Operator manual Notion sync (priority #1)

**Target:** Copy refreshed stale-spec packet into Notion Canon Spine.

**Source:** `out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json` → `stale_lane_records`

**Procedure:** Per [`docs/notion/GOVERNANCE_V3_NOTION_SYNC.md`](../notion/GOVERNANCE_V3_NOTION_SYNC.md) — manual copy-paste only; no API writeback.

| Lane | Repo truth (6/6 pilot) |
|------|------------------------|
| P131 | Operator decision record implemented; 6/6 per-candidate advisory shadow approval supported |
| P132 | Advisory shadow activation record implemented (6/6 candidates approved) |
| P133 | Production lane deferred (`NOT_COMPUTABLE`) |

---

## Phase 2 — Codegen harness attestation intake prep (priority #2)

**Target:** Operator attestation template for shadow replay harness activation.

**Blocker:** `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_review_001.latest.json` routes to `NOT_COMPUTABLE` until external operator attestation.

**Validation blockers (dry run):**
- `operator_identity_not_attested`
- `operator_decision_not_attested`
- `operator_rationale_not_attested`
- `operator_signature_not_attested`
- `operator_evidence_bundle_not_attested`

**Out of scope:** `core/codegen_shadow_replay_harness.py` creation, harness activation, decision-record auto-creation, Notion API writeback.

---

## Phase 3 — Deferred lanes

| Lane | Status |
|------|--------|
| P133 production activation | Separate governed design; `execution_authority=true` not implemented |
| P128→P130 spine regeneration | **Forbidden** — guardrail active |
| Tier-3 pipelines (8) | `NO_GOVERNED_SPEC_BINDING_PRESENT` |
| Archive P52→P64 re-seal | Forbidden without operator lane |

---

## Recommended PR sequence

| PR | Branch | Scope |
|----|--------|-------|
| **#736** | `cursor/post-merge-735-audit-refresh-1234` | Post-merge audit + continuation plan |
| **#737** | `cursor/codegen-shadow-replay-attestation-intake-1234` | Codegen operator attestation intake template |

---

## Explicit non-goals

- P128–P130 canary spine regeneration
- Notion API writeback or GitHub writeback automation
- P133 production activation implementation
- Treating advisory shadow pilot completion as production activation authority
