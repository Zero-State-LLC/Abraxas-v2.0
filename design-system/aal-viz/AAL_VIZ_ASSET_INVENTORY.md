# AAL-Viz Asset Inventory

**Hallmark:** atmospheric-technical · custom Abraxas grammar · Tier B SVG  
**Authority:** projection-only · activation DENIED · deploy NO_GO

## Batch 0 — Visual foundation

| Family | Masters | Path |
|--------|--------:|------|
| Identity / brand | 11 | `brand/` |
| Authority (+ solid) | 30 (60 files) | `authority/` |
| Activation (+ solid) | 16 (32 files) | `activation/` |
| Navigation (+ solid) | 44 (88 files) | `navigation/` |
| Subsystem (+ solid) | 24 (48 files) | `subsystem/` |
| Graph nodes / edges / ports | 51 | `graph/` |
| Manifest | `aal_viz_asset_manifest.v1.json` | |

## Batch 1 — Runtime console completeness

| Family | Count | Path |
|--------|------:|------|
| Workflow states | 30 | `workflow/` |
| Metrics + chart annotations | 44 | `metrics/` |
| Signal weather compact | 17 | `weather/compact/` |
| Signal weather panel | 17 | `weather/panel/` |
| Signal weather timeline | 17 | `weather/timeline/` |
| Empty / error illustrations | 26 | `empty/` (badge: NOT_COMPUTABLE / FAIL_CLOSED / …) |
| Panel / container frames | 22 | `panels/` |
| A11y pattern fills | 12 | `a11y/patterns/` |
| A11y line styles | 6 | `a11y/lines/` |
| A11y focus chrome | 3 | `a11y/focus/` |
| A11y templates | 7 | `a11y/templates/` |
| Manifest | `aal_viz_asset_manifest.batch1.v1.json` | |

## Batch 2 — Symbolic operating language (runes)

| Family | Count | Path |
|--------|------:|------|
| AAL-Viz-specific runes | 11 × 4 variants | `runes/aal_viz/` |
| Shared ABX runes (viz-visible) | 19 × 4 variants | `runes/shared/` |
| Rune registry | 1 | `AAL_VIZ_RUNE_REGISTRY.json` |
| Manifest | `aal_viz_asset_manifest.batch2.v1.json` | |

Variants per rune: outline · solid · engrave · motion (segmented paths).

**Approx SVG total (batches 0–2):** ~604

## Deferred

| Batch | Scope |
|-------|--------|
| 3 | Architecture diagrams, reports, marketing derivatives |
| 4 | Motion primitives, wallpapers, PWA rasters |

## Existing system (do not duplicate)

- `design-system/icons/system/*` — general Abraxas icons
- `design-system/runes/glyphs/*` — engineering runes
- `design-system/brand/*` — **Abraxas root** mark

## Regenerate

```bash
python scripts/design/generate_aal_viz_batch0_assets.py
python scripts/design/generate_aal_viz_batch1_assets.py
python scripts/design/generate_aal_viz_batch2_assets.py
```
