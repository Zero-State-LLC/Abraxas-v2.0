# Post–Operator Hold Clearance — Optional Forks

Advisory routing for continuation work deferred by default after PR #719–#721.

## P132 research canary activation (pilot complete)

**Status:** DROP006A pilot advisory shadow activation implemented via P132 lane.

**Remaining for full unlock:**
- Expand to DROP006B–DROP007C per-candidate operator attestation
- Validated P128→P130 spine replay (attempted 2026-06-18; reverted after P129 degradation — do not regen without operator lane)
- Full production activation requires separate P133+ governed lane

## v2 hygiene Phase 1 stabilization chain

**Default:** Out of scope (`clearance_scope.v2_hygiene_phase1_stabilization_holds=false`).

**Requires:**

- Set master attestation `v2_hygiene_phase1_stabilization_holds=true`
- Normalize operator IDs across v2 payloads (`daniel_meyer` vs `AALM1tch-Daniel-20260616`)
- Walk 10+ intake gates documented in `operator_input/templates/README.md`

## Tier-3 missing-contract pipelines (8 deferred)

**Default:** Spec-first lane per pipeline; no bulk clearance.

**Blocker:** `NO_GOVERNED_SPEC_BINDING_PRESENT` in gap backlog.

## 91-surface bulk hold clearance

**Default:** Not achievable via single attestation. Use P102 compression pattern or phased per-domain intake (as demonstrated by post-2.5.0 edge clearance).

## Operator choice

Select one fork explicitly in master attestation `clearance_scope` or via separate governed operator decision record before implementation begins.
