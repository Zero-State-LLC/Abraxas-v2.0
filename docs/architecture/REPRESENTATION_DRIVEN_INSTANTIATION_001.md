# Representation-Driven Instantiation 001

**Status:** FORMALIZED_ADVISORY / IMPLEMENTATION PARTIAL
**Authority:** Existing Governance V3 and activation policy only
**Scope:** Doctrine and reuse mapping, not a parallel subsystem
**Empirical posture:** This doctrine is not empirical validation of hyperstition,
causal attribution, consciousness, or universal simulation/instantiation equivalence.

**Reuse audit:** [`REPRESENTATION_DRIVEN_INSTANTIATION_REUSE_AUDIT_001.md`](REPRESENTATION_DRIVEN_INSTANTIATION_REUSE_AUDIT_001.md)

## 1. Purpose

This document defines how Abraxas studies whether a represented construct `H`
has evidence-backed causal implementation. The repository's existing architecture
is authoritative. Representation-driven instantiation is a cross-cutting use of
CFAR, evidence ingest, Belief Graph, SHADOW, FORECAST, settlement, provenance,
operator-loop, routing, visualization, and governance primitives.

The governing chain is:

```text
representation
  → causal access
  → observable consequence
  → state transition
  → settlement
  → model update
```

Each arrow is a claim requiring evidence and an epistemic label. A broken or
unsupported arrow remains `NOT_COMPUTABLE` rather than being filled by narrative.

## 2. Scope and non-goals

In scope:

- constructs that may have symbolic, cognitive, behavioral, network,
  computational, institutional, economic, or material consequences;
- state and transition descriptions with provenance and uncertainty;
- forecasts under explicit intervention and no-intervention conditions;
- post-observation settlement and feedback-contamination accounting;
- recursive reinforcement as a special, independently evidenced property.

Non-goals:

- proving that all simulations instantiate their referents;
- proving that simulation excludes instantiation;
- metaphysical claims presented as engineering facts;
- a universal scalar Instantiation Depth, maturity ladder, or hidden score;
- autonomous intervention, canon promotion, or SHADOW-to-FORECAST escalation;
- production or social-world intervention in the initial fixture harness.

## 3. Simulation and instantiation

For a represented construct `H`, Abraxas must infer neither:

```text
simulation(H) ⇒ instantiated(H)
simulation(H) ⇒ not_instantiated(H)
```

Simulation is evidence only for the constitutive properties actually demonstrated
by the execution or representation. A software simulation may demonstrate
executable embodiment while leaving behavioral, institutional, economic, or
material consequence unobserved or `NOT_COMPUTABLE`.

**Instantiation** means evidence-backed causal implementation of one or more
constitutive properties of `H`. It is not a binary declaration about the whole
construct.

**Representation-driven instantiation** is the evidence-backed transition from a
representation through causal access and observable consequence into a changed
state that can later be settled and used to update a model.

**Hyperstition** is representation-driven recursive instantiation. It additionally
requires evidence that consequences attributable to `H` increase, modify, or
preserve `H`'s subsequent capacity for further instantiation. Belief, popularity,
narrative coherence, propagation, correlation, and self-fulfilling appearance do
not by themselves satisfy this definition.

## 4. Canonical domain semantics

These names are doctrine-level aliases until the reuse audit establishes whether
an active schema can carry every required field.

### InstantiationState

Evidence-backed state of `H` at time `t`. A state binds:

- construct identity and operational definition;
- time or observation window;
- independently evidenced InstantiationVector dimensions;
- source and artifact provenance;
- per-claim epistemic classification;
- assumptions, conflicts, and missing-evidence reasons;
- causal exposure when computable.

### InstantiationTransition

The change between two states. A transition binds both state references and records
the changed, unchanged, regressed, bifurcated, or unavailable dimensions. It also
records confidence and epistemic classification without upgrading correlation or
temporal order into causation.

### Intervention

A declared bounded perturbation containing a target, predicted delta, constraints,
provenance, activation lane, and falsification or settlement criteria. Declaration
does not authorize execution. Execution authority remains solely with Governance
V3, `core/governance/activation_policy.py`, and the operator where required.

