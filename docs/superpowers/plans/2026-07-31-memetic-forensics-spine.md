# Memetic Forensics Spine (Slice C) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a deterministic SHADOW forensics path from EvidencePack → ForensicDispositionPacket.v0 with PropagationGraph dry-run and MemeticOpsGate always DENIED (forensics engine first; ops stubbed).

**Architecture:** Compose existing forage → ingest → spine → oracle/belief bridge, then add thin pure builders for propagation dry-run, disposition, and ops gate. CLI `abraxas os forensics run|status`. No live publish, queue write, brier write, or EXTERNAL_PRODUCTION.

**Tech Stack:** Python 3, `core.canonical.json.canonical_hash`, jsonschema Draft7 tests, pytest, existing `abraxas.cli` argparse, fixture at `skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json`.

**Spec:** `docs/superpowers/specs/2026-07-31-memetic-forensics-dual-function-design.md`

## Global Constraints

- `lane: SHADOW` · `advisory_only: true` on all new packets
- Authority fields false: `execution_authority`, `forecast_weight_allowed` / `forecast_routing_authorized`, `canon_mutation_allowed`, `publish_authorized`, `queue_write_authorized`
- OpsGate `gate_status` must be `DENIED` for every slice-C path (even when disposition is `READY`)
- Propagation dry-run required before `READY` (no silent skip)
- No network at import; no writes to `out/operator_review_queue`, `out/brier`, durable memory, or social APIs
- Deterministic: same inputs → same `canonical_hash`
- Conventional commits: `feat(shadow):` / `docs:` / `test:` as appropriate
- Use project venv: `.venv/bin/python -m pytest …`

## File map

| Path | Responsibility |
|------|----------------|
| `docs/architecture/MEMETIC_FORENSICS_MISSION_001.md` | Mission map + taxonomy pointer |
| `STATUS.md` | Primary eng objective → forensics spine |
| `docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md` | Link dual-function mission (minimal) |
| `contracts/forensics/forensic_disposition.v0.schema.json` | Disposition schema |
| `contracts/forensics/propagation_graph.v0.schema.json` | Propagation dry-run schema |
| `contracts/forensics/memetic_ops_gate.v0.schema.json` | Ops gate schema |
| `core/forensics/__init__.py` | Package exports |
| `core/forensics/propagation_graph.py` | Build PropagationGraph.v0 from pack |
| `core/forensics/disposition.py` | Build ForensicDispositionPacket.v0 |
| `core/forensics/ops_gate.py` | Build MemeticOpsGate.v0 |
| `core/forensics/pipeline.py` | Orchestrate pack path → full forensic run |
| `core/signal/spine_bridge.py` | Optional: expose forensics in kernel status surfaces |
| `abraxas/cli.py` | `os forensics run` / `os forensics status` |
| `tests/test_forensics_propagation_graph.py` | Propagation tests |
| `tests/test_forensics_disposition.py` | Disposition tests |
| `tests/test_forensics_ops_gate.py` | Gate DENIED invariant |
| `tests/test_forensics_pipeline.py` | E2E fixture path |
| `tests/test_forensics_cli.py` | CLI smoke |

---

### Task 1: Mission map docs (C0)

**Files:**
- Create: `docs/architecture/MEMETIC_FORENSICS_MISSION_001.md`
- Modify: `STATUS.md` (Current-state block Active objective + AI OS rows only as needed)
- Modify: `docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md` (short pointer near top or §8)

**Interfaces:**
- Consumes: approved design decisions
- Produces: contributor-facing mission language (no runtime API)

- [ ] **Step 1: Write mission doc**

Create `docs/architecture/MEMETIC_FORENSICS_MISSION_001.md` with:

- Dual mission (forensics + ops)
- Forensics-gated ops rule
- Slice C scope / non-goals
- Table: FORENSIC_CORE / OPS_STUB / INFRA / PARK (copy from design §5)
- Link to design spec path above
- Seal: advisory; no authority grant

- [ ] **Step 2: Update STATUS.md Active objective row**

In the Current-state block, set Active objective to:

```markdown
| Active objective | **Memetic Forensics Spine (slice C)** · ops held behind forensics gate · CLEAR dual-control remains operator-only | [`docs/architecture/MEMETIC_FORENSICS_MISSION_001.md`](docs/architecture/MEMETIC_FORENSICS_MISSION_001.md) · design `docs/superpowers/specs/2026-07-31-memetic-forensics-dual-function-design.md` |
```

