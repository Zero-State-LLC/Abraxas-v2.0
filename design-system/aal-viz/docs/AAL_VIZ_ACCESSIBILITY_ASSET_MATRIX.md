# AAL-Viz Accessibility Asset Matrix

| Requirement | Batch 0 provision | Residual |
|-------------|-------------------|----------|
| Non-color status | Unique path geometry per authority glyph | Pattern fills (batch 1) |
| Monochrome set | `currentColor` masters | High-contrast dual stroke pack |
| 16px reduced detail | Optical test pending QA flag | Dedicated 16px masters if needed |
| Large targets | Nav icons work at 24/48 | 44px hit areas are CSS |
| Focus rings | CSS `--aalviz-focus` | Not in SVG |
| Decorative suppression | Call-site `aria-hidden` | Registry field `decorative_ok` |
| Alt-text templates | Manifest `alt_text` | Expand to locale pack |
| SR ordering | N/A for static pack | Console component ownership |
| Print / grayscale | Mono lockups + stroke icons | Report templates batch 3 |
| Reduced motion | Static splash; no false progress | Motion pack batch 4 |

## Contrast notes

- Cyan `#00D4F5` on `#0B1020` exceeds body-text AA for large UI chrome; small 16px glyphs should keep stroke ≥1.5 and prefer solid badge plate on low-contrast surfaces.
- Violet advisory on dark is for secondary status — always pair with text label.

## Fail closed

If a status cannot be represented without hue, do **not** ship the glyph — use text chip only (`FAIL_CLOSED`, `NOT_COMPUTABLE` always keep textual form).
