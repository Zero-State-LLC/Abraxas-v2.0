# CONTRIBUTING TO ABRAXAS v2.0

## Before you touch anything

**Required reading (in order):**

1. `README.md` — version posture and canonical state
2. `AGENTS.md` — operator doctrine and governance boundaries
3. `PLANS.md` — current canonical roadmap and P-lane edge
4. `ARCHITECTURE.md` — how the layers fit together
5. `QUICKSTART.md` — safe demo path and first commands
6. `docs/GLOSSARY.md` — translation of project-specific terms

Do not modify code until you have read all five documents above.

---

## Choosing your work type

### Type 1 — Bug fix or test fix

A failing test, a broken runner, a hash mismatch, or a schema violation.

**Safe starting point:**

```bash
python -m pytest tests/test_<affected_module>.py -q
python -m ruff check core/<affected_module>.py
```

**Rules:**
- Fix only the specific failing surface.
- Do not regenerate unrelated `out/` artifacts.
- Do not touch `out/research_canary_*` or `out/research_*/`.
- Re-run the doctrine validator after your fix:
  ```bash
  python scripts/run_doctrine_validator.py
  ```

---

### Type 2 — Documentation-only patch

Updating `README.md`, `PLANS.md`, `AGENTS.md`, `ARCHITECTURE.md`,
`QUICKSTART.md`, `CONTRIBUTING.md`, or `docs/GLOSSARY.md`.

**Rules:**
- No `out/` artifacts regenerated.
- No `core/` or `scripts/` logic changed.
- No authority flags modified.
- Run doctrine validator to confirm nothing broke:
  ```bash
  python scripts/run_doctrine_validator.py
  ```
- Confirm research-canary artifacts untouched:
  ```bash
  git diff HEAD -- out/research_canary*
  ```

---

### Type 3 — New metric operator (artifact-chain continuation)

Adding the next step in the TRANSPORT, GEODESIC, CHAMFER, or WASSERSTEIN
chain — or starting a new operator from scratch.

**Required before starting:**
- Read `out/canon_resume_state/latest.json` for the current resume pointer.
- Read the most recent artifact in the chain you are extending.
- Confirm gate hashes in your new artifact match the prior artifact's
  `canonical_hash`.

**Pattern to follow:**

Every artifact-chain step has the same four files:

```
contracts/canon/<name>.v1.schema.json     ← JSON Schema
core/<name>.py                            ← builder + validator
scripts/run_<name>.py                     ← runner (writes to out/)
tests/test_<name>.py                      ← tests (replay-stable)
```

Plus two config changes:
- `core/config.py` — add `@property` for the new output path
- `.gitignore` — add `!out/metric_operator/<name>.latest.json` exception

**Source hash binding:** Your new artifact must read the prior artifact from
disk and verify its `canonical_hash`. Hard-code the expected hash as a
constant at the top of your `core/<name>.py`. If the hash does not match at
runtime, raise immediately.

**Authority locks:** New steps inherit the locks of the prior step and may
unlock only what the prior gate explicitly authorizes. Do not add new
`true` locks that were not authorized upstream.

**Forbidden tokens:** The following substrings must not appear in any string
value in the artifact (enforced by `_check_no_forbidden`):
`executable`, `callable`, `runtime`, `scheduler`, `cache`, `forecast`,
`scoring`, `metric-computation`, `metric-value`, `geodesic-distance`,
`numpy`, `scipy`, `gpu-kernel`, `dijkstra-execution`,
`shortest-path-computation`, `fixture-file`, `manifest-file`, `schema-file`.

Note: `generated_by` values use underscores, never hyphens (e.g.
`TRANSPORT_FIXTURE_CORPUS_CREATION_PLAN_BUILDER`, not
`TRANSPORT-FIXTURE-CORPUS-CREATION-PLAN-BUILDER`).

---

### Type 4 — Schema or contract change

Modifying a `contracts/canon/*.v1.schema.json` or adding a new schema.

**Rules:**
- Schema changes are breaking changes. If the schema changes, every artifact
  produced under the old schema must be re-validated or re-emitted.
- Create a new schema version (`*.v2.schema.json`) rather than mutating an
  existing sealed schema.
- Run the full test suite after any schema change:
  ```bash
  python -m pytest tests/ -q
  ```

---

## Hard stops — do not start without operator instruction

These actions require an explicit operator decision artifact before proceeding:

- **Spine refresh** (`run_temporal_continuity_spine_precheck.py` or anything
  downstream in that chain) — must not be triggered autonomously.
- **Research-canary artifacts** — `out/research_canary_*` and
  `out/research_*/` are a sealed boundary. Any modification requires a
  separate operator-authorized governance design.
- **FORECAST lane activation** — blocked. No artifact currently authorizes it.
- **Production activation** — blocked. `production_activation: false` on every
  artifact.
- **Canon promotion** — blocked. `canon_promotion: false` on every artifact.
- **P43 surface lanes** — blocked. `p43_surface_lanes_authorized: false`.
- **Any `run_research_canary_*.py` script** — do not run without explicit
  instruction. These scripts touch the research-canary guardrail boundary.

---

## Validation checklist before opening a PR

```bash
# 1. Run targeted tests for your touched surface
python -m pytest tests/test_<your_module>.py -q

# 2. Lint check
python -m ruff check core/<your_module>.py scripts/run_<your_module>.py tests/test_<your_module>.py

# 3. Doctrine validator
python scripts/run_doctrine_validator.py

# 4. Confirm research-canary untouched
git diff HEAD -- out/research_canary*

# 5. Confirm no unintended out/ changes
git diff HEAD -- out/
```

All five must pass cleanly before a PR is opened.

---

## PR conventions

- **Branch name**: `<artifact-id>-<sequence>` (e.g.
  `transport-fixture-corpus-creation-plan-001`)
- **PR title**: `<ARTIFACT_ID_UPPERCASE>` (e.g.
  `TRANSPORT_FIXTURE_CORPUS_CREATION_PLAN_001`)
- **Squash merge** only — no merge commits.
- **Commit message** must include `canonical_hash=<64-char-hex>` for any
  artifact emitted.

---

## Asking for help

If the current state is ambiguous, run the safe status demo first:

```bash
python scripts/demo_safe_status.py
```

Then read `out/canon_resume_state/latest.json` for the current resume pointer.
Both are read-only and will not modify any artifacts.
