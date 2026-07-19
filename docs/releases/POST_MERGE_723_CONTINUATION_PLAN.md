# Post–Merge #723 Continuation Plan

Advisory-only routing after PR #723 landed on `main` (2026-06-18).

For the full implementation specification, see [`POST_MERGE_724_EXTENSIVE_CONTINUATION_PLAN.md`](POST_MERGE_724_EXTENSIVE_CONTINUATION_PLAN.md).

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
| #723 | Continuation plan + doc sync | `POST_MERGE_720_722_CONTINUATION_PLAN`, PLANS/STATUS/audit updates |

Prior chain (#719–#722): operator hold clearance, Oracle shadow impl, runtime shadow wiring plan.

## Current governance posture

- `recommended_next_lane`: **NOT_COMPUTABLE**
- Runtime hold: `shadow_wiring_approved=true`, `mandatory_pre_dispatch_wiring=false`
- Shadow wiring plan: `RUNTIME_INTEGRATION_GATE_SHADOW_WIRING_PLAN_READY` (7 integration points)
- P131: all DROP activation candidates remain held
- `out/research_canary_*` regeneration guardrail: **active**

---

## Phase 1 — Next implementation-eligible lane (PR #724)

**Target:** Runtime integration gate shadow wiring **hooks** (implementation, not planning).

**Pattern:** Mirror [`core/oracle_signal.py`](../core/oracle_signal.py) (#721) — consume upstream advisory artifacts, emit deterministic shadow packet, hardcode authority locks to `false`.

### Proposed deliverables

| File | Purpose |
|------|---------|
| `core/runtime_integration_gate_shadow_wiring_hooks.py` | Build hook packet from plan + hold receipt; one binding per `integration_point_id` |
| `scripts/runtime/run_runtime_integration_gate_shadow_wiring_hooks.py` | Runner |
| `tests/test_runtime_integration_gate_shadow_wiring_hooks.py` | Preconditions, 7 bindings, authority locks |
| `docs/audits/REPO_EXECUTION_RECEIPT_runtime_shadow_wiring_hooks.md` | Advisory execution receipt |
| `out/audit/runtime_integration_gate_shadow_wiring_hooks_001.latest.json` | Generated artifact |
| `core/generated_artifact_registry.py` + `.gitignore` | Registry and artifact exceptions |

### Packet shape (advisory)

- `schema_version`: `RuntimeIntegrationGateShadowWiringHooks.v1`
- `status`: `RUNTIME_INTEGRATION_GATE_SHADOW_WIRING_HOOKS_EMITTED` when plan is `READY` and hold receipt valid
- `integration_point_bindings`: read-only projection refs per integration point from plan
- `mandatory_pre_dispatch_wiring`: `false`
- `authority_locks`: all false (execution, runtime_mutation, queue, scheduler)
- Provenance: `source_plan_hash`, `source_hold_receipt_hash`

### Integration points (from plan)

1. `AAL_VIZ_PROJECTION_SPINE_001`
2. `ABX_CODEGEN_INTELLIGENCE_SPINE_001`
3. `BELIEF_GRAPH_ENGINE_001`
4. `GLOBAL_INGEST_ADAPTER_SPINE_001`
5. `PHASE_PERCOLATION_ENGINE_001`
6. `RESEARCH_SHADOW_REPLAY_ENGINE_001`
7. `SITUATION_RUNTIME_ENGINE_001`

### Validation

```bash
python scripts/runtime/run_runtime_integration_gate_shadow_wiring_hooks.py
python -m pytest tests/test_runtime_integration_gate_shadow_wiring_hooks.py -q
python scripts/runtime/run_runtime_integration_gate_shadow_wiring_plan.py
python scripts/run_fast_ci.py
```

### Out of scope

- Ingest runners, queue, scheduler, or dispatch surfaces
- `mandatory_pre_dispatch_wiring=true`
- Live runtime mutation at any integration point

---

## Phase 2 — Doc sync (post-#724)

After PR #724 merges:

- Move `runtime_integration_gate_shadow_wiring_implementation` from `PLANS.md` `implementation_ready` → `completed`
- Add PR #724 to `POST_2_5_0_CONTINUATION_AUDIT.md` completed lanes
- Update `STATUS.md` if needed

---

## Phase 3 — Optional forks (operator choice; defer by default)

See [`POST_CLEARANCE_OPTIONAL_FORKS.md`](POST_CLEARANCE_OPTIONAL_FORKS.md).

| Fork | Default | Blocker |
|------|---------|---------|
| P132 canary activation | Defer | New lane + P131 validation change + P128→P130 replay |
| v2 hygiene Phase 1 chain | Defer | Master attestation scope + operator ID normalization |
| Tier-3 pipelines (8) | Defer | `NO_GOVERNED_SPEC_BINDING_PRESENT` |
| 91-surface bulk clearance | Defer | No intake consumers; phased per-domain only |

---

## Recommended PR sequence

| PR | Branch | Scope |
|----|--------|-------|
| **#724** | `cursor/runtime-shadow-wiring-impl-1234` | Shadow wiring hooks implementation |
| **#725** | TBD | Doc sync post-#724 |
| **#726+** | TBD | Operator fork choice |

---

## Explicit non-goals

- P128–P130 canary spine regeneration without validated replay
- Live ingest/runtime/queue/scheduler mutation under shadow lanes
- Bulk 91-surface hold clearance via single attestation
- Treating plan/hook artifacts as execution authorization
