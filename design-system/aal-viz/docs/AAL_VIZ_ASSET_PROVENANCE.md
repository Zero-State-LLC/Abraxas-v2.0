# AAL-Viz Asset Provenance

| Field | Value |
|-------|--------|
| Producer | Grok Build + Hallmark skill (hand-built SVG Tier B) |
| Generator | `scripts/design/generate_aal_viz_batch0_assets.py` |
| Date | 2026-07-19 |
| Authority | Visual identity / projection layer only |
| Activation | DENIED (unchanged) |
| Deploy | NO_GO (unchanged) |

## Method

1. Pre-flight against Abraxas Visual OS tokens and existing `design-system/` packs.
2. Hallmark custom theme locked to cyan / violet / amber projection grammar.
3. All Batch 0 icons and brand marks emitted as deterministic SVG (no diffusion models, no Lottie).
4. Manifest records default `qa.*` flags to `false` except `authority_safe: true` for projection-only semantics.

## Not used

- Stock illustration libraries (unDraw, Storyset, …)
- Third-party brand logos in core pack
- Fabricated console screenshots

## Regeneration

```bash
python scripts/design/generate_aal_viz_batch0_assets.py
```

Idempotent overwrite of masters under `design-system/aal-viz/`.
