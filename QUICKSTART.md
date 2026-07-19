# ABRAXAS v2.0 — QUICKSTART

**Time required: ~5 minutes. No external services needed.**

---

## 1. Install dependencies (read-only — no artifacts written)

```bash
pip install -r requirements.txt
```

Expected: silent or dependency resolution output. No files written to `out/`.

---

## 2. Run the safe status demo (read-only)

This command reads existing artifacts from `out/` and prints a summary of the
current operator state. It does not write anything, invoke any solver, or touch
any governance artifacts.

```bash
python scripts/demo_safe_status.py
```

Expected output (values reflect current repo state):

```
=== ABRAXAS v2.0 — SAFE STATUS DEMO ===
[READ-ONLY: no files written, no artifacts mutated]

DOCTRINE VALIDATOR
  summary_status : ok
  contract_count : 7
  seal_recommendation : seal

TRANSPORT CHAIN — CURRENT FRONTIER
  plan_status    : TRANSPORT_FIXTURE_CORPUS_CREATION_PLAN_DEFINED
  plan_stage     : FIXTURE_CORPUS_CREATION_PLAN_ONLY
  operator_id    : TRANSPORT
  fixture_count  : 15 (valid=6  invalid=4  not_computable=5)
  next_step      : TRANSPORT_FIXTURE_CORPUS_CREATION
  canonical_hash : 90183e52f9bc2602...

IMPLEMENTATION GATE
  gate_status    : TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE_READY
  computation_authorized : True
  lp_solver_authorized   : True

AUTHORITY POSTURE
  production_activation  : False
  forecast_influence     : False
  runtime_mutation       : False
  canon_promotion        : False
  shadow_lane_only       : True

=== END STATUS (read-only) ===
```

---

## 3. Run the doctrine validator (artifact-writing — writes to out/)

This is the project's CI gate. It validates governance contracts and writes a
projection artifact. It is safe but does update `out/validation/latest.json`.

```bash
python scripts/run_doctrine_validator.py
```

Expected output:

```
{"summary_status": "ok", "contract_count": 7, "seal_recommendation": "seal", ...}
```

If `summary_status` is not `"ok"`, do not proceed with new implementation work
until the contracts are clean.

---

## 4. Run targeted tests for a specific surface (test-only — no artifacts written)

Replace `transport_fixture_corpus_creation_plan` with the module you are
working on.

```bash
python -m pytest tests/test_transport_fixture_corpus_creation_plan.py -q
```

Expected output:

```
........................................................................ [ 91%]
.......                                                                  [100%]
79 passed in ...
```

---

## 5. Run lint check (read-only)

```bash
python -m ruff check core/ scripts/ tests/
```

Expected: `All checks passed!`

---

## What to look at next

- **Architecture**: `ARCHITECTURE.md` — how the layers fit together
- **Contributing**: `CONTRIBUTING.md` — how to choose and start work
- **Glossary**: `docs/GLOSSARY.md` — translation of project-specific terms
- **Governance**: `AGENTS.md` and `PLANS.md` — operator doctrine (required before code changes)

---

## What NOT to run first

| Command | Why to avoid until oriented |
|---|---|
| `python scripts/temporal/run_temporal_continuity_spine_precheck.py` | Writes to `out/`; part of a multi-step governed chain |
| `python scripts/run_research_canary_*.py` | Research-canary guardrail; touching these without operator instruction is a violation |
| `python scripts/run_canon_resume_state.py` | Writes to `out/`; read `PLANS.md` first |
| Any script not in this QUICKSTART | Read `AGENTS.md` before running unfamiliar scripts |
