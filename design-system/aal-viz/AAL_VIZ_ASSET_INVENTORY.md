# AAL-Viz Asset Inventory

**Status:** authored pack **COMPLETE** (batches 0–4)  
**Hallmark:** atmospheric-technical · custom Abraxas grammar · Tier B SVG  
**Authority:** projection-only · activation **DENIED** · deploy **NO_GO**

## Batch 0 — Visual foundation

| Family | Masters | Path |
|--------|--------:|------|
| Identity / brand | 11 | `brand/` |
| Authority (+ solid) | 30 (60 files) | `authority/` |
| Activation (+ solid) | 16 (32 files) | `activation/` |
| Navigation (+ solid) | 44 (88 files) | `navigation/` |
| Subsystem (+ solid) | 24 (48 files) | `subsystem/` |
| Graph nodes / edges / ports | 51 | `graph/` |

## Batch 1 — Runtime console completeness

| Family | Count | Path |
|--------|------:|------|
| Workflow states | 30 | `workflow/` |
| Metrics + chart annotations | 44 | `metrics/` |
| Signal weather (×3 variants) | 51 | `weather/` |
| Empty / error | 26 | `empty/` |
| Panel frames | 22 | `panels/` |
| A11y patterns / lines / focus / templates | 28+ | `a11y/` |

## Batch 2 — Runes

| Family | Count | Path |
|--------|------:|------|
| AAL-Viz runes × 4 variants | 11 | `runes/aal_viz/` |
| Shared ABX runes × 4 variants | 19 | `runes/shared/` |

## Batch 3 — Docs & communication

| Family | Count | Path |
|--------|------:|------|
| Architecture diagrams | 25 | `diagrams/` |
| Infographic templates | 20 | `infographics/` |
| Report / export assets | 25 | `reports/` |
| Banners | 10 | `banners/` |

## Batch 4 — Motion, fields, PWA, marketing

| Family | Count | Path |
|--------|------:|------|
| Motion state icons (+ reduced) | 27 × 2 | `motion/states/` |
| Motion CSS primitives | 1 | `motion/aal_viz_motion.primitives.css` |
| Spatial / wallpaper fields | 20 | `fields/` |
| Responsive headers + controls | 21 | `responsive/` |
| PWA / pinned icons | 5 | `pwa/` |
| Marketing showcases (honesty-labeled) | 17 | `marketing/` |

**Approx SVG total:** ~800+ under `design-system/aal-viz/`

## Registries

| File | Role |
|------|------|
| `aal_viz_asset_manifest.v1.json` + `.batch{1,2,3,4}.v1.json` | Machine inventory |
| `AAL_VIZ_ICON_REGISTRY.json` | Name indexes |
| `AAL_VIZ_RUNE_REGISTRY.json` | Rune ID → files |
| `AAL_VIZ_DIAGRAM_REGISTRY.json` | Diagram honesty labels |
| `AAL_VIZ_MOTION_REGISTRY.json` | Motion tokens + CSS classes |
| `AAL_VIZ_EXPORT_PRESET_REGISTRY.json` | Export presets |

## Existing system (do not duplicate)

- `design-system/icons/system/*` — general Abraxas icons
- `design-system/runes/glyphs/*` — legacy engineering runes
- `design-system/brand/*` — **Abraxas root** mark

## Regenerate

```bash
python scripts/design/generate_aal_viz_batch0_assets.py
python scripts/design/generate_aal_viz_batch1_assets.py
python scripts/design/generate_aal_viz_batch2_assets.py
python scripts/design/generate_aal_viz_batch3_assets.py
python scripts/design/generate_aal_viz_batch4_assets.py
```
