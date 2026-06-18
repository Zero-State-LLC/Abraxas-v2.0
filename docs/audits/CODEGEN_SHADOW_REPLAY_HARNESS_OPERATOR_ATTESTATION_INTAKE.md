# Codegen Shadow Replay Harness — Operator Attestation Intake

Advisory-only intake instructions for external operator attestation on the ABX Codegen Intelligence Spine shadow replay harness lane.

**Authority posture:** This document does not grant harness implementation, decision-record creation, execution authority, canon mutation, Notion writeback, or shadow replay execution.

## Current blocker

Source: `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_review_001.latest.json`

- Status: `ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR`
- `recommended_next_lane`: `NOT_COMPUTABLE`
- `operator_attestations_present`: **false**

Dry-run validation blockers (`out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_dry_run_001.latest.json`):

| Blocker | Required field |
|---------|----------------|
| `operator_identity_not_attested` | `operator_identity` |
| `operator_decision_not_attested` | `operator_decision.selected_decision` |
| `operator_rationale_not_attested` | `operator_decision.rationale` |
| `operator_signature_not_attested` | `operator_identity.operator_signature` |
| `operator_evidence_bundle_not_attested` | `operator_evidence_bundle` |

## Intake procedure

1. Copy the example template:
   - From: `operator_input/templates/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.example.json`
   - To: `operator_input/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json`

2. Replace all `REPLACE_WITH_*` placeholders with external operator values.

3. Review upstream artifacts before attestation:
   - `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_implementation_authorization_gate_001.latest.json`
   - `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_dry_run_001.latest.json`
   - `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_plan_001.latest.json`

4. Allowed operator decisions (planning-only in this lane):
   - `APPROVE` — does **not** auto-authorize implementation; requires separate authorization record
   - `REJECT` — blocks implementation path
   - `REQUEST_REFINEMENT` — routes back to proposal refinement
   - `ESCALATE_TO_META_GATE` — requires meta-gate authorization record planning
   - `DEFER` — holds for more evidence (default in example template)

5. Submit attestation payload for governed intake in a **future** lane. No auto-activation occurs from template completion alone.

## Explicit denials

- Do not create `core/codegen_shadow_replay_harness.py` from this intake alone
- Do not auto-create operator decision records
- Do not enable shadow replay execution
- Do not perform Notion or GitHub writeback
- Do not regenerate `out/research_canary_*` artifacts

## Related surfaces

| Surface | Path |
|---------|------|
| Harness artifact | `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_001.latest.json` |
| Implementation auth gate | `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_implementation_authorization_gate_001.latest.json` |
| ODR dry run | `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_dry_run_001.latest.json` |
| ODR review | `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_review_001.latest.json` |
| Continuation audit | `docs/releases/POST_2_5_0_CONTINUATION_AUDIT.md` |
