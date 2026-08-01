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
| Knowledge Connector | Explicit, canonically hashed links created only from shared evidence references or semantic tags |
| Continual editing | Append/emit new immutable packets; no destructive model or canon mutation |
| Compositional evaluation | Connector-count and cross-modal linkage tests; future benchmark fixtures may extend this |

## Determinism and Ambiguity Controls

- duplicate `memory_id` values are rejected before partitioning;
- connector identities hash canonical structured JSON rather than delimiter-joined strings;
- input ordering does not affect packet or connector ordering;
- entries without shared evidence or semantic tags remain unlinked.

## Explicit Non-Goals

- no LLaVA, MiniGPT-4, BLIP-2, CUDA, checkpoint, or Hugging Face dependency;
- no LoRA or FFN/attention parameter editing;
- no autonomous truth assignment;
- no direct canon mutation;
- no parallel memory database;
- no new Notion hierarchy.

## Governance

The emitted packet is advisory-only and sets all mutation and authority flags to `false`.

## Evidence Paths

- `core/belief_graph/compositional_memory.py`
- `tests/test_compositional_memory.py`
- `core/belief_graph/evidence_object.py`
- `core/belief_graph/engine.py`

## Repository Status (OBSERVED 2026-07-27)

| Surface | State | Evidence |
| --- | --- | --- |
| Pattern assimilation | **MERGED** | PR #986 merged 2026-07-25 |
| Compositional memory contract + tests | **ON MAIN** | `core/belief_graph/compositional_memory.py`, `tests/test_compositional_memory.py` |
| Oracle-ingest adapter | **HELD** | PR #987 closed unmerged (draft/dirty); no new authority granted |
| Notion alignment | **PROJECTION UPDATED** | Master System + Belief Graph + Oracle pages |

```yaml
repository_status: MERGED
pr: 986
continuation_pr: 987
continuation_status: CLOSED_HELD
merge_sha: OBSERVED_VIA_PR_986
authority_change: false
new_pages_created: 0
standalone_subsystem: false
```

## Recommended Next Boundary (HELD)

The narrow next step remains an **optional Oracle-ingest adapter** that converts already-normalized image/text evidence into `CompositionalMemoryEntry` records.

Constraints (unchanged):
- receipt-first
- LOCAL_DEV / SANDBOX only until explicit operator gate
- no model training, LoRA, checkpoints, or runtime authority
- no truth assignment or forecast routing
- no parallel memory store
- no new Notion hierarchy

PR #987 was closed without merge. Any future adapter work must open a **clean, non-stacked branch** from current `main`, remain advisory, and pass fast-CI before review.

Until then the capability is complete at the Belief Graph / packet level and ready for operator-gated Oracle consumption experiments under existing SHADOW attachment paths.
