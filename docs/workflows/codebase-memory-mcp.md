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
# DeusData codebase-memory-mcp v0.8.1+ (pip, installer, or package manager)
pip install codebase-memory-mcp
# Linux: zstd CLI required for team-shared graph export
sudo apt-get install -y zstd   # or distro equivalent

codebase-memory-mcp config set auto_index true
codebase-memory-mcp config set auto_index_limit 50000
```

Copy [`.cursor/mcp.json.example`](../../.cursor/mcp.json.example) to `.cursor/mcp.json` and set the absolute binary path (`which codebase-memory-mcp`).

## Index workspace

From repo root (absolute path required):

```bash
export PATH="$HOME/.local/bin:$PATH"
codebase-memory-mcp cli index_repository '{"repo_path": "/absolute/path/to/workspace", "persistence": true}'
```

`persistence: true` writes `.codebase-memory/graph.db.zst` (team-shared compressed graph) and `.codebase-memory/artifact.json` (metadata). Teammates bootstrap from the artifact on first index instead of full re-indexing.

Via MCP in Cursor: use `index_repository` with `persistence: true`, or say "Index this project" after MCP is wired.

**Size note:** current workspace artifact is ~16 MB compressed (107 MB SQLite source). If binary growth becomes a concern, use Git LFS or keep artifact local-only.

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
