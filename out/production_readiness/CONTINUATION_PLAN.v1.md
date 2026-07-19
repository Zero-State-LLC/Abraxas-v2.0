# Abraxas Production Continuation Plan v1

```yaml
program_id: ABRAXAS_PRODUCTION_CONTINUATION
plan_id: CONTINUATION_PLAN.v1
status: ACTIVE
evidence_state: Partial
current_readiness_state: NOT_READY
primary_goal: bounded production candidate
authority_mode: operator-controlled
```

## 0. Current verified position (as of branch head)

| Area | State | Evidence |
|------|--------|----------|
| WS0 baseline package | COMPLETE package; evidence **Partial** | `out/production_readiness/baseline/` |
| Live fast CI | **exit 0** (RISK-006 CLOSED) | `validation_receipt.v1.json` |
| Interface registry | 32 entries; **SUPPORTED=2** | `canonical_json`, `run_fast_ci` |
| Boundary advisory | Report-only in fast CI; 0 findings after allow-list | RISK-008 MITIGATING |
| Sole-writer advisory | Hardened heuristic; **~138** findings | RISK-008 MITIGATING |
| Service layer | **Missing** | RISK-010 OPEN |
| Threat model | **Missing** | RISK-014 OPEN |
| Notion linkage | **Missing** | RISK-012 OPEN |
| Neon Genie allowlist | **Missing** | RISK-013 OPEN |

**Decision rule:** Do not claim production ready. Optimize for enforceable contracts and evidence.

## 1. Principles (unchanged)

1. Stabilization before expansion  
2. Evidence-gated completion (`Verified` only with linked evidence)  
3. Small reversible changes  
4. One canonical source per concern  
5. Fail closed on authority; advisory on analysis until promoted  
6. Deterministic where declared  

## 2. Ordered work packages

Proceed in order unless marked parallel-safe.

| WP | Name | Priority | Goal | Exit criteria |
|----|------|----------|------|----------------|
| **A** | Writer debt triage | P0 | Classify remaining sole-writer findings; document consolidation decisions | Machine report + counts by class; no fail-closed yet |
| **B** | Validation Service v1 spike | P1 | First versioned service facade (WS3) without internal imports for consumers | Request/response/error schemas; unit+contract tests; registry entry ADVISORY |
| **C** | Service registry seed | P1 | Canonical service registry artifact | Lists Validation Service + candidates; no competing registries |
| **D** | Core writer consolidation (batch 1) | P0 | Reduce highest-risk core runtime writers or allow-list with ownership | finding_count trend down OR explicit ALLOWLISTED_RUNTIME class — **BATCH1 DONE** (brier/canary/drift/promotion/scheduler) |
| **E** | Report-only → fail-closed design | P0 | Criteria + env flag for boundary only (not sole-writer) | Design receipt; flag default off |
| **F** | Threat model v0 | P0 | Minimal threat model for production candidate boundary | `threat_model.v0` artifact + open risks — **DONE (Partial)** |
| **G** | Neon Genie allowlist | P1 | Capability allowlist + governance non-control proof | Allowlist file + CI advisory check |
| **H** | Notion readiness links | P1 | Operator-linked tracker | RISK-012 CLOSED or NOT_COMPUTABLE with reason |
| **I** | Production candidate freeze | P0 | Bounded slice + release decision artifact | Operator decision recorded |

### Parallel-safe with A–C

- Documentation of fail-closed promotion criteria (already in WS1 progress receipt)  
- Notion linkage (operator-owned)  
- Observability inventory (read-only)

### Explicitly deferred (P2/P3)

- Full eight-service implementation  
- Marketplace / consumer UI  
- Fail-closed sole-writer while `core/` has 100+ write hits  
- Autonomous production activation  

## 3. This execution slice

**In scope now:**

1. Land this plan as a tracked artifact under `out/production_readiness/`.  
2. **WP-A:** Writer debt triage generator + report.  
3. **WP-B/C:** Validation Service v1 + service registry seed.

**Out of scope now:**

- Fail-closed CI gates  
- Threat model  
- Neon allowlist  
- Mass core refactors  

## 4. Standard error model (services)

```json
{
  "status": "ERROR",
  "error_class": "SCHEMA_INVALID",
  "message": "Request failed validation.",
  "retryable": false,
  "operator_action_required": true,
  "execution_id": "<execution-id>",
  "service_id": "<service-id>",
  "service_version": "<version>",
  "evidence": []
}
```

## 5. Success metrics (near-term)

| Metric | Now | Target after this slice |
|--------|-----|-------------------------|
| SUPPORTED interfaces | 2 | 2 (no forced promotion) |
| Sole-writer findings | ~138 | Classified; raw count may stay ~138 |
| Service facades | 0 | 1 ADVISORY (validation) |
| Service registry | missing | seed present |
| Live fast CI | green | green |
| Production ready | no | no |

## 6. Rollback

- Revert PR commits for this slice  
- Plan artifact is additive documentation/receipt  
- Validation Service is new package; no existing consumers  

## 7. Next after this slice

1. ~~WP-D batch 1~~ — brier/canary/drift/canary_promotion/canary_scheduler  
2. ~~WP-D batch 2~~ — forecast/oracle/sandbox/state/operator_queue/external_action/overlay_observability  
3. ~~WP-F threat model v0~~ — Partial security baseline  
4. WP-D batch 3 / WP-G Neon allowlist / WP-H Notion links  
