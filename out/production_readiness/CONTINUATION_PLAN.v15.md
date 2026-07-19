# Abraxas Production Continuation Plan v15

```yaml
program_id: ABRAXAS_PRODUCTION_CONTINUATION
plan_id: CONTINUATION_PLAN.v15
supersedes: CONTINUATION_PLAN.v14
status: ACTIVE
drafted_at: 2026-07-19
branch: main
scripts_organization: COMPLETE
scripts_continuation: PATH_HYGIENE_AND_DX
unauthorized_sole_writer_findings: 0
production_activation_authorized: false
deploy_readiness: NO_GO
activation_gate: DENIED
```

**Scripts organization remains complete.** This plan covers **post-org maintenance** (path awareness, inventory, DX)—not another mass move. Activation remains **DENIED**. Deploy remains **NO_GO**.

---

## 1. What this continuation delivers

| Track | Content |
|-------|---------|
| Runtime inventory | Surface patterns match `scripts/<domain>/run_*` as well as legacy root prefixes |
| Baseline / writer inventory | Count and authorize nested domain runners |
| Artifact registry scanner | Skip `preflight/` (non-run packages) when iterating runners |
| Root tooling | Optional helpers under `scripts/tools/` |
| DX | `AGENTS.md`, `CONTRIBUTING.md`, `scripts/README.md`, `QUICKSTART.md` align with domain layout |
| Policy copy | Sole-writer / writer-debt text acknowledges nested `run_*` |

---

## 2. Scripts layout (frozen)

- **709+** domain `run_*.py` under `scripts/<domain>/`
- **Root `run_*`:** only `scripts/run_fast_ci.py`
- **Do not** add `scripts/operator/__init__.py`
- **Do not** bulk-rewrite sealed `v2_hygiene_*` receipts for path strings
- **Status:** `python scripts/organize_scripts.py status` → `complete: true`

---

## 3. Binding authority (unchanged)

| Gate | Status |
|------|--------|
| Activation | **DENIED** |
| Deploy | **NO_GO** |
| Sole-writer | **0** unauthorized |

---

## 4. Remaining scripts backlog (optional)

| Priority | Item | Notes |
|----------|------|--------|
| P2 | Ghost plan paths in core (references to never-landed `scripts/run_*.py`) | Leave or mark advisory; do not invent files |
| P2 | Move `abx_loop*` into `scripts/codegen/` or `scripts/loop/` | Optional; document if kept at root |
| P3 | Operator Notion note: org complete; deploy still held | Ops |
| Hold | Fail-closed sole-writer / deploy / activation | Operator mandate only |

---

## 5. Non-goals

- Wave-4 domain renames  
- Fail-closed CI sole-writer without approval  
- Silent deploy unhold  

---

## 6. Plan control

| Field | Value |
|-------|--------|
| Supersedes | CONTINUATION_PLAN.v14 |
| Scripts org | **COMPLETE** (maintenance mode) |
| Production activation | **Not authorized** |
