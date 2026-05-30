from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportCpuBaselineImplementationPlan.v1"
PLAN_TYPE = "TRANSPORT_CPU_BASELINE_IMPLEMENTATION_PLAN"
OPERATOR_ID = "TRANSPORT"
ALLOWED_IMPLEMENTATION_MODE = (
    "CPU_REFERENCE_PLAN",
    "PURE_PYTHON_PLAN",
    "SIMD_CANDIDATE_PLAN",
    "FUTURE_GPU_CANDIDATE_PLAN",
    "NOT_COMPUTABLE_PLAN",
)
ALLOWED_INTENDED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_TOPOLOGY_STAGE = (
    "BASELINE_PLAN_ONLY",
    "ALGORITHM_TOPOLOGY_ONLY",
    "DATA_LAYOUT_ONLY",
    "BLOCKED_PENDING_OPERATOR_REVIEW",
)
ALLOWED_STEP_TYPE = (
    "INPUT_VALIDATION_STEP",
    "BALANCE_CHECK_TOPOLOGY_STEP",
    "COST_MATRIX_VALIDATION_TOPOLOGY_STEP",
    "DEGENERATE_PATH_TOPOLOGY_STEP",
    "LP_TOPOLOGY_DECLARATION_STEP",
    "NOT_COMPUTABLE_BRANCH_STEP",
    "BASELINE_COMPARATOR_STEP",
)
ALLOWED_IMPLEMENTATION_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
ALLOWED_STABILITY_TYPE = (
    "FLOAT_PRECISION_POLICY",
    "BALANCE_TOLERANCE_POLICY",
    "COST_MATRIX_POLICY",
    "NON_FINITE_VALUE_POLICY",
    "LP_SOLVER_POLICY",
    "NOT_COMPUTABLE_POLICY",
)
ALLOWED_RISK_LEVEL = ("LOW", "MEDIUM", "HIGH", "NOT_COMPUTABLE")
LOCKED_FALSE_FLAGS = (
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "runtime_authority",
    "runtime_mutation",
    "forecast_influence",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "activation_approved",
    "authorization_granted",
)
FORBIDDEN = (
    "executable",
    "callable",
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-computation",
    "metric-value",
    "geodesic-distance",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class TransportCpuBaselineImplementationPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_algorithm_plan() -> list[dict[str, Any]]:
    return [
        {
            "step_id": "step-001",
            "step_type": "INPUT_VALIDATION_STEP",
            "description": (
                "Validate supply vector, demand vector, and cost_matrix inputs "
                "against declared contract: supply and demand must be non-empty "
                "non-negative finite float64 sequences; cost_matrix must have "
                "shape (len(supply), len(demand)) with non-negative finite float64 "
                "entries. No transport distance computation performed at this step."
            ),
            "planned_inputs": ["supply", "demand", "cost_matrix"],
            "planned_outputs": ["validated_input_metadata"],
            "blocked_operations": ["lp_solver_invocation", "transport_distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-002",
            "step_type": "BALANCE_CHECK_TOPOLOGY_STEP",
            "description": (
                "Define balance check topology: compute sum(supply) and sum(demand) "
                "in canonical left-to-right order using float64 accumulation. "
                "Verify |sum(supply) - sum(demand)| <= declared relative balance "
                "tolerance (e.g., 1e-9 * max(sum(supply), sum(demand))). Unbalanced "
                "inputs must route to NOT_COMPUTABLE. No LP invoked at this step."
            ),
            "planned_inputs": ["validated_input_metadata"],
            "planned_outputs": ["balance_check_topology_declaration"],
            "blocked_operations": ["lp_solver_invocation", "transport_distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-003",
            "step_type": "COST_MATRIX_VALIDATION_TOPOLOGY_STEP",
            "description": (
                "Define cost matrix validation topology: verify cost_matrix shape "
                "is exactly (m, n) where m = len(supply) and n = len(demand); "
                "verify all cost values are non-negative finite float64. Shape "
                "mismatch or invalid cost values must route to NOT_COMPUTABLE. "
                "Cost matrix is stored row-major in canonical JSON array-of-arrays "
                "format. No LP invoked at this step."
            ),
            "planned_inputs": ["balance_check_topology_declaration"],
            "planned_outputs": ["cost_matrix_validation_declaration"],
            "blocked_operations": ["lp_solver_invocation", "transport_distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-004",
            "step_type": "DEGENERATE_PATH_TOPOLOGY_STEP",
            "description": (
                "Define closed-form degenerate path topology for cases requiring "
                "no LP: for m=1 (single source), the transport distance equals "
                "sum_j cost_matrix[0][j] * demand[j] in left-to-right order; "
                "for n=1 (single target), the transport distance equals "
                "sum_i cost_matrix[i][0] * supply[i] in left-to-right order; "
                "for the 1×1 case (m=1, n=1), the transport distance equals "
                "cost_matrix[0][0] * supply[0]. These paths are closed-form "
                "float64 weighted sums; no LP solver is involved."
            ),
            "planned_inputs": ["cost_matrix_validation_declaration"],
            "planned_outputs": ["degenerate_path_topology_declaration"],
            "blocked_operations": ["lp_solver_invocation", "transport_distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-005",
            "step_type": "LP_TOPOLOGY_DECLARATION_STEP",
            "description": (
                "Define general m×n LP topology for non-degenerate balanced "
                "transport: the LP has m*n non-negative decision variables T[i,j]; "
                "m row marginal constraints (T @ 1_n = supply); n column marginal "
                "constraints (T^T @ 1_m = demand); objective is minimize "
                "sum_{i,j} cost_matrix[i,j] * T[i,j]. LP solver variant, pivot "
                "rule, and tie-breaking strategy are declared as planned-only; "
                "no LP solver is invoked at this step or in this bundle."
            ),
            "planned_inputs": ["degenerate_path_topology_declaration"],
            "planned_outputs": ["lp_topology_declaration"],
            "blocked_operations": ["lp_solver_invocation", "transport_distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-006",
            "step_type": "NOT_COMPUTABLE_BRANCH_STEP",
            "description": (
                "Define all NOT_COMPUTABLE detection branches: empty supply (m=0) "
                "or demand (n=0); unbalanced transport (|sum(supply)-sum(demand)| "
                "exceeds tolerance); negative supply or demand element; negative "
                "cost element; non-finite value in supply, demand, or cost_matrix; "
                "cost_matrix shape mismatch. Each condition must route to a "
                "documented NOT_COMPUTABLE state without emitting a transport "
                "distance value."
            ),
            "planned_inputs": ["validated_input_metadata"],
            "planned_outputs": ["not_computable_state_declaration"],
            "blocked_operations": ["lp_solver_invocation", "transport_distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-007",
            "step_type": "BASELINE_COMPARATOR_STEP",
            "description": (
                "Define baseline comparator topology: compare future computed "
                "transport distance against expected_transport_distance fields "
                "in valid fixture records. For degenerate closed-form cases "
                "(m=1, n=1, 1×1), tolerance is zero for exact float64 "
                "weighted-sum results. For general LP cases, the declared "
                "balance tolerance also governs the comparison policy. "
                "No computation or comparison executed at this step."
            ),
            "planned_inputs": [
                "degenerate_path_topology_declaration",
                "expected_fixture_values",
                "lp_topology_declaration",
            ],
            "planned_outputs": ["baseline_comparator_topology_declaration"],
            "blocked_operations": [
                "comparator_execution",
                "lp_solver_invocation",
                "transport_distance_emission",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_numerical_stability_plan() -> list[dict[str, Any]]:
    return [
        {
            "stability_id": "stability-001",
            "stability_type": "FLOAT_PRECISION_POLICY",
            "description": (
                "Float64 required for all supply/demand accumulation, cost "
                "accumulation, LP dual variable computation, and comparator "
                "arithmetic. Float32 excluded per readiness dossier numerical "
                "constraints."
            ),
            "risk_level": "MEDIUM",
            "planned_guardrail": (
                "Require float64 precision declaration; reject float32 inputs "
                "at validation boundary."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "stability_id": "stability-002",
            "stability_type": "BALANCE_TOLERANCE_POLICY",
            "description": (
                "Supply-demand balance check uses a relative tolerance declared "
                "as epsilon_rel = 1e-9 * max(sum(supply), sum(demand)). This "
                "value is fixed before implementation. Float64 drift in summation "
                "of non-trivial supply/demand vectors may produce apparent "
                "imbalance; the tolerance prevents spurious NOT_COMPUTABLE."
            ),
            "risk_level": "MEDIUM",
            "planned_guardrail": (
                "Declare balance tolerance = 1e-9 relative to the larger total; "
                "test fixtures must include a near-tolerance boundary case."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "stability_id": "stability-003",
            "stability_type": "COST_MATRIX_POLICY",
            "description": (
                "Cost matrix is stored row-major as a JSON array-of-arrays of "
                "float64 values. Zero cost values are valid and must not trigger "
                "division-by-zero in any comparator. Very large cost values may "
                "cause float64 overflow in objective accumulation; declared input "
                "magnitude bound required before implementation."
            ),
            "risk_level": "LOW",
            "planned_guardrail": (
                "Declare maximum allowed cost value and maximum m*n problem size "
                "in the implementation plan; add NOT_COMPUTABLE branch for "
                "oversized inputs or cost overflow."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "stability_id": "stability-004",
            "stability_type": "NON_FINITE_VALUE_POLICY",
            "description": (
                "Non-finite float64 values (NaN or infinite) in supply, demand, "
                "or cost_matrix must be detected at input validation and produce "
                "NOT_COMPUTABLE without any transport distance computation. "
                "NaN propagation through cost accumulation is explicitly excluded."
            ),
            "risk_level": "HIGH",
            "planned_guardrail": (
                "Scan for non-finite values at input validation; route to "
                "not-computable state before any accumulation or LP declaration."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "stability_id": "stability-005",
            "stability_type": "LP_SOLVER_POLICY",
            "description": (
                "The LP solver variant (e.g., simplex with fixed pivot rule), "
                "tie-breaking strategy for degenerate problems (multiple optimal "
                "transport plans), and iteration limit must be declared and fixed "
                "before any implementation PR may be opened. Stochastic LP "
                "variants and randomized pivot rules are excluded. LP solver "
                "is not invoked in this planning bundle."
            ),
            "risk_level": "MEDIUM",
            "planned_guardrail": (
                "Declare solver variant, pivot rule, and tie-breaking rule in "
                "the implementation plan before implementation begins; restrict "
                "initial test fixtures to problems with unique optimal plans."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "stability_id": "stability-006",
            "stability_type": "NOT_COMPUTABLE_POLICY",
            "description": (
                "Define all conditions under which NOT_COMPUTABLE is the correct "
                "output: empty supply or demand, unbalanced transport, negative "
                "supply/demand/cost element, non-finite value, cost_matrix shape "
                "mismatch. Ensure no silent fallback to a numeric transport "
                "distance value."
            ),
            "risk_level": "NOT_COMPUTABLE",
            "planned_guardrail": (
                "Enumerate all NOT_COMPUTABLE branches in algorithm topology "
                "before implementation; validate each branch has a dedicated "
                "test fixture planned."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_input_data_contract() -> dict[str, bool]:
    return {
        "supply_required": True,
        "demand_required": True,
        "cost_matrix_required": True,
        "balance_tolerance_policy_declared": True,
        "non_negative_policy_declared": True,
        "non_finite_policy_declared": True,
        "empty_supply_policy_declared": True,
        "cost_matrix_shape_policy_declared": True,
        "runtime_binding_enabled": False,
    }


def default_output_data_contract() -> dict[str, bool]:
    return {
        "emits_transport_distance_value": False,
        "emits_alignment_metadata": True,
        "emits_not_computable_state": True,
        "emits_error_metadata": True,
        "runtime_output_binding_enabled": False,
    }


def default_memory_layout_plan() -> dict[str, bool]:
    return {
        "layout_declared": True,
        "supply_representation_declared": True,
        "demand_representation_declared": True,
        "cost_matrix_representation_declared": True,
        "allocation_strategy_declared": True,
        "streaming_mode_enabled": False,
        "gpu_memory_enabled": False,
        "runtime_buffer_binding_enabled": False,
    }


def default_benchmark_plan() -> dict[str, bool]:
    return {
        "benchmark_declared": True,
        "fixture_scale_classes_declared": True,
        "deterministic_replay_required": True,
        "performance_thresholds_declared": False,
        "benchmark_execution_enabled": False,
    }


def default_future_acceleration_seams() -> dict[str, bool]:
    return {
        "simd_candidate_declared": False,
        "gpu_candidate_declared": False,
        "approximation_candidate_declared": True,
        "acceleration_implemented": False,
        "acceleration_runtime_enabled": False,
    }


def default_implementation_constraints() -> dict[str, bool]:
    return {
        "transport_computation_added": False,
        "lp_solver_invoked": False,
        "transport_distance_values_emitted": False,
        "scoring_added": False,
        "runtime_binding_added": False,
        "oracle_integration_added": False,
        "yggdrasil_integration_added": False,
        "aal_viz_runtime_integration_added": False,
        "forecast_influence_added": False,
        "scheduler_integration_added": False,
        "renderer_integration_added": False,
    }


def default_validation_plan() -> dict[str, bool]:
    return {
        "requires_algorithm_topology_tests": True,
        "requires_input_contract_tests": True,
        "requires_output_contract_tests": True,
        "requires_not_computable_tests": True,
        "requires_numerical_guardrail_tests": True,
        "requires_no_transport_distance_value_scan": True,
        "requires_no_authority_scan": True,
        "requires_no_runtime_mutation_scan": True,
        "requires_no_lp_solver_invocation_scan": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_metric_code": False,
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_baseline_plan": True,
        "emits_algorithm_topology": True,
        "emits_validation_requirements": True,
    }


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportCpuBaselineImplementationPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_transport_cpu_baseline_implementation_plan(
    packet: dict[str, Any],
) -> None:
    req = {
        "schema_version", "plan_id", "plan_type", "operator_id",
        "source_readiness_dossier_refs", "source_metric_registry_refs",
        "source_test_vector_pack_refs", "implementation_topology",
        "input_data_contract", "output_data_contract", "algorithm_plan",
        "numerical_stability_plan", "memory_layout_plan", "benchmark_plan",
        "future_acceleration_seams", "implementation_constraints",
        "validation_plan", "output_contract", "governance_flags",
        "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise TransportCpuBaselineImplementationPlanValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise TransportCpuBaselineImplementationPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise TransportCpuBaselineImplementationPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise TransportCpuBaselineImplementationPlanValidationError("unknown_operator_id")

    topo = packet["implementation_topology"]
    if topo.get("implementation_mode") not in ALLOWED_IMPLEMENTATION_MODE:
        raise TransportCpuBaselineImplementationPlanValidationError("unknown_implementation_mode")
    if topo.get("intended_lane") not in ALLOWED_INTENDED_LANE:
        raise TransportCpuBaselineImplementationPlanValidationError("unknown_intended_lane")
    if topo.get("topology_stage") not in ALLOWED_TOPOLOGY_STAGE:
        raise TransportCpuBaselineImplementationPlanValidationError("unknown_topology_stage")

    if packet["input_data_contract"] != default_input_data_contract():
        raise TransportCpuBaselineImplementationPlanValidationError("invalid_input_data_contract")
    if packet["output_data_contract"] != default_output_data_contract():
        raise TransportCpuBaselineImplementationPlanValidationError("invalid_output_data_contract")
    if packet["memory_layout_plan"] != default_memory_layout_plan():
        raise TransportCpuBaselineImplementationPlanValidationError("invalid_memory_layout_plan")
    if packet["benchmark_plan"] != default_benchmark_plan():
        raise TransportCpuBaselineImplementationPlanValidationError("invalid_benchmark_plan")
    if packet["future_acceleration_seams"] != default_future_acceleration_seams():
        raise TransportCpuBaselineImplementationPlanValidationError(
            "invalid_future_acceleration_seams"
        )
    if packet["implementation_constraints"] != default_implementation_constraints():
        raise TransportCpuBaselineImplementationPlanValidationError(
            "invalid_implementation_constraints"
        )
    if packet["validation_plan"] != default_validation_plan():
        raise TransportCpuBaselineImplementationPlanValidationError("invalid_validation_plan")
    if packet["output_contract"] != default_output_contract():
        raise TransportCpuBaselineImplementationPlanValidationError("invalid_output_contract")

    algorithm_plan = packet["algorithm_plan"]
    numerical_plan = packet["numerical_stability_plan"]
    if not algorithm_plan:
        raise TransportCpuBaselineImplementationPlanValidationError(
            "algorithm_plan_must_be_non_empty"
        )
    if not numerical_plan:
        raise TransportCpuBaselineImplementationPlanValidationError(
            "numerical_stability_plan_must_be_non_empty"
        )

    seen_step_ids: set[str] = set()
    for step in algorithm_plan:
        step_id = step.get("step_id")
        if step_id in seen_step_ids:
            raise TransportCpuBaselineImplementationPlanValidationError("duplicate_step_id")
        seen_step_ids.add(step_id)
        if step.get("step_type") not in ALLOWED_STEP_TYPE:
            raise TransportCpuBaselineImplementationPlanValidationError("unknown_step_type")
        if step.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
            raise TransportCpuBaselineImplementationPlanValidationError(
                "unknown_implementation_status"
            )

    seen_stability_ids: set[str] = set()
    for stability in numerical_plan:
        stability_id = stability.get("stability_id")
        if stability_id in seen_stability_ids:
            raise TransportCpuBaselineImplementationPlanValidationError("duplicate_stability_id")
        seen_stability_ids.add(stability_id)
        if stability.get("stability_type") not in ALLOWED_STABILITY_TYPE:
            raise TransportCpuBaselineImplementationPlanValidationError("unknown_stability_type")
        if stability.get("risk_level") not in ALLOWED_RISK_LEVEL:
            raise TransportCpuBaselineImplementationPlanValidationError("unknown_risk_level")
        if stability.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
            raise TransportCpuBaselineImplementationPlanValidationError(
                "unknown_implementation_status"
            )

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise TransportCpuBaselineImplementationPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_transport_cpu_baseline_implementation_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_transport_cpu_baseline_implementation_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_transport_cpu_baseline_implementation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    algorithm_plan = sorted(
        payload.get("algorithm_plan", default_algorithm_plan()),
        key=lambda x: x["step_id"],
    )
    numerical_plan = sorted(
        payload.get("numerical_stability_plan", default_numerical_stability_plan()),
        key=lambda x: x["stability_id"],
    )
    for step in algorithm_plan:
        step["planned_inputs"] = sorted(step.get("planned_inputs", []))
        step["planned_outputs"] = sorted(step.get("planned_outputs", []))
        step["blocked_operations"] = sorted(step.get("blocked_operations", []))

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_readiness_dossier_refs": sorted(
            payload.get("source_readiness_dossier_refs", [])
        ),
        "source_metric_registry_refs": sorted(
            payload.get("source_metric_registry_refs", [])
        ),
        "source_test_vector_pack_refs": sorted(
            payload.get("source_test_vector_pack_refs", [])
        ),
        "algorithm_plan": algorithm_plan,
        "numerical_stability_plan": numerical_plan,
        "input_data_contract": payload.get("input_data_contract", default_input_data_contract()),
        "output_data_contract": payload.get(
            "output_data_contract", default_output_data_contract()
        ),
        "memory_layout_plan": payload.get("memory_layout_plan", default_memory_layout_plan()),
        "benchmark_plan": payload.get("benchmark_plan", default_benchmark_plan()),
        "future_acceleration_seams": payload.get(
            "future_acceleration_seams", default_future_acceleration_seams()
        ),
        "implementation_constraints": payload.get(
            "implementation_constraints", default_implementation_constraints()
        ),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_transport_cpu_baseline_implementation_plan_hash(base)
    validate_transport_cpu_baseline_implementation_plan(base)
    return _finalize(base)
