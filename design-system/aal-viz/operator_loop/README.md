# Operator-loop visual set

Companion to [`docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md`](../../../docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md).

**Rule:** Producer identity records provenance. It does **not** grant authority.

## Contracts and projection (not visual assets)

| Surface | Path / command |
|---------|----------------|
| WorkPacket.v1 | `contracts/engineering/work_packet.v1.schema.json` |
| HandoffEnvelope.v1 | `contracts/engineering/handoff_envelope.v1.schema.json` |
| Runtime helpers | `core/operator_loop.py` |
| Dry-run projection | `python3 scripts/viz/build_aal_viz_operator_loop_projection.py --dry-run-examples --no-console-copy` |
| Agent wiring | `AGENTS.md` (Grok manifests/handoffs); Hermes `skills/abraxas-master-loop-workflow/`; Codex `docs/CODEX_CUSTOM_INSTRUCTIONS.md` + `.cursor/rules/operator-loop-ownership.mdc` |

AAL-Viz **projects** packets and handoffs only; it does not assign work, approve merges, or grant authority.

## Layout

| Path | Contents |
|------|----------|
| `roles/` | Human, Hermes, Grok, Codex/Cursor, GitHub, Notion, CI, AAL-Viz |
| `nodes/` | Work packet, handoff, integration, conflict, operator decision |
| `edges/` | Assignment, peer review, validation, handoff, merge, blocked dependency |
| `badges/` | HERMES · GROK · CODEX · MIXED · HUMAN |
| `work_states/` | ACTIVE · WAITING · BLOCKED · REVIEW · INTEGRATED · SUPERSEDED |
| `diagrams/` | Canonical loop map |

Regenerate: `python scripts/design/generate_aal_viz_operator_loop_assets.py`
