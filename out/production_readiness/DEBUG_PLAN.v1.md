# Abraxas-v2.0 Repository Debug Plan

```yaml
plan_id: DEBUG_PLAN.v1
drafted_at: 2026-07-19
branch: chore/ws0-baseline-live-receipt
tip_at_draft: aab74b1
scope: engineering debug + CI triage (not production activation)
```

**Authority:** This plan is for *debugging and verification*. It does **not** authorize deploy unhold or production activation.

---

## 0. Current health snapshot (at draft)

| Surface | State | Notes |
|---------|--------|--------|
| Unauthorized sole-writer | **0** | Advisory checker green |
| Freeze / release | 8/8 · `CANDIDATE_APPROVED` · deploy_held | Binding |
| Activation / deploy | **DENIED** / **NO_GO** | By design |
| PR #971 CI pattern | Many **cancelled** runs + 1 **fast-ci fail** | Push storm + stale test |
| Last known fail | `test_writer_debt_triage` `assert 0 >= 1` | Fixed in `aab74b1` |
| Soft CI | `CLOSED_BY_ACCEPTANCE` | Soft gates remain |
| Design palette sync | OK | `scripts/design/validate_viz_palette_sync.py` |
| Test inventory | ~1389 `test_*.py` | Fast-CI excludes slow/integration/canon/artifact |

### CI history lesson

Recent `ci.yml` runs on this branch: **cancelled cascade** (new commits abort long `fast-ci`). Treat **push thrash as a first-class bug** in the debug process:

1. Batch commits; avoid push until a logical checkpoint.
2. One push → wait for full suite before next push.
3. Prefer `gh run watch <id>` over rapid force-fixes.

---

## 1. Failure taxonomy (how to classify issues)

| Class | Examples | First response |
|-------|----------|----------------|
| **A. Hard CI fail** | pytest red, ruff, check-organization | Reproduce locally → minimal fix → single push |
| **B. Soft / advisory** | sole-writer report, boundary advisory, neon allowlist | Log; do **not** flip fail-closed without operator |
| **C. Drift / worktree** | fast-ci exit 3, dirty `out/**` mid-run | Restore ignored dirt; re-run with clean tree |
| **D. Authority residual** | DENIED, NO_GO, Partial evidence | Not a code bug — operator process |
| **E. Env / tooling** | missing `python` vs `python3`, PATH, venv | Use `.venv/bin/python`; export PATH |
| **F. Stale assertion** | Tests requiring residual debt after cleanup | Update test to new DoD (as triage fix) |
| **G. Visual OS desync** | Console colors ≠ palette JSON | Run palette sync validator |
| **H. Scale / flaky** | Long pytest, marker warnings | Narrow with `-k` / markers first |

---

## 2. Standard reproduction kit

Always from repo root with venv:

```bash
export PATH="$(pwd)/.venv/bin:$PATH"
python -V   # expect 3.12.x from .venv

# 1) Clean tree check
git status -sb
git restore out/production_readiness/** 2>/dev/null || true   # if only re-pin dirt

# 2) Fast local gate (mirrors CI intent)
python scripts/run_fast_ci.py

# 3) Single-test isolation
python -m pytest path/to/test_file.py::test_name -vv --tb=short

# 4) Readiness advisory (fail-open)
python scripts/run_sole_writer_advisory_check.py
python scripts/run_boundary_advisory_check.py

# 5) Script organization (CI gate)
python scripts/organize_scripts.py dry-run > /tmp/org.json
# Intersect NEW root scripts/run_*.py vs moved[] (see playbook A2)

# 6) Design system
python scripts/design/validate_viz_palette_sync.py
cd apps/aal-viz-live-console && npm test -- --run && npm run build
```

**Do not** claim success if `run_fast_ci.py` was not actually executed or was truncated.

---

## 3. Playbooks by symptom

### A1 — `fast-ci` pytest FAILED

**Signals:** GitHub job red; short summary lists `FAILED tests/...`

**Steps:**

1. Copy exact nodeid from summary.
2. Local: `pytest <nodeid> -vv --tb=short`.
3. Classify: product bug vs stale assertion vs fixture/env.
4. If assertion assumes old residual debt (counts, writers, RISK open): update test to post-DoD reality **and** document why.
5. Re-run full `run_fast_ci.py` once before push.
6. **One** push; watch `gh run watch`.

