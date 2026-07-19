# Operator Input Templates

These templates are non-authoritative examples for external operator input.
They are not consumed by default runners and do not create attestations,
decision records, authorization records, writeback, mutation, activation,
promotion, registration, or execution authority.

## Post-2.5.0 Operator Hold Clearance (Daniel Meyer)

Master index: `operator_input/daniel_meyer_operator_hold_clearance_index.md`

| Domain | Template | Handoff | Preflight |
|--------|----------|---------|-----------|
| Master attestation | `operator_input/templates/daniel_meyer_operator_hold_clearance_attestation_001.example.json` | `operator_input/templates/daniel_meyer_operator_hold_clearance_attestation_handoff.md` | `python3 scripts/preflight_daniel_meyer_operator_hold_clearance_attestation.py` |
| Runtime integration gate | `operator_input/templates/runtime_integration_gate_operator_attestation_payload_001.example.json` | `operator_input/templates/runtime_integration_gate_operator_attestation_handoff.md` | `python3 scripts/preflight_runtime_integration_gate_operator_attestation_payload.py` |
| Oracle Signal physical auth | `operator_input/templates/oracle_signal_physical_implementation_authorization_payload_001.example.json` | `operator_input/templates/oracle_signal_physical_implementation_authorization_handoff.md` | `python3 scripts/preflight_oracle_signal_physical_implementation_authorization_payload.py` |
| Oracle full live endpoint env | redacted external environment only | `operator_input/templates/oracle_full_live_endpoint_environment_handoff.md` | `python scripts/abx_loop.py --emit-oracle-full-live-runtime-preflight --validate-oracle-schemas` |
| P130/P131 research canary | `operator_input/templates/p130_final_activation_operator_decision_payload_001.example.json` | `operator_input/templates/p130_final_activation_operator_decision_handoff.md` | `python3 scripts/preflight_p130_final_activation_operator_decision_payload.py` |
| Codegen shadow replay harness | `operator_input/templates/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.example.json` | `docs/audits/CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE.md` | `python3 scripts/preflight_abx_codegen_shadow_replay_harness_operator_attestation_payload.py` |

