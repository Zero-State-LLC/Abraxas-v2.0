# Abraxas-v2.0 Whole-Repo Debug Plan

```yaml
plan_id: DEBUG_PLAN.v2
supersedes: DEBUG_PLAN.v1
drafted_at: 2026-07-19
branch: main
repository_sha: eea457ad7f238f9d2157a1bab14d58548fa539f7
scope: whole-repository engineering debug + CI triage
production_activation_authorized: false
```

**Authority:** Debug and verification only. Does **not** authorize deploy unhold or production activation.  
**Supersedes:** `DEBUG_PLAN.v1` (pre-merge branch tip).

---

## 0. Whole-repo health snapshot (live reaudit)

### Scale

| Surface | Count |
|---------|------:|
| `tests/test_*.py` | ~1389 |
| `core/**/*.py` | ~1431 |
| `scripts/**/run_*.py` | ~710 |
| `contracts/**` files | ~735 |
| Design icons / runes | 125 / 51 |

### Live gates (this reaudit)

| Gate | Result | Command / evidence |
|------|--------|-------------------|
| Unauthorized sole-writer | **0** | `run_sole_writer_advisory_check.py` |
| Residual packages | **CLOSED_BY_POLICY** | `ws2/residual_package_disposition.v1.json` |
| Soft CI residual | **CLOSED_BY_ACCEPTANCE** | `ws6/soft_ci_gate_acceptance.v1.json` |
| Freeze scorecard | **8/8 PASS** | `ws8/freeze_gate_scorecard.v1.json` |
| Release | **CANDIDATE_APPROVED** · deploy_held | `ws8/release_decision.v1.json` |
| Activation | **DENIED** | `ws8/production_activation_authority_gate.v1.json` |
| Deploy | **NO_GO** | `ws8/candidate_deploy_readiness.v1.json` |
| Ruff (full tree) | **pass** | `ruff check .` |
| Design palette sync | **OK** | `scripts/design/validate_viz_palette_sync.py` |
| aal-viz palette tests | **3/3 pass** | vitest `vizPalette.test.ts` |
| Script org dry-run | 241 historical unorganized (baseline); **CI only fails on NEW root adds** | `organize_scripts.py dry-run` |
| Post-merge re-pin | Present | `ws8/post_merge_main_repin_receipt.v1.json` |
| PR #971 | **MERGED** to main | `a9fea3d` |

### Risk board (baseline register)

| ID | Status | Title |
|----|--------|--------|
| RISK-006 | **CLOSED** | Live validation receipt |
| RISK-004 | MITIGATING | Historical archive surfaces |
| RISK-008 | MITIGATING | Sole-writer/boundary advisory (not fail-closed) |
| RISK-010 | MITIGATING | Full service suite incomplete |
| RISK-011 | MITIGATING | SUPPORTED kernel set limited |
| RISK-012 | MITIGATING | Notion Evidence State not fully Verified |
| RISK-013 | MITIGATING | Neon Genie residual |
| RISK-014 | MITIGATING | Threat model Partial |

### Soft CI inventory (not hard fails)

| Priority | Disposition | Surface |
|----------|-------------|---------|
| P0_TRACKED | KEEP_REPORT_ONLY | fast-ci advisory fail-open commands |
| P1 | KEEP_UNTIL_OPERATOR_RESEAL | P64 manifest source hash gate |
| P1 | REVIEW_HARDEN | status-pages deterministic output |
| P1 | KEEP_REPORT_ONLY | other fast-ci advisory commands |
| P2 | KEEP_REPORT_ONLY | Rune integrity scanner (report-only) |

**p0_blocking_soft_gates:** 0

### Closed since v1

| Issue | Resolution |
|-------|------------|
| `test_writer_debt_triage` required findings ≥1 | Allow 0 post-TD (`aab74b1`) |
| ruff F401 unused Path in research canary review | Removed (`65ec8c3`) |
| check-organization oracle runners | Moved to `scripts/ingest/` |
| Push-cancel CI storms on PR branch | Merge complete; prefer batch pushes on main |
| PR #971 merge readiness | Merged; post-merge re-pin on main |

---

## 1. Repository map (debug by domain)

