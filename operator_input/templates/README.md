# Operator Input Templates

These templates are non-authoritative examples for external operator input.
They are not consumed by default runners and do not create attestations,
decision records, authorization records, writeback, mutation, activation,
promotion, registration, or execution authority.

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

`operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload_001.example.json`

A real external payload, if supplied later, belongs at:

`operator_input/v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload_001.json`

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
