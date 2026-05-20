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
- After P75 generator discovery plan, run `python scripts/run_temporal_continuity_upstream_input_restoration_plan.py` to emit `out/temporal_continuity_upstream_input_restoration_plan/latest.json`. Do not claim runtime spine readiness unless `upstream_restoration_plan_status` permits the implementation planning gate and `recommended_next_lane = P77_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`.
- After P76 upstream input restoration plan, run `python scripts/run_temporal_continuity_upstream_input_regeneration_dry_run_plan.py` to emit `out/temporal_continuity_upstream_input_regeneration_dry_run_plan/latest.json`. Do not claim runtime spine readiness unless `dry_run_plan_status` permits the implementation planning gate and `recommended_next_lane = P78_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE`.
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
