# AAL-Viz Visual Regression Matrix

| Surface | What to lock | How |
|---------|--------------|-----|
| Brand primary symbol | Path silhouette | Snapshot SVG hash / visual diff at 64px |
| Authority set | 30 glyphs side-by-side mono | Showcase grid screenshot |
| Activation set | 16 glyphs | Showcase grid |
| Navigation set | 44 glyphs | Showcase grid |
| Graph nodes | 20 shapes | Showcase grid |
| Social card | 1200×630 composition | Pixel snapshot optional |
| Hero banner | Label PRODUCT VISION present | Text assert in CI (grep) |

## Suggested CI (future)

```bash
# Label honesty
rg -n "PRODUCT VISION" design-system/aal-viz/brand/hero-banner-product-vision.svg
# Generator smoke
python scripts/design/generate_aal_viz_batch0_assets.py
git diff --exit-code design-system/aal-viz
```

Batch 0 does not add a hard CI job yet — avoid thrash until console wiring lands.
