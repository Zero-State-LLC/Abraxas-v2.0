# AAL-Viz Visual QA Checklist

Use before flipping any asset from `CANDIDATE` → `APPROVED` in the manifest.

## Geometry

- [ ] 24×24 viewBox (icons) or documented custom viewBox (brand)
- [ ] Stroke 1.5, round caps/joins
- [ ] Aligns to 24 grid; no 0.5px hairline accidents at 24px
- [ ] Legible at 16px (squint test)
- [ ] No baked glow, blur filters, or drop-shadows in source

## Semantics

- [ ] Shape alone distinguishes status (monochrome pass)
- [ ] Alt text / `<title>` present
- [ ] `authority_implication` is `NONE` unless explicitly reviewed
- [ ] No execution / production-ready metaphor for projection-only surfaces

## Theme

- [ ] Works on dark paper (`#0B1020`)
- [ ] Works on light paper when stroke is dark ink
- [ ] Brand lockups: dark + light + mono as required

## Accessibility

- [ ] Not color-only
- [ ] Decorative uses `aria-hidden` at call site
- [ ] Meaningful uses label / sr-only text at call site
- [ ] Focus rings remain CSS-owned (`--aalviz-focus`), not baked into icon

## Integration

- [ ] Path registered in `aal_viz_asset_manifest.v1.json`
- [ ] Indexed in `AAL_VIZ_ICON_REGISTRY.json` when icon-family
- [ ] Does not break sealed hygiene hash chains (no edits under sealed out/)

## Hallmark gates (showcase / docs surfaces)

- [ ] No italic headers
- [ ] No invented metrics
- [ ] No fake browser chrome
- [ ] Tokens referenced by name in CSS
