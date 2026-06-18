# ABRAXAS Repository Status

> **Last Updated:** 2026-06-18

This document provides a high-level operational status of the Abraxas v2.0 repository. It is intended to be human- and agent-readable.

## Current Overall State

| Area                    | Status          | Last Major Change                              | Notes |
|-------------------------|-----------------|------------------------------------------------|-------|
| CI/CD Stability         | Excellent       | Reusable workflows + cleanup of all temp flags | Very clean and efficient |
| Governance              | Strong          | PR/Issue templates + CODEOWNERS                | Good foundation in place |
| Automation & Tooling    | Excellent       | organize_scripts.py + completions + benchmarks | Strong tooling + performance testing |
| Security Posture        | Strong          | CodeQL + Dependency Review blocking            | Proper gates |
| Documentation           | Excellent       | Post-P95 sync/hold status alignment            | Advisory-only status is explicit |
| Release Process         | Excellent       | Full semantic-release with release.config.js   | Fully automated |

## Current Governance Boundary

The current repo-visible continuation state is advisory-only. Repo/Notion sync artifacts have been refreshed, but they do not authorize live Notion writeback, GitHub writeback automation, auto-continuation, runtime mutation, scheduler mutation, canon mutation, activation, or execution.

`Global Ingest Adapter Spine` has advanced to additive Oracle Signal shadow intake evidence and a review-only operator decision record. Oracle Signal runner is observed at `scripts/run_oracle_signal_intake_boundary.py` (delegates to `Scripts/` implementation). Oracle Signal implementation, ingest runner mutation, queue mutation, route/runtime integration, and execution authority remain blocked until a separate future governed lane explicitly authorizes more.

`Controlled Ingest Scheduler` has a review-only operator record at `out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.json`. The record accepts the scheduler governance audit as reviewed evidence only and keeps scheduler/runtime mutation, ingest runner mutation, queue mutation, canon mutation, writeback, token minting, and execution authority blocked.

`Auto Ingest` has a review-only shadow stabilization record at `out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.json`. The record accepts the validation pack as reviewed evidence only and keeps activation, implementation, runtime mutation, scheduler mutation, queue mutation, forecast authority, canon mutation, writeback, token minting, and execution authority blocked.

Current Oracle Signal shadow review evidence:
- `out/oracle/oracle_signal_intake_receipt.latest.json` is advisory-only and not valid for execution.
- `out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json` requested governed review of the shadow receipt.
- `out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json` approves review-only completion and keeps downstream `NOT_COMPUTABLE`.

The operator authorization record chain is present through the P95 seal review. `out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json` is held for operator review and keeps approval, authorization, token minting, record creation, and execution authority false.

Post-registry-repair advisory chains are sealed on `main` with downstream `NOT_COMPUTABLE`: registry coverage repair (`RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_SEALED`), orphan exclude policy (`ORPHAN_POLICY_GOVERNANCE_SEALED`), operator-authorized orphan inclusion A4b (`ORPHAN_INCLUSION_GOVERNANCE_SEALED`; orphan count 0 via derived-optional registration), traceability audit regeneration (`TRACEABILITY_AUDIT_REGENERATION_COMPLETE`), artifact-lineage frontier revalidation (`ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_COMPLETE`), and artifact-lineage chain closure (`ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_SEALED`). Consolidated synthesis receipt at `out/operator_review/abx_post_registry_repair_governance_synthesis_receipt_001.latest.json` records cross-chain invariants (`POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_SEALED`; P130 hold preserved, no P131, separate A4a/A4b branches, no spine refresh). These surfaces do not authorize activation, execution, runtime/canon/queue mutation, or Notion/GitHub writeback.

