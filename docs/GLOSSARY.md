# ABRAXAS v2.0 — GLOSSARY

Terms used throughout this codebase. Representation-driven instantiation terms
are grouped first; legacy terms follow in their existing order.

---

**ABX-mediated causation**
A causal exposure in which Abraxas observation, modeling, recommendation, or an
authorized intervention lies on a plausible path between a represented construct
and a later observed transition. The label records exposure, not proof that
Abraxas caused the transition.

---

**Feedback contamination** (also: observer-intervention contamination)
The loss of independence between a forecast and its later evidence because
Abraxas output influenced the environment being measured. Contaminated outcomes
may be settled, but must not be counted automatically as independent confirmation
of the originating model.

---

**Hyperstition**
Representation-driven recursive instantiation. Evidence must indicate that
consequences attributable to the represented construct increase, modify, or
preserve its later capacity for further instantiation. Belief, popularity,
narrative force, correlation, or self-fulfilling appearance alone is insufficient.

---

**Instantiation**
Evidence-backed causal implementation of one or more constitutive properties of a
represented construct. Instantiation is property-specific and may be partial,
regressive, bifurcated, or `NOT_COMPUTABLE`.

---

**InstantiationState**
The independently evidenced state of a represented construct at a specified time,
including provenance, epistemic classification, and unavailable dimensions.

---

**InstantiationTransition**
A provenance-bound change between two InstantiationStates. A transition records
confidence, epistemic classification, and causal exposure without converting
temporal association or correlation into causal attribution.

---

**Intervention**
A declared bounded perturbation with a target, predicted change, constraints,
provenance, activation lane, and falsification or settlement criteria. A declared
intervention does not grant its own execution authority.

---

**Recursive reinforcement**
Evidence-backed preservation, modification, or increase of a represented
construct's subsequent capacity for further instantiation. It is an independent
dimension, not a maturity score.

---

**Representation**
An encoded construct, description, symbol, model, rule, artifact, or executable
form that stands for something. Its presence proves representation only, not
instantiation.

---

**Representation-driven instantiation**
An evidence model in which representation can participate in a traceable chain of
causal access, observable consequence, state transition, settlement, and model
update. It does not assume that simulation implies either instantiation or
non-instantiation.

---

**Settlement**
The post-observation comparison of a declared forecast with later evidence,
including the observed transition, prediction error where computable, conflicts,
and contamination flags. Settlement is not execution authority.

---

**Simulation**
Execution or representation under a model, emulation, fixture, or bounded
environment. Simulation alone proves neither instantiation nor non-instantiation
outside the constitutive properties evidenced by that execution.

---

**Advisory-only**
An artifact or surface that records a decision or plan but does not grant
execution authority. Advisory artifacts can be read and linked by downstream
steps but cannot trigger computation, routing, or mutation on their own.
All current Abraxas artifacts are advisory-only.

---

**Artifact**
A JSON file produced by a runner script and stored under `out/`. Artifacts are
canonical: their content determines their hash, and their hash is verified on
read by any downstream step that binds them.

---

**Authority lock**
A boolean flag in an artifact's `authority_locks` block. `true` means the
artifact permits that scope. `false` means it is hard-blocked — enforced by
both the Python builder and the JSON Schema. Authority locks are inherited from
upstream gates; a step can only unlock what its upstream gate explicitly
authorized.

---

**Blocked scope**
A scope that the current artifact explicitly denies — e.g.
`emits_metric_values: false`. Blocked scopes appear in the `blocked_scopes`
and `authority_locks` blocks and are enforced by schema `const` constraints.

---

**Canon**
The authoritative, sealed set of artifacts and code that have passed
operator review. Promoting something to canon requires an explicit governed
step with operator authorization. Nothing auto-promotes.

---

**Canon hash** (also: canonical hash)
A 64-character hex SHA-256 computed from the canonical JSON serialization of
an artifact (with the `canonical_hash` field itself excluded from the
preimage). Recomputing the hash from a stored artifact and comparing it to the
stored value is the integrity check. Every downstream step that binds an
upstream artifact verifies this hash at build time.

---

**Computation_executed**
An authority lock. When `false` (which it always is in plan and gate phases),
it means no actual computation has been run — only plans and gates have been
defined. Becomes `true` only after an explicit computation implementation step
has been authorized and run.

---

