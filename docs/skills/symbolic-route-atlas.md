# Skill: symbolic-route-atlas

Compress YGGDRASIL route and call-path evidence into atlas JSON.

## Targets

- `contracts/yggdrasil/routes/*.route.v1.json`
- `core/yggdrasil_geometric_route_metadata.py`

## MCP workflow

1. `get_graph_schema`
2. `trace_call_path` for route metadata consumers
3. Output atlas summary JSON with provenance header

## Denials

- No route mutation or forecast routing authority
