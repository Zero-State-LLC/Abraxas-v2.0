# Representation-Driven Instantiation Reuse Audit 001

**Status:** RDI-1 COMPLETE / DOCUMENTATION-ONLY
**Authority:** Advisory architecture audit; no execution or promotion grant
**Parent:** [`REPRESENTATION_DRIVEN_INSTANTIATION_001.md`](REPRESENTATION_DRIVEN_INSTANTIATION_001.md)

## 1. Decision

RDI-1 did not add an RDI schema. RDI-2 subsequently used the fixture requirements
below to justify a narrow state/transition composition pair without changing the
reuse conclusions in this audit.

The repository already has reusable contracts for construct definition, evidence
claims, epistemic labels, graph hypotheses, forecasts, settlement, provenance,
work scoping, and activation evaluation. It does not yet have enough validated
semantics to define one stable InstantiationState, InstantiationTransition, or
Intervention wire format without either duplicating those contracts or inventing
measurement semantics.

RDI-2 may introduce only a narrow composition/profile contract after synthetic
fixture requirements prove which missing fields must survive deterministic round
trip. Existing schemas remain authoritative and should be referenced rather than
copied.

RDI-3 subsequently added `InterventionDeclaration.v1` for the proven fields that
could not be expressed by reference alone: named predicted dimension changes,
constraints, falsification criteria, and explicit non-authority locks. It composes
the existing CFAR/state, WorkPacket, ForecastObject, activation-evaluation evidence, and
provenance artifacts by ID/hash. This later gap closure does not change the RDI-1
finding that those source contracts remain authoritative.

## 2. Active contracts inspected

| Surface | Active contract/type | Reusable role |
|---------|----------------------|---------------|
| Construct definition | `ConstructPacket.v1` | construct identity, status, dimensions, assumptions, measurement-equivalence gate |
| Evidence acquisition | `EvidencePack.v0` | sourced claims, epistemic register, confidence note, producer/tool provenance |
| Belief representation | `ClaimObject.v1`, `EvidenceObject.v1`, `TheoryObject.v1`, `SignalGraph.v1`, `BeliefGraphPacket.v1` | claim/evidence/theory identity, support/conflict relations, graph edges, SHADOW/FORECAST locks |
| Forecast | `ForecastObject.v1` | claim, probability, horizon, lane, evidence references, outcome-binding and calibration posture |
| Settlement | `SettlementVerdict.v1` | forecast/evidence binding, decision, reasons, conflicts, status, authority reference, deterministic hash |
| Work declaration | `WorkPacket.v1` | bounded goal, scope, exclusions, inputs, activation lane, outputs, validation, acceptance criteria |
| Producer lineage | `AgentArtifactMetadata.v1`, canonical hashes and receipts | producer provenance, dependencies, evidence, tests, status; identity is not authority |
| Activation | `ActivationRequest`, `ActivationEvaluation` | lane, side effects, reversibility, isolation, observability, rollback, credentials, operator controls |

No contract matching `*intervention*.json` was found. The only contract filename
matching `*transition*.json` is the temporal-regime detector and is not semantically
equivalent to an RDI state transition.

## 3. Field-level mapping

### 3.1 InstantiationState

| Required semantic | Reuse | Coverage | Gap or rule |
|-------------------|-------|----------|-------------|
| Construct identity/definition | CFAR `object_id`, `construct`, `construct_status`, `variable_class` | `PARTIAL` | state needs a stable reference to the CFAR packet, not copied definition text |
| Constitutive dimensions | CFAR `dimensions` | `PARTIAL` | names exist; per-dimension values and evidence bindings do not |
| Observation time/window | `EvidenceObject.timestamp`, EvidencePack `time_horizon` | `PARTIAL` | no shared state observation-window shape |
| Per-dimension epistemic label | EvidencePack claim `register`; ClaimObject `status` | `PARTIAL` | labels exist, but no dimension-to-claim binding profile |
| Per-dimension provenance | ClaimObject `evidence_refs`; EvidenceObject provenance/hash | `PARTIAL` | composable by references; cardinality and required linkage are undefined |
| Confidence | ClaimObject `confidence`, EvidencePack `confidence_note` | `PARTIAL` | numeric confidence must not be invented; `NOT_COMPUTABLE` is supported |
| Assumptions | CFAR `assumptions` | `OBSERVED_EXISTING` | reference the CFAR packet or preserve exact assumptions |
| Missing-evidence reason | CFAR route/rationale, EvidencePack answer status | `PARTIAL` | no normalized per-dimension missing-reason field |
| Causal exposure | none verified | `MISSING` | requires `EXOGENOUS`, `ABX_MEDIATED`, `MIXED`, `UNKNOWN` with fail-closed default |
| Aggregate depth | none | `DEFERRED` | remains `NOT_COMPUTABLE`; no aggregate field is justified |

### 3.2 InstantiationTransition

| Required semantic | Reuse | Coverage | Gap or rule |
|-------------------|-------|----------|-------------|
| Prior/later state references | generic IDs/hashes across forecast and settlement | `PARTIAL` | no typed state-reference pair |
| Changed dimensions | ClaimObject statements and SignalGraph relationships | `PARTIAL` | graph can express hypotheses, not a deterministic dimension delta |
| Evidence for change | ClaimObject `evidence_refs`, SettlementVerdict evidence hash | `PARTIAL` | references exist; transition-specific binding is absent |
| Epistemic classification | ClaimObject `status`, EvidencePack `register` | `OBSERVED_EXISTING` | must remain attached to each transition claim |
| Confidence | ClaimObject `confidence` | `PARTIAL` | can be `NOT_COMPUTABLE`; no new formula |
| Conflict handling | TheoryObject conflicting claims; SettlementVerdict conflict summary | `OBSERVED_EXISTING` | detect and preserve, never auto-resolve |
| Causal attribution/exposure | TheoryObject can hold a hypothesis | `PARTIAL` | graph relationship strings cannot enforce the exposure vocabulary or prevent UNKNOWN→EXOGENOUS promotion |
| Deterministic transition identity/hash | canonical hash utilities | `OBSERVED_EXISTING` | reusable once a minimal payload is justified |