**Decision record**
An artifact that captures a human operator's decision (e.g.
`TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORD_001`). Decision records
are inputs to gate artifacts, which verify the decision-record hash before
proceeding.

---

**Doctrine validator**
`scripts/governance/run_doctrine_validator.py` — runs governance contract checks across
the repo. Its output is the `out/validation/latest.json` artifact. A
`summary_status: ok` means all contracts pass.

---

**Fixture**
A JSON test vector file stored under `input/fixtures/<operator>/`. Fixtures
define the input (e.g. supply/demand/cost_matrix for TRANSPORT) and the
expected output (e.g. `expected_transport_distance`). Fixture files are
created in a separate governed step after the fixture corpus creation plan
is approved.

---

**FORECAST lane**
A projected future authority lane — currently blocked on all artifacts.
`forecast_influence: false` on every artifact. Upgrading from SHADOW to
FORECAST requires a separate governed promotion step.

---

**Gate**
An artifact that explicitly authorizes the next step in a chain (e.g.
`TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE_001`). A gate verifies upstream
artifact hashes, evaluates eligibility conditions, and emits a
`gate_status` that downstream steps check before proceeding.

---

**Governed chain**
A sequence of artifacts where each step binds the hash of its predecessor.
The chain cannot be skipped: if step N's hash is wrong, step N+1 raises
immediately.

---

**Metric operator**
A computation module that calculates a specific distance or similarity metric
(e.g. WASSERSTEIN, CHAMFER, GEODESIC, TRANSPORT). Each operator has its own
artifact chain: authorization → gate → fixture plan → fixture creation →
computation → receipts.

---

**NOT_COMPUTABLE**
A defined outcome for inputs that are structurally invalid for computation but
not schema-invalid (e.g. unbalanced supply/demand for TRANSPORT). The
computation returns `NOT_COMPUTABLE` rather than raising an exception.
NOT_COMPUTABLE branches are enumerated in the gate artifact before any
computation is authorized.

---

**Operator decision**
A human-authored JSON file in `input/` that records a binding operator choice
(e.g. `geodesic_computation_operator_decision.json`). Operator decisions are
read and bound by artifact builders; their content is hashed and included in
the downstream artifact.

---

**P-lane** (also: P-number, P-chain)
A numbered governance lane (e.g. P103, P130). P-lanes are sequential steps
in the canonical roadmap defined in `PLANS.md`. Each P-lane has one or more
artifacts. The current implementation edge is post-P130.

---

**Plan**
An artifact that defines what will be done in a future step without doing it
(e.g. `TRANSPORT_FIXTURE_CORPUS_CREATION_PLAN_001`). Plans bind upstream gate
hashes and enumerate the exact structure of future work. No files are created,
no computation is run.

---

**Production activation**
The step that would make a computation or system live in a production
environment. Currently blocked (`production_activation: false`) on every
artifact. Requires a separate operator-authorized governance design.

---

**Receipt**
An artifact confirming that a governed step completed successfully. Receipts
carry provenance hashes linking them to all prior artifacts in the chain.

---

**Research-canary boundary**
The set of artifacts under `out/research_canary_*/` and `out/research_*/`
(P103–P130). These implement the final activation authorization review chain.
They are sealed. Do not modify or regenerate them without explicit operator
instruction.

---

**Runtime mutation**
Any change to in-flight runtime state (queues, schedules, canon state).
Currently blocked (`runtime_mutation: false`) on every artifact.

---

**Schema version**
A string constant like `TransportFixtureCorpusCreationPlan.v1` that identifies
the artifact type and version. Enforced as a `const` in the JSON Schema.
Changing the schema version creates a new artifact type.

---

**Seal**
The act of finalizing an artifact chain so that its hashes are committed and
no further modification is permitted. Sealed artifacts are referenced by
downstream steps by their exact canonical hash.

---

**SHADOW lane**
The safe, non-authoritative execution context for all current Abraxas work.
SHADOW computations have no effect on production systems, forecasts, or canon
state. All current metric operator work is SHADOW-only.

---

**Spine refresh**
Re-running the temporal continuity spine chain (`run_temporal_continuity_spine_precheck.py`
and downstream scripts). This chain writes to multiple `out/` directories and
must not be run without checking `out/canon_resume_state/latest.json` first.

---

**Test vector**
An input/expected-output pair used to verify a computation implementation.
For TRANSPORT, test vectors consist of (supply, demand, cost_matrix,
expected_transport_distance). Test vectors live in fixture files.
