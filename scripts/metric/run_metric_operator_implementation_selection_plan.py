"""Script: emit deterministic MetricOperatorImplementationSelectionPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.metric_operator_implementation_selection_plan import (
    build_metric_operator_implementation_selection_plan,
    default_implementation_gates,
    default_output_contract,
    default_readiness_constraints,
    default_selection_policy,
    serialize_metric_operator_implementation_selection_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_DISTANCE_SELECTION_PLAN_CANDIDATE_ADDITION_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.metric_operator_implementation_selection_plan_latest

_PAYLOAD: dict = {
    "plan_id": "metric_operator_implementation_selection_plan_001",
    "source_metric_registry_refs": [
        "MetricOperatorRegistry.v1:metric_operator_registry_001",
    ],
    "source_test_vector_pack_refs": [
        "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
    ],
    "source_renderer_implementation_plan_refs": [
        "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
    ],
    "selection_scope": {
        "selection_family": "FIRST_OPERATOR_SELECTION",
        "intended_lane": "SHADOW",
        "selection_stage": "SELECTION_PLAN_ONLY",
    },
    "operator_candidates": [
        {
            "candidate_id": "cand_001_wasserstein",
            "operator_id": "WASSERSTEIN",
            "operator_family": "TRANSPORT_METRIC",
            "selection_rank": 1,
            "readiness_status": "READY_FOR_IMPLEMENTATION_PLAN",
            "implementation_risk": "MEDIUM",
            "evidence_refs": [
                "MetricComputationPreflight.v1:metric_computation_preflight_001",
                "MetricOperatorRegistry.v1:metric_operator_registry_001",
                "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
                "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
            ],
            "blocked_operations": [
                "metric_math_implementation",
                "runtime_mutation",
                "score_computation",
            ],
            "rationale": (
                "Rank-1 selection for shadow-lane planning only. "
                "Operator review completed; planning gate opened. "
                "Implementation, score computation, and runtime mutation remain blocked."
            ),
            "implementation_status": "SELECTED_FOR_PLANNING_ONLY",
        },
        {
            "candidate_id": "cand_002_chamfer_distance",
            "operator_id": "CHAMFER_DISTANCE",
            "operator_family": "SPATIAL_ALIGNMENT",
            "selection_rank": 2,
            "readiness_status": "READY_FOR_IMPLEMENTATION_PLAN",
            "implementation_risk": "LOW",
            "evidence_refs": [
                "ChamferDistanceImplementationReadinessDossier.v1:chamfer_distance_implementation_readiness_dossier_001",
                "ChamferBaselineImplementationPlan.v1:chamfer_baseline_implementation_plan_001",
                "ChamferFixtureCreationActualPRGate.v1:chamfer_fixture_creation_actual_pr_gate_001",
                "ChamferExpectedDistanceValuesActualPRGate.v1:chamfer_expected_distance_values_actual_pr_gate_001",
                "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            ],
            "blocked_operations": [
                "metric_math_implementation",
                "runtime_mutation",
                "score_computation",
            ],
            "rationale": (
                "Rank-2 selection for shadow-lane planning only. "
                "Canonical operator ID discrepancy resolved (CHAMFER_DISTANCE). "
                "Fixture files, fixture manifest, and static expected distances in place. "
                "14-artifact Chamfer chain kickoff complete. "
                "Implementation, score computation, and runtime mutation remain blocked."
            ),
            "implementation_status": "SELECTED_FOR_PLANNING_ONLY",
        },
    ],
    "selection_policy": default_selection_policy(),
    "readiness_constraints": default_readiness_constraints(),
    "implementation_gates": default_implementation_gates(),
    "output_contract": default_output_contract(),
    "governance_flags": {
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "runtime_mutation": False,
        "forecast_influence": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "activation_approved": False,
        "authorization_granted": False,
    },
    "provenance": {
        "source": "CHAMFER_DISTANCE_SELECTION_PLAN_CANDIDATE_ADDITION",
        "evidence_refs": [
            "MetricComputationPreflight.v1:metric_computation_preflight_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
            "ChamferDistanceImplementationReadinessDossier.v1:chamfer_distance_implementation_readiness_dossier_001",
            "ChamferExpectedDistanceValuesActualPRGate.v1:chamfer_expected_distance_values_actual_pr_gate_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_computation_preflight.v1.schema.json",
            "contracts/canon/metric_operator_implementation_selection_plan.v1.schema.json",
            "contracts/canon/metric_operator_registry.v1.schema.json",
            "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "metric_operator_implementation_selection_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "metric_operator_implementation_selection_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_metric_operator_implementation_selection_plan(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_metric_operator_implementation_selection_plan(packet), encoding="utf-8"
    )

    log_event(
        logger,
        "INFO",
        "metric_operator_implementation_selection_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
