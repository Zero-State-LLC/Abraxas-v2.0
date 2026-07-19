# Abraxas Production Continuation Plan v9

```yaml
program_id: ABRAXAS_PRODUCTION_CONTINUATION
plan_id: CONTINUATION_PLAN.v9
supersedes: CONTINUATION_PLAN.v8
status: ACTIVE
drafted_at: 2026-07-19
branch: chore/ws0-baseline-live-receipt
pull_request: https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971
evidence_state: Partial
current_readiness_state: CANDIDATE_HELD_FOR_OPERATOR_DEPLOY
primary_goal: stabilize candidate track; reduce residual debt; never silent-activate
authority_mode: operator-controlled
production_activation_authorized: false
release_decision: CANDIDATE_APPROVED
deploy_held: true
deploy_readiness: NO_GO
activation_gate: DENIED
```

**Stabilization only.** Feature expansion and production go-live are out of scope unless a later plan is explicitly operator-mandated.

**Binding docs:** [`README.md`](README.md) · [`docs/production_readiness/ENGINEERING_GUIDEBOOK.md`](../../docs/production_readiness/ENGINEERING_GUIDEBOOK.md)

---

## 1. Current position (evidence)

| Area | State | Evidence |
|------|--------|----------|
| Freeze scorecard | **8/8 PASS** | `ws8/freeze_gate_scorecard.v1.json` |
| Release decision | **CANDIDATE_APPROVED** · `deploy_held=true` | `ws8/release_decision.v1.json` |
| Readiness state | `CANDIDATE_HELD_FOR_OPERATOR_DEPLOY` | same |
| Production activation | **DENIED** / false | `ws8/production_activation_authority_gate.v1.json` |
| Deploy readiness | **NO_GO** (3 human items MISSING) | `ws8/candidate_deploy_readiness.v1.json` |
| Baseline package | COMPLETE / **Partial** | `baseline/baseline_receipt.v1.json` |
| Live CI (attached) | exit **0** | baseline validation |
| SUPPORTED interfaces | **4** | `ws1/interface_registry_snapshot.v1.json` |
| SUPPORTED services | **2** | `ws3/service_registry.v1.json` |
| Sole-writer residual | ~**76** ACCEPTED_KNOWN_RESIDUAL; fail-closed **off** | `ws1/sole_writer_residual_acceptance.v1.json` |
| Threat model | Partial + ACCEPT_PARTIAL_BASELINE | `ws8/threat_model*.json` |
| Notion | Partial writeback | `ws8/notion_*` |
| Docs package | README + guidebook + crosslink OK | `out/production_readiness/README.md`, `ws8/docs_crosslink_check.v1.json` |

### What “candidate” means (and does not)

| Allowed | Not allowed |
|---------|-------------|
| Documented bounded kernel surface | Production go-live |
| Freeze eligibility (scorecard) | Marketing “production ready” |
| Operator-planned controlled trial (after human plan) | Autonomous deploy / agentic activation |
| Further sole-writer debt reduction | Fail-closed sole-writer while residual high |

---

## 2. Risk board (program)

| ID | Status | Theme | v9 implication |
|----|--------|--------|----------------|
| RISK-006 | CLOSED when live CI attached | Live validation | Re-pin carefully; preserve validation JSON |
| RISK-008 | MITIGATING | Boundary / sole-writer advisory | Keep fail-open; optional D4 reduces residual |
| RISK-010 / 011 | MITIGATING | Services + SUPPORTED | Prefer no forced new SUPPORTED without DoD |
| RISK-012 | MITIGATING | Notion linkage | Operator Verified DoD only |
| RISK-013 | MITIGATING | Neon non-control | Keep allowlist advisory |
| RISK-014 | MITIGATING | Threat Partial | No pen-test Verified claim |
| RISK-004 | OPEN (P1) | Historical archive surfaces | Optional quarantine; not freeze-blocking |

---

## 3. Completed track (v1–v8 summary)

| Era | Outcomes |
|-----|----------|
| v1–v3 | Baseline, triage, validation service, Wave 1 (Neon, WP-D, boundary design) |
| v4–v5 | Artifact service SUPPORTED, Notion mapping/writeback, recovery, threat accept |
| v6 | Freeze scorecard, residual accept, RELEASE_HELD → path to all_pass |
| v7 | **CANDIDATE_APPROVED** deploy-held |
| v8 | Deploy NO_GO packet, activation DENIED, runbook, D4 inventory, **docs overhaul** |

