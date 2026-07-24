# CFAR-001 — Construct-First Analytical Reasoning

**Status:** FORMALIZED_ADVISORY / IMPLEMENTED SHADOW ROUTER  
**Owner:** Abraxas Master System  
**Lane:** SHADOW pre-retrieval  
**Authority:** deny-by-default

## Purpose

CFAR prevents research answers from silently treating latent, disputed, emerging, or culturally variant concepts as directly measurable variables. It runs before evidence retrieval when the requested conclusion depends on the meaning of the question's own terms.

## Deterministic flow

```text
Question
  -> Construct detection
  -> Construct classification
  -> Variable classification
  -> Dimensional decomposition
  -> Measurement-equivalence check
  -> Route decision
```

## Routes

- `EVIDENCE_RETRIEVAL` — construct is sufficiently bounded for source acquisition.
- `FRAMEWORK_ONLY` — operationalization is required before ranking or comparison.
- `HYPOTHESIS_ONLY` — competing definitions permit bounded hypotheses, not definitive rank.
- `NOT_COMPUTABLE` — valid comparison cannot be constructed from available signal.

## Registered runes

- `RUNE.DETECT_CONSTRUCT`
- `RUNE.CLASSIFY_CONSTRUCT`
- `RUNE.DECOMPOSE_CONSTRUCT`
- `RUNE.OPERATIONALIZE_CONSTRUCT`
- `RUNE.CFAR_ROUTE`

The initial repository implementation exposes equivalent deterministic Python functions in `core/cfar.py`. It does not perform source retrieval or LLM inference.

## Packet contract

Schema: `contracts/cfar/construct_packet.v1.schema.json`

Required analytical fields include:

- `construct_status`
- `variable_class`
- `dimensions`
- `assumptions`
- `abstraction_level`
- `measurement_equivalence_required`
- `route`
- `rationale`

## Authority boundary

Every packet seals:

```text
truth_assignment=false
forecast_routing=false
canon_mutation=false
execution_authority=false
```

Retrieval authority is granted only when the deterministic route is `EVIDENCE_RETRIEVAL`. This is routing permission, not truth or execution authority.

## Current limitation

The first implementation uses explicit deterministic vocabulary and suffix heuristics. It is deliberately conservative and reproducible. Expansion of construct dictionaries or domain-specific operationalization templates requires tests and provenance-bound review.
