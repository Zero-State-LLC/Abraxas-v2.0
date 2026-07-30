# Abraxas ↔ Hermes OS Unification 001

**Status:** ACTIVE DRAFT · advisory implementation spine  
**Date:** 2026-07-27  
**Authority:** LOCAL_DEV / SHADOW only · no EXTERNAL_PRODUCTION grant  
**Companions:** `design-system/VISUAL_OPERATING_SYSTEM.md` · `docs/plans/ALEMBIC_SPINE_UNIFICATION_PLAN_001.md` · `docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md` · `artifacts/hermes-surface/DISTILLED_HERMES_SKILL_SET.md`

---

## 1. What “unify into an OS” means here

Abraxas is not becoming a desktop kernel. It becomes a **three-layer operating system for governed intelligence work**, with Hermes as the interactive kernel and Abraxas as the deterministic substrate.

```text
┌─────────────────────────────────────────────────────────────┐
│  L0  OPERATOR  (Daniel) — authority, attestation, go/no-go  │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  L1  AGENT OS (Hermes / Abrasax)                            │
│  skills · memory · cron · gateway · operator loop routing   │
│  WorkPacket.v1 / HandoffEnvelope.v1 · skill evolution traces│
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  L2  SYMBOLIC / ADVISORY OS (Abraxas core)                  │
│  contracts · runes · YGGDRASIL · Oracle · BeliefGraph       │
│  Alembic Spine · ingest · receipts · Brier telemetry        │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  L3  VISUAL OS (design-system / AAL-Viz)                    │
│  semantic tokens · glyphs · console · projection only       │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Job | Must not |
|-------|-----|----------|
| **Visual OS** | Make registers/authority/evidence *legible* | Grant execution |
| **Alembic / Abraxas core** | Deterministic evidence → belief → advisory | Autopromote / deploy |
| **Hermes Agent OS** | Route work, acquire signal, run loops, remember | Bypass Abraxas locks |

Unification = **one mental model, one skill surface, one signal path**, not one monorepo binary.

---

## 2. Design invariants (non-negotiable)

From Abraxas AGENTS + Governance V3 + hermes-surface:

1. **Structure before narrative** — contracts/tokens before prose.
2. **Evidence before authority** — OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE.
3. **Governance before autonomy** — fail-closed; operator for EXTERNAL_PRODUCTION.
4. **Identity ≠ authority** — `producer_system` is provenance only.
5. **SHADOW default** — skill evolution never mutates active skills without operator.
6. **Scrub Hermes env for repo tests** — `env -u PYTHONPATH -u PYTHONHOME`.
7. **Smallest complete evidence packet** — CLI operators / forage receipts, not repo dumps.

---

## 3. Signal acquisition as the primary OS syscall

Everything useful upstream of Neon Genie, Oracle, forecasting, and evolution is **signal → evidence pack → ingest → register tags**.

### Target pipe

```text
Intent (Hermes)
  → abx-familiar-signal-forager   # acquire + normalize + tier claims
  → EvidencePack.v0               # OBSERVED/INFERRED/SPECULATIVE/NOT_COMPUTABLE
  → abraxas-ingest / universal_ingest  # when repo runner exists
  → BeliefGraph / Oracle / Neon Genie / evolution traces
  → receipts under out/ or session artifacts
```

### Hermes-native tools map (signal forage)

| Forage step | Hermes tool / skill |
|-------------|---------------------|
| Web discovery | `web_search`, `web_extract`, browser |
| Paper discovery | `arxiv` skill |
| Social signal | `x_search` / xurl |
| Markets | `polymarket` |
| Local/repo signal | `OP.SEARCH_SIGNAL` / repo-intel / `search_files` |
| Continuity | `session_search`, memory layers |
| Cron forage | `cronjob` with scrubbed scripts |
| Learning loop | OperationTrace → `abx-hermes-skill-evolution` |

**Rule:** Market/revenue/competitor/adoption claims without an EvidencePack → `NOT_COMPUTABLE`.

---

## 4. Hermes skill surface (how Abraxas mounts)

### Mount

```yaml
# ~/.hermes/config.yaml
skills:
  external_dirs:
    - /home/scrimshawlife/Abraxas-v2.0/skills
