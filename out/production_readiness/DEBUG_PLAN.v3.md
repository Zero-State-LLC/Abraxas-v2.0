# Abraxas-v2.0 Whole-Repo Debug Plan v3

```yaml
plan_id: DEBUG_PLAN.v3
supersedes: DEBUG_PLAN.v2
drafted_at: 2026-07-19
branch: main
repository_sha: f976c2a9b8969ff0908c264cb87fec7f7cb161fa
scope: whole-repository engineering debug after scripts org complete
production_activation_authorized: false
deploy_readiness: NO_GO
activation_gate: DENIED
scripts_organization: COMPLETE
related_plan: CONTINUATION_PLAN.v16
```

**Authority:** Debug and verification only. Does **not** authorize deploy unhold or production activation.  
**Supersedes:** `DEBUG_PLAN.v2` (pre–mass-org completion).  
**Companion:** `CONTINUATION_PLAN.v16` (program next steps).

---

## 0. Whole-repo health snapshot (live reaudit 2026-07-19)

### Scale

| Surface | Count |
|---------|------:|
| `tests/test_*.py` | ~1361 |
| `core/**/*.py` | ~1431 |
| `scripts/**/run_*.py` | **710** (709 domain + 1 root keeper) |
| `contracts/**` files | ~735 |
| Organize status | **`complete: true`**, unorganized **0** |

### Live gates (this reaudit)

| Gate | Result | Evidence |
|------|--------|----------|
| Unauthorized sole-writer | **0** | `scripts/readiness/run_sole_writer_advisory_check.py` @ tip |
| Script organization | **COMPLETE** | `python scripts/organize_scripts.py status` |
| Residual packages | **CLOSED_BY_POLICY** | prior readiness package |
| Soft CI residual | **CLOSED_BY_ACCEPTANCE** | prior readiness package |
| Freeze / release / activation / deploy | Unchanged held posture | `CANDIDATE_APPROVED` · DENIED · NO_GO |
| Ruff (scoped sample) | **pass** | production_readiness + fast_ci |
| Scripts PRs #972–#975 | **MERGED** | mass-org + finish + hygiene |

### Closed since DEBUG_PLAN.v2

