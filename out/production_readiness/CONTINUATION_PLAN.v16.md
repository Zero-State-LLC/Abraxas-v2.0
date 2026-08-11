# Abraxas Production Continuation Plan v16

```yaml
program_id: ABRAXAS_PRODUCTION_CONTINUATION
plan_id: CONTINUATION_PLAN.v16
supersedes: CONTINUATION_PLAN.v15
status: DRAFT
drafted_at: 2026-07-19
branch: main
tip_context: production-readiness-evidence-refresh
merged_scripts_prs:
  - https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/972   # mass-org wave 1–2
  - https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/973   # mass-org wave 3
  - https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/974   # finish organization
  - https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/975   # post-org hygiene + DX
scripts_organization: COMPLETE
scripts_maintenance: COMPLETE
unauthorized_sole_writer_findings: 3_report_only
evidence_state: Partial
current_readiness_state: NOT_READY
primary_goal: keep readiness evidence aligned with repo-observed state while activation remains denied
authority_mode: operator-controlled
production_activation_authorized: false
release_decision: RELEASE_HELD
deploy_held: false  # no candidate deploy to hold while release is held
deploy_readiness: NO_GO
activation_gate: DENIED
```

**Scripts track is closed (org + hygiene/DX).** The current readiness evidence refresh keeps the production-candidate package aligned with repo-observed state: release is **RELEASE_HELD**, deploy is **NO_GO**, and production activation remains **DENIED**.

---

## 1. Closed tracks (do not reopen)

| Track | Evidence | Status |
|-------|----------|--------|
| Mass-org waves 1–3 | PRs #972, #973 | Done on main |
| Finish org (preflight, operators, builders) | PR #974 | Done; `status.complete: true` |
| Post-org inventory + DX | PR #975 | Done; CONTINUATION_PLAN.v15 |
| Unauthorized sole-writer | Advisory report | **3** report-only findings; fail-closed off |
| Soft CI disposition | Prior readiness package | `CLOSED_BY_ACCEPTANCE` (do not flip without mandate) |

### Scripts layout (frozen)

- **~709** domain runners under `scripts/<domain>/run_*.py`
- **Root `run_*`:** only `scripts/run_fast_ci.py`
- **Also:** `scripts/preflight/`, `scripts/tools/`, `scripts/viz/build_aal_viz_*`
- **Guides:** `scripts/README.md`, AGENTS.md scripts section
- **Rules:** no `scripts/operator/__init__.py`; no bulk rewrite of sealed `v2_hygiene_*` / handoff hash chains
- **Check:** `python scripts/organize_scripts.py status` → `complete: true`

---

## 2. Binding authority (unchanged by scripts work)

| Gate | Status |
|------|--------|
| Freeze | Current package 7 PASS / 1 PARTIAL (`RELEASE_HELD` recommended) |
| Release | `RELEASE_HELD` · readiness `NOT_READY` |
| Activation | **DENIED** |
| Deploy | **NO_GO** (human plan, env attestation, unhold still required) |
| Sole-writer | **3** report-only findings (advisory / fail-open in fast-ci) |

---

## 3. Recommended next (priority order)

### P0 — Operator / program visibility

| ID | Action | Owner | Exit criteria |
|----|--------|-------|---------------|
| **P0.1** | Notion hub note: scripts org complete (#972–#975); layout domain-based; still **NOT_READY** for deploy/activation | Operator | Hub row/status reflects merge + held posture |
| **P0.2** | Confirm sole-writer pin / readiness hub links point at current main tip when convenient | Eng / Operator | Pin SHA matches main after readiness evidence refresh |
| **P0.3** | Watch main CI after merges; fix only if red | Eng | Main green |

### P1 — Whole-repo health (next eng track)

| ID | Action | Owner | Exit criteria |
|----|--------|-------|---------------|
| **P1.1** | **DEBUG_PLAN.v3** whole-repo reaudit (post mass-org): flaky tests, path ghosts, out/ drift, aal-viz projection tests that fail on empty local `out/` | Eng | Written plan + ranked smallest PRs |
| **P1.2** | Triage **ghost plan paths** (core/tests strings to never-landed `scripts/run_*.py`) — mark advisory or drop dead references; do **not** invent runners | Eng | Inventory + optional small PR |
| **P1.3** | Fast-ci drift hygiene: generators that dirty tracked `out/` (e.g. fusion seals) stay pin-stable | Eng | No surprise exit-code-3 on clean main |

### P2 — Optional polish (defer freely)

| ID | Action | Notes |
|----|--------|-------|
| **P2.1** | Move `abx_loop*` / codex loop CLIs into `scripts/codegen/` or `scripts/loop/` | Optional; currently intentional root entrypoints |
| **P2.2** | Makefile / just recipes for common domain runners | DX only |
| **P2.3** | Figma / Visual OS Phase 10 library import | Design/Operator per prior Visual OS plan |
| **P2.4** | RISK-008 soft→hard criteria window | **No flip without operator approval** |

### Hold — separate authority process

| ID | Action | Required before any eng “go” |
|----|--------|------------------------------|
| **H.1** | Trial deploy Wave A | Deploy plan, env attestation, rollback, operator unhold |
| **H.2** | Dual-control production activation | Separate governed decision; not a scripts PR |

---

## 4. Suggested execution order

```text
1) P0.1 Notion note (ops)          ── parallel ──  P0.3 main CI watch (eng)
2) P1.1 DEBUG_PLAN.v3              → pick 1–2 smallest PRs from audit
3) P1.2 ghost-path triage (if audit ranks it)
4) P2.* only if bandwidth
5) H.1 / H.2 only after explicit operator go
```

**Default eng next:** **P1.1 DEBUG_PLAN.v3** (whole-repo reaudit).  
**Default ops next:** **P0.1 Notion hub note**.

---

## 5. Non-goals

- Wave-4 mass script renames or domain reshuffles  
- Fail-closed sole-writer in shared CI without operator mandate  
- Silent deploy unhold or marketing “production ready”  
- Bulk rewrite of sealed hygiene receipts / operator handoff hash chains  
- Reopening closed readiness package rows without new evidence  

---

## 6. Success metrics (this cycle)

| Metric | Target |
|--------|--------|
| Scripts status | `complete: true` remains true on main |
| Root `run_*.py` | Only `run_fast_ci.py` |
| Sole-writer | 0 unauthorized |
| New runners | Land under `scripts/<domain>/` |
| Deploy / activation | Still held until H.1 / H.2 |

---

## 7. Plan control

| Field | Value |
|-------|--------|
| Supersedes | CONTINUATION_PLAN.v15 |
| Status | **DRAFT** — activate by adopting as ACTIVE on main / hub |
| Scripts track | **CLOSED** (org + maintenance) |
| Next eng focus | Whole-repo DEBUG_PLAN.v3 (or operator Notion first) |
| Production activation | **Not authorized** |

---

## 8. One-line summary

**Scripts work is finished; continuation pivots to operator visibility and whole-repo health while deploy/activation stay held.**
