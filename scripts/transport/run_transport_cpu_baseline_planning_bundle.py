"""Script: emit TRANSPORT_CPU_BASELINE_PLANNING_BUNDLE — three advisory-only artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.transport_cpu_baseline_implementation_plan import (
    build_transport_cpu_baseline_implementation_plan,
    default_algorithm_plan,
    default_benchmark_plan,
    default_future_acceleration_seams,
    default_implementation_constraints,
    default_input_data_contract,
    default_memory_layout_plan,
    default_numerical_stability_plan,
    default_output_contract as impl_plan_output_contract,
    default_output_data_contract,
    default_validation_plan as impl_validation_plan,
    serialize_transport_cpu_baseline_implementation_plan,
)
from core.transport_cpu_baseline_validation_plan import (
    build_transport_cpu_baseline_validation_plan,
    default_fixture_validation_scope,
    default_invalid_fixture_rejection_scope,
    default_no_forecast_scan,
    default_no_lp_solver_scan,
    default_no_p43_scan,
    default_no_runtime_scan,
    default_output_contract as val_plan_output_contract,
    default_tolerance_policy,
    serialize_transport_cpu_baseline_validation_plan,
)
from core.transport_cpu_baseline_actual_pr_gate_review import (
    build_transport_cpu_baseline_actual_pr_gate_review,
    default_gate_conditions,
    default_output_contract as gate_review_output_contract,
    serialize_transport_cpu_baseline_actual_pr_gate_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "TRANSPORT_CPU_BASELINE_PLANNING_BUNDLE_001"
_LOCKED_FALSE_FLAGS = {
    "production_activation": False, "canon_promotion": False,
    "scheduler_mutation": False, "runtime_authority": False,
    "runtime_mutation": False, "forecast_influence": False,
    "execution_authority": False, "token_minting_allowed": False,
    "valid_for_execution": False, "activation_approved": False,
    "authorization_granted": False,
}

_PATHS = RuntimePaths.from_env()
IMPL_OUT = _PATHS.transport_cpu_baseline_implementation_plan_latest
VAL_OUT  = _PATHS.transport_cpu_baseline_validation_plan_latest
GATE_OUT = _PATHS.transport_cpu_baseline_actual_pr_gate_review_latest

_IMPL_PLAN_PAYLOAD: dict = {
    "plan_id": "transport_cpu_baseline_implementation_plan_001",
    "implementation_topology": {
        "implementation_mode": "CPU_REFERENCE_PLAN",
        "intended_lane": "SHADOW",
        "topology_stage": "ALGORITHM_TOPOLOGY_ONLY",
    },
    "algorithm_plan": default_algorithm_plan(),
    "numerical_stability_plan": default_numerical_stability_plan(),
    "input_data_contract": default_input_data_contract(),
    "output_data_contract": default_output_data_contract(),
    "memory_layout_plan": default_memory_layout_plan(),
    "benchmark_plan": default_benchmark_plan(),
    "future_acceleration_seams": default_future_acceleration_seams(),
    "implementation_constraints": default_implementation_constraints(),
    "validation_plan": impl_validation_plan(),
    "output_contract": impl_plan_output_contract(),
    "governance_flags": dict(_LOCKED_FALSE_FLAGS),
    "provenance": {
        "source": "TRANSPORT_CPU_BASELINE_PLANNING_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/transport_cpu_baseline_implementation_plan.v1.schema.json",
        ],
        "evidence_refs": [
            "TransportDistanceImplementationReadinessDossier.v1:"
            "transport_distance_implementation_readiness_dossier_001",
            "TransportTestVectorSchemaPlan.v1:"
            "transport_test_vector_schema_plan_001",
            "MetricOperatorRank5SelectionPlan.v1:"
            "metric_operator_rank5_selection_plan_001",
        ],
    },
    "source_readiness_dossier_refs": [
        "TransportDistanceImplementationReadinessDossier.v1:"
        "transport_distance_implementation_readiness_dossier_001",
    ],
    "source_metric_registry_refs": [
        "MetricOperatorRegistryStabilization.v1:"
        "metric_operator_registry_stabilization_002",
    ],
    "source_test_vector_pack_refs": [
        "MetricOperatorBaselineTestVectorPack.v1:"
        "metric_operator_baseline_test_vector_pack_001",
    ],
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_VAL_PLAN_PAYLOAD: dict = {
    "plan_id": "transport_cpu_baseline_validation_plan_001",
    "fixture_validation_scope": default_fixture_validation_scope(),
    "tolerance_policy": default_tolerance_policy(),
    "invalid_fixture_rejection_scope": default_invalid_fixture_rejection_scope(),
    "no_runtime_scan": default_no_runtime_scan(),
    "no_forecast_scan": default_no_forecast_scan(),
    "no_p43_scan": default_no_p43_scan(),
    "no_lp_solver_scan": default_no_lp_solver_scan(),
    "output_contract": val_plan_output_contract(),
    "governance_flags": dict(_LOCKED_FALSE_FLAGS),
    "provenance": {
        "source": "TRANSPORT_CPU_BASELINE_PLANNING_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/transport_cpu_baseline_validation_plan.v1.schema.json",
        ],
        "evidence_refs": [
            "TransportCpuBaselineImplementationPlan.v1:"
            "transport_cpu_baseline_implementation_plan_001",
        ],
    },
    "source_implementation_plan_refs": [
        "TransportCpuBaselineImplementationPlan.v1:"
        "transport_cpu_baseline_implementation_plan_001",
    ],
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_GATE_REVIEW_PAYLOAD: dict = {
    "review_id": "transport_cpu_baseline_actual_pr_gate_review_001",
    "review_status": "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
    "plans_reviewed": [
        "TransportCpuBaselineImplementationPlan.v1:"
        "transport_cpu_baseline_implementation_plan_001",
        "TransportCpuBaselineValidationPlan.v1:"
        "transport_cpu_baseline_validation_plan_001",
    ],
    "gate_conditions": default_gate_conditions(),
    "implementation_recommendation": "ADVISORY_REVIEW_ONLY",
    "stop_boundary_reason": (
        "Operator authorization required before any implementation PR may be "
        "opened. LP solver variant, pivot rule, tie-breaking strategy, and "
        "balance tolerance must be finalized as locked constants. "
        "This gate review is advisory-only. gate-cond-005 is not met."
    ),
    "output_contract": gate_review_output_contract(),
    "governance_flags": dict(_LOCKED_FALSE_FLAGS),
    "provenance": {
        "source": "TRANSPORT_CPU_BASELINE_PLANNING_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/transport_cpu_baseline_actual_pr_gate_review.v1.schema.json",
        ],
        "evidence_refs": [
            "TransportCpuBaselineImplementationPlan.v1:"
            "transport_cpu_baseline_implementation_plan_001",
            "TransportCpuBaselineValidationPlan.v1:"
            "transport_cpu_baseline_validation_plan_001",
            "TransportDistanceImplementationReadinessDossier.v1:"
            "transport_distance_implementation_readiness_dossier_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "transport_cpu_baseline_planning_bundle",
        artifact_path=IMPL_OUT,
        context={"patch_id": PATCH_ID},
    )
    log_event(logger, "INFO", "transport_cpu_baseline_planning_bundle_started",
              correlation_id=correlation_id)

    IMPL_OUT.parent.mkdir(parents=True, exist_ok=True)

    impl_plan = build_transport_cpu_baseline_implementation_plan(_IMPL_PLAN_PAYLOAD)
    IMPL_OUT.write_text(
        serialize_transport_cpu_baseline_implementation_plan(impl_plan), encoding="utf-8"
    )
    log_event(logger, "INFO", "transport_implementation_plan_emitted",
              canonical_hash=impl_plan.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"impl_plan   canonical_hash={impl_plan.get('canonical_hash','?')}")
    print(f"  steps={len(impl_plan.get('algorithm_plan',[]))}")
    print(f"  wrote={IMPL_OUT.as_posix()}")

    val_plan = build_transport_cpu_baseline_validation_plan(_VAL_PLAN_PAYLOAD)
    VAL_OUT.write_text(
        serialize_transport_cpu_baseline_validation_plan(val_plan), encoding="utf-8"
    )
    log_event(logger, "INFO", "transport_validation_plan_emitted",
              canonical_hash=val_plan.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"val_plan    canonical_hash={val_plan.get('canonical_hash','?')}")
    print(f"  valid_fixture_count={val_plan['fixture_validation_scope']['valid_fixture_count']}")
    print(f"  wrote={VAL_OUT.as_posix()}")

    gate_review = build_transport_cpu_baseline_actual_pr_gate_review(_GATE_REVIEW_PAYLOAD)
    GATE_OUT.write_text(
        serialize_transport_cpu_baseline_actual_pr_gate_review(gate_review), encoding="utf-8"
    )
    log_event(logger, "INFO", "transport_gate_review_emitted",
              canonical_hash=gate_review.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"gate_review canonical_hash={gate_review.get('canonical_hash','?')}")
    conds = gate_review.get("gate_conditions", [])
    met = sum(1 for c in conds if c.get("condition_met"))
    print(f"  gate_conditions={len(conds)} met={met}/{len(conds)}")
    print(f"  recommendation={gate_review.get('implementation_recommendation','?')}")
    print(f"  wrote={GATE_OUT.as_posix()}")

    log_event(logger, "INFO", "transport_cpu_baseline_planning_bundle_completed",
              correlation_id=correlation_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