**Recent case:** `test_triage_report_shape` required `classified_finding_count >= 1` after unauthorized=0 → fixed to allow 0.

---

### A2 — `check-organization` failed

**Signals:** “N changed unorganized runner scripts”

**Steps:**

1. `python scripts/organize_scripts.py dry-run` → inspect `moved[]`.
2. Diff vs `main`:
   ```bash
   git diff --name-status origin/main...HEAD -- 'scripts/run_*.py' | awk '$1=="A"{print $2}'
   ```
3. Intersection of added root runners ∩ unorganized → `git mv` into `scripts/<domain>/`.
4. Nested runners need `REPO_ROOT` on `sys.path` (see `scripts/ingest/run_oracle_*`).
5. Confirm sole-writer still authorizes `scripts/*/run_*`.

---

### A3 — Ruff / pyright

**Steps:**

1. `ruff check .` (or path from log).
2. Pyright: fast-ci uses scoped targets in `DEFAULT_FAST_CI_PYRIGHT_TARGETS` — may not cover whole monorepo.
3. Prefer minimal fixes; no mass reformat unless requested.

---

### B1 — Sole-writer / boundary “findings”

**If advisory `finding_count > 0`:**

1. Open `out/production_readiness/ws1/sole_writer_advisory_report.v1.json`.
2. Group by package (`core` vs `skills` vs `scripts`).
3. Core: pure-builder + `scripts/run_*` publisher.
4. Skills/afe: package policy prefixes — not silent ignore.
5. Do **not** enable fail-closed without operator approval (RISK-008).

**If finding_count = 0 but product wrong:** checker allowlist may be too broad — audit `core/production_readiness/sole_writer_check.py` authorize rules.

---

### C1 — Fast-CI drift exit (exit 3)

**Cause:** suite mutates tracked files or mid-run `out/` re-pin dirt.

**Steps:**

1. `git status` immediately after fail.
2. Discard accidental `out/**` dirt; never force-add mid-debug.
3. Re-run; advisory gates run **after** status decision by design.

---

### D1 — “Not production ready” reported as bug

**Not bugs:**

- Activation DENIED  
- Deploy NO_GO / missing CD-06..08  
- Evidence Partial / Notion not fully Verified  
- Soft CI residual accepted  

**Debug path:** operator process (token, dual-control, deploy plan) — see activation gate + candidate_deploy_readiness artifacts.

---

### E1 — `python: command not found` / PATH

Use `.venv/bin/python` or `export PATH="$(pwd)/.venv/bin:$PATH"`.  
CI uses setup-python 3.12; local must match.

---

### G1 — Console looks wrong after design-system change

1. `python scripts/design/validate_viz_palette_sync.py`
2. `cd apps/aal-viz-live-console && npm run build`
3. Confirm `@import` of `design-system/tokens/abraxas.tokens.css` and Vite `fs.allow` repo root.
4. Theme: `data-theme` on `<html>`, localStorage `abx-theme`.

---

## 4. Prioritized investigation queue (recommended order)

| Prio | Item | Why | Owner | Done when |
|------|------|-----|-------|-----------|
| **P0** | Land green `fast-ci` on tip `aab74b1` (or successor) | Unblocks PR #971 merge | Eng | Job green once without cancel |
| **P0** | Stop push-cancel loops | CI never finishes otherwise | Eng | ≥1 full suite between pushes |
| **P1** | Audit tests that hardcode residual debt counts | Same class as triage fail | Eng | Grep + fix or mark intentional — **done 2026-07-19** (see §5 results) |
| **P1** | Catalog soft gates vs hard gates in CI | Prevent false “all soft” mental model | Eng | Doc table in STATUS/README |
| **P2** | RISK-008 advisory→fail-closed readiness window | Product quality | Operator + Eng | Written criteria + green window |
| **P2** | Evidence SHA re-pin policy | Stale `repository_sha` confuses debug | Eng | Document when to re-pin |
| **P2** | Design-system palette auto-sync in CI | Drift between JSON and TS | Eng | Optional CI step (non-blocking first) |
| **P3** | Full pytest mark hygiene (`canon`/`security` unknown marks) | Warning noise | Eng | pytest.ini markers registered |
| **P3** | Historical archive RISK-004 quarantine audit | Hygiene | Eng | Confirm quarantine artifact current |
| **P3** | Notion strategic rows still Partial/Missing | Comms | Operator | Per-row DoD, not agent auto-Verified |
| **Hold** | Activation / deploy unhold | Not debug | Operator dual-control | Out of band |

