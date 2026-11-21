# Persistence research assimilation, 2026-11-20 PT

Status: **CANON-SHADOW, reference implementation candidate**.
Parent: [ABX-SHADOW-PERSISTENCE-OBS-001](ABX_SHADOW_PERSISTENCE_OBSERVABILITY_001.md).
User instruction: "Okay continue with all recommendations" after the November 20 shortlist.

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
python -m pytest tests/test_persistence_shadow_research.py tests/test_persistence_observability_contracts.py -o addopts='' -q
python scripts/run_fast_ci.py
git diff --check
```

Stop on lane violations, missing required evidence, incompatible source policy,
fixture drift or privacy failure. Do not relax existing tests to obtain a pass.
Runtime deployment, persistent writes, production activation and canon promotion
remain outside this change. A future port must inspect current runtime ownership
and metadata before adding adapters. No second One Mind store may be introduced.
