# Live YGGDRASIL Topology Enrichment 001

Status: CONTRACT_LOCK_CANDIDATE

## Purpose

`AALViz.YggdrasilTopology.v1` is a deterministic, evidence-backed topology
projection for AAL-Viz. It describes repository-observed and strictly derived
relationships without granting execution, routing, mutation, scheduling,
promotion, alerting, or production authority.

The projection is published at
`out/projections/aal_viz_yggdrasil_topology_v1.latest.json` and may be embedded
unchanged as the optional `yggdrasil_topology` member of an
`AALViz.LiveConsoleProjectionBundle.v0.2`. Its summarized nodes and edges map
into the unchanged `AALViz.OperatorPlatformProjection.v0.2` topology section so
`AALViz.TemporalDiff.v1` can compare their stable identities.

## Identity and ordering

Existing graph-render node and edge IDs, rune IDs, system IDs, route IDs,
binding IDs, and route-binding IDs are preserved. New identities use these
forms:

- `contract:<contract_id>` for contracts;
- `interface:<repository-relative-path>` for producer, validator, consumer,
  and operator interfaces;
- `receipt:<record_id>` and `packet:<record_id>` for evidence records;
- `edge:<sha256>` for new edges, where SHA-256 covers the compact canonical
  JSON array of edge class, source ID, target ID, and relation.

Nodes, edges, evidence records, roles, evidence references, source artifacts,
and validation findings are unique and ordered lexicographically by stable
identity. Duplicate identities, dangling endpoints, dangling evidence
references, malformed paths, and noncanonical ordering fail validation.

## Evidence semantics

Node classes are `SYSTEM`, `RUNE`, `CONTRACT`, `PACKET`, `RECEIPT`, `ROUTE`,
and `INTERFACE`. Interface roles are `PRODUCER`, `VALIDATOR`, `CONSUMER`, and
`OPERATOR`. Edge classes are `PRODUCES`, `VALIDATES`, `CONSUMES`, `BINDS`,
`ROUTES_TO`, `EVIDENCES`, `EXPOSES`, `REFERENCES`, and `RENDER_RELATION`.

Direct declarations from integrity-valid source artifacts are `OBSERVED` with
`VERIFIED` confidence. Exact stable-identity joins across integrity-valid
sources are `INFERRED` with `SUPPORTED` confidence. A single-source derived
relationship may be `INFERRED` with `INFERRED` confidence. Fuzzy matching,
name similarity, and unsupported link creation are forbidden.

Resolution is `RESOLVED`, `UNRESOLVED`, or `NOT_COMPUTABLE`. Freshness is
generation-relative: `CURRENT`, `STALE`, or `NOT_COMPUTABLE`. Wall-clock age
does not affect topology semantics.

## Generation and temporal binding

`topology_generation_id` is SHA-256 over canonical JSON of the complete
artifact after removing `canonical_hash` and `temporal_linkage`, and removing
`generated_at`, `topology_generation_id`, and
`operator_platform_generation_id` from `generation`. This identity therefore
describes semantic topology and source evidence without a self-reference or a
temporal feedback loop.

`canonical_hash` is SHA-256 over canonical JSON of the complete artifact
excluding only `canonical_hash`. `SOURCE_DATE_EPOCH` controls `generated_at`
for reproducible publication without changing normal generation behavior.

The finalized artifact binds to the current Operator Platform generation after
its summarized topology has been mapped. Temporal linkage is `MATCHED` only
when the supplied diff's current generation equals that binding. A mismatch is
`STALE`; missing diff evidence is `NOT_COMPUTABLE`. Nodes and edges expose
stable temporal references using their own IDs and the existing
`TOPOLOGY_NODE` or `TOPOLOGY_EDGE` categories. Diff entry IDs are never written
back into semantic topology.

## Failure posture

Missing optional sources produce `PARTIAL`; no usable sources produce
`NOT_COMPUTABLE` with a null payload and explicit reason. Malformed required
records, authority violations, invalid declared hashes, absolute or traversing
paths, schema violations, duplicate IDs, and graph-integrity violations fail
publication closed.

The builder reads only its explicit source registry. Archived P70-P130
continuity artifacts and `out/research_canary_*` are outside the source set and
must not be read or regenerated.

## Contract lock gate

The contract is locked only after the schema self-validates, valid fixtures
pass, invalid fixtures fail for their expected reasons, deterministic identity
and hash vectors pass, CI succeeds, and the contract-only pull request merges.
No builder, adapter, runtime, or AAL-Viz behavior belongs in the contract PR.
