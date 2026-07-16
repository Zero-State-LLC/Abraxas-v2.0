# YGGDRASIL Topology Delta Intelligence 001

Status: CONTRACT_LOCK_CANDIDATE

## Purpose

`AALViz.YggdrasilTopologyDeltaIntelligence.v1` is a deterministic,
projection-only interpretation of two explicitly supplied YGGDRASIL topology
generations. Optional matching integrity and Temporal Diff documents enrich the
comparison. The evaluator does not discover snapshots, retain history, deliver
alerts, schedule work, mutate topology, or grant execution authority.

The projection is published at
`out/projections/aal_viz_yggdrasil_topology_delta_intelligence_v1.latest.json`
and may be embedded unchanged as the optional
`yggdrasil_topology_delta_intelligence` member of an unchanged
`AALViz.LiveConsoleProjectionBundle.v0.2`.

## Inputs and generation binding

Prior and current `AALViz.YggdrasilTopology.v1` documents are required. Prior
and current `AALViz.YggdrasilTopologyIntegrity.v1` documents and one matching
`AALViz.TemporalDiff.v1` document are optional. Every supplied document is
validated before comparison. Integrity projections must bind to their
corresponding topology generation. Temporal Diff prior/current generation IDs
must match the topology documents' Operator Platform bindings.

The artifact records raw content hashes separately from declared canonical
hashes. Missing optional evidence makes only the dependent sections partial or
not computable. Malformed inputs, authority violations, invalid hashes, unsafe
paths, duplicate IDs, dangling references, or schema violations fail closed.

## Finding correlation

The correlation key is `correlation:<sha256>` over canonical JSON of finding
type, entity category, entity ID, and subject key. It excludes generation
metadata. Exact keys produce `NEW`, `RESOLVED`, and `PERSISTENT` states.
Resolution is emitted only when the relevant evidence domain is complete in
both generations. Severity transitions use the entity reference and subject
key only and are emitted only for one-to-one matches.

Topology-linked findings are `CHANGE_CORRELATED`, never described as caused by
a change. Each correlation records observed or inferred provenance and sorted
supporting topology entity and Temporal Diff entry IDs.

Pairwise persistence reports `observed_generation_count = 2` and the elapsed
seconds between supplied generation timestamps as a lower bound. True
first-seen age is always `NOT_COMPUTABLE` in v1.

## Structural semantics

Operational analysis uses only `PRODUCES`, `VALIDATES`, `CONSUMES`, `BINDS`,
`ROUTES_TO`, and `EXPOSES`. `EVIDENCES` and `RENDER_RELATION` never influence
components or dependency paths. Traversal uses lexicographically ordered
adjacency and deterministic breadth-first search.

Closed structural classes are `ISOLATED_NODE_EMERGENCE`,
`ORPHANED_CONTRACT`, `VALIDATOR_COVERAGE_LOSS`,
`BROKEN_PRODUCER_CONSUMER_PATH`, `OWNERSHIP_DRIFT`,
`STALE_EVIDENCE_CHAIN`, `TOPOLOGY_FRAGMENTATION`, and
`UNEXPECTED_CLUSTER_FUSION`. Unexpected fusion requires an added inferred or
non-verified operational bridge between previously separate components.
Verified, directly declared bridges remain ordinary topology additions.

Any conclusion depending on absence requires complete, integrity-valid prior
and current evidence. Missing or partial evidence never implies resolution,
removal, path breakage, weakening, isolation, orphaning, coverage loss, or
fragmentation.

## Review scoring

Active computable items receive a transparent integer score capped at 100:

| Component | Maximum |
| --- | ---: |
| Current severity | 35 |
| Structural class | 30 |
| Affected operational surfaces | 20 |
| Pairwise persistence | 10 |
| Confidence | 5 |

Every priority record contains the complete component breakdown, evidence
count, affected systems/routes/operator interfaces, and deterministic rank.
Ordering is descending score, descending severity weight, descending evidence
count, then stable ID. Resolved and non-computable observations are excluded
from the active review queue.

## Identity, ordering, and authority

Record IDs are typed prefixes plus SHA-256 over canonical semantic identity.
`delta_generation_id` hashes the complete artifact excluding
`canonical_hash`, `generation.generated_at`, and itself. `canonical_hash`
covers the complete artifact excluding only itself. Arrays declared set-like
by the schema are lexicographically ordered and duplicate-free.

Authority locks prohibit acknowledgement state, alert delivery, browser
persistence, canon or runtime mutation, graph-driven execution, production
activation, ROUTE_RECEIPT triggering, scheduling, automatic remediation, and
autonomous escalation.

## Contract lock gate

The contract locks only after schema self-validation, valid and invalid
fixtures, fixed ID/hash vectors, deterministic review, CI, and merge of the
contract-only PR. Evaluator, runner, adapter, frontend, and generated projection
changes are excluded from that PR.
