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

Scans `out/metric_operator/`, `out/projections/wasserstein_*`, `out/chamfer_*/`
artifact files, and optionally ingests the P40 climate+motif fusion overlay
(`out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json`) into
the bundle's `fusion_overlay` field when present. Writes the projection bundle.

```bash
python scripts/build_aal_viz_projection_bundle.py
```

Output: `apps/aal-viz-live-console/public/projection-bundle.json`

The frontend fetches `/projection-bundle.json` on load. If the file is absent or
fails authority validation, it falls back to `SAMPLE_FALLBACK` mode.

### Live feed transport posture

The live console transport is advisory-only and fail-closed:

- WebSocket first when `VITE_AAL_VIZ_WS_URL` is configured
- deterministic polling fallback when the socket is unavailable or closes
- sample fallback remains available through the existing bundle loader
- invalid stream payloads fail closed and trigger transport diagnostics rather than execution behavior

Slice67 adds deterministic exponential reconnect scheduling with a `1000ms`
base delay and an `8000ms` cap. The UI now exposes transport mode, fallback
reason, last error reason, and retry delay in the existing status area.

**Never reads:** `research_canary` artifacts.
**Never writes to:** `out/`.

When `fusion_overlay` is present on the bundle, `FusionOverlayPanel` maps P40
`overlay_nodes` to deterministic SVG coordinates and renders resolved
`overlay_edges` as line segments. Dangling edges (missing endpoints) are skipped
and surfaced as `resolved/total` in the panel caption; upstream P40 degradation
is not repaired in the UI.

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
| DynamicMetricDashboardPanel | ABX metric strip, delta tracker, candidate metrics, fusion matrix, feeds, overlay preview, and non-filtering monitor |
| LineageRelationshipOverlayPanel | Declared lineage nodes and relationship arrows with visual-only authority and NOT_COMPUTABLE missing-source styling |
| PacketBindingLayerPanel | v6.7 packet binding readiness frame with live-store keys, Notion deep-link slots, relationship stream slots, and writer/broadcast locks |
| ScoringBindingPanel | v6.8 run-ledger/Brier scoring projection surface with NOT_COMPUTABLE missing forecast/outcome joins and no promotion authority |
| BrierNodeBehaviorPanel | v6.9 Brier-weighted visual behavior surface with neutral CALIBRATION_NOT_COMPUTABLE defaults and no forecast/authority mutation |
| ClusterCalibrationPanel | v7.0 Brier-weighted cluster weather surface with neutral CLUSTER_CALIBRATION_NOT_COMPUTABLE defaults, mixed-cluster shear, static-mode availability, and no forecast/score/authority mutation |
| TemporalCalibrationPanel | v7.1 temporal calibration projection surface with static timeline summaries, temporal gap markers, descriptive curves, and no playback/forecast/score/authority mutation |
| StrategyAttributionPanel | v7.2 descriptive strategy attribution and domain drift surface with explicit baseline comparison gaps, under-sampled/not-computable guards, and no Notion/WebSocket/routing/forecast/score/authority mutation |
| OperatorDecisionOutcomePanel | v7.3 operator decision packet and outcome attribution projection surface with pending/not-computable joins, descriptive decision quality, and no execution/Notion/WebSocket/routing/forecast/score/authority mutation |
| LiveOutcomeReviewPanel | v7.4 live outcome feed and decision review queue projection surface with candidate-only resolutions, append-only correction workflow, review routing, and no provider polling/Notion/WebSocket/execution/routing/forecast/score/truth authority |
| ProviderReliabilityDashboard | v7.5 provider reliability scoring surface with observation ledger, trust bands, provider conflicts, source reliability overlay state, and no healthcheck/Notion/WebSocket/execution/routing/forecast/Brier/outcome truth mutation |
| ReviewSuggestionMatrixPanel | v7.6 automated review suggestions and provider comparison matrix with reason codes, required evidence, source redundancy state, and no writeback/execution/outcome/correction/forecast/score/routing/provider removal authority |
| OperatorWorkflowCommandCenterPanel | v7.7 operator workflow UI with workflow inbox, evidence checklist, provider side panel, composer previews, audit preview, timeline, keyboard command-bar state, Notion context panel, and no writeback/WebSocket/execution/outcome/correction/forecast/score/provider/routing/truth authority |
| WorkflowOperatorAnalyticsPanel | v7.8 workflow analytics and operator performance feedback surface with bottleneck, review aging, suggestion effectiveness, calibration, override/correction quality, visual overlay mapping, and no writeback/WebSocket/execution/promotion/forecast/score/provider/routing/truth authority |
| AnalyticsNarrativeSummaryPanel | v7.9 analytics narrative summary surface with deterministic template rules, provenance-labeled findings, explicit gaps, review prompts, briefing cards, and no writeback/WebSocket/execution/outcome/forecast/score/provider/routing/truth authority |
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

---

## Suggestion Cards Panel

`SuggestionCardsPanel` generates deterministic, display-only intervention suggestion cards from loaded operator action packets. It is placed below `DecisionAttributionPanel` in the center column.

### Card types

| type | trigger |
|---|---|
| `NEXT_SAFE_STEP` | Generated for every packet — surfaces `recommended_next_step` |
| `VALIDATION_REMINDER` | Generated for packets with non-empty `validation_checklist` |
| `AUTHORITY_BOUNDARY` | Generated for packets with non-empty `blocked_scopes` |
| `FRONTIER_PAUSE` | Generated for `REVIEW_REQUIRED` packets only |

### Card fields

