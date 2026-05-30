# AAL-VIZ LIVE CONSOLE

Projection-only operator console for the Abraxas-v2.0 governed symbolic execution substrate.
Displays operator state, projection bundles, and copyable action packets.
No execution authority. No canon mutation. No metric emission.

## Authority Boundary

| Constraint | Value |
|---|---|
| projection_only | true |
| runtime_mutation_allowed | false |
| promotion_allowed | false |
| production_activation_allowed | false |
| metric_emission | blocked |
| forecast influence | blocked |
| P43 surface lanes | blocked |
| execution_allowed | false (all packets) |

All action packets are **copy-only**. No auto-apply. No auto-execute. No auto-merge.

---

## Adapters

### 1. Artifact Index Adapter

Scans `out/metric_operator/`, `out/projections/wasserstein_*`, and `out/chamfer_*/`
artifact files. Reads 61 source artifacts. Writes the projection bundle.

```bash
python scripts/build_aal_viz_projection_bundle.py
```

Output: `apps/aal-viz-live-console/public/projection-bundle.json`

The frontend fetches `/projection-bundle.json` on load. If the file is absent or
fails authority validation, it falls back to `SAMPLE_FALLBACK` mode.

**Never reads:** `research_canary` artifacts.
**Never writes to:** `out/`.

### 2. Operator Action Packet Adapter

Reads the projection bundle and key source artifacts from `out/metric_operator/`.
Generates copyable manual action packets for operator use.

```bash
python scripts/build_aal_viz_operator_action_packets.py
```

Output: `apps/aal-viz-live-console/public/operator-action-packets.json`

The frontend fetches `/operator-action-packets.json` on load and shows each packet
in the **OPERATOR ACTION PACKETS** panel. Each packet has a copy button.
If the clipboard API is unavailable, a fallback textarea is shown for manual selection.

**Packets are manual/copy-only.** The operator reads the packet, copies the prompt
or checklist, and implements the action manually outside this console.
**Never auto-applies. Never executes. Never mutates `out/` or canon.**

---

## Running Adapters

Run both adapters to keep the console current after any chain step completes:

```bash
python scripts/build_aal_viz_projection_bundle.py
python scripts/build_aal_viz_operator_action_packets.py
```

Both scripts are idempotent and safe to re-run at any time.

---

## Setup

```bash
cd apps/aal-viz-live-console
npm install
npm run dev        # dev server at http://localhost:5173
npm run typecheck  # TypeScript validation
npm run build      # production build
```

The Vite dev server serves `public/` files at the root path, so
`/projection-bundle.json` and `/operator-action-packets.json` are available
immediately after running the adapter scripts.

---

## Tests

### Frontend tests (Vitest + React Testing Library)

```bash
cd apps/aal-viz-live-console
npm run test        # run all tests once
npx vitest          # watch mode
```

| test file | coverage |
|---|---|
| `src/App.test.tsx` | App smoke — renders, 10 systems visible, source mode indicator, no enabled danger buttons |
| `src/components/AuthorityBoundaryPanel.test.tsx` | All 10 forbidden controls disabled, aria-disabled, no enabled buttons |
| `src/components/OperatorActionPacketPanel.test.tsx` | Null bundle empty state, packet render, lock indicators, no exec buttons |

### Python adapter tests

```bash
python -m pytest tests/test_build_aal_viz_projection_bundle.py -q       # adapter bundle tests
python -m pytest tests/test_build_aal_viz_operator_action_packets.py -q  # adapter packet tests
```

---

## Panels

| Panel | Description |
|---|---|
| StatusPills | 8 status pills incl. source mode indicator |
| SystemSpineGrid | All metric operator systems; click to select |
| SystemDetailPanel | Detail view of selected system |
| ProjectionPacketInspector | Projection packets for selected system |
| LedgerReceiptPanel | Ledger receipts for selected system |
| OperatorActionPacketPanel | 4 copyable action packets with authority locks |
| SignalWeatherPanel | Computed metrics: ready/partial/fail/nc/avg/risk |
| OperatorReviewQueue | Chain review items, auto-apply blocked |
| AuthorityBoundaryPanel | Authority flags + disabled forbidden controls |

---

## Source Mode Indicator

The header and the 8th status pill show the current data source:

| Mode | Meaning |
|---|---|
| `LIVE ARTIFACT BUNDLE` | Loaded from `out/` artifacts via the adapter |
| `SAMPLE FALLBACK` | Adapter not run or file not found |
| `FAIL CLOSED` | Authority validation failed |

---

## Forbidden Controls

All buttons labeled `FORBIDDEN_BY_AUTHORITY_BOUNDARY` are permanently disabled.
They are shown to make the authority boundary visible, not to be enabled.

---

## Operator Workflow Panel

`OperatorWorkflowPanel` converts loaded operator action packets into local UI workflow items. It is placed below `OperatorActionPacketPanel` in the center column.

### Workflow item states

| Status | Meaning |
|---|---|
| `AVAILABLE` | Packet ready for copy/review; no action taken yet |
| `COPIED` | Operator clicked COPY; text sent to clipboard |
| `REVIEW_REQUIRED` | Operator marked item as requiring manual review |
| `BLOCKED` | Packet disallowed by authority or manually blocked |
| `COMPLETED_MANUALLY` | Operator marked item as done outside the console |

### Initial state mapping (derived from packet data)

| Packet `action_type` | `allowed` | Initial status |
|---|---|---|
| `COPY_PROMPT` | `true` | `AVAILABLE` |
| `COPY_CHECKLIST` | `true` | `AVAILABLE` |
| `REVIEW_REQUIRED` | `true` | `REVIEW_REQUIRED` |
| any | `false` | `BLOCKED` |

### Authority boundary — what this panel DOES NOT do

