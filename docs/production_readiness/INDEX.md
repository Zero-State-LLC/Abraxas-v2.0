# Production readiness documentation index

Canonical package: [`out/production_readiness/`](../../out/production_readiness/)

| Document | Role |
|----------|------|
| [Production readiness README](../../out/production_readiness/README.md) | Primary readiness overview, quickstart, architecture |
| [Engineering Guidebook](ENGINEERING_GUIDEBOOK.md) | Deep technical / governance / operational guide |
| [CONTINUATION_PLAN.v11](../../out/production_readiness/CONTINUATION_PLAN.v11.md) | **Active** — post-debt hygiene (org + Notion scoped DoD) |
| [CONTINUATION_PLAN.v10](../../out/production_readiness/CONTINUATION_PLAN.v10.md) | Prior — tech debt resolution complete |
| [CONTINUATION_PLAN.v9](../../out/production_readiness/CONTINUATION_PLAN.v9.md) | Prior D4 pure-builder waves |
| [CONTINUATION_PLAN.v8](../../out/production_readiness/CONTINUATION_PLAN.v8.md) | Prior plan (deploy/auth/runbook/docs) |
| [Operator runbook](../../out/production_readiness/ws8/supported_surface_operator_runbook.v1.md) | SUPPORTED surface procedures |
| [Root README](../../README.md) | Repo identity + navigation |
| [START_HERE](../START_HERE.md) | Contributor front door |

## Guardrails

- Evidence states: `Missing | Partial | Verified | NOT_COMPUTABLE`
- Binding decisions live in JSON under `out/production_readiness/ws8/`
- Production activation: **DENIED** unless future operator process says otherwise
- Deploy: **NO_GO** until human plan + unhold

## Validation

```bash
export PATH="$(pwd)/.venv/bin:$PATH"
python scripts/run_production_readiness_docs_crosslink_check.py
```
