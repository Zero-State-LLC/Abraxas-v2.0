# Abraxas Production Continuation Plan v13

```yaml
program_id: ABRAXAS_PRODUCTION_CONTINUATION
plan_id: CONTINUATION_PLAN.v13
supersedes: CONTINUATION_PLAN.v12
status: ACTIVE
drafted_at: 2026-07-19
branch: main
merged_pr: https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/972
merge_commit: 333127804881a4346d59883bb588ba107c1ae7d9
evidence_state: Partial
current_readiness_state: CANDIDATE_HELD_FOR_OPERATOR_DEPLOY
primary_goal: post mass-org stabilization; optional long-tail runner organize; operator-held deploy
authority_mode: operator-controlled
production_activation_authorized: false
release_decision: CANDIDATE_APPROVED
deploy_held: true
deploy_readiness: NO_GO
activation_gate: DENIED
unauthorized_sole_writer_findings: 0
scripts_mass_org: waves_1_and_2_merged
root_run_scripts_remaining: 105
```

**PR #972 (mass-organize scripts) is merged. Production activation remains DENIED. Deploy remains NO_GO.**

---

## 1. What landed on main (this merge)

| Track | Content |
|-------|---------|
| Mass-org wave 1 | ~241 runners → domain packages via `PREFIX_MAP` |
| Mass-org wave 2 | +~330 runners → `hygiene`, `codegen`, `geometry`, `readiness`, `runtime`, `notion`, `belief`, `campaign`, plus existing domains |
| Import/path rewrites | `scripts.run_X` / `from scripts import` / CI / docs; sealed `out/` hygiene receipts **not** bulk-rewritten |
| Sole-writer | Nested `scripts/<domain>/run_*.py` authorized; **finding_count: 0** |
| Artifact registry | Scans domain runners |
| Operator package | `scripts/operator/` is a **namespace package** (no `__init__.py`) to avoid stdlib `operator` shadowing under `python scripts/*.py` |

### Domain inventory (post-merge)

| Domain | Approx. runners |
|--------|----------------:|
| hygiene | 110 |
| temporal | 91 |
| codegen | 71 |
| research | 49 |
| geometry | 48 |
| operator | 46 |
| transport | 44 |
| viz | 39 |
| artifact | 30 |
| readiness | 15 |
| ingest | 14 |
| runtime | 13 |
| metric | 11 |
| notion | 8 |
| governance | 7 |
| belief | 5 |
| campaign | 4 |
| **root residual** | **~105** |

Root residuals include intentional stay-put scripts (`run_fast_ci.py`, `run_operator_review_*`) and long-tail prefixes (`run_grok_*`, `run_manual_*`, `run_human_*`, `run_review_*`, one-offs).

---

## 2. Binding authority (unchanged by merge)

| Gate | Status |
|------|--------|
| Freeze | 8/8 PASS (prior package) |
| Release | CANDIDATE_APPROVED · deploy_held |
| Activation | **DENIED** |
| Deploy | **NO_GO** (missing human plan, env attestation, unhold) |
| Sole-writer | **0** unauthorized (re-pinned at merge SHA) |

---

## 3. Recommended next

| Priority | Item | Owner |
|----------|------|--------|
| P0 | Watch main CI after #972; fix only if red | Eng |
| P1 | Optional wave-3: map long-tail root prefixes (`grok`, `manual`, `human`, `review`, `fusion`, `brier`, …) | Eng |
| P1 | Operator Notion hub note: PR #972 merged; script layout domain-based; still NOT_READY for deploy | Operator |
| P2 | Prefer `python -m scripts.<domain>.run_*` or repo-root `python scripts/...` with care; never put `scripts/` alone on `PYTHONPATH` with `operator` domain | Eng |
| P2 | Soft→hard gate (RISK-008) — **no flip without approval** | Operator |
| Hold | Trial deploy Wave A | Operator + plan + rollback |
| Hold | Dual-control production activation | Separate process |

---

## 4. Non-goals

- Silent deploy unhold  
- Marketing “production ready”  
- Fail-closed sole-writer in shared CI without operator mandate  
- Bulk rewrite of sealed hygiene hash-chain receipts under `out/operator_review/v2_hygiene_*`  

---

## 5. Plan control

| Field | Value |
|-------|--------|
| Supersedes | CONTINUATION_PLAN.v12 |
| Status | **ON MAIN** — candidate held for operator |
| Production activation | **Not authorized** |
| Evidence pin | sole-writer advisory @ `333127804881a4346d59883bb588ba107c1ae7d9` |
