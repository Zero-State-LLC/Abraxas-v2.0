# v2 Hygiene Phase 1 Stabilization Materialization Approval Handoff

Use this packet only when an external operator is ready to approve the next governed materialization step for the already planned stabilization decision record.

Example template:
`operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_payload_001.example.json`

Real payload path:
`operator_input/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_payload_001.json`

Preflight command:

```bash
python3 scripts/preflight_v2_hygiene_phase1_stabilization_decision_record_materialization_approval_payload.py
```

Required groups:

- `operator_identity`
- `materialization_scope_acknowledgement`
- `materialization_disposition`
- `authority_boundary_acknowledgement`
- `terminal_output_controls`

Expected conservative values:

- `source_materialization_authorization_gate_path`: `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_authorization_gate_001.latest.json`
- `source_materialization_plan_path`: `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_plan_001.latest.json`
- `selected_materialization_disposition`: `APPROVE_DECISION_RECORD_MATERIALIZATION_FOR_SEPARATE_GOVERNED_RECORD_EMISSION_LANE`
- `downstream_lane_disposition`: `NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_MATERIALIZATION_EMISSION`
- `decision_record_materialization_now_allowed`: `false`
- `decision_record_auto_materialization_allowed`: `false`
- `future_record_materialization_allowed_by_this_payload`: `false`

Do not change these authority boundaries: no decision-record auto-materialization, no immediate decision-record materialization, no execution, no implementation, no runtime mutation, no canon mutation, no queue mutation, no scheduler mutation, no Notion writeback, no GitHub writeback, no activation, no promotion, no registration, and no auto-continuation.

Passing preflight grants no authority. It only validates operator input for a future governed record-emission gate.
