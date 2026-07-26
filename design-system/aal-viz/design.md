# AAL-Viz Visual System · design.md

> Hallmark-locked design system for the AAL-Viz **projection layer**.
> Visual identity only — does **not** authorize production activation, deploy unhold, or execution authority.

```
/* Hallmark · genre: atmospheric-technical · theme: custom (Abraxas projection grammar)
 * macrostructure: Workbench (asset inventory, not marketing page)
 * enrichment: Tier B hand-built SVG · nav: N/A (system pack) · footer: N/A
 * pre-emit critique: P4 H5 E4 S5 R4 V4
 */
```

## Audience · Use · Tone

| Field | Value |
|-------|--------|
| **Audience** | Abraxas operators, engineers, readiness reviewers using AAL-Viz live console and docs |
| **Use case** | Author a single recognisable projection-layer visual language: status without hue-only, topology without text-only boxes, brand without implying authority |
| **Tone** | Technical · austere · projection-only |

## Genre & theme

- **Genre:** atmospheric-technical hybrid (dark console density + restrained cyan/violet grammar).
- **Theme route:** **custom** — locked to existing Abraxas tokens, not a Hallmark catalog theme.
- **Paper:** `#0B1020` / `#080B12` (dark default).
- **Accent primary:** cyan `#00D4F5` (observation / runtime / focus).
- **Accent projection:** violet `#A78BFA` (projection / advisory / inferred).
- **Accent drift/operator:** amber `#F59E0B` / gold `#F2C14E`.
- **Projection domain:** teal `#2DD4BF`.
- **Display / body:** IBM Plex Sans + IBM Plex Mono (existing Visual OS).

## Non-negotiables

1. **Projection-only.** Marks never imply execution, mutation, or production go-live.
2. **Shape ≠ color alone.** Authority/status glyphs must remain legible in monochrome.
3. **`currentColor` stroke icons.** No baked glow in source SVG.
4. **Distinct from Abraxas kernel mark.** AAL-Viz sigil is viewport-plane + constellation, not the lattice-core logo.
5. **Procedural stays procedural.** Live charts, graph layouts, heatmaps, timelines stay code-driven.
6. **Honest labels.** Hero/social that exceed implemented UI must say `PRODUCT VISION`.

## Stroke grammar (icons)

| Token | Value |
|-------|--------|
| Grid | 24×24 |
| Stroke | 1.5 |
| Caps / joins | round |
| Optical sizes | 16 / 24 / 48 |
| Variants | outline · solid (badge plate) · monochrome via `currentColor` |

## Package map

| Path | Role |
|------|------|
| `brand/` | Primary symbol, lockups, favicon, splash, social, hero, watermark |
| `authority/` | Epistemic / evidence status glyphs (30) |
| `activation/` | Engineering activation-lane marks (16) |
| `navigation/` | Console nav icons (44) |
| `subsystem/` | System/subsystem glyphs (24) |
| `graph/nodes\|edges\|ports/` | Topology primitives |
| `aal_viz_asset_manifest.v1.json` | Machine inventory |
| `AAL_VIZ_ICON_REGISTRY.json` | Name indexes |
| `docs/` | Naming, QA, a11y, provenance, handoff, gap ledger |
| `showcase/` | Hallmark preview surface |

## Batch plan

| Batch | Scope | Status |
|-------|--------|--------|
| **0** | Identity + authority + activation + nav + subsystem + graph + governance | **Shipped** |
| **1** | Empty/error, workflow, metrics, weather (×3 variants), panels, a11y patterns | **Shipped** |
| **2** | AAL-Viz + shared engineering runes (outline/solid/engrave/motion) | **Shipped** |
| **3** | Architecture diagrams, infographics, reports, banners | **Shipped** |
| 4 | Motion primitives, wallpapers, PWA raster set | Planned |

### Batch 1–2 paths

| Family | Path | Generator |
|--------|------|-----------|
| Workflow | `workflow/` | `generate_aal_viz_batch1_assets.py` |
| Metrics | `metrics/` | batch1 |
| Weather | `weather/{compact,panel,timeline}/` | batch1 |
| Empty/error | `empty/` | batch1 |
| Panels | `panels/` | batch1 |
| A11y | `a11y/{patterns,lines,focus,templates}/` | batch1 |
| Runes AAL-Viz | `runes/aal_viz/` | `generate_aal_viz_batch2_assets.py` |
| Runes shared | `runes/shared/` | batch2 |
| Rune registry | `AAL_VIZ_RUNE_REGISTRY.json` | batch2 |
| Diagrams | `diagrams/` | `generate_aal_viz_batch3_assets.py` |
| Infographics | `infographics/` | batch3 |
| Reports | `reports/` | batch3 |
| Banners | `banners/` | batch3 |
| Manifests | `aal_viz_asset_manifest.batch{1,2,3}.v1.json` | batch1–3 |

### Rune grammar (batch 2)

- 24×24 grid, frame 22×22 @ (1,1) rx=2, stroke 1.5
- One alphabet — no unique decorative language per rune
- Variants: **outline · solid · engrave · motion** (segmented paths)
- Optical sizes: 16 / 24 / 48 via CSS scaling (same master)
- Does **not** auto-mutate `contracts/runes/catalog.v1.json`; map EXACT only with mandate

## Relationship to Abraxas Visual OS

- Tokens: `design-system/tokens/*` remain canonical.
- System icons / runes already under `design-system/icons` and `design-system/runes` remain valid; AAL-Viz pack is the **projection-layer authored set** with explicit manifest.
- Console bridge: consume via CSS `currentColor` or `<img>`/`<svg>` sprite; do not fork palette hex in components.

## Forbidden

- Occult / fantasy rune aesthetics
- Fabricated live dashboards as marketing truth
- Third-party vendor logos in core pack
- Glassmorphism chrome, aurora-blob backgrounds, gradient display text
- Italic headers (Hallmark gate)
- Lottie for simple status glyphs
