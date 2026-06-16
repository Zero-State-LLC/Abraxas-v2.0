# v2 Hygiene Phase 1 Stabilization Decision-Record Creation Approval Handoff

This packet is documentation only. It is not an operator approval, decision
record, authorization record, evidence bundle, implementation request,
writeback request, mutation request, activation request, promotion request,
registration request, auto-continuation request, or execution request.

## Files

- Example template: `operator_input/templates/v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload_001.example.json`
- Real payload path: `operator_input/v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload_001.json`
- Preflight command: `python3 scripts/preflight_v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload.py`
- Source authorization gate: `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_001.latest.json`
- Source compression audit: `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001.latest.json`

## Required Approval Groups

- `operator_identity`
- `creation_scope_acknowledgement`
- `creation_disposition`
- `authority_boundary_acknowledgement`
- `terminal_output_controls`

## Expected Conservative Values

- `source_authorization_gate_path`: `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_001.latest.json`
- `source_compression_audit_path`: `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001.latest.json`
- `terminal_creation_hold_acknowledged`: `true`
- `approved_record_id`: `v2_hygiene_phase1_stabilization_decision_record_001`
- `approved_record_output_path`: `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_001.latest.json`
- `selected_creation_disposition`: `APPROVE_DECISION_RECORD_CREATION_FOR_SEPARATE_GOVERNED_MATERIALIZATION_LANE`
- `decision_record_creation_now_allowed`: `false`
- `decision_record_auto_creation_allowed`: `false`
- `separate_materialization_lane_required`: `true`
- `downstream_lane_disposition`: `NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_CREATION_MATERIALIZATION`
- `future_materialization_gate_required`: `true`
- `future_record_creation_allowed_by_this_payload`: `false`
- `rollback_or_supersession_policy`: `fresh governed operator decision required`

## Do Not Change Authority Boundary

The payload must preserve:

- no decision-record auto-creation
- no immediate decision-record creation
- no execution
- no implementation
- no runtime mutation
- no canon mutation
- no queue mutation
- no scheduler mutation
- no Notion writeback
- no GitHub writeback
- no activation
- no promotion
- no registration
- no auto-continuation

## Validation Workflow

1. Copy the example template to the real payload path only when an external
   operator is ready to approve a separate governed materialization lane.
2. Replace every `REPLACE_WITH_...` placeholder with externally supplied values.
3. Run the creation-approval preflight validator in real mode:

   ```bash
   python3 scripts/preflight_v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload.py
   ```

4. Do not create `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_001.latest.json`
   from this payload. Passing preflight only prepares a future governed
   materialization gate.

Passing preflight grants no authority. A later separate governed
decision-record materialization lane is required before any record creation or
downstream authorization.