Update Last Updated line to mention forensics mission (keep date accurate).

- [ ] **Step 3: Point unification plan at mission**

In `docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md` after the AI OS framing paragraph, add 3–5 lines:

```markdown
**Product function (2026-07-31):** Abraxas is a forensics-gated memetic dual-function OS.
Slice C builds the forensics engine first. See
[`MEMETIC_FORENSICS_MISSION_001.md`](../architecture/MEMETIC_FORENSICS_MISSION_001.md)
and design spec `docs/superpowers/specs/2026-07-31-memetic-forensics-dual-function-design.md`.
```

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/MEMETIC_FORENSICS_MISSION_001.md STATUS.md docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md
git commit -m "docs: memetic forensics dual-function mission map (slice C)"
```

---

### Task 2: PropagationGraph.v0 dry-run (C2)

**Files:**
- Create: `contracts/forensics/propagation_graph.v0.schema.json`
- Create: `core/forensics/__init__.py`
- Create: `core/forensics/propagation_graph.py`
- Test: `tests/test_forensics_propagation_graph.py`

**Interfaces:**
- Consumes: EvidencePack-like `dict` with `sources[]` and `claims[]` (or empty)
- Produces:
  - `build_propagation_graph_from_pack(pack: Mapping[str, Any] | None) -> dict[str, Any]`
  - Schema version const `PropagationGraph.v0`
  - Fields: `nodes`, `edges`, `write_performed: false`, `network_calls: false`, `canonical_hash`, `authority` all false

- [ ] **Step 1: Write failing tests**

```python
# tests/test_forensics_propagation_graph.py
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft7Validator
from core.forensics.propagation_graph import build_propagation_graph_from_pack

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json"
SCHEMA = REPO / "contracts/forensics/propagation_graph.v0.schema.json"

def test_graph_from_fixture_deterministic():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    a = build_propagation_graph_from_pack(pack)
    b = build_propagation_graph_from_pack(pack)
    assert a == b
    assert a["schema_version"] == "PropagationGraph.v0"
    assert a["write_performed"] is False
    assert a["network_calls"] is False
    assert len(a["nodes"]) >= 1
    assert a["authority"]["execution_authority"] is False
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(a)

def test_graph_none_pack():
    g = build_propagation_graph_from_pack(None)
    assert g["schema_version"] == "PropagationGraph.v0"
    assert g["nodes"] == []
    assert g["edges"] == []
```

- [ ] **Step 2: Run tests — expect FAIL (import/module missing)**

```bash
.venv/bin/python -m pytest tests/test_forensics_propagation_graph.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Schema**

Create `contracts/forensics/propagation_graph.v0.schema.json` with required:
`schema_version` const `PropagationGraph.v0`, `write_performed` const false, `network_calls` const false, `nodes` array, `edges` array, `advisory_only` const true, `lane` const `SHADOW`, `authority` object with false flags, `canonical_hash` 64 hex.

- [ ] **Step 4: Implementation**

`core/forensics/propagation_graph.py`:

