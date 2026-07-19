# Fusion Downstream Advisory Continuity Consumer Audit

## Scope
Read-only audit of downstream consumers for:
- `out/projections/cross_run_topology_fusion_001.latest.json`
- `out/audit/fusion_evidence_materialization_seal_001.latest.json`
- `out/projections/temporal_state_diff_pulse_ledger_001.latest.json`
- `out/projections/temporal_lineage_pulse_ledger_001.latest.json`

## Consumer map and classification

| Consumer | Path | Inputs observed | Classification | Notes |
|---|---|---|---|---|
| Multi-run convergence packet builder | `core/multi_run_convergence.py` | `cross_run_topology_fusion` | ALREADY_CONSUMED | Reads fusion packet and projects advisory-only fusion metrics/status into convergence output. |
| Temporal continuity spine precheck | `core/temporal_continuity_spine_precheck.py` | `cross_run_topology_fusion` | ALREADY_CONSUMED | Fusion is a required path in temporal coherence chain group and status-probed. |
| Temporal upstream evidence receipt | `core/temporal_upstream_evidence.py` | `cross_run_topology_fusion` | ALREADY_CONSUMED | Fusion is required dependency with producer script and advisory-only evidence-state classification. |
| Generated artifact registry policy | `core/generated_artifact_registry.py` | fusion packet, pulse ledgers, seal receipt | PROJECTION_ONLY_READY | Artifacts are tracked as derived optional surfaces; registry can include them without authority drift. |
| Fusion seal receipt generator | `scripts/viz/run_fusion_evidence_materialization_seal.py` | pulse ledgers + fusion hash summary | NOT_APPLICABLE | Produces seal receipt; does not serve as downstream consumer bridge. |
| AAL-Viz runtime projection | `core/aal_viz_runtime_projection.py` | none of fusion/seal/pulse ledgers | MISSING_VIEW_ADAPTER | Projection module remains advisory-only but has no adapter for fusion summary exposure. |
| Operator runtime console | `core/operator_runtime_console.py` | none of fusion/seal/pulse ledgers | ADVISORY_CONSUMER_GAP | Console is advisory/projection-only and deterministic, but fusion evidence is not surfaced. |
| Canon resume state | `core/canon_resume_state.py` | no direct fusion/seal usage | NOT_APPLICABLE | Lane evidence surface; not a projection consumer for fusion seal flow. |
| Sync snapshot surfaces | `core/sync_snapshot.py` | no direct fusion/seal usage | NOTION_SYNC_ONLY | Sync snapshots are sync-facing; no direct runtime projection bridge found for fusion seal. |
| Oracle Signal Layer surfaces | no dedicated module found by query | none | NOT_APPLICABLE | No explicit Oracle Signal Layer consumer path found in repository query results. |

## Strongest current legal consumer
`core/multi_run_convergence.py` is the strongest current legal downstream consumer. It already consumes `cross_run_topology_fusion` and carries only advisory/projection metrics (`cross_run_topology_fusion_status`, fusion counts, continuity statuses, advisory flags), with no mutation authority granted.

## Routing verdict
- **Sealed fusion result is already routed** via `cross_run_topology_fusion` into temporal continuity and convergence surfaces.
- **Seal receipt (`fusion_evidence_materialization_seal`) is currently visible but mostly unused** as a downstream projection input.
- **Pulse ledgers are consumed upstream by fusion generation and represented in seal evidence hashes**, but not independently bridged into AAL-Viz or operator console packets.

## Single safest first downstream bridge
Bridge target: **AAL-Viz runtime projection summary block** in `core/aal_viz_runtime_projection.py`.

Reason:
1. Existing surface is already projection-only/advisory-only with hard authority invariants.
2. Existing packet structure already integrates deterministic summaries from multiple advisory artifacts.
3. Adding a compact, deterministic fusion seal summary (status/hash/blocker count only) is a minimal adapter with no canon/runtime mutation.

## Exact minimal missing bridge
Add a **fusion evidence summary adapter** in AAL-Viz runtime projection:
- input: `out/audit/fusion_evidence_materialization_seal_001.latest.json`
- output fields (deterministic summary only):
  - `fusion_seal_status`
  - `fusion_final_status`
  - `fusion_remaining_blocker_count`
  - `fusion_summary_hash`
  - `fusion_receipt_hash`
- hard invariants preserved:
  - `advisory_only = true`
  - `projection_only = true`
  - `authority_granted = false`
  - `forecast_authority = false`
  - `mutation_allowed = false`
- no scheduler, network, threshold logic, routing, or execution hooks.

## Recommended next Codex patch prompt
"Implement a minimal projection-only adapter in `core/aal_viz_runtime_projection.py` that reads `out/audit/fusion_evidence_materialization_seal_001.latest.json` and adds a deterministic `fusion_evidence_summary` block (status/hash/blocker-count only) into the runtime projection packet. Preserve all authority invariants and add focused tests in `tests/test_aal_viz_runtime_projection.py` for present/missing/corrupt seal input with fail-closed `NOT_COMPUTABLE` behavior. Do not modify fusion generation or seal receipt semantics."

## Governance risk assessment
- **Current risk**: low-to-medium observability gap (sealed fusion evidence not surfaced in key projection UI packet).
- **Authority risk**: low if adapter remains summary-only and inherits existing AAL-Viz runtime projection authority boundary.
- **Drift risk**: low if adapter uses deterministic field extraction and canonical ordering.
- **Escalation risk**: low; no new subsystem required, no duplicate architecture.
