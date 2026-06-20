# Audit Archive Compression 001

Brier Score: 0.20

## Status
Brier Score: 0.20

P2-002 audit compression layer for issue `#769` on branch `shadow/v2.5-p2-docs-compression`.

This page compresses the audit/archive landscape into a navigable index surface. It does not replace raw audit receipts, archive seals, or release continuity evidence.

## Purpose
Brier Score: 0.21

- Shorten the path from high-level audit questions to the correct historical surface
- Group audit/archive materials by current navigational use rather than raw chronology alone
- Preserve provenance and historical custody without collapsing the underlying evidence chain

## Audit Family Compression
Brier Score: 0.22

| Audit Family | Primary Surface | What It Covers | Current Relevance | Brier Score |
| --- | --- | --- | --- | --- |
| Active audit entrypoints | [`AUDIT_INDEX.md`](./AUDIT_INDEX.md) | Current audit routing, sweep receipts, and machine-readable companions | Active navigation | 0.22 |
| Repository organization and topology audits | [`REPOSITORY_ORGANIZATION_INVENTORY_001.md`](./REPOSITORY_ORGANIZATION_INVENTORY_001.md) | Repo structure, anomalies, and document topology | Active reference | 0.22 |
| Sprint 001 closure and mirror provenance | [`REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md`](./REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md) | Merged closure state, hashes, and boundary reporting | Active reference | 0.22 |
| Release continuity audits | [`POST_2_5_0_CONTINUATION_AUDIT.md`](../releases/POST_2_5_0_CONTINUATION_AUDIT.md) | Post-release continuation posture and held lanes | High-value historical reference | 0.22 |
| Archive and execution receipts | [`docs/audits/`](./) | Historical seals, execution receipts, and archived audit evidence | Historical reference | 0.22 |

## Archive Routing Table
Brier Score: 0.19

| If you need to inspect... | Start here | Then drill into |
| --- | --- | --- |
| The current audit entry topology | [`AUDIT_INDEX.md`](./AUDIT_INDEX.md) | Current markdown and JSON audit companions |
| Repo organization and doc-discovery debt | [`REPOSITORY_ORGANIZATION_INVENTORY_001.md`](./REPOSITORY_ORGANIZATION_INVENTORY_001.md) | [`DOCUMENTATION_TOPOLOGY_AUDIT_001.md`](./DOCUMENTATION_TOPOLOGY_AUDIT_001.md) and related audit receipts |
| Sprint 001 closure evidence | [`REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md`](./REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md) | `START_HERE.md`, `INDEX.md`, and merged PR references |
| Post-2.5.0 continuation posture | [`POST_2_5_0_CONTINUATION_AUDIT.md`](../releases/POST_2_5_0_CONTINUATION_AUDIT.md) | Release continuity chain and held/deferred lanes |
| Older archive seals and execution receipts | [`AUDIT_INDEX.md`](./AUDIT_INDEX.md) | Specific `REPO_EXECUTION_RECEIPT_*`, `REPO_FINAL_*`, and archived audit surfaces |

## Compression Notes
Brier Score: 0.23

- This page is a routing/compression layer only.
- Active audit usage should prefer the current indexes and receipts before opening older archive bodies.
- Historical execution receipts and archive seals remain authoritative for provenance and should not be rewritten here.

## Provenance
Brier Score: 0.24

- Issue: `#769`
- Branch: `shadow/v2.5-p2-docs-compression`
- Compression Mode: `AUDIT_NAVIGATION_LAYER_ONLY`
- Upstream audit topology source: [`AUDIT_INDEX.md`](./AUDIT_INDEX.md)
- Repo topology source: [`REPOSITORY_ORGANIZATION_INVENTORY_001.md`](./REPOSITORY_ORGANIZATION_INVENTORY_001.md)
- Release continuity source: [`POST_2_5_0_CONTINUATION_AUDIT.md`](../releases/POST_2_5_0_CONTINUATION_AUDIT.md)
- Boundary: no production activation, no governance expansion, no canon promotion, no destructive archive reduction