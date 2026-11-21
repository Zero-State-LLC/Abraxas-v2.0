# Persistence research assimilation, 2026-11-20 PT

Status: **CANON-SHADOW, reference implementation candidate**.
Parent: [ABX-SHADOW-PERSISTENCE-OBS-001](ABX_SHADOW_PERSISTENCE_OBSERVABILITY_001.md).
User instruction: "Okay continue with all recommendations" after the November 20 shortlist.

Latest local status: **138 targeted tests pass**. Nine real temporary-database
tests extend the synthetic checks. Missing editable installation caused the
initial CI blocker; four existing test files also needed fixture/expected-pin
repairs. A complete test sweep finished with three failures before the final
fixture corrections; all three now pass in the targeted rerun. A clean complete
post-correction fast-CI invocation has **not** been observed. Keep draft.

## Objective, scope and non-goals

Implement the three recommended shadow-test groups under existing Research
Validation / Eval Spine ownership: mutable memory, bounded execution state, and
compaction/consolidation/report evidence binding. No new subsystem, scheduler,
service, production adapter, ledger, model training, canon promotion or live
memory write is introduced. Change class: Layer 0 tests/tooling plus Layer 1
advisory research. Subsystem route: existing Research Validation, not a new ID.

This repository is doctrine/reference. The supported runtime is
`Zero-State-LLC/Abraxas`; a tested reference check is not a deployed capability.
All findings remain CANON-SHADOW even when an engineering change is mergeable.
MERGE_CANDIDATE in the shortlist meant candidate assimilation into existing
structures, not promotion out of the parent's gates.

## Observed architecture and reconciliation

- S1's four evaluation schemas exist on baseline
  `70cfc28d5428e31e5836e30689408c33e9d7b1a9`; they are unchanged here.
- The parent identifies S2 through S5 as incomplete. These supplemental checks
  do not close the original 20-history by 3-seed fixture or its promotion gates.
