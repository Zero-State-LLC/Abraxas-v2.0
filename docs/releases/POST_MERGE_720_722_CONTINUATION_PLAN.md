# Post–Merge #720–#722 Continuation Plan

Advisory-only routing after PR #720–#722 landed on `main` (2026-06-18).

## Validation baseline (post-merge)

| Check | Command | Result |
|-------|---------|--------|
| Fast CI | `python scripts/run_fast_ci.py` | **PASS** |
| Canon resume | `python scripts/run_canon_resume_state.py` | **PASS** |
| Continuation frontier | `python scripts/run_continuation_frontier_reconciliation.py` | **PASS** (`NOT_COMPUTABLE`) |
| Gap backlog | `python Scripts/run_global_pipeline_gap_backlog.py` | **PASS** |
| Bulk disposition | `out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json` | `authority_grant_count=0` |

## Completed on `main`

| PR | Lane | Deliverable |
|----|------|-------------|
| #720 | Audit sync | `POST_2_5_0_CONTINUATION_AUDIT`, PLANS/STATUS, bulk disposition refresh |
| #721 | Oracle shadow physical implementation | `core/oracle_signal.py` auth-record-bound shadow processing packet |
| #722 | Runtime shadow wiring plan | 7 integration points, advisory plan artifacts |

## Current governance posture

- `recommended_next_lane`: **NOT_COMPUTABLE**
- Oracle gap backlog: **AUTHORIZED_ADVISORY_SHADOW** (P0)
- Runtime hold: `shadow_wiring_approved=true`, `mandatory_pre_dispatch_wiring=false`
- P131: all DROP activation candidates remain held
- `out/research_canary_*` regeneration guardrail: **active**

---

## Phase 1 — Next implementation-eligible lane (PR #724-class)

**Target:** Runtime integration gate shadow wiring **implementation** (hooks only, not live dispatch).

**Source:** `out/audit/runtime_integration_gate_shadow_wiring_plan_001.latest.json`

- Status: `RUNTIME_INTEGRATION_GATE_SHADOW_WIRING_PLAN_READY`
- Integration points: 7 (`AAL_VIZ_PROJECTION_SPINE_001` through `SITUATION_RUNTIME_ENGINE_001`)
- `recommended_next_action`: prepare additive shadow wiring implementation PR per integration point

**Scope:**

1. Document shadow wiring hooks per `integration_point_id`
2. Add read-only projection bindings only
3. Verify authority locks remain false after wiring
4. Extend hold receipt / plan consumer tests

**Preconditions:**

- Hold receipt on `main`: `valid_for_runtime_wiring=true`
- Plan artifact on `main`
- No operator payload change required (default: `APPROVE_SHADOW_WIRING_ONLY`)

**Validation:**

```bash
python scripts/runtime/run_runtime_integration_gate_shadow_wiring_plan.py
python -m pytest tests/test_runtime_integration_gate_shadow_wiring_plan.py -q
python scripts/run_fast_ci.py
```

**Out of scope:**

- `mandatory_pre_dispatch_wiring=true` without explicit operator payload change
- Live dispatch, queue mutation, scheduler mutation, runtime execution authority

---

## Phase 2 — Doc sync (included in this PR)

- Move `oracle_signal_shadow_physical_implementation` and `runtime_integration_gate_shadow_wiring_plan` from `PLANS.md` `implementation_ready` → `completed`
- Add PR #721/#722 to `POST_2_5_0_CONTINUATION_AUDIT.md` completed lanes
- Update `STATUS.md` product-version note (#720–#722 merged)

---

## Phase 3 — Optional forks (operator choice; defer by default)

See [`POST_CLEARANCE_OPTIONAL_FORKS.md`](POST_CLEARANCE_OPTIONAL_FORKS.md).

| Fork | Default | Blocker |
|------|---------|---------|
| P132 canary activation | Defer | New lane + P131 validation change + P128→P130 replay |
| v2 hygiene Phase 1 chain | Defer | Master attestation scope + operator ID normalization |
| Tier-3 pipelines (8) | Defer | `NO_GOVERNED_SPEC_BINDING_PRESENT` |
| 91-surface bulk clearance | Defer | No intake consumers; phased per-domain only |

Select one fork explicitly in master attestation `clearance_scope` or via separate governed operator decision record before implementation begins.

---

## Recommended PR sequence

| PR | Branch | Scope |
|----|--------|-------|
| **#723** | `cursor/post-merge-continuation-plan-1234` | This plan + doc sync |
| **#724** | `cursor/runtime-shadow-wiring-impl-1234` | Shadow wiring hooks per integration point |
| **#725+** | TBD | Operator fork choice (P132 / v2 hygiene / tier-3 spec) |

---

## Explicit non-goals

- P128–P130 canary spine regeneration without validated replay
- Live ingest/runtime/queue/scheduler mutation under shadow lanes
- Bulk 91-surface hold clearance via single attestation
- Treating gap backlog or bulk disposition as authority grant
