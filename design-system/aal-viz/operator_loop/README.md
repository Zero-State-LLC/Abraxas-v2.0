# Operator-loop visual set

Companion to [`docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md`](../../../docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md).

**Rule:** Producer identity records provenance. It does **not** grant authority.

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
