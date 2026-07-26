# Abraxas Multi-Agent Operator Loop 001

**Status:** Architecture specification  
**Scope:** Human operator, Hermes, Grok, Codex/Cursor, GitHub, Notion, CI, and AAL-Viz  
**Authority:** Engineering responsibility and routing model only  
**External production authority:** Not granted

## Purpose

Define one coherent operator-governed engineering loop for Abraxas so Hermes, Grok, Codex/Cursor, Notion, GitHub, CI, and AAL-Viz have explicit responsibilities and do not duplicate authority or create parallel architectures.

The agents are **peer producer systems**, not independent authorities. Producer identity records provenance; it does not grant canon, merge, execution, forecast, or deployment authority.

## Existing architecture mapping

```text
Human Operator
    │ intent, constraints, decisions
    ▼
Operator Loop / Work Router
    │
    ├── Hermes Orchestrator
    │     ├── context acquisition
    │     ├── task decomposition
    │     ├── research/tool routing
    │     ├── cross-agent continuity
    │     └── completion synthesis
    │
    ├── Grok Producer
    │     ├── broad architecture exploration
    │     ├── divergent solution generation
    │     ├── design and visual production
    │     ├── large implementation batches
    │     └── independent second-pass critique
    │
    ├── Codex/Cursor Producer
    │     ├── repository-grounded implementation
    │     ├── precise refactoring and consolidation
    │     ├── tests, static analysis, CI repair
    │     ├── diff-scoped verification
    │     └── PR-ready code changes
    │
    ├── GitHub
    │     ├── implementation truth
    │     ├── branch and PR state
    │     ├── CI and review evidence
    │     └── merge history
    │
    ├── Notion
    │     ├── architecture and ownership map
    │     ├── durable specifications
    │     ├── registered subsystem state
    │     └── operator decision context
    │
    ├── CI / Validation
    │     ├── deterministic tests
    │     ├── schema validation
    │     ├── lint and type checks
    │     └── security and drift checks
    │
    └── AAL-Viz
          ├── work-state projection
          ├── lineage and handoff visualization
          ├── blocker and conflict display
          ├── validation evidence display
          └── operator review surface
```

## Authority hierarchy

| Layer | Responsibility | Authority |
|---|---|---|
| Human operator | Intent, priorities, conflict disposition, merge/deploy decisions | Final operator authority |
| Repository contracts and tests | Behavioral and structural truth | Technical evidence |
| GitHub | Current implementation and merge truth | Implementation source of truth |
| Notion | Architecture, ownership, durable specifications | Architecture source of truth |
| Hermes | Orchestration, routing, continuity, synthesis | No independent canon or merge authority |
| Grok | Peer production, design, exploration, independent implementation | No independent canon or merge authority |
| Codex/Cursor | Peer production, precise implementation, verification | No independent canon or merge authority |
| AAL-Viz | Projection and operator comprehension | No assignment, execution, or approval authority |

## Agent responsibility model

### Human Operator

**Owns**

- goal definition;
- priority ordering;
- acceptable risk and scope;
- semantic conflict disposition;
- canon promotion decisions;
- final merge and external production decisions.

**Must not be replaced by**

- agent confidence;
- majority vote;
- newest implementation;
- automated visual status;
- generated approval artifacts.

### Hermes — Orchestration and continuity

Hermes is the default **work router and continuity coordinator**.

**Primary responsibilities**

- load canonical context from Notion and repository docs;
- resolve current repository, branch, PR, and CI state;
- decompose goals into bounded work packets;
- assign packets according to agent specialization;
- prevent duplicate work;
- track dependencies and handoffs;
- gather completion evidence;
- present unresolved conflicts to the operator;
- update status surfaces after verified changes.

**Hermes should not**

- act as a second runtime kernel;
- create a parallel task database when GitHub/Notion already own state;
- silently resolve architectural conflicts;
- approve its own work;
- treat agent identity as authority;
- generate ordinary-development authorization chains.

### Grok — Divergent producer and visual/design specialist

Grok is the preferred producer for work benefiting from broad exploration, visual synthesis, or independent alternative generation.

**Preferred work**

- visual asset families and design-system exploration;
- architecture alternatives and large conceptual maps;
- broad code-generation batches with explicit contracts;
- UI/UX variants;
- adversarial second opinions;
- discovery of missing surfaces and creative integration options;
- external research when current sources are required.

**Grok output requirements**

- preserve existing contracts and architecture;
- tag durable artifacts with `producer_system: GROK`;
- distinguish implemented work from product vision;
- provide file manifests and integration notes;
- avoid overlapping an active Codex/Cursor work packet;
- return generated visual assets through the asset manifest and QA pipeline.

### Codex/Cursor — Convergent implementation and verification specialist

Codex/Cursor is the preferred producer for repository-grounded changes where precision, dependency tracing, tests, or controlled consolidation matter most.

**Preferred work**

- implementation inside existing modules;
- refactoring and code consolidation;
- migration of duplicate paths;
- test creation and repair;
- CI diagnosis;
- schema and type enforcement;
- security review and hardening;
- PR preparation and diff verification;
- integration of Grok-generated assets or code into canonical repository locations.

