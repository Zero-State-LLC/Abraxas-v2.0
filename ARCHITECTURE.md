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
- `core/yggdrasil/` — route graph models, validator, and runtime topology.
- `core/belief_graph/` — Belief Graph contracts and builders (SignalGraph.v1 frozen).
- `core/alembic/` — **Alembic Spine** advisory multi-architecture orchestration
  (taxonomy, registry, eligibility router, adapters, verification, fusion,
  shadow compare, proposal-only meta-optimization). Status:
  `ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS`. See `docs/alembic/ALEMBIC_SPINE.md`.
- `core/phase_percolation_engine_stub.py` — advisory temporal regime surface.
- `core/hygiene/` — **optional Soft Facade advisory receipts** (OutputHygiene,
  YggdrasilScan, CommonPipeline, ProofPair + uniform checklist). Pure
  observability composites; individual runes remain the sole authority.
  `execution_authority` is hard-coded `False`; no production wiring.

### `scripts/`

Runner scripts: `scripts/run_<name>.py`. Each runner is a thin shell around a
`core/` module. A runner loads paths from `RuntimePaths.from_env()`, calls a
`build_*` function, validates the result, and writes the artifact to `out/`.

Runners are the only entry points that write to `out/`. Do not write to `out/`
from `core/` or `tests/`.

### `contracts/`

- `contracts/canon/` — JSON Schema files for core artifacts.
- `contracts/belief_graph/` — Belief Graph packet and SignalGraph.v1 (frozen).
- `contracts/phase_percolation/` — PhaseRegimeObject.v1 and TemporalFormula.v1.
- `contracts/yggdrasil/` — Route graphs, binding matrix, coupling map, Shadow Map.v1.
- `contracts/runes/` — Rune catalog and bind/merge receipt schemas.
- `contracts/alembic/` — Alembic task/contribution/routing/fusion schemas, registry snapshot, router policy, rune proposals (non-live).

### `out/`

Emitted artifacts organized by subsystem. **Do not regenerate sealed research-canary
or continuity-spine artifacts without explicit operator instruction.**

### `skills/`

Class-level umbrella skills are the primary extension and automation mechanism.
Each skill declares its contract in `SKILL.md` (YAML frontmatter + Overview,
When to Use, workflow, guardrails, verification, common pitfalls, references).
Session/campaign detail lives in `references/`.

Notable research/catalog example:
- `modular-synth-catalog-research` — autonomous modular synthesizer brand/module cataloging (767+ brands, full provenance tiers, source rotation, Obsidian + JSON master catalog, PATCHHIVE integration paths). See its `SKILL.md` and `references/`.

See also workflow umbrellas (`abraxas-jamon-agentic-workflow`, `abraxas-master-loop-workflow`) and supporting intelligence skills. Prefer extending class-level SKILL.md + references/ over narrow one-offs.

### `input/`

Operator decisions and fixture files.

### `tests/`

Replay-stable verifiers. Tests never write to `out/`.

### `AGENTS.md`

Operator doctrine for coding agents. **Read this before making any code changes.**

### `PLANS.md`

Current canonical roadmap.

---

## Recent Advisory Surfaces (2026-07-23)

These surfaces were formalized under the Shared Multi-Agent Engineering Contract
(`producer_system=GROK`) and sealed by operator. They remain
**advisory / shadow** unless a later operator gate elevates them.

| Surface | Status | Notes |
|---------|--------|-------|
| Belief Graph + SignalGraph GSP | HARNESS_VERIFIED_ADVISORY | Contractive confidence fixed-point (local stub); SignalGraph.v1 frozen |
| Zone Isolation Policy (T0–T4) | Sealed | Residual YGGDRASIL nodes default to T0 (leave unmapped) |
| Phase Percolation + zone bridge | PARTIAL + ZONE_BRIDGE_ADVISORY | Local dry-run validated; no schema mutation |
| Codegen Intelligence Spine | Hygiene-only scope | Full spine still gap-analysis-plan ready; expansion operator-gated |
| Shared Multi-Agent Engineering Contract | CANON-ACTIVE | Grok ↔ Codex peer collaboration rules |
| **Soft Facades (`core/hygiene/`)** | **ON MAIN (advisory)** | OutputHygieneReceipt, YggdrasilScanReceipt, CommonPipelineReceipt, ProofPairReceipt + checklist. Optional observability only; `execution_authority=False`; net catalog delta = 0 |

Local shadow stubs (GSP, zone bridge) exist under `artifacts/shadow/` and are
not yet promoted to the main repository tree. Soft Facades live under
`core/hygiene/` as optional imports only.

---

## Artifact taxonomy

| Term | What it is | Where to find it |
|---|---|---|
| **Schema** | JSON contract for an artifact type | `contracts/**/*.v1.schema.json` |
| **Artifact** | A JSON file produced by a runner | `out/` subdirectories |
| **Gate** | An artifact that explicitly authorizes (or blocks) the next step | `out/**/*_gate_*.latest.json` |
| **Decision record** | An artifact recording a human operator decision | `out/**/*_decision_record_*.latest.json` |
| **Receipt** | An artifact confirming completion of a governed step | `out/**/*_receipt_*.latest.json` |
| **Plan** | An artifact defining the structure of future work (without doing it) | `out/**/*_plan_*.latest.json` |
| **Shadow Map** | Advisory hygiene proposal only (no execution) | `contracts/yggdrasil/shadow_map.v1.schema.json` |
| **Soft Facade** | Optional composite receipt over existing runes (observability only) | `core/hygiene/` |
| **Canon hash** | 64-char hex SHA-256 of the artifact's canonical JSON | Every artifact's `canonical_hash` field |

---

## Execution lanes

| Lane | Meaning |
|---|---|
| **SHADOW** | Safe, non-authoritative; no production effect |
| **PROJECTION** | Read-only overlay; visualization only; no runtime effect |
| **OBSERVATION_ONLY** | Passive monitoring; no decisions |
| **FORECAST_GATED** | Requires explicit forecast boundary validation |
| **GOVERNANCE** | Review gates, validation, operator review |
| **FORECAST / PRODUCTION** | Not currently authorized; blocked |

All current work remains in the **SHADOW** lane unless an explicit operator
gate elevates it.

---

## Authority lock pattern

Every artifact carries an `authority_locks` (or equivalent) block. Locks that
are `false` are hard boundaries enforced by both Python validators and JSON
Schema. Any attempt to set a locked field to `true` fails validation.

---

## Multi-Agent Engineering Contract (summary)

Grok and Codex are peer collaborators. Neither is supervisory. Required
behaviors:
- Inspect existing peer work before changing overlapping surfaces
- Prefer complementary workstreams
- Tag durable artifacts with `producer_system`
- Resolve conflicts via contracts, tests, lineage, and operator intent
- Operator retains sole authority over merge and canon decisions

Full text lives in the Abraxas Master System (AAL Canon) Notion page.
