# C6 AAL-Viz Forensic Projection Design

**Status:** ADVISORY DESIGN · pending operator review  
**Date:** 2026-07-31  
**Lane:** SHADOW · `advisory_only` · `projection_only`  
**Authority:** None — does not open OpsGate, grant execution/publish, or authorize EXTERNAL_PRODUCTION  
**Parent:** [`2026-07-31-memetic-forensics-dual-function-design.md`](2026-07-31-memetic-forensics-dual-function-design.md)  
**Mission:** [`docs/architecture/MEMETIC_FORENSICS_MISSION_001.md`](../../architecture/MEMETIC_FORENSICS_MISSION_001.md)  
**Spine (landed):** PR #1079 · C′ seal PR #1080  

---

## 1. Goal

Ship a **thin, deterministic AAL-Viz projection packet** from an existing `ForensicRunPacket.v0` (or EvidencePack path via the existing forensics pipeline) so operators and projection consumers can see disposition + graph summary + **OpsGate DENIED** without leaving SHADOW.

**Success criteria:**

1. Fixture EvidencePack → projection with `disposition == READY`, `ops_gate_status == DENIED`, `projection_only == true`.
2. Same inputs → same `canonical_hash`.
3. No network, no queue/Brier/social writes, no OpsGate open, no live-console wiring required.
4. CI green with schema validation + pipeline-compose tests.

**Non-goals:**

- Live-console / public JSON auto-copy (deferred; may follow as one-liner once a consumer exists).
- Geometric renderer / WebGL / canvas graph full-render (wrong layer).
- Opening OpsGate, Level 99 / Neon hooks, or dual-control attestations.
- Canon/runtime mutation, EXTERNAL_PRODUCTION, readiness claims as true.
- Replacing CLI `os forensics run|status` (projection is additive).

---

## 2. Architecture

```text
EvidencePack path
      │
      ▼
run_forensics_from_pack_path   (existing core.forensics.pipeline)
      │
      ▼
ForensicRunPacket.v0
      │
      ▼
build_aal_viz_forensic_projection(run)   (NEW pure builder)
      │
      ▼
AALVizForensicProjection.v0
      │
      ├── stdout / CLI summary
      └── optional --out → write_canonical_artifact (AUDIT_EVIDENCE)
          preferred path: out/projections/aal_viz_forensic.v0.latest.json
```

**Compose only.** Projection builder does not re-implement disposition/graph/gate logic. It **echoes** sealed fields and summarizes graph metrics for visualization consumers.

**Authority model:** Projection inherits and re-asserts forensics authority locks; adds AAL-Viz governance flags (`projection_only`, `render_consumer_only`, `non_authoritative`) aligned with `core/aal_viz_operator_climate_overlay.py` patterns without requiring the full climate flag set if redundant.

---

## 3. Packet: `AALVizForensicProjection.v0`

### 3.1 Required fields

| Field | Type / constraint | Notes |
|-------|-------------------|--------|
| `schema_version` | const `AALVizForensicProjection.v0` | |
| `projection_id` | string | Deterministic id, e.g. `aal_viz_forensic:` + first 16 of `source_run_hash` |
| `source_run_hash` | 64-hex or empty | From run `canonical_hash` |
| `pack_id` | string or null | From run |
| `pack_path` | string | Echo run (path-scoped; document that hash of projection includes path if present) |
| `disposition` | `READY` \| `HOLD` \| `NOT_COMPUTABLE` \| `""` | From run.disposition.disposition |
| `ops_gate_status` | const `DENIED` | **Must always be DENIED** even if source is malformed |
| `simulation` | `WOULD_ALLOW` \| `WOULD_DENY` | From ops_gate |
| `ops_gate_hint` | string | From disposition |
| `blocked_by` | string[] | From disposition (default `[]`) |
| `register_counts` | object | From disposition when present; else empty counts |
| `graph_summary` | object | See §3.2 |
| `bridge_status` | string | From run |
| `projection_only` | const `true` | |
| `advisory_only` | const `true` | |
| `render_consumer_only` | const `true` | |
| `non_authoritative` | const `true` | |
| `lane` | const `SHADOW` | |
| `authority` | object | All false — same keys as forensics `DEFAULT_AUTHORITY` |
| `canonical_hash` | 64-hex | Body without this field, then attach |

### 3.2 `graph_summary`

| Field | Constraint |
|-------|------------|
| `node_count` | int ≥ 0 |
| `edge_count` | int ≥ 0 |
| `write_performed` | const `false` |
| `network_calls` | const `false` |
| `schema_version` | optional echo of PropagationGraph.v0 |

Counts derived from `run["propagation"]` nodes/edges lists (len). Do not embed full node/edge arrays in v0 (keep projection small). Full graph remains on the ForensicRunPacket / optional `--out` of `forensics run`.

### 3.3 Builder signature

