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