| Issue | Resolution |
|-------|------------|
| ~435+ unorganized root `run_*` | Waves 1–3 + finish (#972–#974) |
| Sole-writer domain auth for nested runners | Generalized `is_authorized_writer` |
| Stdlib `operator` shadowing | No `scripts/operator/__init__.py` |
| Post-org inventory/DX | #975: runtime inventory, baseline counts, AGENTS/CONTRIBUTING |
| check-organization for new root runners | Still enforces; historical root debt **gone** |

### Risk board (unchanged posture)

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

---

## 1. Failure taxonomy (post-org)

| Class | Meaning | First move |
|-------|---------|------------|
| **A** Hard CI | pytest / ruff / org / aal-viz red | Reproduce → minimal fix → one push → wait |
| **B** Soft / advisory | sole-writer, boundary, neon allowlist | Log only; no fail-closed flip |
| **C** Drift / dirt | fast-ci exit **3**, dirty tracked `out/` | Restore dirt; pin generators; clean re-run |
| **D** Authority residual | DENIED / NO_GO / Partial | Not a product bug |
| **E** Environment | PATH, python, venv, node, Hermes PYTHONPATH | `.venv/bin`; `env -u PYTHONPATH` |
| **F** Stale assertion | DoD moved, test didn’t | Update test with rationale |
| **G** Visual desync | palette / tokens / CSS | `validate_viz_palette_sync` + build |
| **H** Scale / noise | 1.3k+ tests | Narrow with `-k` / markers |
| **I** ~~Historical org debt~~ | **CLOSED** | Status complete; only fail new root `run_*` |
| **J** Ghost plan paths | Strings to never-landed runners | Inventory; do not invent files |
| **K** Local fixture / out/ incomplete | Bundle/topology tests fail without full `out/` corpus | Compare to CI; seed fixtures or mark env |
| **L** Cross-language parity | Schema vs TS symbol mismatch | Align enum / TEMPORAL_OPERATIONS |

---

## 2. Live findings (this reaudit)

### 2.1 Class K — aal-viz projection tests (local / incomplete out)

| Test | Symptom | Hypothesis |
|------|---------|------------|
| `test_operator_platform_maps_pr959_surfaces` | `production_slice` payload `None` | Bundle builder fail-closed without full source receipts |
| `test_yggdrasil_topology_sidecar_is_published_and_embedded` | `KeyError: 'CONTRACT'` | Topology node_class_counts shape / empty corpus |
| Related delta/alerts tests | Missing section keys | Same family |

**Notes:** Reproduced on clean `main` worktree with same env → **not** introduced solely by path moves. CI `fast-ci` on merge PRs was green (marker subset / different out state).  

**First move:**  
1. Run builder: `python scripts/viz/build_aal_viz_projection_bundle.py`  
2. Diff local vs CI fixture expectations  
3. Either seed minimal `out/` fixtures for tests or mark as needing integration corpus  

**Smallest PR candidate:** `test(aal-viz): fixture-stabilize projection-bundle operator platform tests`

### 2.2 Class L — cross-language parity

| Test | Symptom |
|------|---------|
| `test_cross_language_parity_is_confirmed` | `PARITY_FAILED`; symbol **`UNCHANGED`** = **MISMATCH** |

**Root cause (confirmed):**  
- Python audit list includes `UNCHANGED` in `TEMPORAL_OPERATIONS`  
- Schema dump of `aal_viz_operator_platform_projection.v0.2.schema.json` does **not** contain the string `UNCHANGED`  
- TS may validate with a set that includes `UNCHANGED` separately  

**First move:** Align contract: add `UNCHANGED` to schema enum **or** drop from Python parity list if not in contract. Prefer schema truth + TS + Python single source.

**Smallest PR candidate:** `fix(aal-viz): align UNCHANGED temporal op across schema/TS/parity audit`

### 2.3 Class J — ghost plan paths (~129 refs)

References to `scripts/run_*.py` (or nested) where **no file exists**, e.g.:

| Area | Examples |
|------|----------|
| Codegen plans | `scripts/run_codegen_contract_audit.py`, `scripts/run_abx_codegen_intelligence_spine.py` |
| Belief advisory | `scripts/run_belief_graph_engine_advisory_receipt.py` |
| Registry map | `scripts/run_temporal_coherence_evidence_restoration_planning.py` |
| Tests | Fixture names `run_foo.py`, `run_example.py`, never-landed repair runners |

**First move:** Inventory only; classify **historical plan string** vs **live producer path**. Do not create stub runners to silence strings.

**Smallest PR candidate:** `docs(core): annotate ghost runner paths as NOT_COMPUTABLE / historical` (optional, low urgency)

### 2.4 Class C — fast-ci worktree drift (watch)

| Pattern | Example |
|---------|---------|
| Exit code 3 after green pytest | Dirty tracked `out/` (e.g. fusion seal receipt_hash) during validation |

**First move:** Playbook C1; pin generator outputs when they change under domain moves.

### 2.5 Class B — advisory noise (expected)

| Surface | Mode |
|---------|------|
| Sole-writer | finding_count 0 — quiet |
| Boundary advisory | may report unregistered surfaces — fail-open |
| Neon Genie allowlist | denied probes expected — fail-open |

---

## 3. Repository map (debug by domain)

| Domain | Paths | Primary checks | Common fails |
|--------|-------|----------------|--------------|
| **Kernel / contracts** | `core/canonical/`, `contracts/` | schema tests | schema drift |
| **Runtime / execution** | `core/runtime/`, manual execution | pure-core tests | illegal `out/` writes from core |
| **Sole-writer / boundary** | `core/production_readiness/` | advisory checks | new writers |
| **Scripts (organized)** | `scripts/<domain>/` | `organize_scripts.py status`, imports | wrong domain, PYTHONPATH/`operator` |
| **Ingest / oracle** | `scripts/ingest/`, `core/oracle*` | ingest tests | ghost plan paths |
| **Canary / research** | `scripts/research/`, `core/research_canary*` | canary tests | authority locks |
| **Geometry / transport** | `scripts/geometry/`, `scripts/transport/` | scoped pyright + tests | type errors |
| **AAL-viz** | `apps/aal-viz-live-console/`, `scripts/viz/` | npm test/build, bundle builder | Class K fixtures, Class L parity |
| **Visual OS** | `design-system/` | palette sync | JSON/TS desync |
| **Hygiene gates** | `scripts/hygiene/`, `core/sync/v2_hygiene_*` | hash-chain tests | sealed path rewrites (**avoid**) |
| **Production readiness** | `out/production_readiness/` | freeze/release producers | wrong decision codes |
| **CI** | `.github/workflows/` | fast-ci, org, security | drift exit 3, soft cancel |

---

## 4. Standard whole-repo reproduction kit

```bash
cd /path/to/Abraxas-v2.0
export PATH="$(pwd)/.venv/bin:$PATH"
git checkout main && git pull

git status -sb

# Layout + sole-writer
python scripts/organize_scripts.py status
python scripts/readiness/run_sole_writer_advisory_check.py
python scripts/readiness/run_boundary_advisory_check.py

# Primary local CI mirror
python scripts/run_fast_ci.py

# Design
python scripts/design/validate_viz_palette_sync.py

# Console
cd apps/aal-viz-live-console && npm ci && npm test && npm run build && cd ../..

# Targeted pytest
python -m pytest path/to/test.py::name -vv --tb=short

# Scrub Hermes env if collection imports wrong venv
env -u PYTHONPATH -u PYTHONHOME .venv/bin/python -m pytest tests/test_foo.py
```

**CI watch (no thrash):**

```bash
gh run list --branch main --limit 5
gh run watch <run_id>
# One logical push, then wait
```

---

## 5. Playbooks (delta from v2)

### A3 — check-organization (updated)

1. `python scripts/organize_scripts.py status` must show `complete: true`.  
2. New root `scripts/run_*.py` in PR vs base → move into domain; extend `PREFIX_MAP` if needed.  
3. Nested `REPO_ROOT = parents[2]`; imports `scripts.<domain>.run_*`.  
4. Never add `scripts/operator/__init__.py`.

### C1 — Drift / dirty worktree (reinforced)

1. `git status` immediately after failed fast-ci (exit 3).  
2. If only tracked `out/` dirt from a runner → pin or restore.  
3. Re-run `python scripts/run_fast_ci.py` on clean tree.

### I1 — ~~241 unorganized~~ → **CLOSED**

Historical org debt cleared. Playbook I1 retired.

### J1 — Ghost plan paths (new)

1. Confirm path does not exist under `scripts/**`.  
2. If live producer: rewrite to real domain path.  
3. If historical/plan-only: leave or annotate; do not invent stubs.

### K1 — Local projection / topology failures

1. Confirm CI green on same SHA.  
2. If local-only, classify **K** not **A**.  
3. Fix with fixtures or CI-parity setup before treating as merge blocker.

### L1 — Parity UNCHANGED

1. Dump schema JSON + TS TEMPORAL ops + Python list.  
2. Single-source: schema enum wins.  
3. Update TS + audit list + re-run parity test.

---

## 6. Ranked smallest PRs (debug queue)

| Rank | Class | PR theme | Why first |
|------|-------|----------|-----------|
| **1** | L | Align `UNCHANGED` temporal op (schema ↔ TS ↔ parity audit) | Deterministic 1-symbol fix; clear test |
| **2** | K | Stabilize aal-viz projection-bundle tests with fixtures or skip-if-incomplete | Stops local/CI confusion |
| **3** | C | Audit generators that rewrite tracked `out/` during fast-ci | **Closed**: residual-only drift exit + write-if-changed |
| **4** | J | Inventory ghost paths; optional docs annotations | Hygiene only |
| **5** | B/D | Operator Notion: debug posture + still held | Ops, not code |

**Default eng start:** **Rank 1 (parity UNCHANGED)** — closed in #976.  
**Rank 2 closed:** projection-bundle tests skip when stabilization/yggdrasil corpus incomplete.


---

## 7. What not to debug as product bugs

| Symptom | Actual class |
|---------|----------------|
| Activation DENIED / deploy NO_GO | **D** authority |
| Sole-writer advisory noise (if rebounds) | **B** unless new unauthorized writer |
| 700+ runners “mess” | **I closed** — use `scripts/README.md` |
| Sealed hygiene hash failures after path rewrite | Self-inflicted — restore seals |
| Hermes/venv import chaos | **E** environment |

---

## 8. Plan control

| Field | Value |
|-------|--------|
| Supersedes | DEBUG_PLAN.v2 |
| Status | **ACTIVE draft for eng** |
| Companion | CONTINUATION_PLAN.v16 |
| Production activation | **Not authorized** |
| Next eng action | Rank-1 PR (UNCHANGED parity) or Rank-2 projection fixtures |

---

## 9. One-line summary

**Scripts org is done; remaining debug is aal-viz parity/fixtures, ghost plan strings, and drift hygiene—while deploy/activation stay held.**
