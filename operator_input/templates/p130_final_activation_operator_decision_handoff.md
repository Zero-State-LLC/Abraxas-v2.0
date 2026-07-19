# P130/P131 Research Canary Operator Decision Handoff

This packet is documentation only. It does not grant live canary activation,
production activation, execution authority, or canon promotion.

## Files

- Example template: `operator_input/templates/p130_final_activation_operator_decision_payload_001.example.json`
- Real payload path: `operator_input/p130_final_activation_operator_decision_payload_001.json`
- Preflight: `python3 scripts/preflight_p130_final_activation_operator_decision_payload.py`
- P131 decision record: `python3 scripts/research/run_research_canary_final_activation_operator_decision_record.py`

## Required Attestation Groups

- `operator_identity`
- `upstream_acknowledgement`
- `candidate_dispositions` (exactly 6 entries)
- `operator_disposition`
- `authority_boundary_acknowledgement`

## Critical Hash Binding

`upstream_acknowledgement.upstream_packet_hash` must match `packet_hash` from:

`out/research_canary_final_activation_authorization_review/latest.json`

Do not regenerate P128–P130 canary spine artifacts casually. Refresh the hash
only when P130 is intentionally replayed from a validated source.

## Candidate IDs (must match P130 `analyzed_candidates`)

- `DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER`
- `DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER`
- `DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER`
- `DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER`
- `DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER`
- `DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER`

## Code Constraint

The P131 builder currently requires all four candidate booleans
(`activation_approved`, `authorization_granted`, `production_activation`,
`execution_authority`) to be `false` in the payload. Live activation approval
requires a separate governed code change before payloads can express
`activation_approved=true`.

## Fields Daniel Must Replace

- `operator_attestation_hash`
- `operator_reviewed_at_source_observed`
- `upstream_packet_hash`

## Validation Workflow

```bash
python3 scripts/preflight_p130_final_activation_operator_decision_payload.py
python3 scripts/research/run_research_canary_final_activation_operator_decision_record.py
```

P131 emits a new decision record; it does not mutate the P130 artifact in place.

Passing P131 emission still grants no execution authority.
