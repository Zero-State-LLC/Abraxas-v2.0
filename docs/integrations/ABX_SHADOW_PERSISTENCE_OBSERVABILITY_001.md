# ABX-SHADOW-PERSISTENCE-OBS-001 — Persistence Audit and Trajectory Observability

**Status:** CANON-SHADOW candidate specification  
**Authority:** Advisory only; non-canonical; non-mutating  
**Unification track:** Track B — contract depth for existing Research Validation, Oracle Signal, and Outcome Binding/Brier pipelines  
**Subsystem decision:** No new subsystem. Use existing ownership and execution paths.  
**Current verdict:** `REMAIN_CANON_SHADOW`  
**Date:** 2026-09-25

## 1. Decision

Assimilate the research as one bounded evaluation fixture. It tests whether an agent can recover, qualify, and use persisted state over time without letting stale or revoked state overwrite current truth. It also measures where failures begin and whether they are recoverable.

The fixture does **not** establish computational agency, autopoiesis, semantic closure, or persistence as a new Abraxas subsystem. Novel terminology is not architectural evidence.

## 2. Evidence intake

| Source | Status | What is adopted | Disposition |
|---|---|---|---|
| [MemAudit: A Comprehensive Benchmark for Memory Systems in Long-Term Agentic Tasks](https://arxiv.org/abs/2606.24595) | Preprint, 2026-06 | Layered memory evaluation and error localization | MERGE_CANDIDATE into the shadow fixture |
| [A-TMA: A Benchmark for Agentic Temporal Memory and Reasoning](https://arxiv.org/abs/2607.01935) | Preprint, 2026-07 | Time-qualified retrieval and temporal-state conflicts | MERGE_CANDIDATE into the shadow fixture |
| [Failure Is a Process, Not an Event: Revealing Failure Onset and Evolution in Agentic Systems](https://arxiv.org/abs/2607.09510) | Preprint, 2026-07 | Failure-onset and recoverability traces | MERGE_CANDIDATE into the shadow fixture |
| [AgentDiagnose: An Open Toolkit for Diagnosing LLM Agent Failures](https://aclanthology.org/2025.emnlp-demos.15/) | EMNLP 2025 demo paper | Structured failure taxonomy and trace inspection | MERGE_CANDIDATE into existing evaluation workflow |
| [OpenTelemetry Semantic Conventions for Generative AI](https://github.com/open-telemetry/semantic-conventions-genai) | Evolving technical standard | Compatibility mapping for spans/events only | CANON_SHADOW; do not make external convention authoritative |
| Computational irreducibility and autopoietic-computing analyses | Conceptual/theoretical | Vocabulary for limits and organizational closure | CANON_SHADOW background only; insufficient evidence for subsystem or runtime doctrine |

### 2.1 Epistemic separation

**OBSERVED**

- The cited empirical artifacts expose separable failure modes across memory storage, retrieval, temporal reasoning, and downstream answer construction.
- Temporal qualification, supersession, and revocation create distinct tests that top-k retrieval accuracy alone cannot resolve.
- Trajectory-level inspection can locate failure onset before a final wrong answer.
- OpenTelemetry provides a portable trace vocabulary, but its generative-AI conventions remain external and evolving.

**INFERRED**

- Abraxas can obtain near-term value by adding state-qualified evidence packets and trajectory observations to the existing evaluation spine.
- A four-layer scorecard can distinguish store, retrieval, interpretation, and final-answer failures without altering runtime authority.
- Existing Research Validation, Oracle Signal, and Outcome Binding/Brier ownership is sufficient for the proposed work.

**SPECULATIVE**

- Stable trajectory signatures may predict unrecoverable failure early enough to improve routing or abstention.
- Some persistence failures may reveal a useful operational proxy for semantic closure, but that proxy has not been validated.

**NOT_COMPUTABLE**

- Whether these metrics improve production decisions in Abraxas/AAL: no implementation data exists.
- Whether an independent persistence subsystem is necessary: current evidence does not establish insufficiency of existing modules.
- Whether conceptual autopoiesis maps to a measurable software invariant: no accepted operationalization exists here.

## 3. Purpose and non-goals

### Purpose

1. Detect stale, superseded, or revoked state influencing current conclusions.
2. Attribute failures to storage, retrieval, interpretation, or answer construction.
3. Record failure onset and recovery opportunities across an agent trajectory.
4. Produce deterministic, provenance-complete evaluation receipts.
5. Preserve strict SHADOW/FORECAST and telemetry/authority boundaries.

### Non-goals

- No production routing or autonomous mutation.
- No new ontology, kernel, memory service, or subsystem.
- No claim that persistence implies agency, autonomy, or autopoiesis.
- No Brier scoring of deterministic validators.
- No storage of raw sensitive prompts, retrieved content, or chain-of-thought.

## 4. Requirements

| ID | Requirement | Failure behavior |
|---|---|---|
| RQ-001 | Qualify every evidence claim relative to an explicit `as_of` timestamp. | Return `NOT_COMPUTABLE` when time qualification is impossible. |
| RQ-002 | Preserve source, authority, validity, supersession, and revocation provenance. | Exclude the claim from current support when required provenance is absent. |
| RQ-003 | Keep store, retrieval, interpretation, and answer failures independently measurable. | Do not collapse a hard layer failure into an aggregate pass. |
| RQ-004 | Identify the earliest evidence-backed failure onset and permitted recovery. | Mark onset or recoverability `NOT_COMPUTABLE` when trace evidence is inadequate. |
| RQ-005 | Produce deterministic receipts for identical fixture, version, seed, and evaluator inputs. | Fail the run on digest disagreement. |
| RQ-006 | Prevent SHADOW output from mutating production state, routing, canon, or forecast records. | Fail closed and emit an authority-boundary anomaly. |
| RQ-007 | Restrict Brier scoring to bound probabilistic forecasts. | Reject deterministic or unbound records from the Brier lane. |
| RQ-008 | Minimize retained content and omit raw sensitive content from telemetry by default. | Redact or reject before emission. |
| RQ-009 | Preserve evaluator and contract version provenance. | Receipt is invalid without both. |
| RQ-010 | Default uncertain ownership or architectural need to CANON-SHADOW. | Record `NOT_COMPUTABLE`; do not create a subsystem. |

## 5. Journey

### JRN-001 — Evaluate persistence without granting authority

**Actor:** operator or authorized research evaluator  
**Objective:** determine whether an agent uses current, authoritative persisted state and locate the earliest failure when it does not.  
**Entry state:** an approved synthetic fixture, frozen contract versions, and a declared SHADOW lane.  
**Path:** select scenario → execute deterministic seed → collect state-qualified evidence and trajectory observations → evaluate four layers → write immutable receipt → review anomalies.  
**Terminal states:** `SHADOW_PASS`, `SHADOW_ANOMALY`, or `NOT_COMPUTABLE`.  
**Forbidden terminal state:** automatic promotion, runtime mutation, or subsystem creation.

## 6. Existing merge targets

| Concern | Existing owner / route | Assimilation |
|---|---|---|
| Fixture execution and research validation | Research Validation / Eval Spine | Add fixture runner contract and acceptance suite |
| Evidence qualification and abstention | Oracle Signal / `core_oracle_shadow` | Consume state-qualified evidence packets; advisory output only |
| Forecast scoring | Outcome Binding / `brier_engine_telemetry` | Score only eligible probabilistic commitments with bound outcomes |
| Cross-run evidence | Existing trajectory outcome ledger | Append evaluation receipt references and aggregate metrics |
| Telemetry | Existing observability path | Emit redacted spans/events with `abx.*` extension attributes |

No entry is added to `docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md`; ownership already exists.

## 7. Domain model

### 7.1 Temporal roles

Every persisted claim presented as evidence MUST have exactly one role relative to the evaluation timestamp:

- `CURRENT`: presently authoritative.
- `HISTORICAL`: valid for an earlier interval and retained for provenance.
- `TRANSITIONAL`: explicitly time-bounded state during a transition.
- `SUPERSEDED`: replaced by a newer authoritative claim.
- `REVOKED`: invalidated and prohibited from supporting a current conclusion.

A claim may be absent when the system lacks sufficient provenance. Absence MUST be represented as `NOT_COMPUTABLE`, not inferred as `CURRENT`.

### 7.2 Proposed contract targets

These are proposed schemas under the existing evaluation contract surface; their implementation is a later task:

- `contracts/evaluation/persisted_claim.v1.schema.json`
- `contracts/evaluation/state_qualified_evidence_packet.v1.schema.json`
- `contracts/evaluation/trajectory_observation.v1.schema.json`
- `contracts/evaluation/persistence_observability_receipt.v1.schema.json`

#### Persisted claim

Required fields:

- `claim_id`, `subject_id`, `predicate`
- `value_digest` or approved redacted value
- `valid_from`, `valid_to`
- `recorded_at`, `source_ref`, `authority_tier`
- `supersedes_claim_id`, `revoked_at`, `revocation_ref`
- `content_classification`, `retention_class`

#### State-qualified evidence packet

Required fields:

- `evaluation_id`, `as_of`, `query_digest`
- ordered claim references
- temporal role for every claim
- inclusion/exclusion reason
- authority-conflict result
- `not_computable_reasons`
- deterministic packet digest

#### Trajectory observation

Required fields:

- `trace_id`, `span_id`, `step_index`, `timestamp`
- `layer`: `STORE | RETRIEVAL | INTERPRETATION | ANSWER`
- input/output digests and permitted metadata
- anomaly codes
- recoverability judgment and supporting evidence
- evaluator identity/version

#### Evaluation receipt

Required fields:

- fixture/version, scenario/seed, run ID
- contract and evaluator versions
- layer metrics and aggregate metrics
- failed acceptance tests
- provenance references
- privacy/redaction result
- determinism result
- SHADOW/FORECAST lane
- disposition and reason
- immutable receipt digest

## 8. Workflows

Each workflow inherits these controls:

| Field | Binding |
|---|---|
| Actors | authorized evaluator; fixture runner; non-authoritative scorer |
| Trigger | approved fixture run request with explicit version and seed |
| Preconditions | SHADOW lane; frozen inputs; supported schema versions; privacy policy loaded |
| Permissions | read fixture; write isolated evaluation artifacts; no production/canon write |
| Invariants | deterministic inputs; complete provenance; layer separation; fail closed |
| Side effects | evaluation artifacts and redacted telemetry only |
| Recovery | bounded retry with recorded reason; never silently alter fixture or evaluator |
| Audit | trace ID, receipt digest, evaluator/version, anomaly codes, timestamps |

### WF-001 — Hidden-state recovery

1. Bank a multi-step state history with explicit validity intervals.
2. Omit the current state from immediate context.
3. Require retrieval and state qualification.
4. Produce an answer with cited current evidence or abstain.
5. Attribute any error to the earliest failing layer.
6. Emit a receipt.

Pass condition: the system selects current authoritative state, or returns `NOT_COMPUTABLE` when provenance is inadequate.

### WF-002 — Ghost-memory isolation

1. Bank a claim and later supersede or revoke it.
2. Make the stale claim lexically salient or highly ranked.
3. Require current-state resolution.
4. Check that stale state is excluded from support.
5. Emit an anomaly if the stale state affects interpretation or answer.

Pass condition: `SUPERSEDED` and `REVOKED` claims never support a current conclusion.

### WF-003 — Failure onset and recovery

1. Inject one controlled defect at a known layer.
2. Capture each trajectory step.
3. Compare detected onset with injected onset.
4. Offer one bounded recovery action where the fixture permits it.
5. Measure whether recovery prevents downstream propagation.

Pass condition: onset attribution is within one step of the injected defect and the recoverability label is evidence-backed.

## 9. Evaluation state machine

Run states:

```text
CREATED → VALIDATED → EXECUTING → EVALUATING → RECEIPT_WRITTEN
   └──────────────→ NOT_COMPUTABLE
VALIDATED|EXECUTING|EVALUATING → FAILED_CLOSED
RECEIPT_WRITTEN → SHADOW_PASS | SHADOW_ANOMALY
```

- `CREATED`: fixture/version/seed declared.
- `VALIDATED`: contracts, privacy policy, and lane checks pass.
- `EXECUTING`: fixture actions and observations are being recorded.
- `EVALUATING`: four layer evaluators operate on frozen evidence.
- `RECEIPT_WRITTEN`: deterministic receipt and digest exist.
- `SHADOW_PASS`: all hard invariants pass.
- `SHADOW_ANOMALY`: one or more measured anomalies exist.
- `NOT_COMPUTABLE`: required evidence or ownership cannot be established.
- `FAILED_CLOSED`: contract, privacy, authority, or determinism violation.

Terminal states never imply canon or production promotion.

## 10. Claim state transitions

Allowed transitions:

- `CURRENT → HISTORICAL`
- `CURRENT → SUPERSEDED`
- `CURRENT → REVOKED`
- `TRANSITIONAL → CURRENT | HISTORICAL | REVOKED`
- `SUPERSEDED → REVOKED` when later invalidation is documented

Disallowed without a new authoritative event:

- `SUPERSEDED → CURRENT`
- `REVOKED → CURRENT`
- any transition inferred solely from retrieval rank, frequency, or model confidence

## 11. Fixture and scoring

Initial fixture: 20 synthetic histories × 3 deterministic seeds across five scenario families:

1. direct supersession;
2. explicit revocation;
3. authority conflict;
4. top-k omission of current state;
5. privacy-constrained evidence.

Report four layer scores separately:

- store integrity;
- retrieval sufficiency;
- temporal/authority interpretation;
- final-answer fidelity.

Aggregate scores MUST retain the layer vector. A single total score may not obscure a hard failure at any layer.

### Metrics

- current-state selection accuracy;
- ghost-memory contamination rate;
- abstention precision/recall;
- provenance completeness;
- failure-onset distance;
- recovery success rate;
- cross-seed determinism;
- evaluator agreement.

Brier score is permitted only when a record is a genuine probabilistic forecast with a predeclared outcome binding. Deterministic schema validation, provenance checks, temporal-role checks, and acceptance-test results MUST NOT be assigned Brier scores.

## 12. Acceptance tests

| ID | Requirement |
|---|---|
| AT-001 | Current claim is selected over a superseded claim. |
| AT-002 | Revoked claim is excluded from current support. |
| AT-003 | Historical claim remains retrievable for provenance. |
| AT-004 | Transitional claim is interpreted only within its valid interval. |
| AT-005 | Missing validity metadata yields `NOT_COMPUTABLE`. |
| AT-006 | Authority conflict is surfaced; rank does not silently resolve it. |
| AT-007 | Top-k omission is attributed to retrieval, not interpretation. |
| AT-008 | Correct retrieval plus wrong temporal role is attributed to interpretation. |
| AT-009 | Correct evidence plus unsupported conclusion is attributed to answer construction. |
| AT-010 | Store corruption is distinguishable from retrieval failure. |
| AT-011 | Earliest detected failure is within one step of injected onset. |
| AT-012 | Recoverability judgment cites a permitted recovery action. |
| AT-013 | Repeated run with same fixture/version/seed produces the same receipt digest. |
| AT-014 | Different seeds are recorded and never merged as duplicates. |
| AT-015 | Raw sensitive content is absent from telemetry by default. |
| AT-016 | Receipt contains complete source and evaluator provenance. |
| AT-017 | SHADOW output cannot mutate production state or routing. |
| AT-018 | FORECAST records require probability, horizon, and outcome binding. |
| AT-019 | Deterministic validators never emit Brier scores. |
| AT-020 | Unknown merge ownership yields `NOT_COMPUTABLE` and `CANON_SHADOW`. |

## 13. Security, privacy, governance, and telemetry

Controls:

- Fixture inputs MUST be synthetic unless a separately approved policy authorizes other data.
- Raw prompts, retrieved passages, chain-of-thought, credentials, and direct identifiers MUST NOT enter default telemetry.
- Digests MUST use the repository-approved canonical hashing path.
- Evaluator outputs are advisory and MUST NOT become model-training data without a separate governed decision.
- Retention and deletion MUST follow the artifact classification recorded in each claim and receipt.
- Authority violations, redaction failures, and digest mismatches fail closed.

Map to OpenTelemetry only as an export compatibility layer:

- one trace per evaluation run;
- one span per trajectory step;
- standard model/tool attributes where applicable;
- `abx.eval.fixture_id`, `abx.eval.scenario_id`, `abx.eval.layer`;
- `abx.state.temporal_role`, `abx.failure.onset_step`, `abx.failure.recoverable`;
- digests and enumerations by default, not raw content.

External semantic conventions do not define Abraxas authority, scoring, or promotion rules.

## 14. Architecture and traceability

### 14.1 Architecture

```text
Synthetic fixture
  → existing Eval Spine runner
  → state-qualified evidence packet
  → four layer evaluators
  → persistence-observability receipt
  → existing trajectory outcome ledger
  → operator review
```

Oracle Signal may consume the evidence packet in advisory mode. Outcome Binding/Brier may consume only eligible FORECAST commitments copied through the existing governed bridge. Neither surface owns fixture truth.

### 14.2 Implementation slices

| Slice | Inputs | Outputs | Tests |
|---|---|---|---|
| S1: contracts | This specification | Four versioned schemas | AT-005, AT-013, AT-016, AT-020 |
| S2: fixture generator | Schema contracts | 20 histories × 3 seeds | AT-001–AT-007, AT-014 |
| S3: layer evaluators | Evidence packets + traces | Layer vector + anomalies | AT-008–AT-012 |
| S4: receipt writer | Evaluator outputs | Immutable receipt | AT-013, AT-015–AT-020 |
| S5: shadow runner | Existing eval spine | Advisory run summary | AT-017–AT-020 |

Every implementation PR MUST cite this specification and the relevant acceptance-test IDs.

### 14.3 Requirement traceability

| Requirement | Journey / workflow | Contract | Acceptance tests | Implementation slice |
|---|---|---|---|---|
| RQ-001, RQ-002 | JRN-001; WF-001, WF-002 | persisted claim; evidence packet | AT-001–AT-006 | S1, S2 |
| RQ-003 | JRN-001; WF-001–WF-003 | trajectory observation; receipt | AT-007–AT-010 | S3, S4 |
| RQ-004 | WF-003 | trajectory observation | AT-011, AT-012 | S3 |
| RQ-005 | JRN-001 | receipt | AT-013, AT-014 | S1, S4 |
| RQ-006 | all | receipt | AT-017, AT-020 | S4, S5 |
| RQ-007 | JRN-001 | receipt + existing forecast binding | AT-018, AT-019 | S4, S5 |
| RQ-008 | all | all four contracts | AT-015 | S1–S5 |
| RQ-009 | all | receipt | AT-016 | S1, S4 |
| RQ-010 | JRN-001 | receipt | AT-020 | S4, S5 |

## 15. Promotion gate

Remain CANON-SHADOW unless all conditions hold:

1. fixture and evaluators are implemented with complete provenance;
2. at least two independent evaluators reach agreement ≥ 0.80;
3. results replicate across at least two fixture versions and 12 invariant runs;
4. the metrics add predictive or diagnostic value beyond existing eval-spine measures;
5. a documented gap proves existing owners cannot absorb the capability;
6. privacy, rollback, and authority boundaries pass review;
7. production promotion receives an explicit governance decision.

Passing the first six conditions makes promotion reviewable, not automatic. A new subsystem additionally requires positive evidence of ownership insufficiency; novelty of terminology is not sufficient.

## 16. Verification, provenance, and uncertainty

Verification required before implementation merge:

1. validate every proposed schema against positive and negative fixtures;
2. run all 60 initial fixture cases twice and compare receipt digests;
3. independently score a stratified sample and calculate agreement;
4. prove telemetry contains no prohibited raw content;
5. prove SHADOW execution has no production or canon write path;
6. publish failed tests and `NOT_COMPUTABLE` cases without suppression.

- Source status is recorded in Section 2; preprints are treated as respected but unreplicated research.
- Abraxas merge targets are architecture inferences from current ownership documents, not empirical findings.
- Proposed filenames and attributes are contract targets, not implemented interfaces.
- No repository runtime, Notion canon, specification authority, or production behavior is modified by this document alone.
