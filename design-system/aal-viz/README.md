# AAL-Viz visual foundation (Batch 0)

Hallmark-locked **projection-layer** asset pack for Abraxas AAL-Viz.

| | |
|--|--|
| **Status** | CANDIDATE masters · Batches **0 + 1 + 2** |
| **Authority** | Visual only — activation **DENIED**, deploy **NO_GO** |
| **Method** | Hallmark · atmospheric-technical · Tier B hand-built SVG |
| **Generators** | `generate_aal_viz_batch{0,1,2}_assets.py` |

## Start here

1. [`design.md`](./design.md) — locked system
2. [`AAL_VIZ_ASSET_INVENTORY.md`](./AAL_VIZ_ASSET_INVENTORY.md) — counts
3. [`showcase/index.html`](./showcase/index.html) — open in a browser
4. Manifests: `aal_viz_asset_manifest.v1.json` (B0) · `.batch1.v1.json` · `.batch2.v1.json`
5. Runes: [`AAL_VIZ_RUNE_REGISTRY.json`](./AAL_VIZ_RUNE_REGISTRY.json)

## Layout

```
brand/          identity, lockups, social, hero (PRODUCT VISION)     [B0]
authority/      30 epistemic status glyphs (+ solid)                 [B0]
activation/     16 activation-lane marks (+ solid)                   [B0]
navigation/     44 console nav icons (+ solid)                       [B0]
subsystem/      24 system glyphs (+ solid)                           [B0]
graph/          nodes, edges, ports                                  [B0]
workflow/       operator workflow states                             [B1]
metrics/        metric + chart annotation marks                      [B1]
weather/        signal weather (compact · panel · timeline)          [B1]
empty/          empty / blocked / error illustrations                [B1]
panels/         scalable panel / rail / frame treatments             [B1]
a11y/           patterns, line styles, focus, templates              [B1]
runes/aal_viz/  11 projection-layer runes × 4 variants               [B2]
runes/shared/   19 shared ABX runes × 4 variants                     [B2]
docs/           naming, QA, a11y, provenance, handoff, gaps
showcase/       Hallmark workbench preview
```

## Distinct from Abraxas root brand

`design-system/brand/*` is the **kernel** mark. AAL-Viz uses a viewport-plane + constellation sigil under `aal-viz/brand/`.
