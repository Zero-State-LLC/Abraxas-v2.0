# Abraxas Production Continuation Plan v2

```yaml
program_id: ABRAXAS_PRODUCTION_CONTINUATION
plan_id: CONTINUATION_PLAN.v2
supersedes: CONTINUATION_PLAN.v1
status: ACTIVE
drafted_at: 2026-07-19
baseline_head_sha: 3171f2ea8e899af489b9d214563107003398dfbf
branch: chore/ws0-baseline-live-receipt
pull_request: https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971
evidence_state: Partial
current_readiness_state: NOT_READY
primary_goal: bounded production candidate
authority_mode: operator-controlled
governance_mode: advisory unless explicitly authorized
```

This plan is a **stabilization and release-readiness** roadmap, not a feature roadmap.  
Do not treat Abraxas as production-ready because tests pass, docs exist, or agents report completion.

---

## 1. Current position (evidence-backed)

### 1.1 What is true now

| Area | State | Evidence |
|------|--------|----------|
| WS0 baseline package | Package **COMPLETE**; evidence **Partial** | `out/production_readiness/baseline/` |
| Live fast CI | **exit 0** | `validation_receipt.v1.json` (RISK-006 **CLOSED**) |
| Interface registry | **33** entries; **SUPPORTED = 2** | `canonical_json`, `run_fast_ci` |
| Boundary advisory | Report-only in fast CI; **0** findings post allow-list | WS1 boundary report |
| Sole-writer advisory | Hardened; **~95** findings | WS1 sole-writer report |
| Writer debt triage | Classified | `ws2/writer_debt_triage.v1.json` |
| WP-D consolidations | **12** runtime modules pure; runners publish | `ws2/wp_d_consolidation_receipt.v1.json` |
| Service layer | **1** implemented ADVISORY service | `validation_service` + `ws3/service_registry.v1.json` |
| Threat model | **v0 Partial** (10 threats / 8 controls) | `ws8/threat_model.v0.json` (RISK-014 **MITIGATING**) |
| Notion readiness links | **Missing** | RISK-012 **OPEN** |
| Neon Genie allowlist | **Missing** | RISK-013 **OPEN** |
| Production candidate freeze | **Not started** | No release decision artifact |

### 1.2 Risk board

| ID | Title | Status | Priority |
|----|--------|--------|----------|
| RISK-006 | Live validation receipt | **CLOSED** | P0 |
| RISK-008 | Boundary / sole-writer enforcement | **MITIGATING** | P0 |
| RISK-010 | Canonical service layer | **MITIGATING** | P1 |
| RISK-011 | SUPPORTED interfaces incomplete | **MITIGATING** (2) | P0 |
| RISK-014 | Threat model | **MITIGATING** (v0 Partial) | P0 |
| RISK-004 | Historical archive surfaces | **OPEN** | P1 |
| RISK-012 | Notion readiness linkage | **OPEN** | P1 |
| RISK-013 | Neon Genie capability allowlist | **OPEN** | P1 |

### 1.3 Sole-writer debt snapshot (latest triage)

| Class | Count | Disposition |
|-------|------:|-------------|
| CORE_BUILDER_OR_HELPER | ~74 | Consolidate further (batch 3+) |
| SKILL_OUT_WRITER | ~12 | Allowlist advisory skill surfaces |
| ABX_AFE_WRITER | ~6 | Adapter boundary |
| ORACLE_EXECUTION_WRITER | ~2 | Consolidate or quarantine |
| SCRIPT_NON_RUN_WRITER | ~1 | Rename/allowlist |
| RUNTIME_PACKET_WRITER | **0** | Cleared by WP-D batches 1–2 |
| **Total findings** | **~95** | Fail-closed **not** ready |

### 1.4 Completed work packages (v1 track)

