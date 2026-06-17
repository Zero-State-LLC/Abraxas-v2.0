# Phase 20 Autonomy Activation + Brier (Murphy + Yates) Hardening Handoff

This packet is documentation only. It records manual operator review for Phase 20
autonomy activation hardening and dual Brier decomposition telemetry under continued
ACTIVE operator review posture. It is not an auto-approval, webhook trigger, Notion
writeback request, authorization record, or gate-granted execution authority grant.

## Provenance

| Field | Classification | Value |
|---|---|---|
| `operator_review_posture` | OBSERVED | `ACTIVE` |
| `notion_writeback_allowed` | OBSERVED | `false` |
| `valid_for_autonomy_hardening` | INFERRED | true only when gate READY |
| `valid_for_execution` | OBSERVED | `false` |
| `downstream` | OBSERVED | `NOT_COMPUTABLE` |

## Hash chain review (operator must verify)

| Link | Expected source |
|---|---|
| Phase 19 gate | `out/operator_review/v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_001.latest.json` |
| Phase 20 gate | `out/operator_review/v2_hygiene_phase13_autonomy_activation_brier_hardening_gate_001.latest.json` |

## Surfaces hardened when gate READY (recorded only)

| Surface | Promotion class |
|---|---|
| `rune_visualization_layer` | `OPERATOR_EXECUTION_AUTONOMY_RUNE_VIZ_HARDENING_RECORDED` |
| `incarnation_core_planning_binding` | `OPERATOR_EXECUTION_AUTONOMY_INCARNATION_CORE_HARDENING_RECORDED` |
| `planning_lane_outputs` | `OPERATOR_EXECUTION_AUTONOMY_PLANNING_LANE_HARDENING_RECORDED` |
| `core_oracle_shadow` | `OPERATOR_EXECUTION_AUTONOMY_ORACLE_SHADOW_HARDENING_RECORDED` |
| `brier_engine_telemetry` | `OPERATOR_EXECUTION_AUTONOMY_BRIER_TELEMETRY_HARDENING_RECORDED` |

## Brier decomposition telemetry

- Murphy decomposition: reliability, resolution, uncertainty
- Yates decomposition: bias_squared, excess_variance, covariance_deficit
- Unified entry point: `core/scoring/brier.py::compute_full_decomposition()`
- Resolution authority remains denied at gate level

## Authority boundaries (fail-closed)

- `execution_authority`
- `brier_resolution_authorized`
- `package_lock_mutation_authorized`
- `toolchain_provisioning_authorized`
- `notion_writeback_allowed`

## Manual operator steps

1. Review hash chain in Phase 20 gate `operator_attestation_workflow_contract.hash_chain`
2. Confirm Phase 19 gate hash matches operator sign-off record
3. Verify dual Brier decomposition telemetry in `brier_hardening_contract`
4. Confirm all five surfaces show `autonomy_hardening_recorded: true` when READY
5. Do not treat this gate as execution authorization
