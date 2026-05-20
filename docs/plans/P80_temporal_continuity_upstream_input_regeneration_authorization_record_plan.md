# P80 — Temporal Continuity Upstream Input Regeneration Authorization Record Plan (Advisory)

## Scope

P80 is a deterministic advisory-only upstream input regeneration **authorization record plan** lane driven strictly by:
`out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json` (P79 output).

This lane **does not**:
- create an authorization record or token
- grant authorization
- set `authorization_granted = true`
- set `operator_approved = true`
- grant `execution_authority`
- execute commands
- run generators
- regenerate upstream inputs
- regenerate artifacts
- repair evidence
- mutate canon/runtime/scheduler/forecast state
- claim runtime spine readiness

## Required outputs

- `core/temporal_continuity_upstream_input_regeneration_authorization_record_plan.py`
- `scripts/run_temporal_continuity_upstream_input_regeneration_authorization_record_plan.py`
- `contracts/canon/temporal_continuity_upstream_input_regeneration_authorization_record_plan.v1.schema.json`
- `tests/test_temporal_continuity_upstream_input_regeneration_authorization_record_plan.py`
- `out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json`

## Artifact

- `artifact_type = TemporalContinuityUpstreamInputRegenerationAuthorizationRecordPlan.v1`
- `canonical_status = ADVISORY_ONLY`
- `audit_only = true`
- `projection_only = true`
- `authorization_record_plan_only = true`
- `authorization_granted = false`
- `operator_approved = false`
- `authorization_record_creation_allowed = false`
- all authority flags hard-locked false, including execution/authorization/authorization-record-creation/generator/upstream-input/artifact-regeneration/spine implementation authority

## Authorization record plan status semantics

| Condition | authorization_record_plan_status |
|---|---|
| P79 source missing/unreadable/malformed | `NOT_COMPUTABLE` |
| P79 `authorization_gate_status = AUTHORIZATION_ELIGIBLE` and `authorization_required_record.required = true` | `AUTHORIZATION_RECORD_PLAN_READY` |
| P79 `authorization_gate_status = AUTHORIZATION_BLOCKED` | `AUTHORIZATION_RECORD_PLAN_BLOCKED` |
| P79 `authorization_gate_status = AUTHORIZATION_NOT_REQUIRED` | `AUTHORIZATION_RECORD_NOT_REQUIRED` |
| Any inconsistent status combination | `NOT_COMPUTABLE` |

## Authorization doctrine

P80 remains strictly plan-only:
- `authorization_record_creation_allowed` is always `false`
- `authorization_record_creation_authority` is always `false`
- `authorization_authority` is always `false`
- `authorization_granted` is always `false`
- `operator_approved` is always `false`
- `execution_authority` is always `false`

The `planned_authorization_record` field describes the **shape** of a future `OperatorAuthorizationToken.v1` only.
P80 does not create `out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json`.

## Planned authorization record shape

When P79 is `AUTHORIZATION_ELIGIBLE`, P80 emits a `planned_authorization_record` describing:

```json
{
  "artifact_type": "OperatorAuthorizationToken.v1",
  "authorization_scope": [...],
  "authorized_commands": [...],
  "authorized_expected_outputs": [...],
  "source_authorization_gate_hash": "<sha256 of P79 artifact>",
  "source_authorization_gate_path": "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json",
  "operator_approval_required": true,
  "operator_approved": false,
  "authorization_granted": false,
  "execution_authority": false,
  "authorization_created_by": "NOT_CREATED_BY_P80",
  "authorization_created_at": "NOT_CREATED_BY_P80",
  "expiration_policy": { "policy_type": "OPERATOR_DEFINED", ... },
  "revocation_policy": { "policy_type": "OPERATOR_DEFINED", "revocable": true, ... },
  "validation_requirements": [...],
  "packet_hash_required": true
}
```

This is a shape definition only. P80 does not create this file.

## Authorization scope rules

- `authorization_scope` derives only from P79 `eligible_execution_steps[].target_input_path`.
- `authorized_command_candidates` derives only from P79 `eligible_commands[].command`.
- `authorized_expected_output_candidates` derives only from P79 `eligible_commands[].expected_output_path`.
- Blocked commands and steps are excluded from all candidates.
- If P79 is not `AUTHORIZATION_ELIGIBLE`, all candidate lists are empty.

## Recommended next-lane logic

| authorization_record_plan_status | recommended_next_lane |
|---|---|
| `NOT_COMPUTABLE` | `P79_AUTHORIZATION_GATE_REGENERATION` |
| `AUTHORIZATION_RECORD_PLAN_READY` | `P81_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE` |
| `AUTHORIZATION_RECORD_PLAN_BLOCKED` | `P81_TEMPORAL_CONTINUITY_AUTHORIZATION_BLOCKER_REPAIR_PLAN` |
| `AUTHORIZATION_RECORD_NOT_REQUIRED` + degraded evidence | `P81_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN` |
| `AUTHORIZATION_RECORD_NOT_REQUIRED` + artifact dry-run route | `P81_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN` |
| `AUTHORIZATION_RECORD_NOT_REQUIRED` + spine gate route | `P81_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE` |

## Provenance bindings

P80 emits deterministic provenance bindings including:
- `source_authorization_gate_path`
- `source_authorization_gate_hash`
- `eligible_step_ids`
- `eligible_command_hashes`
- `expected_output_paths`
- `inherited_degraded_evidence_count`
- `inherited_blocker_count`
- `inherited_drift_flag_count`

## Operator approval requirements

P80 emits deterministic operator approval requirements covering:
- Explicit human/operator approval
- Exact command review
- Exact output-path review
- Scope review
- Source hash review
- Expiration policy review
- Revocation policy review
- No-op rollback review
- Post-run validation review
- Authority-denial confirmation

## Token creation requirements

P80 specifies token creation requirements:
- Token creation is future-lane only
- Token must include `source_authorization_gate_hash`
- Token must include `authorized_commands`
- Token must include `authorized_expected_outputs`
- Token must keep `execution_authority = false` unless a separate explicitly authorized execution lane exists
- Token must be revocable
- Token must be deterministic canonical JSON with `packet_hash`
- Token must not be generated by P80

## Governance invariants

P80 remains non-authoritative and fail-closed:
- advisory-only
- projection-only
- authorization-record-plan-only
- no authorization record creation
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

After P79 authorization gate, run:

```bash
python scripts/run_temporal_continuity_upstream_input_regeneration_authorization_record_plan.py
```

This emits `out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json`.

Do not claim authorization, execution, or runtime spine readiness unless a future explicit operator authorization record and governed execution lane are created separately.