**Live codegen envelope (cleared):** [`operator_input/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json`](../abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json) — status `OPERATOR_ATTESTATION_INTAKE_CLEARED`; intake **VALIDATED**; ODR **INTAKE_CLEARED_OBSERVED** (post-#741).

Run intake gate after envelope updates:

```bash
python3 scripts/run_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate.py
```

## Notion Manual Sync Handoffs

| Domain | Handoff | Generator |
|--------|---------|-----------|
| Spec-stack schema audit (#744) | `operator_input/templates/abraxas_spec_stack_schema_audit_notion_sync_handoff.md` | `python scripts/run_abraxas_spec_stack_schema_audit_notion_sync_receipt.py` |
| Phase 13 hygiene | `operator_input/templates/phase13_notion_sync_handoff.md` | `python scripts/run_phase13_notion_sync_packet.py` |

Manual copy-paste only. No Notion API writeback.

Preflight example templates with `--template` to allow `REPLACE_WITH_...` placeholders.
Real payloads belong under `operator_input/` at the paths listed in the index.

Passing preflight does not create attestations, records, writeback, mutation,
activation, promotion, registration, or execution authority.

To validate v2 hygiene Phase 1 stabilization attestation intake, a governed
operator may supply a real payload at:

`operator_input/v2_hygiene_phase1_stabilization_operator_attestation_payload_001.json`

The current intake gate validates only whether that payload is complete and
conservative enough for a future governed decision-record gate. It does not
create the decision record.

Preflight a real payload before running the intake gate:

```bash
python3 scripts/preflight_v2_hygiene_phase1_stabilization_operator_attestation_payload.py
```

Preflight the example template while allowing placeholder values:

```bash
python3 scripts/preflight_v2_hygiene_phase1_stabilization_operator_attestation_payload.py \
  operator_input/templates/v2_hygiene_phase1_stabilization_operator_attestation_payload_001.example.json \
  --template
```

Passing preflight does not create attestations, records, writeback, mutation,
activation, promotion, registration, or execution authority.

## Decision-Record Creation Approval

The v2 hygiene Phase 1 stabilization creation authorization chain is compressed
to a terminal external-operator creation hold. To prepare the explicit external
approval payload without creating the decision record, start from:

`operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_creation_approval_handoff.md`

`operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload_001.example.json`

A real external payload, if supplied later, belongs at:

`operator_input/v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload_001.json`

The real `operator_approval_hash` must be a lowercase `sha256:<64 hex>` digest
for the externally observed approval source.

Preflight a real creation-approval payload:

```bash
python3 scripts/preflight_v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload.py
```

Preflight the example template while allowing placeholder values:

```bash
python3 scripts/preflight_v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload.py \
  operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload_001.example.json \
  --template
```

Passing this preflight does not create the stabilization decision record,
authorize automatic record creation, create evidence bundles or authorization
records, grant implementation authority, write back to Notion or GitHub, mutate
runtime/canon/queue/scheduler state, register, activate, promote,
auto-continue, or execute.

## Decision-Record Materialization Approval

The v2 hygiene Phase 1 stabilization materialization authorization gate is held
for explicit external operator approval before any future record-emission gate.
To prepare that approval payload without materializing the decision record,
start from:

`operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_handoff.md`

`operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_payload_001.example.json`

A real external payload belongs at:

`operator_input/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_payload_001.json`

The real `operator_approval_hash` must be a lowercase `sha256:<64 hex>` digest
for the externally observed materialization approval source.

Preflight a real materialization-approval payload:

```bash
python3 scripts/preflight_v2_hygiene_phase1_stabilization_decision_record_materialization_approval_payload.py
```

Preflight the example template while allowing placeholder values:

```bash
python3 scripts/preflight_v2_hygiene_phase1_stabilization_decision_record_materialization_approval_payload.py \
  operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_payload_001.example.json \
  --template
```

Passing this preflight does not materialize the stabilization decision record,
authorize automatic record materialization, create evidence bundles or
authorization records, grant implementation authority, write back to Notion or
GitHub, mutate runtime/canon/queue/scheduler state, register, activate,
promote, auto-continue, or execute.

## Decision-Record Completion-Validation Approval

The v2 hygiene Phase 1 stabilization completion-validation authorization gate is
held for explicit external operator approval before any future completion
validation can be accepted. To prepare that approval payload without validating
or completing the decision record, start from:

`operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_handoff.md`

`operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_payload_001.example.json`

A real external payload belongs at:

`operator_input/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_payload_001.json`

The real `operator_approval_hash` must be a lowercase `sha256:<64 hex>` digest
for the externally observed completion-validation approval source.

Preflight a real completion-validation approval payload:

```bash
python3 scripts/preflight_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_payload.py
```

Preflight the example template while allowing placeholder values:

```bash
python3 scripts/preflight_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_payload.py \
  operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_payload_001.example.json \
  --template
```

Passing this preflight does not validate, complete, finalize, emit, or
materialize the stabilization decision record, authorize automatic completion
validation, create evidence bundles or authorization records, grant
implementation authority, write back to Notion or GitHub, mutate
runtime/canon/queue/scheduler state, register, activate, promote,
auto-continue, or execute.

## Governed Authorization Record — Phase 30 Live Hyperstition

Operator-supplied governed authorization evidence for Phase 30 live hyperstition
propagation lives at:

- `operator_input/governed_authorization_phase30_live_hyperstition.json`
- `operator_input/governed_authorization_phase30_live_hyperstition.md`

This record documents operator disposition and hash-chain acknowledgement. It does
not mutate gates, grant repo execution authority by itself, write back to Notion or
GitHub, or activate runtime/queue/scheduler/canon surfaces without a separate governed
execution lane.
