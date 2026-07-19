# RISK-008 — Fail-closed sole-writer / boundary criteria (draft)

```yaml
risk_id: RISK-008
status: MITIGATING
document: criteria_only
fail_closed_enabled: false
production_activation_authorized: false
drafted_at: 2026-07-19
```

## Current posture

- Sole-writer check: **advisory** in fast-ci (fail-open)
- Boundary check: **advisory**; `ABRAXAS_BOUNDARY_FAIL_CLOSED` **opt-in**, default **off**
- Unauthorized sole-writer findings: **0** (as of post-#971 main re-pin)
- Residual packages: **CLOSED_BY_POLICY** (skills/afe), not deleted

## What fail-closed would mean

If enabled in shared CI:

1. `run_sole_writer_advisory_check.py --fail-closed` (or equivalent) exits non-zero when unauthorized findings > 0  
2. Boundary check with `ABRAXAS_BOUNDARY_FAIL_CLOSED=1` fails on sensitive import / surface violations  
3. Merge to `main` blocked until green  

This is a **product quality promotion**, not a readiness activation.

## Preconditions (all required before operator enables)

| # | Criterion | Measurement |
|---|-----------|-------------|
| 1 | Unauthorized sole-writer = 0 on `main` | `run_sole_writer_advisory_check.py` finding_count=0 |
| 2 | Green window | ≥ N consecutive green `fast-ci` on main (recommend **N=5** scheduled or push runs) |
| 3 | Package policy reviewed | `package_writer_policy.v1` still accurate for skills/afe |
| 4 | Nested runners covered | `scripts/*/run_*` authorized; no false positives in org layout |
| 5 | Escape plan | Document: unset env / revert workflow step; who can flip |
| 6 | Operator dual approval | Written approval (not agent-only) for enabling env in CI |
| 7 | No open P0 sole-writer regressions | Issue tracker / risk board |

## Explicit non-preconditions

- Production activation **not** required  
- Deploy unhold **not** required  
- Full SUPPORTED surface expansion **not** required  
- Notion overall Verified **not** required  

## Rollout recommendation (when approved)

1. **Week 0:** Keep advisory; publish this criteria (done)  
2. **Week 1–2:** Observe green window (criterion 2)  
3. **Week 3:** Optional: enable fail-closed on **PR-only** first (not yet main schedule)  
4. **Week 4+:** Enable on main if PR window clean  
5. **Never** combine with silent production activation  

## Kill switch

```bash
# CI / local
unset ABRAXAS_BOUNDARY_FAIL_CLOSED
# Remove --fail-closed from sole-writer if added to workflow
```

## Decision log

| Date | Decision | Actor |
|------|----------|-------|
| 2026-07-19 | Criteria drafted; **fail-closed remains OFF** | Engineering (DEBUG_PLAN.v2 P2) |

---

*Does not change runtime authority. Does not enable fail-closed.*
