# Alembic Spine — Audit & Reconciliation Map

**Classification legend:** `OBSERVED` · `INFERRED` · `SPECULATIVE` · `NOT_COMPUTABLE`  
**Date:** 2026-07-26 · **Authority:** advisory documentation only

## Capability matrix

| Capability | Existing implementation | Canonical owner | Maturity | Duplication | Gap | Recommended action |
| --- | --- | --- | --- | --- | --- | --- |
| Alembic plan | `docs/plans/ALEMBIC_SPINE_UNIFICATION_PLAN_001.md` | docs/plans | proposal only | none | no code | Implement advisory spine under `core/alembic/` |
| Architecture taxonomy | none observed | — | absent | — | missing | Add taxonomy + descriptors |
| Paradigm router | YGGDRASIL route graphs (pipeline routing, not architecture selection) | `core/yggdrasil/` | mature for pipelines | conceptual overlap only | no architecture router | New Alembic router; do not fork YGGDRASIL |
| Adapter protocol | `core/ingest/ingest_adapter.py` | ingest | mature for ingest | different domain | no architecture adapters | New architecture adapter protocol; reuse patterns |
| Fusion/normalization | belief-graph packet assembly; conflict scan | belief_graph / `core/conflict_scan.py` | partial | naming overlap | no multi-arch fusion | Alembic fusion + reuse conflict posture |
| Symbolic verification | pipeline validate / proof runes | pipelines/runes | mature for pipelines | — | no architecture contribution verifier | Alembic verify surface |
| Brier / calibration | `core/scoring/brier.py`, `contracts/calibration/` | scoring | mature | none | multi-level architecture scoring | Wrap Brier only for probabilistic outputs |
| SHADOW / FORECAST | doctrine + many shadow runners | governance / research | mature | none | architecture shadow compare | Alembic shadow compare; keep lane locks |
| Decision records | many operator decision record builders | operator_review | mature | many historical variants | architecture routing decision | New `RoutingDecision.v1` only |
| Receipts / canonical JSON | `core/canonical/json.py`, receipt contracts | canonical / receipts | mature | none | alembic run receipt | Emit via canonical writers |
| Global ingest | `core/ingest/` | ingest | mature | none | architecture-aware intake metadata | Thin hooks only |
| Oracle Signal | `core/oracle_signal*.py` | oracle | mature | none | architecture metadata at intake | Integrate via hooks, not second pipeline |
| Rune registry | `contracts/runes/catalog.v1.json` | runes | mature | none | no Alembic-native runes | Reuse existing; proposals file only |
| Codegen spine | many `abx_codegen_*` plan modules | codegen | advisory/planning | large plan surface | unrelated execution | Do not duplicate; leave separate |
| Meta-optimization | Optuna/Bayesian research surfaces | research | partial | — | router proposals | Proposal-only layer, operator-gated |

## Findings

- **OBSERVED:** Before this implementation, repository search found exactly one Alembic artifact: the unification plan. No `core/alembic`, contracts, fixtures, CLI, or tests existed.
- **OBSERVED:** Adequate canonical subsystems already exist for JSON hashing, Brier, ingest adapters, conflict detection posture, rune catalog, and SHADOW/FORECAST locks.
- **OBSERVED:** `tests/test_yggdrasil_rune_route_binding_matrix.py` requires `unbound_runes == []`, so live catalog additions without pipeline bindings fail closed.
- **INFERRED:** Highest value is reconciliation into one advisory spine that reuses canonical infrastructure rather than inventing parallel stacks.
- **SPECULATIVE:** SNN/neuromorphic, SSM, and generative backends remain experimental stubs until evaluation evidence justifies promotion.
- **NOT_COMPUTABLE:** Production readiness / external specialist backend quality — no evidence in-repo.

## Target ownership (post-reconciliation)

| Concern | Owner |
| --- | --- |
| Alembic domain + pipeline | `core/alembic/` |
| Contracts/policy | `contracts/alembic/` |
| CLI | `scripts/alembic/run_alembic_spine.py` |
| Tests | `tests/test_alembic_spine.py`, `tests/test_run_alembic_spine.py` |
| Docs | `docs/alembic/` |

## Migration / file actions

| Action | Paths |
| --- | --- |
| Create | `core/alembic/**`, `contracts/alembic/**`, `scripts/alembic/**`, `fixtures/alembic/**`, `docs/alembic/**`, tests |
| Modify | `scripts/organize_scripts.py` (PREFIX_MAP), STATUS/ARCHITECTURE/PLANS/README, unification plan status |
| Deprecated | none (no prior Alembic code) |
| Removed | none |
| Deferred | live `RUNE.ARCHITECTURE_*` catalog entries; deep YGGDRASIL alembic route; external backends |
