# P79 — Temporal Continuity Upstream Input Regeneration Authorization Gate (Advisory)

## Scope

P79 is a deterministic advisory-only upstream input regeneration **authorization gate** lane driven strictly by:
`out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json` (P78 output).

This lane **does not**:
- grant authorization
- create authorization tokens
- execute commands
- run generators
- regenerate upstream inputs
- regenerate artifacts
- repair evidence
- mutate canon/runtime/scheduler/forecast state
- claim runtime spine readiness

## Required outputs

- `core/temporal_continuity_upstream_input_regeneration_authorization_gate.py`
- `scripts/temporal/run_temporal_continuity_upstream_input_regeneration_authorization_gate.py`
- `contracts/canon/temporal_continuity_upstream_input_regeneration_authorization_gate.v1.schema.json`
- `tests/test_temporal_continuity_upstream_input_regeneration_authorization_gate.py`
- `out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json`

## Artifact

- `artifact_type = TemporalContinuityUpstreamInputRegenerationAuthorizationGate.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- `authorization_gate_only = true`
- `authorization_granted = false`
- all authority flags hard-locked false, including execution/authorization/generator/upstream-input/artifact-regeneration/spine implementation authority

## Authorization-gate status semantics

| Condition | authorization_gate_status |
|---|---|
| P78 source missing/unreadable/malformed | `NOT_COMPUTABLE` |
| P78 `execution_plan_status = EXECUTION_PLAN_READY` and eligible allowlisted execution steps exist | `AUTHORIZATION_ELIGIBLE` |
| P78 `execution_plan_status = EXECUTION_PLAN_BLOCKED` | `AUTHORIZATION_BLOCKED` |
| P78 `execution_plan_status = EXECUTION_PLAN_NOT_REQUIRED` | `AUTHORIZATION_NOT_REQUIRED` |
| Any inconsistent status combination | `NOT_COMPUTABLE` |

## Authorization doctrine

P79 separates:
- authorization eligibility
- authorization granted
- execution authority

`authorization_eligible` may be true only when P78 is structurally ready for future operator review.

`authorization_granted` is always `false`.

`authorization_authority` is always `false`.

`execution_authority` is always `false`.

`execution_authorized` is always `false` for eligible and blocked execution-step projections.

## Authorization required record

When P79 is eligible, it emits a requirement for a future operator authorization record only:
- `required_record_type = OPERATOR_AUTHORIZATION_TOKEN_V1`
- `required_record_path = out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json`
- `authorization_token_observed = false`
- `authorization_token_hash = NOT_COMPUTABLE`

P79 never creates or observes the token.

## Recommended next-lane logic

| authorization_gate_status | recommended_next_lane |
|---|---|
| `NOT_COMPUTABLE` | `P78_EXECUTION_PLAN_REGENERATION` |
| `AUTHORIZATION_ELIGIBLE` | `P80_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_RECORD_PLAN` |
| `AUTHORIZATION_BLOCKED` | `P80_TEMPORAL_CONTINUITY_EXECUTION_BLOCKER_REPAIR_PLAN` |
| `AUTHORIZATION_NOT_REQUIRED` + degraded evidence | `P80_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN` |
| `AUTHORIZATION_NOT_REQUIRED` + artifact dry-run planning route | `P80_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN` |
| `AUTHORIZATION_NOT_REQUIRED` + non-degraded spine route | `P80_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE` |

Routing precedence is deterministic and fail-closed:
1. if `degraded_evidence_inputs` is non-empty, route to degraded-evidence repair planning
2. otherwise, use the upstream P78 `recommended_next_lane` category to distinguish artifact dry-run planning from the spine implementation planning gate
3. otherwise, return `NOT_COMPUTABLE`

## Governance invariants

P79 remains non-authoritative and fail-closed:
- advisory-only
- projection-only
- authorization-gate-only
- no authorization grant
- no authorization authority
- no execution authority
- no repair authority
- no restoration execution authority
- no generator execution authority
- no upstream input generation authority
- no artifact regeneration authority
- no runtime spine implementation authority

## Handoff

After P78 upstream input regeneration execution plan, run:

```bash
python scripts/temporal/run_temporal_continuity_upstream_input_regeneration_authorization_gate.py
```

This emits `out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json`.

Do not claim runtime spine readiness unless `authorization_gate_status` routes to a non-execution planning gate and `recommended_next_lane = P80_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`.
