# Forensics contracts

SHADOW advisory memetic forensics spine (slice C). No network crawl, no queue write, no Brier resolution, no publish/execution authority.

| Schema | Role |
|--------|------|
| `propagation_graph.v0.schema.json` | PropagationGraph.v0 — dry-run graph from EvidencePack sources/claims (`write_performed` always false, `network_calls` always false) |
| `forensic_disposition.v0.schema.json` | ForensicDispositionPacket.v0 — READY / HOLD / NOT_COMPUTABLE from pack + propagation; ops never auto-open |
| `memetic_ops_gate.v0.schema.json` | MemeticOpsGate.v0 — always `gate_status: DENIED` in slice C even when disposition is READY |
| `aal_viz_forensic_projection.v0.schema.json` | AALVizForensicProjection.v0 — projection-only view of ForensicRunPacket (C6); ops always DENIED |

## ForensicRunPacket.v0 (inline composition)

No separate schema file yet. Built by `core.forensics.pipeline.run_forensics_from_pack_path` as the compose envelope:

| Key | Notes |
|-----|--------|
| `schema_version` | `"ForensicRunPacket.v0"` |
| `pack_path` | Path string of the EvidencePack input |
| `pack_id` | From pack (may be null) |
| `pack_hash` | Pack-native hash, bridge hash, or derived `canonical_hash` |
| `bridge_status` | From familiar oracle belief bridge (SHADOW) |
| `propagation` | PropagationGraph.v0 body |
| `disposition` | ForensicDispositionPacket.v0 body |
| `ops_gate` | MemeticOpsGate.v0 body — **always DENIED** |
| `ok` | True when disposition ∈ {READY, HOLD, NOT_COMPUTABLE} and gate is DENIED |
| `advisory_only` | Always `true` |
| `lane` | Always `"SHADOW"` |
| `authority` | All grants false (execution / forecast / canon / publish / queue) |
| `canonical_hash` | Deterministic hash of body without this field |

**Seal language:** advisory only; no authority grant. `ops_gate.gate_status` is always `DENIED` on this slice. Simulation may report `WOULD_ALLOW` / `WOULD_DENY` for operator review, but never opens ops.

## Canonical builders

| Module | Builder |
|--------|---------|
| `core.forensics.propagation_graph` | `build_propagation_graph_from_pack` |
| `core.forensics.disposition` | `build_forensic_disposition` |
| `core.forensics.ops_gate` | `build_memetic_ops_gate` |
| `core.forensics.pipeline` | `run_forensics_from_pack_path` |
| `core.forensics.aal_viz_projection` | `build_aal_viz_forensic_projection` / `…_from_pack_path` |

Package re-exports: `core.forensics` (`__all__` lists the builders above).

## CLI

```bash
python -m abraxas os forensics run --pack PATH_TO_EVIDENCE_PACK.json
python -m abraxas os forensics project --pack PATH_TO_EVIDENCE_PACK.json
python -m abraxas os forensics status
```

- `run` — EvidencePack path → ForensicRunPacket summary (SHADOW; ops gate always DENIED)
- `project` — EvidencePack path → AALVizForensicProjection.v0 summary (projection-only; DENIED)
- `status` — engine posture (`forensics_engine: SLICE_C`, `ops_gate_default: DENIED`); no prior-run disk dependency

## Authority boundary

- Producer identity records provenance; it does not grant authority.
- No live publish, operator queue write, Brier outcome resolution, or production activation from this surface.
- Real ops opening (Level 99 / Neon dual-control) is deferred beyond slice C.