**Codex/Cursor output requirements**

- read `AGENTS.md` and canonical architecture first;
- inspect active peer work before editing overlapping surfaces;
- tag durable artifacts with `producer_system: CODEX` or `MIXED`;
- run targeted tests followed by fast CI;
- report exact commands, failures, and residual risks;
- avoid broad redesign unless repository evidence requires it.

## Task routing matrix

| Work type | Primary | Secondary / verifier | Operator gate |
|---|---|---|---|
| Goal decomposition and dependency routing | Hermes | Codex/Cursor checks repo feasibility | Only for scope conflict |
| Current repository-state analysis | Codex/Cursor | Hermes synthesizes | No routine gate |
| Architecture exploration | Grok | Codex/Cursor validates feasibility | Operator chooses material tradeoffs |
| Architecture consolidation | Codex/Cursor | Grok adversarial review | Operator resolves semantic conflicts |
| Visual asset production | Grok | Codex/Cursor integrates and validates | Operator approves visual direction |
| Design-system implementation | Codex/Cursor | Grok visual QA | Operator approves breaking changes |
| UI/UX alternatives | Grok | Hermes routes, Codex validates | Operator selects direction |
| Feature implementation | Codex/Cursor | Grok second pass when useful | Normal PR review |
| Large parallel implementation batch | Hermes routes | Grok and Codex on non-overlapping packets | Operator resolves collisions |
| Test and CI repair | Codex/Cursor | Hermes tracks blockers | No routine gate |
| External research | Grok or Hermes research worker | Codex verifies implementation impact | Operator only for strategic claims |
| Notion architecture update | Hermes | Codex validates repo evidence | Operator for canon changes |
| GitHub PR creation and merge prep | Codex/Cursor | Hermes summarizes | Operator controls merge policy |
| Production deployment | Dedicated deployment workflow | All agents advisory | Explicit operator approval |

## Canonical operator loop

```text
1. INTAKE
   Operator supplies goal, constraints, and desired outcome.

2. CONTEXT LOAD
   Hermes reads engineering context, relevant Notion canon, AGENTS.md,
   repository status, open PRs, active branches, and CI state.

3. CLASSIFY
   Work is classified by domain, risk, activation lane, and required evidence.

4. DECOMPOSE
   Hermes creates bounded work packets with explicit ownership and no overlap.

5. ROUTE
   Grok receives divergent/design/research packets.
   Codex/Cursor receives convergent/implementation/verification packets.

6. PRODUCE
   Agents work independently within declared file and conceptual boundaries.

7. VALIDATE
   Repository-native tests, schema checks, lint, types, security, and visual QA run.

8. RECONCILE
   Hermes compares outputs, detects overlap and contradiction, and routes conflicts.

9. OPERATOR REVIEW
   Only unresolved semantic, architectural, governance, or deployment decisions
   require operator disposition.

10. INTEGRATE
    Codex/Cursor performs controlled integration into the canonical repository.

11. SEAL
    GitHub records implementation evidence; Notion is updated to verified state;
    AAL-Viz projects outcome, lineage, blockers, and remaining work.

12. CONTINUE OR CLOSE
    Hermes emits the next bounded work packet or closes the loop.
```

## Work packet contract

Every routed packet should contain:

```yaml
work_packet_id: WP-...
goal: string
producer_system: HERMES | GROK | CODEX | MIXED
primary_agent: string
secondary_reviewer: string | null
scope:
  files: []
  concepts: []
exclusions: []
inputs:
  notion_pages: []
  repository_paths: []
  source_artifacts: []
activation_lane: LOCAL_DEV | SANDBOX | INTERNAL_CANARY | EXTERNAL_PRODUCTION
expected_outputs: []
validation_commands: []
acceptance_criteria: []
dependencies: []
conflict_policy: DETECT_CLASSIFY_OPERATOR_DISPOSITION
handoff_target: string
```

## Handoff contract

Every completed packet must return:

```yaml
work_packet_id: WP-...
producer_system: GROK | CODEX | MIXED
status: COMPLETE | PARTIAL | BLOCKED | NOT_COMPUTABLE
changed_files: []
generated_assets: []
commands_run: []
tests:
  passed: []
  failed: []
observed_findings: []
inferred_findings: []
conflicts_detected: []
residual_risks: []
next_recommended_action: string
```

## Conflict and overlap policy

Use:

```text
Detect → Classify → Operator disposition
```

Conflict classes:

- `FILE_OVERLAP`
- `CONTRACT_CONFLICT`
- `ARCHITECTURE_CONFLICT`
- `SEMANTIC_CONFLICT`
- `TEST_EVIDENCE_CONFLICT`
- `SOURCE_TRUTH_CONFLICT`
- `VISUAL_LANGUAGE_CONFLICT`
- `SCHEDULE_OR_DEPENDENCY_CONFLICT`

Automatic resolution is permitted only for mechanical, evidence-unambiguous conflicts such as formatting or branch rebasing where behavior is unchanged. Semantic and architectural conflicts must not be resolved by agent voting.