```python
"""PropagationGraph.v0 dry-run from EvidencePack sources/claims. No network."""

from __future__ import annotations
from typing import Any, Mapping
from core.canonical.json import canonical_hash

SCHEMA_VERSION = "PropagationGraph.v0"
DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "publish_authorized": False,
}

def build_propagation_graph_from_pack(pack: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(pack, Mapping):
        body = {
            "schema_version": SCHEMA_VERSION,
            "pack_id": "",
            "nodes": [],
            "edges": [],
            "node_count": 0,
            "edge_count": 0,
            "write_performed": False,
            "network_calls": False,
            "authority": dict(DEFAULT_AUTHORITY),
            "advisory_only": True,
            "lane": "SHADOW",
        }
        body["canonical_hash"] = canonical_hash(body)
        return body

    pack_id = str(pack.get("pack_id") or "")
    sources = pack.get("sources") if isinstance(pack.get("sources"), list) else []
    claims = pack.get("claims") if isinstance(pack.get("claims"), list) else []
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    source_ids: list[str] = []

    for src in sources:
        if not isinstance(src, dict):
            continue
        sid = str(src.get("source_id") or "")
        if not sid:
            continue
        source_ids.append(sid)
        nodes.append({
            "node_id": f"src:{sid}",
            "kind": "source",
            "register": "OBSERVED",
            "label": str(src.get("title") or sid)[:200],
        })

    for claim in claims:
        if not isinstance(claim, dict):
            continue
        cid = str(claim.get("claim_id") or claim.get("id") or "")
        if not cid:
            continue
        reg = str(claim.get("register") or "NOT_COMPUTABLE")
        nodes.append({
            "node_id": f"meme:{cid}",
            "kind": "meme_unit",
            "register": reg,
            "label": str(claim.get("text") or claim.get("claim_text") or cid)[:200],
        })
        kind = (
            "observed_cite"
            if reg == "OBSERVED"
            else "inferred_echo"
            if reg == "INFERRED"
            else "speculative_spread"
        )
        refs = claim.get("source_ids") or claim.get("sources") or []
        if isinstance(refs, list) and refs:
            for ref in refs[:8]:
                edges.append({
                    "from_id": f"src:{ref}",
                    "to_id": f"meme:{cid}",
                    "kind": kind,
                })
        elif source_ids:
            edges.append({
                "from_id": f"src:{source_ids[0]}",
                "to_id": f"meme:{cid}",
                "kind": kind,
            })

    fixed_edges = []
    for i, e in enumerate(sorted(edges, key=lambda x: (x["from_id"], x["to_id"], x["kind"]))):
        fixed = dict(e)
        fixed["edge_id"] = f"e:{fixed['from_id']}:{fixed['to_id']}:{fixed['kind']}:{i}"
        fixed_edges.append(fixed)

    nodes_sorted = sorted(nodes, key=lambda n: n["node_id"])
    edges_sorted = sorted(fixed_edges, key=lambda e: e["edge_id"])
    body = {
        "schema_version": SCHEMA_VERSION,
        "pack_id": pack_id,
        "nodes": nodes_sorted,
        "edges": edges_sorted,
        "node_count": len(nodes_sorted),
        "edge_count": len(edges_sorted),
        "write_performed": False,
        "network_calls": False,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "SHADOW",
    }
    body["canonical_hash"] = canonical_hash(body)
    return body
```

Clean up the `if False` stub when implementing — use only the fixed_edges path.

`core/forensics/__init__.py`:

```python
from core.forensics.propagation_graph import build_propagation_graph_from_pack
__all__ = ["build_propagation_graph_from_pack"]
```

- [ ] **Step 5: Run tests — expect PASS**

```bash
.venv/bin/python -m pytest tests/test_forensics_propagation_graph.py -v
```

- [ ] **Step 6: Commit**

```bash
git add contracts/forensics/propagation_graph.v0.schema.json core/forensics/ tests/test_forensics_propagation_graph.py
git commit -m "feat(shadow): PropagationGraph.v0 dry-run from EvidencePack"
```

---

### Task 3: ForensicDispositionPacket.v0 (C1)

**Files:**
- Create: `contracts/forensics/forensic_disposition.v0.schema.json`
- Create: `core/forensics/disposition.py`
- Modify: `core/forensics/__init__.py`
- Test: `tests/test_forensics_disposition.py`

**Interfaces:**
- Consumes:
  - `pack: Mapping | None`
  - `propagation: Mapping | None` (from Task 2)
  - optional `bridge_status: str`, `register_counts: Mapping[str, int]`
- Produces:
  - `build_forensic_disposition(*, pack, propagation, bridge_status="", receipt_status="", extra_blocked_by=None) -> dict`
  - `disposition` in `READY` | `HOLD` | `NOT_COMPUTABLE`
  - `ops_gate_hint` always not auto-open

- [ ] **Step 1: Write failing tests**

