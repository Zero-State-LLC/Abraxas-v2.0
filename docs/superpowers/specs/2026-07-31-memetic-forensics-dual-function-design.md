# Memetic Forensics Dual-Function OS — Design Spec

**Date:** 2026-07-31  
**Status:** APPROVED_FOR_SPEC (operator design approval via brainstorming)  
**Authority:** ADVISORY design only · no production unlock · no live publish  
**Repo:** Abraxas-v2.0 · `main` at design time includes AI OS kernel ACTIVE_SHADOW and residual dry-runs (#1072–#1077)

---

## 1. Problem

Abraxas v2.0 has grown into a multi-product monorepo (forecast, sports, Neon, Level 99, Phonomicon, production-readiness, CLEAR). The profound identity already claimed is a **deterministic symbolic OS**. Without a sharp product function, eng effort redistributes into parallel residual dry-runs and inventory work without a single operator-visible mission.

**Redirect:** Use existing systems to focus on:

1. **Symbolic analysis / meme forensics** — registers, provenance, graph structure, propagation-as-evidence  
2. **Memetic operations** — campaign/content routing (Level 99 / Neon-adjacent)

Ops is **forensics-gated**. First shipped slice builds the **forensics engine only**; ops stays stubbed behind the gate.

---

## 2. Decisions (locked)

| Decision | Choice |
|----------|--------|
| Mission | Dual function: forensics + ops |
| Coupling | Forensics-gated ops (explicit operator override receipt only) |
| First slice | **C — Forensics engine first** |
| Method | Assimilate existing systems; demote/park non-core; no mass delete |
| Approach | Memetic Forensics Spine (compose forage → belief → memetic → propagation → disposition → closed OpsGate) |

---

## 3. North star

Abraxas v2.0 is a **forensics-gated memetic dual-function OS**:

1. **Analyze** symbolic/meme streams with OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE, receipts, and graph structure.  
2. **Operate** campaigns only when forensics disposition is READY (or operator override receipt exists).

**Slice C success:** Operator runs a deterministic forensic path from an EvidencePack fixture to a `ForensicDispositionPacket.v0`; OpsGate remains DENIED even when disposition is READY; no EXTERNAL_PRODUCTION, no auto-publish, no live queue/ledger/memory write.

---

## 4. Architecture

### 4.1 Mental model

```text
Operator (disposition / dual-control later)
        │
        ├── FORENSICS ENGINE (slice C — build)
        ├── OPS GATE (always DENIED this slice; would_allow simulation only)
        └── DEMOTE / PARK (no feature work this slice)
```

### 4.2 Forensic path (compose)

| Stage | Surface | Role |
|-------|---------|------|
| 1 | EvidencePack.v0 / `forage` | Intake + registers |
| 2 | FamiliarIngestionReceipt | SHADOW ingest receipt |
| 3 | FamiliarSpineTouchpoint | Advisory spine seeds |
| 4 | FamiliarOracleBeliefBridge | Oracle/belief seeds only |
| 5 | Belief Graph / compositional memory | Symbolic structure; no canon mutation |
| 6 | Memetic futurecast + hyperstition/slang tags | Memetic charge as evidence |
| 7 | **PropagationGraph.v0** dry-run | Propagation structure; no network publish |
| 8 | **ForensicDispositionPacket.v0** | READY \| HOLD \| NOT_COMPUTABLE |
| 9 | **MemeticOpsGate.v0** | Always DENIED in slice C |

Optional adjuncts (not blocking): Noctis dream IR, research intake/validation, oracle_signal when already feeding packs. Existing dry-runs (familiar queue, noctis review, memetic Brier, holler outcome) remain optional side projections.

### 4.3 New packets (slice C)

#### ForensicDispositionPacket.v0

Required concepts:

- `schema_version`, `disposition_id`, `source_pack_hash`, `register_counts`
- `disposition`: `READY` | `HOLD` | `NOT_COMPUTABLE`
- `blocked_by[]`, `failed_gates[]`
- `inputs[]` — hashes of pack, receipt, bridge, graph seed, propagation dry-run
- `authority` — all false: execution, forecast_weight, publish, canon_mutation, queue_write
- `ops_gate_hint`: `DENIED` | `WOULD_ALLOW_IF_OPERATOR` (never auto-open)
- `canonical_hash`
- `advisory_only: true`, `lane: SHADOW`

#### PropagationGraph.v0 (dry-run)

- Nodes: source, meme_unit/claim, channel_class (no live account mutation by default)
- Edges: `observed_cite` | `inferred_echo` | `speculative_spread` (aligned to registers)
- `write_performed: false`, no social APIs
- Deterministic graph hash

#### MemeticOpsGate.v0

- Input: disposition packet only
- `gate_status: DENIED` always in slice C
- If disposition=READY → optional `simulation: WOULD_ALLOW` for tests only
- No Level 99 / Neon execution hooks in this packet

### 4.4 Disposition rules (v0)

| Condition | Disposition |
|-----------|-------------|
| Invalid/empty pack | NOT_COMPUTABLE |
| Insufficient OBSERVED density when policy requires it | HOLD |
| Open conflict requiring operator | HOLD |
| Privacy/medical blocks on dream-adjacent path | HOLD + blocked_by |
| Propagation dry-run missing (default policy) | HOLD |
| Authority leak in any input | HOLD + authority_violations |
| Pack valid, propagation complete, no hard blocks | READY |

Default: **propagation dry-run is required** before READY (no silent skip).

### 4.5 CLI (slice C)

```text
python -m abraxas os forensics run --pack PATH
python -m abraxas os forensics status
```

Optional `--out` audit artifacts via classified writer only. No campaign-run CLIs.

### 4.6 Failure handling

- Fail closed: prefer HOLD / NOT_COMPUTABLE over READY  
- No network at import  
- No writes to `out/operator_review_queue`, `out/brier`, durable memory, or live social sinks  
- Conflicts: Detect → Classify → Operator (existing doctrine)

### 4.7 Testing

- Fixture EvidencePack → stable disposition + graph hashes  
- Negatives: empty pack, authority leak, missing propagation  
- Invariant: disposition READY ⇒ OpsGate still DENIED  
- Determinism: identical inputs ⇒ identical packets  

---

## 5. Taxonomy (assimilate, do not delete)

| Role | Surfaces |
|------|----------|
| **FORENSIC_CORE** | familiar/forage chain, Belief Graph/MemEIC, memetic_futurecast, hyperstition/slang skills, conflict doctrine, new disposition/propagation/ops-gate, AAL-Viz forensic summary |
| **OPS_STUB** | level99_content, neon_genie_ideation (as forensic input only), campaign publish language (gate-closed) |
| **INFRA** | Governance V3, operator_review_queue, canon_sync, drift, Brier/PSE (calibration later), canonical writer, CI, Hermes/WorkPacket for forensic work |
| **PARK** | hollersports live odds stack, beatoven, phonomicon mint/export, CLEAR mass-delete track, Alembic unstub |

**STATUS language:** Primary eng objective = Memetic Forensics Spine (slice C). Secondary held = Memetic Ops (gated). Operator-only = CLEAR dual-control, EXTERNAL_PRODUCTION.

---

## 6. Implementation plan sketch (PR order)

| PR | Deliverable |
|----|-------------|
| **C0** | Docs: mission map, role taxonomy, STATUS/unification pointers |
| **C1** | ForensicDispositionPacket.v0 schema + builder from pack→bridge |
| **C2** | PropagationGraph.v0 dry-run |
| **C3** | Wire disposition ← propagation (default require graph) |
| **C4** | MemeticOpsGate.v0 always DENIED |
| **C5** | CLI `os forensics run|status` |
| **C6** | Optional AAL-Viz forensic projection |
| **C7** | Ownership/`os status` role tags (no mass delete) |

Dependency: C0 ∥ start; C1+C2 → C3 → C4 → C5; C6/C7 after C3+.

---

## 7. Explicit non-goals

- EXTERNAL_PRODUCTION / live publish / auto-post  
- Opening OpsGate for real Level 99 / Neon execution in slice C  
- Mass deletion of PARK code  
- Full `contracts/pipelines/*.v1_1.json` for all product surfaces  
- Canon/runtime mutation from forensic READY  
- Autonomous Notion writeback  
- Mixing CLEAR dual-control deletion into forensics PRs  

---

## 8. Later (out of this spec)

**Ops series (post-C):** Level 99 / Neon consume READY dispositions under dual-control; publish remains operator-gated. Separate design/plan required.

---

## 9. Risks

| Risk | Mitigation |
|------|------------|
| Scope creep into full OS rebuild | Compose existing CLI path; thin glue only |
| Ops pressure before forensics ready | OpsGate DENIED invariant in tests |
| Propagation graph becomes social crawler | Dry-run only; no network; channel_class not live accounts |
| Doc drift vs code | C0 + C7 refresh STATUS/matrix |

---

## 10. Approval record

| Section | Status |
|---------|--------|
| §1 North star & boundary | Approved (operator) |
| §2 Architecture & data flow | Approved |
| §3 Taxonomy | Approved |
| §4 Implementation sketch | Approved |
| Written spec | Pending operator file review |

---

## Seal

Design surface only. Does not grant authority, mutate canon/runtime, enable writeback, promote shadow results, or authorize production.
