# AAL-Viz Asset Integration Handoff

## For console (`apps/aal-viz-live-console`)

1. Prefer CSS chips for authority text; add glyph `<img>` or inline SVG **beside** label, never instead of label.
2. Import icons with `currentColor` so theme tokens drive stroke:
   ```tsx
   // Example pattern — inline or sprite
   <span className="aalviz-status" data-status="OBSERVED">
     <ObservedIcon aria-hidden />
     <span>OBSERVED</span>
   </span>
   ```
3. Do not hotlink diffusion-generated PNGs for status.
4. Graph: use `graph/nodes/*` and edge stroke patterns from CSS/SVG templates; layout remains procedural.
5. **Batch 1 wiring**
   - Workflow states → `workflow/{available,copied,review_required,...}.svg`
   - Signal Weather panel → `weather/compact/*` in chips; `weather/panel/*` in empty header; `weather/timeline/*` on rails
   - Empty panels → `empty/*` with existing textual reason codes (badge already in SVG)
   - Metrics deltas/confidence → `metrics/*` next to mono numbers (values stay procedural)
   - Panel chrome → prefer CSS; use `panels/*` as reference frames or masks
   - Color-blind fills → `a11y/patterns/*` on graph nodes when hue is insufficient

## For docs / README

- Hero: `brand/hero-banner-product-vision.svg` (already labeled PRODUCT VISION).
- Social: `brand/social-preview-1200x630.svg`.
- Co-brand when Abraxas parent must appear: `brand/lockup-cobrand.svg`.

## For design-system consumers

- Register package in `design-system/ASSET_REGISTRY.v1.json` → `aal_viz_projection`.
- Tokens: keep using `abraxas.tokens.css`; optional aliases in `aal-viz/tokens.css`.

## QA gate before APPROVED

Run checklist in `AAL_VIZ_VISUAL_QA_CHECKLIST.md`. Flip manifest `status` only after human semantic review.

## Out of scope

- Deploy unhold, activation, sole-writer fail-closed flips
- Inventing ghost runners or fake telemetry art
