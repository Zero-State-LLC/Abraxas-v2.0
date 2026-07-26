# Operator Loop Work Packets (Hermes emit / consume)

**Companion:** `docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md`  
**Runtime helpers:** `core/operator_loop.py`  
**Does not authorize:** production activation, deploy, CLEAR mass deletion, merge/canon authority, or a new task database.

## Central rule

> **Producer identity records provenance. It does not grant authority.**

`producer_system` (HERMES / GROK / CODEX / MIXED / HUMAN) is an audit label only. Authority locks on every packet and handoff force `producer_identity_grants_authority: false` and keep auto-merge / auto-canon / auto-deploy / assignment / execution false. Operator review is required on semantic conflict.

## Schema paths

| Contract | Path |
| --- | --- |
| WorkPacket.v1 | `contracts/engineering/work_packet.v1.schema.json` |
| HandoffEnvelope.v1 | `contracts/engineering/handoff_envelope.v1.schema.json` |

Load and validate via:

- `core.operator_loop.validate_work_packet(payload)`
- `core.operator_loop.validate_handoff(payload)`
- `core.operator_loop.WORK_PACKET_SCHEMA_PATH` / `HANDOFF_SCHEMA_PATH`
- `core.operator_loop.default_authority()` — embed the locked authority object
- `core.operator_loop.example_work_packet(...)` / `example_handoff(...)` — fixtures for dry-run

## Hermes routing role

HERMES is the **default work router**. Hermes:

1. **Emits** a `WorkPacket.v1` before producer work starts (Grok, Codex/Cursor, or mixed).
2. **Routes** only — assignment is orchestration of bounded scope, not merge/canon/deploy authority.
3. **Consumes** a `HandoffEnvelope.v1` when the producer completes (or blocks/partials).
4. **Forbids** overlapping file scope with other **active** peer packets (`ACTIVE`, `WAITING`, `BLOCKED`, `REVIEW`).
5. Never treats producer identity as authority when synthesizing results or recommending next action.

Do **not** invent a parallel task DB, packet format, or authority layer. Use these contracts + `core/operator_loop.py` only.

## WorkPacket.v1 — emit before producer work

Required fields (see schema for types/enums):

| Field | Notes |
| --- | --- |
| `schema_version` | Must be `"WorkPacket.v1"` |
| `work_packet_id` | `WP-...` pattern |
| `goal` | Bounded, verifiable goal string |
| `producer_system` | Provenance only: `HERMES` \| `GROK` \| `CODEX` \| `MIXED` \| `HUMAN` |
| `primary_agent` | Who executes (e.g. `codex-or-cursor`, `grok-build`) |
| `secondary_reviewer` | Peer reviewer or `null` |
| `scope.files` / `scope.concepts` | Ownership boundaries; files must not overlap active peers |
| `exclusions` | Paths/agents must not touch (e.g. `scripts/operator/__init__.py`) |
| `inputs` | `notion_pages`, `repository_paths`, `source_artifacts` |
| `activation_lane` | Prefer `LOCAL_DEV` / `SANDBOX`; production lanes stay operator-gated |
| `expected_outputs` | Concrete paths or artifact names |
| `validation_commands` | Narrowest targeted checks |
| `acceptance_criteria` | Machine-checkable where possible |
| `dependencies` | Other `work_packet_id`s or blocker ids |
| `conflict_policy` | Const: `DETECT_CLASSIFY_OPERATOR_DISPOSITION` |
| `handoff_target` | Where completion goes (e.g. operator review / integration) |
| `work_state` | `ACTIVE` \| `WAITING` \| `BLOCKED` \| `REVIEW` \| `INTEGRATED` \| `SUPERSEDED` |
| `authority` | Locked object from `default_authority()` — never escalate |

Optional: `branch`, `pull_request`, `notes`.

### Emit checklist (Hermes)

1. Decompose the goal into non-overlapping file/concept scope.
2. Call `detect_work_packet_file_overlaps` against **all known active packets** (including this draft).
3. If any `FILE_OVERLAP` finding appears → do **not** start the producer; classify and surface for operator disposition.
4. `validate_work_packet` before recording/routing.
5. Set `work_state` to `ACTIVE` (or `WAITING` if blocked on dependency).
6. Hand the validated packet to the producer; retain the same `work_packet_id` for the handoff.

## HandoffEnvelope.v1 — consume on completion

Required fields:

