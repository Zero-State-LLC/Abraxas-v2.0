# Historical Governance Agent Notes

Status: `HISTORICAL_REFERENCE`  
Purpose: preserve operational notes removed from the root agent startup path.

These notes are provenance and recovery guidance. They do not override [`AGENTS.md`](../../AGENTS.md) or [`GOVERNANCE_V3.md`](../../GOVERNANCE_V3.md), and they do not grant production, canon, CLEAR, or runtime authority.

## Research canary spine-refresh isolation guardrail

Do not regenerate `out/research_canary_*` artifacts during a spine-refresh run unless the full canary chain (P128 source -> P129 -> P130) is intentionally replayed from a validated, current P128 source.

Observed failure mode: spine-refresh scripts can downgrade canary artifacts from `COMPLETE_AND_STABLE` to `NOT_COMPUTABLE`, causing cascading CI failure.

Recovery procedure:

1. Run spine-refresh scripts in isolation, scoped only to the temporal-continuity chain.
2. Before any spine refresh, confirm `out/research_canary_activation_readiness_evidence_record/latest.json` and `out/research_canary_final_activation_authorization_review/latest.json` will not be touched.
3. If canary artifacts are accidentally degraded, restore from the last known good commit.

## Temporal continuity P102 handoff archive

When working on sealed temporal-continuity repair lanes, consult these historical runners and outputs:

- P102A: `python scripts/temporal/run_temporal_continuity_p101_readiness_repair_plan.py` -> `out/temporal_continuity_p101_readiness_repair_plan/latest.json`
- P102 compression audit: `python scripts/temporal/run_temporal_continuity_recursive_authorization_chain_compression_audit.py` -> `out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json`
- P102B router: `python scripts/temporal/run_temporal_continuity_repair_execution_plan_router.py`
- P102C selected plan: `python scripts/temporal/run_temporal_continuity_selected_repair_execution_plan.py`

When `chain_recommendation` is `SEAL_RECURSIVE_AUTHORIZATION_CHAIN` or `COMPRESS_TO_GENERIC_TEMPLATE`, do not add another hand-written recursive authorization lane. Route to the recommended P103 lane instead.

## CLI operator layer archive

Prefer targeted CLI operators before broad agent context dumps when they materially reduce ambiguity:

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

Rule: send the smallest complete evidence packet, not a full repo dump. See [`docs/workflows/cli-operator-layer.md`](../workflows/cli-operator-layer.md) when that workflow is relevant.