| Domain | Paths | Primary checks | Common fails |
|--------|-------|----------------|--------------|
| **Kernel / contracts** | `core/canonical/`, `contracts/` | schema tests, validation_service | schema drift, hash mismatch |
| **Runtime / execution** | `core/manual_execution*`, `core/runtime/`, graph_runner | pure-core tests, sole-writer | illegal `out/` writes from core |
| **Sole-writer / boundary** | `core/production_readiness/sole_writer_*`, `boundary_*` | advisory checks | new write paths, allowlist holes |
| **Ingest / oracle** | `core/ingest/`, `scripts/ingest/` | ingest tests, org layout | unorganized root runners |
| **Services** | `core/services/`, `scripts/run_validation_service.py`, artifact | service unit tests | request validation, path deny |
| **Canary / forecast** | `core/canary*`, `core/forecast*`, research canary | canary tests, authority locks | accidental activation flags |
| **Governance / overlay** | `core/governance*`, `core/overlay_*` | overlay tests | authority bleed |
| **Yggdrasil / topology** | contracts yggdrasil, aal-viz | aal-viz npm test/build | projection shape, palette desync |
| **Geometry / chamfer** | many `core/chamfer_*`, metric operators | fast-ci scoped pyright + tests | type errors in scoped files |
| **AAL-viz console** | `apps/aal-viz-live-console/` | `npm test`, `npm run build` | token import, Vite fs.allow |
| **Visual OS** | `design-system/` | palette sync, showcase | JSON/TS desync |
| **Production readiness** | `core/production_readiness/`, `out/production_readiness/` | freeze/release/activation producers | wrong decision_code, missing validation |
| **abx-afe / skills** | `abx-afe/`, `skills/` | package writer policy | ungoverned writes |
| **CI workflows** | `.github/workflows/` | org, fast-ci, security, release | soft continue-on-error, cancel storms |
| **Docs / STATUS** | `STATUS.md`, `docs/`, `README.md` | docs crosslink | stale plan pointers |

---

## 2. Failure taxonomy (whole repo)

| Class | Meaning | First move |
|-------|---------|------------|
| **A** Hard CI | pytest / ruff / org / aal-viz red | Reproduce → minimal fix → one push → wait |
| **B** Soft / advisory | sole-writer, boundary, neon allowlist | Log only; no fail-closed flip |
| **C** Drift / dirt | fast-ci exit 3, dirty `out/` | restore dirt; clean tree re-run |
| **D** Authority residual | DENIED / NO_GO / Partial | Not a product bug |
| **E** Environment | PATH, python, venv, node | `.venv/bin` + `export PATH` |
| **F** Stale assertion | DoD moved, test didn’t | Update test with rationale |
| **G** Visual desync | palette / tokens / CSS | `validate_viz_palette_sync` + build |
| **H** Scale / noise | 1.4k tests, mark warnings | Narrow with `-k` / markers |
| **I** Historical org debt | 241 unorganized runners | Only fail if **new** root `scripts/run_*.py` |
| **J** Scheduled CI on main | Nightly/history reds | Compare to latest merge SHA before panic |

---

## 3. Standard whole-repo reproduction kit

```bash
cd /path/to/Abraxas-v2.0
export PATH="$(pwd)/.venv/bin:$PATH"
git checkout main && git pull

# Cleanliness
git status -sb

# Hard gates (local)
python -m ruff check .
python scripts/run_fast_ci.py          # full local mirror of primary CI gate
python scripts/organize_scripts.py dry-run > /tmp/org.json

# Readiness advisory (fail-open)
python scripts/run_sole_writer_advisory_check.py
python scripts/run_boundary_advisory_check.py
python scripts/run_neon_genie_allowlist_check.py

# Design system
python scripts/design/validate_viz_palette_sync.py

# Console
cd apps/aal-viz-live-console && npm ci && npm test && npm run build && cd ../..

# Targeted pytest
python -m pytest path/to/test.py::name -vv --tb=short
```

**CI watch (no thrash):**

```bash
gh run list --branch main --limit 5
gh run watch <run_id>
# One logical push, then wait for full suite
```

---

## 4. Playbooks (expanded)

### A1 — fast-ci pytest failure

1. Copy exact nodeid from log summary.  
2. Local pytest that nodeid.  
3. Classify A vs F (stale assert).  
4. Fix; re-run full `run_fast_ci.py` once.  
5. Single push; watch.

### A2 — ruff failure

1. `ruff check .` locally.  
2. Prefer `--fix` only for auto-safe fixes; review.  
3. Avoid mass reformat.

### A3 — check-organization

1. Dry-run org; list `moved[]`.  
2. Intersect with **new** root `scripts/run_*.py` vs `main` parent.  
3. `git mv` into domain dir (`ingest/`, `artifact/`, …).  
4. Nested `sys.path` + sole-writer nested auth.

### A4 — aal-viz-console CI fail