- No backend writes of any kind
- No persistence (no localStorage, no sessionStorage)
- No execution of any action
- No runtime mutation
- No canon mutation
- No metric emission
- No forecast influence
- No P43 lane activation

All status changes are **UI_ONLY / NON_AUTHORITATIVE**. Transitioning a packet to `COMPLETED_MANUALLY` in the UI does not signal any downstream system. The panel footer always shows: `NO_EXECUTION · NO_RUNTIME_MUTATION · NO_BACKEND_WRITES · NO_PERSISTENCE · REVIEW_ONLY`.

### Counts bar

The panel header row shows live counts for all five statuses, updating as the operator changes local state.

---

## Frontend Testing

```sh
npm run test       # vitest run — 35+ tests, ~5s
npm run typecheck  # tsc --noEmit
npm run build      # vite production build
```

Test files:

| file | tests |
|---|---|
| `src/App.test.tsx` | 10 smoke tests |
| `src/components/AuthorityBoundaryPanel.test.tsx` | 11 tests |
| `src/components/OperatorActionPacketPanel.test.tsx` | 14 tests |
| `src/components/OperatorWorkflowPanel.test.tsx` | 20 tests |

---

## Evidence Checklist Panel

`EvidenceChecklistPanel` displays the `validation_checklist`, `blocked_scopes`, and `provenance_refs` for any loaded operator action packet. It is placed below `OperatorWorkflowPanel` in the center column.

### Packet selection

A dropdown at the top of the panel lists all loaded packets by title. The first packet is selected by default. Switching packets resets all local toggle state.

If no bundle is loaded, or the selected packet has no checklist, the panel shows a **FAIL CLOSED** empty state.

### Checklist toggles

Each checklist item has a checkbox. Checking an item:
- marks it visually (strikethrough + muted color)
- increments the `REVIEWED N / M [UI_ONLY]` counter

Toggle state is **UI_ONLY / NON_AUTHORITATIVE**:
- No backend write of any kind
- No localStorage or sessionStorage
- No mutation of source packet JSON
- Switching packets resets all toggles

### Authority locks displayed

| lock | value |
|---|---|
| `EXEC BLOCKED` | `execution_allowed=false` |
| `MUTATION BLOCKED` | `runtime_mutation_allowed=false` |
| `PROMOTION BLOCKED` | `promotion_allowed=false` |

### Blocked scopes and provenance refs

Shown when present on the selected packet. These are read-only display fields only.

### Authority boundary — what this panel DOES NOT do

- No execution
- No runtime mutation
- No backend writes
- No persistence
- No metric emission
- No forecast influence
- No P43 lane activation

Footer always shows: `NO_EXECUTION · NO_RUNTIME_MUTATION · NO_BACKEND_WRITES · NO_PERSISTENCE · REVIEW_ONLY`

---

## Frontend Testing

```sh
npm run test       # vitest run — 70+ tests, ~7s
npm run typecheck  # tsc --noEmit
npm run build      # vite production build
```

Test files:

| file | tests |
|---|---|
| `src/App.test.tsx` | 10 smoke tests |
| `src/components/AuthorityBoundaryPanel.test.tsx` | 11 tests |
| `src/components/OperatorActionPacketPanel.test.tsx` | 14 tests |
| `src/components/OperatorWorkflowPanel.test.tsx` | 17 tests |
| `src/components/EvidenceChecklistPanel.test.tsx` | 24 tests |

---

## Decision Attribution Panel

`DecisionAttributionPanel` provides a local UI-only stub for attributing operator decisions to loaded action packets. It is placed below `EvidenceChecklistPanel` in the center column.

### Editable attribution fields (all UI_ONLY)

| field | type | description |
|---|---|---|
| Outcome Status | enum button selector | `UNKNOWN` · `MERGED` · `FAILED` · `HELD` · `SUPERSEDED` |
| Linked PR | text input | freeform PR reference (e.g. `#379`) |
| Manual Result Note | textarea | freeform operator result notes |

Outcome defaults to `UNKNOWN`. Attribution state is stored per-packet in local component state — switching packets preserves each packet's independent attribution.

### Warning banner

The panel always shows:

> ⚠ UI_ONLY — DOES NOT UPDATE REPO, NOTION, OR ARTIFACTS

### Types added

```ts
type DecisionOutcomeStatus = 'UNKNOWN' | 'MERGED' | 'FAILED' | 'HELD' | 'SUPERSEDED';

interface DecisionOutcomeAttribution {
  packet_id: string;
  outcome_status: DecisionOutcomeStatus;
  copied_at: string | null;
  manual_result: string;
  linked_pr: string;
  _ui_only: true;
  _non_authoritative: true;
}
```

### Authority boundary — what this panel DOES NOT do

- No backend write of any kind
- No persistence (no localStorage, no sessionStorage)
- No update to any repo, Notion page, or out/ artifact
- No execution, mutation, promotion, or metric emission

Footer always shows: `NO_EXECUTION · NO_RUNTIME_MUTATION · NO_BACKEND_WRITES · NO_PERSISTENCE · REVIEW_ONLY`

---

## Frontend Testing

```sh
npm run test       # vitest run — 100+ tests, ~9s
npm run typecheck  # tsc --noEmit
npm run build      # vite production build
```

Test files:

| file | tests |
|---|---|
| `src/App.test.tsx` | 10 smoke tests |
| `src/components/AuthorityBoundaryPanel.test.tsx` | 11 tests |
| `src/components/OperatorActionPacketPanel.test.tsx` | 14 tests |
| `src/components/OperatorWorkflowPanel.test.tsx` | 17 tests |
| `src/components/EvidenceChecklistPanel.test.tsx` | 26 tests |
| `src/components/DecisionAttributionPanel.test.tsx` | 30 tests |
