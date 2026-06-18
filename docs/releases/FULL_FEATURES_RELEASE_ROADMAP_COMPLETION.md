# Full Features Release Roadmap — Completion Receipt

Product version **2.5.0** — Full Features Release Roadmap implementation.

## Phase 0 — Foundation

- [x] Governance V3 merged (PR #709)
- [x] Notion sync checklist: [`docs/notion/GOVERNANCE_V3_NOTION_SYNC.md`](docs/notion/GOVERNANCE_V3_NOTION_SYNC.md)
- [x] Version strategy: [`docs/releases/VERSION_STRATEGY.md`](docs/releases/VERSION_STRATEGY.md)
- [x] AAL-Viz Node 20 toolchain (`.nvmrc`, `package-lock.json` refresh)

## Phase 1 — v2 Hygiene Foundation (v2.2.0 scope)

Implemented under `abraxas/v2/`:

- HygieneMode (`abraxas/v2/governance/mode.py`)
- LoopDynamics, V2Output, V2HygieneRune base
- Five hygiene runes + HygienePipeline
- JSON schemas + validator
- Tests: `tests/v2/hygiene/`
- Example: `examples/v2_hygiene_integration.py`
- v2 runes registered in `contracts/runes/catalog.v1.json`

## Phase 2 — Oracle Signal + Global Ingest (v2.3.0 scope)

- [`core/oracle_signal.py`](core/oracle_signal.py) — shadow processing packet builder
- [`core/ingest/controlled_handoff_eligibility.py`](core/ingest/controlled_handoff_eligibility.py)
- [`contracts/global_pipeline/oracle_signal_pipeline.v1.schema.json`](contracts/global_pipeline/oracle_signal_pipeline.v1.schema.json)

## Phase 3 — Intelligence Layer (v2.4.0 scope)

- [`core/belief_graph/engine.py`](core/belief_graph/engine.py)
- [`core/geometric_intelligence_runtime.py`](core/geometric_intelligence_runtime.py)
- [`core/codegen/shadow_replay_harness.py`](core/codegen/shadow_replay_harness.py)

## Phase 4 — Full Features (v2.5.0 scope)

- AAL-Viz geometric renderer: `apps/aal-viz-live-console/src/components/GeometricRenderer.tsx`
- P40 climate+motif fusion overlay live-console consumer: adapter ingests `out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json` into `fusion_overlay` on the projection bundle; `FusionOverlayPanel` renders P40 nodes with degraded-posture caption (PR #713)
- Product version bumped to **2.5.0** in `pyproject.toml`, `VERSION`, README badge

## Validation

Fast CI passes (`python scripts/run_fast_ci.py`).

```bash
python scripts/run_fast_ci.py
pytest -q tests/v2/hygiene tests/test_oracle_signal.py tests/test_belief_graph_engine.py
```

## Milestone coverage

| Release | Scope | Status |
|---------|-------|--------|
| v2.2.0 | v2 Hygiene Phase 1 (14 tasks) | Implemented under `abraxas/v2/` |
| v2.3.0 | Oracle Signal + controlled ingest eligibility | Implemented (shadow/advisory) |
| v2.4.0 | Belief Graph engine, geometric runtime, codegen harness, YGGDRASIL v2 bindings | Implemented (advisory) |
| v2.5.0 | AAL-Viz geometric renderer + product version 2.5.0 | Implemented |

## Notion follow-up

Operator manual steps remain in [`GOVERNANCE_SIMPLIFICATION_001.md`](GOVERNANCE_SIMPLIFICATION_001.md) and [`docs/notion/GOVERNANCE_V3_NOTION_SYNC.md`](docs/notion/GOVERNANCE_V3_NOTION_SYNC.md).

## Merge record

- **PR #710** merged to `main` on 2026-06-18
- Post-merge continuation: [`docs/releases/PRODUCT_2_5_0_RELEASE_READY.md`](PRODUCT_2_5_0_RELEASE_READY.md)
