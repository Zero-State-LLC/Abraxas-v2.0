# Abraxas Production Continuation Plan v14

```yaml
program_id: ABRAXAS_PRODUCTION_CONTINUATION
plan_id: CONTINUATION_PLAN.v14
supersedes: CONTINUATION_PLAN.v13
status: ACTIVE
drafted_at: 2026-07-19
branch: main
scripts_organization: COMPLETE
merged_prs:
  - https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/972
  - https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/973
  - https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/974
unauthorized_sole_writer_findings: 0
production_activation_authorized: false
deploy_readiness: NO_GO
activation_gate: DENIED
```

**Scripts organization is complete.** Production activation remains **DENIED**. Deploy remains **NO_GO**.

## Scripts layout (final)

- **709** domain-organized `run_*.py` under `scripts/<domain>/`
- **Root `run_*` keeper:** `scripts/run_fast_ci.py` only
- **Also organized:** `scripts/preflight/`, `scripts/viz/build_aal_viz_*`
- **Root tooling (non-run):** `organize_scripts.py`, `abx_loop.py`, related loop/emitter helpers
- **Status:** `python scripts/organize_scripts.py status` → `complete: true`
- **Guide:** `scripts/README.md`

## Binding authority

| Gate | Status |
|------|--------|
| Activation | DENIED |
| Deploy | NO_GO |
| Sole-writer | 0 unauthorized |

## Recommended next

1. Operator Notion note: organization complete; deploy still held  
2. Optional DEBUG_PLAN.v3 reaudit  
3. Hold trial deploy / activation until operator process  
