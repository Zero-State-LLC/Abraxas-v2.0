# Daniel Meyer — Operator Hold Clearance Attestation

Operator: **Daniel Meyer** (`daniel_meyer`)

Master scope declaration for post-2.5.0 edge hold clearance. Consumed by preflight only; domain-specific payloads drive intake gates.

Payload: [`daniel_meyer_operator_hold_clearance_attestation_001.json`](daniel_meyer_operator_hold_clearance_attestation_001.json)

Preflight:

```bash
python scripts/preflight_daniel_meyer_operator_hold_clearance_attestation.py
```

Domain payloads:

| Domain | Payload |
|--------|---------|
| Runtime integration gate | `runtime_integration_gate_operator_attestation_payload_001.json` |
| Oracle Signal physical implementation | `oracle_signal_physical_implementation_authorization_payload_001.json` |
| P130/P131 research canary | `p130_final_activation_operator_decision_payload_001.json` |