| Field | Notes |
| --- | --- |
| `schema_version` | Must be `"HandoffEnvelope.v1"` |
| `handoff_id` | `HO-...` pattern |
| `work_packet_id` | Must match the issued WorkPacket |
| `producer_system` | Completing producer provenance (`GROK` \| `CODEX` \| `MIXED` \| `HUMAN`) — not authority |
| `status` | `COMPLETE` \| `PARTIAL` \| `BLOCKED` \| `NOT_COMPUTABLE` |
| `changed_files` / `generated_assets` | Manifest of durable outputs |
| `commands_run` | Exact commands executed |
| `tests.passed` / `tests.failed` | Evidence lists |
| `observed_findings` / `inferred_findings` | Epistemic split |
| `conflicts_detected` | Objects with `conflict_class` + `detail` (+ optional `subject_ids`) |
| `residual_risks` | Open risk strings |
| `next_recommended_action` | Advisory only — not auto-approved |
| `authority` | Same locks; never escalate |

Optional: `branch`, `pull_request`, `notes`.

### Consume checklist (Hermes)

1. `validate_handoff` — reject malformed envelopes.
2. Confirm `work_packet_id` matches the active packet.
3. Treat `producer_system` as provenance only; ignore it for merge/canon/deploy grants.
4. Fold `conflicts_detected` and overlap findings into operator-visible state; do not auto-resolve.
5. Update packet `work_state` toward `REVIEW` / `INTEGRATED` / `SUPERSEDED` only as orchestration bookkeeping — **not** as production activation.
6. Synthesize next WorkPacket or close the loop per operator / stop condition.

## Overlap detection

```python
from core.operator_loop import detect_work_packet_file_overlaps

findings = detect_work_packet_file_overlaps(active_packets)
# findings: list of advisory dicts with conflict_class "FILE_OVERLAP"
# auto_resolve_allowed is always False
```

- Only states in `ACTIVE_OVERLAP_STATES` (`ACTIVE`, `WAITING`, `BLOCKED`, `REVIEW`) participate.
- `INTEGRATED` / `SUPERSEDED` do not conflict.
- Detection is **classify + surface**; disposition is operator-only (`conflict_policy`).

## Authority locks (always)

From `core.operator_loop.AUTHORITY_LOCKS` / `default_authority()`:

| Key | Value |
| --- | --- |
| `producer_identity_grants_authority` | `false` |
| `auto_merge` | `false` |
| `auto_canon_promotion` | `false` |
| `auto_deploy` | `false` |
| `assignment_authority` | `false` |
| `execution_authority` | `false` |
| `operator_review_on_semantic_conflict` | `true` |

`authority_decision_matrix(...)` intentionally ignores `producer_system` for any grant. `producer_grants_authority` is defense-in-depth and must remain false.

## Example validation (local dry-run)

```python
from core.operator_loop import (
    example_work_packet,
    example_handoff,
    validate_work_packet,
    validate_handoff,
    detect_work_packet_file_overlaps,
    producer_grants_authority,
)

wp_a = example_work_packet(
    work_packet_id="WP-hermes-route-001",
    producer_system="CODEX",
    files=["skills/abraxas-master-loop-workflow/SKILL.md"],
)
wp_b = example_work_packet(
    work_packet_id="WP-hermes-route-002",
    producer_system="GROK",
    files=["docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md"],
)
validate_work_packet(wp_a)
validate_work_packet(wp_b)
assert detect_work_packet_file_overlaps([wp_a, wp_b]) == []
assert producer_grants_authority(wp_a) is False

ho = example_handoff(
    handoff_id="HO-hermes-route-001",
    work_packet_id="WP-hermes-route-001",
    producer_system="CODEX",
)
validate_handoff(ho)
```

Optional projection (read-only; no assignment UI):

```bash
python scripts/viz/build_aal_viz_operator_loop_projection.py --dry-run-examples --no-console-copy
```

## Forbidden

- Treating HERMES / GROK / CODEX identity as merge, canon, or deploy authority.
- Starting producer work without a validated WorkPacket.v1.
- Accepting completion without a validated HandoffEnvelope.v1 (or explicit BLOCKED/PARTIAL envelope).
- Overlapping `scope.files` with another active packet without operator disposition.
- Inventing a second packet schema or task database.
- Production activation, deploy unhold, or CLEAR mass deletion from this skill path.
- Creating or relying on `scripts/operator/__init__.py`.
