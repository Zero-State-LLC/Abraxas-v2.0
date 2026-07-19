# v2 Hygiene Phase 1 Stabilization Operator Handoff

This packet is documentation only. It is not an attestation, decision record,
authorization record, evidence bundle, implementation request, writeback request,
mutation request, activation request, promotion request, registration request, or
execution request.

## Files

- Example template: `operator_input/templates/v2_hygiene_phase1_stabilization_operator_attestation_payload_001.example.json`
- Real payload path: `operator_input/v2_hygiene_phase1_stabilization_operator_attestation_payload_001.json`
- Preflight command: `python3 scripts/preflight_v2_hygiene_phase1_stabilization_operator_attestation_payload.py`
- Intake gate runner: `python3 scripts/run_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate.py`

## Required Attestation Groups

- `operator_identity`
- `strategy_scope_acknowledgement`
- `stabilization_disposition`
- `authority_boundary_acknowledgement`
- `terminal_output_controls`

## Expected Conservative Values

- `selected_strategy_id`: `terminal_snapshot_strategy`
- `approved_strategy_id`: `terminal_snapshot_strategy`
- `source_strategy_plan_path`: `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.json`
- `terminal_snapshot_allowed`: `true`
- `bulk_scan_exclusion_allowed`: `true`
- `two_phase_manifest_allowed`: `false`
- `naive_regeneration_allowed`: `false`
- `downstream_lane_disposition`: `NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_INTAKE`
- `future_dry_run_allowed`: `false`
- `future_record_creation_gate_required`: `true`
- `rollback_or_supersession_policy`: `fresh governed operator decision required`

## Do Not Change Authority Boundary

The payload must preserve:

- no execution
- no implementation
- no runtime mutation
- no canon mutation
- no Notion writeback
- no GitHub writeback
- no decision-record auto-creation
- no activation
- no promotion
- no registration

## Validation Workflow

1. Copy the example template to the real payload path only when an external
   operator is ready to attest.
2. Replace every `REPLACE_WITH_...` placeholder with externally supplied values.
3. Run the preflight validator in real mode:

   ```bash
   python3 scripts/preflight_v2_hygiene_phase1_stabilization_operator_attestation_payload.py
   ```

4. Only after preflight passes, rerun the existing intake gate:

   ```bash
   python3 scripts/run_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate.py
   ```

Passing preflight or intake validation still grants no authority. A later
separate governed decision-record gate is required before any downstream
authorization.
