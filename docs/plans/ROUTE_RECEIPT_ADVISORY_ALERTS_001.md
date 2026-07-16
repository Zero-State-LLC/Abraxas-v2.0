# ROUTE_RECEIPT Advisory Alerts 001

Status: CONTRACT_LOCK_CANDIDATE

## Purpose

`AALViz.RouteReceiptAdvisoryAlerts.v1` converts one explicitly supplied,
validated `AALViz.YggdrasilTopologyDeltaIntelligence.v1` projection into a
deterministic aggregate of advisory ROUTE_RECEIPT records. An optional prior
alert projection provides one-generation history. Optional
`AALViz.RouteReceiptAdvisoryAcknowledgements.v1` metadata is read-only,
non-authorizing, and display-only.

The evaluator performs no discovery, retention, scheduling, external delivery,
remediation, escalation, topology mutation, canon mutation, or runtime
mutation. Publication means writing the projection artifact only.

## Inputs and identity

The current delta-intelligence projection is required. Prior alerts and
acknowledgements are optional explicit repository-relative inputs. The prior
alert projection must bind its current topology and Operator Platform
generation IDs to the current delta's prior generation IDs. Mismatched optional
inputs are suppressed with deterministic diagnostics; malformed inputs fail
closed.

`alert_id` is SHA-256 over canonical JSON of policy version, source-reference
category, and source-reference entity ID. Multiple matching rules for that
source are aggregated as sorted trigger types. `receipt_id` hashes alert ID,
event type, receipt disposition, and current delta generation ID.

`alert_generation_id` hashes the complete semantic projection excluding
`generation.generated_at`, itself, and `canonical_hash`. `canonical_hash`
covers the complete artifact excluding only itself.

## Eligibility policy

The v1 policy uses four score tiers: `BASELINE` 0-49, `ELEVATED` 50-69,
`HIGH` 70-84, and `CRITICAL` 85-100.

| Trigger | Eligibility |
| --- | --- |
| `NEW_CRITICAL_STRUCTURAL_FINDING` | NEW, HIGH, score >= 70, SUPPORTED or VERIFIED, affected surfaces present |
| `SEVERITY_ESCALATION` | PERSISTENT and INCREASED to HIGH, or score reaches 70+, SUPPORTED or VERIFIED |
| `VALIDATOR_COVERAGE_LOSS` | score >= 60, SUPPORTED or VERIFIED |
| `BROKEN_PRODUCER_CONSUMER_PATH` | score >= 60, SUPPORTED or VERIFIED |
| `OWNERSHIP_DRIFT` | score >= 60, SUPPORTED or VERIFIED |
| `TOPOLOGY_FRAGMENTATION` | score >= 70, SUPPORTED or VERIFIED |
| `UNEXPECTED_CLUSTER_FUSION` | score >= 60; INFERRED is allowed only with complete topology evidence |
| `PERSISTENT_UNRESOLVED_DAMAGE` | PERSISTENT MEDIUM/HIGH, score >= 70, SUPPORTED/VERIFIED, persistence >= 86400 seconds |

Candidates are suppressed for insufficient score, confidence, persistence,
evidence, or affected surfaces; no eligible trigger; duplication; or unchanged
cooldown. Missing computability is `NOT_COMPUTABLE`, never suppression.

## Pairwise lifecycle and noise control

The cooldown is 86,400 seconds. An unchanged eligible alert within cooldown
remains in the active section but its receipt is suppressed with
`UNCHANGED_WITHIN_COOLDOWN`. A severity transition, score-tier transition,
trigger-set change, or explicit resolution bypasses cooldown. After cooldown,
an unchanged eligible alert becomes `REFRESHED`.

Events are `FIRST_OBSERVED`, `REFRESHED`, `UPDATED`, `RESOLVED`, or
`CARRIED_FORWARD`. A prior active alert closes only when a current correlated
finding is explicitly `RESOLVED` and the correlation section is AVAILABLE.
Structural-only prior alerts without explicit resolution are carried forward.
Missing prior alerts allow first-observed receipts while history-dependent
conclusions remain partial.

Acknowledgement metadata never changes eligibility, rank, cooldown,
suppression, lifecycle, or authority. Unknown acknowledgement references are
excluded with a validation finding.

## Projection and authority

The aggregate is published at
`out/projections/aal_viz_route_receipt_advisory_alerts_v1.latest.json` and may
be embedded unchanged as optional `route_receipt_advisory_alerts` in the
unchanged live-console v0.2 bundle.

Authority locks prohibit execution, runtime/canon/topology mutation, scheduling,
notification delivery, browser persistence, acknowledgement writeback,
automatic remediation, autonomous escalation, and production activation.
Receipt records contain `delivery_state: NOT_DELIVERED` and no destination or
remediation command.

## Contract lock gate

The contract locks after schema self-validation, valid and invalid fixtures,
fixed identity/hash vectors, deterministic ordering checks, CI, review, and
merge of the contract-only PR. Evaluator, runner, bundle, frontend, and
generated projection changes are excluded from that PR.
