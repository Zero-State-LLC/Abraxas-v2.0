# Visual OS roadmap (phases)

| Phase | Deliverables | Status |
|------:|--------------|--------|
| **1** | Brand system, logo, typography, color tokens, semantic map | **LANDED** (this foundation) |
| **2** | Icon library 100–300 (expand seed) | Seed 32 icons |
| **3** | ABX rune system 50–100 glyphs | Seed 24 glyphs + map to `contracts/runes` |
| **4** | UI component library | CSS primitives v0 |
| **5** | Data viz primitives | Spec in VOS doc; implement incrementally |
| **6** | Illustration language | Existing `docs/media` adopted + rules |
| **7** | Motion system | Principles landed |
| **8** | Wallpapers / splash | Seed dark wallpapers |
| **9** | Documentation theme | Callout/chip styles in primitives |
| **10** | Figma + export pipeline | Future; tokens are export-ready JSON |

## Constraints (permanent)

1. Vector-first SVG; crisp at 16 / 24 / 48 px.
2. Design tokens are source of truth (spacing, radii, elevation, stroke, type, color).
3. Dark theme first; light theme second (parity in CSS).
4. Semantic layer ≠ presentation layer — new states/runes do not require redesign.
5. Handoff structure: `tokens/ icons/ runes/ components/ illustrations/ motion/ wallpapers/ docs/`.
