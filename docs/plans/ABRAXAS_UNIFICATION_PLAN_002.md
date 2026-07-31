# Abraxas Unification Plan 002

**Status:** PROPOSAL · `ADVISORY_ONLY` · operator review required  
**Date:** 2026-07-31  
**Authority locks:** `canon_mutation=false` · `runtime_mutation=false` · `execution_authority=false` · `writeback=false`  
**North star:** Abraxas as a **deterministic symbolic AI OS** (not a desktop kernel, not EXTERNAL_PRODUCTION).  
**Supersedes as front-door:** does not delete `docs/plans/ALEMBIC_SPINE_UNIFICATION_PLAN_001.md`; that plan is the multi-architecture track. This plan **unifies the whole Abraxas surface** around what is already observed on `main`.

## 0. AI OS framing (the evolution we discussed)

“Evolve to an AI OS” means **one governed stack for intelligence work**, not a product launch:

```text
L0  Operator — authority, attestation, go/no-go
L1  Agent OS (Hermes) — skills, memory, loops, WorkPacket/Handoff
L2  Symbolic OS (Abraxas core) — contracts, runes, YGGDRASIL, Oracle,
    BeliefGraph, Alembic, ingest, receipts, Brier
L3  Visual OS (design-system / AAL-Viz) — legibility only, no execution
```

