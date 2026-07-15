# Temporal Diff Engine v1

Status: CONTRACT_LOCK_CANDIDATE

## Purpose

`AALViz.TemporalDiff.v1` compares two explicitly supplied,
schema-valid `AALViz.OperatorPlatformProjection.v0.2` documents. It is a
projection-only description of observed change. It retains no history, selects
no implicit baseline, and grants no mutation, routing, scheduling, promotion,
or production authority.

The existing `core.temporal_state_diff` and P70-P130 temporal-continuity
artifacts are historical inputs only. This contract neither extends nor
regenerates them.

## Inputs and generation identity

The caller supplies generation N and N+1. Both projections must pass the
Operator Platform v0.2 schema and authority checks before comparison.

For generation identity, remove `generation.generated_at` and the complete
`temporal_diff` section, normalize the remaining projection as described below,
serialize it as UTF-8 JSON with sorted object keys and compact separators, and
compute SHA-256. The raw input-file SHA-256 is recorded separately as source
provenance and does not create a semantic change by itself.

Published source paths are repository-relative POSIX paths. Absolute paths are
invalid and must fail publication.

## Normalized comparison document

Object keys are sorted. The following collections become maps keyed by their
stable `id`: topology nodes, topology edges, contracts, evidence records, and
system-status work items. Duplicate or empty IDs fail validation.

These arrays are set-like and are deduplicated and sorted: contract producers,
validators, and consumers; evidence inputs, outputs, schemas, and links; source
descriptors; failures; inherited debt; operator summaries; validators;
artifacts; receipts; excluded surfaces; and unresolved links. Orchestration and
execution-flow arrays preserve their declared order. Any array not explicitly
listed preserves order.

`field_path` is an RFC 6901 JSON Pointer into this normalized document. IDs are
escaped using the RFC 6901 `~0` and `~1` rules.

## Operations and ordering

The engine emits only `ADDED`, `REMOVED`, `CHANGED`, and `NOT_COMPUTABLE`.
Unchanged values produce no entry.

Entries are ordered by category, surface, entity ID, field path, operation, and
entry ID. An entry ID is SHA-256 of the compact UTF-8 JSON array containing
operation, category, entity ID, and field path.

Categories are `TOPOLOGY_NODE`, `TOPOLOGY_EDGE`, `CONTRACT_FIELD`, `OWNERSHIP`,
`VALIDATOR_STATE`, `RECEIPT`, `PACKET`, `SOURCE_INTEGRITY`, and
`SECTION_STATUS`.

Impact is `STRENGTHENED`, `WEAKENED`, `NEUTRAL`, or `NOT_COMPUTABLE`.
Ownership changing from unresolved to resolved is strengthened; the inverse is
weakened. An empty validator set becoming non-empty is strengthened; the
inverse is weakened. Arbitrary owner strings, validator contents, and
validation-mode strings are neutral changes.

## Missing evidence

`REMOVED` is valid only when the relevant prior and current evidence statuses
are both `AVAILABLE`. If either side is `PARTIAL` or `NOT_COMPUTABLE`, an
unmatched entity is `NOT_COMPUTABLE`, never removed or added.

Entities observed on both sides may still produce field changes when their
specific values are valid. Missing sections produce one section-level
`NOT_COMPUTABLE` entry and no fabricated descendant changes. Missing input
files produce a valid `NOT_COMPUTABLE` artifact; malformed required fields,
authority violations, duplicate IDs, invalid hashes, and absolute published
paths fail closed and publish nothing.

## Comparison scope

v1 compares topology node and edge presence; contract language, version,
ownership, validation mode, reachability, producers, validators, and consumers;
and evidence-record hashes, status, inputs, outputs, schemas, links, and
fail-closed reasons. Evidence records are classified as receipts or packets by
their explicit Operator Platform source key; unknown keys use `PACKET` only
when the source contract declares packet semantics.

Queue, transport, lineage, alerts, ROUTE_RECEIPT scheduling, topology mutation,
orchestration, hyperstition forecasting, and production activation are out of
scope.

## Operator Platform mapping

The implementation keeps `AALViz.LiveConsoleProjectionBundle.v0.2` and
`AALViz.OperatorPlatformProjection.v0.2`. The temporal section gains prior and
current generation IDs, comparison scope, category counts, and typed entries.
Legacy lineage, queue, and transport counters remain zero and are explicitly
listed as out of scope. The Changes view consumes the typed category counts.

## Contract lock gate

The contract is locked only after the schema validates, all valid fixtures
pass, all invalid fixtures fail for the expected reason, canonical hashes and
entry IDs match fixed vectors, CI passes, and the contract-only pull request is
merged. No engine or AAL-Viz behavior may enter that pull request.
