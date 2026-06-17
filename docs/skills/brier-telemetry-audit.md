# Skill: brier-telemetry-audit

Audit Brier telemetry hooks across v2 hygiene lanes without resolving outcomes.

## Targets

- `core/scoring/brier.py`
- `core/governance/brier_provenance.py`
- `core/sync/v2_hygiene_phase*` → `brier_scoring_contract`

## MCP workflow

1. `search_graph(name_pattern=".*brier_scoring_contract.*")`
2. `trace_call_path` from `compute_brier_score` to hygiene receipt builders
3. Report `telemetry_only`, `resolution_allowed`, `brier_resolution_authorized` for each surface

## Denials

- `brier_resolution_authorized: false`
- `binary_outcome` remains `NOT_COMPUTABLE` until explicit operator resolution lane
