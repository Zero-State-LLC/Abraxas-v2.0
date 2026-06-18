# Post–Operator Hold Clearance — Optional Forks

Advisory routing for continuation work deferred by default after PR #719–#721.

## P132 research canary activation (high governance cost)

**Default:** Defer until Oracle shadow implementation and runtime shadow wiring lanes prove the per-domain pattern.

**Requires:**

- New P132 lane (schema, builder, runner, receipt) — do not mutate P130 in place
- Code change to relax P131 `_validate_payload` hardcoded `false` booleans
- Validated P128→P130 replay before any `out/research_canary_*` regeneration
- Daniel Meyer per-candidate dispositions in `operator_input/p130_final_activation_operator_decision_payload_001.json`

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
