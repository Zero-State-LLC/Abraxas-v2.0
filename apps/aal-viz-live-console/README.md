# AAL-Viz Live Console

Projection-only operator console for the Abraxas AAL-Viz surface.

## Authority

- `projection_only: true`
- `runtime_mutation_allowed: false`
- `promotion_allowed: false`
- `production_activation_allowed: false`

This surface is read-only. It does not emit metric values, mutate runtime state, promote systems, activate production, enable forecast influence, or open P43 lanes.

## Setup

```bash
cd apps/aal-viz-live-console
npm install
```

## Commands

```bash
npm run typecheck   # TypeScript type check
npm run build       # Production build
npm run dev         # Development server (port 5174)
npm run preview     # Preview production build
```

## Validation Checks

- `systems_visible = 10` (neon_genie, pse, hollersports, level99, noctis, beatoven, phonomicon, psyfi, patchhive, global_spine_registry)
- `forbidden_controls_enabled = 0` (10 controls shown as disabled with FORBIDDEN_BY_AUTHORITY_BOUNDARY label)
- `projection_only = true`
- Authority boundary panel: always visible
- Operator review queue: always visible, no auto-apply

## Data Contract

Schema: `AALViz.LiveConsoleProjectionBundle.v0.1`

All data sourced from static `sampleProjectionBundle`. No external API calls.

## Panels

| Panel | Description |
|-------|-------------|
| StatusPills | 7 system-wide status pills |
| SystemSpineGrid | All 10 systems with status indicators; click to select |
| SystemDetailPanel | Detail view of selected system |
| ProjectionPacketInspector | Projection packets for selected system |
| LedgerReceiptPanel | Ledger receipts for selected system |
| SignalWeatherPanel | Computed metrics: ready/partial/fail/nc/avg/risk |
| OperatorReviewQueue | 5 queue items, auto-apply blocked |
| AuthorityBoundaryPanel | Authority flags + 10 disabled forbidden controls |
