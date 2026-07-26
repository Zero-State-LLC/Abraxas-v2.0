# ABRAXAS

![Abraxas — Governed Symbolic Intelligence](assets/hero-abraxas-readme.jpg)

**Governed Symbolic Intelligence** · *Deterministic · Observable · Recursive*

> Structure before narrative. Evidence before authority. Governance before autonomy.

[![CI](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

| Field | Value |
|-------|--------|
| **Product posture** | Candidate · **deploy held** · production activation **DENIED** |
| **Governance** | [Governance V3](GOVERNANCE_V3.md) (implementation-first) |
| **Live status** | [`STATUS.md`](STATUS.md) — replace block, do not invent readiness |
| **License** | [Apache-2.0](LICENSE) |

**Do not claim production ready.** Candidate ≠ activation. Merge ≠ go-live.

---

## What this is

**Abraxas v2.0** is a governed symbolic-intelligence architecture in the Applied Alchemy Labs (AAL) ecosystem: deterministic execution, receipt-first provenance, and human-in-the-loop sovereignty over root definitions.

It is **not** a generic chatbot wrapper. Default posture is **advisory / projection-only** for research and operator surfaces unless a lane explicitly authorizes more (see [ADR-0017](docs/adr/ADR-0017-BOUNDED-ACTIVATION-POLICY.md)).

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
| **Belief Graph / Phase Percolation** | Structured knowledge + temporal regimes | contracts + tests |
| **CFAR** | Construct-first research gate (before retrieval) | [`docs/research/CFAR_CONSTRUCT_FIRST_REASONING_001.md`](docs/research/CFAR_CONSTRUCT_FIRST_REASONING_001.md) · `core/cfar.py` |
| **AAL-Viz** | Projection-layer console + visual language | [`apps/aal-viz-live-console/`](apps/aal-viz-live-console/) · [`design-system/aal-viz/`](design-system/aal-viz/) |
| **Design system** | Tokens, icons, runes, Visual OS | [`design-system/`](design-system/) |
| **Agent artifact metadata** | Multi-agent provenance schema | [`contracts/engineering/agent_artifact_metadata.v1.schema.json`](contracts/engineering/agent_artifact_metadata.v1.schema.json) |

---

## Quick start

**Requirements:** Python 3.12+, pip. No external services for the safe demo.

```bash
# 1. Clone and install
git clone https://github.com/scrimshawlife-ctrl/Abraxas-v2.0.git
cd Abraxas-v2.0
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Safe read-only status (no out/ writes)
python scripts/tools/demo_safe_status.py

# 3. Product CLI (LOCAL_DEV)
python -m abraxas status
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
```

---

## Repository map

```text
abraxas/                 Product CLI + client
apps/api/                Service factory (create_app)
apps/aal-viz-live-console/  Projection console (Vite)
core/                    Domain logic (no uncontrolled out/ writes)
contracts/               JSON Schema contracts (incl. cfar/, engineering/)
scripts/<domain>/        Organized runners (scripts/README.md)
design-system/           Visual OS + aal-viz asset pack
docs/                    Atlas, ADRs, production readiness guides
out/                     Generated artifacts (mostly gitignored; some receipts tracked)
tests/                   Pytest suite
```

Scripts are **domain-organized** (`scripts/<domain>/run_*.py`). Root keeps `scripts/run_fast_ci.py` as the CI mirror. See [`scripts/README.md`](scripts/README.md).

---

## Documentation index

| Audience | Document |
|----------|----------|
| First run | [QUICKSTART.md](QUICKSTART.md) |
| Live ops status | [STATUS.md](STATUS.md) |
| Agent / contributor rules | [AGENTS.md](AGENTS.md) · [CONTRIBUTING.md](CONTRIBUTING.md) |
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) · [docs/atlas/ABRAXAS_ATLAS.md](docs/atlas/ABRAXAS_ATLAS.md) |
| Roadmap | [PLANS.md](PLANS.md) |
| Production readiness | [out/production_readiness/README.md](out/production_readiness/README.md) |
| Program roadmap | [PLANS.md](PLANS.md) · [CONTINUATION_PLAN.v16](out/production_readiness/CONTINUATION_PLAN.v16.md) |
| HTTP API (human) | [docs/api/HTTP_API.md](docs/api/HTTP_API.md) · OpenAPI freeze: `contracts/api/openapi_supported_surface.v1.json` |
| Glossary | [docs/GLOSSARY.md](docs/GLOSSARY.md) |
| Design system | [design-system/README.md](design-system/README.md) |
| AAL-Viz assets | [design-system/aal-viz/README.md](design-system/aal-viz/README.md) · [showcase](design-system/aal-viz/showcase/index.html) |
| Multi-agent contract | Peer collaborators (Grok/Codex) — `producer_system` provenance only; schema above |
| Changelog | [CHANGELOG.md](CHANGELOG.md) (semantic-release tags + Unreleased digest) |
| Security / secrets | Do not commit credentials; see CI security workflows |

---

## Multi-agent engineering

Grok and Codex operate as **peer collaborators** under a shared contract:

- Inspect existing peer work before overlapping changes
- Prefer complementary workstreams over duplication
- Tag artifacts with `producer_system` (`GROK` \| `CODEX` \| `MIXED` \| `HUMAN` \| `IMPORTED`)
- Machine companion: **AgentArtifactMetadata.v1** — identity does **not** grant authority, auto-merge, or canon promotion
- Operator retains final authority on merge and canon

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

Copyright and license: **[Apache License 2.0](LICENSE)**.

---

**Applied Alchemy Labs** — schema-driven, provenance-tagged systems at the intersection of symbolic intelligence, forecasting, and governed engineering.

*Notion mirrors architecture/registered state; GitHub governs implementation and merge evidence.*
