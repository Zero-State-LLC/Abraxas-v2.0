# Abraxas Repository ↔ Notion Convergence Snapshot

**Audit date:** 2026-07-23  
**Observed `main`:** `308fb3694871e08dc95cfc5926655b53357ca5fc`  
**Posture:** advisory reconciliation only  
**Production activation:** denied

## Authority split

- **Notion:** architectural intent, registered subsystem state, ownership routing, and governance doctrine.
- **GitHub:** implementation, tests, review, merge evidence, and executable contracts.
- When the two differ on implementation state, live repository evidence wins. When they differ on governance meaning, the controlling canonical Notion surface governs unless superseded by an explicit repository governance contract.

## July 23 implementation sequence

| PR | Surface | State | Boundary |
|---:|---|---|---|
| #990–#994 | Hygiene Soft Facades and activation documentation | merged | optional observability; `execution_authority=false` |
| #995 | YGGDRASIL scan nodes on `universal_ingest` | merged pilot | no new runes; route expansion not implied |
| #996 | `ConflictReport.v1` builder | merged | detection/classification only; no auto-resolution |
| #997 | Oracle intake conflict population | merged | conflicted inputs fail closed and require review |
| #998 | Cross-drop conflict dimension checks | merged | operator resolution required |
| #986 | MemEIC compositional evidence-memory assimilation | open | existing Belief Graph extension; no parallel subsystem |
| #987 | Normalized Oracle evidence adapter | open, stacked on #986 | deterministic advisory conversion only |
| #989 | `AgentArtifactMetadata.v1` | open | producer identity is provenance, never authority |

## Canonical architectural placement

```text
INGEST
  → EvidenceObject
  → Compositional Memory Packet
  → Belief Graph
  → Oracle SHADOW attachment
  → Conflict scan / advisory receipts
  → Operator review
```

The MemEIC pattern is assimilated into existing Belief Graph and Oracle surfaces. It does not authorize a second memory database, a new Notion hierarchy, parameter editing, truth assignment, runtime mutation, FORECAST routing, or canon mutation.

## Drift findings

1. `STATUS.md` is dated 2026-07-19 and predates PRs #986–#998.
2. Broad CI/readiness labels in older status surfaces should not be treated as proof of current workflow health without commit-specific checks.
3. The Notion Canon Spine required a current registration addendum for Soft Facades, YGGDRASIL route scans, conflict reporting, MemEIC assimilation, and multi-agent provenance.
4. Conflict detection is now implemented, but conflict resolution remains deliberately operator-controlled.
5. Candidate approval does not grant deployment authority; production activation remains denied.

## Continuation order

1. Reconcile and merge or explicitly dispose PR #986.
2. Retarget PR #987 to `main` after #986 lands, then rerun focused and repository gates.
3. Reconcile PR #989 against the merged cooperative-engineering prose contract.
4. Refresh `STATUS.md` from commit-specific evidence rather than inherited readiness language.
5. Preserve the feature/consolidation boundary until the open continuation stack is resolved.

## Seal criteria

- PR #986 has a final disposition.
- PR #987 is no longer stacked on a non-main base and has a final disposition.
- PR #989 is reconciled without duplicating the cooperative engineering contract.
- `STATUS.md` records the July 23 baseline and bounded CI wording.
- Notion contains no duplicate MemEIC, registry, or architecture hierarchy.
- All authority flags remain fail-closed unless explicitly promoted by governance.
