# Abraxas Production Continuation Plan v3

```yaml
program_id: ABRAXAS_PRODUCTION_CONTINUATION
plan_id: CONTINUATION_PLAN.v3
supersedes: CONTINUATION_PLAN.v2
status: ACTIVE
drafted_at: 2026-07-19
baseline_head_sha: af662db28d79890e40a4f5e9748ce091a6427788
branch: chore/ws0-baseline-live-receipt
pull_request: https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971
evidence_state: Partial
current_readiness_state: NOT_READY
primary_goal: bounded production candidate
authority_mode: operator-controlled
```

Stabilization and release-readiness only. Feature expansion is out of scope.

---

## 1. Current position (evidence)

| Area | State | Evidence |
|------|--------|----------|
| Baseline package | COMPLETE / **Partial** | `baseline/` |
| Live fast CI | **exit 0** | RISK-006 **CLOSED** |
| SUPPORTED interfaces | **2** | `canonical_json`, `run_fast_ci` |
| Sole-writer findings | **~69** | hardened advisory |
| Pure runtime modules | **20** | WP-D batches 1–3 |
| Validation Service | **1 ADVISORY** | `core/services/validation_service.py` |
| Neon allowlist | **present** | `ws5/` RISK-013 **MITIGATING** |
| Boundary fail-closed | **design only, default off** | WP-E |
| Threat model | **v0 Partial** | `ws8/` RISK-014 **MITIGATING** |
| Notion linkage | **Missing** | RISK-012 **OPEN** |

### Risk board

| ID | Status |
|----|--------|
| RISK-006 | CLOSED |
| RISK-008 | MITIGATING |
| RISK-010 | MITIGATING |
| RISK-011 | MITIGATING |
| RISK-013 | MITIGATING |
| RISK-014 | MITIGATING |
| RISK-004 / 012 | OPEN |

### Debt snapshot

| Class | ~Count |
|-------|-------:|
| CORE_BUILDER_OR_HELPER | 48 |
| SKILL_OUT_WRITER | 12 |
| ABX_AFE_WRITER | 6 |
| ORACLE_EXECUTION_WRITER | 2 |
| SCRIPT_NON_RUN_WRITER | 1 |
| RUNTIME_PACKET_WRITER | 0 |

### Completed (v1–v2 track)

A triage · B Validation Service · C service registry · D batches 1–3 · E boundary design · F threat model v0 · G Neon allowlist

---

## 2. Principles (binding)

Stabilization before expansion · Evidence-gated Done · Small reversible PRs · One canonical source · Fail closed on authority · Deterministic where declared  

Evidence states: `Missing | Partial | Verified | NOT_COMPUTABLE`

---

## 3. Ordered work packages (forward)

### This execution slice (v3)

| WP | Name | Priority | Goal | Exit criteria |
|----|------|----------|------|----------------|
| **J** | Artifact & Provenance Service v0 | P1 | Thin service over SUPPORTED `canonical_json` | ADVISORY service + schemas + tests + registry |
| **G+** | Neon allowlist in fast CI (report-only) | P1 | Visibility every PR | Advisory step in `run_fast_ci` (fail-open) |
| **D4** | Optional: 1–2 more pure runtimes if low risk | P0 | Further write-debt reduction | Only if runners exist and tests stay green |

### Next after this slice

| WP | Name | Priority |
|----|------|----------|
| **K** | Third SUPPORTED promotion (Validation Service *or* Artifact Service after soak) | P0 |
| **N** | Soft CI gate audit | P0 |
| **H** | Notion readiness linkage | P1 (operator) |
| **O** | Recovery drill v0 | P0 |
| **I** | Production candidate freeze | P0 (blocked until gates pass) |

### Deferred

Full 8-service suite · marketplace · fail-closed sole-writer while findings ≫ 0 · autonomous production activation

---

## 4. Recommended next three PRs (after this slice)

1. **K** — Promote one ADVISORY service to SUPPORTED with ownership + contract tests  
2. **N** — Soft CI gate audit artifact  
3. **H/O** — Notion links + recovery drill (can parallelize with operator)

---

## 5. Production candidate gate (unchanged bar)

Candidate only when: green CI · operator-reviewed threat model · SUPPORTED set ≥3 preferred · sole-writer residual accepted · Neon non-control proven · ≥1 SUPPORTED service path · release decision artifact · no unmitigated P0s.

**Until then: `NOT_READY`.**

---

## 6. Immediate execution (this session)

```text
1. Land CONTINUATION_PLAN.v3.md
2. Implement WP-J Artifact & Provenance Service v0
3. Wire neon allowlist check as report-only fast-CI step (G+)
4. Refresh registries/receipts; live CI; push PR #971
```

---

## 7. Related artifacts

| Path | Role |
|------|------|
| `CONTINUATION_PLAN.v3.md` | This plan |
| `CONTINUATION_PLAN.v2.md` | Prior plan |
| `baseline/` | WS0 |
| `ws1/` | Registry / boundary / sole-writer |
| `ws2/` | Writer triage / WP-D / WP-E design |
| `ws3/` | Service registry |
| `ws5/` | Neon allowlist |
| `ws8/` | Threat model v0 |