## AAL-Viz mapping

AAL-Viz projects the operator loop but does not run it.

### Required visual surfaces

- operator-loop topology;
- active work packets by producer;
- agent specialization and current assignment;
- file/concept ownership boundaries;
- dependency graph;
- handoff queue;
- validation status;
- conflict and overlap matrix;
- operator decisions pending;
- merged/integrated outcomes;
- lineage from request to PR/commit/Notion update;
- producer attribution without authority implication.

### Required AAL-Viz asset additions

- Human Operator glyph;
- Hermes Orchestrator glyph;
- Grok Producer glyph;
- Codex/Cursor Producer glyph;
- GitHub implementation-truth glyph;
- Notion architecture-truth glyph;
- CI validator glyph;
- AAL-Viz projection glyph;
- work packet node;
- handoff node;
- integration node;
- operator decision node;
- conflict node;
- peer-review edge;
- assignment edge;
- handoff edge;
- validation edge;
- merge edge;
- blocked dependency edge;
- mixed-producer badge;
- active, waiting, blocked, review, integrated, and superseded work states.

Agent marks must be functional system-role glyphs, not anthropomorphic mascots by default. Third-party product logos should not be required for semantic comprehension.

## Repository placement

This specification maps to existing surfaces rather than creating a new runtime subsystem:

| Concern | Existing placement |
|---|---|
| Agent doctrine | `AGENTS.md` |
| Architecture | `ARCHITECTURE.md`, `docs/architecture/` |
| Work orchestration skills | `skills/abraxas-master-loop-workflow/` and related workflow skills |
| Conflict detection | `core/conflict_scan.py`, conflict-report workflow |
| Producer metadata | existing `producer_system` fields and artifact metadata |
| Implementation evidence | GitHub commits, PRs, CI |
| Architecture state | Notion Master System, Engineering Context, ownership map |
| Visual projection | `apps/aal-viz-live-console/` |
| Visual asset backlog | `docs/design/AAL_VIZ_VISUAL_ASSET_GAP_INVENTORY_001.md` |

No new orchestration database, agent authority layer, or parallel runtime kernel is authorized by this document.

## Implementation sequence

1. **DONE** — Add role and work-packet assets to the AAL-Viz Batch 0 backlog (`design-system/aal-viz/operator_loop/`, #1033).
2. **DONE** — Formalize JSON Schema for work packet and handoff envelopes (`contracts/engineering/work_packet.v1.schema.json`, `handoff_envelope.v1.schema.json`).
3. **DONE** — Read-only AAL-Viz operator-loop projection adapter (`core/operator_loop.py`, `scripts/viz/build_aal_viz_operator_loop_projection.py`).
4. **DONE (partial)** — Work-packet file-overlap detection in `core/operator_loop.detect_work_packet_file_overlaps` (advisory; operator disposition required). Full integration into legacy `core/conflict_scan.py` pipelines remains optional.
5. **DONE** — Tests prove producer identity does not affect authority decisions (`tests/test_operator_loop_contracts.py`).
6. **DONE** — Hermes workflow skill emit/consume of shared packet shape (`skills/abraxas-master-loop-workflow/SKILL.md` §3b; `skills/abraxas-master-loop-workflow/references/operator-loop-work-packets.md`; links `core/operator_loop.py` + WorkPacket.v1 / HandoffEnvelope.v1 schemas).
7. **DONE** — Codex/Cursor prompts honor packet ownership boundaries (`docs/CODEX_CUSTOM_INSTRUCTIONS.md`; `.cursor/rules/operator-loop-ownership.mdc`; WorkPacket.v1 scope + HandoffEnvelope.v1 completion; producer identity provenance-only).
8. **DONE** — Grok/AGENTS handoff and manifest requirements (`AGENTS.md` Projection / multi-agent + Grok Build section; `design-system/aal-viz/operator_loop/README.md` contracts + projection pointer; dry-run `python3 scripts/viz/build_aal_viz_operator_loop_projection.py --dry-run-examples --no-console-copy`).
9. **DONE** — Project GitHub/Notion/CI evidence in AAL-Viz (`core/operator_loop.build_truth_surfaces` / `collect_local_truth_surfaces`; projection `truth_surfaces`; builder evidence dir `out/operator_loop/evidence/`; live gatherer `scripts/viz/gather_operator_loop_github_ci_evidence.py`; live-console `OperatorLoopProjectionPanel`).
10. **DONE (standing rule)** — Assignment and approvals remain outside AAL-Viz (`authority.assignment_authority` / `approval_authority` forced false; panel displays only).

## Acceptance criteria

- Hermes, Grok, and Codex/Cursor responsibilities are non-overlapping by default.
- Every durable output records producer provenance.
- Producer identity never grants authority.
- Work packets declare file and concept ownership.
- Active overlaps are visible before integration.
- Tests and contracts decide mechanical correctness.
- The operator decides semantic and architectural conflicts.
- GitHub remains implementation truth.
- Notion remains architecture and ownership truth.
- AAL-Viz remains projection-only.
- External production remains operator-gated.
