# ABRAXAS

![Abraxas — Governed Symbolic Intelligence](assets/hero-abraxas-readme.jpg)

**How representations become causes** · *Deterministic · Provenance-bound · Falsifiable*

> Structure before narrative. Evidence before authority. Governance before autonomy.

[![CI](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Proprietary-334155.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

| Field | Value |
|-------|--------|
| **Mission** | Make the transition from **representation → consequence** observable, measurable, forecastable, falsifiable, and—only where evidence and authority permit—engineerable |
| **Measurement doctrine** | [Representation-driven instantiation (RDI)](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md) |
| **Development doctrine** | [Three-Settlement](#three-settlement-doctrine) · science × engineering × commerce |
| **Live status** | [`STATUS.md`](STATUS.md) — replace block; do not invent readiness |
| **Product posture** | Candidate · **deploy held** · production activation **DENIED** |
| **Governance** | [Governance V3](GOVERNANCE_V3.md) · lane-based activation (ADR-0017) |
| **License** | [Proprietary](LICENSE) — all rights reserved |

**Do not claim production go-live.** Candidate ≠ activation. Merge ≠ go-live.  
**Do not claim empirical proof** of hyperstition, universal simulation/instantiation equivalence, or Instantiation Depth scores. Those remain `NOT_COMPUTABLE` until validated.

---

## What this is

**Abraxas** is a governed computational intelligence system for studying, forecasting, and eventually engineering the processes by which **representations acquire causal structure in the world**.

It is part of Applied Alchemy Labs (AAL): deterministic execution, receipt-first provenance, and human-in-the-loop sovereignty over root definitions. Default posture is **advisory / SHADOW / projection-only** unless a lane explicitly authorizes more.

It is **not** a generic chatbot wrapper, a score-of-everything dashboard, or a parallel “hyperstition engine.” Existing systems (CFAR, Oracle/ingest, Belief Graph, SHADOW/FORECAST, settlement, Brier, YGGDRASIL, Alembic, AAL-Viz, Governance V3, operator loop) **are** the RDI stack. RDI names what they collectively measure.

### The operative question

Not “is this real or simulated?”  
But: **which constitutive properties of a represented construct have become causally implemented, to what degree, through what mechanisms, and with what evidence?**

Simulation is neither proof nor disproof of instantiation. Missing measurement stays `NOT_COMPUTABLE`.

### Operational loop

```text
DEFINE → OBSERVE → MODEL → FORECAST → INTERVENE → SETTLE → UPDATE
```

| Step | Role | Primary surfaces |
|------|------|------------------|
| **DEFINE** | Construct + falsifiable bounds *before* retrieval | CFAR · `core/cfar.py` |
| **OBSERVE** | Evidence with provenance and time | Oracle / ingest · EvidencePack |
| **MODEL** | Constructs, hypotheses, state | Belief Graph · InstantiationState |
| **SHADOW** | Anomaly / drift / contamination only — does **not** explain | `core/instantiation/shadow.py` · forensics spine |
| **FORECAST** | Evidence-conditioned prediction — does **not** grant authority | Forecast contracts · Eval/Brier |
| **INTERVENE** | Bounded, authorized perturbation only | InterventionDeclaration · activation policy |
| **SETTLE** | Predicted vs observed + contamination flags | SettlementVerdict · binding bridge |
| **UPDATE** | Feed resolved evidence forward without rewriting history | Provenance / receipts · model refresh |

Doctrine: [`docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md`](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md)  
Canon (Notion, 2026-08-09): *Abraxas — Master System* · *Engineering Direction Board*

---

## Three-Settlement Doctrine

Every important capability seeks **three independent settlements**. Do not collapse them.

| Settlement | Question | Does **not** imply |
|------------|----------|--------------------|
| **Empirical** | Is the claim supported under an appropriate design? | Product-market fit |
| **Technical** | Does it work deterministically, reproducibly, under governance? | Scientific validity |
| **Economic** | Is it useful enough that someone allocates scarce resources to it? | Causal truth |

**One shared core.** Research, field/commercial, and lab/synthetic work reuse the same objects: Construct, Evidence, InstantiationState/Transition, SHADOW finding, Forecast, Intervention, Settlement, provenance, contamination.

**Evidence lanes** (preserve origin; no laundering):

- `RESEARCH` — controlled / publication-oriented  
- `FIELD` — commercial / operational  
- `LAB` — synthetic, fixture, simulation, bounded-agent  
- `INTERNAL` — engineering hygiene / internal only  

**Bidirectional loop:**  
`FIELD → candidate phenomenon → hypothesis → LAB → RESEARCH → validated method → FIELD`

Field success may generate hypotheses and product evidence; it does **not** automatically become independent scientific causal proof. ABX-mediated outcomes stay contamination-flagged for independent confirmation.

Details: [`ARCHITECTURE.md` § Three-Settlement Doctrine](ARCHITECTURE.md) · [`docs/GLOSSARY.md`](docs/GLOSSARY.md)

---

## Paired vertical slices

Do **not** sequence as “research forever, product never” or “monetize first, science later.”

Where practical, each major capability should produce:

| Expression | Example |
|------------|---------|
| **RESEARCH** | Benchmark, controlled experiment, calibration / falsification artifact |
| **FIELD** | Customer-facing analysis, decision support, audit, scenario, intervention plan |

**First paired milestone (directional):** `RDI Vertical Slice 001`

- Research: observer-intervention contamination benchmark (`RDI-EXP-001`)  
- Field: **Instantiation Audit** v0.1 (strategic intelligence wrapper)  
- Shared path: `CFAR → Evidence → InstantiationState → SHADOW → FORECAST → Intervention → Settlement`

Commerce is **one settlement surface**, not a separate commercial engine. Sell **wrappers** that solve legible problems on the same RDI core—do not lead with “buy Abraxas the mystical machine.”

Near-term product direction (strategy, not activation): Instantiation Audit · signal/operator surfaces · later software/API only after technical + field settlement mature.

Claim discipline: no marketing scientific validation from field success alone; no Instantiation Depth scores; no unsupported predictive accuracy.

---

## Epistemic firewall

Hard distinctions everywhere durable artifacts matter:

```text
OBSERVED ≠ INFERRED ≠ SPECULATIVE ≠ NOT_COMPUTABLE
```

- Narrative coherence is not evidence  
- Correlation is not causation  
- Model output is not observation  
- Simulation is not instantiation proof  
- Technical green is not empirical green  
- Economic success is not scientific truth  

**Hyperstition** (operational): *representation-driven recursive instantiation* — consequences attributable to a construct increase, modify, or preserve its later capacity for further instantiation. Belief, popularity, or self-fulfilling appearance alone is insufficient.

**Observer-intervention contamination:** Abraxas may sit inside the system it studies. Transitions record causal exposure (`INDEPENDENT` / `ABX_MEDIATED` / `MIXED` / `UNKNOWN`). ABX-mediated outcomes cannot auto-confirm the model that helped produce them.

---

## Design pillars

- **Deterministic execution** — canonical hashes, receipts, replay-stable tests  
- **Provenance-first** — source lineage and authority locks on every durable path  
- **SHADOW ≠ FORECAST** — detection separated from explanation/prediction  
- **Contract-bound operators** — schemas, fail-closed gates, no silent promotion  
- **Lane-based activation** — LOCAL_DEV / SANDBOX allowed; EXTERNAL_PRODUCTION operator-gated  
- **Reuse before invent** — close schema gaps only when gap audit proves need  

Language boundary: **Python owns semantics. Rust owns mechanics (conditional only).** No Rust in-repo today; mechanical candidates deferred unless measured need appears. See [`ARCHITECTURE.md` § Language / runtime boundary](ARCHITECTURE.md).

---

## System map (RDI-aligned)

| Layer | Surfaces | Role |
|-------|----------|------|
| **Define** | CFAR | Construct-first gate before retrieval |
| **Observe** | Oracle, ingest, EvidencePack, signal forager | Provenanced intake |
| **Model** | Belief Graph, InstantiationState/Transition | Structured state & claims |
| **Detect** | SHADOW RDI, memetic forensics | Anomaly / propagation (ops gate **DENIED**) |
| **Predict** | FORECAST, Brier / calibration | Evidence-conditioned trajectories |
| **Intervene** | InterventionDeclaration, activation policy | Bounded; never self-authorizing |
| **Settle** | SettlementVerdict, binding bridge | Predicted vs observed + contamination |
| **Route / orchestrate** | YGGDRASIL, Alembic Spine | Deterministic topology & advisory multi-arch |
| **Project** | AAL-Viz, InstantiationProjectionView | Read/render only — **no execution authority** |
| **Govern** | Governance V3, operator loop, WorkPacket/Handoff | Human sovereignty; provenance ≠ authority |
| **Agent OS** | Hermes skills, AI OS kernel (`ACTIVE_SHADOW`) | Forage → pack → spine under SHADOW |

Implementation status and held gates: always **[`STATUS.md`](STATUS.md)**.

### Recent landings (2026-07-31 → 2026-08-10)

| Track | Landed | Posture |
|-------|--------|---------|
| RDI doctrine + fixtures + intervention | #1096 · **1.178.0** | PARTIAL · fixture / advisory |
| Settlement binding bridge + three-settlement docs | #1104 | Technical settlement increment |
| RDI-4 SHADOW detector + projection-only view | #1105 | Anomaly-only · no authority |
| Memetic forensics C+C′+C6 · Ops D0/D2 | #1079–#1083 | SHADOW · **OpsGate DENIED** |
| Slice G / P4 · OmegaClaw · collab board | #1095–#1102 | Docs / advisory |
| README direction rewrite | this | Aligns GitHub surface to Notion 2026-08-09 canon |

---

## Quick start

**Requirements:** Python 3.12+. No external services for the safe demo.

```bash
# 1. Clone and install
git clone https://github.com/scrimshawlife-ctrl/Abraxas-v2.0.git
cd Abraxas-v2.0
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 2. Safe read-only status (no out/ writes)
python scripts/tools/demo_safe_status.py

# 3. Product CLI (LOCAL_DEV)
python -m abraxas status
python -m abraxas os status
python -m abraxas os forensics status
python -m abraxas analyze --alembic-task fixtures/alembic/example_task.json
python -m abraxas validate \
  --schema-ref contracts/alembic/task_envelope.v1.schema.json \
  --payload fixtures/alembic/example_task.json
```

```python
from abraxas import AbraxasClient
client = AbraxasClient()
print(client.status()["candidate_status"])  # NOT_READY
```

Full onboarding: **[QUICKSTART.md](QUICKSTART.md)** · contributor path: **[docs/START_HERE.md](docs/START_HERE.md)**

### Common engineering commands

```bash
python scripts/organize_scripts.py status   # scripts layout gate
python scripts/run_fast_ci.py               # local CI mirror

env -u PYTHONPATH -u PYTHONHOME .venv/bin/python -m pytest \
  tests/test_instantiation_contracts.py \
  tests/test_instantiation_shadow_projection.py \
  tests/test_settlement_binding_bridge.py \
  tests/test_cfar.py -q
```

---

## Repository map

```text
abraxas/                 Product CLI + client (status / os / forensics)
apps/api/                Service factory (create_app)
apps/aal-viz-live-console/  Projection console (Vite)
core/                    Domain logic (instantiation/, forensics/, cfar, settlement/, …)
contracts/               JSON Schema (instantiation/, forensics/, engineering/, …)
scripts/<domain>/        Domain-organized runners
design-system/           Visual OS + aal-viz pack
docs/                    Doctrine, architecture, atlas, readiness
out/                     Generated artifacts (mostly gitignored)
tests/                   Replay-stable pytest suite
skills/                  Hermes-mountable skills
```

Scripts: `scripts/<domain>/run_*.py`. CI mirror: `scripts/run_fast_ci.py`. See [`scripts/README.md`](scripts/README.md).

---

## Documentation

| Need | Route |
|------|--------|
| Live posture | [STATUS.md](STATUS.md) |
| Architecture + three-settlement + language boundary | [ARCHITECTURE.md](ARCHITECTURE.md) |
| RDI doctrine · Fable handoff | [RDI 001](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md) · [Fable](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_FABLE_HANDOFF_001.md) |
| Glossary | [docs/GLOSSARY.md](docs/GLOSSARY.md) |
| Roadmap | [PLANS.md](PLANS.md) |
| Contributor / agent rules | [CONTRIBUTING.md](CONTRIBUTING.md) · [AGENTS.md](AGENTS.md) |
| Collab board | [GitHub Project](https://github.com/users/scrimshawlife-ctrl/projects/5) · labels `track/rdi`, `track/ai-os`, `collab` |
| Doc index | [docs/INDEX.md](docs/INDEX.md) · [docs/START_HERE.md](docs/START_HERE.md) |
| Production readiness | [out/production_readiness/README.md](out/production_readiness/README.md) |
| Design system / AAL-Viz | [design-system/](design-system/) · [aal-viz](design-system/aal-viz/) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

**Atlas protocol:** Notion governs architecture / registered state; GitHub governs implementation and merge evidence. Notion mirrors do not grant execution or canon authority.

---

## Multi-agent engineering

Grok, Codex, Hermes, and human operators are **peer collaborators** under a shared contract:

- Inspect existing peer work before overlapping  
- Prefer complementary workstreams  
- Tag artifacts with `producer_system` (`GROK` \| `CODEX` \| `MIXED` \| `HUMAN` \| `IMPORTED` \| …)  
- **AgentArtifactMetadata.v1** records provenance — never authority, auto-merge, or canon promotion  
- Operator retains final merge and canon authority  

---

## Governance & activation

| Lane | Posture |
|------|---------|
| `LOCAL_DEV` / `SANDBOX` | Allowed for engineering |
| `INTERNAL_CANARY` | Conditional |
| `EXTERNAL_PRODUCTION` | **Operator-gated / held** |

SHADOW and FORECAST stay authority-separated. AAL-Viz is projection-only.

Details: [GOVERNANCE_V3.md](GOVERNANCE_V3.md) · [STATUS.md](STATUS.md) · [ADR-0017](docs/adr/ADR-0017-BOUNDED-ACTIVATION-POLICY.md)

---

## Contributing

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md)  
2. Prefer vertical slices that advance at least **two** settlement surfaces without duplicate architecture  
3. Small PRs with focused tests; run `python scripts/run_fast_ci.py` before opening a PR  
4. Do not invent Instantiation Depth, causal coefficients, or phantom metrics  
5. Do not bulk-rewrite sealed hygiene hash chains or invent ghost runners  
6. Never add `scripts/operator/__init__.py` (stdlib `operator` shadowing)  

---

## License

**Proprietary** — Copyright (c) 2024–2026 Applied Alchemy Labs / Daniel Meyer / Zero State.  
All rights reserved. No open-source license is granted.

See [`LICENSE`](LICENSE). Contact maintainers for commercial licensing.

---

**Applied Alchemy Labs** — one core; three settlements; wrappers over a provenance-bound RDI spine.

*Abraxas studies how representations become causes.*
