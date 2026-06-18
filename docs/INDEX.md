# ABRAXAS Documentation Index

Primary navigation hub for the repository. **New contributors:** start at [`START_HERE.md`](START_HERE.md).

## Repository overview

| Document | Purpose |
|----------|---------|
| [`START_HERE.md`](START_HERE.md) | 30-minute contributor path |
| [`../README.md`](../README.md) | Architecture, status, workflow |
| [`../STATUS.md`](../STATUS.md) | Operational status |
| [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | PR and development workflow |
| [`../PLANS.md`](../PLANS.md) | Canonical roadmap edge |
| [`../AGENTS.md`](../AGENTS.md) | Agent operating doctrine |
| [`../GOVERNANCE_V3.md`](../GOVERNANCE_V3.md) | Active governance model |

## Subsystem map

| Domain | Code | Docs / artifacts |
|--------|------|------------------|
| Governance / Brier | `core/governance/`, `core/scoring/` | AGENTS.md, MCP graph tools |
| v2 hygiene | `core/sync/`, `abraxas/v2/` | PLANS.md, `out/sync/v2_hygiene_*` |
| Codegen intelligence spine | `core/abx_codegen_*` | [`audits/CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE.md`](audits/CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE.md) |
| Research canary P103–P130 | `core/abx_research_canary_*` | POST_2_5_0 audit (**do not regen spine casually**) |
| Temporal continuity P70–P102 | `core/temporal_continuity_*` | Historical — `docs/plans/P71–P99` |
| Operator narrative P42/P44 | `core/operator_narrative_*` | `out/reports/operator_narrative_*` |
| Runtime integration gate | `core/runtime_integration_*` | Shadow wiring hooks audit |
| Ingest / Oracle Signal | `core/ingest/`, Oracle runners | Shadow/advisory only |
| Geometric / chamfer (v0.1) | chamfer builders | Archived audits |
| Belief graph engine | `core/belief_graph_*` | PR #715 surface |

Full inventory: [`audits/REPOSITORY_ORGANIZATION_INVENTORY_001.md`](audits/REPOSITORY_ORGANIZATION_INVENTORY_001.md).

## Execution surfaces

| Command | Purpose |
|---------|---------|
| `python scripts/run_fast_ci.py` | Pre-PR validation |
| `python scripts/run_canon_resume_state.py` | Continuity pointer |
| `python scripts/run_continuation_frontier_reconciliation.py` | Frontier audit |
| `python scripts/run_artifact_regeneration.py --check-drift` | Artifact drift |

CLI operator layer: [`workflows/cli-operator-layer.md`](workflows/cli-operator-layer.md).

## Governance surfaces

- [`../PLANS.md`](../PLANS.md) — implemented / held / deferred lanes
- [`../AGENTS.md`](../AGENTS.md) — guardrails, canary spine rule
- [`releases/POST_2_5_0_CONTINUATION_AUDIT.md`](releases/POST_2_5_0_CONTINUATION_AUDIT.md) — current baseline
- `out/audit/continuation_frontier_reconciliation_001.latest.json`

## Operator surfaces

- [`../operator_input/README.md`](../operator_input/README.md) — payloads and templates
- [`../operator_input/templates/README.md`](../operator_input/templates/README.md) — template index
- [`notion/GOVERNANCE_V3_NOTION_SYNC.md`](notion/GOVERNANCE_V3_NOTION_SYNC.md) — manual Notion sync
- `out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json`

## Audit surfaces

- [`audits/ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_IMPLEMENTATION_PLAN_001.md`](audits/ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_IMPLEMENTATION_PLAN_001.md) — spec-stack schema audit lane (advisory-only)
- [`audits/AUDIT_INDEX.md`](audits/AUDIT_INDEX.md) — all audit docs classified
- [`audits/DOCUMENTATION_TOPOLOGY_AUDIT_001.md`](audits/DOCUMENTATION_TOPOLOGY_AUDIT_001.md) — entrypoint audit
- [`audits/REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md`](audits/REPOSITORY_ORGANIZATION_SWEEP_001_RECEIPT.md) — sweep receipt

## Artifact surfaces

- [`artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md) — ACTIVE / REFERENCE / ARCHIVED
- [`../core/generated_artifact_registry.py`](../core/generated_artifact_registry.py) — producer registry
- `out/audit/`, `out/operator_review/`, `out/canon_resume_state/`

## Testing surfaces

- [`testing/TEST_INDEX.md`](testing/TEST_INDEX.md) — subsystem test map
- `python scripts/run_fast_ci.py`
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md)

## Release history

- [`releases/RELEASE_INDEX.md`](releases/RELEASE_INDEX.md) — all release/continuation docs
- [`releases/POST_2_5_0_CONTINUATION_AUDIT.md`](releases/POST_2_5_0_CONTINUATION_AUDIT.md) — **authoritative current**
- [`releases/PRODUCT_2_5_0_RELEASE_READY.md`](releases/PRODUCT_2_5_0_RELEASE_READY.md)
- [`releases/VERSION_STRATEGY.md`](releases/VERSION_STRATEGY.md)

## Architecture and roles

| Directory | Purpose |
|-----------|---------|
| [`atlas/ABRAXAS_ATLAS.md`](atlas/ABRAXAS_ATLAS.md) | Master system atlas |
| [`atlas/`](atlas/) | Architecture cards |
| [`operators/`](operators/) | new-operator, contributor, researcher, architect |
| [`workflows/`](workflows/) | CLI operator layer, codebase memory MCP |
| [`plans/`](plans/) | Historical P71–P99 + phase plans |
| [`status/`](status/) | Generated badges, continuity spine JSON |
| [`skills/`](skills/) | Agent skill notes |

## Key subdirectories (legacy table)

| Directory | Purpose | Notable files |
|-----------|---------|---------------|
| `atlas/` | System architecture cards | `ABRAXAS_ATLAS.md` |
| `operators/` | Role-specific guides | `contributor.md`, `new-operator.md` |
| `workflows/` | Development workflow specs | `cli-operator-layer.md` |
| `status/` | Live generated status | `badges.json`, `continuity-spine.json` |
| `audits/` | Audit reports | `AUDIT_INDEX.md` |
| `releases/` | Release continuation | `RELEASE_INDEX.md` |

---

*Updated by Repository Organization Sweep 001 (2026-06-18). Prefer START_HERE → this index → subsystem docs.*
