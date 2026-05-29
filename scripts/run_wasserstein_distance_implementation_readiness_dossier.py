"""Script: emit deterministic WassersteinDistanceImplementationReadinessDossier.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wasserstein_distance_implementation_readiness_dossier import (
    build_wasserstein_distance_implementation_readiness_dossier,
    default_authority_locks,
    default_governance_flags,
    default_output_contract,
    serialize_wasserstein_distance_implementation_readiness_dossier,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_P44_WASSERSTEIN_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_distance_implementation_readiness_dossier_latest

_PAYLOAD: dict = {
    "dossier_id": "wasserstein_distance_implementation_readiness_dossier_001",
    "source_selection_plan_hash": (
        "7a3fb47ca43587983d359d4a6e9cd1ef1868f76ac2ae90c130f3b5dc14acc9b8"
    ),
    "source_metric_preflight_hash": (
        "e1e3f8a0bd2999aebecf0dcbc5c94ce87d967c056f2ed18261b33e6de2b20238"
    ),
    "source_metric_registry_hash": (
        "0493c034f1f270d31f23c211c0a938d75e0634299f1123db872b503ccb4bd0e3"
    ),
    "source_baseline_vector_pack_hash": (
        "053988aac083e06cf727a42675ae6e3f025e884d521f584d5b631ff813c2f0db"
    ),
    "implementation_scope": {
        "mode": "PLANNING_ONLY",
        "planning_lane": "SHADOW_METRIC_OPERATOR",
        "readiness_status": "WASSERSTEIN_READINESS_DOSSIER_DEFINED",
    },
    "mathematical_requirements": [
        (
            "1D Wasserstein (Earth Mover Distance on R): computed via sorted CDF difference; "
            "deterministic and O(n log n); no approximation required."
        ),
        (
            "2D Wasserstein on R^2: requires discrete optimal transport (OT) linear program; "
            "deterministic for a fixed solver and pinned configuration."
        ),
        (
            "Ground metric (cost function c(x, y)) must be fully specified before fixture creation; "
            "Euclidean distance is the default candidate and has not yet been confirmed "
            "for the AAL-Viz geometric surface context."
        ),
        (
            "Higher-dimensional inputs require OT or Sinkhorn approximation; "
            "any approximation algorithm must freeze tolerance parameters "
            "before fixture creation to guarantee reproducibility."
        ),
        (
            "No Wasserstein computation is performed in this dossier; "
            "mathematical requirements are planning metadata only."
        ),
    ],
    "input_shape_requirements": [
        (
            "Input pair: two discrete probability distributions or finite point clouds "
            "over a shared metric space; exact domain to be determined at test vector schema plan stage."
        ),
        (
            "Distributions must be represented as finite discrete measures with non-negative weights "
            "summing to 1, or as unnormalised histograms with normalisation applied before computation."
        ),
        (
            "Point cloud inputs require a ground metric (cost matrix or implicit metric function) "
            "to be frozen before fixture creation."
        ),
        (
            "Geometric surface descriptor type (SVG path data, Canvas pixel array, WebGL vertex buffer) "
            "is not yet mapped to a Wasserstein input shape; "
            "input shape determination is deferred to the test vector schema plan."
        ),
        (
            "Input shape specification is advisory and planning-only; "
            "no computation is performed in this dossier."
        ),
    ],
    "determinism_requirements": [
        (
            "All Wasserstein computations must be deterministic given identical inputs "
            "and frozen algorithm parameters."
        ),
        (
            "1D Wasserstein is fully deterministic via sort-based algorithms "
            "with no tolerance parameters."
        ),
        (
            "For 2D and higher inputs, the OT solver must be pinned to a fixed version "
            "and configuration; solver non-determinism must be characterised before fixture creation."
        ),
        (
            "Sinkhorn epsilon and max_iterations parameters must be frozen if approximation is used; "
            "epsilon variation must be documented as a numerical stability risk."
        ),
        (
            "Hash stability requires byte-identical output for identical inputs; "
            "floating-point non-determinism across CPU architectures must be assessed "
            "at the test vector schema plan stage."
        ),
    ],
    "numerical_stability_requirements": [
        (
            "1D Wasserstein on R: stable for well-separated distributions; "
            "degenerate inputs (all mass at one point) must be handled "
            "without division by zero and produce a documented NOT_COMPUTABLE path."
        ),
        (
            "Discrete OT for 2D and higher inputs: condition number of the cost matrix "
            "affects solver stability; ill-conditioned matrices must be flagged "
            "in the test vector schema plan."
        ),
        (
            "Sinkhorn regularisation: log-domain stabilisation required for small epsilon; "
            "naive exponentiation overflows for distributions with large support."
        ),
        (
            "Empty or zero-weight distribution inputs must be handled gracefully "
            "with a documented NOT_COMPUTABLE output path."
        ),
        (
            "Float64 (double) precision required throughout; "
            "float32 must be flagged as a numerical risk in the test vector schema plan."
        ),
    ],
    "validation_requirements": [
        {
            "strategy_id": "val_001_reference_vector",
            "validation_type": "REFERENCE_VECTOR",
            "description": (
                "Baseline test vectors from the metric operator baseline test vector pack "
                "must be extended with Wasserstein-specific reference inputs and pinned "
                "expected output scalars before implementation begins."
            ),
            "evidence_refs": [
                "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            ],
        },
        {
            "strategy_id": "val_002_deterministic_replay",
            "validation_type": "DETERMINISTIC_REPLAY",
            "description": (
                "Dossier generation must replay deterministically with stable canonical hash "
                "equivalence across all runs."
            ),
            "evidence_refs": [
                "tests/test_wasserstein_distance_implementation_readiness_dossier.py",
            ],
        },
        {
            "strategy_id": "val_003_numerical_stability",
            "validation_type": "NUMERICAL_STABILITY",
            "description": (
                "Degenerate and near-degenerate input cases must be explicitly covered "
                "in the fixture plan; NOT_COMPUTABLE paths must be documented."
            ),
            "evidence_refs": [
                "contracts/canon/wasserstein_distance_implementation_readiness_dossier.v1.schema.json",
            ],
        },
        {
            "strategy_id": "val_004_floating_point_drift",
            "validation_type": "FLOATING_POINT_DRIFT",
            "description": (
                "Float64 precision requirement must be verified across target CPU architectures "
                "before implementation begins; float32 is explicitly excluded."
            ),
            "evidence_refs": [
                "MetricOperatorRegistry.v1:metric_operator_registry_001",
            ],
        },
        {
            "strategy_id": "val_005_edge_case_validation",
            "validation_type": "EDGE_CASE_VALIDATION",
            "description": (
                "Empty distribution, single-point distribution, and equal-distribution inputs "
                "must produce documented expected outputs in the test vector schema plan."
            ),
            "evidence_refs": [
                "MetricComputationPreflight.v1:metric_computation_preflight_001",
            ],
        },
    ],
    "implementation_prerequisites": [
        {
            "prerequisite_id": "prereq_001_selection_plan",
            "status": "REQUIRED",
            "description": (
                "MetricOperatorImplementationSelectionPlan.v1 must be present and sealed "
                "with WASSERSTEIN at rank 1, readiness_status READY_FOR_IMPLEMENTATION_PLAN."
            ),
            "evidence_refs": [
                "MetricOperatorImplementationSelectionPlan.v1:metric_operator_implementation_selection_plan_001",
            ],
        },
        {
            "prerequisite_id": "prereq_002_preflight",
            "status": "REQUIRED",
            "description": (
                "MetricComputationPreflight.v1 must be present with "
                "metric_computation_authorized: true and emits_metric_values: false."
            ),
            "evidence_refs": [
                "MetricComputationPreflight.v1:metric_computation_preflight_001",
            ],
        },
        {
            "prerequisite_id": "prereq_003_registry",
            "status": "REQUIRED",
            "description": (
                "MetricOperatorRegistry.v1 must be present with WASSERSTEIN "
                "registered as ADVISORY_ONLY and NOT_IMPLEMENTED."
            ),
            "evidence_refs": [
                "MetricOperatorRegistry.v1:metric_operator_registry_001",
            ],
        },
        {
            "prerequisite_id": "prereq_004_baseline_vectors",
            "status": "REQUIRED",
            "description": (
                "MetricOperatorBaselineTestVectorPack.v1 must be present with at least "
                "one VALID_METADATA_VECTOR for WASSERSTEIN."
            ),
            "evidence_refs": [
                "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            ],
        },
        {
            "prerequisite_id": "prereq_005_ground_metric",
            "status": "DEFERRED",
            "description": (
                "Ground metric (cost function) for Wasserstein on AAL-Viz geometric surface "
                "descriptors must be specified before fixture creation; deferred to test vector schema plan."
            ),
            "evidence_refs": [],
        },
        {
            "prerequisite_id": "prereq_006_input_shape",
            "status": "DEFERRED",
            "description": (
                "Wasserstein input shape (distribution pair type and dimensionality) must be "
                "confirmed from geometric surface descriptor analysis; "
                "deferred to test vector schema plan."
            ),
            "evidence_refs": [],
        },
    ],
    "dependency_inventory": [
        {
            "dependency_id": "dep_001_test_vector_pack",
            "dependency_type": "TEST_VECTOR",
            "description": (
                "Wasserstein baseline test vector from the metric operator baseline test vector pack; "
                "currently VALID_METADATA_VECTOR and NOT_IMPLEMENTED."
            ),
            "required": True,
            "evidence_refs": [
                "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            ],
        },
        {
            "dependency_id": "dep_002_ot_numerical_library",
            "dependency_type": "NUMERICAL_LIBRARY",
            "description": (
                "Discrete optimal transport solver library (e.g. scipy.optimize.linprog or POT); "
                "version must be pinned for determinism; not yet selected."
            ),
            "required": False,
            "evidence_refs": [],
        },
        {
            "dependency_id": "dep_003_data_layout",
            "dependency_type": "DATA_LAYOUT",
            "description": (
                "Distribution pair data layout: weights array and support array per distribution; "
                "layout must be frozen before fixture creation."
            ),
            "required": True,
            "evidence_refs": [],
        },
        {
            "dependency_id": "dep_004_geometric_abstraction",
            "dependency_type": "GEOMETRIC_ABSTRACTION",
            "description": (
                "Geometric surface descriptor abstraction layer: mapping from AAL-Viz renderer outputs "
                "(SVG/Canvas/WebGL) to Wasserstein input distributions; not yet defined."
            ),
            "required": True,
            "evidence_refs": [
                "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
            ],
        },
        {
            "dependency_id": "dep_005_memory_layout",
            "dependency_type": "MEMORY_LAYOUT",
            "description": (
                "Memory layout for cost matrix storage; "
                "must be contiguous float64 array for OT solver compatibility."
            ),
            "required": False,
            "evidence_refs": [],
        },
        {
            "dependency_id": "dep_006_future_acceleration",
            "dependency_type": "FUTURE_ACCELERATION",
            "description": (
                "GPU-accelerated OT (e.g. cuOT or JAX-based) is a future candidate; "
                "not required for planning stage."
            ),
            "required": False,
            "evidence_refs": [],
        },
    ],
    "numerical_constraints": [
        "No floating-point Wasserstein kernel execution in this planning lane.",
        "Hash and serialization determinism required across all dossier fields.",
        "Float64 precision required for any future implementation; float32 is excluded.",
        "OT solver version must be pinned before fixture creation.",
    ],
    "implementation_risks": [
        {
            "risk_id": "risk_001_dimensionality",
            "risk_level": "MEDIUM",
            "description": (
                "Geometric surface descriptor dimensionality is unspecified; "
                "higher-dimensional inputs require OT or approximation algorithms "
                "with non-trivial determinism constraints."
            ),
            "mitigation": (
                "Defer dimensionality decision to test vector schema plan; "
                "begin with 1D reference implementation only."
            ),
            "evidence_refs": [
                "MetricOperatorImplementationSelectionPlan.v1:metric_operator_implementation_selection_plan_001",
            ],
        },
        {
            "risk_id": "risk_002_solver_nondeterminism",
            "risk_level": "MEDIUM",
            "description": (
                "OT solver non-determinism across CPU architectures or library versions "
                "could break hash stability and fixture reproducibility."
            ),
            "mitigation": (
                "Pin solver library version; characterise non-determinism before fixture creation; "
                "require deterministic replay test in fixture plan."
            ),
            "evidence_refs": [],
        },
        {
            "risk_id": "risk_003_sinkhorn_precision",
            "risk_level": "MEDIUM",
            "description": (
                "Sinkhorn regularisation introduces tolerance-dependent numerical error; "
                "epsilon variation breaks byte-identical reproducibility."
            ),
            "mitigation": (
                "Freeze epsilon and max_iterations parameters; "
                "use log-domain stabilisation; "
                "prefer exact OT for 1D case to avoid approximation entirely."
            ),
            "evidence_refs": [],
        },
        {
            "risk_id": "risk_004_degenerate_inputs",
            "risk_level": "LOW",
            "description": (
                "Degenerate inputs (empty distributions, zero-weight entries, "
                "single-point distributions) may produce undefined or infinite distances."
            ),
            "mitigation": (
                "Define explicit NOT_COMPUTABLE guard paths in the fixture plan; "
                "add degenerate-input test vectors."
            ),
            "evidence_refs": [
                "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            ],
        },
        {
            "risk_id": "risk_005_planning_drift",
            "risk_level": "LOW",
            "description": (
                "Future implementation could diverge from planning constraints "
                "if advisory locks are not enforced fail-closed."
            ),
            "mitigation": (
                "Keep all advisory lock checks fail-closed in schema and module; "
                "validate governance flags and authority locks on every build."
            ),
            "evidence_refs": [
                "contracts/canon/wasserstein_distance_implementation_readiness_dossier.v1.schema.json",
            ],
        },
    ],
    "blocked_scopes": [
        "canon_promotion",
        "emits_metric_values",
        "execution_authority",
        "forecast_influence",
        "inference_authority",
        "p43_surface_lanes",
        "production_activation",
        "runtime_mutation",
        "wasserstein_computation",
    ],
    "authority_locks": default_authority_locks(),
    "recommended_next_step": "WASSERSTEIN_TEST_VECTOR_SCHEMA_PLAN",
    "output_contract": default_output_contract(),
    "governance_flags": default_governance_flags(),
    "provenance": {
        "source": "P44_WASSERSTEIN_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER",
        "evidence_refs": [
            "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
            "MetricComputationPreflight.v1:metric_computation_preflight_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "MetricOperatorImplementationSelectionPlan.v1:metric_operator_implementation_selection_plan_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_computation_preflight.v1.schema.json",
            "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
            "contracts/canon/metric_operator_implementation_selection_plan.v1.schema.json",
            "contracts/canon/metric_operator_registry.v1.schema.json",
            "contracts/canon/wasserstein_distance_implementation_readiness_dossier.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_distance_implementation_readiness_dossier",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_distance_implementation_readiness_dossier_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_wasserstein_distance_implementation_readiness_dossier(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_distance_implementation_readiness_dossier(packet),
        encoding="utf-8",
    )

    log_event(
        logger,
        "INFO",
        "wasserstein_distance_implementation_readiness_dossier_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"dossier_id={packet['dossier_id']}")
    print(f"dossier_status={packet['dossier_status']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
