# C6 AAL-Viz Forensic Projection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `AALVizForensicProjection.v0` — thin SHADOW projection from ForensicRunPacket with OpsGate always DENIED.

**Architecture:** Pure builder echoes sealed forensics run fields + graph_summary counts; CLI `os forensics project` composes pack path → pipeline → projection; optional AUDIT_EVIDENCE write.

**Tech Stack:** Python 3, `core.canonical.json.canonical_hash`, jsonschema Draft7, pytest, `abraxas.cli`, hermes EvidencePack fixture.

**Spec:** `docs/superpowers/specs/2026-07-31-c6-aal-viz-forensic-projection-design.md`

## Global Constraints

- `lane: SHADOW` · `advisory_only: true` · `projection_only: true`
- `ops_gate_status` always `DENIED` (force even if source gate is wrong)
- Authority all false (forensics DEFAULT_AUTHORITY keys)
- No network; no queue/Brier/social/live-console writes
- Deterministic: same inputs → same `canonical_hash`
- Conventional commits: `feat(shadow):` / `docs:` / `test:`
- Venv: `.venv/bin/python -m pytest …`
- Fixture: `skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json`

## File map

| Path | Responsibility |
|------|----------------|
| `contracts/forensics/aal_viz_forensic_projection.v0.schema.json` | Draft7 schema |
| `core/forensics/aal_viz_projection.py` | Pure builders |
| `core/forensics/__init__.py` | Exports |
| `tests/test_forensics_aal_viz_projection.py` | Unit + schema tests |
| `abraxas/cli.py` | `os forensics project` |
| `tests/test_forensics_cli.py` | CLI smoke |
| `core/signal/spine_bridge.py` | Optional surface + command |
| `contracts/forensics/README.md` | Document schema |
| `STATUS.md` | C6 pointer after land |

---

### Task 1: Schema + pure builder + tests

**Files:**
- Create: `contracts/forensics/aal_viz_forensic_projection.v0.schema.json`
- Create: `core/forensics/aal_viz_projection.py`
- Modify: `core/forensics/__init__.py`
- Test: `tests/test_forensics_aal_viz_projection.py`

**Interfaces:**
- `build_aal_viz_forensic_projection(run: Mapping | None) -> dict`
- `build_aal_viz_forensic_projection_from_pack_path(path, *, repo_root=None) -> dict`

- [ ] **Step 1: Failing tests** then implement schema + builder (TDD)
- [ ] **Step 2:** Fixture READY + DENIED; fail-closed None; force DENIED; determinism; schema validate
- [ ] **Step 3:** Commit `feat(shadow): AALVizForensicProjection.v0 from ForensicRunPacket`

---

### Task 2: CLI `os forensics project`

**Files:**
- Modify: `abraxas/cli.py`
- Modify: `tests/test_forensics_cli.py`

**Interfaces:**
- `python -m abraxas os forensics project --pack PATH [--out PATH]`
- Exit: 0 READY, 2 HOLD|NOT_COMPUTABLE, 1 hard fail
- Summary includes ops_gate_status DENIED, projection_only true

- [ ] **Step 1:** CLI tests then wire argparse + handler (mirror forensics run)
- [ ] **Step 2:** Commit `feat(shadow): CLI os forensics project`

---

### Task 3: Kernel surface + docs seal

**Files:**
- Modify: `core/signal/spine_bridge.py`
- Modify: `tests/test_ai_os_slice_c.py`
- Modify: `contracts/forensics/README.md`
- Modify: `STATUS.md` (Active objective mention C6)

- [ ] **Step 1:** `forensics_aal_viz_projection` surface + `forensics_project` command
- [ ] **Step 2:** README + STATUS
- [ ] **Step 3:** Full regression + commit `docs: C6 AAL-Viz forensic projection seal`

---

## Spec coverage

| Spec item | Task |
|-----------|------|
| Packet fields + graph_summary | 1 |
| Force DENIED | 1 |
| Path helper | 1 |
| CLI project | 2 |
| Kernel optional | 3 |
| README / STATUS | 3 |
| No live-console | Global (omit) |
