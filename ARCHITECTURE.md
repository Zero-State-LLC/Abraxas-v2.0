# ABRAXAS v2.0 — ARCHITECTURE

## What this repository is

Abraxas v2.0 is a **deterministic governed symbolic execution substrate**.
It is a Python 3.12 / FastAPI codebase that implements a strict governance
layer over computational operators. No computation is permitted to run
without an explicit chain of operator-authorized artifacts. Nothing is
inferred, auto-approved, or executed adaptively.

The key design principle: **all authority is denied by default and must be
explicitly unlocked through governed artifact chains.**

---

## Mental model

```
 OPERATOR DECISION / INPUT
         │
         ▼
  contracts/canon/          ← JSON Schemas (what an artifact must look like)
         │
         ▼
     core/                  ← Python builders (how artifacts are produced)
         │
         ▼
   scripts/run_*.py         ← Runners (entry points that call core/ and write out/)
         │
         ▼
       out/                 ← Emitted artifacts (governance receipts, plans, gates)
         │
         ▼
    tests/test_*.py         ← Verifiers (replay-stable, no side effects)
```

Artifacts in `out/` are canonical state. They are not logs — they are the
authoritative record of what has been decided, planned, or gated. Each
artifact carries a `canonical_hash` that is recomputable from its content.

---

## Directory map

### `core/`

Python modules that implement the logic for each operator, artifact builder,
and governance surface. Every module is deterministic: same inputs, same
output, same hash. Core modules never write to disk themselves — they return
Python dicts that runners then serialize.

Key subdirectories:
- `core/canonical/` — the canonical JSON serializer and hash function used by
  every artifact. **Do not bypass this.**
- `core/config.py` — `RuntimePaths` class: all output file paths in one place.
  Add a `@property` here for any new artifact before writing to disk.
- `core/audit/`, `core/canary/`, `core/canary_activation/`, etc. — operator
  subsystem implementations organized by domain.

### `scripts/`

Runner scripts: `scripts/run_<name>.py`. Each runner is a thin shell around a
`core/` module. A runner loads paths from `RuntimePaths.from_env()`, calls a
`build_*` function, validates the result, and writes the artifact to `out/`.

Runners are the only entry points that write to `out/`. Do not write to `out/`
from `core/` or `tests/`.

### `contracts/canon/`

JSON Schema files: `contracts/canon/<name>.v1.schema.json`. Each schema is the
binding contract for one artifact type. The schema enforces required fields,
constant values (authority locks, status strings), and hash format. Tests
validate artifacts against schemas using `jsonschema`.

### `out/`

Emitted artifacts organized by subsystem:
- `out/metric_operator/` — metric operator chain artifacts (plans, gates,
  receipts, decision records)
- `out/research_*/` — research-canary continuity chain artifacts (P103–P130)
- `out/validation/` — doctrine validator output
- `out/canon_resume_state/` — resume pointer for the continuity chain
- `out/projections/` — non-authoritative projection surfaces (AAL-Viz, etc.)
- `out/audit/` — audit receipts and performance profiles

**Do not regenerate `out/research_canary_*` or `out/research_*/` artifacts
without explicit operator instruction.** These are the research-canary
guardrail boundary.

### `input/`

Operator decisions and fixture files:
- `input/*.json` — operator authorization decisions, seal decisions, etc.
  These are the human-provided inputs that artifact chains read and bind.
- `input/fixtures/` — test vector fixture files (when created). Currently
  planned but not yet created for the TRANSPORT chain.

### `tests/`

Test files mirror `core/` and `scripts/`. Each test file exercises one module:
- constant invariants (schema version, operator IDs, locked hashes)
- sub-builder functions (valid/invalid/NC fixture plans, authority locks)
- full build + validate round-trip
- JSON schema validation
- disk artifact presence (skipped if runner not yet executed)

Tests are **replay-stable**: they produce no side effects and can be run in
any order. Tests never write to `out/`.

### `AGENTS.md`

Operator doctrine for coding agents. **Read this before making any code
changes.** Contains the canonical edge, governance boundaries, test execution
order, and determinism rules.

### `PLANS.md`

Current canonical roadmap. Lists all implemented P-lanes (P27–P130+) and
their status. Read this before starting new implementation work to understand
where the chain currently sits.

---

## Artifact taxonomy

| Term | What it is | Where to find it |
|---|---|---|
| **Schema** | JSON contract for an artifact type | `contracts/canon/*.v1.schema.json` |
| **Artifact** | A JSON file produced by a runner | `out/` subdirectories |
| **Gate** | An artifact that explicitly authorizes (or blocks) the next step | `out/metric_operator/*_gate_*.latest.json` |
| **Decision record** | An artifact recording a human operator decision | `out/metric_operator/*_decision_record_*.latest.json` |
| **Receipt** | An artifact confirming completion of a governed step | `out/metric_operator/*_receipt_*.latest.json` |
| **Plan** | An artifact defining the structure of future work (without doing it) | `out/metric_operator/*_plan_*.latest.json` |
| **Fixture** | A JSON test vector used to verify a computation | `input/fixtures/<operator>/` |
| **Operator decision** | A human-authored JSON in `input/` that a chain reads and binds | `input/*_operator_decision.json` |
| **Canon hash** | A 64-char hex SHA-256 of the artifact's canonical JSON (minus `canonical_hash` field) | Every artifact's `canonical_hash` field |

---

## Execution lanes

| Lane | Meaning |
|---|---|
| **SHADOW** | Safe, non-authoritative; no production effect |
| **PROJECTION** | Read-only overlay; visualization only; no runtime effect |
| **OBSERVATION_ONLY** | Passive monitoring; no decisions |
| **FORECAST** | Not currently authorized; blocked |
| **PRODUCTION** | Not currently authorized; blocked |

All current work is in the **SHADOW** lane. FORECAST and PRODUCTION lanes are
explicitly denied by authority locks on every artifact.

---

## Authority lock pattern

Every artifact carries an `authority_locks` block. Locks that are `true`
describe what the artifact is permitted to do. Locks that are `false` are hard
boundaries. Example from the current TRANSPORT chain frontier:

```json
"authority_locks": {
  "advisory_only": true,
  "shadow_lane_only": true,
  "fixture_corpus_creation_plan_only": true,
  "transport_computation_implementation_authorized": true,
  "lp_solver_invocation_authorized_for_test_vectors": true,
  "fixture_files_created": false,
  "computation_executed": false,
  "emits_metric_values": false,
  "forecast_influence": false,
  "production_activation": false,
  "canon_promotion": false,
  "runtime_mutation": false
}
```

The `false` locks are enforced in both the Python builder and the JSON Schema.
Any artifact that sets a `false` lock to `true` will fail schema validation and
the Python validator will raise.

---

## Current active chain: TRANSPORT metric operator

The TRANSPORT chain is the current implementation frontier (as of 2026-05-30):

```
PR #365  TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORD_001  ✓
PR #366  TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE_001               ✓
PR #367  TRANSPORT_FIXTURE_CORPUS_CREATION_PLAN_001                  ✓
         TRANSPORT_FIXTURE_CORPUS_CREATION                           ← next
         (fixture JSON files for 15 test vectors)
         TRANSPORT_COMPUTATION_IMPLEMENTATION                        ← future
         (LP solver implementation, bounded, SHADOW only)
```

The research-canary continuity chain (P103–P130) is complete and sealed.
Do not modify those artifacts without operator instruction.