`InterventionDeclaration.v1` is the narrow composition profile for this semantic.
It references, rather than duplicates, the CFAR construct, baseline state,
WorkPacket, ForecastObject, activation-evaluation evidence, and provenance artifacts. It binds
only named predicted dimension changes, constraints, and falsification criteria.
Predicted changes may be `INFERRED`, `SPECULATIVE`, or `NOT_COMPUTABLE`, never
`OBSERVED`. Its authority fields are const-false and cannot substitute for an
activation evaluation or operator approval.

The declaration validates reference shape and deterministic hashes but does not
resolve an artifact store. Cross-artifact existence, schema identity, and semantic
coherence remain required integration checks before execution or settlement.

### Settlement

The post-observation comparison between a predicted and observed transition. It
records the linked forecast and evidence, prediction error when the forecast has
validated scoring semantics, conflicts, causal exposure, and contamination flags.
The existing `SettlementVerdict.v1` is the primary reusable verdict envelope, but
its current model does not explicitly encode the full InstantiationVector or
ABX-mediated exposure.

## 5. InstantiationVector

The conceptual state vector is:

```text
I_H(t) = [
  symbolic_persistence,
  cognitive_penetration,
  behavioral_consequence,
  network_propagation,
  executable_embodiment,
  economic_institutional_embodiment,
  material_consequence,
  recursive_reinforcement
]
```

The dimensions may coexist, regress, bifurcate, develop in different orders, or
remain `NOT_COMPUTABLE`. They are not stages and are not ordered by maturity.
No repository evidence reviewed for this doctrine validates normalization,
weights, aggregation, thresholds, or a scalar Instantiation Depth. Therefore:

```text
aggregate_instantiation_depth = NOT_COMPUTABLE
```

An absent dimension is not zero and is not false. It is `NOT_COMPUTABLE` unless
evidence supports another epistemically labeled value.

## 6. Epistemic labels

Every relevant claim retains exactly one of:

- `OBSERVED`: directly supported by bound evidence within its stated scope;
- `INFERRED`: derived from observations and declared assumptions;
- `SPECULATIVE`: a bounded hypothesis without sufficient observational support;
- `NOT_COMPUTABLE`: required semantics, evidence, provenance, or comparability are
  absent.

Symbolic interpretation, narrative coherence, correlation, model output, or an
Abraxas intervention must not silently promote `INFERRED` to `OBSERVED`.

## 7. ABX-mediated causation and contamination

Abraxas may be inside the causal system it observes:

```text
H
  → Abraxas observation/model
  → recommendation or authorized intervention A
  → environment
  → H′
```

Where computable, transition evidence records one causal-exposure class:

| Exposure | Meaning |
|----------|---------|
| `EXOGENOUS` | independently observed relative to the Abraxas path under study |
| `ABX_MEDIATED` | Abraxas output or intervention lies on a plausible causal path |
| `MIXED` | exogenous and ABX-mediated exposure cannot be separated cleanly |
| `UNKNOWN` | evidence does not support classification |

These labels describe exposure, not proven attribution. Causal attribution remains
`INFERRED` or `NOT_COMPUTABLE` unless a validated design supports more.

**Feedback contamination** occurs when a model predicts `X`, Abraxas influences an
intervention supporting `X`, and the occurrence of `X` is then treated as
independent confirmation. Settlement must retain the intervention lineage and must
not count that observation automatically as exogenous evidence. Unknown exposure
must never default to `EXOGENOUS`.

## 8. SHADOW, FORECAST, and settlement

**SHADOW detects only:** anomaly, divergence, unexpected transition, missing
evidence, contamination, feedback inversion, and unexplained propagation or decay.
SHADOW does not explain why a transition occurred, issue a forecast, or authorize
an intervention.

**FORECAST predicts only:** a future state or transition conditional on evidence,
assumptions, horizon, and declared intervention or no-intervention conditions. A
forecast must bind outcome and settlement criteria before it can contribute to
calibration. FORECAST does not grant intervention authority.

