# AAL-Viz

See [ABRAXAS_ATLAS.md#aal-viz](./ABRAXAS_ATLAS.md#aal-viz).

## Surfaces

| Surface | Path |
|---------|------|
| Live console | `apps/aal-viz-live-console/` |
| Projection runners | `scripts/viz/run_aal_viz_*.py` (domain folder — **not** repo root) |
| Visual language pack | `design-system/aal-viz/` (batches **0–4 COMPLETE**) |
| Pack showcase | `design-system/aal-viz/showcase/index.html` |
| Design system root | `design-system/README.md` |

## Current design and integration specifications

- [AAL-Viz Visual Asset Gap Inventory 001](../design/AAL_VIZ_VISUAL_ASSET_GAP_INVENTORY_001.md) — exhaustive asset backlog / batching / QA (historical inventory; pack landings supersede gap status for shipped families)
- [Abraxas Multi-Agent Operator Loop 001](../architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md) — operator, Hermes, Grok, Codex/Cursor, GitHub, Notion, CI, AAL-Viz
- [design-system/aal-viz/README.md](../../design-system/aal-viz/README.md) — shipped pack inventory

AAL-Viz is the **projection and operator-comprehension** layer. It may display assignments, handoffs, validation, conflicts, lineage, and pending decisions, but it does **not** assign work, approve changes, merge code, mutate canon, or grant production authority.
