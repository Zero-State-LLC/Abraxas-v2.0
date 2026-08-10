# ABRAXAS

![Abraxas — Governed Symbolic Intelligence](assets/hero-abraxas-readme.jpg)

**Governed Symbolic Intelligence** · *Deterministic · Observable · Recursive*

> Structure before narrative. Evidence before authority. Governance before autonomy.

[![CI](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Proprietary-334155.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

| Field | Value |
|-------|--------|
| **Product posture** | Candidate · **deploy held** · production activation **DENIED** |
| **Governance** | [Governance V3](GOVERNANCE_V3.md) (implementation-first) |
| **Live status** | [`STATUS.md`](STATUS.md) — replace block, do not invent readiness |
| **License** | [Proprietary](LICENSE) — all rights reserved |

**Do not claim production go-live.** Candidate ≠ activation. Merge ≠ go-live.

---

## What this is

**Abraxas v2.0** is a governed symbolic-intelligence architecture in the Applied Alchemy Labs (AAL) ecosystem: deterministic execution, receipt-first provenance, and human-in-the-loop sovereignty over root definitions.

Abraxas treats representations as potentially causal structures rather than assuming a binary distinction between simulation and instantiation. It studies evidence-backed transitions from representation into behavioral, computational, institutional, economic, and material consequence while preserving provenance, uncertainty, and observer-intervention contamination. See [`REPRESENTATION_DRIVEN_INSTANTIATION_001`](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md).

It is **not** a generic chatbot wrapper. Default posture is **advisory / projection-only** for research and operator surfaces unless a lane explicitly authorizes more (see [ADR-0017](docs/adr/ADR-0017-BOUNDED-ACTIVATION-POLICY.md)).

Abraxas is primarily developed in Python for semantic and research agility, with Rust considered selectively for stable execution boundaries such as canonicalization, replay, high-throughput ingest, and future deterministic simulation — only where measured need justifies it (see [ARCHITECTURE.md § Language / runtime boundary](ARCHITECTURE.md)). No Rust component currently exists.

### Design pillars

- **Deterministic execution** — traceable paths, receipts, artifact lineage
- **Observable processes** — audit surfaces, status matrices, operator review
- **Recursive continuity** — self-improving loops under frozen governance rules
- **Contract-bound operators** — schemas, runes, fail-closed authority locks
- **Lane-based activation** — LOCAL_DEV / SANDBOX allowed; EXTERNAL_PRODUCTION operator-gated

### Key surfaces

| Surface | Role | Start here |
|---------|------|------------|
| **Oracle / ingest** | Signal intake, shadow execution | `docs/atlas/research-canary.md` |
| **Alembic Spine** | Advisory multi-architecture orchestration | [`docs/alembic/ALEMBIC_SPINE.md`](docs/alembic/ALEMBIC_SPINE.md) |
| **YGGDRASIL** | Deterministic routing topology | ARCHITECTURE.md |
| **Belief Graph Engine** | Structured knowledge representation (advisory) | contracts + tests |
| **Phase Percolation** | Temporal regime surfaces (advisory) | contracts + tests |
| **Codegen Intelligence Spine** | **hygiene-only** by default; expansion operator-gated | gap-analysis plan under `out/audit/` |
| **CFAR** | Construct-first research gate (before retrieval) | [`docs/research/CFAR_CONSTRUCT_FIRST_REASONING_001.md`](docs/research/CFAR_CONSTRUCT_FIRST_REASONING_001.md) · `core/cfar.py` |
| **RDI / Instantiation** | Representation-driven instantiation (fixture contracts + intervention declarations; **PARTIAL**) | [`docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md`](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md) · `contracts/instantiation/` · `core/instantiation/` |
| **Fable RDI handoff** | Continuation packet for RDI roadmap (advisory only) | [`docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_FABLE_HANDOFF_001.md`](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_FABLE_HANDOFF_001.md) |
| **Memetic Forensics** | SHADOW spine: EvidencePack → propagation → disposition; **OpsGate always DENIED** | [`docs/architecture/MEMETIC_FORENSICS_MISSION_001.md`](docs/architecture/MEMETIC_FORENSICS_MISSION_001.md) · `python -m abraxas os forensics status` |
| **AAL-Viz** | Projection-layer console + visual language (+ forensic projection C6) | [`apps/aal-viz-live-console/`](apps/aal-viz-live-console/) · [`design-system/aal-viz/`](design-system/aal-viz/) |
| **Design system** | Tokens, icons, runes, Visual OS | [`design-system/`](design-system/) |
| **Agent artifact metadata** | Multi-agent provenance schema | [`contracts/engineering/agent_artifact_metadata.v1.schema.json`](contracts/engineering/agent_artifact_metadata.v1.schema.json) |
| **Multi-agent operator loop** | Hermes/Grok/Codex responsibilities (provenance ≠ authority) | [`docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md`](docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md) · glyphs in `design-system/aal-viz/operator_loop/` |
| **Hermes OS unification** | Three-layer OS: Visual + Abraxas core + Hermes agent; signal forage syscall | [`docs/architecture/ABRAXAS_HERMES_OS_UNIFICATION_001.md`](docs/architecture/ABRAXAS_HERMES_OS_UNIFICATION_001.md) · skill `abx-familiar-signal-forager` |
| **AI OS realization backlog** | Work packages for kernel path; Slice G (consumption + handoff) defined | [`docs/architecture/ABRAXAS_AI_OS_REALIZATION_BACKLOG_001.md`](docs/architecture/ABRAXAS_AI_OS_REALIZATION_BACKLOG_001.md) |
| **AI OS kernel audit** | K1–K12 evidence vs main (`ACTIVE_SHADOW`, not production) | [`docs/architecture/AI_OS_KERNEL_AUDIT_001.md`](docs/architecture/AI_OS_KERNEL_AUDIT_001.md) · `python -m abraxas os status` |
| **AI OS unification plan** | Whole-system tracks A–D (nav, contracts, alembic, authz) | [`docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md`](docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md) |
| **AI OS primitives map** | Classic OS primitives → Abraxas surfaces (projection) | [`docs/architecture/AI_OS_PRIMITIVES_MAP_001.md`](docs/architecture/AI_OS_PRIMITIVES_MAP_001.md) · #1050 |
| **OmegaClaw track** | Symbolic integration concepts (advisory / SHADOW) | [`docs/architecture/OMEGACLAW_CONCEPT_INTEGRATION_001.md`](docs/architecture/OMEGACLAW_CONCEPT_INTEGRATION_001.md) · [`docs/plans/OMEGACLAW_SYMBOLIC_INTEGRATION_PLAN_001.md`](docs/plans/OMEGACLAW_SYMBOLIC_INTEGRATION_PLAN_001.md) |

### Recent landings (2026-07-31 → 2026-08-10)

| Track | What landed | Authority |
|-------|-------------|-----------|
| **RDI / Fable** #1096 · release **1.178.0** | Doctrine + reuse audit; fixture `InstantiationState/Transition.v1`; bounded `InterventionDeclaration.v1`; Fable handoff + validation | Advisory / fixture-only; no empirical claim; no activation |
| **Slice G + P4 surfaces** #1098 | Consumption hardening + operator handoff definition; Hermes unification P4 notes; volume/patch palette | SHADOW / docs + skill surfaces |
| **Memetic forensics C+C′+C6** #1079–#1081 | Pipeline, disposition, propagation graph, CLI `os forensics *`, AAL-Viz forensic projection | SHADOW; **MemeticOpsGate always DENIED** |
| **Ops D0 / D2** #1082–#1083 | `MemeticOpsRouteIntent` + Level99 content seed (no publish) | Gate still DENIED |
| **OmegaClaw** #1095 | Concept integration + symbolic plan (advisory) | No inter-agent live authority |
| **Collab board** #1102 | GitHub Project collaboration section in CONTRIBUTING | Process only |

Live replace-block status: always read **[`STATUS.md`](STATUS.md)** before claiming readiness.

---

## Quick start

**Requirements:** Python 3.12+, pip. No external services for the safe demo.

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

Full onboarding: **[QUICKSTART.md](QUICKSTART.md)** (~5 minutes).

### Common engineering commands

```bash
# Layout gate (scripts organization complete)
python scripts/organize_scripts.py status

# Local CI mirror
python scripts/run_fast_ci.py

# Targeted tests (scrub Hermes/venv noise if needed)
env -u PYTHONPATH -u PYTHONHOME .venv/bin/python -m pytest tests/test_cfar.py -q
env -u PYTHONPATH -u PYTHONHOME .venv/bin/python -m pytest \
  tests/test_instantiation_contracts.py tests/test_forensics_cli.py -q
```

---

## Repository map

```text
abraxas/                 Product CLI + client (incl. `os status` / `os forensics`)
apps/api/                Service factory (create_app)
apps/aal-viz-live-console/  Projection console (Vite)
core/                    Domain logic (forensics/, instantiation/, cfar, …)
contracts/               JSON Schema (cfar/, engineering/, forensics/, instantiation/, …)
scripts/<domain>/        Organized runners (scripts/README.md)
design-system/           Visual OS + aal-viz asset pack
docs/                    Atlas, ADRs, architecture, production readiness
out/                     Generated artifacts (mostly gitignored; some receipts tracked)
tests/                   Pytest suite
skills/                  Hermes-mountable skills (forager, neon-genie, evolution, …)
```

Scripts are **domain-organized** (`scripts/<domain>/run_*.py`). Root keeps `scripts/run_fast_ci.py` as the CI mirror. See [`scripts/README.md`](scripts/README.md).

---

## Documentation index

| Audience | Document |
|----------|----------|
| First run | [QUICKSTART.md](QUICKSTART.md) · [docs/START_HERE.md](docs/START_HERE.md) |
| Live ops status | [STATUS.md](STATUS.md) |
| Agent / contributor rules | [AGENTS.md](AGENTS.md) · [CONTRIBUTING.md](CONTRIBUTING.md) |
| Collaboration board | [CONTRIBUTING § Collaboration](CONTRIBUTING.md#collaboration-github-project) · [GitHub Project](https://github.com/users/scrimshawlife-ctrl/projects/5) |
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) · [docs/atlas/ABRAXAS_ATLAS.md](docs/atlas/ABRAXAS_ATLAS.md) · [docs/INDEX.md](docs/INDEX.md) |
| RDI / Fable | [RDI doctrine](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md) · [Fable handoff](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_FABLE_HANDOFF_001.md) |
| Memetic forensics | [Mission map](docs/architecture/MEMETIC_FORENSICS_MISSION_001.md) · `contracts/forensics/` |
| Roadmap | [PLANS.md](PLANS.md) |
| Production readiness | [out/production_readiness/README.md](out/production_readiness/README.md) |
| Program roadmap | [PLANS.md](PLANS.md) · [CONTINUATION_PLAN.v16](out/production_readiness/CONTINUATION_PLAN.v16.md) |
| HTTP API (human) | [docs/api/HTTP_API.md](docs/api/HTTP_API.md) · OpenAPI freeze: `contracts/api/openapi_supported_surface.v1.json` |
| Glossary | [docs/GLOSSARY.md](docs/GLOSSARY.md) |
| Design system | [design-system/README.md](design-system/README.md) |
| AAL-Viz assets | [design-system/aal-viz/README.md](design-system/aal-viz/README.md) · [showcase](design-system/aal-viz/showcase/index.html) |
| Multi-agent contract | Peer collaborators (Grok/Codex) — `producer_system` provenance only; schema above |
| Changelog | [CHANGELOG.md](CHANGELOG.md) (semantic-release; tip **1.178.0** RDI fixtures + intervention) |
| Security / secrets | Do not commit credentials; see CI security workflows |

---

## Multi-agent engineering

Grok and Codex operate as **peer collaborators** under a shared contract:

- Inspect existing peer work before overlapping changes
- Prefer complementary workstreams over duplication
- Tag artifacts with `producer_system` (`GROK` \| `CODEX` \| `MIXED` \| `HUMAN` \| `IMPORTED`)
- Machine companion: **AgentArtifactMetadata.v1** — identity does **not** grant authority, auto-merge, or canon promotion
- Operator retains final authority on merge and canon
- Shared board: [Abraxas v2.0 GitHub Project](https://github.com/users/scrimshawlife-ctrl/projects/5) · labels `collab`, `track/rdi`, `track/ai-os` (see [CONTRIBUTING.md](CONTRIBUTING.md))

---

## Governance & activation

| Lane | Posture |
|------|---------|
| `LOCAL_DEV` / `SANDBOX` | Allowed for engineering |
| `INTERNAL_CANARY` | Conditional |
| `EXTERNAL_PRODUCTION` | **Operator-gated / held** |

SHADOW and FORECAST lanes stay visually and authority-separated. AAL-Viz is a **projection layer** (read/render) — not an execution authority.

Details: [GOVERNANCE_V3.md](GOVERNANCE_V3.md) · [STATUS.md](STATUS.md) · [ADR-0017](docs/adr/ADR-0017-BOUNDED-ACTIVATION-POLICY.md)

---

## Contributing

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md)
2. Prefer small PRs with focused tests
3. Run `python scripts/run_fast_ci.py` before opening a PR
4. Do not bulk-rewrite sealed hygiene hash chains or invent ghost runners
5. Never add `scripts/operator/__init__.py` (stdlib `operator` shadowing)

---

## License

**Proprietary** — Copyright (c) 2024–2026 Applied Alchemy Labs / Daniel Meyer / Zero State.  
All rights reserved. No open-source license is granted.

See [`LICENSE`](LICENSE) for the full proprietary notice. Contact the maintainers for commercial licensing.

---

**Applied Alchemy Labs** — schema-driven, provenance-tagged systems at the intersection of symbolic intelligence, forecasting, and governed engineering.

*Notion mirrors architecture/registered state; GitHub governs implementation and merge evidence.*
