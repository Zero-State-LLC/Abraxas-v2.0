# PLANS — CURRENT CANONICAL ROADMAP

## Sealed baseline (current canonical chain)

Completed and stable:

- P27 Temporal Resonance Coherence
- P28 Coherence Field Operator Surface
- P29 Operator Attention Weather
- P30 Operator Review Routing Enhancer
- P31 Operator Attention Ledger

P31 canonical commit reference (Notion-provided): `06057d9` (`feat(p31): add operator attention ledger`).

## Current edge

- Current implementation edge is **post-P130** (`P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW`).
- Implemented research-canary continuity chain is **P103 → P130**.
- Regenerated artifact spine now includes `out/research_*/latest.json` artifacts for P103→P130.
- P130 currently routes to governance hold lane `P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HOLD` and does not authorize activation or execution.
- Controlled ingest advisory lanes are present on `main`: `PATCH-ABX-AUTO-INGEST-002` (scheduler + windowing + governance audit) and `PATCH-ABX-AUTO-INGEST-003` (scheduler-to-runtime SHADOW handoff executor).
- Current ingest frontier is operator review of the advisory scheduler/handoff chain, not live execution authority: `out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json` recommends `CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW`, while `out/ingest/oracle_intake_queue_001.latest.json` remains `SHADOW_HANDOFF_ONLY`.
- P130 does not authorize production activation, execution, runtime mutation, scheduler mutation, canon promotion, forecast influence, or token minting; it is not valid for execution and keeps activation/authorization booleans false.
- No P131 is introduced in this patch; any operational activation path requires separate governance design outside P101–P130.
- P40 and P42 planning-gate documents are present and remain non-authoritative roadmap surfaces.
- Next work must begin with an explicit planning/audit pass.
- Canon continuity precheck now runs through `scripts/run_canon_resume_state.py` (`out/canon_resume_state/latest.json`) before any new subsystem lane work.
- After canon resume state, run `python scripts/run_temporal_continuity_spine_precheck.py` to emit `out/temporal_continuity_spine_precheck/latest.json`.
- If precheck recommends binder-contract work, run `python scripts/run_temporal_continuity_spine_binder_contract.py` to emit `out/temporal_continuity_spine_binder_contract/latest.json`.
- After the binder contract, run `python scripts/run_temporal_continuity_binder_readiness_audit.py` to emit `out/temporal_continuity_binder_readiness_audit/latest.json`.
- After P72 binder readiness audit, run `python scripts/run_temporal_continuity_evidence_index.py` to emit `out/temporal_continuity_evidence_index/latest.json`. Do not claim runtime spine readiness unless `evidence_index_status = EVIDENCE_READY` and `recommended_next_lane = P74_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`.
- After P73 evidence index, run `python scripts/run_temporal_continuity_missing_evidence_restoration_plan.py` to emit `out/temporal_continuity_missing_evidence_restoration_plan/latest.json`. Do not claim runtime spine readiness unless `restoration_plan_status = RESTORATION_NOT_REQUIRED`, degraded evidence is cleared, and `recommended_next_lane = P75_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`.
- After P74 missing evidence restoration plan, run `python scripts/run_temporal_continuity_generator_discovery_plan.py` to emit `out/temporal_continuity_generator_discovery_plan/latest.json`. Do not claim runtime spine readiness unless `generator_discovery_status` allows a planning gate and `recommended_next_lane` is either `P76_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN` (all generators observed with prerequisites) or `P76_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE` (generator discovery not required with no degraded evidence).
- After P75 generator discovery plan, run `python scripts/run_temporal_continuity_upstream_input_restoration_plan.py` to emit `out/temporal_continuity_upstream_input_restoration_plan/latest.json`. Do not claim runtime spine readiness unless `upstream_restoration_plan_status = UPSTREAM_RESTORATION_NOT_REQUIRED`, degraded evidence is cleared, and `recommended_next_lane = P77_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`.
- After P76 upstream input restoration plan, run `python scripts/run_temporal_continuity_upstream_input_regeneration_dry_run_plan.py` to emit `out/temporal_continuity_upstream_input_regeneration_dry_run_plan/latest.json`. Do not claim runtime spine readiness unless `dry_run_plan_status` permits the implementation planning gate and `recommended_next_lane = P78_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`.
- After P77 upstream input regeneration dry-run plan, run `python scripts/run_temporal_continuity_upstream_input_regeneration_execution_plan.py` to emit `out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json`.
- After P78 upstream input regeneration execution plan, run `python scripts/run_temporal_continuity_upstream_input_regeneration_authorization_gate.py` to emit `out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json`. Do not claim runtime spine readiness unless `authorization_gate_status` routes to a non-execution planning gate and `recommended_next_lane = P80_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`.
- After P79 authorization gate, run `python scripts/run_temporal_continuity_upstream_input_regeneration_authorization_record_plan.py` to emit `out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json`. Do not claim authorization, execution, or runtime spine readiness unless a future explicit operator authorization record and governed execution lane are created separately.
- After P80 authorization record plan emits `NOT_COMPUTABLE`, run `python scripts/run_temporal_continuity_authorization_record_plan_source_status_audit.py` to emit `out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json`. Use `source_chain_status` and `recommended_next_lane` before any P81 template work.
- After P81 source-status audit routes to P79 source repair, run `python scripts/run_temporal_continuity_p79_authorization_gate_source_repair_plan.py` to emit `out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json`. Use `p79_source_repair_plan_status` and `recommended_next_lane` before attempting P79/P80 regeneration or template work.
- After P82 routes to P79 status repair, run `python scripts/run_temporal_continuity_p79_authorization_gate_status_repair_plan.py` to emit `out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json`. Use `p79_status_repair_plan_status` and `recommended_next_lane` before attempting any P79 repair or regeneration execution planning.
- After P83 routes to P80 authorization record plan regeneration, run `python scripts/run_temporal_continuity_p80_authorization_record_plan_regeneration_plan.py` to emit `out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json`. Use `p80_regeneration_plan_status` and `recommended_next_lane` before attempting any P80 regeneration execution planning.
- After P84 routes to P80 regeneration execution planning, run `python scripts/run_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan.py` to emit `out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json`. Use `p80_regeneration_execution_plan_status` and `recommended_next_lane` before any P86 authorization-gate work.
- After P85 routes back to P84 regeneration planning, run `python scripts/run_temporal_continuity_p84_regeneration_plan_regeneration_plan.py` to emit `out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json`. Use `p84_regeneration_plan_regeneration_status` and `recommended_next_lane` before attempting P84 execution planning.
- After P86 routes to P83 status plan regeneration, run `python scripts/run_temporal_continuity_p83_status_plan_regeneration_plan.py` to emit `out/temporal_continuity_p83_status_plan_regeneration_plan/latest.json`. Use `p83_regeneration_plan_status` and `recommended_next_lane` before attempting P83 regeneration execution planning.
- After P87 routes to P83 regeneration execution planning, run `python scripts/run_temporal_continuity_p83_status_plan_regeneration_execution_plan.py` to emit `out/temporal_continuity_p83_status_plan_regeneration_execution_plan/latest.json`. Use `p83_regeneration_execution_plan_status` and `recommended_next_lane` before any P89 authorization-gate work.
- After P88 routes to P83 regeneration authorization gate, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_gate.py` to emit `out/temporal_continuity_p83_regeneration_authorization_gate/latest.json`. Use `p83_regeneration_authorization_gate_status`, `p83_regeneration_authorization_eligible`, and `recommended_next_lane` before any authorization record planning.
- After P89 routes to P83 regeneration authorization record planning, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_plan.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_plan/latest.json`. Use `p83_regeneration_record_plan_status`, `p83_regeneration_record_required`, and `recommended_next_lane` before any authorization record creation planning.
- After P90 routes to P83 regeneration authorization record creation planning, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_plan.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_plan/latest.json`. Use `p83_regeneration_record_creation_plan_status`, `p83_regeneration_record_creation_required`, and `recommended_next_lane` before any authorization record creation authorization gate.
- After P91 routes to P83 regeneration authorization record creation authorization gate, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate/latest.json`. Use `p83_record_creation_authorization_gate_status`, `p83_record_creation_authorization_eligible`, and `recommended_next_lane` before any authorization record creation record planning.
- After P92 routes to P83 regeneration authorization record creation record planning, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_record_plan/latest.json`. Use `p83_record_creation_record_plan_status`, `p83_record_creation_record_required`, and `recommended_next_lane` before any authorization record creation record creation planning.
- After P93 routes to P83 regeneration authorization record creation record creation planning, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_record_creation_plan.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_record_creation_plan/latest.json`. Use `p83_record_creation_sequence_plan_status`, `p83_record_creation_sequence_required`, and `recommended_next_lane` before any authorization record creation sequence authorization gate.
- After P94 routes to P83 regeneration authorization record creation sequence authorization gate, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate/latest.json`. Use `p83_record_creation_sequence_authorization_gate_status`, `p83_record_creation_sequence_authorization_eligible`, and `recommended_next_lane` before any authorization record creation sequence record planning.
- After P95 routes to P83 regeneration authorization record creation sequence record planning, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan/latest.json`. Use `p83_sequence_record_plan_status`, `p83_sequence_record_required`, and `recommended_next_lane` before any authorization record creation sequence record creation planning.
- After P96 routes to P83 regeneration authorization record creation sequence record creation planning, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_plan.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_plan/latest.json`. Use `p83_sequence_record_creation_plan_status`, `p83_sequence_record_creation_required`, and `recommended_next_lane` before any authorization record creation sequence record creation authorization gate.
- After P97 routes to P83 regeneration authorization record creation sequence record creation authorization gate, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_authorization_gate.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_authorization_gate/latest.json`. Use `p83_sequence_record_creation_authorization_gate_status`, `p83_sequence_record_creation_authorization_eligible`, and `recommended_next_lane` before any sequence record creation record planning.
- After P98 routes to P83 regeneration authorization record creation sequence record creation record planning, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/latest.json`. Use `p83_sequence_record_creation_record_plan_status`, `p83_sequence_record_creation_record_required`, and `recommended_next_lane` before any sequence record creation record creation planning.
- After P99 routes to P83 regeneration authorization record creation sequence record creation record creation planning, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan/latest.json`. Use `p83_sequence_record_creation_record_creation_plan_status`, `p83_sequence_record_creation_record_creation_required`, and `recommended_next_lane` before any sequence record creation record creation authorization gate.
- After P100 routes to P83 regeneration authorization record creation sequence record creation record creation authorization gate, run `python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate.py` to emit `out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate/latest.json`. Use `p83_sequence_record_creation_record_creation_authorization_gate_status`, `p83_sequence_record_creation_record_creation_authorization_eligible`, and `recommended_next_lane` before any P102 compression audit.
- After P101 routes to P102 compression audit, run `python scripts/run_temporal_continuity_recursive_authorization_chain_compression_audit.py` to emit `out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json`. Use `chain_compression_audit_status`, `chain_recommendation`, and `recommended_next_lane` before any further recursive expansion.
- If P102 recommends `SEAL_RECURSIVE_AUTHORIZATION_CHAIN` or `COMPRESS_TO_GENERIC_TEMPLATE`, do not add another hand-written recursive authorization lane. Route to the recommended P103 lane instead.
- After P102 reports `COMPRESSION_AUDIT_DEGRADED` and routes to `P101_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION`, run `python scripts/run_temporal_continuity_p101_readiness_repair_plan.py` to emit `out/temporal_continuity_p101_readiness_repair_plan/latest.json`. Use `p101_readiness_repair_status`, `recommended_next_lane`, and `future_command_sequence` before rerunning P99/P100/P101/P102.
- After P102A emits a readiness repair plan, run `python scripts/run_temporal_continuity_repair_execution_plan_router.py` to emit `out/temporal_continuity_repair_execution_plan_router/latest.json`. Use `p102b_router_status`, `selected_execution_plan_lane`, `selected_command_sequence`, and `recommended_next_lane` before creating any execution-plan-specific P102C lane.
- After P102B emits a selected repair execution plan route, run `python scripts/run_temporal_continuity_selected_repair_execution_plan.py` to emit `out/temporal_continuity_selected_repair_execution_plan/latest.json`. Use `p102c_execution_plan_status`, `selected_branch_type`, `planned_execution_steps`, and `recommended_next_lane` before any execution authorization gate.
- After P102C emits a selected repair execution plan, run `python scripts/run_temporal_continuity_selected_repair_execution_authorization_gate.py` to emit `out/temporal_continuity_selected_repair_execution_authorization_gate/latest.json`. P102D authorizes eligibility only and does not grant execution authority.
- After P102D emits an eligibility-only authorization gate, run `python scripts/run_temporal_continuity_selected_repair_execution_authorization_record_plan.py` to emit `out/temporal_continuity_selected_repair_execution_authorization_record_plan/latest.json`. P102E plans the required human/operator authorization-record decision only and does not create a record or grant execution authority.
- After P102E emits an operator-decision-only authorization record plan, run `python scripts/run_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt.py` to emit `out/temporal_continuity_operator_authorization_record_decision_reconciliation_receipt/latest.json`. P102F reconciles repo-observed P102E against operator-decision evidence and must keep any P103-like route `NOT_COMPUTABLE` unless explicit operator decision evidence exists.
- If historical P103–P107 continuity state is disputed, run `python scripts/run_temporal_continuity_historical_recovery_audit.py` to emit `out/temporal_continuity_historical_recovery_audit/latest.json`. P102G is historical-audit-only and must not create P103, approval records, authorization records, decision records, execution paths, or downstream continuity lanes.
- Do not resume at P27 and do not redo P27–P35 unless audit/tests fail.
- P102 IMPLEMENTED advisory recursive authorization chain compression audit.
- P102A IMPLEMENTED advisory P101 readiness repair plan after degraded P102 compression audit.
- P102B IMPLEMENTED advisory repair execution plan router after P102A readiness repair plan.
- P102C IMPLEMENTED advisory selected repair execution plan.
- P102D IMPLEMENTED advisory selected repair execution authorization gate (eligibility only, no execution authority grant).
- P102E IMPLEMENTED advisory selected repair execution authorization record plan (operator-decision only, no record creation or execution authority grant).
- P102F IMPLEMENTED advisory operator authorization-record decision reconciliation receipt (repo↔Notion reconciliation only, no P103 authorization).
- P102G IMPLEMENTED advisory historical recovery audit for disputed P103–P107 continuity evidence (audit-only, no downstream lane creation).
- P103 IMPLEMENTED advisory research shadow replay audit.
- P104 IMPLEMENTED advisory research boundary decay analysis.
- P105 IMPLEMENTED advisory research promotion blocker ledger.
- P106 IMPLEMENTED advisory research canary eligibility dossier.
- P107 IMPLEMENTED advisory research canary review packet.
- P108 IMPLEMENTED advisory research canary decision record.
- P109 IMPLEMENTED advisory research canary plan draft.
- P110 IMPLEMENTED advisory research canary plan review record.
- P111 IMPLEMENTED advisory research canary authorization draft.
- P112 IMPLEMENTED advisory research canary authorization review record.
- P113 IMPLEMENTED advisory research canary final precheck record.
- P114 IMPLEMENTED advisory research canary authorization package draft.
- P115 IMPLEMENTED advisory research canary authorization package review record.
- P116 IMPLEMENTED advisory research canary authorization decision record.
- P117 IMPLEMENTED advisory research canary authorization denial/hold routing.
- P118 IMPLEMENTED advisory research controlled canary envelope draft.
- P119 IMPLEMENTED advisory research canary runtime observation record.
- P120 IMPLEMENTED advisory research canary rollback termination governance.
- P121 IMPLEMENTED advisory research canary operator go/no-go review.
- P122 IMPLEMENTED advisory research canary activation package draft.
- P123 IMPLEMENTED advisory research canary activation package review record.
- P124 IMPLEMENTED advisory research canary activation decision record.
- P125 IMPLEMENTED advisory research canary activation decision review record.
- P126 IMPLEMENTED advisory research canary activation denial/hold routing.
- P127 IMPLEMENTED advisory research canary activation envelope draft.
- P128 IMPLEMENTED advisory research canary activation envelope review record.
- P129 IMPLEMENTED advisory research canary activation readiness evidence record.
- P130 IMPLEMENTED advisory research canary final activation authorization review boundary (held for operator; non-operative).

