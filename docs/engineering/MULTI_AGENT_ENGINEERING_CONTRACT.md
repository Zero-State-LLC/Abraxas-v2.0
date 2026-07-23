# Multi-Agent Engineering Contract

## Status

`FORMALIZED_ADVISORY — OPERATOR_GOVERNED`

## Purpose

This contract coordinates Grok, Codex, human contributors, and imported agent work as peer engineering inputs to one Abraxas architecture.

No model is treated as an authority layer above another model. Notion records canonical intent and registered state. GitHub records implementation evidence. The operator retains final merge, canon, and authority decisions.

## Canonical Flow

```text
Notion intent
  -> architecture contract
  -> implementation by GROK | CODEX | MIXED | HUMAN | IMPORTED
  -> GitHub branch and pull request
  -> tests, CI, review, and lineage evidence
  -> merge
  -> Notion status alignment
```

## Repository-First Coordination

When engineering accounts differ, resolve them in this order:

1. explicit operator intent;
2. merged repository behavior and tests;
3. active pull-request evidence and review state;
4. Notion architectural intent;
5. unmerged agent output.

Producer identity is provenance, not authority.

## Shared Artifact Metadata

Durable artifacts should expose the fields defined by:

`contracts/engineering/agent_artifact_metadata.v1.schema.json`

At minimum, record:

- artifact identifier;
- producer system and version when known;
- implementation surface;
- contract version;
- dependencies and supersession;
- tests and evidence;
- branch, pull request, or merge SHA;
- current lifecycle status.

## Capability Routing

| Capability | Preferred contributor | Exclusive |
| --- | --- | --- |
| Rapid exploration and broad parallel construction | Grok | No |
| Contract alignment and integration closure | Codex | No |
| Testing, CI, review, architecture, and documentation | Shared | No |
| Merge, canon, and authority decisions | Operator | Yes |

Preferences optimize throughput. They do not prohibit either system from contributing to any engineering surface.

## Collision Rules

Before editing overlapping paths:

1. inspect existing Grok, Codex, human, and mixed work;
2. identify the contract and behavior already implemented;
3. reuse compatible work directly;
4. avoid wrappers, renames, or supersession without an observed compatibility reason;
5. preserve all contributing lineages in mixed artifacts;
6. route unresolved semantic conflicts to operator review;
7. never silently report branch work as merged or canon-aligned.

## Shared Vocabulary

Use canonical project terms without model-specific synonyms:

- `EvidenceObject`
- `CompositionalMemoryEntry`
- `KnowledgeConnectorLink`
- `Oracle`
- `Belief Graph`
- `YGGDRASIL`
- `Rune`
- `Artifact`
- `Lineage`
- `SHADOW`
- `FORECAST`
- `Advisory`

## Status Vocabulary

Use the following lifecycle states:

- `PROPOSED`
- `IMPLEMENTED_IN_BRANCH`
- `VALIDATED`
- `MERGED`
- `CANON_ALIGNED`
- `RECONCILIATION_REQUIRED`
- `NOT_COMPUTABLE`

## Governance Locks

```text
MODEL_IDENTITY_GRANTS_AUTHORITY=false
AUTO_SUPERSESSION=false
AUTO_CANON_PROMOTION=false
AUTO_MERGE=false
PRESERVE_PRODUCER_LINEAGE=true
OPERATOR_REVIEW_ON_CONFLICT=true
```

## Current Application

- PR #986: compositional evidence memory; Codex-primary, Grok-compatible.
- PR #987: Oracle compositional-memory adapter; Codex-primary, Grok-compatible, stacked on #986.
- Grok ABX-runes reconciliation: Grok-source evidence processed through repository reconciliation and operator-review surfaces.

The contract applies to future work regardless of which model starts or completes the implementation.