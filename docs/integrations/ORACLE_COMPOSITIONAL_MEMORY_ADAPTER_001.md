# ORACLE COMPOSITIONAL MEMORY ADAPTER 001

## Status

`FORMALIZED_ADVISORY — STACKED_CONTINUATION`

## Purpose

Convert already-normalized Oracle evidence into the compositional evidence-memory contract introduced by `MEMEIC_ASSIMILATION_001`.

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

## Dependency

This continuation is stacked on the MemEIC assimilation branch and should be rebased or retargeted to `main` after PR #986 merges.
