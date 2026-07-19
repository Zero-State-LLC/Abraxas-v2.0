# Repository Organization Inventory 001

Advisory-only inventory emitted 2026-06-18 (post-#741 merge). Readonly scan; no runtime or governance mutation.

## Executive summary

| Area | Files | Dirs | Notes |
|------|------:|-----:|-------|
| `core/` | 2,494 | 172 | Flat module namespace + subpackages (`sync/`, `ingest/`, `governance/`) |
| `contracts/` | 642 | 49 | Schemas, canon, runes, yggdrasil routes |
| `scripts/` | 982 | 13 | Primary `run_*` runner surface (~599 `run_*.py`) |
| `Scripts/` | 233 | 1 | **Casing duplicate** — legacy/alternate tree; do not merge without operator review |
| `tests/` | 2,141 | 10 | ~1,034 `test_*.py` modules |
| `docs/` | 167 | 12 | Audits, releases, plans, atlas, operators |
| `operator_input/` | 60 | 1 | Payloads + templates (no root README before sweep) |
| `out/` | 1,214 | 220 | 178 top-level artifact lanes |
| `abraxas/` | 36 | 12 | Legacy v2 package subtree |
| `fixtures/` | 9 | 3 | Test/chamfer fixtures |

**Registry cross-check:** [`core/generated_artifact_registry.py`](../../core/generated_artifact_registry.py) references ~638 explicit `out/**/*.latest.{json,md}` producer paths.

---

## Top-level repository tree

```text
/workspace
├── core/              # Deterministic builders, governance, scoring, sync
├── contracts/         # JSON schemas, canon, runes, routes
├── scripts/           # run_* artifact generators and CI runners
├── Scripts/           # Legacy casing duplicate (see anomalies)
├── tests/             # Pytest suite
├── docs/              # Human documentation and audit prose
├── operator_input/    # External operator payloads (non-authoritative until attested)
├── out/               # Generated artifacts (derived surfaces)
├── abraxas/           # v2 implementation subtree
├── abraxas_v2/        # Stub/placeholder
├── workflows/         # GitHub workflow helpers
├── fixtures/          # Shared test fixtures
├── README.md          # Primary overview
├── PLANS.md           # Canonical roadmap edge
└── AGENTS.md          # Agent operating doctrine
```

---

## Core subsystem map (by file count)

| Subdomain | Approx. `.py` files | Purpose |
|-----------|--------------------:|---------|
| `(root modules)` | 513 | Flat `core/*.py` builders (codegen, temporal, operator narrative, chamfer, etc.) |
| `core/sync/` | 137 | v2 hygiene sync, phase artifacts |
| `core/ingest/` | 17 | Controlled ingest, scheduler handoff |
| `core/governance/` | (see graph) | Authority, Brier provenance |
| `core/scoring/` | (see graph) | Deterministic ledger scoring |
| Overlay / proposal / manual execution families | ~12–13 each | Sandbox, custody, receipt chains |

**Navigation:** Prefer [`docs/INDEX.md`](../INDEX.md) subsystem map and MCP graph tools (`search_graph`, `trace_call_path`) over raw directory walks.

---

## Scripts inventory

| Prefix family | `run_*.py` count | Primary purpose |
|---------------|----------------:|-----------------|
| `v2_hygiene` | 108 | Hygiene phase stabilization chain |
| `abx_codegen` | 56 | Codegen intelligence spine |
| `temporal_continuity` | 53 | P70–P102 continuity spine |
| `research_canary` | 29 | P103–P130 canary chain |
| `operator_narrative` | 23 | P42/P44 narrative surfaces |
| `runtime_integration` | 10 | Shadow wiring hooks |
| `chamfer_*` | ~20+ | Geometric/chamfer planning arc (historical) |

**Entrypoints for contributors:** `python scripts/run_fast_ci.py`, `python scripts/readiness/run_canon_resume_state.py`, `python scripts/readiness/run_continuation_frontier_reconciliation.py`.

---

## Out/ artifact lanes (178 top-level)

| Lane group | Count | Classification |
|------------|------:|----------------|
| `research_canary*` / `research_*` | 42 | REFERENCE — P103–P130 spine (do not regenerate casually) |
| `temporal_continuity*` | 42 | REFERENCE — historical procedural chain |
| `chamfer*` | 21 | ARCHIVED — geometric planning arc v0.1 |
| `proposal*` / `overlay*` | 24 | REFERENCE — sandbox/overlay research |
| `canary*` (non-research) | 8 | REFERENCE |
| `continuity_namespace*` | 5 | REFERENCE |
| `audit/` | 1 dir | ACTIVE — audit receipts including continuation frontier |
| `archive/` | 1 dir | ARCHIVED |
| `canon_resume_state/` | 1 dir | ACTIVE — continuity pointer |
| `operator_review/` | 1 dir | ACTIVE — operator disposition surfaces |
| `sync/` | 1 dir | ACTIVE — Notion reconciliation packets |

Full lane index: [`docs/artifacts/ARTIFACT_INDEX.md`](../artifacts/ARTIFACT_INDEX.md).

---

## Docs inventory

| Subdirectory | Files | Role |
|--------------|------:|------|
| `docs/plans/` | ~60 | P71–P99 temporal continuity + phase plans (**historical branch**) |
| `docs/audits/` | 48 | Audit receipts, execution receipts, archive seals |
| `docs/releases/` | 13 | Release and post-merge continuation plans |
| `docs/atlas/` | — | System architecture cards |
| `docs/operators/` | 4 | Role paths (new-operator, contributor, researcher, architect) |
| `docs/workflows/` | 2 | CLI operator layer, codebase memory MCP |
| `docs/notion/` | 1 | Governance V3 Notion sync checklist |
| `docs/status/` | — | Generated badges and continuity spine JSON |

---

## Operator input inventory

**Live payloads (14 JSON):** see [`operator_input/README.md`](../../operator_input/README.md).

**Templates:** `operator_input/templates/` (30+ handoff/example files).

---

## Orphans and anomalies

| Item | Severity | Action |
|------|----------|--------|
| `Scripts/` vs `scripts/` | Medium | Document only; do not merge without governed review |
| `docs/plans/P71–P99` | Low | Mark historical; superseded by Governance V3 + POST_2_5_0 audit |
| `docs/audits/*.json` (3 files) | Low | Machine-readable audit companions; keep alongside markdown |
| `docs/INDEX.md` pre-sweep | Medium | Expanded in sweep — was missing releases/artifacts/testing |
| `operator_input/` no root README | Medium | Added in sweep |
| `docs/artifacts/`, `docs/testing/` | Medium | Created in sweep |
| Stale #741 / intake BLOCKED references | Medium | Repaired in sweep (POST_2_5_0, PLANS, POST_MERGE_739, templates README) |
| Broken relative links in older release docs | Low | Cataloged in [`DOCUMENTATION_TOPOLOGY_AUDIT_001.md`](DOCUMENTATION_TOPOLOGY_AUDIT_001.md) |

---

## Missing README coverage (pre-sweep)

| Path | Status after sweep |
|------|-------------------|
| `operator_input/README.md` | Created |
| `docs/artifacts/ARTIFACT_INDEX.md` | Created |
| `docs/testing/TEST_INDEX.md` | Created |
| `docs/START_HERE.md` | Created |
| `docs/audits/AUDIT_INDEX.md` | Created |
| `docs/releases/RELEASE_INDEX.md` | Created |

---

## Governance note

This inventory is **advisory-only**. It does not authorize execution, mutate canon, regenerate canary artifacts, or change authority posture.