---

## 5. Targeted greps for “stale residual” tests (P1)

Run after green tip to prevent next surprise:

```bash
# Tests that may still assume debt remaining
rg -n 'finding_count\s*>=\s*[1-9]|classified_finding_count\s*>=\s*[1-9]|assert .* > 0' tests/ -g '*sole*' -g '*writer*' -g '*debt*' -g '*boundary*'

# Fail-closed assumptions
rg -n 'fail_closed_ready.*True|ABRAXAS_BOUNDARY_FAIL_CLOSED' tests/ core/production_readiness/

# Hardcoded production-ready claims in tests
rg -n 'production_activation_authorized.*True|CANDIDATE_APPROVED.*deploy_held.*False' tests/
```

For each hit: confirm intent vs post-TD reality.

### P1 grep results (2026-07-19, tip `aab74b1`)

| Location | Assertion | Verdict |
|----------|-----------|---------|
| `tests/test_writer_debt_triage.py` | `classified_finding_count >= 0` | **OK** (fixed; was `>= 1`) |
| `tests/test_boundary_advisory_check.py` | `import_allowlist_size >= 12` | **OK** — floor on allowlist size, not residual debt |
| `tests/test_boundary_advisory_check.py` | `sensitive_import_findings == 0` | **OK** — target state |
| `tests/test_candidate_deploy_readiness.py` | `go_no_go` starts with `NO_GO` | **OK** — authority posture |
| `tests/test_release_decision.py` | CANDIDATE_APPROVED forbids activation | **OK** — authority posture |
| `fail_closed_ready is True` in tests | — | **None found** requiring true by default |
| `production_activation_authorized True` as product state | transport baseline confirms *false* | **OK** |

No further P1 residual-count landmines found in readiness/sole-writer/debt/boundary tests.

---

## 6. Component debug maps

| Subsystem | Entry | Artifacts | Common fail |
|-----------|--------|-----------|-------------|
| Sole-writer | `scripts/run_sole_writer_advisory_check.py` | `ws1/sole_writer_*.json` | New `write_canonical` in core |
| Boundary | `scripts/run_boundary_advisory_check.py` | `ws1/boundary_*.json` | Import edges |
| Freeze/release | `run_freeze_gate_scorecard` / `run_release_decision` | `ws8/*` | Missing validation receipt |
| Activation | `run_production_activation_authority_gate.py` | gate JSON | Token present but not dual-control |
| Soft CI | `run_soft_ci_gate_audit.py` | `ws6/*` | Soft mistaken for hard |
| Script org | `organize_scripts.py` | CI workflow | New root `run_*.py` |
| aal-viz | `apps/aal-viz-live-console` | npm test/build | Token import path, theme |
| Design OS | `design-system/` | registry + palette | JSON/TS desync |
| Geometry/chamfer | many `core/chamfer_*` | fast-ci pyright scope | Type errors in scoped files |

---

## 7. Debug session template (copy into PR/issue)

```markdown
### Symptom
### Class (A–H)
### Reproduce command + exit code
### Expected vs actual
### Root cause
### Fix (minimal)
### Verification (commands run)
### Residual risk
### Authority impact (none / advisory / requires operator)
```

---

## 8. What success looks like for “debug complete”

- [ ] Tip has **one** full green CI suite (fast-ci + org + aal-viz + security + commits)
- [ ] No open P0 test failures under `run_fast_ci.py` locally
- [ ] Sole-writer unauthorized still 0
- [ ] Known soft gates documented, not “silently fixed” by fail-closed
- [ ] Design palette sync OK
- [ ] Activation still DENIED unless operator process changed intentionally

---

## 9. Related docs

| Doc | Role |
|-----|------|
| `AGENTS.md` | Governance V3 workflow |
| `out/production_readiness/README.md` | Readiness posture |
| `design-system/docs/MERGE_READINESS.md` | PR merge criteria |
| `CONTINUATION_PLAN.v11.md` | Program plan |
| `design-system/docs/PHASE10_FIGMA_EXPORT.md` | Design export (non-runtime) |

---

*End DEBUG_PLAN.v1 — draft for engineering use; update when tip CI stabilizes.*
