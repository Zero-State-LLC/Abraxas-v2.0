# AGENTS OPERATING DOCTRINE

This repository is governed, deterministic, and fail-closed. Agents must preserve advisory/projection behavior and never escalate authority.

## Mandatory pre-change reads

Before proposing or making changes, coding agents must read:

1. `README.md`
2. `PLANS.md`
3. Latest relevant artifacts under `out/` for the target lane

## Current canonical edge

- Treat P27–P31 as sealed (`COMPLETE_AND_STABLE`) unless a fresh audit/test run proves breakage.
- Current coding edge is post-P35, with P40/P42 planning-gate surfaces present.
- Before new subsystem coding, run `scripts/run_canon_resume_state.py` and consult `out/canon_resume_state/latest.json` as the continuity pointer.
- After canon resume state, run `python scripts/run_temporal_continuity_spine_precheck.py` to emit `out/temporal_continuity_spine_precheck/latest.json`.
- If precheck recommends binder-contract work, run `python scripts/run_temporal_continuity_spine_binder_contract.py` to emit `out/temporal_continuity_spine_binder_contract/latest.json`.
- After the binder contract, run `python scripts/run_temporal_continuity_binder_readiness_audit.py` to emit `out/temporal_continuity_binder_readiness_audit/latest.json`. Do not claim runtime spine readiness unless `readiness_status = READY` and `recommended_next_lane = P73_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING`.
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
- If a user asks for audit/docs-only work, do not perform feature implementation.

## Test execution order

- Run targeted tests first for touched surfaces.
- Run broader/full tests only after targeted checks pass or when explicitly requested.
- If environment constraints block tests, record exact command failures without claiming success.

## Determinism and serialization rules

- Preserve deterministic serialization and hash behavior across packet/artifact writers.
- Never introduce wall-clock, UUID, filesystem-order, randomness, or network dependency into deterministic surfaces.
- Keep canonical ordering and stable field shapes intact.

## Governance and authority boundaries

- Keep SHADOW and FORECAST surfaces separated.
- Keep all advisory/projection surfaces non-authoritative.
- Preserve: advisory_only, projection_only, non_authoritative.
- Deny: mutation, execution, routing authority (unless explicitly advisory-only), forecast authority, canon/runtime/queue mutation.
- No auto-approval, no auto-execution, no adaptive learning unless future canon explicitly allows it.

## Failure and drift reporting

- Record broken surfaces explicitly; never hide or silently bypass them.
- Prefer fail-closed reporting with concrete blocker reasons.
- Do not fabricate artifact/test outcomes.
