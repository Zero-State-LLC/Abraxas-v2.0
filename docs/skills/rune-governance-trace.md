# Skill: rune-governance-trace

Trace governance and rune surfaces without catalog mutation.

## Targets

- `core/governance/`
- `contracts/runes/catalog.v1.json`
- `core/sync/v2_hygiene_phase*/` → `rune_governance_mapping`

## MCP workflow

1. `search_graph(name_pattern=".*rune_governance_mapping.*")`
2. `trace_call_path` from governance modules to receipt builders
3. Emit compact JSON atlas with `OBSERVED` / `INFERRED` / `SPECULATIVE` per field

## Denials

- `rune_registration_authorized: false`
- No catalog writes
