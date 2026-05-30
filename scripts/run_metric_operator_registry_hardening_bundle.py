"""Script: emit METRIC_OPERATOR_REGISTRY_HARDENING_BUNDLE — hardening record + frontier update."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.metric_operator_registry_hardening import (
    build_metric_operator_registry_hardening,
    default_drift_guards,
    default_governance_flags as hardening_governance_flags,
    default_hardening_checks,
    default_operator_state_vector,
    default_output_contract as hardening_output_contract,
    serialize_metric_operator_registry_hardening,
)
from core.metric_operator_frontier_recommendation import (
    build_metric_operator_frontier_recommendation,
    default_governance_flags as frontier_governance_flags,
    default_output_contract as frontier_output_contract,
    four_operator_planned_ranked_options,
    serialize_metric_operator_frontier_recommendation,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "METRIC_OPERATOR_REGISTRY_HARDENING_BUNDLE_001"

_PATHS = RuntimePaths.from_env()
HARDENING_OUT  = _PATHS.metric_operator_registry_hardening_001_latest
FRONTIER_OUT   = _PATHS.metric_operator_frontier_recommendation_003_latest

_HARDENING_PAYLOAD: dict = {
    "hardening_id": "metric_operator_registry_hardening_001",
    "hardening_status": "STABLE",
    "operator_state_vector": default_operator_state_vector(),
    "drift_guards": default_drift_guards(),
    "hardening_checks": default_hardening_checks(),
    "source_refs": [
        "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
        "MetricOperatorFrontierRecommendation.v1:metric_operator_frontier_recommendation_002",
        "NormGeometryCpuBaselineActualPrGateReview.v1:"
        "norm_geometry_cpu_baseline_actual_pr_gate_review_001",
        "NormGeometryCpuBaselineImplementationPlan.v1:"
        "norm_geometry_cpu_baseline_implementation_plan_001",
        "NormGeometryCpuBaselineValidationPlan.v1:"
        "norm_geometry_cpu_baseline_validation_plan_001",
        "MetricOperatorRank4SelectionPlan.v1:metric_operator_rank4_selection_plan_001",
    ],
    "output_contract": hardening_output_contract(),
    "governance_flags": hardening_governance_flags(),
    "provenance": {
        "source": "METRIC_OPERATOR_REGISTRY_HARDENING_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_registry_hardening.v1.schema.json",
            "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
        ],
        "evidence_refs": [
            "MetricOperatorRegistryStabilization.v1:"
            "metric_operator_registry_stabilization_002",
            "NormGeometryCpuBaselineActualPrGateReview.v1:"
            "norm_geometry_cpu_baseline_actual_pr_gate_review_001",
            "MetricOperatorRank4SelectionPlan.v1:"
            "metric_operator_rank4_selection_plan_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_FRONTIER_PAYLOAD: dict = {
    "recommendation_id": "metric_operator_frontier_recommendation_003",
    "recommendation_status": "ADVISORY_ONLY",
    "ranked_options": four_operator_planned_ranked_options(),
    "recommended_next_step": "G_SEALED_PAUSE",
    "required_operator_decision": True,
    "stop_boundary_reason": (
        "Registry hardening is complete. NORM_GEOMETRY is at "
        "CPU_BASELINE_PLANNING_COMPLETE posture with gate-cond-005 unmet. "
        "All advancement beyond rank-5 selection requires operator instruction. "
        "NORM_GEOMETRY implementation authorization requires separate explicit "
        "operator authorization. No self-authorizing next step exists."
    ),
    "output_contract": frontier_output_contract(),
    "governance_flags": frontier_governance_flags(),
    "provenance": {
        "source": "METRIC_OPERATOR_REGISTRY_HARDENING_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_frontier_recommendation.v1.schema.json",
            "contracts/canon/metric_operator_registry_hardening.v1.schema.json",
        ],
        "evidence_refs": [
            "MetricOperatorRegistryHardening.v1:metric_operator_registry_hardening_001",
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
            "NormGeometryCpuBaselineActualPrGateReview.v1:"
            "norm_geometry_cpu_baseline_actual_pr_gate_review_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "metric_operator_registry_hardening_bundle",
        artifact_path=HARDENING_OUT,
        context={"patch_id": PATCH_ID},
    )
    log_event(logger, "INFO", "metric_operator_registry_hardening_bundle_started",
              correlation_id=correlation_id)

    HARDENING_OUT.parent.mkdir(parents=True, exist_ok=True)

    hardening = build_metric_operator_registry_hardening(_HARDENING_PAYLOAD)
    HARDENING_OUT.write_text(
        serialize_metric_operator_registry_hardening(hardening), encoding="utf-8"
    )
    log_event(logger, "INFO", "metric_operator_registry_hardening_emitted",
              canonical_hash=hardening.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    osv = hardening.get("operator_state_vector", [])
    shadow_count = sum(
        1 for e in osv if e.get("computation_status") == "SHADOW_STUB_ONLY"
    )
    not_impl_count = sum(
        1 for e in osv if e.get("computation_status") == "NOT_IMPLEMENTED"
    )
    checks = hardening.get("hardening_checks", [])
    passed = sum(1 for c in checks if c.get("check_result") == "PASS")
    guards = hardening.get("drift_guards", [])
    active = sum(1 for g in guards if g.get("guard_status") == "ACTIVE")
    print(f"hardening  canonical_hash={hardening.get('canonical_hash','?')}")
    print(f"  hardening_status={hardening.get('hardening_status','?')}")
    print(f"  shadow_stub_only={shadow_count}  not_implemented={not_impl_count}")
    print(f"  hardening_checks={len(checks)} passed={passed}/{len(checks)}")
    print(f"  drift_guards={len(guards)} active={active}/{len(guards)}")
    print(f"  wrote={HARDENING_OUT.as_posix()}")

    frontier = build_metric_operator_frontier_recommendation(_FRONTIER_PAYLOAD)
    FRONTIER_OUT.write_text(
        serialize_metric_operator_frontier_recommendation(frontier), encoding="utf-8"
    )
    log_event(logger, "INFO", "metric_operator_frontier_recommendation_003_emitted",
              canonical_hash=frontier.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    opts = frontier.get("ranked_options", [])
    print(f"frontier   canonical_hash={frontier.get('canonical_hash','?')}")
    print(f"  recommendation_status={frontier.get('recommendation_status','?')}")
    print(f"  recommended_next_step={frontier.get('recommended_next_step','?')}")
    print(f"  ranked_options={len(opts)}")
    print(f"  wrote={FRONTIER_OUT.as_posix()}")

    log_event(logger, "INFO", "metric_operator_registry_hardening_bundle_completed",
              correlation_id=correlation_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
