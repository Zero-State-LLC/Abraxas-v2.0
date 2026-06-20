# Oracle V2 Readiness 005

Brier Score: 0.12

## Status
Brier Score: 0.12

P4 support surface for Neon Genie integration on branch `shadow/v2.5-p4-neon-genie-integration`.

This file routes symbolic/oracle-facing Neon Genie concepts into a readiness model. It does not activate an oracle runtime, define production inference behavior, or promote any canon authority.

## Oracle Readiness Matrix
Brier Score: 0.12

| Oracle Capability | Neon Genie Testbed | Readiness State | Required Evidence | Boundary | Brier Score |
| --- | --- | --- | --- | --- | --- |
| Symbolic draw semantics | Deckbuilder card draws | Planned | Docs-only schema for draw inputs/outputs | No live oracle draws | 0.12 |
| Memetic compression | Roguelite loop summaries | Planned | Compression rubric and review examples | No autonomous generation | 0.13 |
| Autognome generation | Prototype helper/persona sketches | Planned | Explicit prompt/evaluation contract | No agent deployment | 0.14 |
| Constraint interpretation | Puzzle-state interpretation | Planned | Visualization and state model mapping | No solver activation | 0.13 |
| Experiment receipt routing | Venture seed handoffs | Advisory | Receipt template and Brier table | No production telemetry ingestion | 0.11 |

## Neon Genie Oracle Routes
Brier Score: 0.13

| Route | Input | Output | Review Gate | Brier Score |
| --- | --- | --- | --- | --- |
| Deck draw route | Card/mechanic concept | Symbolic reading stub | Operator verifies metaphor remains bounded | 0.13 |
| Loop omen route | Roguelite run summary | Compression note | Reviewer confirms no runtime inference claim | 0.13 |
| Puzzle oracle route | Constraint pattern | Interpretation matrix | Visualization surface confirms state boundaries | 0.13 |
| Venture forecast route | Prototype seed | Brier forecast table | Receipt captures uncertainty and provenance | 0.12 |

## Dependencies
Brier Score: 0.12

| Dependency | Role | Link | Brier Score |
| --- | --- | --- | --- |
| Neon Genie Integration 007 | Primary venture/testbed map | [`NEON_GENIE_INTEGRATION_007.md`](../ventures/NEON_GENIE_INTEGRATION_007.md) | 0.12 |
| Runtime Readiness Matrix 003 | Runtime gating baseline | [`RUNTIME_READINESS_MATRIX_003.md`](../runtime/RUNTIME_READINESS_MATRIX_003.md) | 0.12 |
| Transport Inventory 004 | Transport boundary routing | [`TRANSPORT_INVENTORY_004.md`](../transport/TRANSPORT_INVENTORY_004.md) | 0.12 |
| Visualization Surface Inventory 006 | Visual/state inventory route | [`VISUALIZATION_SURFACE_INVENTORY_006.md`](../visualization/VISUALIZATION_SURFACE_INVENTORY_006.md) | 0.12 |

## Deferred Implementation Questions
Brier Score: 0.14

| Question | Deferred Until | Reason | Brier Score |
| --- | --- | --- | --- |
| What is the concrete oracle input schema? | P5 or later | P4 is docs-only seed | 0.14 |
| What models or services power oracle behavior? | Separate implementation plan | Avoid runtime activation by implication | 0.15 |
| How are oracle outputs evaluated? | Evaluation-specific issue | Needs test data and acceptance criteria | 0.14 |
| How does ABX-GLOBAL-INGEST participate? | Ingest planning lane | No live ingest hook in P4 | 0.15 |

## Boundary
Brier Score: 0.10

- Oracle readiness surface only.
- No oracle runtime activation.
- No autonomous agent deployment.
- No production inference.
- No canon promotion.
- No governance expansion.

## Provenance
Brier Score: 0.12

- Branch: `shadow/v2.5-p4-neon-genie-integration`
- Parent P4 surface: [`NEON_GENIE_INTEGRATION_007.md`](../ventures/NEON_GENIE_INTEGRATION_007.md)
- Parent P3 surface: [`RUNTIME_READINESS_MATRIX_003.md`](../runtime/RUNTIME_READINESS_MATRIX_003.md)
- Status: `P4_NEON_GENIE_SEED_SHADOW_READY`
