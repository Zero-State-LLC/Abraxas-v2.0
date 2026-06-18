# Codegen Shadow Replay Harness — Operator Attestation Intake

Advisory-only intake instructions for external operator attestation on the ABX Codegen Intelligence Spine shadow replay harness lane.

**Authority posture:** This document does not grant harness implementation, decision-record creation, execution authority, canon mutation, Notion writeback, or shadow replay execution.

## Current posture

Source: `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_review_001.latest.json`

- Status: `ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW_INTAKE_CLEARED_OBSERVED`
- Intake gate: **VALIDATED** (`INTAKE_CLEARED_ONLY`)
- `recommended_next_lane`: `NOT_COMPUTABLE`
- `operator_attestations_present`: **false** (harness implementation authorization still denied)

Intake clearance is observed; a **separate** governed lane with `authorize_harness_implementation=true` is required before any harness implementation authorization.

## Intake procedure

1. **Canonical draft envelope (cleared):** `operator_input/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.json`
   - Status: `OPERATOR_ATTESTATION_INTAKE_CLEARED`
   - Distinct from the ODR-aligned example template at `operator_input/templates/abx_codegen_shadow_replay_harness_operator_attestation_payload_001.example.json`

2. Run envelope preflight:

```bash
python scripts/preflight_abx_codegen_shadow_replay_harness_operator_attestation_payload.py
```

3. Run intake gate (observes cleared payload and ODR review):

```bash
python scripts/run_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate.py
```

Expected: `ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE_VALIDATED` with `downstream=INTAKE_CLEARED_ONLY`.

4. Review upstream artifacts before completing attestation:
   - `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_implementation_authorization_gate_001.latest.json`
   - `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_dry_run_001.latest.json`
   - `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_plan_001.latest.json`

4. Allowed operator decisions (planning-only in this lane):
   - `APPROVE` — does **not** auto-authorize implementation; requires separate authorization record
   - `REJECT` — blocks implementation path
   - `REQUEST_REFINEMENT` — routes back to proposal refinement
   - `ESCALATE_TO_META_GATE` — requires meta-gate authorization record planning
   - `DEFER` — holds for more evidence (default in example template)

5. Harness implementation authorization requires a **future separate governed lane** with explicit `authorize_harness_implementation=true`. Intake clearance alone does not authorize implementation.

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
| Intake gate | `out/audit/abx_codegen_shadow_replay_harness_operator_attestation_intake_gate_001.latest.json` |
| Continuation audit | `docs/releases/POST_2_5_0_CONTINUATION_AUDIT.md` |
| Continuation plan | `docs/releases/POST_MERGE_738_CODEGEN_ATTESTATION_CONTINUATION_PLAN.md` |
