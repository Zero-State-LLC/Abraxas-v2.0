# Post–P132 Research Canary Continuation Plan

Advisory routing after P132 advisory shadow activation pilot (DROP006A).

## Completed

| Lane | Deliverable |
|------|-------------|
| P131 (relaxed) | Per-candidate advisory shadow approval; routes to P132 |
| P132 | `RESEARCH_CANARY_ADVISORY_SHADOW_ACTIVATION_RECORD_EMITTED` for DROP006A pilot |

## Current posture

- **DROP006A:** `advisory_shadow_activation_approved=true`, `wiring_mode=SHADOW_ADVISORY_ONLY`
- **DROP006B:** `advisory_shadow_activation_approved=true`, `wiring_mode=SHADOW_ADVISORY_ONLY`
- **DROP006C–DROP007C:** held (`OPERATOR_DECISION_MAINTAIN_HOLD`)
- Execution, production activation, runtime, scheduler: **denied**
- P130 hold lane unchanged; P131/P132 additive only

## Spine refresh note (2026-06-18)

`run_research_canary_artifact_spine_refresh.py` was executed and **reverted** after P129 degraded to `CANARY_ACTIVATION_READINESS_EVIDENCE_INCOMPLETE`. Pre-refresh artifacts restored from git. Do not regenerate `out/research_canary_*` without a separate governed operator replay lane.

## Next steps

### Expand pilot to additional candidates

1. Update `operator_input/p130_final_activation_operator_decision_payload_001.json` per candidate
2. Re-run preflight + P131 + P132 intake
3. One candidate per PR recommended

### Full production activation (separate track)

Requires new P133+ lane design:
- Schema allowing `execution_authority=true` with explicit operator attestation
- No mutation of P130 in place
- Separate governed execution authorization record

## Validation

```bash
python scripts/preflight_p130_final_activation_operator_decision_payload.py
python scripts/run_research_canary_final_activation_operator_decision_record.py
python scripts/run_research_canary_advisory_shadow_activation_record.py
python -m pytest tests/test_research_canary_p131_advisory_shadow_activation.py tests/test_research_canary_advisory_shadow_activation_record.py -q
python scripts/run_fast_ci.py
```

## Explicit non-goals

- Bulk unlock of all 6 candidates without per-candidate attestation
- Spine regeneration without validated replay lane
- Treating advisory shadow activation as execution authorization
