# ABRAXAS AGENT DOCTRINE

## 1. Purpose

This is the constitutional router for agents working in Abraxas-v2.0. It defines authority, startup reads, execution modes, skill routing, evidence standards, and completion semantics. Detailed procedures live in linked domain documents.

## 2. Authority hierarchy

```text
USER TASK
  ↓
AGENTS.md
  ↓
GOVERNANCE_V3.md
  ↓
SKILLS.md
  ↓
selected skills/*/SKILL.md
  ↓
domain architecture / contracts / tests
  ↓
implementation
```

A skill may specialize execution. A skill may not silently override this file, grant itself authority, bypass Governance V3, or reinterpret historical artifacts as current authority. Producer identity is provenance, not authority.

## 3. Mandatory startup

Always read, in order:

1. [`README.md`](README.md)
2. [`STATUS.md`](STATUS.md)
3. [`PLANS.md`](PLANS.md)
4. [`GOVERNANCE_V3.md`](GOVERNANCE_V3.md)
5. [`AGENTS.md`](AGENTS.md)
6. [`SKILLS.md`](SKILLS.md)

Then read only the domain documents required by the task. Historical P70-P130 continuity material, archived operator-review chains, and specialized architecture packets are not routine startup requirements.

## 4. MSW execution kernel

Use the smallest work structure that proves the task contract:

```text
contract ← requested outcome + smallest proof criteria
while ∃ claim c:
    deleting c leaves contract unmet or unproven
    do c
    prove c
halt
report
```

Interpretation: state the contract, define minimal proof, discard unnecessary claims, execute only surviving claims, verify each one, stop when proved, and report evidence plus unresolved uncertainty. MSW reduces ceremony; it is not another process layer.

## 5. Evidence states

Use these labels when making claims about repository state, research conclusions, forecasts, causal claims, readiness, external conditions, operator decisions, or unsupported assumptions:

- `OBSERVED`: directly supported by bound evidence in stated scope.
- `INFERRED`: derived from observations plus declared assumptions.
- `SPECULATIVE`: bounded hypothesis without sufficient observation.
- `NOT_COMPUTABLE`: required evidence, semantics, provenance, or comparability is absent.

Do not fabricate data, sources, test results, benchmarks, or operator decisions. Ordinary code-edit prose does not need a tag unless it makes one of the claim types above.

## 6. Execution routing

Choose proportional execution:

| Mode | Use for | Proof shape |
| --- | --- | --- |
| `DIRECT` | trivial factual lookup or direct tool use | answer/tool result |
| `BOUNDED` | normal single-agent implementation | code → targeted tests → broader validation as needed |
| `OPERATOR_LOOP` | real delegated/peer multi-agent work | `WorkPacket.v1` → producer work → `HandoffEnvelope.v1` |
| `FORECAST` | prediction or probabilistic inference | forecast → settlement criteria → later outcome/scoring |
| `MASTER_LOOP` | long-running autonomous campaigns, recursive improvement, scheduled loops | contract/state/claims/action/verification/stop-condition cycles |

Normal bounded engineering does not require WorkPackets, seal packets, approval packets, or master-loop orchestration.

## 7. Governance and activation boundaries

Governance V3 is authoritative and implementation-first. Every engineering task starts at Layer 0 unless objective evidence shows a higher boundary.

- Layer 0: internal engineering, docs, tests, validators, refactors, tooling.
- Layer 1: advisory architecture, research, SHADOW, prototypes.
- Layer 2: canon-sensitive contracts, accepted truth surfaces, governance definitions.
- Layer 3: externally consequential runtime, deployment, promotion, production activation.

`LOCAL_DEV` and bounded `SANDBOX` work are allowed. `INTERNAL_CANARY` is conditional. `EXTERNAL_PRODUCTION`, public deployment, irreversible external mutation, billing, broad network authority, or user/customer data exposure remain operator-gated.

## 8. Deterministic engineering invariants

Mandatory invariants:

- canonical serialization and stable `canonical_hash` behavior;
- schema validation for contract-bound surfaces;
- artifact lineage and reproducible generator/output relationships;
- deterministic ordering;
- no hidden wall-clock, filesystem-order, random UUID, randomness, or network dependency in deterministic surfaces unless explicitly modeled;
- targeted tests for touched surfaces;
- `python scripts/run_fast_ci.py` or repository-documented equivalent before completion claims;
- exact failure reporting without false success claims.

Language boundary: Python owns evolving semantics; Rust is only for justified stable mechanics. Do not rewrite working Python into Rust without measured need. See [`ARCHITECTURE.md`](ARCHITECTURE.md).

## 9. SHADOW / FORECAST boundary

```text
SHADOW:  detect, classify, and surface anomalies/drift. No causal story invention. No intervention authority.
FORECAST: infer or predict from evidence, declare prediction and settlement criteria, score only after valid settlement. No intervention authority.
```

Do not let SHADOW become implicit forecasting. Do not let FORECAST become activation authority. Brier scoring is for genuine probabilistic forecasts, not routine deterministic code validation.

## 10. Representation-driven instantiation rules

When work concerns simulation, instantiation, hyperstition, or representation effects, follow [`docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md`](docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md). Agent-level invariants:

- representation is not instantiation;
- simulation is neither proof nor disproof of instantiation;
- constitutive properties remain multidimensional;
- causal provenance matters;
- intervention-contaminated outcomes must be marked;
- unsupported dimensions remain `NOT_COMPUTABLE`;
- no unvalidated aggregate score;
- predictions require settlement criteria.

## 11. Multi-agent routing

Use `WorkPacket.v1`, `HandoffEnvelope.v1`, and [`core/operator_loop.py`](core/operator_loop.py) only when there is actual producer delegation or peer-agent coordination. Contract paths:

- [`contracts/engineering/work_packet.v1.schema.json`](contracts/engineering/work_packet.v1.schema.json)
- [`contracts/engineering/handoff_envelope.v1.schema.json`](contracts/engineering/handoff_envelope.v1.schema.json)

Enforce explicit scope, file-overlap detection, no implicit authority escalation, producer identity != authority, and operator disposition on semantic conflicts. Agent handoff alone never grants external production activation, merge, canon promotion, deploy, assignment, or CLEAR authority.

## 12. Skill routing

[`SKILLS.md`](SKILLS.md) is the canonical skill registry/router. Load a skill only when it adds task-specific capability. Do not load a skill merely because it exists. The master-loop skill is specialist-only for autonomous multi-cycle work, not the default for ordinary engineering.

## 13. Validation and completion

Before reporting completion:

1. inspect `git status --short` and relevant diffs;
2. run targeted validation for touched surfaces;
3. run broader validation or fast CI when required by scope;
4. run `git diff --check`;
5. report files changed, commands run, validation results, unresolved risks, and `NOT_COMPUTABLE` items.

If a test or environmental blocker prevents proof, report `PARTIAL` or `BLOCKED` with exact command evidence.

## 14. Historical material

Historical governance, continuity, and operator-review artifacts are preserved for provenance but do not pollute the default execution path. Use them only when the task touches their surface. See [`GOVERNANCE_SIMPLIFICATION_001.md`](GOVERNANCE_SIMPLIFICATION_001.md), [`scripts/README.md`](scripts/README.md), and [`docs/status/HISTORICAL_GOVERNANCE_AGENT_NOTES.md`](docs/status/HISTORICAL_GOVERNANCE_AGENT_NOTES.md).
