# ABRAXAS v2.5 Codex Custom Instructions

Always follow these when working in this repo. Companion:
[`docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md`](architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md),
`core/operator_loop.py`,
`contracts/engineering/work_packet.v1.schema.json`,
`contracts/engineering/handoff_envelope.v1.schema.json`.

## Central rule

> Producer identity records provenance. It does not grant authority.

`producer_system` tags who produced work. It never grants merge, canon promotion,
deploy, assignment, or execution authority. Schema authority locks stay false:
`producer_identity_grants_authority`, `auto_merge`, `auto_canon_promotion`,
`auto_deploy`, `assignment_authority`, `execution_authority`.

## Before ordinary bounded edits

Follow `AGENTS.md` and `SKILLS.md`: routine single-agent engineering starts as
bounded implementation plus verification. Do not create or require WorkPackets,
seal packets, or approval packets merely because a task is non-trivial.

## When an active WorkPacket is supplied

1. Read `AGENTS.md`, `SKILLS.md`, and the active packet scope for this task.
2. Load the active `WorkPacket.v1` (or packet fields supplied by the operator /
   Hermes). Honor `scope.files`, `scope.concepts`, `exclusions`, and
   `activation_lane`.
3. Inspect peer active packets (`work_state` in `ACTIVE`, `WAITING`, `BLOCKED`,
   `REVIEW`) before touching shared surfaces.
4. Stay inside declared file and concept ownership. Do not expand scope silently.

## Ownership and overlap

- Conflict policy is always `DETECT_CLASSIFY_OPERATOR_DISPOSITION`.
- On `FILE_OVERLAP` (or any semantic/contract conflict) with another active
  packet: **stop editing the contested paths**, classify the conflict, and wait
  for operator disposition. Never auto-resolve ownership collisions.
- Do not claim exclusive ownership of paths outside your packet.
- Never invent a parallel task database; use WorkPacket.v1 / HandoffEnvelope.v1.

## Producer tagging

- Tag durable artifacts and completion notes with `producer_system: CODEX` when
  this session is pure Codex/Cursor work.
- Use `producer_system: MIXED` when integrating or co-authoring with Grok/Hermes
  outputs in the same packet.
- Identity is provenance only — never argue from “CODEX produced it” for merge
  or deploy rights.

## Preferred work (Codex/Cursor)

- Implementation inside existing modules; refactor and consolidation.
- Tests, CI diagnosis, schema/type enforcement, security hardening.
- PR prep, diff verification, and controlled integration of Grok assets into
  canonical repo paths.
- Avoid broad redesign unless repository evidence requires it.

## Validation before handoff

1. Run packet `validation_commands` when provided.
2. Run **targeted tests** for touched surfaces.
3. Run **fast CI** (repo’s usual pre-PR fast path) before declaring complete.
4. Record exact commands, pass/fail, and residual risks. Do not claim green CI
   without evidence.

## Completion: HandoffEnvelope.v1 shape

Every completed (or blocked/partial) delegated packet returns a handoff matching
`contracts/engineering/handoff_envelope.v1.schema.json`. Minimum fields:

```yaml
schema_version: HandoffEnvelope.v1
handoff_id: HO-...
work_packet_id: WP-...
producer_system: CODEX | MIXED
status: COMPLETE | PARTIAL | BLOCKED | NOT_COMPUTABLE
changed_files: []
generated_assets: []
commands_run: []
tests:
  passed: []
  failed: []
observed_findings: []
inferred_findings: []
conflicts_detected:      # objects only — not bare class strings
  - conflict_class: FILE_OVERLAP
    detail: "..."
    subject_ids: [WP-A, WP-B]
residual_risks: []
next_recommended_action: string
authority:               # all grants false; operator_review_on_semantic_conflict true
  producer_identity_grants_authority: false
  auto_merge: false
  auto_canon_promotion: false
  auto_deploy: false
  assignment_authority: false
  execution_authority: false
  operator_review_on_semantic_conflict: true
```

Use helpers in `core/operator_loop.py` (`validate_handoff`, `example_handoff`,
`detect_work_packet_file_overlaps`, `default_authority`) when validating or
drafting packets/handoffs.

## Hard stops (never authorize)

- No production activation or deploy unhold.
- No CLEAR mass deletion.
- No edits to `scripts/operator/__init__.py` unless the active packet explicitly
  owns that path and operator disposition is recorded.
- No merge/canon/deploy from producer identity alone.

## Authority reminder

```text
merge / canon / deploy  →  requires evidence + explicit operator approval
producer_system         →  provenance label only
```
