# Runtime Integration Gate — Shadow Wiring Plan

Advisory-only planning surface for post-#719 shadow runtime wiring (`APPROVE_SHADOW_WIRING_ONLY`).

## Artifact

- JSON: `out/audit/runtime_integration_gate_shadow_wiring_plan_001.latest.json`
- Runner: `python scripts/runtime/run_runtime_integration_gate_shadow_wiring_plan.py`

## Integration points (from runtime gate receipt)

Seven covered subsystems map to shadow-advisory wiring candidates only. No mandatory pre-dispatch wiring or live runtime mutation is authorized.

## Implementation sequence (advisory)

1. Document shadow wiring hooks per `integration_point_id`
2. Add read-only projection bindings only
3. Verify authority locks remain false after wiring
4. Separate governed lane required for `mandatory_pre_dispatch_wiring=true`

## Authority posture

- `shadow_wiring_approved=true`, `valid_for_runtime_wiring=true` (hold receipt)
- `mandatory_pre_dispatch_wiring=false`, `execution_authority=false`
- `recommended_next_lane`: NOT_COMPUTABLE until a future implementation PR lane is designed
