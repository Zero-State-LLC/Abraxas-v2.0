# Abraxas Production Continuation Plan v6

```yaml
program_id: ABRAXAS_PRODUCTION_CONTINUATION
plan_id: CONTINUATION_PLAN.v6
supersedes: CONTINUATION_PLAN.v5
status: ACTIVE
drafted_at: 2026-07-19
branch: chore/ws0-baseline-live-receipt
pull_request: https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971
evidence_state: Partial
current_readiness_state: NOT_READY
primary_goal: bounded production candidate
authority_mode: operator-controlled
```

Stabilization and freeze-prep only. Feature expansion is out of scope.  
**No autonomous production activation.**

---

## 1. Current position (evidence)

| Area | State | Evidence |
|------|--------|----------|
| Live CI | green locally / CI pending or green | RISK-006 path; PR #971 |
| SUPPORTED interfaces | **4** | `ws1/interface_registry_snapshot.v1.json` |
| SUPPORTED services | **2** | validation + artifact provenance |
| Threat model | Partial + **ACCEPT_PARTIAL_BASELINE** | `ws8/threat_model_operator_decision_record.v0.json` |
| Notion linkage | Live writeback **Partial** | `ws8/notion_writeback_receipt.v1.json` |
| Soft CI | keep soft (N2) | `ws6/soft_ci_gate_disposition.v1.json` |
| Sole-writer findings | **~72** advisory | `ws1/sole_writer_advisory_report.v1.json` |
| Neon allowlist | present + advisory CI | `ws5/` |
| Release decision | **missing → this slice** | WP-I |
| Overall | **`NOT_READY`** | — |

### Risk board

| ID | Status | Notes |
|----|--------|--------|
| RISK-006 | CLOSED when live green attached | Baseline generator-gated |
| RISK-008 | MITIGATING | Report-only boundary/sole-writer |
| RISK-010 / 011 | MITIGATING | Services + SUPPORTED advancing |
| RISK-012 | MITIGATING | Writeback done; Verified DoD open |
| RISK-013 | MITIGATING | Neon allowlist |
| RISK-014 | MITIGATING | Threat Partial accepted |
| RISK-004 | OPEN (P1) | Historical archive surfaces |

---

## 2. Completed (v1–v5 track)

A–G, J, K, K2, N, N2, O, H, H+, P, P+ · pure runtime consolidations · CONTINUATION_PLAN.v1–v5

---

## 3. This execution slice (v6)

| WP | Name | Priority | Goal | Exit criteria |
|----|------|----------|------|----------------|
| **Q** | Sole-writer residual acceptance | P0 | Set threshold + record residual as known debt (not fail-closed) | `sole_writer_residual_acceptance.v1` |
| **GATE** | Freeze gate scorecard | P0 | Evaluate WP-I criteria 1–8 honestly | `freeze_gate_scorecard.v1` Partial/Verified per gate |
| **I** | Release decision + surface freeze inventory | P0 | Emit operator-controlled decision | `release_decision.v1` with **RELEASE_HELD** (unless all gates true AND operator asked for candidate) |

### Explicit non-goals this slice

- Fail-closed sole-writer or boundary  
- CANDIDATE_APPROVED / production activation  
- Feature expansion / marketplace / full 8-service suite  
- Closing RISK-004 archive debt  

---

## 4. Principles (binding)

Stabilization before expansion · Evidence-gated Done · Small reversible PRs · One canonical source · Fail closed on authority · Deterministic where declared  

Evidence states: `Missing | Partial | Verified | NOT_COMPUTABLE`  

Release decision codes (fail-closed vocabulary):

| Code | Meaning |
|------|---------|
| `RELEASE_HELD` | Hold; do not ship candidate |
| `OPERATOR_REVIEW_REQUIRED` | Human review incomplete |
| `NOT_COMPUTABLE` | Evidence insufficient |
| `CANDIDATE_APPROVED` | Bounded candidate only (operator-only; not used without full gates) |

---

## 5. Production candidate gate (scorecard)

| # | Criterion | Target this slice |
|---|-----------|-------------------|
| 1 | Live CI green on pinned SHA | Score from evidence |
| 2 | Threat model operator-reviewed | PASS if ACCEPT_PARTIAL_BASELINE |
| 3 | SUPPORTED set ≥ 1 (prefer ≥3) | PASS if supported_count ≥ 3 |
| 4 | Sole-writer residual accepted or under threshold | PASS only after WP-Q |
| 5 | Neon non-control (allowlist + tests) | PASS if allowlist + check present |
| 6 | ≥1 SUPPORTED service path | PASS if supported services ≥ 1 |
| 7 | Release decision artifact | PASS when WP-I emits decision |
| 8 | No unmitigated OPEN P0 | PASS if all P0 CLOSED or MITIGATING |

**Candidate freeze (CANDIDATE_APPROVED) requires all PASS and explicit operator request.**  
This slice expects **RELEASE_HELD** with documented surface inventory.

---

## 6. Immediate execution order

```text
1. Land CONTINUATION_PLAN.v6.md
2. WP-Q sole-writer residual acceptance (threshold + known-debt record)
3. WP-GATE freeze gate scorecard
4. WP-I release_decision RELEASE_HELD + supported surface inventory
5. Refresh registries/receipts; focused tests; push PR #971
```

---

## 7. Execution result (this session)

| WP | Outcome |
|----|---------|
| **Q** | `ACCEPT_KNOWN_RESIDUAL` — finding_count under threshold 100; fail-closed **off** |
| **GATE** | **8/8 PASS** after live fast CI exit 0 + residual + release artifact |
| **I** | **`RELEASE_HELD`** (explicit) — scorecard may recommend CANDIDATE_APPROVED, but decision remains HELD without operator deploy request |
| Live CI | exit 0 attached to baseline receipt |
| Activation | **false** · readiness **NOT_READY** |

Scorecard `recommended_release_code` may read `CANDIDATE_APPROVED` when all gates pass.  
**Binding decision is `release_decision.v1.json` → RELEASE_HELD** until an operator re-emits CANDIDATE_APPROVED with deploy intent.

### Next (post-v6)

| WP | Notes |
|----|--------|
| **I+** | Optional operator re-decision to CANDIDATE_APPROVED (bounded only) |
| **H++** | Notion checkpoint Verified DoD |
| **D4** | Optional more sole-writer consolidation |
| **Prod** | Explicit production activation path — **not** this program until separate authority |

---

## 8. Related artifacts

| Path | Role |
|------|------|
| `CONTINUATION_PLAN.v6.md` | This plan |
| `ws1/sole_writer_residual_acceptance.v1.json` | WP-Q |
| `ws8/freeze_gate_scorecard.v1.json` | WP-GATE |
| `ws8/release_decision.v1.json` | WP-I |
| `ws8/supported_surface_freeze_inventory.v1.json` | WP-I companion |
