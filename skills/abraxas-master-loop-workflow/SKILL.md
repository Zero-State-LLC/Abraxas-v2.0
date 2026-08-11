---
name: abraxas-master-loop-workflow
description: Use only for Abraxas tasks that require autonomous multi-cycle execution, recursive/self-healing loops, scheduled/proactive campaigns, complex orchestration, or durable loop state. Not the default for bounded engineering.
version: 2.0.0
author: Hermes / Abraxas Governed Operator (appliedalchemylabs)
license: Proprietary
platforms: [macos, linux]
metadata:
  status: SPECIALIZED
  scope: autonomous_loop
  default: false
  authority: specialized_no_authority_grant
  supersedes: [abraxas-jamon-agentic-workflow]
  hermes:
    tags: [abraxas, master-loop, autonomous, loop-engineering, workflow, governance, deterministic, generator-evaluator]
    related_skills: [abraxas-repo-intel, abx-familiar-signal-forager, abx-hermes-skill-evolution]
---

# ABRAXAS MASTER LOOP WORKFLOW

## Purpose

Specialist skill for autonomous campaigns and repeated improvement loops in Abraxas. Use the smallest execution structure that proves the task contract. Escalate here only when the task requires repeated cycles, autonomous continuation, recursive evaluation, scheduled/proactive work, or durable campaign state.

This skill does not grant production, canon, runtime, merge, deploy, CLEAR, or external action authority. `AGENTS.md`, `GOVERNANCE_V3.md`, and `SKILLS.md` remain authoritative.

## Use when

- The user asks for a long-running autonomous campaign.
- The work requires repeated observe -> act -> verify cycles.
- The loop must persist state across sessions or scheduled wakeups.
- A self-healing or recursive improvement process is explicitly in scope.
- Multiple producers or delegated packets require loop-level coordination.
- Independent generator/evaluator passes materially reduce ambiguity or risk.

## Do not use when

- The task is a trivial lookup or direct tool call.
- The task is ordinary bounded engineering that can be proved by code plus tests.
- The task only needs repository mapping; use `abraxas-repo-intel` if helpful.
- The task only needs external evidence acquisition; use `abx-familiar-signal-forager`.
- The task is a deterministic code/doc/schema change with clear acceptance tests.

## MSW loop kernel

Every loop cycle uses the AGENTS.md MSW discipline:

```text
CONTRACT: requested outcome + smallest proof criteria
STATE: current observed state and blockers
SURVIVING CLAIMS: only claims whose deletion leaves the contract unmet or unproven
ACTION: bounded step for one or more surviving claims
VERIFICATION: concrete check proving or refuting the claim
STOP CONDITION: halt when contract is proved, blocked, or not computable
NEXT STATE: only if another cycle is required
```

Delete unnecessary claims before acting. Complexity must reduce ambiguity; if it adds ceremony without proof value, remove it.

## Evidence and forecasts

Preserve `OBSERVED`, `INFERRED`, `SPECULATIVE`, and `NOT_COMPUTABLE` labels for repository state, research conclusions, forecasts, causal claims, readiness, operator decisions, and unsupported assumptions.

Brier scoring is required only for genuine probabilistic forecasts with declared settlement criteria. Do not attach Brier values to deterministic code correctness, docs edits, migrations, refactors, schema work, CI repair, or routine architecture work.

## Generator / evaluator use

Generator/evaluator separation is optional by default and required only when independent evaluation adds real control value:

- autonomous loops;
- ambiguous architecture choices;
- high-risk reasoning;
- research interpretation;
- generated design alternatives;
- multi-agent delegated work.

Prefer objective validation over persona ceremony. Never claim success from self-description alone.

## Multi-agent packet workflow

Use `WorkPacket.v1` and `HandoffEnvelope.v1` only when there is actual producer delegation or peer-agent coordination.

Required contracts:

- `contracts/engineering/work_packet.v1.schema.json`
- `contracts/engineering/handoff_envelope.v1.schema.json`
- `core/operator_loop.py`

Rules:

1. WorkPacket scope must be explicit before delegated producer work.
2. File overlap is detect/classify/operator-disposition only.
3. HandoffEnvelope records evidence, changed files, tests, conflicts, and residual risks.
4. Producer identity is provenance only.
5. Handoff does not grant merge, canon, deploy, assignment, or execution authority.

## Authority boundaries

- Routine engineering starts at Governance V3 Layer 0.
- Local development and sandbox work are allowed when bounded.
- External production remains operator-gated.
- SHADOW detects anomalies/drift and grants no intervention authority.
- FORECAST predicts with settlement criteria and grants no intervention authority.
- Skill evolution produces candidate patches only; active mutation requires operator disposition.

## Minimal loop receipt

When this skill is used, report:

```yaml
contract: "..."
state: "OBSERVED current state"
surviving_claims:
  - claim: "..."
    why_required: "..."
actions:
  - "..."
verification:
  - command: "..."
    result: "PASS|FAIL|BLOCKED|NOT_COMPUTABLE"
stop_condition: "..."
next_state: "only if another cycle is objectively required"
authority:
  production_activation: false
  canon_mutation: false
  runtime_mutation: false
```

## References

- [`../../AGENTS.md`](../../AGENTS.md)
- [`../../SKILLS.md`](../../SKILLS.md)
- [`../../GOVERNANCE_V3.md`](../../GOVERNANCE_V3.md)
- [`../../docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md`](../../docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md)
- [`references/operator-loop-work-packets.md`](references/operator-loop-work-packets.md)
- [`references/loop-types-and-controls.md`](references/loop-types-and-controls.md)
- [`references/generator-evaluator-split.md`](references/generator-evaluator-split.md)
