# ABRAXAS V2.5 — START HERE

Brier Score: 0.25

Single entry navigation for the Sprint 001 canonical surfaces sweep.

## Primary Hubs
- [Technical Debt & Engineering Direction Board](https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254)
- [Sprint 001 Hub](https://app.notion.com/p/3853e8ba2f5c8139a132ef1eab0ae237)

## Sprint 001 Navigation
- [INDEX.md](./INDEX.md)
- [AUDIT_INDEX.md](./audits/AUDIT_INDEX.md)
- [RELEASE_INDEX.md](./releases/RELEASE_INDEX.md)
- [ARTIFACT_INDEX.md](./artifacts/ARTIFACT_INDEX.md)
- [TEST_INDEX.md](./testing/TEST_INDEX.md)
- [Artifact Registry](./artifacts/ARTIFACT_REGISTRY.md)
- [Subsystem Ownership Matrix](./status/SUBSYSTEM_OWNERSHIP_MATRIX.md)
- [Runtime Readiness Matrix](./status/RUNTIME_READINESS_MATRIX.md)
- [Continuity Lineage Map 001](./audits/CONTINUITY_LINEAGE_MAP_001.md)

## P2 Lineage Compression
Brier Score: 0.18

- [Continuity Lineage Map 002](./lineage/CONTINUITY_LINEAGE_MAP_002.md)
- [Audit Archive Compression 001](./audits/AUDIT_ARCHIVE_COMPRESSION_001.md)
- Issue focus: `#768`, `#769`
- Branch: `shadow/v2.5-p2-docs-compression`
- Purpose: compress P70–P130 and the audit/archive surfaces into navigable repo-native layers without replacing raw historical artifacts

## Broader Repo Topology
- Existing audits, releases, artifacts, testing, workflows, status, operators, plans, and skills docs remain authoritative repo-native surfaces.
- Sprint 001 adds a technical-debt navigation overlay; it does not replace historical evidence or operational release continuity.

## Operating Boundary
- Mode: `SHADOW_ONLY` during execution, merged to `main` after operator gate
- Scope: engineering surfaces, repo organization, technical debt reconciliation
- Excluded: governance expansion, production activation, canon promotion, runtime authority mutation

## Provenance
- Parent Board ID: `3843e8ba-2f5c-8194-80d0-f2c5ffce6254`
- Sprint Hub ID: `3853e8ba-2f5c-8139-a132-ef1eab0ae237`
- Mirror Status: `LAYERED_MIRROR_STABILIZED`
- Merge PR: `#767`
- Embedded DB Status: linked in Notion, not fully row-exported in-session