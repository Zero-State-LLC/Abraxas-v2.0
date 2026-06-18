# AGENTS OPERATING DOCTRINE

This repository is governed, deterministic, and fail-closed. Agents must preserve advisory/projection behavior and never escalate authority.

## Mandatory pre-change reads

Before proposing or making changes, coding agents must read:

1. `README.md`
2. `PLANS.md`
3. Latest relevant artifacts under `out/` for the target lane

## Current canonical edge

- Treat P27–P31 as sealed (`COMPLETE_AND_STABLE`) unless a fresh audit/test run proves breakage.
- Current coding edge is post-P130 (`P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW`), with P40/P42 planning-gate surfaces present.
- Implemented research-canary continuity chain is P103→P130, and regenerated artifacts now exist under `out/research_*/latest.json` for those lanes.
- Registry coverage repair chain (#681–#688) is sealed on `main`; do not reopen registry repair or refresh research-canary spine artifacts without separate governed operator review. Track A4b orphan inclusion was operator-authorized separately (`ORPHAN_INCLUSION_CHAIN_COMPLETE`); do not merge into sealed repair chain closure.
- Orphan output registry policy governance is sealed (`ORPHAN_POLICY_GOVERNANCE_SEALED`). Track A4b orphan registry inclusion is operator-authorized separately (`ORPHAN_INCLUSION_GOVERNANCE_SEALED`); 10 paths registered as derived optional via `ORPHAN_INCLUSION_CHAIN_COMPLETE`; do not merge into sealed repair chain closure.
- Artifact-lineage direct repair chain is sealed (`ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_SEALED`); traceability regeneration and frontier revalidation are complete; do not reopen artifact-lineage repair without separate operator review. Post-registry-repair synthesis receipt consolidates all six sealed chains; advisory-only; does not grant authority.
- P130 currently routes to governance hold lane `P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HOLD` and does not authorize activation or execution.
- Controlled ingest scheduler and runtime handoff lanes are now present on `main` through `PATCH-ABX-AUTO-INGEST-002` and `PATCH-ABX-AUTO-INGEST-003`.
- Oracle Signal intake boundary runner is present at `scripts/run_oracle_signal_intake_boundary.py` for additive-shadow observation only; it does not grant ingest, queue, runtime, or execution authority.
- Runtime Integration Gate operator attestation chain (PR #698) is advisory-only: `out/audit/runtime_integration_gate_operator_review_decision_record_001.latest.json` is operator-attested and denies `mandatory_pre_dispatch_wiring`; terminal hold `out/audit/runtime_integration_gate_operator_review_decision_record_hold_receipt_001.latest.json` routes downstream `NOT_COMPUTABLE`.
- v2 hygiene Phase 1 stabilization operator decision record (PR #698) is advisory-only: `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_operator_decision_record_001.latest.json` with terminal hold receipt; no hygiene implementation authority.
- Hygiene phase8–phase14 pinned-hash cascade refreshed on `main` via PR #698; artifacts remain advisory-only.
- Hygiene phase10–phase25 pinned-hash cascade refreshed on `main` via PR #700; phase25 governed-authorization hash refreshed post-cascade; artifacts remain advisory-only.
- Temporal continuity spine P76–P81 observation on `main` (PR #700): P80 `AUTHORIZATION_RECORD_PLAN_READY`; P81 template `OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY` routes to P82 dry run; archive/coherence blockers persist; no runtime spine readiness claimed.
- Treat `out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json`, `out/ingest/runtime_handoff_receipt_set_001.latest.json`, and `out/ingest/oracle_intake_queue_001.latest.json` as advisory-only SHADOW evidence surfaces.
- Do not treat ingest scheduler decisions, runtime handoff receipts, source pull receipts, or Oracle intake queue packets as live execution authorization; they remain non-authoritative until a separate governed operator review or later canon lane explicitly allows more.
- No P131 is implemented or planned by this documentation sync patch; future operational activation requires separate governance design outside P101–P130.
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
- After P102C emits a selected repair execution plan, run `python scripts/run_temporal_continuity_selected_repair_execution_authorization_gate.py` to emit `out/temporal_continuity_selected_repair_execution_authorization_gate/latest.json`. P102D is eligibility-only and never grants execution authority.
- After P102D emits an eligibility-only authorization gate, run `python scripts/run_temporal_continuity_selected_repair_execution_authorization_record_plan.py` to emit `out/temporal_continuity_selected_repair_execution_authorization_record_plan/latest.json`. P102E plans the required human/operator authorization-record decision only and never creates records, grants authorization, or grants execution authority.
- After P102E emits an operator-decision-only authorization record plan, run `python scripts/run_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt.py` to emit `out/temporal_continuity_operator_authorization_record_decision_reconciliation_receipt/latest.json`. P102F reconciles repo-observed P102E against operator-decision evidence and must keep any P103-like route `NOT_COMPUTABLE` unless explicit operator decision evidence exists.
- If historical P103–P107 continuity state is disputed, run `python scripts/run_temporal_continuity_historical_recovery_audit.py` to emit `out/temporal_continuity_historical_recovery_audit/latest.json`. P102G is historical-audit-only and must not create P103, approval records, authorization records, decision records, execution paths, or downstream continuity lanes.
- If a user asks for audit/docs-only work, do not perform feature implementation.
- Documentation/status alignment receipts (`DOCUMENTATION_ALIGNMENT_RECEIPT_001`, `STATUS_REGENERATION_RECEIPT_001`) are advisory-only sync evidence. They may update README/PLANS/AGENTS/status wording and badges from repo-visible evidence, but they must not authorize execution, research canary activation, artifact-lineage repair implementation, Notion/GitHub writeback, canon mutation, runtime mutation, scheduler mutation, queue mutation, or forecast routing.
- Preserve documentation alignment baselines unless a future deterministic status/audit surface proves otherwise: `governance_status=FROZEN`, `canon_status=ADVISORY_ONLY`, continuity `lane_count=58`, highest observed continuity lane `P102G`, and unsupported downstream claims `NOT_COMPUTABLE`.
- Operator-sync, Oracle planning, and artifact-lineage repair planning surfaces remain non-authoritative: Global Ingest requires governed operator decision, Oracle confidence calibration cannot grant truth/authorization, and direct artifact-lineage repair validation planning is not repair execution.

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

## CLI Operator Layer

Before asking an AI agent to inspect or modify the repo, prefer targeted CLI operators.

- `OP.SEARCH_SIGNAL`
- `OP.FIND_PATH`
- `OP.JSON_EXTRACT`
- `OP.YAML_EXTRACT`
- `OP.PR_CONTROL`
- `OP.DIFF_COMPRESS`
- `OP.REPO_PACK`
- `OP.STRUCTURAL_SEARCH`
- `OP.STATIC_SCAN`
- `OP.LOC_METRIC`

Rule: "Send AI the smallest complete evidence packet, not a full repo dump."

Reference: `docs/workflows/cli-operator-layer.md`


## Research canary spine-refresh isolation guardrail

**Rule:** Do NOT regenerate `out/research_canary_*` artifacts during a spine-refresh run unless the full canary chain (P128 source → P129 → P130) is intentionally replayed from a validated, current P128 source.

**Mechanism of failure:** The spine-refresh scripts (`run_temporal_continuity_spine_binder_contract.py` and related) regenerate all artifacts that share a dependency chain with the binder contract. If `out/research_canary_*` artifacts are included in that sweep and P128 is stale or degraded, all 25 canary artifacts are downgraded (e.g., `COMPLETE_AND_STABLE` → `NOT_COMPUTABLE`) — degrading P129 and triggering a cascading CI failure.

**Correct procedure:**
- Run spine-refresh scripts in isolation, scoped only to the temporal-continuity chain.
- Before any spine-refresh, confirm that `out/research_canary_activation_readiness_evidence_record/latest.json` (`P129`) and `out/research_canary_final_activation_authorization_review/latest.json` (`P130`) will NOT be touched by the run.
- If canary artifacts are accidentally degraded, restore them from the last known good commit (do not regenerate from current inputs unless P128 is confirmed valid).

**Current canary chain state:** P129=`CANARY_ACTIVATION_READINESS_EVIDENCE_RECORD_EMITTED` · P130=`FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HELD_FOR_OPERATOR` · hold=`FORMAL_HOLD_RECORD_EMITTED` · `advisory_only: true`.

---

## PR validation discipline

Before opening or updating a PR, run:

```bash
python scripts/run_fast_ci.py
```

This enforces deterministic fast checks (artifact validation-only + drift, fast pytest subset, Ruff, Pyright) without full artifact regeneration.
Do not treat schedule/manual workflow runs as fast-ci substitutes; those are canon-validation lanes.