| Document | Role |
|----------|------|
| [`docs/architecture/ABRAXAS_HERMES_OS_UNIFICATION_001.md`](../architecture/ABRAXAS_HERMES_OS_UNIFICATION_001.md) | Three-layer OS model + Hermes mount |
| [`docs/architecture/ABRAXAS_AI_OS_REALIZATION_BACKLOG_001.md`](../architecture/ABRAXAS_AI_OS_REALIZATION_BACKLOG_001.md) | Kernel path WPs / slices A–E |
| [`docs/architecture/AI_OS_PRIMITIVES_MAP_001.md`](../architecture/AI_OS_PRIMITIVES_MAP_001.md) | Classic OS primitives → Abraxas surfaces (PR #1050) |
| [`docs/alembic/ALEMBIC_SPINE.md`](../alembic/ALEMBIC_SPINE.md) | Multi-architecture “pluralism” layer inside L2 |
| This file (002) | Whole-system unification + how tracks serve AI OS |

**Primary OS syscall (signal path):**

```text
Intent (Hermes)
  → signal forager → EvidencePack (OBSERVED|INFERRED|SPECULATIVE|NOT_COMPUTABLE)
  → universal_ingest / familiar_ingestion (SHADOW)
  → BeliefGraph / Oracle / Alembic / domain pipelines
  → receipts → Operator disposition
```

**Done for AI OS ≠ EXTERNAL_PRODUCTION.** Done = kernel path real, contract-bound, replayable under LOCAL_DEV/SHADOW (see realization backlog K1–K12).

### How Tracks A–D serve AI OS

| Track | AI OS layer | Serves |
|-------|-------------|--------|
| **A** Navigation | L0–L3 mental model | K1 — single map |
| **B** MISSING_CONTRACT | L2 pipelines | K3–K6 — every product surface is a real pipeline, not a skill-only story |
| **C** Alembic residuals | L2 pluralism | K5 optional depth — multi-architecture select/fuse |
| **D** Authz compression | L0 governance | Prevents recursive plan trees from blocking kernel work |

## 1. Why unify

Abraxas v2.0 is strong as a **fail-closed, receipt-first symbolic substrate**, but the working surface has fragmented across:

| Fragmentation class | OBSERVED signal |
|---------------------|-----------------|
| Multi-architecture orchestration | Alembic Spine **advisory-complete with residuals** (`core/alembic/`, `docs/alembic/ALEMBIC_SPINE.md`) |
| Subsystem contracts | Ownership matrix: **18 subsystems**, **8 MISSING_CONTRACT** |
| Planning / authorization chains | Long recursive operator-review and temporal-continuity plan families under `docs/plans/` + `out/` |
| Skills / Hermes adapters | Multiple skills with overlapping “route / invent / govern” language |
| Docs navigation | START_HERE / INDEX / STATUS / PLANS all active; contributors must know which is authoritative |

**Goal:** one mental model and one next-action map so operators and agents stop inventing parallel spines.

## 2. Unification thesis

```text
                    ┌─────────────────────────────┐
                    │   Operator + Governance V3  │
                    │   (fail-closed, receipts)   │
                    └─────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
  Artifact spine            Alembic spine             Domain pipelines
  (contracts → core →       (architecture select,     (oracle, ingest,
   scripts → out → tests)    fuse, verify, shadow)     forecast, viz, …)
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ▼
                     Ownership matrix + PLANS.md
                     (what is ALIGNED vs MISSING_CONTRACT)
```

**Single sentence:** Abraxas is one governed substrate; Alembic is the multi-architecture *selector/fusion* layer on top of it; every other subsystem is a **pipeline with a contract**, not a second OS.

## 3. Canonical ownership (do not fork)

| Concern | Canonical owner | Do not create |
|---------|-----------------|---------------|
| Authority / gates / operator decision records | Governance V3 + `operator_review` | Parallel approval engines |
| Deterministic JSON + hashes | `core/canonical/` | Ad-hoc serializers |
| Pipeline inventory / routing topology | `core/pipelines/`, YGGDRASIL | Second graph of “systems” |
| Multi-architecture select/fuse | `core/alembic/` | Generic LLM router product |
| Scoring / Brier | `core/scoring/`, calibration contracts | Per-skill score dialects |
| Ingest / Oracle signal | `core/ingest/`, oracle surfaces | Shadow ingest clones |
| Product / opportunity packaging (external) | Separate product skills when needed | Absorb into Abraxas runtime authority |
| Forecast vs SHADOW | Doctrine locks | Cross-lane auto-promotion |

## 4. Current-state baselines (OBSERVED)

### 4.1 Alembic Spine (multi-architecture track)

| Field | Value |
|-------|--------|
| Status | `ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS` |
| Code | `core/alembic/`, `contracts/alembic/`, `scripts/alembic/run_alembic_spine.py` |
| Tests | `tests/test_alembic_spine.py`, `tests/test_run_alembic_spine.py` |
| Docs | `docs/alembic/ALEMBIC_SPINE.md`, audit map, plan 001 |
| Residuals | Live `RUNE.ARCHITECTURE_*` deferred; SSM/generative/SNN stubs; optional pipeline inventory seal deferred |

Phase 1 of plan 001 is **implemented as advisory**. Unification work here is **residuals + integration**, not greenfield.

### 4.2 Ownership matrix (contract track)

From `docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md` (advisory projection):

| ALIGNED (keep; tighten receipts) | MISSING_CONTRACT (priority backlog) |
|----------------------------------|-------------------------------------|
| AAL-Viz, Canon Governance, Drift, Operator Governance, Oracle Signal, Outcome/Brier, PSE Forecast, Research Intake, Research Validation, Universal Ingest | BeatOven/PsyFi, HollerSports, Level 99, **Neon Genie**, Noctis, Oracle/ASE/Memetic Futurecast, Phonomicon, abx-familiar |

### 4.3 Production posture

Production activation remains **DENIED / HELD_FOR_OPERATOR**. Unification does **not** unlock deploy.

## 5. Unification tracks (ordered)

### Track A — Mental model & navigation (1–3 days, docs-only)

**Outcome:** One front door for “where do I work?”

| Action | Artifact |
|--------|----------|
| Keep this file as unification front door | `docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md` |
| Point START_HERE / INDEX “Active Work Route” at Tracks A–D | docs only |
| Declare PLANS.md `alembic_spine` + ownership matrix as **status truth** | no second status DB |
| Deprecate *narrative* competition among plans: older plans become historical unless linked here | docs classification only |

**Exit:** Contributor can answer in 5 minutes: spine vs pipeline vs shadow vs forecast.

### Track B — Contract closure for MISSING_CONTRACT subsystems (2–6 weeks)

**Outcome:** Every Tier-2/3 shadow product has a minimal pipeline contract + receipt shape.

Priority order (fail-closed, smallest contract first):

1. **Neon Genie ideation** — novelty validation + operator packet (no packaging runtime authority in Abraxas core)
2. **abx-familiar** — receipt + proof + review chain
3. **Noctis** — dream analysis → receipt + IR + review
4. **HollerSports** — forecast proof + outcome binding
5. **Memetic futurecast / ASE** — horizon policy + validation gates + Brier bridge
6. **Level 99** — virality scoring boundaries + operator review
7. **BeatOven / PsyFi** — shared runic core pipeline contract
8. **Phonomicon** — provenance / artifact proof chain

**Pattern per subsystem (mandatory):**

```text
contract (JSON Schema) → core builder → scripts/run_* → out/ receipt
  → targeted tests → ownership matrix flip to ALIGNED
```

No contract → no claim of production readiness.

### Track C — Alembic residuals & integration (2–4 weeks, advisory)

**Outcome:** Spine remains advisory but is **wired as the multi-architecture entry**, not a side experiment.

| Residual | Recommended action | Gate |
|----------|--------------------|------|
| Live `RUNE.ARCHITECTURE_*` | Keep deferred; document reuse of bound pipeline runes | Operator gate before catalog mutation |
| Stub backends (SSM / generative / SNN) | Leave stubs until evaluation fixtures exist | EvidencePack required to unstub |
| Oracle bridge | Keep metadata-only; no second oracle | Already fail-closed |
| Optional pipeline inventory registration | Register `alembic_spine` only when inventory seal is authorized | Explicit seal |

**Integration rule:** Domain pipelines may *emit architecture-tagged contributions* into Alembic; Alembic must not replace their contracts.

### Track D — Authorization surface compression (ongoing, advisory)

**Outcome:** Stop growing recursive plan/gate trees without terminal disposition.

| Action | Why |
|--------|-----|
| Prefer **one** decision record + hold receipt over nested plan→gate→plan chains | Operator review terminal-hold consolidation already points this way |
| New work must cite this plan’s track ID (A/B/C/D) | Prevents orphan plans |
| Bulk-hold families stay held unless attestation exists | No auto-unhold |

## 6. Explicit non-goals

- Merging external product repos into Abraxas monorepo “for convenience”
- Granting runtime, deploy, or canon authority via this plan
- Auto-applying Alembic router proposals
- Replacing Governance V3 with a lighter ad-hoc process
- Absorbing forecast into SHADOW or vice versa
- Unifying everything into a single skill or single CLI flag

## 7. Success metrics (evidence-bound)

| Metric | Target | Evidence |
|--------|--------|----------|
| MISSING_CONTRACT count | Decreasing; publish delta in ownership refresh receipts | matrix + audit receipt |
| Alembic advisory CLI | `validate-registry` + `execute-advisory` green on fixtures | tests on CI |
| Orphan plans | New plans link Track A–D or marked HISTORICAL | docs review |
| Authority incidents | Zero silent runtime/canon writes from unification work | PR checklist |
| Contributor time-to-route | ≤5 minutes from START_HERE to correct surface | qualitative operator check |

## 8. Immediate next steps (operator-gated)

Aligned with AI OS realization backlog (prefer finishing kernel path over new parallel tracks):

1. **Review this plan** — accept, amend, or reject (docs PR / comment enough for advisory).
2. **Reconcile STATUS** — if Slices A–E claim COMPLETE, confirm `AI_OS_KERNEL` / `ACTIVE_SHADOW` rows match repo evidence; fix drift only with links.
3. **Track A** — link START_HERE + PLANS + this file + Hermes OS unification 001 + realization backlog (one navigation triangle).
4. **Kernel continuity** — if any K1–K12 gap remains open on `main`, that beats new subsystem work; else **Track B** one MISSING_CONTRACT (recommended: familiar_ingestion / EvidencePack bridge residual or Neon ideation contract stub).
5. **Track C** — Alembic stays advisory; unstub only with evaluation fixtures.
6. **Do not** mix CLEAR dual-control / EXTERNAL_PRODUCTION unhold into AI OS eng PRs.
7. **Optional:** merge open primitives map PR #1050 if still desired as pure projection.

## 9. Relationship to prior plans

| Document | Role after 002 |
|----------|----------------|
| `docs/plans/ALEMBIC_SPINE_UNIFICATION_PLAN_001.md` | Historical + multi-arch vision; Phase 1 done as advisory |
| `docs/alembic/ALEMBIC_SPINE.md` | **Canonical Alembic behavior** |
| `docs/alembic/AUDIT_AND_RECONCILIATION_001.md` | Pre-implementation map (partially superseded by code) |
| `docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md` | **Canonical ownership projection** |
| `PLANS.md` `alembic_spine` block | Machine-readable status snippet |
| This file (002) | **Whole-system unification front door** |

## 10. Seal

Proposal surface only. Does **not** grant authority, mutate canon/runtime, enable writeback, promote shadow results, or register live runes. Aligns with Governance V3 and fail-closed development.

**Recommended PR title:** `docs: Abraxas unification plan 002 (front door + tracks A–D)`