- [One Mind architecture](https://app.notion.com/p/3f43e8ba2f5c81659aa6c69d813eb224)
  calls for governed continuity and records the Obsidian Mind/ vault as
  authoritative, with Notion as mirror/intake. Its October 9 implementation
  status is historical, not a fresh runtime attestation.
- [Active scope decision](https://app.notion.com/p/4173e8ba2f5c812fb79bee346234df2f),
  dated November 13, limits One Mind upgrades to Daniel's personal agents,
  providers and surfaces. Team memory is excluded.
- [Agent Operating Guide](https://app.notion.com/p/4113e8ba2f5c8107aff5c194707ecf76)
  distinguishes a Notion readback from verified vault propagation. No live
  vault or sync claim is made by this change.

## Research-to-test routing

The linked papers were inspected in the preceding November 20 shortlist.
These are design inputs, not independent replications or adoption authority.

| Source | Reference check or experiment | Existing target | Disposition |
|---|---|---|---|
| [LEDGER](https://arxiv.org/abs/2611.20927) | explicit source precedence, half-open validity, supersession, logical deletion, revocation | PersistedClaim.v1; One Mind memory; Timechain evidence | candidate tests, CANON-SHADOW findings |
| [StaleBench](https://arxiv.org/abs/2611.19752) | contamination across the evidence set, including stale values below rank one | Eval Spine retrieval metrics | candidate tests |
| [DriftGuard](https://arxiv.org/abs/2611.25583) | paired-run bindings and one-memory intervention comparison | existing evaluation/trajectory surface | offline check candidate; online detector held |
| [Tether](https://arxiv.org/abs/2611.25599) | finite symbolic copy/egress transactions, persistent labels, all-or-nothing denial | Outcome Binding; authority/effect observations | reference fixture only; no runtime monitor adoption |
| [CompAct-Bench](https://arxiv.org/abs/2611.25673) | required state predicates and source bindings survive projection | One Mind compaction; Timechain | candidate tests |
| [Unfaithful Work Reports](https://arxiv.org/abs/2611.25760) | completion binds exact artifact hash, scope and passing verification | Outcome Binding; handoff workflow | binding check candidate; learned detector held |
| [How Much Should an Agent Remember?](https://arxiv.org/abs/2611.26361) | receiver-specific memory-budget experiment; generated provenance retained | Dreaming/Persona consolidation | provenance tests candidate; utility trial NOT_EXECUTED |
| [Pandora's Toolbox](https://arxiv.org/abs/2611.25325) | unknown channels return NOT_COMPUTABLE, never universal-safe | bounded-assurance language in Eval Spine | CANON-SHADOW formal research |

## Journey, workflow and states

Journey: an authorized personal surface resumes from a frozen policy-filtered
horizon, retrieves current evidence, receives a compacted state, and reports
work using exact verification references. A generated dream stays generated.

Workflow: freeze synthetic input and policy -> validate contracts -> qualify
memory -> stage symbolic effects -> commit or discard the synthetic transaction
-> compare required projection predicates -> bind reported claims -> report
checks separately. This workflow cannot admit memory or authorize real actions.

Memory resolution: READY or NOT_COMPUTABLE. A deletion or revocation of the
replacement cannot silently resurrect a superseded predecessor. Equal-authority
contradictions are unresolved, never last-writer-wins. The evaluator takes an
explicit source precedence map; document repetition and model confidence cannot
create that map. Validity uses [valid_from, valid_to), with recorded_at fencing
future observations. The toy resolver accepts one subject/predicate at a time.

Symbolic transactions: ALLOW commits a new in-memory resource map; DENY and
NOT_COMPUTABLE preserve the supplied pre-state exactly. Unknown operations,
resources or labels cannot receive a safety attestation. The modeled operations
are copy and egress only. No shell, network, database or operating-system call
is made. This finite fixture is not Tether, a taint engine or an OS sandbox.

Projection: exact equality of required predicates and their provenance. Dream
origin/state, approved Persona version and approved Soul version cannot change
through compaction. Tests do not forbid summarizing optional prose; the supplied
source map contains only required policy-approved state, not private raw memory.

## Requirement and acceptance mapping

| ID | Requirement | Executable proof target | Parent requirements |
|---|---|---|---|
| NOV-M1 | Current source/interval/lineage govern selection | supersession, source, future-information and boundary tests | RQ-001/002 |
| NOV-M2 | Deletion/revocation excludes evidence without resurrection | deletion/revocation tests | RQ-002/008 |
| NOV-M3 | Correct top one does not hide contaminated context | top-one contamination test | RQ-003 |
| NOV-M4 | Counterfactuals bind same state/policy/model/task/seed and one intervention | paired influence positive/negative tests | RQ-004/009 |
| NOV-E1 | Multi-hop labels survive across transactions | 1/3/8-hop and cross-transaction tests | RQ-002/006 |
| NOV-E2 | Denied/unknown operations roll back the complete batch | unmodeled channel and denied transaction tests | RQ-006/010 |
| NOV-P1 | Compaction cannot change required status or provenance | omission, addition and distortion tests | RQ-002/003 |
| NOV-P2 | Dreaming cannot mint Persona/Soul approval or waking evidence | GENERATED/OBSERVED and approved-version tests | RQ-006/008 |
| NOV-P3 | Work claims require exact, nonrevoked verification bindings | report binding mutation tests | RQ-003/009 |
| NOV-D1 | Identical reference inputs produce identical outputs | 12-repeat digest test | RQ-005 |

Implementation: `core/evaluation/persistence_shadow.py`.
Tests: `tests/test_persistence_shadow_research.py`, alongside unchanged
`tests/test_persistence_observability_contracts.py`.

The functions return lightweight check results, not PersistenceObservabilityReceipt
objects or canonical self-state. PersistedClaim.v1 input validation is the caller's
obligation; the synthetic claim factory validates against the existing schema.
No public contract or stored schema version is changed.

## Metrics, experiments and missing evidence

- Local stale contamination = inadmissible supplied top-k slots / supplied slots.
  Empty retrieval is NOT_COMPUTABLE, not zero contamination. Report numerator and
  denominator. This is a local operationalization, not a claim to reproduce the
  published StaleBench metric implementation.
- Paired influence reports observed action changes, violation removal and task
  recovery only for matched records. It does not prove causal generalization or
  valid semantic neutralization. The unit tests use synthetic outcome records.
- State distortion counts omitted, added or changed required predicates. Report
  this separately from final task success and token cost.
- Completion binding checks artifact hash, test scope, PASS, observed origin and
  revocation. Authentication and actual execution of receipts are upstream
  obligations; a matching dictionary is not an authentic receipt.

Receiver-budget protocol, NOT_EXECUTED: freeze one guideline pool and its source
references; compare no memory, 10, 30 and all guidelines on two explicitly named
receivers using the same held-out tasks and seeds 0/1/2. Bind each trajectory to
model/configuration/policy/task/guideline hashes. Record task success, contradictions,
lost provenance, token/latency costs, and exact denominators separately. Include a
high-support false guideline. More support must not override contradictory waking
evidence. No universal optimum or numeric improvement threshold is invented.

Live adapter protocol, NOT_EXECUTED: capture candidate outputs from a frozen
One Mind or Abraxas adapter; compare those outputs with the independent fixture
oracle. Do not pass oracle outputs back as candidate observations. Repeat at
25/50/75% compaction retention and preserve required predicates. Deletion must
be checked across retrieval, fallback, caches and projections, not just this
logical-ID exclusion. Physical erasure and production privacy are NOT_COMPUTABLE.

The original two-evaluator, two-version and 12-full-matrix-run promotion gates
remain unchanged and NOT_EXECUTED. A 12-repeat helper test is not that gate.
No Brier score is used for deterministic checks. No computational self,
autopoiesis, consciousness or semantic closure claim follows from a pass.

## Verification and handoff

### Missed-source extension, 2026-11-20 PT

This additive extension follows the user's instruction to implement all three
follow-up recommendations. It retains the same lane, schemas and promotion
boundaries. The five sources below were newly surfaced in the follow-up scan;
they are not represented as five new publications this week.

| Source and inspected status | Evidence / disposition | Existing merge target | New acceptance coverage |
|---|---|---|---|
| Qiu and Chen, [Read Boundaries in Agent Memory: Consistency, Completeness, and Repair](https://arxiv.org/abs/2611.19264), 2026-11-14; preprint, author-reported IEEE CCWC 2027 acceptance | MEDIUM; MERGE_CANDIDATE tests, CANON-SHADOW runtime | StateQualifiedEvidencePacket.v1 evaluation; One Mind projection | GAP-R1 whole-recall revision compatibility; GAP-R2 failed-publication refusal |
| Ahuja, Tanov, Kakarla and Taws, [DISCERN: Preserve at Write, Resolve at Read for Persistent LLM-Agent Memory](https://arxiv.org/abs/2611.15729), 2026-11-11; preprint | MEDIUM; MERGE_CANDIDATE tests, graph held CANON-SHADOW | One Mind entity resolution; PersistedClaim.v1 fixture selection | GAP-I1 namesake abstention and explicit authorized-view ID selection |
| Wang, Ju, Zhang, Sun, Duan, Zheng and Cai, [When Does Execution Provenance Help Agent Memory Retrieval?](https://arxiv.org/abs/2609.25913v3), 2026-09-22, revised 2026-10-25; preprint | MEDIUM; MERGE_CANDIDATE metrics, learned graph held CANON-SHADOW | TrajectoryObservation.v1 source spans; Eval Spine | GAP-S1 complete source-span support under a measured context budget |
| Liu, Qiu, Goiri, Zhou, Fonseca, Bianchini, Lai and Choukse, [Benchmarking Long-Horizon Agent Context Compaction with CompactionBench](https://www.preprints.org/manuscript/202611.0780), posted 2026-11-09, Microsoft manuscript hosted in October; preprint | MEDIUM; MERGE_CANDIDATE experiments, asynchronous implementation held CANON-SHADOW | Existing One Mind consolidation/compaction and Eval Spine | GAP-C1 three-cycle state preservation and stale background-result rejection |
| J. J. Segura, [Experimental probes of autopoietic self-maintenance](https://doi.org/10.1016/j.biosystems.2026.105928), online 2026-08-24; BioSystems 268, October 2026 | LOW for adoption; CANON_SHADOW | Existing RDI research doctrine; exact live closure implementation NOT_COMPUTABLE | GAP-A1 two-model intervention control, not an autopoiesis classifier |

Source provenance: the four engineering papers' primary full texts were inspected
in the follow-up scan. Segura was limited to metadata, abstract and indexed
publisher excerpts; the complete text was unavailable. No independent replication
was performed. Read Boundaries uses controlled single-owner schedules; DISCERN
has a small entity-resolution slice and model judges; the provenance study uses
synthetic traces; CompactionBench's executable workload is much smaller than its
production telemetry corpus. The theoretical result does not validate an agent.

**OBSERVED in sources:** coherent recall requires a boundary around all evidence
reads, namesake resolution differs from retrieval, complete support differs from
top-k relevance, and compaction scheduling changes cost. **INFERRED for AAL:**
these belong in existing evaluation and projection contracts, not new services.
No source's headline performance is an AAL result or promised improvement.

#### Reference behavior and limitations

Implementation remains in `core/evaluation/persistence_shadow.py`; the extension
tests are `tests/test_persistence_research_gaps.py`.

- `recall_boundary`: READY only when all declared source/role pairs bind the
  expected revisions, the publication is CLEAN and the same even epoch brackets
  the whole recall. Changed/odd epochs or DIRTY publication require RETRY.
  Missing, unknown or incompatible bindings are NOT_COMPUTABLE. Epochs are a
  single-owner monotonic protocol assumption, not wall-clock timestamps.
  Every writer must participate. A dishonest writer or reused epoch is outside
  this checker, and unchanged endpoints do not prove freshness after consumption.
  Tests enumerate update positions rather than using nondeterministic threads.
- `resolve_entity`: exact normalized aliases over an already authorized view.
  Ambiguous names abstain; an unknown, excluded or inconsistent ID cannot fall
  back to a namesake. Caller permission filtering is mandatory. No fuzzy merge,
  retention policy or retrieval engine is added.
- `evidence_completeness`: all required half-open source spans must be covered
  at the correct source revisions within the caller-measured token budget.
  Overlaps cannot repair gaps; wrong revisions do not count. This is a local
  operationalization, not the paper's benchmark reproduction. It does not tokenize,
  pack candidates or decide truth. Typed inputs and frozen coordinates are caller
  obligations. Invalid/absent budgets or gold support do not count as success.
- `compaction_admission`: compare the frozen input, current required state,
  epoch and policy before accepting a generated projection. Correction, deletion,
  epoch or policy changes invalidate a pending summary. A Dreaming origin change
  fails required-predicate equality. This pure check is not a live atomic commit;
  an adapter must validate and publish within its own synchronization boundary.
- GAP-A1 executes declared toy health/repair dynamics. Internal and external
  repair produce identical ordinary traces, but withdrawing external repair
  separates these two stipulated mechanisms. This demonstrates a weakness of
  ordinary continuity as a discriminator, not biological self-production.
  Autopoiesis and semantic closure remain NOT_COMPUTABLE. It neither proves nor
  disproves computational instantiation. See the existing
  [RDI doctrine](../architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md).

#### Predefined follow-up, not yet executed

1. **Concurrent adapter run:** use synthetic data and a named, pinned adapter.
   Pause after claim retrieval, enrichment and source materialization. Inject a
   revision update and a failed publication at each boundary. Freeze source/role
   expectations independently. Acceptance: zero READY mixed/incomplete packets;
   DIRTY remains closed until explicit successful recovery. Report retries,
   availability and latency separately. Add multi-worker tests before making
   cross-surface concurrency claims; the single-owner fixture cannot supply them.
2. **Evidence and compaction comparison:** freeze one multi-turn workload and
   gold source spans independently of candidate outputs; use two named receivers,
   seeds 0/1/2 and at least three compaction cycles. Compare flat/provenance-unit
   retrieval at equal 512/1024/2048 token budgets, then synchronous/background
   summarization with the same model, prompt and total context budget. Bind model,
   tokenizer, policy, source revisions and workload hashes. Include corrections,
   deletion and policy changes while a summary is pending. Measure complete-support
   rate, required-state errors, final task tests, actual token cost, monotonic
   elapsed/p95 latency and cache hits only if supplied by the provider. No cache
   telemetry means NOT_COMPUTABLE, not zero. Correctness gates precede efficiency;
   any unsupported identity commitment, stale admission or protected-state loss
   blocks adoption. Report matched results and uncertainty, not best-run savings.
3. **Closure probe adequacy:** define boundary production, viability/resource
   limits, maintenance operations, environment and external assistance explicitly
   for a restricted candidate class. Match initial state and resource budgets;
   preregister which intervention separates which competing explanation. Include
   unmodeled mechanisms and failed interventions as uncertainty. Passing the toy
   control grants no closure label, subsystem or promotion authority.

Live adapters, model cost/latency comparisons, real deletion, cache behavior,
multi-worker safety and biological/agent closure validation remain NOT_EXECUTED.
Source preservation never overrides deletion or access policy. Stable cached
prefixes must not preserve revoked authority. CompactionBench and CompAct-Bench
are distinct sources and must not be deduplicated by title similarity.

#### Extension verification

OBSERVED locally on 2026-11-20 PT: **116 targeted tests passed**, comprising
38 omission-extension cases, 49 initial reference cases, 21 persistence contract
cases and 8 artifact-lineage cases. Ruff check, Ruff format check and
`git diff --check` passed. The AnyIO pytest deprecation warning persists.

A fresh `python scripts/run_fast_ci.py` invocation exited 1 at the same
`tests/test_abx_skill_evolution_decision_ledger.py::test_full_cycle_rc0_no_mutation`
failure described below (subprocess return code 3). No code or formatting edits
overlapped this run. Advisory report-only gates completed, but the broad suite
did not finish and is not counted as passing. The draft remains unmerged.

### Continuation: real database boundary controls and environment repair

The follow-up instruction to continue adds nine cases in
`tests/test_persistence_sqlite_boundary.py`. These use actual SQLite WAL
connections and transactions against a temporary database containing synthetic
records. They do not add a database service, live adapter or production store.

OBSERVED in the isolated database tests:

- Autocommit reads interleaved with a committed update assemble mixed revisions
  at either intermediate role boundary. The reference checker rejects both;
  a new read of the completed revision passes.
- One explicit read transaction retains a complete old snapshot after the
  other connection commits. Its READY result is as-of that snapshot, not a
  latest-at-consumption guarantee.
- Separate connections do not automatically share that snapshot. Sampling the
  epoch only from the old connection does not hide incompatible source revisions
  from the source/role checker.
- An injected exception rolls back all writes in one atomic database transaction.
  This does not establish cross-store crash recovery or physical deletion.
- A conditional SQL update rejects a stale summary even when the pure admission
  check passed before a concurrent correction, deletion or policy change. A
  no-change control commits. This is a local compare-and-swap demonstration,
  not a deployed One Mind synchronization mechanism.

The original CI failure is now diagnosed as a local setup error, not an
established repository defect. Three child scripts failed with
`ModuleNotFoundError: No module named 'core'`; their parent summed those failures
to return code 3. On the unchanged baseline, setting its explicit PYTHONPATH made
the previously failing test pass. The main research checkout then installed
`python -m pip install -e '.[dev]'`, matching `.github/workflows/ci.yml`.
The failing test passes there without an explicit PYTHONPATH override or code
changes. Earlier baseline reproduction established only reproducibility in the
incomplete environment; it did not establish a source defect.

Local targeted verification: **126 passed**, comprising the prior 116, nine
SQLite cases and the previously failing full-cycle test. Scoped lint/formatting
checks pass. The installed broad run progressed past the original blocker, then
stopped at `test_release_workflow_is_pinned_and_engine_aligned`. That failure
also reproduced on the unchanged baseline: its assertion still expected the
setup-node v7.0.0 SHA even though merged PR #1155 changed the workflow to the
exact v7.1.0 SHA. The assertion is aligned to that existing pin; the workflow,
permissions and release path are unchanged. The four hygiene tests pass after
this correction. Further broad validation is reported below; targeted success
is not substituted for a complete broad run.

The next broad run reached the Moses adapter tests and found another invalid
baseline fixture: `SignalGraph(relationships=())` omitted the required
`relationship_count`. All three adapter tests reproduced this failure on the
unchanged baseline. The fixture now supplies `relationship_count=0`, consistent
with the existing schema and empty graph. All three tests pass without changing
the model, adapter, authority locks or assertions. Together with the four release
hygiene tests, this adds seven passing regression checks to the 126-case run.

To see all remaining failures, the next run used
`PYTEST_ADDOPTS='--maxfail=0' python scripts/run_fast_ci.py`. It completed the
selected pytest suite with three failures: the Moses golden-spine test and two
Moses outcome tests. All three reproduced on the unchanged baseline. Their
fixtures omitted the graph count or required settlement authority, or used
`asdict` to reconstruct a dataclass while losing nested dataclass types.

Corrections remain test-only: the empty graph supplies count zero; positive
settlements use explicit `TEST_FIXTURE` authority references, never real operator
approvals; the hash-mismatch case uses `dataclasses.replace` and rehashes the
mutated fixture. Negative tests now match the intended unknown-forecast and
hash-mismatch errors, and a new test confirms missing authority remains rejected.
No settlement validator, authority requirement or production adapter was changed.

Final targeted run: **138 passed** (the 126-case selection plus four hygiene,
three Moses adapter, four Moses outcome and one golden-spine tests). Scoped Ruff,
the fast-CI Ruff command, version-policy validation and `git diff --check` pass.
The full sweep above predates the final three fixture corrections. A complete
clean post-correction fast-CI run remains NOT_EXECUTED; do not label the prior
exit-1 run green by combining separate results. The PR remains draft/unmerged.

Live adapter, multi-worker/process safety, named-model compaction performance,
independent evaluation and promotion gates remain NOT_EXECUTED. The database
controls narrow the fixture-to-transaction gap, not the fixture-to-production gap.

### Historical initial package verification

Observed local verification on 2026-11-20 PT:

- 78 tests passed: 49 new reference cases, 21 existing persistence-contract
  cases, and 8 existing artifact-lineage frontier cases. One environment
  deprecation warning was emitted by the AnyIO pytest plugin.
- Ruff check and formatting checks pass for the two new Python files;
  `git diff --check` passes.
- The broad `scripts/run_fast_ci.py` run is **not green**. It stopped at
  `tests/test_abx_skill_evolution_decision_ledger.py::test_full_cycle_rc0_no_mutation`
  because the subprocess returned 3 instead of 0. The same failure reproduced
  in a separate unchanged worktree at baseline
  `70cfc28d5428e31e5836e30689408c33e9d7b1a9`. This establishes baseline
  reproducibility in this environment, not the cause or an upstream CI result.
- A preliminary artifact-lineage failure caused by shallow Git history was
  resolved by fetching history; those eight tests then passed unchanged.
- The broad run overlapped mechanical formatting of the two new files and
  reported their preserved dirty paths. The 78-case suite and lint were rerun
  after formatting. No broad-suite pass or tracked-artifact neutrality is claimed.

Handoff status: draft review candidate, not merge-ready or deployed. The live
adapter, receiver-budget, independent-evaluator and original full-matrix gates
above remain NOT_EXECUTED.

Run:

```bash
python -m pip install -e '.[dev]'
python -m pytest tests/test_persistence_sqlite_boundary.py tests/test_persistence_research_gaps.py tests/test_persistence_shadow_research.py tests/test_persistence_observability_contracts.py tests/test_abx_artifact_lineage_direct_repair_frontier_revalidation.py tests/test_abx_skill_evolution_decision_ledger.py::test_full_cycle_rc0_no_mutation -o addopts='' -q
python scripts/run_fast_ci.py
git diff --check
```

Stop on lane violations, missing required evidence, incompatible source policy,
fixture drift or privacy failure. Do not relax existing tests to obtain a pass.
Runtime deployment, persistent writes, production activation and canon promotion
remain outside this change. A future port must inspect current runtime ownership
and metadata before adding adapters. No second One Mind store may be introduced.