### 3.3 Intervention

| Required semantic | Reuse | Coverage | Gap or rule |
|-------------------|-------|----------|-------------|
| Bounded goal/target | WorkPacket `goal`, `scope.concepts` | `PARTIAL` | engineering scope is not a domain target/dimension selector |
| Constraints/exclusions | WorkPacket `exclusions`, activation controls | `OBSERVED_EXISTING` | reuse directly |
| Inputs/provenance | WorkPacket `inputs`, AgentArtifactMetadata | `OBSERVED_EXISTING` | producer identity remains provenance only |
| Activation lane | WorkPacket `activation_lane`, ActivationRequest `lane` | `OBSERVED_EXISTING` | activation policy remains sole runtime authority |
| Side-effect declaration | ActivationRequest side-effect and mutation fields | `OBSERVED_EXISTING` | evaluates blast radius, not predicted domain effect |
| Isolation/reversibility/rollback | ActivationRequest control fields | `OBSERVED_EXISTING` | reuse directly |
| Predicted dimension delta | ForecastObject claim | `PARTIAL` | free-text claim cannot bind dimension, direction, baseline, and condition |
| Intervention/no-intervention condition | none verified | `MISSING` | forecast needs explicit condition reference |
| Falsification criteria | WorkPacket acceptance criteria | `PARTIAL` | engineering acceptance is not a domain outcome binding |
| Execution receipt/reference | artifact receipts and hashes | `PARTIAL` | lineage exists; no RDI intervention execution reference profile |

### 3.4 Settlement and contamination

| Required semantic | Reuse | Coverage | Gap or rule |
|-------------------|-------|----------|-------------|
| Forecast binding | SettlementVerdict forecast ID/hash and binding ID/hash | `OBSERVED_EXISTING` | reuse directly |
| Later evidence binding | SettlementVerdict evidence packet ID/hash | `OBSERVED_EXISTING` | reuse directly |
| Decision/status | SettlementVerdict decision and settlement status | `OBSERVED_EXISTING` | reuse directly |
| Reasons/conflicts | SettlementVerdict reasons and conflict summary | `OBSERVED_EXISTING` | contamination may be referenced, but not typed |
| Prediction error | Brier telemetry for binary probabilistic outcomes | `PARTIAL` | only applicable where outcome semantics justify Brier scoring |
| ABX-mediated exposure | provenance links can show Abraxas involvement | `PARTIAL` | no required exposure classification |
| Contamination flag/reason | none verified | `MISSING` | must survive settlement round trip and block independent-confirmation treatment |
| Unknown remains non-exogenous | none enforced | `MISSING` | future contract must default missing exposure to `UNKNOWN`, never `EXOGENOUS` |

## 4. Composition rules for RDI-2

1. Reference existing object IDs and canonical hashes. Do not duplicate full CFAR,
   EvidencePack, Belief Graph, ForecastObject, SettlementVerdict, WorkPacket, or
   activation payloads.
2. Preserve epistemic labels at claim or dimension granularity.
3. Represent an unavailable dimension explicitly as `NOT_COMPUTABLE`; omission is
   not zero, false, or absence of instantiation.
4. Do not add an aggregate Instantiation Depth field.
5. Add no numeric confidence, weight, delta, or reinforcement formula without a
   fixture-backed measurement contract.
6. Causal exposure must be typed and fail closed. Missing or ambiguous exposure is
   `UNKNOWN`, not `EXOGENOUS`.
7. Intervention declaration and activation evaluation remain separate. Neither a
   forecast nor a work packet grants execution authority.
8. SHADOW outputs may identify anomaly or contamination only. FORECAST outputs may
   predict only. Settlement compares later evidence.

## 5. Minimum proven gap for RDI-2

The smallest justified new contract surface is not a subsystem. It is a narrow,
deterministic composition profile capable of binding:

- one CFAR construct reference;
- eight named dimensions, each carrying claim/evidence references and an epistemic
  label or `NOT_COMPUTABLE` reason;
- an observation window;
- a typed causal-exposure value;
- optional prior-state reference for transitions;
- optional forecast, intervention-declaration, and settlement references;
- contamination flags and reasons;
- canonical hash and fail-closed authority locks.

RDI-2 selected a small state/transition pair after adding one state-only, one
no-intervention forecast, and one ABX-mediated intervention settlement requirement
fixture. The fixtures are synthetic contract evidence, not empirical validation.

## 6. RDI-1 result

| Question | Result |
|----------|--------|
| Can existing schemas represent sourced epistemic claims? | `OBSERVED_EXISTING` |
| Can they represent construct definition and assumptions? | `OBSERVED_EXISTING` |
| Can they bind forecasts to settlement evidence? | `OBSERVED_EXISTING` |
| Can they independently encode all InstantiationVector dimensions? | `MISSING` |
| Can they enforce typed ABX-mediated exposure and contamination? | `MISSING` |
| Can activation policy authorize bounded execution without an RDI subsystem? | `OBSERVED_EXISTING` |
| Is a scalar Instantiation Depth justified? | `NOT_COMPUTABLE` |
| Should RDI-1 add a schema now? | No |
