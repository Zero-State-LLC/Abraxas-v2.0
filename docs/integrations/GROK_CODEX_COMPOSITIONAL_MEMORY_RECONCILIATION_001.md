# GROK + CODEX COMPOSITIONAL MEMORY RECONCILIATION 001

## Decision

The MemEIC-derived compositional evidence-memory work in PRs #986 and #987 is a cooperative extension of existing Abraxas systems. It does not supersede Grok-authored work, and it must consume Grok-derived artifacts through the repository's existing evidence-first reconciliation posture.

## Existing Grok Reconciliation Authority

The repository already contains `core/sync/grok_abx_runes_reconciliation_plan.py`, which establishes the relevant pattern:

- Grok shares and conversations are external evidence sources, not repository authority by themselves;
- Grok claims are compared against live repository artifacts and canonical hashes;
- conflicting implementation or promotion claims are held for operator review;
- no catalog, schema, runtime, Notion, GitHub, or YGGDRASIL mutation is granted implicitly;
- missing or unverifiable evidence returns a blocked or `NOT_COMPUTABLE` state.

This pattern is reused for compositional memory and Oracle intake.

## Cooperative Intake Rule

Grok-produced text, images, schemas, implementation notes, code, or symbolic artifacts may enter the compositional-memory flow when they are normalized into an `EvidenceObject` with explicit provenance.

Required provenance fields should include, when available:

- `producer_system: GROK`
- source conversation or artifact reference
- source timestamp
- content hash
- repository commit or branch reference when code exists
- operator-provided intent or acceptance state

Codex-produced artifacts use the same shape with `producer_system: CODEX`. Jointly reconciled artifacts use `producer_system: MIXED` and identify both source lineages.

## Non-Competition Rule

Neither system's output is wrapped, replaced, or downgraded solely because it came from the other system.

When both systems touch the same capability:

1. preserve both source lineages;
2. compare contracts, behavior, tests, and repository fit;
3. merge compatible work at the narrowest shared contract;
4. record material semantic differences;
5. route unresolved conflicts to operator review;
6. never infer authority from recency, model identity, or narrative confidence.

## Mapping to Active PRs

### PR #986

`CompositionalMemoryEntry` and `KnowledgeConnectorLink` are system-neutral contracts. They may describe Grok, Codex, human, imported, or mixed evidence without changing behavior.

### PR #987

`NormalizedOracleEvidence` is a normalization boundary, not a Codex ownership claim. Grok-originated evidence may pass through this adapter with Grok provenance preserved.

## Governance

- Grok and Codex are peer engineering collaborators.
- Notion stores shared canonical intent.
- GitHub stores implementation evidence.
- Daniel retains final operator authority.
- System identity is provenance, not authority.
- No autonomous truth assignment, canon promotion, FORECAST routing, or runtime mutation is granted.

## Final Seal

```text
GROK_PEER_STATUS=ACTIVE
CODEX_PEER_STATUS=ACTIVE
PROVENANCE_PRESERVED=true
NON_COMPETITION_RULE=true
OPERATOR_REVIEW_ON_CONFLICT=true
MODEL_IDENTITY_GRANTS_AUTHORITY=false
```
