# ABRAXAS v2.0 — Kernel Zero

> **Recursively governed symbolic operating substrate.**
> Not a chatbot. Not a loose automation framework.

---

## Goal

Kernel Zero is the minimal executable governance spine of ABRAXAS v2.0.
It establishes the foundational authority model, pipeline contracts, rune catalog,
YGGDRASIL route topology, and receipt/proof system — before any intelligence or
forecasting layers are introduced.

**Core doctrine:**
- governance before intelligence
- deterministic outputs
- typed IR everywhere
- explicit authority boundaries
- SHADOW / FORECAST separation
- ABX-Runes as typed operation layer
- YGGDRASIL as route/dependency topology
- AAL-Viz is projection-only
- receipts + proofs are mandatory
- fail closed on missing provenance
- no implementation claim without execution receipt

---

## Repository Layout

```
abraxas-v2/
  apps/api/               FastAPI application
  core/
    canonical/            Canonical JSON + hashing
    governance/           Authority model + doctrine constants
    pipelines/            Contract models, registry, validator, orchestrator
    runes/                ABX-Rune contract models and registry
    yggdrasil/            Route graph models and validator
    receipts/             Execution receipt models and builder
    operators/            Operator review queue
    projections/          AAL-Viz projection packet (projection-only)
  contracts/
    pipelines/            7 Tier-1 pipeline contracts
    runes/                Rune catalog
    yggdrasil/routes/     7 YGGDRASIL route graphs
  out/                    Generated artifacts (registry, validation, receipts, projections)
  scripts/                CLI scripts
  tests/                  pytest suite
```

---

## Installation

```bash
# Using uv (recommended)
pip install uv
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Or plain pip
pip install fastapi uvicorn "pydantic>=2.7" pytest httpx
```

---

## Running Tests

```bash
pytest -q
```

Expected: all tests pass (no forecasting, no LLM, no external calls).

---

## Running the Registry

Reads all 7 Tier-1 pipeline contracts from `contracts/pipelines/` and writes
the global pipeline registry to `out/registry/latest.json`.

```bash
python scripts/run_registry.py
```

---

## Running the Doctrine Validator

Validates all 7 Tier-1 contracts against the rune catalog and YGGDRASIL route
graphs. Writes:
- `out/validation/latest.json`
- `out/projections/aal_viz.latest.json`
- `out/operator_review/latest.json`

```bash
python scripts/run_doctrine_validator.py
```

---

## Generating a Receipt

Creates a simulated execution receipt under `out/receipts/latest.json`.

```bash
python scripts/run_receipt.py \
  --execution-state simulated \
  --command-id KERNEL_ZERO_BOOTSTRAP \
  --operator-command "bootstrap kernel zero"
```

---

## Running the API

```bash
uvicorn apps.api.main:app --reload
```

Endpoints:
- `GET /health` — system health
- `GET /registry` — pipeline registry
- `GET /validation` — latest doctrine validation run
- `GET /projection` — latest AAL-Viz projection packet

---

## Authority Boundaries

All authority flags default to `False`.  Any `True` flag is a doctrine violation
caught at model construction time (Pydantic `model_validator`).

Authority flags:
- `promotion_allowed` — may promote SHADOW → Canon
- `forecast_weight_allowed` — may apply forecast weights
- `runtime_mutation_allowed` — may mutate runtime state
- `baseline_mutation_allowed` — may mutate baseline
- `canon_mutation_allowed` — may write to Canon
- `aal_viz_inference_authority` — may infer (always False for projection-only)

Call `authority.assert_locked()` anywhere to enforce the fail-closed rule.

---

## AAL-Viz Projection-Only Rule

AAL-Viz **projects** pipeline state for operator visibility.  It has **zero**
inference authority.  The `build_projection_packet()` function enforces:

```python
assert packet["projection_only"] is True
assert packet["inference_authority"] is False
assert all(v is False for v in packet["authority"].values())
```

Any attempt to set `inference_authority=True` or any authority flag raises
`ValueError` immediately.

---

## Hard Boundaries (Kernel Zero)

Do **not** add to this layer:
- Forecasting logic or LLM integration
- Autonomous execution or external API fetching
- Sports, market, or Oracle modules
- Any authority boolean defaulting to `True`
- Silent Canon mutation

---

## Next Recommended Milestone

**v2.0.1-rune-layer** — Implement typed rune execution stubs,
shadow run harness, and receipt chaining.
