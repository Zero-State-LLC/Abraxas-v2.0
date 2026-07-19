# Daniel Meyer — Operator Hold Clearance Index

Master index for post-2.5.0 edge hold clearance payloads. All surfaces remain advisory-only.

## Master attestation

| Item | Path |
|------|------|
| Real payload | [`daniel_meyer_operator_hold_clearance_attestation_001.json`](daniel_meyer_operator_hold_clearance_attestation_001.json) |
| Mirror | [`daniel_meyer_operator_hold_clearance_attestation_001.md`](daniel_meyer_operator_hold_clearance_attestation_001.md) |
| Template | [`templates/daniel_meyer_operator_hold_clearance_attestation_001.example.json`](templates/daniel_meyer_operator_hold_clearance_attestation_001.example.json) |
| Handoff | [`templates/daniel_meyer_operator_hold_clearance_attestation_handoff.md`](templates/daniel_meyer_operator_hold_clearance_attestation_handoff.md) |

## Domain payloads

| Domain | Real JSON | Mirror | Template | Handoff |
|--------|-----------|--------|----------|---------|
| Runtime integration gate | [`runtime_integration_gate_operator_attestation_payload_001.json`](runtime_integration_gate_operator_attestation_payload_001.json) | [`.md`](runtime_integration_gate_operator_attestation_payload_001.md) | [`.example.json`](templates/runtime_integration_gate_operator_attestation_payload_001.example.json) | [handoff](templates/runtime_integration_gate_operator_attestation_handoff.md) |
| Oracle Signal physical auth | [`oracle_signal_physical_implementation_authorization_payload_001.json`](oracle_signal_physical_implementation_authorization_payload_001.json) | [`.md`](oracle_signal_physical_implementation_authorization_payload_001.md) | [`.example.json`](templates/oracle_signal_physical_implementation_authorization_payload_001.example.json) | [handoff](templates/oracle_signal_physical_implementation_authorization_handoff.md) |
| P130/P131 research canary | [`p130_final_activation_operator_decision_payload_001.json`](p130_final_activation_operator_decision_payload_001.json) | [`.md`](p130_final_activation_operator_decision_payload_001.md) | [`.example.json`](templates/p130_final_activation_operator_decision_payload_001.example.json) | [handoff](templates/p130_final_activation_operator_decision_handoff.md) |

## Validation workflow

```bash
python scripts/preflight_daniel_meyer_operator_hold_clearance_attestation.py
python scripts/preflight_runtime_integration_gate_operator_attestation_payload.py
python scripts/preflight_oracle_signal_physical_implementation_authorization_payload.py
python scripts/preflight_p130_final_activation_operator_decision_payload.py
```

Template mode (placeholders allowed):

```bash
python scripts/preflight_daniel_meyer_operator_hold_clearance_attestation.py \
  operator_input/templates/daniel_meyer_operator_hold_clearance_attestation_001.example.json --template
python scripts/preflight_runtime_integration_gate_operator_attestation_payload.py \
  operator_input/templates/runtime_integration_gate_operator_attestation_payload_001.example.json --template
python scripts/preflight_oracle_signal_physical_implementation_authorization_payload.py \
  operator_input/templates/oracle_signal_physical_implementation_authorization_payload_001.example.json --template
python scripts/preflight_p130_final_activation_operator_decision_payload.py \
  operator_input/templates/p130_final_activation_operator_decision_payload_001.example.json --template
```

## Intake chain (after real preflights pass)

```bash
python scripts/runtime/run_runtime_integration_gate_operator_attestation_intake_gate.py
python scripts/runtime/run_runtime_integration_gate_operator_review_decision_record.py
python scripts/ingest/run_oracle_signal_physical_implementation_authorization_intake_gate.py
python scripts/ingest/run_oracle_signal_physical_implementation_authorization_record.py
python scripts/research/run_research_canary_final_activation_operator_decision_record.py
```

Passing preflight or intake validation grants no execution authority.
