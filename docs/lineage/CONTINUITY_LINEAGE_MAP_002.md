# Continuity Lineage Map 002

Brier Score: 0.18

## Status
Brier Score: 0.18

P2-001 compression layer for issue `#768` on branch `shadow/v2.5-p2-docs-compression`.

This page compresses the P70–P130 continuity archive into a navigable index layer. It is a documentation surface, not a canon rewrite, archive reduction, or execution authority surface.

## Purpose
Brier Score: 0.19

- Reduce time-to-orientation across the P70–P130 archive
- Route readers to the correct raw surfaces without forcing full continuity-dump reading
- Preserve provenance, branch context, and historical status labels

## Compression Rules
Brier Score: 0.21

- This map links to raw artifacts and repo-native documents instead of duplicating full historical bodies.
- P70–P130 remains a preserved historical continuity archive under `PLANS.md` and related docs.
- Embedded Notion DB constraints from Sprint 001 remain unchanged; this P2 pass focuses on repo-native historical continuity surfaces.

## Continuity Segment Index
Brier Score: 0.20

| Segment | Span | Primary Role | Current Status | Primary Raw Surface | Brier Score |
| --- | --- | --- | --- | --- | --- |
| Temporal continuity archive | P70-P99 | Procedural continuity and recursive planning chain | HISTORICAL | [`docs/plans/`](../plans/) | 0.20 |
| P102 handoff and compression edge | P100-P102 | Readiness repair, compression audit, and router handoff into later continuity | HISTORICAL | [`PLANS.md`](../../PLANS.md) | 0.20 |
| Research canary continuity | P103-P130 | Research canary review, advisory shadow, and activation hold chain | HISTORICAL / HELD | [`POST_P132_RESEARCH_CANARY_CONTINUATION_PLAN.md`](../releases/POST_P132_RESEARCH_CANARY_CONTINUATION_PLAN.md) | 0.20 |
| Post-P130 release audit edge | Post-2.5.0 closure | Repo-observed continuation posture after the historical chain | ACTIVE REFERENCE | [`POST_2_5_0_CONTINUATION_AUDIT.md`](../releases/POST_2_5_0_CONTINUATION_AUDIT.md) | 0.20 |
| Sprint 001 compression precursor | Sweep 001 | Initial continuity compression placeholder and navigation overlay | MERGED REFERENCE | [`CONTINUITY_LINEAGE_MAP_001.md`](../audits/CONTINUITY_LINEAGE_MAP_001.md) | 0.20 |

## Artifact Family Compression
Brier Score: 0.22

| Artifact Family | Coverage | What It Tells You | Where To Drill Down | Current Relevance | Brier Score |
| --- | --- | --- | --- | --- | --- |
| Historical continuity plans | P70-P99 | Original recursive continuity and governance-era handoff bodies | [`docs/plans/`](../plans/) | Historical reference | 0.22 |
| Continuity repair and router surfaces | P100-P102 | Transition from recursive continuity into later routed lanes | [`PLANS.md`](../../PLANS.md) | Historical reference | 0.22 |
| Research canary release docs | P103-P130 | Advisory shadow status, explicit holds, and continuation options | [`docs/releases/`](../releases/) | High-value historical reference | 0.22 |
| Audit receipts and inventory surfaces | Cross-cutting | Repo-observed closure, topology, and artifact classification evidence | [`docs/audits/`](../audits/) | Active navigation reference | 0.22 |
| Generated artifact lanes | Cross-cutting | Raw `out/` families for temporal continuity and research canary evidence | [`ARTIFACT_INDEX.md`](../artifacts/ARTIFACT_INDEX.md) | Active drill-down route | 0.22 |

## Reader Routing Table
Brier Score: 0.19

| If you need to understand... | Start here | Then drill into |
| --- | --- | --- |
| The overall historical posture of P70-P130 | [`PLANS.md`](../../PLANS.md) | [`docs/plans/`](../plans/) and [`POST_P132_RESEARCH_CANARY_CONTINUATION_PLAN.md`](../releases/POST_P132_RESEARCH_CANARY_CONTINUATION_PLAN.md) |
| Where the temporal continuity bodies physically live | [`REPOSITORY_ORGANIZATION_INVENTORY_001.md`](../audits/REPOSITORY_ORGANIZATION_INVENTORY_001.md) | `docs/plans/` and `out/temporal_continuity*` via [`ARTIFACT_INDEX.md`](../artifacts/ARTIFACT_INDEX.md) |
| The later canary continuation edge | [`POST_P132_RESEARCH_CANARY_CONTINUATION_PLAN.md`](../releases/POST_P132_RESEARCH_CANARY_CONTINUATION_PLAN.md) | [`POST_2_5_0_CONTINUATION_AUDIT.md`](../releases/POST_2_5_0_CONTINUATION_AUDIT.md) |
| The current repo-accepted posture after closure work | [`POST_2_5_0_CONTINUATION_AUDIT.md`](../releases/POST_2_5_0_CONTINUATION_AUDIT.md) | [`START_HERE.md`](../START_HERE.md) and [`INDEX.md`](../INDEX.md) |
| The first continuity compression pass | [`CONTINUITY_LINEAGE_MAP_001.md`](../audits/CONTINUITY_LINEAGE_MAP_001.md) | this page |

## Coverage Notes
Brier Score: 0.23

- P70-P99 is represented here as a compressed family and directory route rather than a page-by-page transcription.
- P100-P102 is compressed through the canonical `PLANS.md` handoff notes because that file explicitly records the archive posture and downstream routing rules.
- P103-P130 is compressed around the release and continuation docs that capture the advisory shadow and hold posture without claiming live activation authority.
- This page does not delete, replace, or supersede raw continuity artifacts.

## Provenance
Brier Score: 0.24

- Issue: `#768`
- Branch: `shadow/v2.5-p2-docs-compression`
- Compression Mode: `NAVIGATION_LAYER_ONLY`
- Upstream continuity posture source: [`PLANS.md`](../../PLANS.md)
- Repo topology source: [`REPOSITORY_ORGANIZATION_INVENTORY_001.md`](../audits/REPOSITORY_ORGANIZATION_INVENTORY_001.md)
- Sprint 001 precursor: [`CONTINUITY_LINEAGE_MAP_001.md`](../audits/CONTINUITY_LINEAGE_MAP_001.md)
- Boundary: no production activation, no governance expansion, no canon promotion, no destructive archive reduction