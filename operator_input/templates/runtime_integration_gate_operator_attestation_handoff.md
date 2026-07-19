# Runtime Integration Gate Operator Attestation Handoff

This packet is documentation only. It does not grant execution authority,
mandatory pre-dispatch wiring, runtime mutation, or canon mutation.

## Files

- Example template: `operator_input/templates/runtime_integration_gate_operator_attestation_payload_001.example.json`
- Real payload path: `operator_input/runtime_integration_gate_operator_attestation_payload_001.json`
- Preflight: `python3 scripts/preflight_runtime_integration_gate_operator_attestation_payload.py`
- Intake gate: `python3 scripts/run_runtime_integration_gate_operator_attestation_intake_gate.py`
- Decision record: `python3 scripts/run_runtime_integration_gate_operator_review_decision_record.py`

## Required Attestation Groups

- `operator_identity`
- `review_attestations`
- `operator_disposition`
- `authority_boundary_acknowledgement`

## Allowed `selected_decision` Values

| Value | Effect |
|-------|--------|
| `MAINTAIN_HOLD` | Terminal hold; no shadow wiring |
| `APPROVE_SHADOW_WIRING_ONLY` | Advisory shadow wiring; execution denied |
| `APPROVE_MANDATORY_PRE_DISPATCH_WIRING` | Would flip mandatory wiring if decision-record lane permits |

## Disposition Acknowledgement Alignment

- `APPROVE_SHADOW_WIRING_ONLY`: set `valid_for_runtime_wiring_denied_acknowledged` to `false`
- `MAINTAIN_HOLD` or `APPROVE_MANDATORY_PRE_DISPATCH_WIRING`: set `valid_for_runtime_wiring_denied_acknowledged` to `true`
- `mandatory_pre_dispatch_wiring_denied_acknowledged` must be `true` unless explicitly approving mandatory wiring

## Fields Daniel Must Replace

- `operator_attestation_hash`
- `operator_reviewed_at_source_observed`

## Validation Workflow

```bash
python3 scripts/preflight_runtime_integration_gate_operator_attestation_payload.py
python3 scripts/run_runtime_integration_gate_operator_attestation_intake_gate.py
python3 scripts/run_runtime_integration_gate_operator_review_decision_record.py
python3 scripts/run_runtime_integration_gate_operator_review_decision_record_hold_receipt.py
```

Passing intake validation still grants no execution authority.
