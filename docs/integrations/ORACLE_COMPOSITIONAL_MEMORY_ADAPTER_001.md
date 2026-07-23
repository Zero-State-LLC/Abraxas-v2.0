# ORACLE COMPOSITIONAL MEMORY ADAPTER 001

## Status

`FORMALIZED_ADVISORY — STACKED_CONTINUATION`

## Purpose

Convert already-normalized Oracle evidence into the compositional evidence-memory contract introduced by `MEMEIC_ASSIMILATION_001`.

## Cooperative Engineering Boundary

This adapter is system-neutral. It does not claim Codex ownership over Oracle intake and does not supersede Grok-authored Oracle, ingest, memory, routing, or rune work.

Grok-produced evidence may enter the same adapter when provenance is preserved. Codex-produced evidence follows the same rule. Jointly reconciled evidence should identify both source lineages.

The repository's existing Grok reconciliation posture remains authoritative for Grok-derived claims:

- external Grok material is evidence, not automatic repository authority;
- claims are compared against live repository artifacts and canonical hashes;
- conflicts are held for operator review;
- missing evidence is blocked or `NOT_COMPUTABLE`;
- model identity does not grant authority.

See `docs/integrations/GROK_CODEX_COMPOSITIONAL_MEMORY_RECONCILIATION_001.md`.

## Flow

```text
NormalizedOracleEvidence
  -> EvidenceObject
  -> CompositionalMemoryEntry
  -> CompositionalMemoryPacket
```

## Deterministic Inputs

- explicit signal identifier;
- source and timestamp;
- evidence type and content hash;
- explicit modality;
- preserved OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE lane;
- provenance map;
- optional normalized semantic tags.

## Producer Provenance

Recommended producer identifiers:

- `producer_system: GROK`
- `producer_system: CODEX`
- `producer_system: MIXED`
- `producer_system: HUMAN`
- `producer_system: IMPORTED`

These identifiers record lineage only. They do not change confidence, truth status, retrieval priority, or authority.

## Non-Goals

- no raw signal extraction;
- no image or text classification;
- no embeddings or vector search;
- no model inference;
- no truth assignment;
- no FORECAST routing;
- no runtime mutation;
- no execution authority.

## Fail-Closed Rule

Empty input emits a `NOT_COMPUTABLE` receipt with no memory packet. The adapter does not fabricate empty evidence, modality, associations, or authority.

## Evidence Paths

- `core/oracle/compositional_memory_adapter.py`
- `core/belief_graph/compositional_memory.py`
- `tests/test_oracle_compositional_memory_adapter.py`
- `core/sync/grok_abx_runes_reconciliation_plan.py`
- `docs/integrations/GROK_CODEX_COMPOSITIONAL_MEMORY_RECONCILIATION_001.md`

## Dependency

This continuation is stacked on the MemEIC assimilation branch and should be rebased or retargeted to `main` after PR #986 merges.
