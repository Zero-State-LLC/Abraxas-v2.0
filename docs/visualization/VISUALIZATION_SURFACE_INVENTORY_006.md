# Visualization Surface Inventory 006

Brier Score: 0.12

## Status
Brier Score: 0.12

P4 support surface for Neon Genie integration on branch `shadow/v2.5-p4-neon-genie-integration`.

This file inventories visualization surfaces and routing needs for Neon Genie concepts. It is a documentation/planning surface only and does not create dashboards, UI, gameplay visuals, live telemetry, or production visualization pipelines.

## Visualization Node Inventory
Brier Score: 0.12

| Node | Purpose | Neon Genie Route | Runtime/Transport Link | Brier Score |
| --- | --- | --- | --- | --- |
| Venture map | Show seed concepts and lineage | Neon Genie Integration 007 | Runtime readiness matrix | 0.12 |
| Mechanic compression board | Map game mechanics to symbolic patterns | Roguelite, deckbuilder, puzzle, UGC | Oracle readiness surface | 0.12 |
| Prototype readiness lane | Show Planned/Shadow/Advisory states | Service-first prototype routing | P3 runtime states | 0.13 |
| Transport chain view | Show input, adapter, receipt, and audit routes | Prototype handoff planning | Transport Inventory 004 | 0.13 |
| Receipt timeline | Preserve wave delivery and forecast | P4 receipt | P2/P3/P4 receipts | 0.11 |

## Drill-Down Taxonomy
Brier Score: 0.12

| Visualization Family | Primary Question | Source Surface | Output Type | Brier Score |
| --- | --- | --- | --- | --- |
| Map | How do Neon Genie concepts route through Abraxas surfaces? | [`NEON_GENIE_INTEGRATION_007.md`](../ventures/NEON_GENIE_INTEGRATION_007.md) | Static diagram or docs table | 0.12 |
| Matrix | Which mechanic maps to which symbolic compression pattern? | Neon Genie mechanic mapping | Markdown table first | 0.12 |
| Timeline | What wave delivered which surface? | P3 and P4 receipts | Receipt-linked chronology | 0.11 |
| Readiness board | What can move from Planned to Advisory? | Runtime readiness and oracle readiness | Planning board only | 0.13 |
| Forecast view | Which prototype has the highest next-step confidence? | Brier forecast tables | Docs-native scorecard | 0.13 |

## Visualization Boundaries
Brier Score: 0.10

| Boundary | Allowed in P4 | Not Allowed in P4 | Brier Score |
| --- | --- | --- | --- |
| Static docs | Markdown tables, diagrams described in prose, link topology | Live dashboard implementation | 0.10 |
| Prototype planning | Visual taxonomy and routing | Game UI production design | 0.11 |
| Runtime state | Readiness visualization | Runtime telemetry collection | 0.12 |
| Oracle route | Symbolic visualization planning | Live oracle output renderer | 0.12 |

## Neon Genie Node
Brier Score: 0.12

| Attribute | Value | Brier Score |
| --- | --- | --- |
| Node name | Neon Genie | 0.12 |
| Node role | Venture/testbed planning layer | 0.12 |
| Primary route | [`NEON_GENIE_INTEGRATION_007.md`](../ventures/NEON_GENIE_INTEGRATION_007.md) | 0.12 |
| Runtime route | [`RUNTIME_READINESS_MATRIX_003.md`](../runtime/RUNTIME_READINESS_MATRIX_003.md) | 0.12 |
| Oracle route | [`ORACLE_V2_READINESS_005.md`](../oracle/ORACLE_V2_READINESS_005.md) | 0.12 |
| Transport route | [`TRANSPORT_INVENTORY_004.md`](../transport/TRANSPORT_INVENTORY_004.md) | 0.12 |

## Deferred Visualization Work
Brier Score: 0.14

| Deferred Surface | Reason Deferred | Candidate Future Lane | Brier Score |
| --- | --- | --- | --- |
| Live dashboard | Requires data contracts and UI scope | P5 visualization | 0.14 |
| Gameplay concept board | Requires creative/product design intent | P5/P6 venture design | 0.15 |
| Oracle output renderer | Requires oracle schema and evaluation rules | Post-Oracle readiness | 0.15 |
| Telemetry visualization | Requires runtime instrumentation plan | Runtime activation lane | 0.15 |

## Boundary
Brier Score: 0.10

- Documentation/planning inventory only.
- No dashboard implementation.
- No gameplay UI production artifact.
- No live telemetry ingestion.
- No oracle renderer activation.
- No production/runtime/governance/canon mutation.

## Provenance
Brier Score: 0.12

- Branch: `shadow/v2.5-p4-neon-genie-integration`
- Parent P4 surface: [`NEON_GENIE_INTEGRATION_007.md`](../ventures/NEON_GENIE_INTEGRATION_007.md)
- Related oracle surface: [`ORACLE_V2_READINESS_005.md`](../oracle/ORACLE_V2_READINESS_005.md)
- Related runtime surface: [`RUNTIME_READINESS_MATRIX_003.md`](../runtime/RUNTIME_READINESS_MATRIX_003.md)
- Status: `P4_NEON_GENIE_SEED_SHADOW_READY`