**Settlement compares:** the declared forecast with later evidence. Brier scoring
is applicable only to forecasts with valid probabilistic outcome semantics and a
bound outcome. Existing Brier telemetry remains scoring and calibration telemetry,
not authority and not causal proof.

## 9. Existing-system mapping

| Doctrine need | Existing Abraxas primitive | Mapping and boundary | Status |
|---------------|----------------------------|----------------------|--------|
| Define `H` before retrieval | `core/cfar.py`, `ConstructPacket.v1` | construct status, dimensions, assumptions, route; no truth or execution authority | `OBSERVED_EXISTING` |
| Acquire evidence | EvidencePack, familiar/universal ingest, Oracle intake | register labels, source summaries, deterministic receipt provenance | `OBSERVED_EXISTING` |
| Represent construct/evidence hypotheses | `core/belief_graph/`, Belief Graph contracts | nodes/edges can represent structured claims; RDI field-level profile not defined | `PARTIAL` |
| Route deterministically | YGGDRASIL | routes artifacts without creating causal or activation authority | `OBSERVED_EXISTING` |
| Specialist architecture/model routing | Alembic Spine | optional advisory analysis; not a parallel kernel | `OBSERVED_EXISTING` |
| Detect drift/contamination | SHADOW surfaces | anomaly-only responsibility is architecturally defined; RDI hooks are not | `PARTIAL` |
| Predict transitions | `ForecastObject.v1`, forecast modules | probability, horizon, evidence refs, outcome-binding state; intervention condition/delta profile is missing | `PARTIAL` |
| Settle later evidence | `SettlementVerdict.v1` | forecast/evidence hashes, reasons, conflicts, verdict and deterministic hash | `PARTIAL` |
| Score predictions | Brier modules and ledger | valid only for settlement-compatible probabilistic outcomes; telemetry-only | `OBSERVED_EXISTING` |
| Preserve lineage | canonical hashes, receipts, artifact registry, agent metadata | traceability and producer identity; identity does not grant authority | `OBSERVED_EXISTING` |
| Bound work and handoff | `WorkPacket.v1`, `HandoffEnvelope.v1` | scope, findings, tests, residual risks, all authority fail-closed | `OBSERVED_EXISTING` |
| Authorize perturbation | Governance V3 and activation policy | LOCAL_DEV/SANDBOX bounded; external production operator-gated | `OBSERVED_EXISTING` |
| Preserve human authority | operator loop | Hermes routes, producers produce, operator decides | `OBSERVED_EXISTING` |
| Project state and lineage | AAL-Viz | read-only visualization, no execution or approval authority | `PARTIAL` |
| Full RDI state/transition profile | `InstantiationState.v1`, `InstantiationTransition.v1` composition contracts | RDI-2 provides fixture-only per-dimension bindings and typed state references; intervention declaration remains separate | `PARTIAL` |
| ABX-mediated exposure round trip | `InstantiationTransition.v1` causal exposure and contamination fields | RDI-2 preserves `ABX_MEDIATED`, `MIXED`, and `UNKNOWN` fail-closed behavior in synthetic fixtures | `PARTIAL` |
| Aggregate Instantiation Depth | no validated semantics | no normalization, weighting, or aggregation may be inferred | `DEFERRED` |

## 10. Falsification and NOT_COMPUTABLE behavior

A forecast or intervention declaration must specify what later observation would
count against it, what evidence window applies, which dimensions may change, and
how contamination affects settlement. A construct is not hyperstitional when the
recursive-reinforcement requirement lacks evidence, even if other dimensions are
observed. In that case the hyperstition claim is `NOT_COMPUTABLE` or contradicted
according to the declared falsification criteria, not rescued by interpretation.

Use `NOT_COMPUTABLE` when any required item is absent, including:

- an operational definition of `H`;
- source or artifact provenance;
- a measurement contract for a dimension;
- comparable state windows;
- a bound forecast outcome or settlement criterion;
- distinguishable exogenous and ABX-mediated exposure;
- validated semantics for aggregation or causal attribution.

## 11. Governance and projection boundaries