---

## 4. Principles (binding)

1. **Evidence-gated** — `Missing | Partial | Verified | NOT_COMPUTABLE`; no overclaim  
2. **Repo is SoT** — JSON under `out/production_readiness/` beats narrative  
3. **Fail-closed on authority** — activation DENIED until separate process  
4. **Small reversible PRs** — one WP theme per PR when possible  
5. **Sole-writer** — `scripts/run_*` + `canonical_json` for `out/`  
6. **SUPPORTED only with tests + ownership + contracts**  

---

## 5. Recommended work packages (forward)

### Wave A — Operator / deploy (optional, blocking for any trial ship)

| WP | Priority | Goal | Exit criteria | Execute without human? |
|----|----------|------|---------------|------------------------|
| **DEPLOY-PLAN** | P0 | Human deploy + rollback plan for candidate trial | Signed plan path + checklist CD-06 PASS | **No** (operator) |
| **DEPLOY-ENV** | P0 | Env/secrets attestation for candidate target | CD-07 PASS | **No** (operator) |
| **DEPLOY-UNHOLD** | P0 | Explicit unhold decision (separate from CANDIDATE_APPROVED) | CD-08 PASS; deploy readiness may move off pure NO_GO | **No** (operator) |
| **H-VERIFIED** | P1 | Notion checkpoints Verified only with DoD | Tracker Evidence State Verified + durable links | **No** (operator) |

### Wave B — Engineering debt (safe to automate in-repo)

| WP | Priority | Goal | Exit criteria | Notes |
|----|----------|------|---------------|-------|
| **D4-C1** | P1 | Pure builders for `manual_execution*` + `run_*` publishers | Fewer sole-writer hits; receipt; tests green | Highest-value residual cluster |
| **D4-C2** | P1 | Ingest scheduler publication ownership | Writer findings ↓ on `core/ingest/*` | After or parallel C1 if small |
| **D4-C3** | P2 | Observability / proposal_sandbox writers | Inventory → optional consolidate | Lower urgency |
| **RESIDUAL-REFRESH** | P1 | Re-run sole-writer + residual acceptance after D4 | Updated acceptance under threshold | Re-pin scorecard |
| **DOCS-SYNC** | P2 | Keep readiness README/guidebook aligned after WPs | Crosslink check exit 0 | Cheap |

### Wave C — Explicitly deferred / hard-no (default)

| Item | Why deferred |
|------|----------------|
| Fail-closed sole-writer / boundary in shared CI | Residual still high; operator approval required |
| New SUPPORTED promotions | Prefer stability over count |
| Full 8-service suite / marketplace | Feature expansion |
| Production activation AUTHORIZED | Separate dual-control authority process |
| Baseline evidence → Verified | Multiple DoD residual (Notion Verified, archive debt, etc.) |
| RISK-004 full archive quarantine | P1 cleanup; not candidate-gate blocking |

---

## 6. Recommended next three PRs (engineering)

| Order | PR theme | Scope |
|-------|----------|--------|
| **1** | **D4-C1** manual_execution sole-writer consolidation | Pure `core/manual_execution*` builders; `scripts/run_*` publish; tests; residual re-pin |
| **2** | **D4-C2** ingest scheduler consolidation (if still hot after C1) | Same pattern; keep Neon/control-plane untouched |
| **3** | **RESIDUAL-REFRESH + docs sync** | Re-emit residual acceptance, scorecard, readiness README metrics; crosslink check |

**Operator-parallel (not code-only):** DEPLOY-PLAN / ENV / UNHOLD if a controlled trial is desired.

---

## 7. Production candidate gate (status)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Live CI green | **PASS** (attached) |
| 2 | Threat model operator-reviewed | **PASS** (Partial accept) |
| 3 | SUPPORTED ≥3 | **PASS** (4) |
| 4 | Sole-writer residual accepted | **PASS** (known debt) |
| 5 | Neon non-control | **PASS** |
| 6 | ≥1 SUPPORTED service | **PASS** (2) |
| 7 | Release decision present | **PASS** (CANDIDATE_APPROVED) |
| 8 | No unmitigated OPEN P0 | **PASS** |

