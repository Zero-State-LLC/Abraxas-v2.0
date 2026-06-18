# Operator Input

External operator payloads and templates. **Non-authoritative** until validated by governed intake gates. No auto-execution, writeback, or authority grant from payload presence alone.

## Quick reference

| Category | Description |
|----------|-------------|
| **Required (cleared)** | Payloads on disk that passed intake validation |
| **Optional** | v2 hygiene stabilization family — supply when operator lane requires |
| **Attestation** | External operator attestation envelopes |
| **Execution** | Phase handoff templates — historical; execution denied by default |
| **Review** | Hold clearance and disposition indexes |

Template details: [`templates/README.md`](templates/README.md).

---

## Required / cleared payloads

| Payload | Status | Intake / review |
|---------|--------|-----------------|
| [`abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json`](abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json) | `OPERATOR_ATTESTATION_INTAKE_CLEARED` | Intake **VALIDATED**; ODR **INTAKE_CLEARED_OBSERVED** |
| [`runtime_integration_gate_operator_attestation_payload_001.json`](runtime_integration_gate_operator_attestation_payload_001.json) | Operator attested | Shadow wiring approved; execution denied |
| [`oracle_signal_physical_implementation_authorization_payload_001.json`](oracle_signal_physical_implementation_authorization_payload_001.json) | Operator attested | Shadow implementation authorized |
| [`daniel_meyer_operator_hold_clearance_attestation_001.json`](daniel_meyer_operator_hold_clearance_attestation_001.json) | Master hold clearance | See [`daniel_meyer_operator_hold_clearance_index.md`](daniel_meyer_operator_hold_clearance_index.md) |

---

## Attestation payloads (governed intake)

| Domain | Payload | Preflight | Runner |
|--------|---------|-----------|--------|
| Codegen shadow replay harness | `abx_codegen_*_payload_001.json` | `preflight_abx_codegen_shadow_replay_harness_operator_attestation_payload.py` | `run_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate.py` |
| Runtime integration gate | `runtime_integration_gate_*_001.json` | `preflight_runtime_integration_gate_operator_attestation_payload.py` | `run_runtime_integration_gate_operator_attestation_intake_gate.py` |
| Oracle Signal physical | `oracle_signal_physical_*_001.json` | `preflight_oracle_signal_physical_implementation_authorization_payload.py` | `run_oracle_signal_physical_implementation_authorization_intake_gate.py` |
| P130/P131 research canary | `p130_final_activation_*_001.json` | `preflight_p130_final_activation_operator_decision_payload.py` | — (P130 hold active) |
| v2 hygiene Phase 1 | `v2_hygiene_phase1_stabilization_operator_attestation_payload_001.json` | `preflight_v2_hygiene_phase1_stabilization_operator_attestation_payload.py` | intake gate under `out/operator_review/` |

Intake doc: [`docs/audits/CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE.md`](../docs/audits/CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE.md).

---

## Optional payloads (v2 hygiene decision-record chain)

Approval payloads for stabilization decision-record materialization/emission/finalization/completion — supply only when external operator lane requires:

- `v2_hygiene_phase1_stabilization_decision_record_*_approval_payload_001.json`
- `v2_hygiene_phase19_external_operator_attestation_autonomy_payload_001.json`

See [`templates/README.md`](templates/README.md) for handoffs and preflight commands.

---

## Review payloads

| File | Purpose |
|------|---------|
| [`daniel_meyer_operator_hold_clearance_index.md`](daniel_meyer_operator_hold_clearance_index.md) | Master index for post-2.5.0 hold clearance |
| [`p130_final_activation_operator_decision_payload_001.json`](p130_final_activation_operator_decision_payload_001.json) | P130 production hold decision (held) |

---

## Execution payloads (historical templates)

Phase 13–32 handoff templates under [`templates/`](templates/) — planning and operator signoff shapes only. **Do not treat as execution authorization.** Examples:

- `phase30_live_execution_activation_authorization_review_handoff.md`
- `phase31_full_live_hyperstition_propagation_eternal_authority_seal_handoff.md`

---

## Next distinct lane (not intake clearance)

Harness **implementation** authorization requires a **separate** governed payload with:

```yaml
authorize_harness_implementation: true
authorize_harness_execution: false
authorize_production_activation: false
```

Intake clearance (`INTAKE_CLEARED_ONLY`) alone does not unlock implementation.

---

## Explicit denials

- No auto-create decision records from templates
- No Notion/GitHub API writeback from payloads
- No `out/research_canary_*` regeneration from operator_input
- No canon/runtime/queue/scheduler mutation