1. `cd apps/aal-viz-live-console && npm test && npm run build`.  
2. Check Vite `fs.allow` includes repo root for design-system CSS.  
3. Palette: `validate_viz_palette_sync.py`.

### B1 — Sole-writer findings rebound

1. Open `ws1/sole_writer_advisory_report.v1.json`.  
2. If core: pure builder + script publisher.  
3. If skills/afe: package policy prefixes.  
4. Never enable fail-closed without operator (RISK-008).

### C1 — Drift / dirty worktree

1. `git status` immediately.  
2. Discard accidental re-pin dirt under `out/` if not intentional.  
3. Re-run fast-ci clean.

### D1 — “Not production ready”

Not a code bug. See activation gate + deploy readiness missing CD-06..08.

### I1 — 241 unorganized scripts on dry-run

Expected historical debt. CI fails only when **new** root runners appear in the PR diff vs base. Do not mass-organize in a mega-PR without mandate.

### J1 — Old scheduled main failures

Historical scheduled `ci` failures on main (pre-#971) are not auto-current. Always compare **head SHA** to `origin/main` tip before treating as live regression.

---

## 5. Priority queue (post-merge whole repo)

| Prio | Item | Owner | Status |
|------|------|-------|--------|
| **P0** | Keep main green after #971 (watch merge CI) | Eng | Monitor |
| **P0** | Unauthorized sole-writer remains 0 | Eng | **Green now** |
| **P1** | Document soft vs hard gates (this plan §0) | Eng | **Done** |
| **P1** | Stale residual-count tests | Eng | **Cleared** |
| **P2** | Optional CI step: palette sync (non-blocking first) | Eng | **Done** — advisory in `run_fast_ci` |
| **P2** | pytest.ini register `canon`/`security`/`integration` marks | Eng | **Done** |
| **P2** | RISK-008 fail-closed criteria doc + green window | Operator+Eng | **Criteria drafted** (`ws2/risk_008_fail_closed_criteria.v1.md`); fail-closed still OFF |
| **P2** | Historical org debt batch (I1) only if mandated | Eng | Open / large |
| **P3** | RISK-004 archive quarantine review | Eng | MITIGATING |
| **P3** | Notion strategic rows → honest Verified | Operator | MITIGATING |
| **P3** | Expand SUPPORTED set (RISK-010/011) | Eng+Operator | MITIGATING |
| **Hold** | Deploy unhold / dual-control activation | Operator | DENIED/NO_GO |

---

## 6. Hard vs soft CI (operator cheat sheet)

| Check | Blocking? | Notes |
|-------|-----------|--------|
| fast-ci (pytest + ruff + drift) | **Yes** | Primary |
| check-organization | **Yes** | New root runners only |
| aal-viz-console | **Yes** | App package |
| security-scan / dependency-review | **Yes** | Supply chain |
| validate-commits | **Yes** | Conventional commits |
| CodeQL | **Yes** (when required) | Analyze |
| sole-writer / boundary / neon in fast-ci | **No** (advisory) | Fail-open by design |
| Rune integrity scanner | **No** | report-only |
| P64 hash gate | **Soft** until operator reseal | |
| status-pages deterministic | **Soft** / REVIEW_HARDEN | |

---

## 7. Debug session template

```markdown
### Symptom
### Class (A–J)
### Domain (from §1 map)
### Reproduce command + exit
### Expected vs actual
### Root cause
### Fix (minimal)
### Verification commands
### Residual risk
### Authority impact (none / advisory / operator)
```

---

## 8. Success criteria (“whole-repo debug posture healthy”)

- [x] Unauthorized sole-writer = 0  
- [x] Full ruff clean on tip  
- [x] Palette sync OK  
- [x] Readiness gates consistent DENIED/NO_GO/CANDIDATE_APPROVED  
- [x] DEBUG plan refreshed for main post-#971  
- [ ] Latest **main** merge CI `fast-ci` green (watch run in progress)  
- [ ] No unowned P0 hard fails on current `origin/main`  
- [ ] Soft gates remain documented, not silently promoted  

---

## 9. Related artifacts

| Path | Role |
|------|------|
| `DEBUG_PLAN.v1.md` | Pre-merge draft (superseded) |
| `CONTINUATION_PLAN.v12.md` | Post-merge program plan |
| `design-system/docs/MERGE_READINESS.md` | Merge criteria used for #971 |
| `ws8/post_merge_main_repin_receipt.v1.json` | Main re-pin receipt |
| `AGENTS.md` | Governance V3 workflow |

---

*End DEBUG_PLAN.v2 — whole-repo reaudit after PR #971 merge.*
