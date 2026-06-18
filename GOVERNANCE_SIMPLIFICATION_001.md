# GOVERNANCE_SIMPLIFICATION_001 — Migration Receipt

## Scope

`GOVERNANCE_SIMPLIFICATION_001` documents the transition from procedural governance (FROZEN / ADVISORY_ONLY pre-implementation gates) to **Governance V3** (implementation-first development).

This receipt is a documentation migration record. It does **not**:

- delete historical artifacts under `out/`
- rewrite repository history
- remove testing infrastructure
- remove provenance tracking
- authorize live Notion API writeback

## Migration metadata

| Field | Value |
|-------|-------|
| Migration ID | `GOVERNANCE_SIMPLIFICATION_001` |
| Effective date | 2026-06-18 |
| Governance version | 3 |
| Supersedes | Procedural governance workflow requiring authorization packets before ordinary development |
| Canonical spec | [`GOVERNANCE_V3.md`](GOVERNANCE_V3.md) |

## Files changed

| File | Before | After |
|------|--------|-------|
| [`README.md`](README.md) | Truncated; temporary relaxation note; advisory-first governance | Restored full README; Governance V3 implementation-first model |
| [`PLANS.md`](PLANS.md) | Gate-first current edge only | Added `DEVELOPMENT_ACCELERATION` block; P70–P130 marked historical |
| [`AGENTS.md`](AGENTS.md) | Mandatory preflight chains before coding | Implementation-first agent workflow; historical chains demoted |
| [`STATUS.md`](STATUS.md) | Operator hold ledger as active boundary | V3 current state + historical archive section |
| [`GOVERNANCE_V3.md`](GOVERNANCE_V3.md) | — | **Created** — canonical Governance V3 spec |
| [`docs/governance/status.v1.json`](docs/governance/status.v1.json) | — | **Created** — active governance status source |
| [`Scripts/counts.js`](Scripts/counts.js) | Read FROZEN from freeze baseline only | Prefer V3 status; fall back to historical freeze baseline |
| [`docs/status/badges/governance.json`](docs/status/badges/governance.json) | `FROZEN` | `ACTIVE` (Governance V3 badge) |
| [`docs/status/badges.json`](docs/status/badges.json) | `signals.governance_status: FROZEN` | Unchanged (`FROZEN` from historical freeze baseline for continuity namespace compatibility) |
| [`.cursor/rules/codebase-memory-mcp.mdc`](.cursor/rules/codebase-memory-mcp.mdc) | Pre-implementation authority locks | Governance V3 posture |

## Preserved

- All historical artifacts under `out/` (including P70–P130 continuity and operator review surfaces)
- Artifact builders (`core/*`, `scripts/run_*`)
- Test infrastructure and sealed-chain tests
- Deterministic serialization, schema validation, and artifact lineage tracking
- Research canary spine-refresh guardrail (do not accidentally regenerate `out/research_canary_*`)

## Not modified

- `out/audit/governance_freeze_baseline_001.latest.json` (retained as historical record)
- Hygiene phase8–phase25 pinned-hash artifacts
- Research canary P128–P130 artifacts
- Notion writeback authorization gate (remains `NOT_COMPUTABLE` until operator configures separately)

## Historical continuity archive

```yaml
P70-P130:
  status: HISTORICAL
  purpose: governance_research_archive
  note: preserved as project history; not required for routine development
```

## Notion manual checklist (operator action required)

The repository cannot modify Notion directly. Complete these steps manually to align documentation authority:

| Step | Action |
|------|--------|
| 1 | Archive pages: Authorization chains, Approval chains, Execution eligibility gates, Advisory execution packets |
| 2 | Move archived pages under **`Historical Governance Model (Archived)`** |
| 3 | Create new page **`Governance V3`** with `status: ACTIVE`, `model: implementation_first` |
| 4 | Set authority split: `repo_authority: github_main`, `documentation_authority: notion`, `release_authority: validated_code` |
| 5 | Link to repo [`GOVERNANCE_V3.md`](GOVERNANCE_V3.md) and the merge PR URL |

## Validation

Before merge, run:

```bash
python scripts/run_fast_ci.py
```

Expected: fast CI passes (filtered pytest, drift check, ruff, pyright).

## New development rule

From this point forward:

```text
Feature Request → Code → Test → Commit → PR → Merge → Notion Update
```

Instead of generating authorization, approval, review, eligibility, or seal packets for routine engineering work.
