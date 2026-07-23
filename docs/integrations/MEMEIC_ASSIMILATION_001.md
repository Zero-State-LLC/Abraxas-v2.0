# MEMEIC ASSIMILATION 001

## Decision

**ASSIMILATE PATTERN; DO NOT IMPORT RUNTIME.**

MemEIC's useful architectural contribution is a three-part pattern:

1. modality-aware external memory;
2. separated textual and visual integration surfaces;
3. an explicit connector between related knowledge units.

Abraxas already has the necessary canonical surfaces: Oracle ingest, provenance-bound evidence objects, Belief Graph claims/evidence/theories/relationships, artifact lineage, deterministic receipts, and advisory-only governance. A new top-level subsystem or additional Notion page family would duplicate these systems.

## Implemented Mapping

| MemEIC concept | Abraxas assimilation |
| --- | --- |
| Mem-E external memory | `CompositionalMemoryEntry` descriptors derived from existing `EvidenceObject` records |
| Separate visual/textual memory | Deterministic `textual_memory` and `visual_memory` partitions in one packet |
| Knowledge Connector | Explicit, hashed links created only from shared evidence references or semantic tags |
| Continual editing | Append/emit new immutable packets; no destructive model or canon mutation |
| Compositional evaluation | Connector-count and cross-modal linkage tests; future benchmark fixtures may extend this |

## Explicit Non-Goals

- no LLaVA, MiniGPT-4, BLIP-2, CUDA, checkpoint, or Hugging Face dependency;
- no LoRA or FFN/attention parameter editing;
- no autonomous truth assignment;
- no direct canon mutation;
- no parallel memory database;
- no new Notion hierarchy.

## Governance

The emitted packet is advisory-only and sets all mutation and authority flags to `false`. Connector generation is deterministic and fail-closed: entries without shared evidence or tags remain unlinked rather than receiving an inferred association.

## Evidence Paths

- `core/belief_graph/compositional_memory.py`
- `tests/test_compositional_memory.py`
- `core/belief_graph/evidence_object.py`
- `core/belief_graph/engine.py`

## Recommended Next Boundary

After this contract is validated in CI, the narrow next step is an optional Oracle-ingest adapter that converts already-normalized image/text evidence into `CompositionalMemoryEntry` records. That adapter should remain receipt-first and must not add model training or runtime authority.