```python
# tests/test_forensics_disposition.py
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft7Validator
from core.forensics.propagation_graph import build_propagation_graph_from_pack
from core.forensics.disposition import build_forensic_disposition

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json"
SCHEMA = REPO / "contracts/forensics/forensic_disposition.v0.schema.json"

def test_none_pack_not_computable():
    d = build_forensic_disposition(pack=None, propagation=None)
    assert d["disposition"] == "NOT_COMPUTABLE"
    assert d["ops_gate_hint"] == "DENIED"
    assert d["authority"]["publish_authorized"] is False

def test_fixture_with_propagation_ready_or_hold():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    prop = build_propagation_graph_from_pack(pack)
    d = build_forensic_disposition(pack=pack, propagation=prop, bridge_status="BRIDGED_SHADOW")
    assert d["schema_version"] == "ForensicDispositionPacket.v0"
    assert d["disposition"] in {"READY", "HOLD"}
    assert d["ops_gate_hint"] in {"DENIED", "WOULD_ALLOW_IF_OPERATOR"}
    if d["disposition"] == "READY":
        assert d["ops_gate_hint"] == "WOULD_ALLOW_IF_OPERATOR"
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(d)

def test_missing_propagation_holds():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    d = build_forensic_disposition(pack=pack, propagation=None)
    assert d["disposition"] == "HOLD"
    assert "PROPAGATION_REQUIRED" in d["blocked_by"]

def test_authority_leak_holds():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    prop = build_propagation_graph_from_pack(pack)
    d = build_forensic_disposition(
        pack=pack,
        propagation=prop,
        extra_authority_violations=["authority.execution_authority"],
    )
    assert d["disposition"] == "HOLD"
    assert d["authority_violations"]
```

- [ ] **Step 2: Run — expect FAIL**

```bash
.venv/bin/python -m pytest tests/test_forensics_disposition.py -v
```

- [ ] **Step 3: Schema + implementation**

Rules in `build_forensic_disposition`:

1. If pack is None or invalid (no pack_id and no sources/claims): `NOT_COMPUTABLE`, blocked_by includes `NO_PACK`
2. If `propagation is None` or `propagation.get("node_count", 0) == 0` and pack has claims/sources: `HOLD`, `PROPAGATION_REQUIRED` (if pack has no sources and no claims, NOT_COMPUTABLE already)
3. If `extra_authority_violations` non-empty: `HOLD`
4. Else if pack has at least one claim or source and propagation has nodes: `READY`, `ops_gate_hint=WOULD_ALLOW_IF_OPERATOR`
5. Always set authority all false; never set publish true

Include `register_counts` from pack if present, else count claim registers.

- [ ] **Step 4: Tests PASS + commit**

```bash
.venv/bin/python -m pytest tests/test_forensics_disposition.py tests/test_forensics_propagation_graph.py -v
git add contracts/forensics/forensic_disposition.v0.schema.json core/forensics/disposition.py core/forensics/__init__.py tests/test_forensics_disposition.py
git commit -m "feat(shadow): ForensicDispositionPacket.v0 from pack + propagation"
```

---

### Task 4: MemeticOpsGate.v0 always DENIED (C4)

**Files:**
- Create: `contracts/forensics/memetic_ops_gate.v0.schema.json`
- Create: `core/forensics/ops_gate.py`
- Modify: `core/forensics/__init__.py`
- Test: `tests/test_forensics_ops_gate.py`

**Interfaces:**
- Consumes: disposition dict from Task 3
- Produces: `build_memetic_ops_gate(disposition: Mapping[str, Any] | None) -> dict`
  - `gate_status` always `"DENIED"`
  - `simulation` is `"WOULD_ALLOW"` only if disposition is READY; else `"WOULD_DENY"`
  - `execution_authorized: false`, `publish_authorized: false`

- [ ] **Step 1: Failing tests**

```python
from core.forensics.ops_gate import build_memetic_ops_gate

def test_ready_still_denied():
    gate = build_memetic_ops_gate({
        "disposition": "READY",
        "canonical_hash": "a" * 64,
        "ops_gate_hint": "WOULD_ALLOW_IF_OPERATOR",
    })
    assert gate["schema_version"] == "MemeticOpsGate.v0"
    assert gate["gate_status"] == "DENIED"
    assert gate["simulation"] == "WOULD_ALLOW"
    assert gate["publish_authorized"] is False
    assert gate["execution_authorized"] is False

def test_hold_denied():
    gate = build_memetic_ops_gate({"disposition": "HOLD", "canonical_hash": "b" * 64})
    assert gate["gate_status"] == "DENIED"
    assert gate["simulation"] == "WOULD_DENY"
```

- [ ] **Step 2: Implement minimal builder + schema + PASS + commit**

```bash
git commit -m "feat(shadow): MemeticOpsGate.v0 always DENIED in slice C"
```

---

### Task 5: Forensic pipeline orchestrator (C3 + C5 core)

