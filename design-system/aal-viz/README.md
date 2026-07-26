# AAL-Viz visual foundation (Batch 0)

Hallmark-locked **projection-layer** asset pack for Abraxas AAL-Viz.

| | |
|--|--|
| **Status** | CANDIDATE masters · Batches **0–4 COMPLETE** |
| **Authority** | Visual only — activation **DENIED**, deploy **NO_GO** |
| **Method** | Hallmark · atmospheric-technical · Tier B hand-built SVG |
| **Generators** | `generate_aal_viz_batch{0,1,2,3,4}_assets.py` |

## Start here

1. [`design.md`](./design.md) — locked system
2. [`AAL_VIZ_ASSET_INVENTORY.md`](./AAL_VIZ_ASSET_INVENTORY.md) — counts
3. [`showcase/index.html`](./showcase/index.html) — open in a browser
4. Manifests: `aal_viz_asset_manifest.v1.json` + `.batch{1,2,3,4}.v1.json`
5. Runes / diagrams / motion: `AAL_VIZ_{RUNE,DIAGRAM,MOTION}_REGISTRY.json`

## Layout

```
brand/ … graph/          foundation                                 [B0]
workflow/ … a11y/        runtime console                             [B1]
runes/                   engineering alphabet                        [B2]
diagrams/ infographics/ reports/ banners/                            [B3]
motion/ fields/ responsive/ pwa/ marketing/                          [B4]
docs/ showcase/
```

See [`AAL_VIZ_ASSET_INVENTORY.md`](./AAL_VIZ_ASSET_INVENTORY.md) for full counts.

## Distinct from Abraxas root brand

`design-system/brand/*` is the **kernel** mark. AAL-Viz uses a viewport-plane + constellation sigil under `aal-viz/brand/`.
