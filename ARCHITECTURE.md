# ABRAXAS v2.0 — ARCHITECTURE

## What this repository is

Abraxas v2.0 is a **deterministic governed symbolic intelligence substrate**
(Python 3.12 / FastAPI). It preserves provenance, schema validation, and
fail-closed authority locks while operating under **Governance V3**
implementation-first development.

Authority is **lane-based**, not a universal pre-computation artifact chain:

| Lane | Default |
| --- | --- |
| `LOCAL_DEV` | allowed (no authorization packet) |
| `SANDBOX` | allowed when isolated and reversible |
| `INTERNAL_CANARY` | conditional |
| `EXTERNAL_PRODUCTION` | operator-gated |

Runtime policy module: [`core/governance/activation_policy.py`](core/governance/activation_policy.py).
Bounded policy doc: [`docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md`](docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md).
Production convergence target: [`docs/architecture/PRODUCTION_TARGET_ARCHITECTURE_001.md`](docs/architecture/PRODUCTION_TARGET_ARCHITECTURE_001.md).

Hard boundaries remain: no autonomous canon promotion, no silent
SHADOW→FORECAST escalation, no fabricated evidence, no external production
deploy without an explicit operator decision.

Representation-driven instantiation is an analytical doctrine within this
architecture, not a parallel subsystem. It reuses CFAR, ingest, Belief Graph,
FORECAST, settlement, provenance, and activation surfaces to distinguish a
represented construct from evidence of its causal implementation. Canonical
semantics and current implementation gaps are defined in
[`docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md`](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md).

---

## Mental model

```
 OPERATOR / API / CLI INPUT
         │
         ▼
  contracts/                ← JSON Schemas (what an artifact must look like)
         │
         ▼
     core/                  ← Pure builders + application orchestration
         │
         ▼
   scripts/ / apps/api      ← Thin runners / service adapters (disk I/O)
         │
         ▼
       out/                 ← Emitted artifacts (classified; not all are domain state)
         │
         ▼
    tests/test_*.py         ← Verifiers (replay-stable, no side effects)
```

**Supported product spine (target):**

```text
InputEnvelope → Ingest → Evidence → BeliefGraph
  → [AlembicSpine optional] → Oracle → AdvisoryResult
  → ArtifactRepository → CLI/API
```

Alembic Spine (`core/alembic/`) is an **optional advisory specialist** for
multi-architecture routing/fusion — not a parallel product kernel.

Artifacts in `out/` carry `canonical_hash` provenance. Only designated
canonical domain artifacts and governance decisions should influence current
canonical state; audit, build, plan, and historical receipts are evidence
(see ADR-0018). Historical operator-review chains are archived under
Governance V3 and are not required for routine LOCAL_DEV/SANDBOX work.

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
- `core/cfar.py` — **CFAR** construct-first analytical reasoning gate (deterministic
  route before evidence retrieval; advisory research surface). See
  `docs/research/CFAR_CONSTRUCT_FIRST_REASONING_001.md`.
- `core/hygiene/` — **optional Soft Facade advisory receipts** (OutputHygiene,
  YggdrasilScan, CommonPipeline, ProofPair + uniform checklist). Pure
  observability composites; individual runes remain the sole authority.
  `execution_authority` is hard-coded `False`; no production wiring.

### `scripts/`

Runners are **domain-organized**: `scripts/<domain>/run_*.py` (mass-org complete).
Root keeper: `scripts/run_fast_ci.py`. See `scripts/README.md` and
`python scripts/organize_scripts.py status` → `complete: true`.

Historical note: older docs may say root-only `scripts/run_<name>.py`. Each runner is a thin shell around a
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
- `contracts/cfar/` — ConstructPacket.v1 schema for CFAR.
- `contracts/engineering/` — multi-agent companion schemas (e.g. AgentArtifactMetadata.v1).

### `design-system/`

Visual Operating System: tokens, brand, system icons, engineering runes, components.
**AAL-Viz projection pack** (`design-system/aal-viz/`) — authored identity, status glyphs,
runes, diagrams, motion, and fields for the live console (batches 0–4). Projection-only;
does not grant execution authority. See `design-system/aal-viz/README.md`.

### `apps/`

- `apps/api/` — FastAPI service factory (`create_app`); supported OpenAPI surface frozen.
- `apps/aal-viz-live-console/` — Vite/React projection console (LOCAL_DEV).

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

Semantic inference lanes (orthogonal to activation lanes above):

| Lane | Meaning |
|---|---|
| **SHADOW** | Safe, non-authoritative; no production effect |
| **PROJECTION** | Read-only overlay; visualization only; no runtime effect |
| **OBSERVATION_ONLY** | Pure monitoring; no decisions |
| **FORECAST_GATED** | Requires explicit forecast boundary validation |
| **GOVERNANCE** | Review gates, validation, operator review |
| **FORECAST / PRODUCTION** | Inference authority; not granted by LOCAL_DEV/SANDBOX alone |

Advisory and SHADOW outputs remain non-authoritative unless an explicit
promotion path elevates them. Activation-lane allowance for local/sandbox
engineering does **not** grant FORECAST or EXTERNAL_PRODUCTION authority.

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
