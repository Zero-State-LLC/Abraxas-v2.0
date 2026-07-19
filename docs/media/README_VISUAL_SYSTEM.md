# README VISUAL SYSTEM

> **Canonical design system:** [`design-system/`](../../design-system/)  
> This folder holds **architecture illustration inventory**. Palette and rules are
> superseded by the Visual OS tokens; values below remain for historical diagram compatibility.

## Palette (aligned to Visual OS)

| Name | Hex | Token |
|------|-----|-------|
| Obsidian | `#0B1020` | `--abx-bg-base` |
| Graphite | `#1F2937` | panel (legacy) |
| Deep Indigo | `#2E3A8C` | `--abx-accent-secondary-dim` |
| Cyan | `#00D4F5` / `#06B6D4` | `--abx-accent-primary` |
| Muted Gold | `#C9A227` / `#BFA36A` | `--abx-accent-tertiary` |
| Spectral Amber | `#F59E0B` | `--abx-status-warning` |
| Advisory Violet | `#A78BFA` / `#7C3AED` | `--abx-auth-advisory` |

## Rules

- Use observable architectural elements from repository evidence.
- Represent real runtime topology, governance flow, and continuity lanes.
- Keep diagrams deterministic, compositional, and evidence-oriented.
- No robots. No brains. No generic AI imagery. No fake runtime diagrams.
- All visuals must reflect observable architecture.
- Use shared node/edge language across atlas diagrams.
- Use lane labels and evidence-oriented captions over marketing phrases.
- Route/Rune Binding surfaces must be labeled `FORMALIZED_ADVISORY` and styled with Advisory Violet border.
- Belief Graph surfaces must be labeled `NOT_COMPUTABLE` and must not be styled as implemented surfaces.

## Surface Tier Colors

- Tier 1 (routing/runtime): `--abx-tier-1` / Cyan
- Tier 2 (governance/continuity): `--abx-tier-2` / Gold
- Tier 3 (research/projection): `--abx-tier-3` / Indigo
- Advisory (formalized but non-authoritative): `--abx-tier-advisory`

## Atlas Diagram Inventory

| File | Surface | Status |
|---|---|---|
| `atlas.svg` | Full system topology overview | CURRENT |
| `oracle-signal-layer.svg` | Oracle Signal Layer detail | CURRENT |
| `governance-promotion.svg` | Governance promotion flow | CURRENT |
| `temporal-continuity-spine.svg` | Continuity spine lanes | CURRENT |
| `yggdrasil-routing.svg` | YGGDRASIL route topology | CURRENT |
| `abx-runes.svg` | ABX-Runes catalog surface | CURRENT |
| `aal-core.svg` | AAL core projection surface | CURRENT |
| `runtime-map.svg` | Runtime map | CURRENT |

Registered in: `design-system/ASSET_REGISTRY.v1.json`.

## Sources

All diagram data must be sourced from:

- `docs/status/badges.json`
- `docs/status/continuity-spine.json`
- `out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json`
- `out/audit/yggdrasil_coupling_map_001.latest.json`
- `contracts/runes/catalog.v1.json`
- `contracts/yggdrasil/routes/*.route.v1.json`
- `out/production_readiness/**` (readiness topology)
