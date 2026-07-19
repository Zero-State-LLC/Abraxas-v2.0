# Visual OS + readiness track — merge readiness notes

Branch: `chore/ws0-baseline-live-receipt` · PR #971

## What this PR carries (engineering)

1. **Production-candidate readiness package** under `out/production_readiness/`  
   - Unauthorized sole-writer = 0  
   - CANDIDATE_APPROVED · deploy_held  
   - Activation DENIED · deploy NO_GO  
2. **Abraxas Visual Operating System** under `design-system/` (phases 1–9 + Phase 10 spec)  
3. **aal-viz console** token bridge, topology palette, light/dark theme toggle  

## Merge criteria (engineering)

| Check | Expectation |
|-------|-------------|
| check-organization | pass |
| validate-commits | pass |
| dependency-review | pass |
| aal-viz-console | pass |
| security-scan | pass |
| fast-ci | pass (allow long runtime; avoid force-push/cancel storms) |
| CodeQL | pass / no new critical |

## Explicit non-merge criteria

Do **not** block merge on:

- Notion overall NOT_READY (honest)  
- Deploy NO_GO / activation DENIED (by design)  
- Soft-CI residual accepted  
- Figma file not yet published (Phase 10 is spec-only)  

## Operator post-merge (optional)

1. Publish Figma library per `PHASE10_FIGMA_EXPORT.md`  
2. Deploy unhold only with human plan + attestation  
3. Dual-control activation only with authority token  

## Rollback

Revert PR. No production systems activated by visual OS or readiness artifacts.
