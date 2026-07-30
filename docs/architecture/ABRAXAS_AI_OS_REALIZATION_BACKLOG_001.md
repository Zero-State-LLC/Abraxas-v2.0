# Abraxas AI OS — Realization Backlog 001

**Status:** ACTIVE · eng track under Governance V3  
**Date:** 2026-07-27  
**Authority:** LOCAL_DEV / SHADOW default · EXTERNAL_PRODUCTION remains operator-gated  
**Companions:**
- [`ABRAXAS_HERMES_OS_UNIFICATION_001.md`](ABRAXAS_HERMES_OS_UNIFICATION_001.md) — three-layer model
- [`VISUAL_OPERATING_SYSTEM.md`](../../design-system/VISUAL_OPERATING_SYSTEM.md)
- [`ALEMBIC_SPINE.md`](../alembic/ALEMBIC_SPINE.md)
- [`ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md`](ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md)
- [`PRODUCTION_TARGET_ARCHITECTURE_001.md`](PRODUCTION_TARGET_ARCHITECTURE_001.md)
- PR [#1052](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1052) — signal forage + Neon EvidencePack path (land first)

---

## 0. Definition of “done” (AI OS, not product go-live)

Abraxas is realized as an **AI OS** when an operator can run governed intelligence work through one coherent stack:

```text
Operator
  → Hermes (Agent OS): skills, packets, forage, loops
  → Abraxas core (Symbolic OS): EvidencePack → ingest → belief/oracle/alembic → receipts
  → AAL-Viz (Visual OS): registers/authority legible
  → back to Operator (disposition only on conflict / production)
```

**Done ≠ EXTERNAL_PRODUCTION.** Done means the *kernel path* is real, contract-bound, and replayable under LOCAL_DEV/SANDBOX.

### Acceptance criteria (OS kernel)

| # | Criterion | Evidence |
|---|-----------|----------|
| K1 | Single mental model doc + STATUS row | This file + unification 001 + STATUS |
| K2 | Signal syscall: forage → EvidencePack.v0 | `abx-familiar-signal-forager` + fixture |
| K3 | Pack is a first-class contract (not skill-only) | `contracts/` schema + core validate |
| K4 | Pack → ingest bridge (SHADOW) | runner + receipt |
| K5 | Ingest → advisory spine touchpoint | Oracle/BeliefGraph or explicit abstain receipt |
| K6 | Neon Genie refuses commercial claims without pack | #1052 tests |
| K7 | Hermes can discover Abraxas skills | `skills.external_dirs` |
| K8 | WorkPacket/Handoff loop usable for multi-agent | already on main |
| K9 | Visual OS encodes pack registers | AAL-Viz chips / token bind |
| K10 | Learning loop: OperationTrace → evolution SHADOW | hermes-surface + skill-evolution |
| K11 | Product CLI surfaces OS status | `python -m abraxas status` (or subcmd) shows OS kernel posture |
| K12 | Fast CI green on all of the above | PR checks |

**Explicitly not required for AI OS realization:** CLEAR mass deletion, live providers, sandbox probe, EXTERNAL_PRODUCTION unhold.

---

## 1. What already exists (do not rebuild)

| Layer | Landed | Proof |
|-------|--------|-------|
| L0 Operator doctrine | GOVERNANCE_V3, activation lanes, conflict detect→classify→operator | main |
| L1 Hermes mount | `skills.external_dirs`, master-loop, forager, Neon pack path | #1052 + local config |
| L1 Operator loop | WorkPacket.v1, HandoffEnvelope.v1, glyphs, gh/CI glance | #1033–#1046 |
| L2 Product spine target | InputEnvelope → Ingest → Evidence → BeliefGraph → Oracle → Advisory | ARCHITECTURE.md |
| L2 CLI / API | `abraxas` CLI, `create_app`, DeniedProvider default | main |
| L2 Alembic | Advisory complete w/ residuals (stubs OK) | ALEMBIC_SPINE.md |
| L2 CFAR | Construct-first advisory gate | #1030 |
| L3 Visual OS | tokens, icons, runes, AAL-Viz batches 0–4 + operator-loop | design-system/ |
| Convergence | Phase 0–14 landed; candidate held | STATUS |

---

## 2. Gap map (realization blockers)

### Critical path (kernel)

```text
[A] Land #1052
      ↓
[B] Promote EvidencePack.v0 → contracts/ + core validate
      ↓
[C] familiar_ingestion pipeline: pack → IngestReceipt (SHADOW)
      ↓
[D] Bridge IngestReceipt → Oracle intake OR BeliefGraph seed (advisory)
      ↓
[E] CLI: abraxas os status | forage validate | ingest-from-pack
      ↓
[F] Visual: register chips for EvidencePack on AAL-Viz / console
      ↓
[G] Trace: forage/neon receipts → OperationTrace emitter in-repo
      ↓
[H] STATUS/PLANS/README declare AI OS kernel ACTIVE_SHADOW
```

### Parallel (important, not blocking kernel)

- Missing pipeline contracts (Neon, Noctis, Holler, …) — **contract stubs only** until product pressure
- Alembic residual operator review + stub adapters stay stubbed
- Repo-intel real implementation (beyond SKILL stub)
- Hyperagent forager dry-run roles
- hermes-surface fold / pin in docs

### Operator-only tracks (do not mix into OS eng PRs)

- CLEAR dual-control attestations
- Live provider authorization
- ORACLE_SANDBOX_PROBE_GATE_CONFIRMED
- EXTERNAL_PRODUCTION / deploy unhold

---

## 3. Work packages (repo tasks)

Priority: **P0** merge foundation → **P1** kernel contracts → **P2** spine bridge → **P3** surface/UX → **P4** harden/pluralism.

### WP-0 — Foundation merge

| ID | Task | Owner surface | Done when |
|----|------|---------------|-----------|
| WP-0.1 | Merge PR #1052 (forager + Neon EvidencePack path + OS unification doc) | GitHub | green CI + merge |
| WP-0.2 | Refresh STATUS current-state: AI OS kernel track + #1052 | STATUS.md | row + evidence links |
| WP-0.3 | Point PLANS active workstreams at AI OS realization (keep CLEAR as operator track) | PLANS.md | non-conflicting dual tracks |

### WP-1 — EvidencePack as OS primitive (contracts)

| ID | Task | Owner surface | Done when |
|----|------|---------------|-----------|
| WP-1.1 | Lift schema to `contracts/signal/evidence_pack.v0.schema.json` (skill copy remains mirror or `$ref`) | contracts/ | schema in tree + test |
| WP-1.2 | `core/signal/evidence_pack.py` — load, validate (jsonschema), register_counts, commercial gate (share logic w/ Neon) | core/ | unit tests; Neon imports core or thin adapter |
| WP-1.3 | Runner `scripts/research/run_evidence_pack_validate.py` (or extend existing template) | scripts/research/ | validate fixture + fail closed |
| WP-1.4 | ADR-short or docs note: EvidencePack is session/operator evidence until ingest promotes | docs/adr or architecture | linked from unification doc |
| WP-1.5 | Fixture remains under skill; golden path test uses contracts validate | tests/ | CI |

### WP-2 — familiar_ingestion pipeline (syscall → substrate)

| ID | Task | Owner surface | Done when |
|----|------|---------------|-----------|
| WP-2.1 | Contract: `contracts/ingest/familiar_ingestion_receipt.v0.schema.json` (or v1) | contracts/ | schema |
| WP-2.2 | `core/` builder: EvidencePack → FamiliarIngestionReceipt (SHADOW, no network) | core/ | pure function + hash |
| WP-2.3 | Runner writes receipt under `out/signal_forage/...` or `out/ingest/familiar_*` via classified writer | scripts/ingest/ | sole-writer discipline |
| WP-2.4 | Update `core/pipelines/registry.py` familiar_ingestion: MISSING_CONTRACT → ALIGNED/PARTIAL | registry + ownership matrix | STATUS/matrix refresh |
| WP-2.5 | Tests: pack fixture → receipt replay-stable | tests/ | green |

### WP-3 — Spine touchpoint (ingest → advisory)

| ID | Task | Owner surface | Done when |
|----|------|---------------|-----------|
| WP-3.1 | Inventory existing universal_ingest / oracle intake hooks for pack-shaped evidence | docs + core | short design note |
| WP-3.2 | Minimal adapter: FamiliarIngestionReceipt → InputEnvelope fields **or** Oracle shadow intake packet | core/ingest or oracle | advisory only |
| WP-3.3 | Explicit abstain path when envelope incomplete (NOT_COMPUTABLE preserved) | core/ | test |
| WP-3.4 | Optional: CFAR pre-check wrapper before forage expansion (doc + thin CLI flag) | core/cfar + skill | advisory |

*Do not require BeliefGraph full GSP production for OS kernel — seed or shadow packet is enough.*

### WP-4 — Product CLI as OS control plane

| ID | Task | Owner surface | Done when |
|----|------|---------------|-----------|
| WP-4.1 | `python -m abraxas os status` — kernel posture: skills present, last pack path, activation lane, alembic status | abraxas/cli.py | LOCAL_DEV |
| WP-4.2 | `python -m abraxas forage validate PATH` | CLI → core validate | exit codes |
| WP-4.3 | `python -m abraxas forage ingest PATH` — SHADOW receipt only | CLI → WP-2 runner | no network |
| WP-4.4 | Document in QUICKSTART + OS unification §9 | docs | linked |

### WP-5 — Visual OS bind (registers legible)

| ID | Task | Owner surface | Done when |
|----|------|---------------|-----------|
| WP-5.1 | Token/chip mapping for EvidencePack registers already in Visual OS → confirm completeness | design-system | checklist |
| WP-5.2 | AAL-Viz projection: render pack summary (counts + top OBSERVED) from JSON fixture | design-system/aal-viz or console | dry-run builder |
| WP-5.3 | Operator-loop glyph/docs cross-link “signal syscall” | aal-viz/operator_loop | doc only OK |

### WP-6 — Agent OS closed loop (learning)

| ID | Task | Owner surface | Done when |
|----|------|---------------|-----------|
| WP-6.1 | In-repo OperationTrace emitter path under `hermes-surface/` or `skills/.../scripts` (canonical, scrubbed) | hermes-surface or skills | runnable |
| WP-6.2 | Adapter: FamiliarIngestionReceipt / Neon receipt → OperationTrace v0.1 | scripts | SHADOW |
| WP-6.3 | Document weekly evolution cycle command (already exists) + when to run | docs/workflows | |
| WP-6.4 | Optional: pin distilled skill set list in `docs/skills/DISTILLED_OS_SKILL_SET.md` (copy from artifacts) | docs | |

### WP-7 — Contract debt (OS-adjacent product surfaces)

Prioritize only if they block the kernel path; otherwise stub contracts.

| ID | Subsystem | Next eng action | Priority |
|----|-----------|-----------------|----------|
| WP-7.1 | abx-familiar | closed by WP-2 | **P1** |
| WP-7.2 | neon_genie_ideation | venture packet + novelty/overlap receipt schema | P2 |
| WP-7.3 | universal_ingest | pack-aware source type in global pipeline | P2 (with WP-3) |
| WP-7.4 | noctis_dream | receipt + IR schema | P3 |
| WP-7.5 | hollersports_ticket | forecast proof chain | P3 (product) |
| WP-7.6 | memetic_futurecast | horizon + Brier bridge | P3 |
| WP-7.7 | level99 / phonomicon / beatoven | defer | P4 |

### WP-8 — Alembic pluralism (optional AI OS depth)

| ID | Task | Done when |
|----|------|-----------|
| WP-8.1 | Operator residual review of live rune proposals (doc disposition) | decision recorded |
| WP-8.2 | Keep SNN/SSM/generative **stubbed** until evaluation dossier | no fake adapters |
| WP-8.3 | Wire Alembic shadow compare receipt into `abraxas os status` | CLI shows residual flag |

### WP-9 — Multi-agent OS ops (Hermes/Grok/Codex)

| ID | Task | Done when |
|----|------|-----------|
| WP-9.1 | Example WorkPacket templates for: forage, ingest bridge, viz bind | `docs/` or `fixtures/` |
| WP-9.2 | Handoff checklist in master-loop skill points at EvidencePack path field | skill patch |
| WP-9.3 | Hyperagent forager role dry-run only | no live deploy |

### WP-10 — Hygiene / declaration

| ID | Task | Done when |
|----|------|-----------|
| WP-10.1 | STATUS: AI OS kernel `ACTIVE_SHADOW` once WP-1–4 land | |
| WP-10.2 | README “What this is” includes AI OS one-liner + link | |
| WP-10.3 | AGENTS.md one paragraph: OS kernel path + forage first | |
| WP-10.4 | Do not flip production readiness from this track | held |

---

## 4. Suggested sprint slices (mergeable PR sizes)

### Slice A — “Contracts” (after #1052)

WP-1.1–1.5 · small · pure validate · **IN PROGRESS / this PR track**

- [x] `contracts/signal/evidence_pack.v0.schema.json`
- [x] `core/signal/evidence_pack.py` + package export
- [x] Neon Genie facade re-exports core
- [x] `scripts/research/run_evidence_pack_validate.py`
- [x] tests: `tests/test_evidence_pack_core.py`

### Slice B — “Familiar ingestion”

WP-2.1–2.5 · medium · receipt writer · **this PR track**

- [x] `contracts/ingest/familiar_ingestion_receipt.v0.schema.json`
- [x] `core/ingest/familiar_ingestion_receipt.py`
- [x] `scripts/ingest/run_familiar_ingestion_from_pack.py`
- [x] tests: `tests/test_familiar_ingestion_receipt.py`
- [x] registry + ownership matrix next_action refresh

### Slice C — “Spine touch + CLI”

WP-3.1–3.3 + WP-4.1–4.3 · medium · **this PR track**

- [x] FamiliarSpineTouchpoint.v0 contract + `core/signal/spine_bridge.py`
- [x] `python -m abraxas os status`
- [x] `python -m abraxas forage validate|ingest|spine-touch`
- [x] tests: `tests/test_ai_os_slice_c.py`

### Slice D — “Viz + traces”

WP-5 + WP-6 · medium · projection + SHADOW emit · **COMPLETE**

- [x] `core/signal/operation_trace_adapter.py` — receipt / touchpoint → OperationTrace v0.1
- [x] CLI `forage ingest` now emits `os_signal_*.latest.json` to `out/audit`
- [x] Emitter updated to pick up OS signal traces
- [x] `tests/test_operation_trace_adapter.py`
- [x] AAL-Viz chip / register for evidence density / signal tiers (visual bind) — palette + viz-primitives + CSS


### Slice F — “Real session volume in evolution cycle”

Hermes-native forager + visual registers (current branch).

- [x] Enhanced `--from-hermes-traces` → higher-density packs (0.82 achieved, strong OBSERVED bias)
- [x] Better claims + direct `os_kernel.*` palette register mapping in provenance (palette_registers field + confidence notes)
- [x] Feed volume into abx-hermes-skill-evolution (runner now emits OperationTrace via adapter; emitter picks os_signal traces)
- [x] End-to-end example: scripts/research/run_slice_f_end_to_end_example.py (pack → trace → emitter)

### Post-Slice F Continuation (current work)
- [x] TDD test for signal_forage trace in evolution
- [x] Minimal SHADOW ledger bridge: scripts/research/run_hermes_signal_evolution_ingest.py
- [x] Additional P3 pluralism dry-run
- [x] Enhanced E2E to call ledger bridge
- [x] Update full backlog with new artifacts and commit



### Slice E — “Declare”

WP-0.2–0.3 rest + WP-10 · docs only after A–C green

---

## 5. Default build order (next actions)

1. **Merge #1052** (CI already green).
2. **Slice A** — EvidencePack in `contracts/` + `core/signal`.
3. **Slice B** — familiar_ingestion receipt closes ownership matrix gap.
4. **Slice C** — CLI OS control plane + minimal spine adapter.
5. **Slice D** — Visual bind + OperationTrace closed loop. **COMPLETE**
6. **Slice E** — STATUS/PLANS declare AI OS kernel ACTIVE_SHADOW. **COMPLETE**
7. Hermes signal volume + evolution tie-in (current branch) + optional WP-7/8 product depth (SHADOW only).

---

## 6. Anti-patterns (kill these if they appear)

- Rebuilding Hermes inside Abraxas
- Treating Visual OS as activation authority
- Coupling CLEAR deletion to OS kernel PRs
- Inventing market claims without packs
- Implementing Alembic stubs as “success”
- Auto-resolving Oracle conflicts
- Network at import time for providers
- One mega-PR that mixes kernel + production unhold

---

## 7. Tracking

| Field | Value |
|-------|--------|
| Eng track name | `AI_OS_KERNEL` |
| First merge gate | #1052 |
| Primary packages | `contracts/signal`, `core/signal`, `core` ingest bridge, `abraxas/cli`, `design-system/aal-viz`, skills |
| Success | K1–K12 above under LOCAL_DEV |

---

*This backlog is the realization plan for Abraxas as AI OS. It does not authorize production activation.*
