# ABRAXAS

```text
   ██████ ██████ ██████  █████ ██   ██ █████ ███████
  ███████ ███████ ███████ ███████ ███████ ███████
  ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██
  ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██
  ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ ██   ██
   █████  ██████  ██████   █████  ██   ██  █████  ███████
```

**Governed Symbolic Intelligence**

Deterministic • Observable • Recursive

![Version](https://img.shields.io/badge/version-2.5.0-0A66C2)

---

<details>
<summary><strong>Table of Contents</strong> (click to expand)</summary>

- [Repository Status](#repository-status)
- [Developer Workflow](#developer-workflow)
- [01. Architecture](#01-architecture)
- [02. Governance](#02-governance)
- [03. Continuity Spine](#03-continuity-spine)
- [04. Evidence Surfaces](#04-evidence-surfaces)
- [05. Routing and Rune Binding](#05-routing-and-rune-binding)
- [06. Repository Signal Surface](#06-repository-signal-surface)
- [07. System Atlas](#07-system-atlas)
- [08. Architecture Diagrams](#08-architecture-diagrams)
- [09. Repository Topology](#09-repository-topology)
- [10. Repo ↔ Notion Reconciliation](#10-repo--notion-reconciliation)
- [11. Roadmap](#11-roadmap)
- [12. Operator Paths](#12-operator-paths)
- [13. Research Domains](#13-research-domains)
- [Optimization](#optimization)
- [14. Shields / GitHub Pages](#14-shields--github-pages)
- [15. Footer](#15-footer)

</details>

---

## Repository Status

**Start here:** New contributors and coding agents should begin with
[`docs/START_HERE.md`](docs/START_HERE.md), then use
[`docs/INDEX.md`](docs/INDEX.md) for master navigation by surface role.
Subsystem routing now lives in
[`docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md`](docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md)
with a receipt-backed repo-native ownership map.
Artifact lifecycle and discoverability posture now routes through
[`docs/artifacts/ARTIFACT_INDEX.md`](docs/artifacts/ARTIFACT_INDEX.md)
and the receipt-first classifier lane anchored by
`out/audit/artifact_registry_classifier_001.latest.json`.
Temporal continuity compression and blocked-route navigation now route through
[`docs/lineage/CONTINUITY_LINEAGE_MAP_002.md`](docs/lineage/CONTINUITY_LINEAGE_MAP_002.md)
and the receipt-backed D3 refresh lane at
`out/audit/continuity_lineage_map_refresh_001.latest.json`.
The rehydrated P75/P76 upstream restoration chain now also routes through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_RESTORATION_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_RESTORATION_ROUTE.md)
and the advisory packaging receipt at
`out/audit/temporal_upstream_restoration_route_refresh_001.latest.json`, making
the current P74 -> P75 -> P76 -> P77 continuity handoff explicit without
opening generator or repair authority.
The P77 dry-run lane is now surfaced directly through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_DRY_RUN_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_DRY_RUN_ROUTE.md)
and `out/audit/temporal_upstream_dry_run_route_refresh_001.latest.json`, so
contributors can route from the tracked P77 packet to P78 planning without
opening execution or regeneration authority.
The P78 execution-planning lane is now surfaced through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_EXECUTION_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_EXECUTION_ROUTE.md)
and `out/audit/temporal_upstream_execution_route_refresh_001.latest.json`, so
contributors can route from the tracked P78 packet to P79 authorization-gate
planning without opening execution authority.
The P79 authorization-gate lane is now surfaced through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_GATE_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_GATE_ROUTE.md)
and `out/audit/temporal_upstream_authorization_gate_route_refresh_001.latest.json`,
so contributors can route from the tracked P79 packet to P80
authorization-record planning without opening authorization or execution
authority.
The missing-P80 authorization-record regeneration route is now surfaced through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_RECORD_REGENERATION_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_RECORD_REGENERATION_ROUTE.md)
and `out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json`,
so contributors can move from the tracked P79 handoff into the real Slice50/Slice51
missing-source and regeneration evidence without treating blocked continuity edges
as implicit or hidden.
The emitted P83 status-repair lane is now surfaced through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_REPAIR_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_REPAIR_ROUTE.md)
and `out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json`,
so contributors can route from the packaged Slice77 blocked-P80 handoff into the
actual emitted P83 packet and then back into the downstream P80 regeneration
planning surfaces without opening repair or authorization authority.
The emitted P84 regeneration-plan lane is now surfaced through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_ROUTE.md)
and `out/audit/temporal_upstream_regeneration_plan_route_refresh_001.latest.json`,
so contributors can route from the emitted P83 packet into the real
`P80_REGENERATION_PLAN_READY` posture and then into the explicit downstream P85
execution-planning handoff without treating the P84 packet as hidden raw output.
The emitted P85 regeneration execution-planning lane is now surfaced through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_EXECUTION_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_EXECUTION_ROUTE.md)
and `out/audit/temporal_upstream_regeneration_execution_route_refresh_001.latest.json`,
so contributors can route from the packaged Slice79 P84 handoff into the real
blocked-yet-observed P85 packet and then into the explicit downstream P86
regeneration-planning surface without inventing execution or authorization authority.
The refreshed emitted P86 regeneration-plan-regeneration lane is now surfaced through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE.md)
and `out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json`,
so contributors can route from the packaged Slice80 P85 handoff into the current
`P84_REGENERATION_NOT_REQUIRED` posture and then preserve the explicit downstream
`P87_TEMPORAL_CONTINUITY_P85_REGENERATION_EXECUTION_PLAN_REGENERATION_PLAN`
handoff without inventing regeneration, execution, or authorization authority.
The repo-real downstream P87 lane is now surfaced through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_ROUTE.md)
and `out/audit/temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json`,
so contributors can route from the packaged Slice81 P86 handoff into the emitted
`p83_status_plan_regeneration` packet family, keep the P87 naming bridge explicit,
and preserve the downstream `P88_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN`
handoff without inventing regeneration, execution, or authorization authority.
The repo-real downstream P88 execution-planning lane is now surfaced through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_ROUTE.md)
and `out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json`,
so contributors can route from the packaged Slice82 P87 handoff into the emitted
`p83_status_plan_regeneration_execution` packet family and preserve the observed
downstream `P89_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN`
handoff without inventing execution or authorization authority.
That observed P89-labelled handoff now also has an explicit contributor-facing
bridge through
[`docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_BRIDGE_ROUTE.md`](docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_BRIDGE_ROUTE.md)
and `out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json`,
which routes the literal downstream label into the existing P84 regeneration-plan
family without creating a parallel execution or governance surface.
Priority 2 subsystem health routing now aggregates ownership, artifact lifecycle,
continuity, migration-runner, and VIZ posture through
[`docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md`](docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md)
and the receipt-backed health packet at
`out/audit/subsystem_health_dashboard_001.latest.json`.
That dashboard now also surfaces the merged held alias-implementation-design
route, so contributors see the current design-only posture instead of a stale
future migration follow-on.
Priority 2 migration tooling and live-console work for this cycle now close
through `out/audit/priority2_live_console_migration_closeout_001.latest.json`,
which routes contributors from the subsystem health dashboard to the continuity
namespace migration status/runbook surfaces and then the AAL-Viz live-console
receipts without reopening execution scope.
Continuity namespace migration tooling now routes through
[`docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md`](docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md)
and the packaging receipt at
`out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json`.
Receipt-driven migration simulation now routes through
[`docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md`](docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md)
and the advisory run receipt at
`out/audit/continuity_namespace_migration_run_001.latest.json`.
Held additive alias implementation design now routes through
[`docs/status/CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md`](docs/status/CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md)
and the advisory design receipt at
`out/audit/continuity_namespace_alias_implementation_design_001.latest.json`.

| Area                        | Status          | Last Major Change                              | Notes |
|-----------------------------|-----------------|------------------------------------------------|-------|
| CI/CD Stability             | Excellent       | Reusable workflows + cleanup of temp flags     | Very clean and efficient |
| Governance                  | Strong          | PR/Issue templates + CODEOWNERS                | Good foundation |
| Automation & Tooling        | Excellent       | organize_scripts.py + completions + release wf | Full modern DX |
| Security Posture            | Strong          | CodeQL + Dependency Review blocking            | Proper gates |
| Documentation               | Good            | Status table + STATUS.md + ToC                 | Well maintained |
| Release Process             | Started         | Reusable create-release workflow               | Foundation ready |
| ABX Codegen Intelligence Spine | Advisory-computable | PRs #797-#803 + Phase 6-9 loop extension | 20/20 required paths observed; authority locks false |

---

### ABX Codegen Intelligence Spine

Status: `ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_COMPUTABLE`

Evidence:
- `out/audit/abx_codegen_intelligence_spine_completion_receipt_001.latest.json`
- `scripts/abraxas_v2.0_codex_governance_loop.py`
- `out/audit/abx_codex_governance_loop_phase_6_post_merge_reconciliation.latest.json`
- `out/audit/abx_codex_governance_loop_phase_7_shadow_runtime_activation_prep.latest.json`
- `out/audit/abx_codex_governance_loop_phase_8_global_ingest_wiring_stub.latest.json`
- `out/audit/abx_codex_governance_loop_phase_9_notion_projection_dryrun.latest.json`
- `out/audit/abx_codegen_phase_10_plus_forward_paths_selector.latest.json`

The governed Codegen loop now supports PHASE_6 through PHASE_9 continuation prompts, receipts, and advisory helper surfaces for post-merge reconciliation, shadow runtime activation prep, Global Ingest wiring stubs, and Notion projection dry runs.

Authority boundary: `CANON_MUTATION=false`, `RUNTIME_MUTATION=false`, `EXECUTION_AUTHORITY=false`, `GITHUB_WRITEBACK=false`, `NOTION_WRITEBACK=false`.

### ABX-LOOP-805 Spine Operationalization

Status: `LOOP805_SLICE44_MEASUREMENT_DRYRUN_DENIAL_CLOSEOUT_RECONCILIATION_READY_ADVISORY_ONLY`

Repo-ledger frontier sync: `ABX_LEDGER_FRONTIER_RECONCILE_DENIAL_READY_ADVISORY_ONLY`

Frontier sync CLI: `python Scripts/abx_ledger_frontier.py --scan --mode=reconcile-denial --commit=7815e720`

Frontier sync receipt: `out/audit/abx_ledger_frontier_reconcile_denial_001.latest.json`

Frontier sync receipt hash: `0b28044325cad08cad70e89f895f4a45729b68f6240fcd7c40b2331e45d77066`

Loop 805 seeds observable operationalization surfaces for the advisory-computable Codegen Spine: baseline token/Brier targets, MCP-shaped `/spine/query`, `/spine/forecast`, and `/spine/audit` projection contracts, held-out Brier fixture telemetry, token optimizer advisory math, plus a PLAN -> EXECUTE -> MEASURE -> ADJUST controller receipt.

Evidence:
- `out/audit/abx_loop_805_operationalization_baseline_001.latest.json`
- `out/audit/abx_loop_805_controller_plan_001.latest.json`
- `out/audit/abx_loop_805_daily_observability_dashboard_001.latest.json`
- `out/audit/abx_loop_805_regression_pr_proposal_001.latest.json`
- `out/audit/abx_loop805_slice2_mcp_exposure_stub.latest.json`
- `out/audit/abx_loop805_slice2_held_out_brier_telemetry.latest.json`
- `out/audit/abx_loop805_slice2_token_optimizer_stub.latest.json`
- `out/audit/abx_loop805_slice2_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice3_activation_proposal.latest.json`
- `out/audit/abx_loop805_slice3_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice3_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice4_gate_selection_matrix.latest.json`
- `out/audit/abx_loop805_slice4_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice4_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice5_brier_attestation_packet.latest.json`
- `out/audit/abx_loop805_slice5_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice5_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice6_fixture_binding_dryrun.latest.json`
- `out/audit/abx_loop805_slice6_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice6_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice7_brier_scoring_shadow_run.latest.json`
- `out/audit/abx_loop805_slice7_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice7_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice8_outcome_policy_review.latest.json`
- `out/audit/abx_loop805_slice8_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice8_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice9_held_out_set_lockfile_proposal.latest.json`
- `out/audit/abx_loop805_slice9_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice9_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice10_held_out_set_attestation_gate.latest.json`
- `out/audit/abx_loop805_slice10_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice10_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice11_measurement_readiness_review.latest.json`
- `out/audit/abx_loop805_slice11_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice11_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice12_measurement_authorization_proposal.latest.json`
- `out/audit/abx_loop805_slice12_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice12_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice13_authorization_evidence_packet.latest.json`
- `out/audit/abx_loop805_slice13_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice13_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice14_fixture_outcome_binding_review.latest.json`
- `out/audit/abx_loop805_slice14_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice14_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice15_measurement_dryrun_authorization_hold.latest.json`
- `out/audit/abx_loop805_slice15_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice15_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice16_measurement_dryrun_preflight_packet.latest.json`
- `out/audit/abx_loop805_slice16_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice16_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice17_measurement_dryrun_decision_request.latest.json`
- `out/audit/abx_loop805_slice17_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice17_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice18_measurement_dryrun_decision_record_template.latest.json`
- `out/audit/abx_loop805_slice18_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice18_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice19_measurement_dryrun_operator_decision_intake_gate.latest.json`
- `out/audit/abx_loop805_slice19_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice19_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice20_measurement_dryrun_operator_decision_intake_packet.latest.json`
- `out/audit/abx_loop805_slice20_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice20_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice21_measurement_dryrun_operator_decision_record_candidate.latest.json`
- `out/audit/abx_loop805_slice21_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice21_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice22_measurement_dryrun_decision_record_review.latest.json`
- `out/audit/abx_loop805_slice22_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice22_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice23_held_out_set_binding_review.latest.json`
- `out/audit/abx_loop805_slice23_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice23_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice24_brier_shadow_resolution_review.latest.json`
- `out/audit/abx_loop805_slice24_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice24_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice25_measurement_dryrun_execution_proposal_stub.latest.json`
- `out/audit/abx_loop805_slice25_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice25_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice26_operator_measurement_execution_gate_review.latest.json`
- `out/audit/abx_loop805_slice26_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice26_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice27_measurement_dryrun_execution_packet_candidate.latest.json`
- `out/audit/abx_loop805_slice27_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice27_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice28_measurement_dryrun_execution_packet_review.latest.json`
- `out/audit/abx_loop805_slice28_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice28_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice29_measurement_dryrun_execution_denial_ledger.latest.json`
- `out/audit/abx_loop805_slice29_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice29_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice30_measurement_dryrun_operator_action_menu.latest.json`
- `out/audit/abx_loop805_slice30_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice30_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice31_measurement_dryrun_operator_selection_review.latest.json`
- `out/audit/abx_loop805_slice31_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice31_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice32_measurement_dryrun_selection_denial_receipt.latest.json`
- `out/audit/abx_loop805_slice32_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice32_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice33_measurement_dryrun_denial_reconciliation_packet.latest.json`
- `out/audit/abx_loop805_slice33_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice33_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice34_measurement_dryrun_operator_handoff_packet.latest.json`
- `out/audit/abx_loop805_slice34_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice34_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice35_measurement_dryrun_operator_handoff_review.latest.json`
- `out/audit/abx_loop805_slice35_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice35_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice36_measurement_dryrun_operator_selection_packet_candidate.latest.json`
- `out/audit/abx_loop805_slice36_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice36_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice37_measurement_dryrun_operator_selection_packet_review.latest.json`
- `out/audit/abx_loop805_slice37_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice37_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice38_measurement_dryrun_operator_selection_packet_denial.latest.json`
- `out/audit/abx_loop805_slice38_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice38_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice39_measurement_dryrun_selection_packet_denial_reconciliation.latest.json`
- `out/audit/abx_loop805_slice39_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice39_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice40_measurement_dryrun_operator_packet_handoff_reconciliation.latest.json`
- `out/audit/abx_loop805_slice40_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice40_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice41_measurement_dryrun_operator_packet_handoff_denial_ledger.latest.json`
- `out/audit/abx_loop805_slice41_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice41_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice42_measurement_dryrun_operator_handoff_final_reconciliation.latest.json`
- `out/audit/abx_loop805_slice42_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice42_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice43_measurement_dryrun_operator_final_denial_summary.latest.json`
- `out/audit/abx_loop805_slice43_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice43_progress_receipt.latest.json`
- `out/audit/abx_loop805_slice44_measurement_dryrun_denial_closeout_reconciliation.latest.json`
- `out/audit/abx_loop805_slice44_prompt_packet.latest.json`
- `out/audit/abx_loop805_slice44_progress_receipt.latest.json`
- `Scripts/abx_loop.py`

Boundary: projection, observability, operator-gated activation proposal, gate-selection advisory matrix, held-out Brier attestation packet, fixture-binding dry-run, Brier scoring shadow-run, outcome-policy review, held-out set lockfile proposal, held-out set attestation gate, measurement readiness review, measurement authorization proposal, authorization evidence packet shape, fixture/outcome binding review, measurement dry-run authorization hold, measurement dry-run preflight shape, measurement dry-run decision request, measurement dry-run decision record template, measurement dry-run operator decision intake gate, measurement dry-run operator decision intake packet, measurement dry-run operator decision record candidate, measurement dry-run decision record review, held-out set binding review, Brier shadow resolution review, measurement dry-run execution proposal stub, operator measurement execution gate review, measurement dry-run execution packet candidate, measurement dry-run execution packet review, measurement dry-run execution denial ledger, operator action menu, operator selection review, selection denial receipt, denial reconciliation packet, operator handoff packet, operator handoff review, operator selection packet candidate, operator selection packet review, operator selection packet denial, selection packet denial reconciliation, operator packet handoff reconciliation, operator packet handoff denial ledger, operator handoff final reconciliation, operator final denial summary, and denial closeout reconciliation only. No live MCP exposure, auto-PR generation, runtime activation, token rewrite enforcement, canon mutation, GitHub/Notion writeback, held-out measurement, measurement dry-run execution, measurement dry-run operator decision intake submission, measurement dry-run decision recording, measurement dry-run authorization, measurement authorization, authorization evidence recording, operator handoff selection recording, operator handoff review selection recording, operator selection packet candidate selection recording, operator selection packet review selection recording, operator selection packet denial selection recording, selection packet denial reconciliation authority promotion, operator packet handoff recording, operator packet handoff reconciliation authority promotion, operator packet handoff denial ledger authority promotion, operator handoff final reconciliation authority promotion, operator final denial summary authority promotion, denial closeout reconciliation authority promotion, operator action selection recording, operator gate recording, operator attestation recording, denial reconciliation authority promotion, Brier shadow resolution, executable measurement dry-run proposal, executable measurement dry-run packet, held-out set attestation, held-out set locking, held-out set binding, fixture binding, outcome policy binding, outcome binding, forecast routing, Brier resolution, or execution authority is granted.

---

### Oracle Signal Layer Canon Extension

Status: `ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED`

Brier Score: 0.10

The Oracle Signal Layer is implemented as an additive canon extension only. New schema surfaces live under `contracts/canon/oracle/` and do not mutate existing root canon files.

Evidence:
- `contracts/canon/oracle/oracle_signal_envelope.v1.schema.json`
- `contracts/canon/oracle/oracle_holler_intake.v1.schema.json`
- `contracts/canon/oracle/oracle_calibration_report.v1.schema.json`
- `contracts/canon/oracle/oracle_adversarial_fixture.v1.schema.json`
- `contracts/canon/oracle/oracle_schema_registry.v1.schema.json`
- `contracts/canon/oracle/oracle_ingest_wiring.v1.schema.json`
- `contracts/canon/oracle/oracle_shadow_dryrun.v1.schema.json`
- `contracts/canon/oracle/oracle_measurement_readiness.v1.schema.json`
- `contracts/canon/oracle/oracle_shadow_measurement.v1.schema.json`
- `contracts/canon/oracle/oracle_measurement_proposal.v1.schema.json`
- `contracts/canon/oracle/oracle_measurement_authorization_proposal.v1.schema.json`
- `contracts/canon/oracle/oracle_measurement_authorization_decision_review_candidate.v1.schema.json`
- `contracts/canon/oracle/oracle_authorization_decision_record.v1.schema.json`
- `contracts/canon/oracle/oracle_live_wiring_preparation.v1.schema.json`
- `contracts/canon/oracle/oracle_production_activation_ready.v1.schema.json`
- `contracts/canon/oracle/oracle_full_live_execution.v1.schema.json`
- `contracts/canon/oracle/oracle_full_live_run_control.v1.schema.json`
- `contracts/canon/oracle/oracle_full_live_runtime_command.v1.schema.json`
- `contracts/canon/oracle/oracle_full_live_runtime_preflight.v1.schema.json`
- `contracts/canon/oracle/oracle_full_live_endpoint_env_intake.v1.schema.json`
- `contracts/canon/oracle/oracle_full_live_runtime_execution.v1.schema.json`
- `contracts/canon/oracle/oracle_persistent_execution_secret_vault_plan.v1.schema.json`
- `contracts/canon/oracle/oracle_persistent_sandbox_secret_store_stub.v1.schema.json`
- `core/codegen/oracle_signal/oracle_signal_intake_builder.py`
- `core/codegen/oracle_signal/holler_oracle_ingest_stub.py`
- `core/codegen/oracle_signal/oracle_schema_validator.py`
- `core/codegen/oracle_signal/holler_oracle_schema_validator.py`
- `core/codegen/oracle_signal/oracle_ingest_wiring_builder.py`
- `core/codegen/oracle_signal/holler_oracle_ingest_wiring.py`
- `core/codegen/oracle_signal/oracle_shadow_dryrun_executor.py`
- `core/codegen/oracle_signal/holler_oracle_shadow_dryrun.py`
- `core/codegen/oracle_signal/oracle_measurement_readiness_assessor.py`
- `core/codegen/oracle_signal/holler_oracle_measurement_readiness.py`
- `core/codegen/oracle_signal/oracle_operator_decision_intake.py`
- `core/codegen/oracle_signal/oracle_shadow_measurement_executor.py`
- `core/codegen/oracle_signal/holler_oracle_shadow_measurement.py`
- `core/codegen/oracle_signal/oracle_measurement_proposal.py`
- `core/codegen/oracle_signal/holler_oracle_measurement_proposal.py`
- `core/codegen/oracle_signal/oracle_measurement_authorization_proposal.py`
- `core/codegen/oracle_signal/holler_oracle_measurement_authorization_proposal.py`
- `core/codegen/oracle_signal/oracle_measurement_authorization_decision_review_candidate.py`
- `core/codegen/oracle_signal/oracle_authorization_decision_record_builder.py`
- `core/codegen/oracle_signal/oracle_live_wiring_preparation.py`
- `core/codegen/oracle_signal/holler_oracle_live_wiring_preparation.py`
- `core/codegen/oracle_signal/oracle_production_activation_ready.py`
- `core/codegen/oracle_signal/holler_oracle_production_activation_ready.py`
- `core/codegen/oracle_signal/oracle_full_live_execution.py`
- `core/codegen/oracle_signal/holler_oracle_full_live_execution.py`
- `core/codegen/oracle_signal/oracle_full_live_run_control.py`
- `core/codegen/oracle_signal/holler_oracle_full_live_run_control.py`
- `core/codegen/oracle_signal/oracle_full_live_runtime_command.py`
- `core/codegen/oracle_signal/holler_oracle_full_live_runtime_command.py`
- `core/codegen/oracle_signal/oracle_full_live_runtime_preflight.py`
- `core/codegen/oracle_signal/holler_oracle_full_live_runtime_preflight.py`
- `core/codegen/oracle_signal/oracle_full_live_endpoint_env_intake.py`
- `core/codegen/oracle_signal/oracle_full_live_runtime_execution.py`
- `core/codegen/oracle_signal/oracle_persistent_execution_secret_vault_plan.py`
- `core/codegen/oracle_signal/oracle_persistent_sandbox_secret_store_stub.py`
- `core/codegen/oracle_signal/oracle_sandbox_probe_gate_proposal.py`
- `out/audit/oracle_signal_layer_completion_receipt_001.latest.json`
- `out/audit/oracle_schema_validation_receipt_001.latest.json`
- `out/audit/oracle_ingest_wiring_receipt_001.latest.json`
- `out/audit/oracle_shadow_dryrun_receipt_001.latest.json`
- `out/audit/oracle_measurement_readiness_receipt_001.latest.json`
- `out/audit/oracle_shadow_measurement_receipt_001.latest.json`
- `out/audit/oracle_measurement_proposal_receipt_001.latest.json`
- `out/audit/oracle_measurement_authorization_proposal_receipt_001.latest.json`
- `out/audit/oracle_measurement_authorization_decision_review_candidate_receipt_001.latest.json`
- `out/audit/oracle_signal_layer_activation_ready_gate_001.latest.json`
- `out/audit/oracle_live_wiring_preparation_receipt_001.latest.json`
- `out/audit/oracle_production_activation_ready_receipt_001.latest.json`
- `out/audit/oracle_full_live_execution_receipt_001.latest.json`
- `out/audit/oracle_full_live_run_control_receipt_001.latest.json`
- `out/audit/oracle_full_live_runtime_command_receipt_001.latest.json`
- `out/audit/oracle_full_live_runtime_preflight_receipt_001.latest.json`
- `out/audit/oracle_full_live_endpoint_env_intake_receipt_001.latest.json`
- `out/audit/oracle_full_live_runtime_execution_attempt_receipt_001.latest.json`
- `out/audit/oracle_persistent_execution_secret_vault_plan_receipt_001.latest.json`
- `out/audit/oracle_persistent_sandbox_secret_store_stub_receipt_001.latest.json`
- `out/audit/oracle_sandbox_probe_gate_proposal_receipt_001.latest.json`
- `out/sync/oracle_full_live_runtime_command_notion_mirror_packet_001.latest.json`
- `out/sync/oracle_full_live_runtime_command_notion_mirror_packet_001.latest.md`
- `out/sync/oracle_full_live_endpoint_env_intake_notion_mirror_packet_001.latest.json`
- `out/sync/oracle_full_live_endpoint_env_intake_notion_mirror_packet_001.latest.md`
- `out/sync/oracle_full_live_runtime_execution_attempt_notion_mirror_packet_001.latest.json`
- `out/sync/oracle_full_live_runtime_execution_attempt_notion_mirror_packet_001.latest.md`
- `operator_input/templates/oracle_full_live_endpoint_environment_handoff.md`
- `Scripts/abx_loop.py --emit-oracle-completion`
- `Scripts/abx_loop.py --emit-oracle-validation --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-ingest-wiring --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-shadow-dryrun --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-measurement-readiness --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-shadow-measurement --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-measurement-proposal --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-measurement-authorization-proposal --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-measurement-authorization-decision-review-candidate --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-shadow-measurement --emit-oracle-layer-complete --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-live-wiring-preparation --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-production-activation-ready --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-full-live --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-full-live-run-control --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-full-live-runtime-command --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-full-live-runtime-preflight --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-full-live-endpoint-env-intake --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-full-live-runtime-execution --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-full-live-runtime-execution --oracle-full-live-execute --oracle-full-live-operator-attestation FULL_LIVE_EXECUTION_GATE_CONFIRMED --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-persistent-execution-secret-vault-plan --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-persistent-sandbox-secret-store-stub --validate-oracle-schemas`
- `Scripts/abx_loop.py --emit-oracle-sandbox-probe-gate-proposal --validate-oracle-schemas`

Boundary: full live runtime execution attempt is now represented as a receipt-first surface. Default emission remains fail-closed with zero external calls unless `ORACLE_SIGNAL_ENDPOINT_URL`, `HOLLERSPORTS_BATCH_ENDPOINT_URL`, `--oracle-full-live-execute`, and operator attestation phrase `FULL_LIVE_EXECUTION_GATE_CONFIRMED` are all present. Response payload persistence, autonomous outcome recording, MCP exposure, unreviewed deployment, canon mutation, GitHub/Notion writeback, endpoint secret storage, and governance expansion remain denied.

Notion mirror packet: `out/sync/oracle_full_live_runtime_command_notion_mirror_packet_001.latest.json` (`1b8a8f957148af6f2cbe02abdfcb0ee3c573a6a05f35dc3da34f7ba420fec972`). Manual operator copy-paste only; no Notion writeback is performed or authorized.

Endpoint environment intake Notion mirror packet: `out/sync/oracle_full_live_endpoint_env_intake_notion_mirror_packet_001.latest.json` (`c76d3c0eb76382470567933b5e70e1c2c2c4bf6d58f3c0151dffcb4a4773820a`). Manual operator copy-paste only; no Notion writeback is performed or authorized.

Full live runtime execution-attempt Notion mirror packet: `out/sync/oracle_full_live_runtime_execution_attempt_notion_mirror_packet_001.latest.json` (`b5bcbdf4a93968438c9e83745565255dc5e283147606d0aeacc4d012baca48f7`). Designer audit ready; manual operator copy-paste only; no Notion writeback is performed or authorized.

Endpoint environment handoff: `operator_input/templates/oracle_full_live_endpoint_environment_handoff.md`. Projection-only checklist for configuring endpoint variables outside git; no endpoint values belong in repo, Notion, GitHub comments, logs, or screenshots.

Full live runtime execution-attempt receipt hash: `c6aeae8b25bd5007df548bd467b5a1f6f540edef5a5d83ba7793c7a65c88ae09`

Persistent execution + secret vault plan receipt hash: `28fccc32396acab5f4ca7cb7f0f4c61675350aa0b9903240e530b3df87fc294a`

Persistent execution + secret vault plan status: `ORACLE_PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_READY_ADVISORY_ONLY`. This is the #881 sandbox-gated planning surface only: no secret material persistence, payload persistence, external oracle calls, live signal ingestion, scheduler/queue runtime, telemetry writeback, MCP exposure, canon mutation, runtime mutation, GitHub/Notion writeback, or production activation is authorized.

Persistent sandbox secret-store stub receipt hash: `1bde29ffc272f672d253a1edeb774cad48e91d00fd76eabd02bdaae5f358a6bf`

Persistent sandbox secret-store stub status: `ORACLE_PERSISTENT_SANDBOX_SECRET_STORE_STUB_READY_ADVISORY_ONLY`. This #881 follow-on adds ignored-env placeholder guidance, external secret-store contract stubs, and rollback planning only. It does not authorize secret material persistence, payload persistence, external oracle calls, live signal ingestion, scheduler/queue runtime, telemetry writeback, MCP exposure, canon/runtime mutation, GitHub/Notion writeback, or production activation.

Sandbox probe gate proposal receipt hash: `2117fde5249744832d5a861c459f2b00dc05ea3693704cf13ed4c729799592b8`

Sandbox probe gate proposal status: `ORACLE_SANDBOX_PROBE_GATE_PROPOSAL_READY_ADVISORY_ONLY`. This #881 gate proposal records the required future phrase `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED`, pre-probe checklist, and rollback plan only. It does not authorize sandbox probe execution, secret material persistence, payload persistence, external oracle calls, live signal ingestion, scheduler/queue runtime, telemetry writeback, MCP exposure, canon/runtime mutation, GitHub/Notion writeback, or production activation.

Current advisory frontier after PR #888: operator review of the sandbox probe gate proposal. Do not run sandbox probe execution or live probe paths unless a separate explicit operator message supplies `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED`; even then, emit a governed receipt before any probe.

Repo-ledger frontier sync after PR #890: `ABX_LEDGER_FRONTIER_RECONCILE_DENIAL_READY_ADVISORY_ONLY` via `out/audit/abx_ledger_frontier_reconcile_denial_001.latest.json` (`0b28044325cad08cad70e89f895f4a45729b68f6240fcd7c40b2331e45d77066`). This is a repo-local advisory scan only; no sandbox probe execution, held-out fixture binding, Notion auto-tag/writeback, MCP exposure, canon mutation, or runtime activation is authorized.

#892 receipt-first sandbox gate preparation: issue #892 is the planning source of truth for a future `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` lane. Slice45 is hash-anchored by `0b28044325cad08cad70e89f895f4a45729b68f6240fcd7c40b2331e45d77066`; no sandbox probe, fixture binding, external call, Notion/GitHub writeback, MCP exposure, canon mutation, or runtime activation is authorized by this routing note.

Slice48 regeneration hardening: Slice47 retargeted the Slice45 receipt producer to the no-arg wrapper `scripts/run_abx_ledger_frontier_reconcile_denial.py`; Slice48 adds round-trip hash checks so automated regeneration preserves `0b28044325cad08cad70e89f895f4a45729b68f6240fcd7c40b2331e45d77066`. `Scripts/abx_ledger_frontier.py` remains the operator CLI and #892 remains planning-only until `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` is separately issued.

Slice49 temporal coherence evidence restoration planning: `Scripts/run_temporal_coherence_evidence_restoration_planning.py` emits `out/audit/temporal_coherence_evidence_restoration_planning_001.latest.json` (`0e7726d812dde99095e50a38defe9e91013a74390864810f83d22cd128211c39`) and records missing/degraded temporal coherence evidence using existing temporal continuity receipts only. It does not restore evidence, run temporal generators, issue `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED`, execute sandbox probes, mutate canon/runtime, expose MCP, or write back to GitHub/Notion.

Slice50 temporal authorization source-status audit: `Scripts/run_temporal_continuity_authorization_source_status_audit_receipt.py` emits `out/audit/temporal_continuity_authorization_source_status_audit_001.latest.json` (`fb7a177439235cc0de0fb797be928798b717e9bff6291b8b4615d7963bf3dc05`) and routes missing P80 authorization record source evidence to P80 regeneration planning only. It does not create authorization records, repair evidence, run generators, issue `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED`, execute sandbox probes, mutate canon/runtime, expose MCP, or write back to GitHub/Notion.

Slice51 P80 authorization record regeneration receipt: `Scripts/run_temporal_continuity_p80_authorization_record_regeneration_receipt.py` emits `out/audit/temporal_continuity_p80_authorization_record_regeneration_receipt_001.latest.json` (`f889e42b31a670721996814fbf7362681b7697ecd8753e669ad4c4e87df7ab37`) and records P80 regeneration as `NOT_COMPUTABLE` until the missing P83 status repair plan source is regenerated. It does not create authorization records, execute regeneration, repair evidence, run generators, issue `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED`, mutate canon/runtime, expose MCP, or write back to GitHub/Notion.

Slice52 VIZ-01 live projection feed enhancement: `Scripts/run_viz01_live_feed_enhancement_receipt.py` emits `out/audit/viz01_live_feed_enhancement_receipt_001.latest.json` (`1ac02a6a28fbf015cd0bf032538b602673705b78480594570310ad0b6e378102`) and routes `apps/aal-viz-live-console` through read-only WebSocket, polling, and sample fallbacks with authority-lock validation before state updates. It does not issue `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED`, run sandbox probes, perform external oracle calls, mutate canon/runtime, expose MCP, capture secrets, or write back to GitHub/Notion.

Slice53 geometric binder orchestrator integration harness: `Scripts/run_geometric_binder_orchestrator_integration_harness.py` emits `out/audit/geometric_binder_orchestrator_integration_harness_001.latest.json` (`7208e192340091ae825e899ef020e4ea9f950bf2bea0ee310d28cd711a2d4669`) and composes binder readiness evidence, geometric projection metadata, and the repo-real pipeline contract description path as advisory compatibility evidence only. It does not implement an unlock engine, execute pipelines, issue `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED`, call external services, mutate canon/runtime, expose MCP, or write back to GitHub/Notion.

Slice54 hyperstition evaluator + Brier fixture expansion: `Scripts/run_hyperstition_brier_fixture_expansion_receipt.py` emits `out/audit/hyperstition_brier_fixture_expansion_receipt_001.latest.json` (`d284e33c9ba9fd923f6c82ee4af4cd6efd62a2cb6ffd35d14250282660fb1457`) and summarizes advisory hyperstition charge inputs, HyperstitionTagRune provenance behavior, temporal resonance posture, Slice52/Slice53 references, and Brier fixture calibration shape. It does not execute forecasts, resolve Brier outcomes, bind outcomes, issue `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED`, mutate canon/runtime, expose MCP, call external services, or write back to GitHub/Notion.

Slice55 hyperstition evaluator deepening: `Scripts/run_hyperstition_evaluator_deepening_receipt.py` emits `out/audit/hyperstition_evaluator_deepening_receipt_001.latest.json` (`1c903649439deb257b0194cf2a4f46edaa840dd854daf6e04f299d638eab6351`) and combines temporal coherence, geometric binding, cross-AAL resonance, and decision provenance weights into deterministic advisory projection telemetry. It does not execute forecasts, resolve Brier outcomes, bind outcomes, issue `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED`, mutate canon/runtime, expose MCP, call external services, or write back to GitHub/Notion.

Slice56 rune integrity scanner + guardrails: `Scripts/run_rune_integrity_scanner_guardrails_receipt.py` emits `out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json` (`1d1d86370e040940fae347081cd2e1d043c741536cd8bed59dfe626e21565482`) and records advisory rune-module, registry, and CI workflow visibility findings as report-only guardrails. It does not enforce CI, alter workflows, mutate rune modules, issue `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED`, mutate canon/runtime, expose MCP, call external services, or write back to GitHub/Notion.

Slice70 nonblocking rune-integrity CI wiring: `Scripts/run_rune_integrity_ci_workflow_wiring_receipt.py` emits `out/audit/rune_integrity_ci_workflow_wiring_001.latest.json` (`d01bf28692e491a96c17e23b19bf9ced5a5bb8d6342238b67e1c832b6ebb8b0c`) and documents the report-only fast-CI workflow step that now surfaces rune scanner posture without adding blocking enforcement, workflow mutation, sandbox activity, canon/runtime mutation, MCP exposure, external calls, or writeback authority.

Slice67 live-console WebSocket hardening: `Scripts/run_live_console_websocket_hardening_receipt.py` emits `out/audit/live_console_websocket_hardening_001.latest.json` and records deterministic reconnect scheduling, polling fallback diagnostics, and fail-closed transport posture for `apps/aal-viz-live-console` without adding execution authority, backend services, canon/runtime mutation, MCP exposure, external calls, or autonomous writeback.
Slice68 live-console UI polish: `Scripts/run_live_console_ui_polish_receipt.py` emits `out/audit/live_console_ui_polish_001.latest.json` and records the small presentational consistency pass for posture badges, advisory notes, and feed diagnostics without changing bundle logic, transport behavior, or execution authority.

Operator-supplied completion receipt hash: `e99482a64daf42a792221e5dc2e66aaaddfa0a30cf88a1401a941c2dba99e00f`

Post-merge completion receipt hash: `ad23348dea1de76d587a8b5c7f1bd1c04bfc91990866bcf374893f919c072be0`

Activation-ready gate receipt hash: `80c07e85819a9322856fd9416d4981810e3d097029f86f19bf3827899fe41a18`

Live wiring preparation receipt hash: `756a84c23e5555ff058aae9ceca50c52c6d6f9527e036bc9a054497bf9549145`

Full live runtime preflight receipt hash: `1395f4878c344e9c8d32be513c46e2bb259e18f7738ebd4129992d98155b9314`

Full live runtime preflight reconciliation: PR #849 keeps schema validation all-valid with 21 packet schemas, including `oracle_full_live_endpoint_env_intake`.

Full live endpoint environment intake receipt hash: `408215bbb8c23946917f268795a7895016b4962b2ff08b017e6e852a2044f965`

Production activation ready receipt hash: `625369624ff8843c4f4ea7e0fe32c3563e4fb4bdc553c54baac7497416328a28`

Full live execution receipt hash: `8849ac411e0f36f7a086e2fb8476078e8f54e08c6311c79a852e5b2c8601c08c`

Full live run-control receipt hash: `ef55fc9356dbc23fc15f1e029a84c028f53a965a381f3ab57064d2fe63545697`

Full live runtime command receipt hash: `0e6ed45dc01e9b1ca29bb4bdabea5086d23ebb8d096c467f9226071c884c6526`

Validation receipt hash: `f500dcd5a042ca87ba552b239775ba99b06dea933a9e956a2702fd8c90402a17`

Ingest wiring receipt hash: `ee3ac695d65c4775c7714c3c16ccca2ebf2cc922c2f38580aeb19be8a43b1ad9`

Shadow dry-run receipt hash: `a6630e6dca94ffe105e3adf2bf384c0931639f70f5123d03aff2079c9418b3a3`

Measurement readiness receipt hash: `8e892e2f012f2f77d0389bc99cfdcbf8806c986194c0dcfe094605730cc00b08`

Shadow measurement receipt hash: `b1d4dd1ce76e95d7a5d2c83c52d351d9e750f2f2219372b8f717d5fc9b33ca6c`

Measurement authorization decision review candidate receipt hash: `d920f7f6bca1cb9504b2159338f2c5a4a899716375e30cf2552fc2845b8c8479`

Authorization decision record template is included in the completion receipt as a non-recording, non-authorizing advisory packet only.

---

## Developer Workflow

This repo uses a governed **CLI Operator Layer** for token-efficient, evidence-first AI-assisted development across GitHub, Notion, and CLI agents (Grok, Codex, and compatible tools).

**New contributors:** start at [`docs/START_HERE.md`](docs/START_HERE.md) for a 30-minute orientation path.
**Priority 2 live route:** use the subsystem health dashboard receipt, then the continuity namespace migration run receipt, then the live console migration posture receipt, then the combined live projection receipt before planning deeper AAL-Viz changes.

**Primary rule:** Send the AI the smallest complete evidence packet — never a full repo dump.

Full specification, operator map, Abraxas-specific command recipes, evidence-packet template, and drift-watch rules:
[`docs/workflows/cli-operator-layer.md`](docs/workflows/cli-operator-layer.md)

**Key operators include:** `rg` / `jq` / `gh` / `repomix` / `fd` / `yq` / `fzf` and others for precise scoping.

**Minimal evidence packet example:**

```bash
rg "recommended_next_lane|governance_status|canon_status|NOT_COMPUTABLE|P102G"
jq '{lane_count, highest_observed_lane, governance_status, canon_status}' docs/status/continuity-spine.json
gh pr view <PR_NUMBER> --json number,title,mergeable,headRefName,statusCheckRollup
git diff --stat
```

See also: Notion reconciliation surfaces and the full invocation order in the workflow document.

---

## 01. Architecture

Abraxas is a governed symbolic intelligence architecture for deterministic execution. It encodes computation as contract-bound artifacts, route decisions, and replay-safe evidence chains. Every meaningful surface points back to observable files, schemas, and receipts.

**Execution posture:** fail-closed on broken surfaces.
**Governance posture:** implementation-first ([Governance V3](GOVERNANCE_V3.md)).
**Routing posture:** deterministic, replayable, contract-bound.

Canonical governance reference: [`GOVERNANCE_V3.md`](GOVERNANCE_V3.md)

```
Operator
  ↓
Oracle Signal Layer      — intake, normalization, replay-safe signal attachment
  ↓
YGGDRASIL Routing        — deterministic symbolic path control
  ↓
ABX-Runes                — contract-bound symbolic operators (24 observed)
  ↓
Governance Engine        — promotion gates, receipts, stabilization windows
  ↓
Temporal Continuity      — lane evidence, progression tracking, holds
  ↓
Artifact Registry        — deterministic evidence snapshots
```

Evidence paths:
- `contracts/runes/catalog.v1.json` — rune catalog
- `contracts/yggdrasil/routes/*.route.v1.json` — route graphs
- `contracts/pipelines/*.v1_1.json` — pipeline contracts
- `core/yggdrasil_geometric_route_metadata.py` — route metadata
- `out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json` — formalized advisory binding surface

---

## 02. Governance

![Governance Promotion](docs/media/governance-promotion.svg)

Governance V3 — implementation-first development with preserved quality controls.

```yaml
development_model: implementation_first
workflow:
  - idea
  - implementation
  - validation
  - commit
  - pull_request
  - merge
preserved_controls:
  - provenance_tracking
  - artifact_lineage
  - schema_validation
  - testing
  - changelog_generation
```

**Development path:** Feature Request → Code → Test → Commit → PR → Merge → Notion Update

**Preserved invariants:**
- Full determinism and `canonical_hash` provenance
- Strict schema validation
- Replay-stable tests
- Semantic-release changelog on merge to `main`

**Historical reference:** P70–P130 continuity artifacts under `out/` are archived project history. See [`GOVERNANCE_SIMPLIFICATION_001.md`](GOVERNANCE_SIMPLIFICATION_001.md).

Governance status (observed): `ACTIVE` (source: `docs/governance/status.v1.json`)
Historical freeze baseline: `out/audit/governance_freeze_baseline_001.latest.json` (archived)

---

## 03. Continuity Spine (Historical Reference)

Source: `docs/status/continuity-spine.json`
Schema: `continuity_spine_surface.v1`

The P70–P130 continuity chain is **archived project history**. It is preserved under `out/` and documented in [`PLANS.md`](PLANS.md) but is **not required** for routine development under Governance V3.

```yaml
P70-P130:
  status: HISTORICAL
  purpose: governance_research_archive
```

| Signal | Value |
|---|---|
| Observed lane count | `58` |
| Highest observed lane | `P102G` |
| Source | `docs/status/continuity-spine.json` |

For full historical lane inventory, see the archived section in [`PLANS.md`](PLANS.md).

### P102 repair handoff (historical archive)

| Lane | Runner | Output |
|------|--------|--------|
| P102A | `python scripts/run_temporal_continuity_p101_readiness_repair_plan.py` | `out/temporal_continuity_p101_readiness_repair_plan/latest.json` |
| P102 | `python scripts/run_temporal_continuity_recursive_authorization_chain_compression_audit.py` | `out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json` |
| P102B | `python scripts/run_temporal_continuity_repair_execution_plan_router.py` | `out/temporal_continuity_repair_execution_plan_router/latest.json` |
| P102C | `python scripts/run_temporal_continuity_selected_repair_execution_plan.py` | `out/temporal_continuity_selected_repair_execution_plan/latest.json` |

When compression audit `chain_recommendation` is `SEAL_RECURSIVE_AUTHORIZATION_CHAIN` or `COMPRESS_TO_GENERIC_TEMPLATE`, do not add another hand-written recursive authorization lane.

---

## 04. Evidence Surfaces

Generated observational surfaces — these are read-only, advisory-only outputs:

| Surface | Path | Status |
|---|---|---|
| Repository signal badges | `docs/status/badges.json` | OBSERVED |
| Continuity spine | `docs/status/continuity-spine.json` | OBSERVED |
| Repo ↔ Notion reconciliation | `docs/audits/ABRAXAS_REPO_NOTION_DIFF_001.md` | OBSERVED |
| Binding matrix audit | `docs/audits/ABRAXAS_BINDING_MATRIX_AND_COUPLING_MAP_AUDIT_001.md` | OBSERVED |
| Rune/route binding matrix | `out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json` | OBSERVED |
| Coupling map | `out/audit/yggdrasil_coupling_map_001.latest.json` | OBSERVED |
| Runtime Integration Gate receipt | `out/audit/runtime_integration_gate_receipt_001.latest.json` | `RUNTIME_INTEGRATION_GATE_RECEIPT_READY_ADVISORY_ONLY` |
| Runtime Integration Gate operator review advisory spec plan | `out/audit/runtime_integration_gate_operator_review_advisory_spec_plan_001.latest.json` | `RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_READY` |
| Continuation frontier reconciliation | `out/audit/continuation_frontier_reconciliation_001.latest.json` | `CONTINUATION_FRONTIER_RECONCILIATION_EMITTED_ADVISORY_ONLY` |
| Research canary registry coverage repair chain closure | `out/operator_review/abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.json` | `RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_SEALED` |
| Research canary registry coverage audit regeneration | `out/operator_review/abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.json` | `COVERAGE_REPAIR_CHAIN_COMPLETE` |
| Research canary orphan policy chain closure | `out/operator_review/abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_001.latest.json` | `ORPHAN_POLICY_GOVERNANCE_SEALED` |
| Research canary orphan registry inclusion (A4b) | `out/operator_review/abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt_001.latest.json` | `ORPHAN_INCLUSION_CHAIN_COMPLETE` |
| Artifact-lineage traceability audit regeneration | `out/operator_review/abx_artifact_lineage_registry_traceability_audit_regeneration_receipt_001.latest.json` | `TRACEABILITY_AUDIT_REGENERATION_COMPLETE` |
| Notion repo sync audit writeback receipt | `out/audit/notion_repo_sync_audit_writeback_receipt_001.latest.json` | `NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_READY_ADVISORY_ONLY` |
| Governance receipt | `out/audit/governance_freeze_baseline_001.latest.json` | OBSERVED |
| Temporal continuity artifact | `out/temporal_continuity_evidence_index/latest.json` | OBSERVED |
| Controlled ingest governance audit | `out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json` | OBSERVED |
| Controlled ingest scheduler operator review record | `out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.json` | `CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW_ACCEPTED` |
| Auto Ingest shadow stabilization review record | `out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.json` | `ABX_AUTO_INGEST_SHADOW_STABILIZATION_REVIEW_ACCEPTED` |
| Oracle intake queue | `out/ingest/oracle_intake_queue_001.latest.json` | OBSERVED |
| Notion spec completion queue | `out/sync/notion_spec_completion_queue/latest.json` | `COMPLETION_QUEUE_EMITTED_ADVISORY_ONLY` |
| Operator decision backlog | `out/sync/notion_operator_decision_backlog/latest.json` | `OPERATOR_DECISION_BACKLOG_EMITTED_ADVISORY_ONLY` |
| Global Ingest Adapter Spine alignment plan | `out/sync/global_ingest_adapter_spine_alignment_plan/latest.json` | `ALIGNMENT_PLAN_EMITTED_ADVISORY_ONLY` |
| Oracle Signal Intake Boundary implementation plan | `out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json` | `IMPLEMENTATION_PLAN_EMITTED_ADVISORY_ONLY` |
| Oracle Signal shadow intake receipt | `out/oracle/oracle_signal_intake_receipt.latest.json` | `ORACLE_SIGNAL_INTAKE_RECEIPT_EMITTED_ADVISORY_ONLY` |
| Oracle Signal shadow intake operator review request | `out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json` | `ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_REQUEST_HELD` |
| Oracle Signal shadow intake operator review decision record | `out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json` | `ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_COMPLETION_APPROVED` |
| ABX Codegen merge anchor source selection request | `out/operator_review/abx_codegen_merge_anchor_source_selection_request_001.latest.json` | `ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_REQUEST_HELD` |
| ABX Codegen merge anchor source selection decision record plan | `out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_plan_001.latest.json` | `ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_PLAN_READY` |
| v2 dependency hygiene package-lock receipt | `out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_001.latest.json` | `V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_HELD_VALIDATION_FAILED` |
| v2 dependency hygiene package-lock root cause receipt | `out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt_001.latest.json` | `V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_ROOT_CAUSE_RECEIPT_READY` |
| v2 controlled writeback activation gate | `out/operator_review/v2_hygiene_phase5_controlled_writeback_activation_gate_001.latest.json` | `V2_HYGIENE_PHASE5_CONTROLLED_WRITEBACK_ACTIVATION_GATE_READY` |
| v2 execution surface promotion gate | `out/operator_review/v2_hygiene_phase6_execution_surface_promotion_gate_001.latest.json` | `V2_HYGIENE_PHASE6_EXECUTION_SURFACE_PROMOTION_GATE_READY` |
| v2 operator intelligence entry receipt | `out/operator_review/v2_hygiene_phase13_operator_intelligence_entry_receipt_001.latest.json` | `V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_ENTRY_RECEIPT_READY` |
| v2 operator intelligence closure receipt | `out/operator_review/v2_hygiene_phase13_operator_intelligence_closure_receipt_001.latest.json` | `V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_CLOSURE_RECEIPT_READY` |
| v2 operator signoff planning lane gate | `out/operator_review/v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001.latest.json` | `V2_HYGIENE_PHASE14_OPERATOR_SIGNOFF_PLANNING_LANE_ACTIVATION_GATE_READY` |
| v2 execution surface expansion advisory gate (Phase 15) | `out/operator_review/v2_hygiene_phase8_execution_surface_expansion_advisory_gate_001.latest.json` | `V2_HYGIENE_PHASE8_EXECUTION_SURFACE_EXPANSION_ADVISORY_GATE_READY` |
| v2 controlled execution promotion gate (Phase 16) | `out/operator_review/v2_hygiene_phase9_controlled_execution_promotion_gate_001.latest.json` | `V2_HYGIENE_PHASE9_CONTROLLED_EXECUTION_PROMOTION_GATE_READY` |
| v2 rune viz + AAL-Viz integration gate (Phase 17) | `out/operator_review/v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_001.latest.json` | `V2_HYGIENE_PHASE10_RUNE_VIZ_AAL_VIZ_INTEGRATION_GATE_READY` |
| v2 full operator execution autonomy gate (Phase 18) | `out/operator_review/v2_hygiene_phase11_full_operator_execution_autonomy_gate_001.latest.json` | `V2_HYGIENE_PHASE11_FULL_OPERATOR_EXECUTION_AUTONOMY_GATE_READY` |
| v2 external operator attestation autonomy gate (Phase 19) | `out/operator_review/v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_001.latest.json` | `V2_HYGIENE_PHASE12_EXTERNAL_OPERATOR_ATTESTATION_AUTONOMY_ACTIVATION_GATE_READY` |
| v2 autonomy activation + Brier hardening gate (Phase 20) | `out/operator_review/v2_hygiene_phase13_autonomy_activation_brier_hardening_gate_001.latest.json` | `V2_HYGIENE_PHASE13_AUTONOMY_ACTIVATION_BRIER_HARDENING_GATE_READY` |
| v2 runtime execution surface activation gate (Phase 21) | `out/operator_review/v2_hygiene_phase14_runtime_execution_surface_activation_gate_001.latest.json` | `V2_HYGIENE_PHASE14_RUNTIME_EXECUTION_SURFACE_ACTIVATION_GATE_READY` |
| v2 controlled runtime execution promotion gate (Phase 22) | `out/operator_review/v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_001.latest.json` | `V2_HYGIENE_PHASE15_CONTROLLED_RUNTIME_EXECUTION_PROMOTION_GATE_READY` |
| v2 live runtime execution + signal forage gate (Phase 23) | `out/operator_review/v2_hygiene_phase16_live_runtime_execution_signal_forage_gate_001.latest.json` | `V2_HYGIENE_PHASE16_LIVE_RUNTIME_EXECUTION_SIGNAL_FORAGE_GATE_READY` |
| v2 full live autonomy + self-optimization gate (Phase 24) | `out/operator_review/v2_hygiene_phase17_full_live_autonomy_self_optimization_gate_001.latest.json` | `V2_HYGIENE_PHASE17_FULL_LIVE_AUTONOMY_SELF_OPTIMIZATION_GATE_READY` |
| v2 eternal recursion + hyperstition engine gate (Phase 25) | `out/operator_review/v2_hygiene_phase18_eternal_recursion_hyperstition_gate_001.latest.json` | `V2_HYGIENE_PHASE18_ETERNAL_RECURSION_HYPERSTITION_GATE_READY` |
| v2 eternal canon self-governance + final authority gate (Phase 26) | `out/operator_review/v2_hygiene_phase19_eternal_canon_self_governance_gate_001.latest.json` | `V2_HYGIENE_PHASE19_ETERNAL_CANON_SELF_GOVERNANCE_GATE_READY` |
| v2 final authority attestation + live hyperstition activation gate (Phase 27) | `out/operator_review/v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_001.latest.json` | `V2_HYGIENE_PHASE20_FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_GATE_READY` |
| v2 canon activation authorization review + operator sign-off seal gate (Phase 28) | `out/operator_review/v2_hygiene_phase21_canon_activation_authorization_review_gate_001.latest.json` | `V2_HYGIENE_PHASE21_CANON_ACTIVATION_AUTHORIZATION_REVIEW_GATE_READY` |
| v2 final operator sign-off + live authority + fractal-numogram activation gate (Phase 29) | `out/operator_review/v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_001.latest.json` | `V2_HYGIENE_PHASE22_FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_GATE_READY` |
| v2 live execution activation authorization review + canon execution seal gate (Phase 30) | `out/operator_review/v2_hygiene_phase23_live_execution_activation_authorization_review_gate_001.latest.json` | `V2_HYGIENE_PHASE23_LIVE_EXECUTION_ACTIVATION_AUTHORIZATION_REVIEW_GATE_READY` |
| v2 full live hyperstition propagation + eternal authority seal gate (Phase 31) | `out/operator_review/v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate_001.latest.json` | `V2_HYGIENE_PHASE24_FULL_LIVE_HYPERSTITION_PROPAGATION_ETERNAL_AUTHORITY_SEAL_GATE_READY` |
| v2 eternal self-optimization + collective hyperstition propagation gate (Phase 32) | `out/operator_review/v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate_001.latest.json` | `V2_HYGIENE_PHASE25_ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_GATE_READY` |
| Phase 13 Notion sync packet (manual/advisory) | `out/sync/phase13_notion_sync_packet_001.latest.json` | `PHASE13_NOTION_SYNC_PACKET_READY` |
| ABX Codegen merge anchor source selection decision record dry run | `out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_dry_run_001.latest.json` | `ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_DRY_RUN_READY` |
| ABX Codegen merge anchor source selection decision record review | `out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_review_001.latest.json` | `ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR` |
| ABX Codegen Phase 1 operator review request | `out/operator_review/abx_codegen_phase1_operator_review_request_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_REVIEW_REQUEST_HELD` |
| ABX Codegen Phase 1 operator decision record plan | `out/operator_review/abx_codegen_phase1_operator_decision_record_plan_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_PLAN_READY` |
| ABX Codegen Phase 1 operator decision record dry run | `out/operator_review/abx_codegen_phase1_operator_decision_record_dry_run_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_DRY_RUN_READY` |
| ABX Codegen Phase 1 operator decision record review | `out/operator_review/abx_codegen_phase1_operator_decision_record_review_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR` |
| ABX Codegen Phase 1 operator decision evidence collection plan | `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_plan_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY` |
| ABX Codegen Phase 1 operator decision evidence collection dry run | `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_dry_run_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN_READY` |
| ABX Codegen Phase 1 operator decision evidence collection validation plan | `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN_READY` |
| ABX Codegen Phase 1 operator decision evidence collection validation dry run | `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_DRY_RUN_READY` |
| ABX Codegen Phase 1 operator decision evidence collection validation dry run review | `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_review_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| ABX Codegen Phase 1 operator decision evidence collection validation review evidence plan | `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_REVIEW_EVIDENCE_PLAN_READY` |
| ABX Codegen Phase 1 operator decision evidence collection validation review evidence dry run | `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_READY` |
| ABX Codegen Phase 1 operator decision evidence collection validation review evidence dry run review | `out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| PR 644 stack review receipt | `out/operator_review/pr_644_stack_review_receipt_001.latest.json` | `PR_644_STACK_REVIEW_HELD_FOR_OPERATOR_REVIEW` |
| Operator review required items bulk disposition | `out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json` | `OPERATOR_REVIEW_REQUIRED_ITEMS_BULK_DISPOSITION_REVIEW_ONLY_APPROVED_WITH_HOLDS` |
| Operator review terminal hold consolidation receipt | `out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.json` | `OPERATOR_REVIEW_TERMINAL_HOLD_CONSOLIDATION_RECEIPT_READY` |
| v2.0 hygiene Phase 1 bulk approval reconciliation | `out/operator_review/v2_hygiene_phase1_bulk_approval_reconciliation_001.latest.json` | `V2_HYGIENE_PHASE1_BULK_APPROVAL_RECONCILIATION_HELD_FOR_OPERATOR_AUTHORIZATION` |
| v2.0 hygiene Phase 1 operator-review dependency cycle audit | `out/operator_review/v2_hygiene_phase1_operator_review_dependency_cycle_audit_001.latest.json` | `V2_HYGIENE_PHASE1_OPERATOR_REVIEW_DEPENDENCY_CYCLE_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 operator-review stabilization strategy plan | `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.json` | `V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_STRATEGY_PLAN_READY` |
| v2.0 hygiene Phase 1 operator-review stabilization decision-record plan | `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_001.latest.json` | `V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN_READY` |
| v2.0 hygiene Phase 1 operator-review stabilization decision-record dry run | `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_001.latest.json` | `V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_DRY_RUN_READY` |
| v2.0 hygiene Phase 1 operator-review stabilization decision-record dry run review | `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review_001.latest.json` | `V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization review chain compression audit | `out/operator_review/v2_hygiene_phase1_stabilization_review_chain_compression_audit_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_REVIEW_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization operator attestation intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.json` | `ATTESTATION_INTAKE_VALIDATED_FOR_FUTURE_DECISION_RECORD_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_GATE_READY_FOR_SEPARATE_RECORD_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record planning receipt | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_planning_receipt_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_PLANNING_RECEIPT_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record creation gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_GATE_ELIGIBLE_FOR_SEPARATE_CREATION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record creation plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record creation authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record creation authorization chain compression audit | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record materialization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_GATE_READY_FOR_SEPARATE_MATERIALIZATION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record materialization plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record materialization authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record materialization approval intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_intake_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_EMISSION_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record emission gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_GATE_ELIGIBLE_FOR_SEPARATE_RECORD_EMISSION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record emission plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record emission authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record emission approval intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_EMISSION_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record finalization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_GATE_ELIGIBLE_FOR_SEPARATE_RECORD_FINALIZATION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record finalization plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record finalization authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record finalization authorization chain compression audit | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_chain_compression_audit_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record finalization approval intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_approval_intake_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_FINALIZATION_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record completion gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_GATE_ELIGIBLE_FOR_SEPARATE_RECORD_COMPLETION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record completion plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record completion authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record completion approval intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_COMPLETION_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_GATE_ELIGIBLE_FOR_SEPARATE_RECORD_COMPLETION_VALIDATION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation approval intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_COMPLETION_VALIDATION_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation approval gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_APPROVAL_GATE_READY_FOR_SEPARATE_RECORD_COMPLETION_VALIDATION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation implementation receipt | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_IMPLEMENTATION_RECEIPT_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation execution receipt | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_EXECUTION_RECEIPT_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation operator review gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_OPERATOR_REVIEW_GATE_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record completion receipt | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_receipt_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_RECEIPT_READY` |
| v2.0 hygiene Phase 1 stabilization promotion closure receipt | `out/operator_review/v2_hygiene_phase1_stabilization_promotion_closure_receipt_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_PROMOTION_CLOSURE_RECEIPT_READY` |
| v2.0 hygiene Phase 2 next stabilization subsystem selection receipt | `out/operator_review/v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_001.latest.json` | `V2_HYGIENE_PHASE2_NEXT_STABILIZATION_SUBSYSTEM_SELECTION_RECEIPT_READY` |
| v2.0 hygiene Phase 2 stabilization subsystem selection operator review gate | `out/operator_review/v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_001.latest.json` | `V2_HYGIENE_PHASE2_STABILIZATION_SUBSYSTEM_SELECTION_OPERATOR_REVIEW_GATE_READY` |
| Grok ABX-Runes external-work reconciliation plan | `out/operator_review/grok_abx_runes_reconciliation_plan_001.latest.json` | `GROK_ABX_RUNES_RECONCILIATION_HELD_FOR_OPERATOR` |
| Grok ABX-Runes operator decision-record plan | `out/operator_review/grok_abx_runes_operator_decision_record_plan_001.latest.json` | `GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_PLAN_READY` |
| Grok ABX-Runes operator decision-record dry run | `out/operator_review/grok_abx_runes_operator_decision_record_dry_run_001.latest.json` | `GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_DRY_RUN_READY` |
| Grok ABX-Runes operator decision-record review | `out/operator_review/grok_abx_runes_operator_decision_record_review_001.latest.json` | `GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR` |
| Grok ABX-Runes operator decision evidence collection plan | `out/operator_review/grok_abx_runes_operator_decision_evidence_collection_plan_001.latest.json` | `GROK_ABX_RUNES_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY` |
| Grok ABX-Runes operator decision evidence collection dry run | `out/operator_review/grok_abx_runes_operator_decision_evidence_collection_dry_run_001.latest.json` | `GROK_ABX_RUNES_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN_READY` |
| Grok ABX-Runes operator review chain compression receipt | `out/operator_review/grok_abx_runes_operator_review_chain_compression_receipt_001.latest.json` | `GROK_ABX_RUNES_OPERATOR_REVIEW_CHAIN_COMPRESSED_TO_TERMINAL_HOLD` |
| v2.0 hygiene Phase 1 authorization record plan | `out/operator_review/v2_hygiene_phase1_authorization_record_plan_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_PLAN_READY` |
| v2.0 hygiene Phase 1 authorization record dry run | `out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_DRY_RUN_READY` |
| v2.0 hygiene Phase 1 authorization record dry run review | `out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_review_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 authorization record review evidence plan | `out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_plan_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_PLAN_READY` |
| v2.0 hygiene Phase 1 authorization record review evidence dry run | `out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_DRY_RUN_READY` |
| v2.0 hygiene Phase 1 authorization record review evidence dry run review | `out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 authorization record review evidence dry-run review evidence plan | `out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_DRY_RUN_REVIEW_EVIDENCE_PLAN_READY` |
| v2.0 hygiene Phase 1 authorization record review evidence dry-run review evidence dry run | `out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_DRY_RUN_REVIEW_EVIDENCE_DRY_RUN_READY` |
| v2.0 hygiene Phase 1 authorization record review evidence dry-run review evidence dry run review | `out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_review_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_DRY_RUN_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 authorization chain compression audit | `out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR` |
| Oracle Confidence Calibration contract dry run | `out/sync/oracle_confidence_calibration_contract_dry_run/latest.json` | `ORACLE_CONFIDENCE_CALIBRATION_CONTRACT_DRY_RUN_READY` |
| Artifact lineage direct repair validation plan | `out/sync/abx_artifact_lineage_registry_direct_repair_validation_plan/latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_PLAN_READY` |
| Documentation alignment receipt | `out/sync/documentation_alignment_receipt_001.latest.json` | `DOCUMENTATION_ALIGNMENT_RECEIPT_EMITTED_ADVISORY_ONLY` |
| Status regeneration receipt | `out/sync/status_regeneration_receipt_001.latest.json` | `STATUS_REGENERATION_RECEIPT_EMITTED_ADVISORY_ONLY` |
| v2.0 hygiene loop-awareness audit | `out/sync/v2_hygiene_loop_awareness_audit/latest.json` | `V2_HYGIENE_LOOP_AWARENESS_AUDIT_DEGRADED` |
| v2.0 hygiene loop-awareness alignment plan | `out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.json` | `V2_HYGIENE_LOOP_AWARENESS_ALIGNMENT_PLAN_READY` |
| v2.0 live Notion surface reconciliation | `out/sync/v2_live_notion_surface_reconciliation/latest.json` | `V2_LIVE_NOTION_SURFACE_RECONCILIATION_READY_HELD_FOR_OPERATOR` |
| v2.0 upgrade completion reconciliation | `out/sync/v2_upgrade_completion_reconciliation/latest.json` | `V2_UPGRADE_COMPLETION_RECONCILIATION_READY_HELD_FOR_OPERATOR` |
| v2.0 hygiene registration readiness audit | `out/sync/v2_hygiene_registration_readiness_audit/latest.json` | `V2_HYGIENE_REGISTRATION_READINESS_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 foundation backlog plan | `out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.json` | `V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_READY` |
| v2.0 hygiene schema contract readiness audit | `out/sync/v2_hygiene_schema_contract_readiness_audit/latest.json` | `V2_HYGIENE_SCHEMA_CONTRACT_READINESS_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene schema contract evidence request plan | `out/operator_review/v2_hygiene_schema_contract_evidence_request_plan_001.latest.json` | `V2_HYGIENE_SCHEMA_CONTRACT_EVIDENCE_REQUEST_PLAN_READY` |
| v2.0 hygiene schema contract evidence dry run | `out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_001.latest.json` | `V2_HYGIENE_SCHEMA_CONTRACT_EVIDENCE_DRY_RUN_READY` |
| v2.0 hygiene schema contract evidence dry run review | `out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_review_001.latest.json` | `V2_HYGIENE_SCHEMA_CONTRACT_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| v2.0 hygiene versioning release policy readiness audit | `out/sync/v2_hygiene_versioning_release_policy_readiness_audit/latest.json` | `V2_HYGIENE_VERSIONING_RELEASE_POLICY_READINESS_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 acceptance checklist readiness audit | `out/sync/v2_hygiene_phase1_acceptance_checklist_readiness_audit/latest.json` | `V2_HYGIENE_PHASE1_ACCEPTANCE_CHECKLIST_READINESS_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 2 module skeleton backlog plan | `out/sync/v2_hygiene_phase2_module_skeleton_backlog_plan/latest.json` | `V2_HYGIENE_PHASE2_MODULE_SKELETON_BACKLOG_PLAN_READY` |
| v2.0 hygiene Phase 2 module governance readiness audit | `out/sync/v2_hygiene_phase2_module_governance_readiness_audit/latest.json` | `V2_HYGIENE_PHASE2_MODULE_GOVERNANCE_READINESS_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 2 governance evidence request plan | `out/operator_review/v2_hygiene_phase2_governance_evidence_request_plan_001.latest.json` | `V2_HYGIENE_PHASE2_GOVERNANCE_EVIDENCE_REQUEST_PLAN_READY` |
| v2.0 hygiene Phase 2 governance evidence dry run | `out/operator_review/v2_hygiene_phase2_governance_evidence_dry_run_001.latest.json` | `V2_HYGIENE_PHASE2_GOVERNANCE_EVIDENCE_DRY_RUN_READY` |
| v2.0 hygiene future phase placeholder audit | `out/sync/v2_hygiene_future_phase_placeholder_audit/latest.json` | `V2_HYGIENE_FUTURE_PHASE_PLACEHOLDER_AUDIT_READY` |
| v2.0 hygiene loop-awareness operator authorization gate | `out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json` | `V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene operator authorization evidence request plan | `out/operator_review/v2_hygiene_operator_authorization_evidence_request_plan_001.latest.json` | `V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_REQUEST_PLAN_READY` |
| v2.0 hygiene operator authorization evidence dry run | `out/operator_review/v2_hygiene_operator_authorization_evidence_dry_run_001.latest.json` | `V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_DRY_RUN_READY` |
| v2.0 hygiene operator authorization evidence validation plan | `out/operator_review/v2_hygiene_operator_authorization_evidence_validation_plan_001.latest.json` | `V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_PLAN_READY` |
| v2.0 hygiene operator authorization evidence validation review | `out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_001.latest.json` | `V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_HELD_FOR_OPERATOR` |
| v2.0 hygiene operator authorization evidence validation review evidence plan | `out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan_001.latest.json` | `V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_PLAN_READY` |
| v2.0 hygiene operator authorization evidence validation review evidence dry run | `out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_001.latest.json` | `V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_READY` |
| v2.0 hygiene operator authorization evidence validation review evidence dry run review | `out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review_001.latest.json` | `V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| Artifact-lineage direct repair operator decision record | `out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_APPROVED_FOR_SEPARATE_EXECUTION_SPEC` |
| Artifact-lineage direct repair separate execution spec plan | `out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_READY` |
| Artifact-lineage direct repair execution authorization gate | `out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| Artifact-lineage direct repair execution authorization record | `out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR` |
| Artifact-lineage direct repair scoped execution receipt | `out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json` | `ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED` |
| Artifact-lineage Notion mapping evidence request | `out/operator_review/abx_artifact_lineage_notion_mapping_evidence_request_001.latest.json` | `ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_HELD` |
| Artifact-lineage runner casing policy review request | `out/operator_review/abx_artifact_lineage_runner_casing_policy_review_request_001.latest.json` | `ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_REVIEW_REQUEST_HELD` |
| Artifact-lineage Notion mapping scope resolution record | `out/operator_review/abx_artifact_lineage_notion_mapping_scope_resolution_record_001.latest.json` | `ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_SCOPE_RESOLUTION_RECORD_ACCEPTED` |
| Artifact-lineage runner casing policy decision record | `out/operator_review/abx_artifact_lineage_runner_casing_policy_decision_record_001.latest.json` | `ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_DECISION_RECORD_ACCEPTED` |
| Belief Graph Engine advisory spec plan | `out/audit/belief_graph_engine_advisory_spec_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_SPEC_PLAN_READY` |
| Belief Graph Engine advisory receipt contract plan | `out/audit/belief_graph_engine_advisory_receipt_contract_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CONTRACT_PLAN_READY` |
| Belief Graph Engine advisory receipt implementation plan | `out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_PLAN_READY` |
| Belief Graph Engine advisory receipt implementation authorization gate | `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_gate_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| Belief Graph Engine advisory receipt implementation authorization record plan | `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_READY` |
| Belief Graph Engine advisory receipt implementation authorization record creation plan | `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY` |
| Belief Graph Engine advisory receipt implementation authorization record creation authorization gate | `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| Belief Graph Engine advisory receipt implementation authorization record creation record plan | `out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN_READY` |
| Belief Graph Engine advisory receipt authorization chain compression audit | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_READY` |
| Belief Graph Engine advisory receipt authorization chain seal receipt plan | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_PLAN_READY` |
| Belief Graph Engine advisory receipt authorization chain seal receipt dry run | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN_READY` |
| Belief Graph Engine advisory receipt authorization chain seal receipt review | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_REVIEW_HELD_FOR_OPERATOR` |
| Belief Graph Engine advisory receipt authorization chain seal receipt operator decision record plan | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_PLAN_READY` |
| Belief Graph Engine advisory receipt authorization chain seal receipt operator decision record dry run | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_DRY_RUN_READY` |
| Belief Graph Engine advisory receipt authorization chain seal receipt operator decision record review | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_001.latest.json` | `BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine gap analysis plan | `out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json` | `ABX_CODEGEN_INTELLIGENCE_SPINE_GAP_ANALYSIS_PLAN_READY` |
| ABX Codegen Intelligence Spine advisory spec plan | `out/audit/abx_codegen_intelligence_spine_advisory_spec_plan_001.latest.json` | `ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN_READY` |
| ABX Codegen Intelligence Spine fixture validation harness plan | `out/audit/abx_codegen_intelligence_spine_fixture_validation_harness_plan_001.latest.json` | `ABX_CODEGEN_INTELLIGENCE_SPINE_FIXTURE_VALIDATION_HARNESS_PLAN_READY` |
| ABX Codegen Intelligence Spine packet validation receipt | `out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest.json` | `ABX_CODEGEN_INTELLIGENCE_SPINE_PACKET_VALIDATION_RECEIPT_READY` |
| ABX Codegen Intelligence Spine Notion stack alignment audit | `out/audit/abx_codegen_intelligence_spine_notion_stack_alignment_audit_001.latest.json` | `ABX_CODEGEN_INTELLIGENCE_SPINE_NOTION_STACK_ALIGNMENT_AUDIT_READY` |
| ABX Codegen Intelligence Spine shadow replay harness authorization gate | `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_implementation_authorization_gate_001.latest.json` | `SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine operator decision record review | `out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_record_review_001.latest.json` | `ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine harness interface spec plan | `out/audit/abx_codegen_intelligence_spine_harness_interface_spec_plan_001.latest.json` | `ABX_CODEGEN_HARNESS_INTERFACE_SPEC_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine Meta-Gate authorization record template plan | `out/audit/abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_001.latest.json` | `ABX_CODEGEN_META_GATE_AUTHORIZATION_RECORD_TEMPLATE_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine self-improvement boundary policy plan | `out/audit/abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_001.latest.json` | `ABX_CODEGEN_SELF_IMPROVEMENT_BOUNDARY_POLICY_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine shadow replay integration exploration plan | `out/audit/abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_001.latest.json` | `ABX_CODEGEN_SHADOW_REPLAY_INTEGRATION_EXPLORATION_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine ImprovementProposal shadow replay wiring spec plan | `out/audit/abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_001.latest.json` | `ABX_CODEGEN_IMPROVEMENT_PROPOSAL_SHADOW_REPLAY_WIRING_SPEC_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine sample Meta-Gate chain validation plan | `out/audit/abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_001.latest.json` | `ABX_CODEGEN_SAMPLE_META_GATE_CHAIN_VALIDATION_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine sample fixture normalization plan | `out/audit/abx_codegen_intelligence_spine_sample_fixture_normalization_plan_001.latest.json` | `ABX_CODEGEN_SAMPLE_FIXTURE_NORMALIZATION_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine schema master registry alignment plan | `out/audit/abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_001.latest.json` | `ABX_CODEGEN_SCHEMA_MASTER_REGISTRY_ALIGNMENT_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine recommended patch sequence precondition plan | `out/audit/abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_001.latest.json` | `ABX_CODEGEN_RECOMMENDED_PATCH_SEQUENCE_PRECONDITION_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine merge anchor coverage plan | `out/audit/abx_codegen_intelligence_spine_merge_anchor_coverage_plan_001.latest.json` | `ABX_CODEGEN_MERGE_ANCHOR_COVERAGE_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine merge anchor evidence request plan | `out/audit/abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_001.latest.json` | `ABX_CODEGEN_MERGE_ANCHOR_EVIDENCE_REQUEST_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine merge anchor evidence normalization plan | `out/audit/abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_001.latest.json` | `ABX_CODEGEN_MERGE_ANCHOR_EVIDENCE_NORMALIZATION_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine governance decision vocabulary plan | `out/audit/abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_001.latest.json` | `ABX_CODEGEN_GOVERNANCE_DECISION_VOCABULARY_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine Canon-Shadow formalization plan | `out/audit/abx_codegen_intelligence_spine_canon_shadow_formalization_plan_001.latest.json` | `ABX_CODEGEN_CANON_SHADOW_FORMALIZATION_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine object-model schema plan | `out/audit/abx_codegen_intelligence_spine_object_model_schema_plan_001.latest.json` | `ABX_CODEGEN_OBJECT_MODEL_SCHEMA_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine module surface plan | `out/audit/abx_codegen_intelligence_spine_module_surface_plan_001.latest.json` | `ABX_CODEGEN_MODULE_SURFACE_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine Phase 1 implementation boundary review | `out/audit/abx_codegen_intelligence_spine_phase1_implementation_boundary_review_001.latest.json` | `ABX_CODEGEN_PHASE1_IMPLEMENTATION_BOUNDARY_REVIEW_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine Phase 1 operator authorization request plan | `out/audit/abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_AUTHORIZATION_REQUEST_PLAN_HELD_FOR_OPERATOR` |
| ABX Codegen Intelligence Spine Phase 1 operator evidence packet | `out/audit/abx_codegen_intelligence_spine_phase1_operator_evidence_packet_001.latest.json` | `ABX_CODEGEN_PHASE1_OPERATOR_EVIDENCE_PACKET_HELD_FOR_OPERATOR` |
| P102G+ operator decision surface audit | `out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json` | `P102G_PLUS_OPERATOR_DECISION_SURFACE_AUDIT_READY` |
| Operator review required items bulk disposition | `out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json` | `OPERATOR_REVIEW_REQUIRED_ITEMS_BULK_DISPOSITION_REVIEW_ONLY_APPROVED_WITH_HOLDS` |
| Operator review terminal hold consolidation receipt | `out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.json` | `OPERATOR_REVIEW_TERMINAL_HOLD_CONSOLIDATION_RECEIPT_READY` |
| v2.0 hygiene Phase 1 bulk approval reconciliation | `out/operator_review/v2_hygiene_phase1_bulk_approval_reconciliation_001.latest.json` | `V2_HYGIENE_PHASE1_BULK_APPROVAL_RECONCILIATION_HELD_FOR_OPERATOR_AUTHORIZATION` |
| v2.0 hygiene Phase 1 operator-review dependency cycle audit | `out/operator_review/v2_hygiene_phase1_operator_review_dependency_cycle_audit_001.latest.json` | `V2_HYGIENE_PHASE1_OPERATOR_REVIEW_DEPENDENCY_CYCLE_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 operator-review stabilization strategy plan | `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.json` | `V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_STRATEGY_PLAN_READY` |
| v2.0 hygiene Phase 1 operator-review stabilization decision-record plan | `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_001.latest.json` | `V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN_READY` |
| v2.0 hygiene Phase 1 operator-review stabilization decision-record dry run | `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_001.latest.json` | `V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_DRY_RUN_READY` |
| v2.0 hygiene Phase 1 operator-review stabilization decision-record dry run review | `out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review_001.latest.json` | `V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization review chain compression audit | `out/operator_review/v2_hygiene_phase1_stabilization_review_chain_compression_audit_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_REVIEW_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization operator attestation intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.json` | `ATTESTATION_INTAKE_VALIDATED_FOR_FUTURE_DECISION_RECORD_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_GATE_READY_FOR_SEPARATE_RECORD_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record planning receipt | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_planning_receipt_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_PLANNING_RECEIPT_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record creation gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_GATE_ELIGIBLE_FOR_SEPARATE_CREATION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record creation plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record creation authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record creation authorization chain compression audit | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record materialization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_GATE_READY_FOR_SEPARATE_MATERIALIZATION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record materialization plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record materialization authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record materialization approval intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_intake_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_EMISSION_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record emission gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_GATE_ELIGIBLE_FOR_SEPARATE_RECORD_EMISSION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record emission plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record emission authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record emission approval intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_EMISSION_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record finalization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_GATE_ELIGIBLE_FOR_SEPARATE_RECORD_FINALIZATION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record finalization plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record finalization authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record finalization authorization chain compression audit | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_chain_compression_audit_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record finalization approval intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_approval_intake_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_FINALIZATION_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record completion gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_GATE_ELIGIBLE_FOR_SEPARATE_RECORD_COMPLETION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record completion plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record completion authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record completion approval intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_COMPLETION_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_GATE_ELIGIBLE_FOR_SEPARATE_RECORD_COMPLETION_VALIDATION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation plan | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_PLAN_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation authorization gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation approval intake gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_COMPLETION_VALIDATION_GATE` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation approval gate | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_APPROVAL_GATE_READY_FOR_SEPARATE_RECORD_COMPLETION_VALIDATION_PLANNING` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation implementation receipt | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_IMPLEMENTATION_RECEIPT_READY` |
| v2.0 hygiene Phase 1 stabilization decision-record completion validation execution receipt | `out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_001.latest.json` | `V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_EXECUTION_RECEIPT_READY` |
| v2.0 hygiene Phase 1 authorization record plan | `out/operator_review/v2_hygiene_phase1_authorization_record_plan_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_PLAN_READY` |
| v2.0 hygiene Phase 1 authorization record dry run | `out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_DRY_RUN_READY` |
| v2.0 hygiene Phase 1 authorization record dry run review | `out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_review_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| v2.0 hygiene Phase 1 authorization record review evidence plan | `out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_plan_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_PLAN_READY` |
| v2.0 hygiene Phase 1 authorization record review evidence dry run | `out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_DRY_RUN_READY` |
| v2.0 hygiene Phase 2 governance evidence dry run | `out/operator_review/v2_hygiene_phase2_governance_evidence_dry_run_001.latest.json` | `V2_HYGIENE_PHASE2_GOVERNANCE_EVIDENCE_DRY_RUN_READY` |
| v2.0 hygiene Phase 1 authorization record review evidence dry run review | `out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_001.latest.json` | `V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` |
| Operator authorization seal review | `out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json` | `OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_REVIEW_HELD_FOR_OPERATOR` |

These surfaces do not grant authority, do not promote canon, and do not alter runtime behavior.

Current operator-sync/planning states:
- **Namespace/status stabilization:** repository badges and continuity spine are observational deterministic surfaces; `governance_status=FROZEN`, `canon_status=ADVISORY_ONLY`, `lane_count=58`, and `highest_observed_lane=P102G` are preserved.
- **Operator sync:** Notion queue/backlog surfaces are advisory-only, deny Notion/GitHub writeback, and deny auto-continuation. The Oracle Signal shadow intake review decision record accepts the shadow receipt as review-only evidence without opening downstream authority.
- **Oracle planning:** Oracle Signal Intake Boundary and Oracle Confidence Calibration surfaces are planning/dry-run evidence only. The additive Oracle Signal shadow receipt is reviewed evidence only; it grants no forecast, runtime, queue, canon, scheduler, route, writeback, token, or execution authority.
- **Authorization seal state:** P81-P95 operator authorization record planning surfaces are present, but the seal review is held for operator review. Approval, authorization, token minting, and execution authority remain false.
- **Artifact-lineage repair planning:** Direct repair has an advisory-only separate execution spec plan and scoped execution receipt. Registry repairs, markdown/JSON pairing repairs, docs-reference repairs, runner casing discovery, and Notion mapping scope are classified by explicit advisory records; live Notion/GitHub writeback, runner path normalization, runtime/canon/queue mutation, and unscoped execution remain denied. Unsupported downstream execution claims remain `NOT_COMPUTABLE`.

---

## 05. Routing and Rune Binding

Route/rune binding is now a formalized advisory surface sourced from repository contracts.

**Binding matrix summary** (source: `out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json`):
- Total runes in catalog: `24`
- Bound runes (present in at least one pipeline): `20`
- Unbound runes: `4` (`RUNE.PIPELINE.OPERATOR_REVIEW`, `RUNE.PIPELINE.STABILIZATION_DECIDE`, `RUNE.YGGDRASIL.ROUTE_RECEIPT`, `RUNE.YGGDRASIL.UNKNOWN_NODE_GATE`)
- Pipelines: `7`
- Route-reachable pipelines: `7`
- Required mapping rows: `89`
- Binding classification: `PARTIAL` (route rune nodes observed without explicit `rune_id` field linkage)
- Advisory status: `BINDING_SURFACE_FORMALIZED_ADVISORY_ONLY`

**Coupling map** (source: `out/audit/yggdrasil_coupling_map_001.latest.json`):
- Derived from: pipeline contracts + route graphs
- Authority locks: all `false` (deny-by-default across all rune/pipeline/route surfaces)

This surface is advisory-only. It describes observed binding topology; it does not grant routing authority.

---

## 06. Repository Signal Surface

Status values generated automatically from repository scans. Badge endpoint availability is conditional: treat Pages-backed badges as live only when `ENABLE_STATUS_PAGES_DEPLOY=true` and GitHub Pages is configured.

| Signal | Observed Value | Source | Badge (deployment-dependent) |
|---|---|---|---|
| Build Status | `NOT_COMPUTABLE` | `badges.json#signals.build_status` | ![Build](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/build.json) |
| Test Status | `NOT_COMPUTABLE` | `badges.json#signals.test_status` | ![Tests](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/tests.json) |
| Coverage Status | `NOT_COMPUTABLE` | `badges.json#signals.coverage_status` | ![Coverage](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/coverage.json) |
| Contracts | `362` | `badges.json#signals.contract_count` | ![Contracts](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/contracts.json) |
| Schemas | `342` | `badges.json#signals.schema_count` | ![Schemas](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/schemas.json) |
| Runes | `24` | `badges.json#signals.rune_count` | ![Runes](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/runes.json) |
| Continuity Lanes | `58` | `badges.json#signals.continuity_lane_count` | ![Continuity](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/continuity.json) |
| Governance Status | `FROZEN` | `badges.json#signals.governance_status` | ![Governance](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/governance.json) |
| Canon Status | `ADVISORY_ONLY` | `badges.json#signals.canon_status` | ![Canon](https://img.shields.io/endpoint?url=https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/canon.json) |

Extended observed counts (source: `docs/status/badges.json#live_status`):
- Observed Tests: `750`
- Observed Artifacts: `561`
- Last Observed Commit: `NOT_COMPUTABLE`
- Last Scan Time: `NOT_COMPUTABLE`

---

## 07. System Atlas

Master atlas: [`docs/atlas/ABRAXAS_ATLAS.md`](docs/atlas/ABRAXAS_ATLAS.md)

| Surface | Atlas Card | Status |
|---|---|---|
| Oracle Signal Layer | [`docs/atlas/oracle-signal-layer.md`](docs/atlas/oracle-signal-layer.md) | OBSERVED |
| YGGDRASIL Routing | [`docs/atlas/yggdrasil-routing.md`](docs/atlas/yggdrasil-routing.md) | OBSERVED |
| ABX-Runes | [`docs/atlas/abx-runes.md`](docs/atlas/abx-runes.md) | OBSERVED |
| Governance Engine | [`docs/atlas/governance-engine.md`](docs/atlas/governance-engine.md) | OBSERVED |
| Temporal Continuity Spine | [`docs/atlas/temporal-continuity-spine.md`](docs/atlas/temporal-continuity-spine.md) | OBSERVED |
| Research Canary | [`docs/atlas/research-canary.md`](docs/atlas/research-canary.md) | OBSERVED |
| AAL-Viz | [`docs/atlas/aal-viz.md`](docs/atlas/aal-viz.md) | OBSERVED |
| Artifact Registry | [`docs/atlas/artifact-registry.md`](docs/atlas/artifact-registry.md) | OBSERVED |

---

## 08. Architecture Diagrams

- ![Oracle Signal Layer](docs/media/oracle-signal-layer.svg)
- ![Governance Promotion](docs/media/governance-promotion.svg)
- ![Temporal Continuity Spine](docs/media/temporal-continuity-spine.svg)
- ![YGGDRASIL Routing](docs/media/yggdrasil-routing.svg)
- ![ABX-Runes](docs/media/abx-runes.svg)
- ![AAL Core](docs/media/aal-core.svg)

Visual system specification: [`docs/media/README_VISUAL_SYSTEM.md`](docs/media/README_VISUAL_SYSTEM.md)

---

## 09. Repository Topology

```text
apps/         read-only API and service entrypoints
core/         deterministic symbolic/gov/runtime logic
  core/optimization/  — Bayesian meta-optimization & Optuna backend (Sprint 4)
contracts/    schemas and contract-bound architecture surfaces
docs/         atlas, audits, plans, visual system, status surfaces
fixtures/     replay fixtures and static verification data
input/        operator-provided runtime inputs and decisions
out/          generated artifacts and governance evidence
scripts/      deterministic generator and replay entrypoints
tests/        replay-stable validation suites
```

---

## 10. Repo ↔ Notion Reconciliation

Source: `docs/audits/ABRAXAS_REPO_NOTION_DIFF_001.md`

Post-refresh note: the repo/Notion advisory sync artifacts were refreshed after the P95 authorization seal review merge. The refreshed queue/backlog still denies Notion writeback, GitHub writeback, auto-continuation, runtime mutation, scheduler mutation, canon mutation, activation, and execution authority.

| Surface | Status | Evidence |
|---|---|---|
| YGGDRASIL ABX-Runes Full Stack Binding | PARTIAL | binding matrix emitted; route rune_id linkage partial |
| Tier-1 Subsystem Registry | OBSERVED | `core/pipelines/registry.py` |
| Runtime Integration Gate | OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_READY | runtime spine skeleton present; deterministic integration receipt emitted; operator-review advisory spec plan emitted; mandatory pre-dispatch wiring remains disabled and downstream remains `NOT_COMPUTABLE` |
| Continuation Frontier | CONTINUATION_FRONTIER_RECONCILIATION_EMITTED_ADVISORY_ONLY | `out/audit/continuation_frontier_reconciliation_001.latest.json`; current repo evidence is ahead of the older Notion queue, P131+ remains stale/superseded without fresh governed operator decision evidence, P130 output is observed with `missing_artifact_records=0`, registry coverage repair completion is observed as `COVERAGE_REPAIR_CHAIN_COMPLETE`, and no research-canary artifact regeneration was performed |
| v2 operator Phase 15 execution surface expansion | REPO_NOTION_ALIGNED_ADVISORY_ONLY | Notion Upgrade Completion Receipt (2026-06-13); PR #659 (`94d310d0`); gate hash `85e69c0120116b88eb212eea75b90223e31ac88f2837f718aaa3fe3996f19172`; upstream Phase 14 `20c83ab91c7aa97ccc6ce92f460c71cbb375f483b2e29a173b487efea6af3577`; `out/operator_review/v2_hygiene_phase8_execution_surface_expansion_advisory_gate_001.latest.json`; denies execution authority and Notion writeback; downstream `NOT_COMPUTABLE` |
| Global Ingest Adapter Spine | PARTIAL | scheduler, handoff executor, ingest queue, additive Oracle Signal shadow receipt, review request, and review-only decision record observed; execution remains advisory-only |
| Belief Graph Engine | ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_REVIEW_HELD_FOR_OPERATOR | seal receipt review held; seal creation, receipt code, and engine implementation remain blocked |
| Research Shadow Replay Engine | OBSERVED | `core/research_shadow_replay_audit.py` |
| Phase Percolation Engine | PARTIAL | partial temporal surfaces only |
| AAL-Viz Projection Spine | OBSERVED | `core/aal_viz_runtime_projection.py` |
| Situation Runtime Engine | PARTIAL | advisory console observed |
| ABX Codegen Intelligence Spine | ADVISORY_STACK_HELD_FOR_OPERATOR | deterministic advisory stack emitted through Phase 1 operator review request plus packet schema/fixture validation receipt and Notion stack alignment audit, field-level ImprovementProposal shadow replay wiring, sample Meta-Gate chain validation, sample fixture normalization planning, schema master registry alignment planning, recommended patch sequence precondition planning, merge-anchor coverage planning, and merge-anchor evidence request planning; codegen spine implementation, harness execution, `contracts/codegen/` creation, `core/codegen/` creation, implementation module/script/test creation, `core/codegen_shadow_replay_harness.py` creation, operator decision record creation, operator attestation, authorization record creation, Meta-Gate seal creation, PatchContract/CodeDropEnvelope/PolicyReviewPacket/CodegenHandoff schema creation, implementation builder/runner creation, live shadow replay receipt creation, schema mutation, recommendation routing, fixture mutation, implementation prompt emission, code generation, code mutation, file writeback, and execution remain blocked |

Overall reconciliation status: `PARTIAL`

Current sync frontier: `Global Ingest Adapter Spine` has reached an additive Oracle Signal shadow intake receipt and review-only decision record. It remains blocked before any Oracle Signal implementation, ingest runner mutation, queue mutation, or route/runtime integration work.

---

## 11. Roadmap

Roadmap items included only where evidence is observable in-repo.

| Item | Status | Evidence |
|---|---|---|
| Route/Rune Binding | `FORMALIZED_ADVISORY` | `out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json` |
| Belief Graph | `ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR` | `out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_001.latest.json`; operator attestations, decision-record creation, seal creation, receipt code, and engine implementation remain blocked |
| Global Ingest | `PARTIAL` | `Scripts/run_ingest_scheduler.py`, `Scripts/run_ingest_handoff_executor.py`, `out/ingest/oracle_intake_queue_001.latest.json`, `out/oracle/oracle_signal_intake_receipt.latest.json`, `out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json`, `out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json` |
| Research Shadow Replay | `OBSERVED` | `scripts/run_research_shadow_replay_audit.py` |
| Phase Percolation | `NOT_COMPUTABLE` | partial only |
| AAL-Viz Projection | `OBSERVED` | `scripts/run_aal_viz_runtime_projection.py` |
| v2.0 Hygiene Loop-Awareness | `V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR` | `out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review_001.latest.json`; deterministic advisory review confirms the simulated validation-review evidence bundle remains missing and unattested. It keeps the validation review, Phase 1/2 backlog, and Phase 3/4 placeholder state held, and denies evidence bundle creation, operator attestation creation, authorization-record creation, output-surface integration, feature-flag activation, component promotion, module code/test creation, module/rune registration, HygienePipeline integration, projection/schema mutation, writeback, auto-continuation, strict-mode enablement, runtime mutation, and execution |
| Codegen Intelligence Spine | `ABX_CODEGEN_INTELLIGENCE_SPINE_NOTION_STACK_ALIGNMENT_AUDIT_READY` | `out/audit/abx_codegen_intelligence_spine_notion_stack_alignment_audit_001.latest.json`; advisory audit confirms the June 12 Notion parent spec, full-stack planning surface, and sample fixture vectors are represented by repo-side packet schemas, deterministic fixtures, packet validation receipt, and held Phase 1 operator review surfaces. Downstream remains `NOT_COMPUTABLE`; Codegen spine implementation, harness execution, `contracts/codegen/` creation, `core/codegen/` creation, implementation module/script/test creation, `core/codegen_shadow_replay_harness.py` creation, operator decision record creation, operator attestation, authorization record creation, evidence bundle creation, Meta-Gate seal creation, PatchContract/CodeDropEnvelope/PolicyReviewPacket/CodegenHandoff schema creation, implementation builder/runner creation, live shadow replay receipt creation, schema mutation, recommendation routing, fixture mutation, implementation prompt emission, code generation, code mutation, file writeback, and execution remain blocked |
| Situation Runtime | `OBSERVED` | `scripts/run_operator_runtime_console.py` |

---

## 12. Operator Paths

- **NEW OPERATOR:** [`docs/operators/new-operator.md`](docs/operators/new-operator.md)
- **RESEARCHER:** [`docs/operators/researcher.md`](docs/operators/researcher.md)
- **ARCHITECT:** [`docs/operators/architect.md`](docs/operators/architect.md)
- **CONTRIBUTOR:** [`docs/operators/contributor.md`](docs/operators/contributor.md)

---

## 13. Research Domains

- [Symbolic Compression](docs/audits/REPO_AUDIT_CHAMFER_EXPECTED_DISTANCE_POLICY_PLAN_v0_1.md)
- [Temporal Resonance](scripts/run_temporal_resonance_coherence.py)
- [Governance Systems](docs/generated_artifact_policy_v1.md)
- [Coherence Fields](scripts/run_coherence_field_operator_surface.py)
- [Forecast Architecture](scripts/run_forecast_candidates.py)
- [Persistence Geometry](scripts/run_temporal_persistence_memory.py)
- [Topology Research](scripts/run_temporal_topology_cartography.py)
- [Research Canary](docs/atlas/research-canary.md)

---

## Optimization

Meta-optimization and Bayesian hyperparameter tuning infrastructure (Sprint 4).

- Location: `core/optimization/`
- Optuna backend wrapper for provenance-aware tuning: `core/optimization/optuna_backend.py`
- Module README: `core/optimization/README.md`

Supports higher-order calibration of prediction engines, rune/route parameters, governance surfaces, and forecast pipelines. All optimization runs remain under the same governance, evidence, and replay rules as the rest of the system.

Status: OBSERVED

---

## 14. Shields / GitHub Pages

Badge endpoints are available after a successful GitHub Pages deployment (`ENABLE_STATUS_PAGES_DEPLOY=true`, Pages configured).

Treat all endpoints as deployment-dependent until Pages has completed successfully:
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges.json`
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/contracts.json`
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/schemas.json`
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/tests.json`
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/continuity.json`
- `https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/governance.json`

---

## 15. Footer

```
README_STATUS_SURFACE_UPDATED=true
CANON_MUTATION=false
RUNTIME_MUTATION=false
FORECAST_ROUTING=false
EXECUTION_AUTHORITY=false
```

**ABRAXAS**
A governed symbolic intelligence architecture.
Built within the Applied Alchemy Labs ecosystem.
Structure before narrative.
Evidence before authority.
Governance before autonomy.
