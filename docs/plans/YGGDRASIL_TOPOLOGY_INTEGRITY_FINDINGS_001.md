# YGGDRASIL Topology Integrity Findings 001

Status: CONTRACT_LOCK_CANDIDATE

## Purpose

`AALViz.YggdrasilTopologyIntegrity.v1` is a deterministic, projection-only
assessment of one validated `AALViz.YggdrasilTopology.v1` document and an
optional matching `AALViz.TemporalDiff.v1` document. It explains integrity
conditions without delivering alerts, retaining state, accepting
acknowledgements, scheduling work, or granting execution authority.

The projection is published at
`out/projections/aal_viz_yggdrasil_topology_integrity_v1.latest.json` and may
be embedded unchanged as the optional `yggdrasil_topology_integrity` member of
an `AALViz.LiveConsoleProjectionBundle.v0.2`.

## Findings and severity

Finding types and their fixed severities are:

| Finding type | Severity |
| --- | --- |
| `SOURCE_INTEGRITY_GAP`, `GENERATION_MISMATCH` | `HIGH` |
| `UNRESOLVED_ENTITY`, `STALE_ENTITY`, `TEMPORAL_REMOVAL`, `TEMPORAL_WEAKENING` | `MEDIUM` |
| `MISSING_EVIDENCE` | `LOW` |
| `INFERRED_LINK` | `INFO` |
| `SECTION_NOT_COMPUTABLE` | `NOT_COMPUTABLE` |

Each finding is an immutable observation with a stable subject key, optional
entity reference, sorted evidence references, provenance, confidence, reason,
computability, and generation binding. There is no lifecycle, acknowledgement,
notification, or delivery state.

## Identity and ordering

Finding IDs are `finding:<sha256>`, where SHA-256 covers compact canonical JSON
of finding type, entity category or null, entity ID or null, subject key, and
the bound topology generation ID. Findings, source artifacts, evidence
references, and validation findings are ordered lexicographically. Duplicate
IDs, dangling entity or evidence references, summary mismatches, severity
mismatches, and noncanonical ordering fail validation.

`integrity_generation_id` is SHA-256 over canonical JSON of the complete
artifact excluding `canonical_hash`, `generation.generated_at`, and
`generation.integrity_generation_id`. `canonical_hash` covers the complete
artifact excluding only itself. `SOURCE_DATE_EPOCH` controls publication time
without changing ordinary generation behavior.

## Missing evidence and temporal semantics

Temporal removal or weakening is computable only when the Temporal Diff input
is integrity-valid and its current generation matches both the topology's
Operator Platform binding and the finding artifact's temporal binding. A
mismatch emits `GENERATION_MISMATCH` and suppresses all temporal conclusions.
Missing, malformed, partial, or not-computable evidence may emit
`MISSING_EVIDENCE`, `SOURCE_INTEGRITY_GAP`, or `SECTION_NOT_COMPUTABLE`; it
never implies removal or weakening.

## Failure and authority posture

Missing optional Temporal Diff evidence may produce `PARTIAL` without changing
topology-derived findings. Missing or unusable topology evidence produces
`NOT_COMPUTABLE` with a null payload and explicit reason. Malformed required
records, invalid hashes, absolute or traversing paths, duplicate IDs, dangling
references, schema violations, or authority violations fail publication.

The evaluator accepts explicit inputs only. It performs no discovery,
retention, scheduling, mutation, alert delivery, acknowledgement writeback,
ROUTE_RECEIPT triggering, or production activation. Archived P70-P130 and
`out/research_canary_*` artifacts are outside its source set.

## Contract lock gate

The contract locks only after schema self-validation, valid and invalid
fixtures, fixed identity and canonical-hash vectors, review, CI, and merge of
the contract-only PR. Evaluator, adapter, frontend, and generated projection
changes are excluded from that PR.