| WP | Outcome |
|----|---------|
| **A** Writer debt triage | Done — classification + CD-001/002/003 documented |
| **B** Validation Service v1 | Done — ADVISORY facade + schemas + tests |
| **C** Service registry seed | Done — 8 services listed; 1 implemented |
| **D batch 1** Runtime sole-writer | Done — brier/canary/drift/promotion/scheduler |
| **D batch 2** Runtime sole-writer | Done — forecast/oracle/sandbox/state/operator_queue/external_action/overlay_observability |
| **F** Threat model v0 | Done — Partial security baseline |

---

## 2. Principles (binding)

1. **Stabilization before expansion** — no new kernel subsystems unless required for readiness.  
2. **Evidence-gated completion** — only `Verified` closes a checkpoint; Partial remains Partial.  
3. **Small, reversible changes** — one principal checkpoint per PR/increment.  
4. **One canonical source per concern** — registries over competing docs.  
5. **Fail closed** on authority, identity, schema, provenance when unknown.  
6. **Deterministic where declared** — canonical JSON, replay tests, no silent randomness.  

Evidence states: `Missing | Partial | Verified | NOT_COMPUTABLE`.

---

## 3. Target architecture (enforced direction)

```text
Consumer → Adapter → Supported Service → Kernel modules → Infrastructure
```

**Write path:** only `scripts/run_*.py` (or explicit allow-list) may publish under `out/` via `write_canonical_json`.

**Supported set today (only these are production-consumable contracts):**

1. `canonical_json` — serialization / hash / atomic write  
2. `run_fast_ci` — mandatory validation entry point  

Everything else is INTERNAL / ADVISORY / EXPERIMENTAL until promoted with tests + ownership attestation.

---

## 4. Ordered continuation work packages (v2)

Proceed in this order unless marked parallel-safe.

### Wave 1 — Close highest remaining P0 gaps (next 2–4 increments)

| WP | Name | Priority | Goal | Exit criteria | Est. |
|----|------|----------|------|----------------|------|
| **G** | Neon Genie capability allowlist | P1→P0 for integration safety | Explicit allowlist of Genie capabilities; prove no governance control | `neon_genie_capability_allowlist.v1.json` + advisory CI check; RISK-013 → MITIGATING — **DONE** | 1 PR |
| **D3** | Writer consolidation batch 3 | P0 | Clear top remaining CORE_BUILDER write clusters (overlay_*, manual_*, review_*) | sole-writer findings ↓; more pure builders; receipt updated — **DONE (8 modules)** | 1–2 PRs |
| **E** | Boundary fail-closed design | P0 | Document + optional env flag for boundary check only (default off) | Design receipt; `ABRAXAS_BOUNDARY_FAIL_CLOSED` exists; never on by default — **DONE** | 1 PR |
| **J** | Artifact & Provenance Service v0 | P1 | Thin service facade over `canonical_json` (SUPPORTED dependency) | ADVISORY service + registry entry + tests | 1 PR |

### Wave 2 — Contract and service hardening

| WP | Name | Priority | Goal | Exit criteria |
|----|------|----------|------|----------------|
| **K** | Third SUPPORTED promotion | P0 | Promote one mature surface (e.g. Validation Service **or** receipt schema *only if* canonical writer used) | `supported_count >= 3` with full registry fields + tests |
| **L** | Execution Receipt Service v0 | P1 | Versioned service; runner must use `write_canonical_json` | Service + tests; no non-canonical dumps on success path |
| **M** | Registry completeness for COMPATIBILITY.md | P1 | Per-schema inventory under pipelines/yggdrasil (not just roots) | Delta receipt; unregistered high-signal schemas → 0 or listed NOT_COMPUTABLE |
| **N** | Soft CI gate audit | P0 | Inventory `continue-on-error` / non-blocking gates; classify keep vs harden | Audit artifact; no silent bypass of P0 gates |

### Wave 3 — Operator, recovery, candidate freeze