**Downstream of freeze (not auto-granted):**

| Gate | Status |
|------|--------|
| Deploy authorized | **NO** (`NO_GO`) |
| Production activation | **NO** (`DENIED`) |

---

## 8. Immediate execution order (when “execute” is requested)

```text
Default engineering path (no deploy unhold):
  1. Land CONTINUATION_PLAN.v9.md (this file)
  2. WP-D4-C1 manual_execution pure builders + runners + tests
  3. Re-run sole-writer advisory + residual acceptance
  4. Refresh freeze scorecard + reaffirm CANDIDATE_APPROVED (deploy_held)
  5. Reaffirm activation DENIED + deploy NO_GO
  6. Docs crosslink check; re-pin; push PR #971

Operator path (only if trial deploy desired):
  A. Author deploy + rollback plan
  B. Env/secrets attestation
  C. Explicit deploy-unhold decision record
  D. Re-run candidate_deploy_readiness (expect fewer MISSING)
  E. Still leave activation DENIED unless separate AUTH process
```

---

## 9. Success metrics (v9 horizon)

| Metric | Current | v9 target |
|--------|---------|-----------|
| Freeze scorecard | 8/8 | 8/8 maintained |
| Sole-writer findings | ~76 | ↓ after D4-C1 (trend, not zero) |
| Fail-closed sole-writer | off | **still off** |
| Deploy go/no-go | NO_GO | NO_GO unless operator Wave A |
| Activation | DENIED | **DENIED** |
| Docs crosslink | all_ok | all_ok |
| Production ready claim | false | **false** |

---

## 10. Rollback and safety

- Each WP independently revertable (`git revert`)  
- Advisory CI remains fail-open  
- Never flip `ABRAXAS_BOUNDARY_FAIL_CLOSED` without operator approval  
- Never auto-honor activation tokens  
- Preserve live CI validation on baseline re-pin (`--validation-json` / `--with-fast-ci`)  

---

## 11. Related artifacts

| Path | Role |
|------|------|
| `CONTINUATION_PLAN.v9.md` | **This plan (ACTIVE)** |
| `CONTINUATION_PLAN.v8.md` | Prior (deploy/auth/runbook/docs) |
| `README.md` | Readiness hub |
| `ws8/release_decision.v1.json` | Binding release code |
| `ws8/candidate_deploy_readiness.v1.json` | Deploy NO_GO |
| `ws8/production_activation_authority_gate.v1.json` | Activation DENIED |
| `ws2/sole_writer_d4_target_inventory.v1.json` | D4 backlog |
| `docs/production_readiness/ENGINEERING_GUIDEBOOK.md` | Engineering guide |

---

## 12. Plan control

| Field | Value |
|-------|--------|
| Drafted | 2026-07-19 |
| Supersedes | CONTINUATION_PLAN.v8 |
| Execution status | **Wave B D4-C1 EXECUTED** (2026-07-19) |
| Production activation | **Not authorized by this plan** |

---

## 13. Execution result (v9 Wave B — D4-C1)

| Item | Outcome |
|------|---------|
| **D4-C1** | `core/manual_execution/runtime.py` + `core/manual_execution_receipts/runtime.py` pure builders |
| Sole-writers | `scripts/run_manual_execution_authorization.py`, `run_manual_execution_receipt_ledger.py` (+ replay helpers) |
| Sole-writer findings | **~76 → ~70** (core 57 → 51 in advisory report) |
| Residual acceptance | Re-affirmed ACCEPTED_KNOWN_RESIDUAL under threshold 100 |
| WP-D receipt | batch4_d4c1; `modules_still_writing=0` for tracked pure modules |
| Freeze scorecard | **8/8 PASS** maintained |
| Release decision | **CANDIDATE_APPROVED** · deploy_held |
| Activation | **DENIED** |
| Deploy | **NO_GO** |
| Docs crosslink | all_ok |

### Next after this execution

1. Optional **D4-C2** ingest scheduler consolidation  
2. Operator Wave A only if trial deploy desired  
3. Activation remains DENIED  

*End of CONTINUATION_PLAN.v9.*
