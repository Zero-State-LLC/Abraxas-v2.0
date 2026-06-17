# v2 Hygiene Phase 1 Stabilization Completion-Validation Approval Handoff

Use this packet only when an external operator is ready to approve the next governed completion-validation step for the planned stabilization decision record.

Example template:
`operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_payload_001.example.json`

Real payload path:
`operator_input/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_payload_001.json`

Preflight command:

```bash
python3 scripts/preflight_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_payload.py
```

Required groups:

- `operator_identity`
- `completion_validation_scope_acknowledgement`
- `completion_validation_disposition`
- `authority_boundary_acknowledgement`
- `terminal_output_controls`

Expected conservative values:

- `source_completion_validation_authorization_gate_path`: `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate_001.latest.json`
- `source_completion_validation_plan_path`: `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan_001.latest.json`
- `selected_completion_validation_disposition`: `APPROVE_DECISION_RECORD_COMPLETION_VALIDATION_FOR_SEPARATE_GOVERNED_COMPLETION_VALIDATION_GATE`
- `downstream_lane_disposition`: `NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_COMPLETION_VALIDATION`
- `decision_record_completion_validation_now_allowed`: `false`
- `decision_record_auto_completion_validation_allowed`: `false`
- `future_record_completion_validation_allowed_by_this_payload`: `false`

Do not change these authority boundaries: no decision-record auto-completion, no immediate decision-record completion validation, no execution, no implementation, no runtime mutation, no canon mutation, no queue mutation, no scheduler mutation, no Notion writeback, no GitHub writeback, no activation, no promotion, no registration, and no auto-continuation.

Validation workflow:

1. Copy the example template to the real payload path only when an external operator is ready to approve a separate governed completion-validation gate.
2. Replace every `REPLACE_WITH_...` placeholder with externally supplied values.
3. Ensure `operator_approval_hash` is a real lowercase `sha256:<64 hex>` digest for the externally observed approval source, not a placeholder.
4. Run the completion-validation approval preflight validator in real mode.
5. Rerun the existing intake gate only after preflight passes.

Passing preflight grants no authority. It only validates operator input for a future governed completion-validation gate and does not complete, validate, finalize, emit, or materialize the stabilization decision record.