Each card carries:
- `suggestion_id` — deterministic from `{TYPE}-{packet_id}`
- `title`, `type`, `source_packet_id`, `rationale`, `suggested_manual_action`
- `authority: 'DISPLAY_ONLY'`
- `execution_allowed: false`, `runtime_mutation_allowed: false`, `promotion_allowed: false`

### Local UI controls

- **Collapse/expand** — each card is collapsed by default; click header to expand
- **Mark reviewed** — UI-only toggle; shows `REVIEWED [UI_ONLY]` badge; increments reviewed count

### Authority boundary — what this panel DOES NOT do

- No auto-apply of any suggestion
- No auto-response
- No execution
- No runtime mutation
- No backend writes
- No persistence

Footer always shows: `DISPLAY_ONLY · NO_AUTO_APPLY · NO_AUTO_RESPONSE · NO_EXECUTION · NO_BACKEND_WRITES · NO_PERSISTENCE`

---

## Frontend Testing

```sh
npm run test       # vitest run — 130+ tests, ~10s
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
| `src/components/DecisionAttributionPanel.test.tsx` | 26 tests |
| `src/components/SuggestionCardsPanel.test.tsx` | 28 tests |

---

## Workflow Analytics Panel

`WorkflowAnalyticsPanel` computes read-only aggregate analytics from the currently loaded operator action packets. It is placed below `SuggestionCardsPanel` in the center column.

### Aggregate metrics computed

| metric | description |
|---|---|
| `total_packets` | Total packets in bundle |
| `copy_prompt_count` | Count of `COPY_PROMPT` packets |
| `copy_checklist_count` | Count of `COPY_CHECKLIST` packets |
| `review_required_count` | Count of `REVIEW_REQUIRED` packets |
| `blocked_packet_count` | Count of packets where `allowed=false` |
| `packets_with_validation_checklist_count` | Packets with non-empty checklist |
| `packets_with_blocked_scopes_count` | Packets with non-empty blocked_scopes |
| `total_validation_checklist_items` | Sum of all checklist items across packets |
| `total_blocked_scope_refs` | Sum of all blocked scope refs across packets |
| `execution_allowed_count` | Packets where `execution_allowed=true` (expected: 0) |
| `runtime_mutation_allowed_count` | Packets where `runtime_mutation_allowed=true` (expected: 0) |
| `promotion_allowed_count` | Packets where `promotion_allowed=true` (expected: 0) |

### Authority health summary

| status | condition |
|---|---|
| `AUTHORITY_CLEAN` | All three forbidden flags count = 0 |
| `FAIL_CLOSED` + `AUTHORITY_VIOLATION_DETECTED` banner | Any forbidden flag count > 0 |

### Analytics source

All metrics are derived from `packetsBundle.packets` only. No external data. No estimates. No stored values.

### Authority boundary — what this panel DOES NOT do

- No backend writes
- No persistence
- No execution
- No runtime mutation
- No metric emission
- No forecast influence

Footer always shows: `READ_ONLY · DISPLAY_ONLY · DERIVED_FROM_LOADED_PACKETS · NO_BACKEND_WRITES · NO_PERSISTENCE`

---

## Frontend Testing

```sh
npm run test       # vitest run — 155+ tests, ~12s
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
| `src/components/DecisionAttributionPanel.test.tsx` | 26 tests |
| `src/components/SuggestionCardsPanel.test.tsx` | 21 tests |
| `src/components/WorkflowAnalyticsPanel.test.tsx` | 30 tests |

---

## Packet Diff Viewer Panel

`PacketDiffViewerPanel` provides a read-only, key-field comparison between any two loaded operator action packets. It is placed below `WorkflowAnalyticsPanel` in the center column.

### Compared fields

| field | diff method |
|---|---|
| `packet_id` | exact string equality |
| `action_type` | exact string equality |
| `recommended_next_step` | truncated to 60 chars, exact equality |
| `execution_allowed` | boolean string equality |
| `runtime_mutation_allowed` | boolean string equality |
| `promotion_allowed` | boolean string equality |
| `blocked_scopes` | joined string equality |
| `validation_checklist_count` | integer count equality |
| `provenance_ref_count` | integer count equality |
| `prompt_body_length` | character count equality |
| `prompt_body_checksum` | deterministic sum-of-charCodes mod 65536, hex |

### Diff statuses

| status | meaning |
|---|---|
| `=` SAME | field value identical in both packets |
| `≠` DIFFERENT | field value differs |
| `←?` MISSING_LEFT | field absent in left packet |
| `?→` MISSING_RIGHT | field absent in right packet |

### Same-packet state

When both selectors point to the same packet, a `SAME PACKET SELECTED` notice is shown and the diff table is hidden.

### Authority diff summary

- `AUTHORITY_CLEAN` — both packets have all three forbidden flags = false
- `FAIL_CLOSED` + `AUTHORITY_DIFF_VIOLATION` banner — any packet has any forbidden flag = true

### Authority boundary — what this panel DOES NOT do

- No backend writes
- No persistence
- No execution
- No runtime mutation
- No external diff libraries

Footer: `READ_ONLY · DISPLAY_ONLY · KEY_FIELDS_ONLY · NO_BACKEND_WRITES · NO_PERSISTENCE`

---

## Frontend Testing

```sh
npm run test       # vitest run — 180+ tests, ~14s
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
| `src/components/DecisionAttributionPanel.test.tsx` | 26 tests |
| `src/components/SuggestionCardsPanel.test.tsx` | 21 tests |
| `src/components/WorkflowAnalyticsPanel.test.tsx` | 28 tests |
| `src/components/PacketDiffViewerPanel.test.tsx` | 22 tests |
