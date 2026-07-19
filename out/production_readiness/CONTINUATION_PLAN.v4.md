# Abraxas Production Continuation Plan v4

```yaml
program_id: ABRAXAS_PRODUCTION_CONTINUATION
plan_id: CONTINUATION_PLAN.v4
supersedes: CONTINUATION_PLAN.v3
status: ACTIVE
drafted_at: 2026-07-19
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
| Live fast CI | **exit 0** (prior) | RISK-006 **CLOSED** |
| SUPPORTED interfaces | **4** | `canonical_json`, `run_fast_ci`, `validation_service.v1`, `artifact_and_provenance_service.v0` |
| SUPPORTED services | **2** | validation + artifact provenance |
| Sole-writer findings | residual | hardened advisory |
| Neon allowlist | **present** | `ws5/` RISK-013 **MITIGATING** |
| Boundary fail-closed | **design only, default off** | WP-E |
| Threat model | **v0 Partial** | `ws8/` RISK-014 **MITIGATING** |
| Threat model operator review | **PENDING** | WP-P request artifact |
| Notion linkage | **Partial mapping** | WP-H; RISK-012 **MITIGATING** (writeback residual) |

### Risk board

| ID | Status |
|----|--------|
| RISK-006 | CLOSED |
| RISK-008 | MITIGATING |
| RISK-010 | MITIGATING |
| RISK-011 | MITIGATING |
| RISK-012 | MITIGATING |
| RISK-013 | MITIGATING |
| RISK-014 | MITIGATING |
| RISK-004 | OPEN |

---

## 2. Completed this slice (v4)

| WP | Name | Result |
|----|------|--------|
| **H** | Notion readiness mapping | `ws8/notion_readiness_mapping.v1.json` — durable Notion IDs + repo path table; **no live writeback** |
| **K2** | artifact_and_provenance_service → SUPPORTED | interface + service registry; supported_count=4 |
| **P** | Threat model operator decision request | `ws8/threat_model_operator_decision_request.v0.json` — **PENDING_OPERATOR**, not auto-accepted |

---

## 3. Principles (binding)

Stabilization before expansion · Evidence-gated Done · Small reversible PRs · One canonical source · Fail closed on authority · Deterministic where declared  

Evidence states: `Missing | Partial | Verified | NOT_COMPUTABLE`

---

## 4. Ordered work packages (forward)

| WP | Name | Priority | Exit criteria |
|----|------|----------|----------------|
| **P+** | Operator decision record for ThreatModel.v0 | P0 | Human-authored decision (ACCEPT/REVISE/REJECT/DEFER) |
| **H+** | Notion tracker Evidence/PR writeback | P1 | RISK-012 CLOSED when rows link durable evidence |
| **I** | Production candidate freeze | P0 | Blocked until gates pass |
| **N2** | Soft-gate remediations (optional) | P1 | Optional |

### Deferred

Full 8-service suite · marketplace · fail-closed sole-writer while findings high · autonomous production activation

---

## 5. Production candidate gate (unchanged bar)

Candidate only when: green CI · **operator-reviewed** threat model · SUPPORTED set ≥3 · sole-writer residual accepted · Neon non-control proven · ≥1 SUPPORTED service path · release decision artifact · no unmitigated P0s.

**Until then: `NOT_READY`.**

---

## 6. Operator actions now

1. Review `out/production_readiness/ws8/threat_model.v0.json` + decision request
2. Emit decision record at path hint (if accepting Partial baseline)
3. Link Evidence/PR on Notion Production Readiness Tracker using WP-H mapping
4. Do **not** claim production ready from this plan alone

---

## 7. Related artifacts

| Path | Role |
|------|------|
| `CONTINUATION_PLAN.v4.md` | This plan |
| `CONTINUATION_PLAN.v3.md` | Prior plan |
| `ws8/notion_readiness_mapping.v1.json` | WP-H |
| `ws8/threat_model_operator_decision_request.v0.json` | WP-P |
| `ws8/threat_model.v0.json` | WP-F |
| `ws3/service_registry.v1.json` | SUPPORTED services |
| `ws1/interface_registry_snapshot.v1.json` | SUPPORTED interfaces |
