# Data visualization primitives (Phase 5)

## Goals

Elegant, engineering-first encoding for:

- knowledge / dependency / symbol graphs  
- forecast & probability (advisory styling)  
- confidence / uncertainty  
- timelines & causal chains  
- artifact lineage  
- telemetry & pipeline status  

## Rules

1. **Hue = category**, not severity alone — pair with width/opacity/stroke style.
2. **Registers:** OBSERVED solid, INFERRED dotted/dashed, SPECULATIVE amber dashed.
3. **Forecast** uses domain forecast color + dash; never looks “canonical solid cyan.”
4. **NOT_COMPUTABLE** uses advisory violet + dashed — never success green.
5. **Uncertainty** = muted band / hatch, not error red.
6. Prefer **tabular mono** for numeric readouts (`--abx-font-mono`).

## Files

| Path | Role |
|------|------|
| `topology_palette.v1.json` | Canonical graph/telemetry palette |
| `../components/viz-primitives.css` | CSS bars, legends, timeline, sparks |
| Console bridge | `apps/aal-viz-live-console/src/design/vizPalette.ts` |

## Consumer

`OperatorPlatformViews` topology uses `NODE_COLORS` from the console bridge, which
must stay in sync with `topology_palette.v1.json`.