| WP | Name | Priority | Goal | Exit criteria |
|----|------|----------|------|----------------|
| **H** | Notion readiness linkage | P1 | Link baseline + threat model + registry into Production Readiness Tracker | RISK-012 CLOSED or NOT_COMPUTABLE with operator reason |
| **O** | Recovery drill v0 | P0 | Document + dry-run restore of critical `out/` artifacts from git | Recovery receipt; rollback steps tested once |
| **P** | Threat model v0 → Partial→Verified path | P0 | Operator review of ThreatModel.v0; close or accept residual risks | Operator decision recorded; optional v0.1 |
| **I** | Production candidate freeze | P0 | Bound supported surface; freeze experimental routes; release decision artifact | `release_decision.v1.json` with RELEASE_HELD or CANDIDATE_APPROVED |

### Explicitly deferred (P2/P3)

- Full eight-service production suite  
- Marketplace / public ecosystem  
- Fail-closed sole-writer while findings ≫ 0 and CORE_BUILDER still large  
- Autonomous production activation  
- Cosmetic refactors without readiness value  

### Parallel-safe (any wave)

- Operator Notion updates (H)  
- Documentation projections of registries (must not fork authority)  
- Read-only observability inventories  

---

## 5. Recommended next three PRs (execute in order)

### PR-1 — WP-G Neon Genie capability allowlist

**Why first:** RISK-013 is open; Genie is already integrated as skill/runner; allowlist is smaller than mass builder cleanup and blocks control-plane creep.

**Deliverables:**

1. `contracts/neon_genie/capability_allowlist.v1.schema.json`  
2. `out/production_readiness/ws5/neon_genie_capability_allowlist.v1.json`  
3. `scripts/run_neon_genie_allowlist_check.py` (advisory; optional report-only in fast CI)  
4. Explicit denials: governance control, canon mutation, production activation, forecast influence  
5. Tests: allowlist loads; denied capability fails closed in checker  

**Exit:** RISK-013 → MITIGATING; no fail-closed on sole-writer.

### PR-2 — WP-D batch 3 (overlay / manual / review runtimes)

**Why:** Largest remaining write debt class (CORE_BUILDER ~74).

**Scope (example batch, adjust to existing `scripts/run_*` pairs):**

- `core/overlay_*/runtime.py` families with matching runners  
- `core/manual_*/runtime.py` if runners exist  
- Avoid one-off temporal_upstream_* unless paired with runners  

**Exit:** sole-writer findings trend down; consolidation receipt updated; tests assert no `write_canonical_json` in migrated modules.

### PR-3 — WP-E boundary fail-closed design + WP-J Artifact service spike (can split)

**E:** design-only + env flag default off; document promotion criteria (already partially in WS1 receipt).  
**J:** thin Artifact & Provenance Service wrapping SUPPORTED `canonical_json` (hash + optional atomic write with explicit path policy).

**Exit:** design receipt; Artifact service ADVISORY in service registry.

---

## 6. Definition of Done (every checkpoint)

```yaml
implementation: COMPLETE
tests: PASS
contract: DOCUMENTED
evidence_state: Verified   # only then mark Done in readiness tracker
artifact_or_pr: LINKED
rollback: DOCUMENTED
security_impact: REVIEWED
readiness_tracker: UPDATED
repository_state: CLEAN
notion_repo_sync: COMPLETE  # or NOT_COMPUTABLE with reason
operator_decision: RECORDED_IF_REQUIRED
```

Anything weaker remains `In progress` / `Partial` / `Missing` / `NOT_COMPUTABLE`.

---

## 7. Production candidate gate (WP-I criteria)

A **bounded production candidate** may be proposed only when **all** hold:

| # | Criterion | Current |
|---|-----------|---------|
| 1 | Live CI green on pinned SHA | Yes |
| 2 | Threat model exists and operator-reviewed | Partial (v0 not reviewed) |
| 3 | SUPPORTED set explicit and non-empty | Yes (2) |
| 4 | Sole-writer residual accepted or below agreed threshold | No (~95; no threshold set) |
| 5 | Neon Genie cannot control governance (allowlist + tests) | No |
| 6 | At least one versioned service for core validation path | Partial (Validation Service ADVISORY) |
| 7 | Release decision artifact with operator sign-off | No |
| 8 | No OPEN P0 without mitigation plan | No (RISK-008 still only MITIGATING) |

**Fail-closed outcomes for promotion:** `RELEASE_HELD`, `OPERATOR_REVIEW_REQUIRED`, `NOT_COMPUTABLE`.

---

## 8. Success metrics (forward-looking)

| Metric | Current | Wave 1 target | Candidate freeze target |
|--------|---------|---------------|-------------------------|
| Live fast CI | green | green | green |
| Sole-writer findings | ~95 | ≤ 60 | threshold agreed + allow-list owned |
| RUNTIME pure modules | 12 | ≥ 20 | all high-hit runtimes pure |
| SUPPORTED interfaces | 2 | 2–3 | 3+ with consumers documented |
| Implemented services | 1 ADVISORY | 2 ADVISORY | ≥1 SUPPORTED service |
| Threat model | v0 Partial | operator-reviewed | residual risks accepted |
| Neon allowlist | missing | present + CI advisory | present + tests green |
| Notion linkage | missing | linked or NOT_COMPUTABLE | linked |
| Production ready | **no** | **no** | **candidate only if gate table passes** |

---

## 9. Rollback and safety

- Each WP is independently revertable (git revert).  
- Advisory CI gates must remain fail-open until operator approves fail-closed.  
- Never flip sole-writer to fail-closed while CORE_BUILDER findings dominate.  
- Do not promote SUPPORTED without tests + ownership + compatibility note.  
- Do not claim Verified baseline without Notion linkage (or explicit NOT_COMPUTABLE).  

---

## 10. Operator decisions required (explicit)

| Decision | Blocking? | Notes |
|----------|-----------|-------|
| Accept ThreatModel.v0 as Partial baseline | Soft | Unblocks RISK-014 path to Verified |
| Set sole-writer residual threshold for candidate | Soft | Needed for WP-I gate #4 |
| Priority: Neon allowlist vs more writer cleanup | Soft | Plan recommends Neon first |
| Notion tracker page + writeback policy | Soft | RISK-012 |
| Any fail-closed CI promotion | Hard | Requires explicit approval |

---

## 11. Immediate recommendation

```text
NEXT_PR: WP-G Neon Genie capability allowlist
THEN:    WP-D batch 3 (CORE_BUILDER clusters with existing runners)
THEN:    WP-E boundary fail-closed design (default off) + optional WP-J Artifact service
```

**Do not** start production freeze (WP-I) until Wave 1 exit criteria and operator decisions above are addressed.

---

## 12. Related artifacts

| Artifact | Path |
|----------|------|
| This plan | `out/production_readiness/CONTINUATION_PLAN.v2.md` |
| Prior plan | `out/production_readiness/CONTINUATION_PLAN.v1.md` |
| Baseline | `out/production_readiness/baseline/` |
| Interface registry | `out/production_readiness/ws1/interface_registry_snapshot.v1.json` |
| Writer triage | `out/production_readiness/ws2/writer_debt_triage.v1.json` |
| WP-D receipt | `out/production_readiness/ws2/wp_d_consolidation_receipt.v1.json` |
| Service registry | `out/production_readiness/ws3/service_registry.v1.json` |
| Threat model | `out/production_readiness/ws8/threat_model.v0.json` |
| Active PR | https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971 |

---

## 13. Final continuation rule

Abraxas is production-ready only when supported behavior is:

**bounded · versioned · enforceable · observable · secure · recoverable · reproducible · evidence-backed · explicitly approved**

Until then: `current_readiness_state: NOT_READY`.
