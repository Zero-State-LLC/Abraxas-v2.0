# Codebase Memory MCP — Operator Workflow

## Status

| Surface | Value |
|---|---|
| `governance_status` | `FROZEN` |
| `canon_status` | `ADVISORY_ONLY` |
| `operator_review_posture` | `ACTIVE` |
| `downstream` | `NOT_COMPUTABLE` |

## Install

```bash
# DeusData codebase-memory-mcp v0.3.4+
# Use official one-line installer with --ui, then:
codebase-memory-mcp config set auto_index true
codebase-memory-mcp config set auto_index_limit 50000
```

Copy [`.cursor/mcp.json.example`](../../.cursor/mcp.json.example) to `.cursor/mcp.json` and set the absolute binary path.

## Index workspace

From repo root:

```bash
# Via MCP tool index_repository(repo_path="/absolute/path/to/workspace")
# Or connect Cursor and run "Index this project"
```

Optional shared artifact: `.codebase-memory/graph.db.zst` (commit after operator index if team-shared graph is desired).

## Token efficiency test protocol

1. Trace `core/governance/authority.py` → `core/scoring/brier.py` via `trace_call_path`
2. Query v2 hygiene Brier hooks via `search_graph(name_pattern=".*brier_scoring_contract.*")`
3. Compare token cost vs full-file grep baseline

Target: structural queries should use graph tools first; reserve `rg` for exact string signals per [cli-operator-layer.md](cli-operator-layer.md).

## Governance trace targets

- `core/governance/brier_provenance.py`
- `core/sync/v2_hygiene_phase6_execution_surface_promotion_gate.py`
- `contracts/scoring/brier_ledger_entry.v1.schema.json`

## Skills

See [docs/skills/](../skills/) for task-specific operator skills:

- `rune-governance-trace`
- `symbolic-route-atlas`
- `brier-telemetry-audit`