```

- External skills are **read-only** to curator (source of truth stays the repo).
- Nested SKILL.md (holler-*, hyperagent) are discoverable.
- Local `~/.hermes/skills/` still wins on name collision.

### Core load order for Abraxas sessions

1. `abraxas-master-loop-workflow` — loop engine  
2. `abx-familiar-signal-forager` — evidence first  
3. Task skills (`abx-neon-genie`, `abx-esoteric-intelligence`, `holler-*`, …)  
4. `abx-hermes-skill-evolution` — after meaningful work, emit traces  

Distilled set: `artifacts/hermes-surface/DISTILLED_HERMES_SKILL_SET.md`.

---

## 5. Patterns distilled to accelerate the build

| Pattern | Source | Use now |
|---------|--------|---------|
| **Semantic → presentation** | Visual OS | New states = tokens first, then CSS/glyphs |
| **Class-level umbrella skills** | skills/* | Prefer one SKILL.md + references/ over one-offs |
| **WorkPacket / HandoffEnvelope** | operator loop | Hermes routes; Grok/Codex produce; operator decides |
| **OperationTrace v0.1** | hermes-surface | Feed evolution without mutating skills |
| **SHADOW scrubbed cycles** | env reconstruction | Isolated uv + `env -u PYTHONPATH -u PYTHONHOME` |
| **Ownership matrix** | Neon Genie | Route, don’t absorb (forecast/dream/music/viz) |
| **EvidencePack gate** | Neon + Familiar | Blocks confident claims without forage |
| **Detect → Classify → Operator** | conflict doctrine | Never auto-resolve semantic conflict |
| **Lane-based activation** | GOVERNANCE_V3 | LOCAL_DEV free; EXTERNAL_PRODUCTION gated |
| **CFAR before retrieval** | `core/cfar.py` | Construct route before expensive forage |

---

## 6. Implementation roadmap (tight)

### P0 — Mount & missing syscall (this pass)

- [x] Document three-layer OS model (this file)
- [x] `skills.external_dirs` → Abraxas `skills/`
- [x] Author missing `abx-familiar-signal-forager` skill
- [x] Restore stub `abraxas-repo-intel` SKILL.md
- [x] Copy bridge emitter helpers into `~/.hermes/tools/` (optional)
- [x] Verify discovery against external_dirs scan

### P1 — Signal OS MVP

- [x] EvidencePack.v0 schema under `skills/abx-familiar-signal-forager/references/`
- [x] First live forage pack: `out/signal_forage/2026-07-27_hermes-agent-skill-os-patterns/`
- [x] Neon Genie `evidence_pack_path` wiring (`skills/abx-neon-genie/evidence_pack.py`)
- [x] Cron/operator template: `docs/workflows/SHADOW_SIGNAL_FORAGE_CRON_TEMPLATE.md` + `scripts/research/run_shadow_signal_forage_template.py`

### P2 — Closed loop

- Adapter: forage receipt → OperationTrace
- Evolution cycle volume from real Hermes sessions (advanced via --from-hermes-traces in forage template)
- AAL-Viz chips for pack tiers (Visual OS bind) — COMPLETE (topology_palette + viz-primitives registers)
- Repo-intel SKILL.md restore (dir exists, skill file missing)

### P3 — Pluralism

- Alembic residual operator review (live runes deferred)
- Hyperagent roles for long-running foragers (LA signal etc.) — dry-run first
- CLEAR dual-control remains separate operator track (do not couple)

### Realization backlog (canonical task list)

Full work-package breakdown: [`ABRAXAS_AI_OS_REALIZATION_BACKLOG_001.md`](ABRAXAS_AI_OS_REALIZATION_BACKLOG_001.md)

Order: merge #1052 → EvidencePack contracts/core → familiar_ingestion receipt → spine touch + CLI → viz/traces → STATUS declare `ACTIVE_SHADOW`.

---

## 7. Anti-goals

- Do not merge Abraxas core into Hermes source.
- Do not treat Visual OS assets as activation authority.
- Do not run live signal forage with `signal_forage_execution_authorized: true` without dual-control gates.
- Do not promote skill-evolution candidates without operator decision ledger.
- Do not open CLEAR mass deletion from this track.

---

## 8. Success criteria

1. From a fresh Hermes desktop session, agent can `skill_view` Abraxas master-loop + signal-forager without manual path hunting.
2. A forage task produces a durable EvidencePack with register tags and source URLs.
3. Neon Genie / research tasks refuse confident market claims without a pack.
4. Meaningful sessions emit OperationTraces; evolution cycle remains SHADOW.
5. Operator can point at one diagram (this doc §1) and the live skill mount and say “that’s the OS.”

---

## 9. Quick operator commands

```bash
# Mount Abraxas skills (if not already)
# skills.external_dirs must be a YAML list in ~/.hermes/config.yaml

# AI OS kernel posture
cd /home/scrimshawlife/Abraxas-v2.0
env -u PYTHONPATH -u PYTHONHOME .venv/bin/python -m abraxas os status

# Signal syscall
env -u PYTHONPATH -u PYTHONHOME .venv/bin/python -m abraxas forage validate \
  --pack skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json
env -u PYTHONPATH -u PYTHONHOME .venv/bin/python -m abraxas forage ingest \
  --pack skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json \
  --print-only
env -u PYTHONPATH -u PYTHONHOME .venv/bin/python -m abraxas forage spine-touch \
  --pack skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json

# Scrubbed Abraxas work
env -u PYTHONPATH -u PYTHONHOME .venv/bin/python scripts/run_fast_ci.py

# Evolution cycle (SHADOW)
env -u PYTHONPATH -u PYTHONHOME .venv/bin/python \
  scripts/codegen/run_abx_hermes_skill_evolution_cycle.py
```

---

*Seal: advisory OS spine. Unifies mental model and skill mount; does not grant production activation.*


## Slice F Progress (current)
- Hermes volume fed into OperationTrace + emitter
- End-to-end example script
- P3 dry-runs started (Hyperagent + Alembic/pluralism notes)


## Post-Slice F Hermes Volume to Evolution (2026-07-30 continuation)
- Ledger bridge implemented for signal_forage
- Pluralism dry-runs expanded
- Full E2E with ledger step
All SHADOW, operator review pending for any future promotion.
