# ABRAXAS v2.0 — ARCHITECTURE

## What this repository is

**Ownership (decided 2026-10-10):** this is the doctrine and reference repository. Everything below that executes is **reference code**, not a supported product. The canonical execution repository is [`Zero-State-LLC/Abraxas`](https://github.com/Zero-State-LLC/Abraxas); see [`docs/SIBLING_REPOS.md`](docs/SIBLING_REPOS.md).

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
Architecture as it actually executes, code tiers, single owners, and the findings register:
[`docs/architecture/ARCHITECTURE_COHERENCE_AUDIT_001.md`](docs/architecture/ARCHITECTURE_COHERENCE_AUDIT_001.md) (2026-10-10).

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

## Language / runtime boundary

The canonical implementation boundary is:

> **Python owns semantics. Rust owns mechanics.**

Python (3.12) is the primary substrate for all rapidly evolving semantic and
research surfaces: CFAR, Belief Graph reasoning, SHADOW logic, FORECAST
inference, Eval/Brier analysis, RDI research logic, model/API adapters,
orchestration, and exploratory work. These are not migration candidates.

Rust is a **conditional** candidate only for narrow, stable, high-assurance
mechanical contracts — canonical serialization/hashing, deterministic event
replay, high-throughput ingest, deterministic simulation kernels, portable
operator tooling — and only when a measured engineering need justifies a
systems boundary. The current repository contains **no Rust code**; every
candidate below is an audit posture, not an implementation commitment.

Audit posture (SYS-RUST-0, 2026-08-10):

| Candidate | Existing implementation | Verdict |
|---|---|---|
| `abx-canonical` | `core/canonical/json.py` — single authority, ~996 importers, deterministic, no measured bottleneck | **REUSE_PYTHON** |
| `abx-replay` | `core/replay_execution/`, `core/replay_ledger/`, `core/settlement/` — canonical contract layers exist; interface convergence is Python-side work | **REUSE_PYTHON / DEFER** |
| `abx-ingest` | `core/ingest/` — scheduler/receipt surfaces; no throughput or concurrency evidence | **NOT_COMPUTABLE / DEFER** |
| `abx-sim` | No simulation kernel or Noema environment exists in this repository | **DEFER** |
| `abx-cli` | `python -m abraxas` product CLI; no portable-binary need evidenced | **REUSE_PYTHON** |

Rules if a candidate is ever elevated: no Rust rewrite of working Python; no
FFI boundary merely to introduce Rust; a Rust component must consume the same
contracts, preserve canonical schema/provenance/causal-exposure semantics
byte-for-byte across the language boundary, and pass cross-language golden
tests. Rust type safety, memory safety, and deterministic replay strengthen
**technical settlement** only — they are never evidence of semantic or
empirical validity.

---

## Three-Settlement Doctrine

Every important Abraxas capability seeks three independent settlements:

| Settlement | Question | Verified by |
|---|---|---|
| **Empirical** | Is the claim supported by evidence? | Declared forecasts, falsification criteria, resolved settlement, calibration |
| **Technical** | Does the instrument perform to specification? | Determinism, schemas, tests, replay, provenance, canonical artifacts |
| **Economic** | Does it produce consequences someone adopts or pays for? | Real-world usefulness, adoption, operational value |

These must not substitute for one another:

```text
TECHNICAL_SUCCESS  != SCIENTIFIC_VALIDITY
COMMERCIAL_SUCCESS != CAUSAL_VALIDITY
SCIENTIFIC_VALIDITY != PRODUCT_DEMAND
REPLAY_SUCCESS     != MODEL_CORRECTNESS
```

Evidence environments remain separated: **LAB** (synthetic fixtures,
controlled simulation), **RESEARCH** (methodologically qualified evidence),
**FIELD** (commercial/operational observation). FIELD evidence generates
hypotheses; it does not automatically become scientific validation. The
flywheel is `FIELD → hypothesis → LAB → RESEARCH → validated method → FIELD`,
with ABX-mediated provenance preventing the loop from counting itself as
independent confirmation.

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

**Supported product spine (target).** As of 2026-10-10 the executable spine is
`CLI/API → run_advisory_spine → activation → validation → Oracle→Alembic bridge →
Alembic advisory → canonical_hash`; `InputEnvelope`, `BeliefGraph` and
`ArtifactRepository` are not yet on that path (audit §3):

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
output, same hash. The intended rule is that core builders return Python dicts
and runners serialize them. In practice many governed-lane builders write
directly (about 470 core files write to disk as of 2026-10-10); new code should
follow the intended rule. Code tiers are defined in the coherence audit §4.

Key subdirectories:
- `core/canonical/` — the canonical JSON serializer and hash function used by
  every artifact. **Do not bypass this.**
- `core/config.py` — `RuntimePaths` class: registry of output file paths
  (`OUT_DIR`/`CONTRACTS_DIR`, cwd-relative). It is not the only path source:
  `core/settings.py` `RuntimeSettings` (`ABRAXAS_*`, repo-root relative) is the
  newer settings owner, and many builders still hard-code `out/` paths.
  Consolidation onto `RuntimeSettings` is tracked as audit finding A5.
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
- `core/forensics/` — **Memetic forensics spine** (SHADOW): EvidencePack →
  PropagationGraph → ForensicDispositionPacket → MemeticOpsGate (always DENIED
  in slice C). CLI: `python -m abraxas os forensics …`. Mission map:
  `docs/architecture/MEMETIC_FORENSICS_MISSION_001.md`.
- `core/instantiation/` — **RDI composition builders** for fixture-only
  InstantiationState/Transition and InterventionDeclaration. Doctrine:
  `docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md`.
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
- `contracts/forensics/` — Memetic forensics v0 schemas (propagation, disposition,
  ops gate, route intent, Level99 seed, AAL-Viz forensic projection).
- `contracts/instantiation/` — Fixture RDI contracts
  (`InstantiationState.v1`, `InstantiationTransition.v1`, `InterventionDeclaration.v1`).

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

Replay-stable verifiers. Intended rule: tests never write to the working
tree's `out/`. Currently violated: `tests/conftest.py` seeds fixture artifacts
into `out/audit` for every session, and some skill-evolution tests write into
`out/operator_input/` (audit findings G3/G10).

### `AGENTS.md`

Operator doctrine for coding agents. **Read this before making any code changes.**

### `PLANS.md`

Current canonical roadmap.

---

## Recent Advisory Surfaces

These surfaces remain **advisory / shadow** unless a later operator gate elevates
them. Replace-block live status: [`STATUS.md`](STATUS.md).

### 2026-07-31 → 2026-08-10

| Surface | Status | Notes |
|---------|--------|-------|
| **RDI / Instantiation** | **PARTIAL** on main | Doctrine + reuse audit + fixture state/transition + intervention declaration; Fable handoff for continuation; no Instantiation Depth formula; #1096 · **1.178.0** |
| **Memetic forensics C+C′+C6** | **ON MAIN (SHADOW)** | Pipeline, disposition, propagation, CLI, AAL-Viz project; **OpsGate always DENIED**; #1079–#1081 |
| **Ops D0 / D2** | **ON MAIN (SHADOW)** | Route intent + Level99 content seed (no publish); gate DENIED; #1082–#1083 |
| **AI OS Slice G / P4** | **DEFINED** · eng IN PROGRESS | Consumption hardening + operator handoff; #1098 |
| **OmegaClaw** | **ADVISORY** | Concept integration + symbolic plan; #1095 |
| Collaboration board | Process | GitHub Project + CONTRIBUTING labels; #1102 |

### 2026-07-23 baseline (still current)

| Surface | Status | Notes |
|---------|--------|-------|
| Belief Graph + SignalGraph GSP | HARNESS_VERIFIED_ADVISORY | Contractive confidence fixed-point (local stub); SignalGraph.v1 frozen |
| Zone Isolation Policy (T0–T4) | Sealed | Residual YGGDRASIL nodes default to T0 (leave unmapped) |
| Phase Percolation + zone bridge | PARTIAL + ZONE_BRIDGE_ADVISORY | Local dry-run validated; no schema mutation |
| Codegen Intelligence Spine | Hygiene-only scope | Full spine still gap-analysis-plan ready; expansion operator-gated |
| Shared Multi-Agent Engineering Contract | CANON-ACTIVE | Grok ↔ Codex peer collaboration rules |
| **Soft Facades (`core/hygiene/`)** | **ON MAIN (advisory)** | OutputHygieneReceipt, YggdrasilScanReceipt, CommonPipelineReceipt, ProofPairReceipt + checklist. Optional observability only; `execution_authority=False`; net catalog delta = 0 |

Local shadow stubs (GSP, zone bridge) were kept outside this repository; no
`artifacts/shadow/` directory exists here. Soft Facades live under
`core/hygiene/` as optional imports only; nothing imports or tests them yet
(audit finding S8).

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

Producer systems (originally Grok and Codex; since then also Claude, Cursor
and Hermes agents) are peer collaborators. Neither is supervisory. Routing for
delegated or peer work is [`AGENTS.md`](AGENTS.md) §11. Required behaviors:
- Inspect existing peer work before changing overlapping surfaces
- Prefer complementary workstreams
- Tag durable artifacts with `producer_system`
- Resolve conflicts via contracts, tests, lineage, and operator intent
- Operator retains sole authority over merge and canon decisions

Full text lives in the Abraxas Master System (AAL Canon) Notion page.