No state, transition, forecast, settlement, score, graph edge, SHADOW finding, or
AAL-Viz projection grants intervention authority. Authorized execution uses the
existing activation lane and operator mechanisms. Producer identity records
provenance only. AAL-Viz may display states, transitions, epistemic labels,
contamination, and lineage, but remains projection-only.

## 12. Worked abstract example

Let `H` be a represented scheduling rule in a synthetic organization fixture.

1. CFAR defines `H`, decomposes its constitutive properties, and permits fixture
   evidence retrieval.
2. At `t0`, the rule exists in documents and executable configuration. Symbolic
   persistence and executable embodiment are `OBSERVED`; all other dimensions are
   `NOT_COMPUTABLE`.
3. FORECAST declares that, under an authorized sandbox intervention exposing the
   rule to fixture agents, behavioral consequence will be observed by `t1`. The
   outcome binding and falsification window are fixed before execution.
4. Governance permits only the isolated, reversible sandbox action. Its receipt is
   linked to the forecast and later evidence.
5. At `t1`, fixture logs show changed scheduling behavior. The behavioral
   transition is `OBSERVED`, while causal attribution to `H` is `INFERRED` and
   exposure is `ABX_MEDIATED` because Abraxas initiated the fixture intervention.
6. Settlement compares the forecast with the logs and records contamination. It
   does not treat the result as independent exogenous confirmation.
7. If the changed behavior makes the represented rule more available in a later
   fixture cycle, recursive reinforcement may be tested. Until that evidence is
   collected, the hyperstition claim remains `NOT_COMPUTABLE`.

## 13. Future fixture harness

The first implementation should be deterministic and synthetic:

```text
define H
  → establish I_H(t0)
  → declare forecast
  → optionally declare intervention
  → execute only within authorized lane
  → collect later fixture evidence
  → establish I_H(t1)
  → settle forecast
  → identify contamination
  → update calibration
```

Minimum acceptance properties are deterministic serialization, schema validity,
epistemic-label preservation, ABX-mediated provenance round trip, unknown exposure
remaining non-exogenous, absent dimensions remaining `NOT_COMPUTABLE`, SHADOW
remaining non-explanatory, and FORECAST remaining non-authoritative.

## 14. Implementation status matrix

| Capability | Status | Evidence or gap |
|------------|--------|-----------------|
| Doctrine and vocabulary | `OBSERVED_EXISTING` after this document | canonical semantics and aliases |
| Construct-first definition | `OBSERVED_EXISTING` | CFAR implementation and schema |
| Evidence registers and ingest provenance | `OBSERVED_EXISTING` | EvidencePack and ingest receipts |
| Deterministic forecast and settlement envelopes | `OBSERVED_EXISTING` | ForecastObject.v1 and SettlementVerdict.v1 |
| Field-level schema/type reuse audit | `OBSERVED_EXISTING` | RDI-1 reuse audit completed; no new schema justified yet |
| InstantiationVector composition contracts | `PARTIAL` | eight dimensions retain claim/evidence references or explicit `NOT_COMPUTABLE`; no numeric measurement semantics |
| Intervention predicted-delta profile | `PARTIAL` | `InterventionDeclaration.v1` binds existing work/forecast/activation/provenance references and named non-observed predicted changes; no execution receipt or settlement profile yet |
| ABX-mediated contamination representation | `PARTIAL` | transition contract enforces typed exposure and can bind the intervention declaration; no transition may self-declare independent confirmation |
| SHADOW RDI anomaly hooks | `MISSING` | architectural boundary exists; RDI-specific detector contract does not |
| AAL-Viz RDI projection | `DEFERRED` | projection authority exists; state/transition visual contract does not |
| Fixture experiment and calibration evaluation | `PARTIAL` | state-only, no-intervention, and ABX-mediated settlement requirement fixtures exist; no execution harness or empirical result claimed |
| Aggregate Instantiation Depth | `DEFERRED` | `NOT_COMPUTABLE` pending validated measurement semantics |

Doctrine formalization makes the architecture more coherent. It does not establish
that any real-world construct is instantiated, hyperstitional, or causally affected
by Abraxas.
