# Phase 10 — Figma / export handoff (spec)

Status: **SPEC LANDED** — no Figma file is committed; tokens are export-ready for operator import.

## Goal

Make the Visual OS loadable into Figma (or Penpot) with:

- Variables (color, spacing, radius, type)
- Component library (buttons, chips, panels, docs notes)
- Icon/rune components (SVG import)
- Styles that match `design-system/tokens/*`

## Source of truth (repo)

| Asset | Path |
|-------|------|
| Colors (dark/light) | `tokens/color.tokens.json` + `semantic.tokens.json` |
| CSS variables | `tokens/abraxas.tokens.css` |
| Typography | `tokens/typography.tokens.json` |
| Spacing / radius / elevation | `tokens/spacing.tokens.json` |
| Motion | `tokens/motion.tokens.json` |
| Topology palette | `viz/topology_palette.v1.json` |
| Icons | `icons/system/*.svg` (125) |
| Runes | `runes/glyphs/*.svg` (51) |
| Brand | `brand/*.svg` |
| Components (CSS) | `components/primitives.css`, `viz-primitives.css`, `docs-theme.css` |
| Registry | `ASSET_REGISTRY.v1.json` |

## Recommended Figma structure

```text
ABX Visual OS
├── 00 Foundations
│   ├── Color / Dark
│   ├── Color / Light
│   ├── Semantic
│   ├── Type
│   └── Spacing & Radius
├── 01 Brand
├── 02 Icons (24 grid)
├── 03 Runes (24 grid)
├── 04 Components
│   ├── Button
│   ├── Chip
│   ├── Panel
│   ├── Callout / Note
│   └── Metric strip
├── 05 Viz
│   ├── Topology legend
│   ├── Confidence bar
│   └── Timeline
└── 06 Documentation layouts
```

## Import procedure (operator)

1. Create Figma file **ABX Visual OS**.
2. Install a variables plugin that accepts JSON (or paste from `color.tokens.json` / `semantic.tokens.json`).
3. Create collections:
   - `Color/Dark`, `Color/Light` from `themes.dark` / `themes.light`
   - `Semantic` from `semantic.tokens.json` roles
4. Import SVGs:
   - Brand marks → components
   - Icons → components named `icon/{name}`
   - Runes → components named `rune/{NAME}`
5. Build components matching CSS class contracts in `components/*.css` (do not invent new semantics).
6. Publish library; link to product files (console mockups, docs).

## Export back to engineering

| From Figma | To repo |
|------------|---------|
| Updated SVG icons | `design-system/icons/system/` |
| New semantic color | `tokens/color.tokens.json` + `semantic.tokens.json` + regenerate `abraxas.tokens.css` |
| Component API change | Document in `VISUAL_OPERATING_SYSTEM.md` first |

**Rule:** semantic roles never renamed without a registry + console bridge update.

## Automated export (future)

Optional scripts (not required for Phase 10 close):

- `scripts/design/export_tokens_css.py` — JSON → CSS (if CSS diverges)
- `scripts/design/validate_palette_sync.py` — assert `vizPalette.ts` ↔ `topology_palette.v1.json`

## Acceptance

- [ ] Operator can recreate dark/light variables from JSON alone  
- [ ] Icon + rune sets import without style drift (stroke 1.5, 24 viewBox)  
- [ ] No occult/fantasy assets in library  
- [ ] Activation/denied chips remain red; advisory remains violet  

## Authority

Figma library publish does **not** authorize production activation or deploy unhold.