**Files:**
- Create: `core/forensics/pipeline.py`
- Test: `tests/test_forensics_pipeline.py`
- Modify: `core/forensics/__init__.py`

**Interfaces:**
- Consumes: pack path `str | Path`, optional `repo_root`
- Produces:
  - `run_forensics_from_pack_path(path, *, repo_root=None) -> dict` with keys:
    - `schema_version`: `ForensicRunPacket.v0`
    - `pack_path`, `pack_hash` (if available)
    - `propagation`, `disposition`, `ops_gate`
    - `ok`: True if disposition in READY|HOLD|NOT_COMPUTABLE and ops_gate DENIED
    - `authority` all false
    - `canonical_hash`

Use existing loaders:

```python
from core.signal.evidence_pack import validate_path  # or load pack JSON
from core.ingest.familiar_ingestion_receipt import build_familiar_ingestion_receipt_from_path
from core.signal.familiar_oracle_belief_bridge import build_bridge_from_pack_path
```

If `validate_path` / load helpers differ, load JSON via `json.loads(Path.read_text)` after existing validate if available.

- [ ] **Step 1: Failing E2E test**

```python
def test_pipeline_fixture_ops_gate_denied():
    from core.forensics.pipeline import run_forensics_from_pack_path
    run = run_forensics_from_pack_path(FIXTURE, repo_root=REPO)
    assert run["schema_version"] == "ForensicRunPacket.v0"
    assert run["ops_gate"]["gate_status"] == "DENIED"
    assert run["disposition"]["disposition"] in {"READY", "HOLD", "NOT_COMPUTABLE"}
    assert run["propagation"]["write_performed"] is False
    a = run_forensics_from_pack_path(FIXTURE, repo_root=REPO)
    assert a == run_forensics_from_pack_path(FIXTURE, repo_root=REPO)
```

- [ ] **Step 2: Implement pipeline**

```python
def run_forensics_from_pack_path(path, *, repo_root=None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root else Path.cwd()
    p = Path(path)
    pack = json.loads(p.read_text(encoding="utf-8"))
    # optional: build_bridge_from_pack_path for bridge_status
    bridge = build_bridge_from_pack_path(p, repo_root=root)
    prop = build_propagation_graph_from_pack(pack)
    disp = build_forensic_disposition(
        pack=pack,
        propagation=prop,
        bridge_status=str(bridge.get("status") or ""),
    )
    gate = build_memetic_ops_gate(disp)
    body = {
        "schema_version": "ForensicRunPacket.v0",
        "pack_path": str(p),
        "pack_id": pack.get("pack_id"),
        "bridge_status": bridge.get("status"),
        "propagation": prop,
        "disposition": disp,
        "ops_gate": gate,
        "advisory_only": True,
        "lane": "SHADOW",
        "authority": { ... all False ... },
    }
    body["canonical_hash"] = canonical_hash(body)
    return body
```

- [ ] **Step 3: PASS + commit**

```bash
git commit -m "feat(shadow): forensic pipeline pack → disposition + denied ops gate"
```

---

### Task 6: CLI `os forensics` (C5)

**Files:**
- Modify: `abraxas/cli.py`
- Test: `tests/test_forensics_cli.py`

**Interfaces:**
- `python -m abraxas os forensics run --pack PATH [--out PATH]`
- `python -m abraxas os forensics status` → prints last run if `--state` file exists, else `{ok:false, reason: NO_PRIOR_RUN}` without requiring disk for default status

For status v0: status can re-run nothing and report:

```python
{"ok": False, "reason": "NO_PRIOR_RUN", "hint": "os forensics run --pack PATH", "advisory_only": True}
```

Or if `--out` was written, status is optional. Prefer simple: `status` returns kernel-aligned forensics posture:

```python
{
  "ok": True,
  "forensics_engine": "SLICE_C",
  "ops_gate_default": "DENIED",
  "commands": {"run": "python -m abraxas os forensics run --pack PATH"},
  "advisory_only": True,
}
```

- [ ] **Step 1: CLI test**

```python
from abraxas.cli import main
import json

def test_cli_forensics_run(capsys):
    code = main(["os", "forensics", "run", "--pack", str(FIXTURE)])
    assert code in {0, 1, 2}
    payload = json.loads(capsys.readouterr().out)
    assert payload["ops_gate_status"] == "DENIED"
    assert payload["advisory_only"] is True

def test_cli_forensics_status(capsys):
    code = main(["os", "forensics", "status"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ops_gate_default"] == "DENIED"
```

