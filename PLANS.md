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

- Current implementation edge is **post-P35**.
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
- Do not resume at P27 and do not redo P27–P35 unless audit/tests fail.

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