```python
def build_aal_viz_forensic_projection(
    run: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Pure. Fail-closed: missing/invalid run → empty disposition, DENIED gate, zero graph."""
```

Optional convenience (same module or pipeline):

```python
def build_aal_viz_forensic_projection_from_pack_path(
    path: str | Path,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    run = run_forensics_from_pack_path(path, repo_root=repo_root)
    return build_aal_viz_forensic_projection(run)
```

### 3.4 Fail-closed rules

| Input | Behavior |
|-------|----------|
| `run is None` / non-mapping | Empty disposition `""`, DENIED, zero graph, empty pack_id |
| Missing nested disposition/ops_gate | Treat as empty / DENIED |
| Nested gate claims non-DENIED | **Force** `ops_gate_status: DENIED` (projection never amplifies a leak) |
| Non-dict pack already rejected by pipeline | Path helper raises; CLI maps to exit 1 |

---

## 4. Schema + files

| Path | Responsibility |
|------|----------------|
| `contracts/forensics/aal_viz_forensic_projection.v0.schema.json` | Draft7 schema |
| `core/forensics/aal_viz_projection.py` | Pure builders |
| `core/forensics/__init__.py` | Export builders |
| `contracts/forensics/README.md` | Table row + CLI line |
| `tests/test_forensics_aal_viz_projection.py` | Schema + fixture READY+DENIED + determinism + fail-closed |
| `abraxas/cli.py` | `os forensics project --pack PATH [--out PATH]` |
| `tests/test_forensics_cli.py` | Smoke project subcommand |
| `STATUS.md` | Optional one-line pointer after merge (C6 MERGED) |
| Mission doc | Optional checkmark C6 done (post-merge polish OK) |

**Not in scope:** `apps/aal-viz-live-console/public/*` copy; new renderer scripts under `scripts/viz/` (CLI is enough for v0).

---

## 5. CLI

```text
python -m abraxas os forensics project --pack PATH [--out PATH]
```

- Composes path → pipeline → projection.
- Prints **summary** JSON (not necessarily full nested graph): at minimum `ok`, `schema_version`, `disposition`, `ops_gate_status`, `simulation`, `projection_only`, `advisory_only`, `pack_id`, `node_count`/`edge_count` (or nested `graph_summary`), `canonical_hash`, `wrote`.
- Exit codes mirror `forensics run`: **0** READY, **2** HOLD|NOT_COMPUTABLE, **1** hard failure.
- `--out`: optional `write_canonical_artifact` with `ArtifactClass.AUDIT_EVIDENCE` (same pattern as other `os` dry-runs). Default out path when writing is caller-supplied; docs recommend `out/projections/aal_viz_forensic.v0.latest.json`.
- `ops_gate_status` in CLI summary is always `DENIED`.

Kernel status (optional light touch, not blocking):

- Add surface `forensics_aal_viz_projection` → path exists for `core/forensics/aal_viz_projection.py`.
- Add command `forensics_project`: `python -m abraxas os forensics project --pack PATH`.

---

## 6. Testing

| Test | Assert |
|------|--------|
| Fixture golden | projection disposition READY, ops_gate_status DENIED, simulation WOULD_ALLOW, projection_only true, write_performed/network_calls false |
| Schema | Draft7Validator against schema |
| Determinism | two builds equal including canonical_hash |
| Fail-closed | `build_aal_viz_forensic_projection(None)` → DENIED, empty/zero graph |
| Force DENIED | crafted run with ops_gate.gate_status ALLOW-like still projects DENIED |
| CLI | `main(["os","forensics","project","--pack", fixture])` → exit 0, DENIED, READY |

Use hermes fixture:  
`skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json`

---

## 7. PR order (implementation)

| Step | Deliverable |
|------|-------------|
| **C6.1** | Schema + pure builder + unit tests |
| **C6.2** | CLI `project` + CLI tests |
| **C6.3** | README + kernel surface/command (optional same PR) + STATUS seal |

Prefer **one PR** if still small; split only if review load requires it.

Conventional commits: `feat(shadow):` for code, `docs:` for docs-only, `test:` if pure test.

---

## 8. Risks

| Risk | Mitigation |
|------|------------|
| Projection becomes second source of disposition truth | Builder only echoes run; no recompute |
| Path in hash breaks content equality | Document path-scoped envelope; tests use fixed fixture path via REPO |
| Ops leak via simulation language | Gate status const DENIED; simulation is advisory only |
| Scope creep into console | Explicit non-goal |

---

## 9. Approval record

| Section | Status |
|---------|--------|
| Approach A (thin ForensicRun → projection) | Operator chose **1** |
| Live-console copy | Deferred |
| Written design | Pending operator file review |

---

## Seal

Design surface only. Does not grant authority, open OpsGate, mutate canon/runtime, enable writeback, or authorize production. Implementation remains SHADOW / advisory / projection-only unless a separate operator attestation says otherwise.
