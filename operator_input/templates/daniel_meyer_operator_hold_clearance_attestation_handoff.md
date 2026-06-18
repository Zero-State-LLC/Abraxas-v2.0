# Daniel Meyer — Operator Hold Clearance Master Attestation Handoff

This packet is documentation only. It is not an attestation, decision record,
authorization record, evidence bundle, implementation request, writeback request,
mutation request, activation request, promotion request, registration request, or
execution request.

## Files

- Example template: `operator_input/templates/daniel_meyer_operator_hold_clearance_attestation_001.example.json`
- Real payload path: `operator_input/daniel_meyer_operator_hold_clearance_attestation_001.json`
- Preflight command: `python3 scripts/preflight_daniel_meyer_operator_hold_clearance_attestation.py`

## Required Attestation Groups

- `operator_identity`
- `clearance_scope`
- `authority_boundary_acknowledgement`

## Clearance Scope

Set each boolean explicitly before running domain intake chains:

| Field | Default draft | Meaning |
|-------|---------------|---------|
| `post_2_5_0_edge_holds` | `true` | Enable runtime gate, Oracle, and P130/P131 payloads |
| `p130_research_canary_hold` | `true` | Include P131 operator decision record lane |
| `oracle_signal_implementation_hold` | `true` | Include Oracle physical implementation authorization |
| `runtime_integration_gate_hold` | `true` | Include runtime integration gate attestation |
| `v2_hygiene_phase1_stabilization_holds` | `false` | Separate v2 hygiene chain (not part of this package) |
| `all_operator_review_surfaces` | `false` | Do not attempt bulk 91-surface clearance |

## Fields Daniel Must Replace

- `operator_attestation_hash`: lowercase `sha256:<64-hex>` digest of externally observed approval
- `operator_reviewed_at_source_observed`: ISO-8601 timestamp of external review

## Validation Workflow

1. Copy the example template to the real payload path only when ready to attest.
2. Replace every `REPLACE_WITH_...` placeholder with externally supplied values.
3. Run preflight in real mode:

   ```bash
   python3 scripts/preflight_daniel_meyer_operator_hold_clearance_attestation.py
   ```

4. Preflight the example template while allowing placeholders:

   ```bash
   python3 scripts/preflight_daniel_meyer_operator_hold_clearance_attestation.py \
     operator_input/templates/daniel_meyer_operator_hold_clearance_attestation_001.example.json \
     --template
   ```

Passing preflight grants no authority. Domain-specific payloads and intake gates
are required before any held artifact booleans may change.
