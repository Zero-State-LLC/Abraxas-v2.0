# Abraxas Visual Operating System

```text
  evidence-oriented · engineering-first · dark-first · never occult
  permanent visual identity for ABRAXAS (2035 OS aesthetic)
```

This package is the **canonical design language** for Abraxas — not a logo drop,
not marketing art. Every token, icon, rune, and surface maps to a semantic role
in the product/architecture.

| Principle | Meaning |
|-----------|---------|
| Clarity | Readable at HUD and dashboard scale |
| Precision | Geometry over ornament |
| State | Color/stroke encode system state |
| Relationships | Edges, lanes, hierarchy are first-class |
| Compression | Dense information without noise |
| Continuity | Same family across years of assets |

**Not allowed:** mystical/occult framing, generic AI brains/robots, fake runtime diagrams, decorative-only chrome.

## Package layout

```text
design-system/
  tokens/           Machine-readable design tokens (JSON + CSS)
  brand/            Abraxas root logo mark, wordmark, favicon, mono
  aal-viz/          AAL-Viz projection-layer pack (Batch 0 · Hallmark)
  icons/system/     SF-Symbols-grade engineering icon family (seed)
  runes/glyphs/     Deterministic geometric function glyphs
  components/       CSS primitives (buttons, panels, chips, HUD)
  illustrations/    Pointers to architecture diagram language
  motion/           Motion principles (informational only)
  wallpapers/       Premium OS wallpapers
  docs/             Phase roadmap + mapping guides
  ASSET_REGISTRY.v1.json   Full asset → system surface map
  VISUAL_OPERATING_SYSTEM.md
```

## Consumer wiring

| Consumer | How to use |
|----------|------------|
| `apps/aal-viz-live-console` | Import `tokens/abraxas.tokens.css`; aliases map legacy `--clr-*` |
| `docs/media/*` | Follow token palette + tier borders |
| Markdown / STATUS | Use semantic chips classes from `components/primitives.css` |
| Future Figma | Import JSON tokens under `tokens/` |

```css
@import url("../../design-system/tokens/abraxas.tokens.css");
```

## Phases

See [`docs/PHASES.md`](docs/PHASES.md).

| Layer | Current |
|-------|---------|
| Tokens | Phase 1 complete (dark + light) |
| Icons | **125** system SVGs |
| AAL-Viz pack | Batch 0 · ~290 SVG masters · see `aal-viz/` |
| Runes | **51** glyphs · **29/29** catalog exact maps |
| Viz | Topology palette + primitives + console bridge |
| Illustrations | Node/edge grammar · `docs/media` retokenized |
| Docs theme | `docs-theme.css` · `docs/showcase.html` |
| Console | Token CSS import + Vite monorepo allow |

**Showcase:** open [`docs/showcase.html`](docs/showcase.html) in a browser.  
**Figma handoff:** [`docs/PHASE10_FIGMA_EXPORT.md`](docs/PHASE10_FIGMA_EXPORT.md)  
**Merge notes:** [`docs/MERGE_READINESS.md`](docs/MERGE_READINESS.md)

```bash
python scripts/design/validate_viz_palette_sync.py   # topology palette ↔ console bridge
```

## Authority

Visual identity does **not** grant production activation, deploy authority, or
canon mutation. Readiness gates remain under `out/production_readiness/`.