Exit codes for `run`:
- 0 if disposition READY
- 2 if HOLD or NOT_COMPUTABLE
- 1 if hard failure

- [ ] **Step 2: Wire argparse**

Under `os_sub`, add nested subparser:

```python
forensics = os_sub.add_parser("forensics", help="Memetic forensics spine (SHADOW)")
forensics_sub = forensics.add_subparsers(dest="forensics_command", required=True)
f_run = forensics_sub.add_parser("run", ...)
f_run.add_argument("--pack", type=Path, required=True)
f_run.add_argument("--out", type=Path, default=None)
f_run.set_defaults(func=_cmd_os_forensics_run)
f_status = forensics_sub.add_parser("status", ...)
f_status.set_defaults(func=_cmd_os_forensics_status)
```

- [ ] **Step 3: PASS + commit**

```bash
git commit -m "feat(shadow): CLI os forensics run|status"
```

---

### Task 7: Kernel status surface + taxonomy note (C7 light)

**Files:**
- Modify: `core/signal/spine_bridge.py` (`build_ai_os_kernel_status`)
- Modify: `docs/architecture/MEMETIC_FORENSICS_MISSION_001.md` if needed (already Task 1)
- Test: extend existing `tests/test_ai_os_slice_c.py` or add assert in `tests/test_forensics_cli.py`

**Interfaces:**
- Add to kernel status `surfaces`:
  - `forensics_core`: path exists for `core/forensics/pipeline.py`
- Add to `commands`:
  - `forensics_run`: `python -m abraxas os forensics run --pack PATH`
- Add to `syscall` path string: append `→ forensics disposition (ops gate DENIED)`

- [ ] **Step 1: Test kernel status includes forensics command**

```python
from core.signal.spine_bridge import build_ai_os_kernel_status
def test_kernel_lists_forensics():
    s = build_ai_os_kernel_status(REPO)
    assert s["surfaces"].get("forensics_core") is True
    assert "forensics" in s["commands"]["forensics_run"]
```

- [ ] **Step 2: Implement + PASS + commit**

```bash
git commit -m "feat(shadow): expose forensics spine on os status"
```

---

### Task 8: Full regression + docs seal

**Files:** none new required; optional touch `contracts/signal/README.md` or `contracts/forensics/README.md` listing schemas

- [ ] **Step 1: Run full forensics test suite**

```bash
.venv/bin/python -m pytest tests/test_forensics_*.py -v
.venv/bin/python -m abraxas os forensics run --pack skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json
.venv/bin/python -m abraxas os forensics status
```

- [ ] **Step 2: Add `contracts/forensics/README.md`**

Table of the three schemas + ForensicRunPacket (inline in pipeline, document fields).

- [ ] **Step 3: Final commit**

```bash
git commit -m "docs: forensics contracts README + slice C seal notes"
```

---

## Spec coverage checklist

| Spec requirement | Task |
|------------------|------|
| Mission / taxonomy docs | Task 1 |
| PropagationGraph.v0 dry-run | Task 2 |
| ForensicDispositionPacket.v0 | Task 3 |
| Propagation required for READY | Task 3 |
| MemeticOpsGate always DENIED | Task 4 |
| Compose pack path pipeline | Task 5 |
| CLI forensics run/status | Task 6 |
| os status surfaces | Task 7 |
| No live publish / queue / brier | Global constraints + tests |
| Optional AAL-Viz (C6) | **Deferred** — not required for slice C success; open follow-up if needed |

## Deferred (not in this plan)

- C6 AAL-Viz forensic projection (optional)
- Real ops opening (Level 99 / Neon) under dual-control
- Full pipeline v1.1 for all PARK products
- Networked social crawl for propagation

## Placeholder / consistency review

- Function names: `build_propagation_graph_from_pack`, `build_forensic_disposition`, `build_memetic_ops_gate`, `run_forensics_from_pack_path` — use consistently
- Schema versions: `PropagationGraph.v0`, `ForensicDispositionPacket.v0`, `MemeticOpsGate.v0`, `ForensicRunPacket.v0`
- No TBD/TODO steps remain after cleanup of edge_id stub note in Task 2 sample code (implementer must emit deterministic edge_ids only)