## Planning-gate surfaces (not canon yet)

- P40 AAL-Viz Climate + Motif Fusion Overlay: `PLANNING_GATE_PRESENT` for roadmap tracking.
- P42 Operator Narrative Report: `PLANNING_GATE_PRESENT` for roadmap tracking.

Any post-P35 work must be treated as non-canonical planning/exploration until explicitly sealed.

## Acceptance criteria for the next approved plan

The next approved lane must:

1. Consume sealed upstream artifacts and explicitly declare any additional dependencies.
2. Remain deterministic (stable ordering, serialization, and hash behavior).
3. Stay advisory/projection-only and non-authoritative.
4. Include all required delivery surfaces:
   - schema contract
   - runner script
   - tests
   - generated artifact registry entry
   - generated artifacts (`.latest.json` and `.latest.md`) where policy applies
5. Pass full tests and artifact drift checks:
   - `pytest -q`
   - `python scripts/run_artifact_regeneration.py --full --validation-only`
   - `python scripts/run_artifact_regeneration.py --check-drift`


## CI validation operating mode

- Pull requests and day-to-day pushes use fast deterministic validation via `python scripts/run_fast_ci.py`.
- Full canon validation remains mandatory on `main`, nightly, and manual `workflow_dispatch` runs: full artifact regeneration, validation-only pass, drift check, and full `pytest -q`.
- If a change directly touches canon/artifact infrastructure, operators should run full canon validation before merge in addition to fast CI.
