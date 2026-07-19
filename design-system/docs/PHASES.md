# Visual OS roadmap (phases)

| Phase | Deliverables | Status |
|------:|--------------|--------|
| **1** | Brand system, logo, typography, color tokens, semantic map | **LANDED** |
| **2** | Icon library 100–300 (expand seed) | **125 icons** (expandable) |
| **3** | ABX rune system 50–100 glyphs | **51 glyphs**; **29/29** catalog exact maps |
| **4** | UI component library | CSS primitives v0 + console token bridge |
| **5** | Data viz primitives | **LANDED** — topology palette + CSS + console bridge |
| **6** | Illustration language | **LANDED** — grammar JSON + docs/media retokenized |
| **7** | Motion system | **LANDED v0** — principles + transitions.css |
| **8** | Wallpapers / splash | Seed dark wallpapers |
| **9** | Documentation theme | **LANDED** — docs-theme.css + showcase + packet sample |
| **10** | Figma + export pipeline | Future; tokens are export-ready JSON |

## Constraints (permanent)

1. Vector-first SVG; crisp at 16 / 24 / 48 px.
2. Design tokens are source of truth (spacing, radii, elevation, stroke, type, color).
3. Dark theme first; light theme second (parity in CSS).
4. Semantic layer ≠ presentation layer — new states/runes do not require redesign.
5. Handoff structure: `tokens/ icons/ runes/ components/ illustrations/ motion/ wallpapers/ docs/`.
