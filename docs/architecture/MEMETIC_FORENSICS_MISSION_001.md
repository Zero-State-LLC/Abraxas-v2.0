# Memetic Forensics Mission 001

**Status:** ADVISORY / CONTRIBUTOR MISSION MAP  
**Date:** 2026-07-31  
**Authority:** None — does not grant execution, forecast routing, canon mutation, live publish, or EXTERNAL_PRODUCTION rights.  
**Lane:** SHADOW · `advisory_only`  
**Design source:** [`docs/superpowers/specs/2026-07-31-memetic-forensics-dual-function-design.md`](../superpowers/specs/2026-07-31-memetic-forensics-dual-function-design.md)  
**Implementation plan:** [`docs/superpowers/plans/2026-07-31-memetic-forensics-spine.md`](../superpowers/plans/2026-07-31-memetic-forensics-spine.md)

---

## 1. Dual mission

Abraxas v2.0 is a **forensics-gated memetic dual-function OS**:

1. **Symbolic analysis / meme forensics** — registers (OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE), provenance, graph structure, propagation-as-evidence, receipts.
2. **Memetic operations** — campaign/content routing (Level 99 / Neon-adjacent) when, and only when, forensics disposition allows (or an explicit operator override receipt exists).

Contributors should treat forensics as the product engine and ops as a gated secondary surface — not two equal parallel product tracks.

---

## 2. Forensics-gated ops rule

- **Ops is forensics-gated.** Campaign/content execution language must not open without a `ForensicDispositionPacket` path (or explicit operator override receipt).
- **Slice C builds the forensics engine only.** Ops stays stubbed; `MemeticOpsGate.v0` is always `DENIED` even when disposition is `READY`.
- Simulation may report `WOULD_ALLOW` for tests; that is not authority and does not open Level 99 / Neon hooks.
- CLEAR dual-control, EXTERNAL_PRODUCTION, and live publish remain **operator-only** and outside this mission map’s eng unlock.

```text
Operator (disposition / dual-control later)
        │
        ├── FORENSICS ENGINE (slice C — build)
        ├── OPS GATE (always DENIED this slice; would_allow simulation only)
        └── DEMOTE / PARK (no feature work this slice)
```

---

## 3. Slice C scope

**In scope (slice C — Memetic Forensics Spine):**

- Compose existing systems: forage → belief → memetic → propagation dry-run → disposition → closed OpsGate
- Packets: `ForensicDispositionPacket.v0`, `PropagationGraph.v0` (dry-run), `MemeticOpsGate.v0` (always DENIED)
- CLI: `python -m abraxas os forensics run|status` (when implemented in later C PRs)
- Role taxonomy tags; optional AAL-Viz forensic projection
- Fail-closed disposition (prefer HOLD / NOT_COMPUTABLE over READY)

**Slice C success criteria (design):** Operator runs a deterministic forensic path from an EvidencePack fixture to a `ForensicDispositionPacket.v0`; OpsGate remains DENIED even when disposition is READY; no EXTERNAL_PRODUCTION, no auto-publish, no live queue/ledger/memory write.

### Non-goals (slice C)

- EXTERNAL_PRODUCTION / live publish / auto-post
- Opening OpsGate for real Level 99 / Neon execution
- Mass deletion of PARK code
- Full `contracts/pipelines/*.v1_1.json` for all product surfaces
- Canon/runtime mutation from forensic READY
- Autonomous Notion writeback
- Mixing CLEAR dual-control deletion into forensics PRs

---

## 4. Role taxonomy (assimilate, do not delete)

| Role | Surfaces |
|------|----------|
| **FORENSIC_CORE** | familiar/forage chain, Belief Graph/MemEIC, memetic_futurecast, hyperstition/slang skills, conflict doctrine, new disposition/propagation/ops-gate, AAL-Viz forensic summary |
| **OPS_STUB** | level99_content, neon_genie_ideation (as forensic input only), campaign publish language (gate-closed) |
| **INFRA** | Governance V3, operator_review_queue, canon_sync, drift, Brier/PSE (calibration later), canonical writer, CI, Hermes/WorkPacket for forensic work |
| **PARK** | hollersports live odds stack, beatoven, phonomicon mint/export, CLEAR mass-delete track, Alembic unstub |

**STATUS language:**

| Priority | Objective |
|----------|-----------|
| Primary eng | Memetic Forensics Spine (slice C) |
| Secondary held | Memetic Ops (gated) |
| Operator-only | CLEAR dual-control, EXTERNAL_PRODUCTION |

Method: assimilate existing systems; demote/park non-core; no mass delete this slice.

---

## 5. PR order (slice C sketch)

| PR | Deliverable |
|----|-------------|
| **C0** | Docs: this mission map, role taxonomy, STATUS/unification pointers |
| **C1** | ForensicDispositionPacket.v0 schema + builder from pack→bridge |
| **C2** | PropagationGraph.v0 dry-run |
| **C3** | Wire disposition ← propagation (default require graph) |
| **C4** | MemeticOpsGate.v0 always DENIED |
| **C5** | CLI `os forensics run\|status` |
| **C6** | Optional AAL-Viz forensic projection |
| **C7** | Ownership/`os status` role tags (no mass delete) |

Dependency: C0 ∥ start; C1+C2 → C3 → C4 → C5; C6/C7 after C3+.

---

## 6. Related surfaces

| Document | Role |
|----------|------|
| [`docs/superpowers/specs/2026-07-31-memetic-forensics-dual-function-design.md`](../superpowers/specs/2026-07-31-memetic-forensics-dual-function-design.md) | Approved design (locked decisions, packets, disposition rules) |
| [`docs/superpowers/plans/2026-07-31-memetic-forensics-spine.md`](../superpowers/plans/2026-07-31-memetic-forensics-spine.md) | Implementation plan for slice C |
| [`docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md`](../plans/ABRAXAS_UNIFICATION_PLAN_002.md) | Whole-system AI OS unification front door |
| [`STATUS.md`](../../STATUS.md) | Active objective + current-state block |
| [`docs/architecture/AI_OS_KERNEL_AUDIT_001.md`](AI_OS_KERNEL_AUDIT_001.md) | Kernel ACTIVE_SHADOW audit (substrate; not this mission’s unlock) |

---

## Seal

Advisory contributor mission map only. Does not grant authority, mutate canon/runtime, enable writeback, promote shadow results, open OpsGate, authorize production, or unlock EXTERNAL_PRODUCTION. All eng work under this map remains SHADOW / `advisory_only` unless a separate operator attestation says otherwise.