`Runtime Integration Gate` operator attestation (PR #698) is advisory-only: `out/audit/runtime_integration_gate_operator_review_decision_record_001.latest.json` is operator-attested (`RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_ATTESTED`) and denies `mandatory_pre_dispatch_wiring`; terminal hold receipt `out/audit/runtime_integration_gate_operator_review_decision_record_hold_receipt_001.latest.json` compresses downstream to `NOT_COMPUTABLE`.

`v2 Hygiene Phase 1 Stabilization` operator attestation (PR #698) is advisory-only: `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_operator_decision_record_001.latest.json` records five attestation groups under `terminal_snapshot_strategy`; hold receipt `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt_001.latest.json` is a terminal compression hold with downstream `NOT_COMPUTABLE`. No hygiene implementation, schema mutation, or module registration is authorized.

Hygiene phase8–phase25 hash chain is consistent on `main` after PR #700 phase10–phase25 cascade refresh (phase10 gate `37f21b4b821085d60256757fcf260893a688a328e686e35769fae6bea3450502` through phase25 gate `6abc67d00913b66dcb71117923c10198538bc821d3f8aa4ef50752d67652e064`). Package-lock hygiene remains `HELD_VALIDATION_FAILED` at `out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_001.latest.json` (advisory-only; no lockfile mutation). Artifacts remain advisory-only.

Temporal continuity spine observation advanced P76→P81: P76 `UPSTREAM_INPUTS_MISSING`; P77 dry-run `DRY_RUN_READY_WITH_MISSING_INPUTS`; P78 execution plan `EXECUTION_PLAN_READY`; P79 authorization gate `AUTHORIZATION_ELIGIBLE`; P80 authorization record plan `AUTHORIZATION_RECORD_PLAN_READY`; P81 operator authorization record template `OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_READY` routing to P82 dry run. P82→P95 operator authorization record chain re-observed: dry run through seal review reaches `OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_REVIEW_HELD_FOR_OPERATOR` with downstream `NOT_COMPUTABLE`; no authorization granted. P55/P56/P67/P68 narrative archive degradation persists; `out/audit/operator_narrative_archive_chain_global_verification_001.latest.json` observes `GLOBAL_VERIFICATION_FAIL`. Spine precheck routes to `P71_TEMPORAL_CONTINUITY_SPINE_BINDER_CONTRACT` with archive/coherence blockers inherited. No runtime spine readiness or repair execution authority is claimed.

Post-#701 merge (2026-06-18): `PLANS.md` phase15–phase25 hash prose aligned; `operator_input/governed_authorization_phase30_live_hyperstition.json` cascade hashes refreshed (`authorization_hash` `a249911bb6cfddc7989b0b5618abceaef2a95062bdc263b37323ebc9a6fa0c2f`); phase25 gate `6abc67d00913b66dcb71117923c10198538bc821d3f8aa4ef50752d67652e064`. Evidence-only operator attestation preflight re-validated phase12 payload and stabilization attestation intake (`ATTESTATION_INTAKE_VALIDATED_FOR_FUTURE_DECISION_RECORD_GATE`); stabilization approval intake chain and terminal hold consolidation re-observed with authority denied; phase12/phase13 hash chain preserved on `main` (no artifact hash drift committed).

Temporal continuity spine binder observation (post-#701): P71 binder contract `CONTRACT_READY_WITH_DEGRADED_EVIDENCE`; P72 binder readiness `READY_WITH_DEGRADED_EVIDENCE` routing to P73 evidence index; archive/coherence blockers inherited (P55/P56/P67/P68 degraded, missing `out/audit/temporal_coherence_chain_001.latest.json`). No runtime spine readiness claimed.

Post-#702 merge (2026-06-18): Operator Hold Ledger published; delegated human approval applied via existing `operator_input` payloads. All stabilization preflights valid (attestation + six approval payloads including creation); five approval intake gates and terminal hold consolidation re-observed with authority denied; stabilization attestation intake gate hash refreshed (`cb70c1c0…`) to align `source_terminal_hold_consolidation_hash`; phase12/phase13 hash chain preserved (no phase12 regen committed).

Temporal continuity spine observation (post-#702): P73 evidence index `MISSING_EVIDENCE_INDEXED`; P74 restoration plan `RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE`; P75 generator discovery `GENERATORS_OBSERVED_WITH_MISSING_PREREQUISITES`; P76 upstream restoration `UPSTREAM_INPUTS_MISSING`; P77 dry-run plan `DRY_RUN_READY_WITH_MISSING_INPUTS` (blocking input: `out/audit/temporal_coherence_chain_001.latest.json`; `safe_to_execute: false`); P78 execution plan `EXECUTION_PLAN_READY`; P79 authorization gate `AUTHORIZATION_ELIGIBLE`; P80 authorization record plan `AUTHORIZATION_RECORD_PLAN_READY` routing to P81 template. Archive/coherence blockers inherited; no `run_temporal_coherence_chain.py` execution or runtime spine readiness claimed.

Post-#703 merge (2026-06-18): PR #703 merged to `main` (`9900192a`); stabilization attestation intake gate hash `cb70c1c055dd2ec52c8dbe8c9a53b31909f3feb727266616905fed7033c205fc` and extended Operator Hold Ledger (P102F, compression audit, creation-approval gap) now on `main`. Stabilization intake chain re-observed post-merge: attestation + five approval intake gates + terminal hold consolidation — all hash-stable (no artifact drift committed); phase12/phase13 hash chain preserved.

Operator authorization record chain re-observation (post-#703): P81 template through P95 seal review re-run from P80 routing (`AUTHORIZATION_RECORD_PLAN_READY` → P81). P82–P94 planning/dry-run/validation surfaces emitted ready statuses; P95 terminal hold confirmed (`OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_REVIEW_HELD_FOR_OPERATOR`, downstream `NOT_COMPUTABLE`). All P81–P95 artifacts hash-stable on re-observation. P80 upstream-regen authorization record plan and P81–P95 generic operator authorization record template chain are both advisory-only; neither grants execution, token minting, or authorization record creation. No P79/P80 repair routes triggered.

Archive observation (post-#703, read-only): `out/audit/operator_narrative_archive_chain_global_verification_001.latest.json` observes `GLOBAL_VERIFICATION_FAIL` (P56 continuity `FAIL`, pytest failure in verification receipt). Canon resume blockers persist: P55 `CLOSURE_RECEIPT_DEGRADED`, P56 `FAIL`, P67 `PACKAGE_STABILITY_RECEIPT_DEGRADED`, P68 `STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED`. Missing `out/audit/temporal_coherence_chain_001.latest.json` remains the blocking upstream input for P77/P78. No archive repair, narrative package regeneration, or `run_temporal_coherence_chain.py` execution performed or authorized.

Repo debug triage (2026-06-18, PR #704): **Tier 1 fixes applied** — commitlint body wrap for #704; `status-pages.yml` Node setup fixed (removed invalid `restore-keys` and broken root `package-lock.json` cache). **CI path-filter note:** docs-only merges to `main` trigger `ci.yml` with zero jobs (path filters exclude `STATUS.md`/`AGENTS.md`/`out/**`); GitHub reports 0s failure — this is a skip misreport, not a workflow syntax error. **Fast CI passes** (filtered pytest + drift + ruff + pyright). **Full `pytest -q` fails** (20 failures at `--maxfail=20` across artifact-lineage sealed-chain tests and `test_generated_artifact_registry.py` orphan-classification assertions); fast CI excludes these via `slow`/`canon`/`artifact` markers in `tests/conftest.py`. **P64 manifest gate:** 24/26 consistent; P57 global verification JSON/md hash mismatch against package manifest. **P56 replay drift (technical):** in-process P52/P53 regeneration produces different hashes than committed baselines (`archive_index_hash` replay `cab10ce2…` vs baseline `12809f78…`; governance audit replay `09e0cb45…` vs baseline `c71a4431…`) → `final_status: FAIL` instead of designed `STABILITY_RECEIPT_DEGRADED`. **Missing coherence inputs:** `out/audit/temporal_coherence_chain_001.latest.json` absent (`.md` only, `BLOCKED`); `out/projections/coherence_field_operator_surface_001.latest.json` and `out/projections/temporal_resonance_coherence_001.latest.json` also absent (`.md` only). Archive repair and `run_temporal_coherence_chain.py` execution remain forbidden without operator authorization lane.

## Operator Hold Ledger (human decision required)

The following frontiers remain `HELD_FOR_OPERATOR` or blocked. Agents may refresh evidence-only intake/attestation receipts but **must not** grant execution authority, authorization, token minting, runtime wiring, or canary activation.

| Frontier | Artifact | Required disposition | Agent may refresh evidence only? |
|----------|----------|----------------------|----------------------------------|
| P95 temporal seal review | `out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json` | Human: `CREATE_OPERATOR_AUTHORIZATION_RECORD_DECISION_OR_HOLD`; missing `operator_authorization_record_decision_evidence` (no intake consumer) | No — structural hold in P95 runner |
| P102F operator decision reconciliation | `out/temporal_continuity_operator_authorization_record_decision_reconciliation_receipt/latest.json` | Human: `CREATE_OPERATOR_AUTHORIZATION_RECORD_DECISION_OR_HOLD`; `OPERATOR_AUTHORIZATION_RECORD_DECISION_EVIDENCE_MISSING` hardcoded in P102F runner | No — no intake consumer lane |
| P130 research canary | `out/research_canary_final_activation_authorization_review/latest.json` | Formal hold preserved; no P128→P130 replay without validated operator lane | No — do not regenerate `out/research_canary_*` |
| Runtime integration dry-run review | `out/audit/runtime_integration_gate_operator_review_dry_run_review_001.latest.json` | External operator attestation; no `operator_input` template | No |
| Belief graph ODR review | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_001.latest.json` | Operator decision on seal receipt chain | No |
| Codegen phase1 evidence dry-run review | `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_001.latest.json` | Operator evidence attestation | No |
| v2 hygiene phase1 compression audit | `out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json` | `HOLD_FOR_OPERATOR_REVIEW`; `operator_input_required: true`; terminal operator-authorization hold — no `operator_input` template | No |
| Stabilization creation approval | `operator_input/v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload_001.json` | Preflight validated; no `creation_approval_intake_gate` runner exists | Preflight only — no intake gate |
| Stabilization attestation intake | `out/operator_review/v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.json` | Validated for future decision-record gate only | Yes — intake refresh only |
| Phase12 external attestation | `out/operator_review/v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_001.latest.json` | Records activation classes; denies execution | Yes — gate regen from `operator_input` payload |

Global ingest adapter spine implementation spec remains `GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_CONSUMED_ADVISORY_ONLY`; belief graph gap analysis remains `BELIEF_GRAPH_ENGINE_GAP_ANALYSIS_PLAN_READY`. Oracle shadow intake observed via `scripts/run_oracle_signal_intake_boundary.py` (advisory-only).

Belief Graph Engine has an audit-only gap-analysis plan at `out/audit/belief_graph_engine_gap_analysis_plan_001.latest.json`, an advisory spec plan at `out/audit/belief_graph_engine_advisory_spec_plan_001.latest.json`, an advisory receipt contract plan at `out/audit/belief_graph_engine_advisory_receipt_contract_plan_001.latest.json`, an advisory receipt implementation plan at `out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.json`, an advisory receipt implementation authorization gate at `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_gate_001.latest.json`, an advisory authorization record plan at `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_001.latest.json`, an advisory authorization record creation plan at `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.json`, an advisory record creation authorization gate at `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.json`, an advisory record creation record plan at `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan_001.latest.json`, an advisory authorization-chain compression audit at `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.json`, an advisory seal receipt plan at `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_001.latest.json`, an advisory seal receipt dry run at `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.json`, an advisory seal receipt review at `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review_001.latest.json`, an advisory seal receipt operator decision record plan at `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan_001.latest.json`, an advisory seal receipt operator decision record dry run at `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run_001.latest.json`, and an advisory seal receipt operator decision record review at `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_001.latest.json`. Belief Graph primitives are observed, but these surfaces reject further redundant record-creation recursion, hold seal receipt review for operator decision, plan future operator decision record requirements only, dry-run the simulated record shape only, and hold the simulated record review for external operator attestations; they create no decision record, create no seal receipt, mint no token, and grant no receipt code creation or engine implementation authority. Implementation, execution, runtime/canon/queue/scheduler mutation, forecast routing, Notion writeback, and GitHub writeback remain denied.

## Known Temporary Measures

All major temporary `continue-on-error` flags have been removed.

## Recent Major Improvements (June 2026)

- Refreshed repo/Notion advisory sync artifacts after the P95 authorization seal review merge
- Added/merged P81-P95 operator authorization record planning and seal-review surfaces, all advisory-only and held for operator
- Added release.config.js for semantic-release customization
- Integrated semantic-release for fully automated releases
- Reusable workflows and organize_scripts.py enhancements
- All temporary stabilization flags cleaned up
- CI and documentation improvements

## Current CI Health Summary

Fast CI (`run_fast_ci.py`) passes on `main` for filtered pytest, drift, ruff, and pyright. `status-pages` workflow was failing on every `main` push due to invalid `setup-node` cache config (fixed in PR #704). Docs-only merges may show `ci.yml` as failed with 0 jobs — path-filter skip, not a syntax error. Full unfiltered `pytest -q` and P57 global verification remain red (see repo debug triage above). P64 manifest gate reports P57 hash mismatch until archive chain is re-sealed under a governed repair lane.

## Governance & Process

- Strong tooling ecosystem
- Fully automated semantic release process
- Excellent documentation navigation

## How Releases Work Now

Pushes to `main` following Conventional Commits will automatically:
- Analyze commits and determine next version
- Update CHANGELOG.md
- Commit the changelog back to the repository
- Create Git tag and GitHub Release

## How to Update This File

Update when major changes occur.
