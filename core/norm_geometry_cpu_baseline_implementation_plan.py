from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryCpuBaselineImplementationPlan.v1"
PLAN_TYPE = "NORM_GEOMETRY_CPU_BASELINE_IMPLEMENTATION_PLAN"
OPERATOR_ID = "NORM_GEOMETRY"
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
    "VECTOR_DIFFERENCE_TOPOLOGY_STEP",
    "ABSOLUTE_VALUE_TOPOLOGY_STEP",
    "POWER_TOPOLOGY_STEP",
    "SUMMATION_TOPOLOGY_STEP",
    "ROOT_TOPOLOGY_STEP",
    "NOT_COMPUTABLE_BRANCH_STEP",
    "BASELINE_COMPARATOR_STEP",
)
ALLOWED_IMPLEMENTATION_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
ALLOWED_STABILITY_TYPE = (
    "FLOAT_PRECISION_POLICY",
    "EMPTY_VECTOR_POLICY",
    "P_PARAMETER_POLICY",
    "NON_FINITE_ELEMENT_POLICY",
    "OVERFLOW_POLICY",
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


class NormGeometryCpuBaselineImplementationPlanValidationError(ValueError):
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
                "Validate vector_x, vector_y, and p_parameter inputs against "
                "declared contract: equal length required, p >= 1.0, both vectors "
                "non-empty, all elements must be finite float64. No Lp norm "
                "computation performed at this step."
            ),
            "planned_inputs": ["vector_x", "vector_y", "p_parameter"],
            "planned_outputs": ["validated_input_metadata"],
            "blocked_operations": ["lp_norm_computation", "distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-002",
            "step_type": "VECTOR_DIFFERENCE_TOPOLOGY_STEP",
            "description": (
                "Define element-wise difference topology: for each index i, "
                "compute x_i - y_i in left-to-right order (index 0 to n-1). "
                "Traversal order is canonical and must be fixed before "
                "implementation. No kernel executed at this step."
            ),
            "planned_inputs": ["validated_input_metadata"],
            "planned_outputs": ["difference_topology_declaration"],
            "blocked_operations": ["lp_norm_computation", "distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-003",
            "step_type": "ABSOLUTE_VALUE_TOPOLOGY_STEP",
            "description": (
                "Define absolute value topology: apply |x_i - y_i| to each "
                "element-wise difference in the same left-to-right order. "
                "For p=inf, the maximum of absolute values is the final result "
                "and the power and summation steps are bypassed. No kernel executed."
            ),
            "planned_inputs": ["difference_topology_declaration"],
            "planned_outputs": ["absolute_difference_topology_declaration"],
            "blocked_operations": ["lp_norm_computation", "distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-004",
            "step_type": "POWER_TOPOLOGY_STEP",
            "description": (
                "Define power topology: for finite p >= 1, compute |x_i - y_i|^p "
                "for each element using float64 power operation. Overflow must "
                "route to NOT_COMPUTABLE. For p=inf this step is skipped. "
                "No kernel executed."
            ),
            "planned_inputs": ["absolute_difference_topology_declaration"],
            "planned_outputs": ["power_topology_declaration"],
            "blocked_operations": ["lp_norm_computation", "distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-005",
            "step_type": "SUMMATION_TOPOLOGY_STEP",
            "description": (
                "Define summation topology: accumulate sum_i |x_i - y_i|^p "
                "in canonical left-to-right order using float64 accumulation. "
                "For p=inf this step is replaced by max aggregation. "
                "No kernel executed."
            ),
            "planned_inputs": ["power_topology_declaration"],
            "planned_outputs": ["summation_topology_declaration"],
            "blocked_operations": ["lp_norm_computation", "distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-006",
            "step_type": "ROOT_TOPOLOGY_STEP",
            "description": (
                "Define root extraction topology: compute "
                "(sum_i |x_i - y_i|^p)^(1/p) via float64 power operation. "
                "For p=1 no root is required (sum is the result). "
                "For p=2 use float64 square root. For p=inf the max from "
                "step-005 is the result. No kernel executed."
            ),
            "planned_inputs": ["summation_topology_declaration"],
            "planned_outputs": ["distance_topology_declaration"],
            "blocked_operations": ["lp_norm_computation", "distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-007",
            "step_type": "NOT_COMPUTABLE_BRANCH_STEP",
            "description": (
                "Define not-computable detection branches: empty vector (n=0), "
                "p < 1.0, mismatched vector lengths, non-finite element values "
                "(NaN or infinite), and power overflow must all route to a "
                "documented NOT_COMPUTABLE state without emitting a distance value."
            ),
            "planned_inputs": ["validated_input_metadata"],
            "planned_outputs": ["not_computable_state_declaration"],
            "blocked_operations": ["lp_norm_computation", "distance_emission"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "step_id": "step-008",
            "step_type": "BASELINE_COMPARATOR_STEP",
            "description": (
                "Define baseline comparator topology: compare future computed "
                "Lp distance against expected_lp_distance fields in valid "
                "fixture records. Tolerance policy declared but not applied. "
                "No computation or comparison executed at this step."
            ),
            "planned_inputs": ["distance_topology_declaration", "expected_fixture_values"],
            "planned_outputs": ["baseline_comparator_topology_declaration"],
            "blocked_operations": ["lp_norm_computation", "comparator_execution"],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_numerical_stability_plan() -> list[dict[str, Any]]:
    return [
        {
            "stability_id": "stability-001",
            "stability_type": "FLOAT_PRECISION_POLICY",
            "description": (
                "Float64 required for all element-wise differences, power "
                "operations, summation accumulation, and root extraction. "
                "Float32 excluded per readiness dossier numerical constraints."
            ),
            "risk_level": "MEDIUM",
            "planned_guardrail": (
                "Require float64 precision declaration; reject float32 "
                "inputs at validation boundary."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "stability_id": "stability-002",
            "stability_type": "EMPTY_VECTOR_POLICY",
            "description": (
                "Empty vector inputs (n=0) must be detected at the input "
                "validation step and produce a documented NOT_COMPUTABLE path "
                "without any element-wise operation."
            ),
            "risk_level": "HIGH",
            "planned_guardrail": (
                "Route to not-computable state; no distance scalar emitted."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "stability_id": "stability-003",
            "stability_type": "P_PARAMETER_POLICY",
            "description": (
                "p < 1.0 is not a valid norm parameter and must be rejected "
                "at input validation. The p=inf sentinel convention must be "
                "declared and fixed before implementation to ensure deterministic "
                "branch selection."
            ),
            "risk_level": "MEDIUM",
            "planned_guardrail": (
                "p < 1.0 routes to NOT_COMPUTABLE; p=inf sentinel declared "
                "explicitly in data layout before implementation."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "stability_id": "stability-004",
            "stability_type": "NON_FINITE_ELEMENT_POLICY",
            "description": (
                "Non-finite float64 values (NaN or infinite) in either input "
                "vector must be detected before any element-wise operation and "
                "produce NOT_COMPUTABLE without propagating NaN through the "
                "power or summation steps."
            ),
            "risk_level": "HIGH",
            "planned_guardrail": (
                "Scan for non-finite values at input validation; route to "
                "not-computable state before any element-wise computation."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "stability_id": "stability-005",
            "stability_type": "OVERFLOW_POLICY",
            "description": (
                "For large p values or large element magnitudes, |x_i - y_i|^p "
                "may overflow float64. Acceptable input magnitude bound and "
                "maximum p value must be declared before implementation; "
                "overflow must route to NOT_COMPUTABLE."
            ),
            "risk_level": "LOW",
            "planned_guardrail": (
                "Declare maximum allowed element magnitude and maximum p value "
                "in the implementation plan; add NOT_COMPUTABLE branch for "
                "detected overflow."
            ),
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "stability_id": "stability-006",
            "stability_type": "NOT_COMPUTABLE_POLICY",
            "description": (
                "Define all conditions under which NOT_COMPUTABLE is the "
                "correct output: empty vector, p < 1, mismatched lengths, "
                "non-finite element, power overflow. Ensure no silent fallback "
                "to a numeric distance value."
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
        "vector_x_required": True,
        "vector_y_required": True,
        "p_parameter_required": True,
        "equal_length_policy_declared": True,
        "p_minimum_policy_declared": True,
        "non_finite_policy_declared": True,
        "empty_vector_policy_declared": True,
        "runtime_binding_enabled": False,
    }


def default_output_data_contract() -> dict[str, bool]:
    return {
        "emits_lp_distance_value": False,
        "emits_alignment_metadata": True,
        "emits_not_computable_state": True,
        "emits_error_metadata": True,
        "runtime_output_binding_enabled": False,
    }


def default_memory_layout_plan() -> dict[str, bool]:
    return {
        "layout_declared": True,
        "vector_representation_declared": True,
        "p_parameter_representation_declared": True,
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
        "simd_candidate_declared": True,
        "gpu_candidate_declared": False,
        "approximation_candidate_declared": False,
        "acceleration_implemented": False,
        "acceleration_runtime_enabled": False,
    }


def default_implementation_constraints() -> dict[str, bool]:
    return {
        "norm_geometry_computation_added": False,
        "lp_distance_values_emitted": False,
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
        "requires_no_lp_distance_value_scan": True,
        "requires_no_authority_scan": True,
        "requires_no_runtime_mutation_scan": True,
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
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_norm_geometry_cpu_baseline_implementation_plan(
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
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            "invalid_schema_version"
        )
    if packet["plan_type"] != PLAN_TYPE:
        raise NormGeometryCpuBaselineImplementationPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise NormGeometryCpuBaselineImplementationPlanValidationError("unknown_operator_id")

    topo = packet["implementation_topology"]
    if topo.get("implementation_mode") not in ALLOWED_IMPLEMENTATION_MODE:
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            "unknown_implementation_mode"
        )
    if topo.get("intended_lane") not in ALLOWED_INTENDED_LANE:
        raise NormGeometryCpuBaselineImplementationPlanValidationError("unknown_intended_lane")
    if topo.get("topology_stage") not in ALLOWED_TOPOLOGY_STAGE:
        raise NormGeometryCpuBaselineImplementationPlanValidationError("unknown_topology_stage")

    if packet["input_data_contract"] != default_input_data_contract():
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            "invalid_input_data_contract"
        )
    if packet["output_data_contract"] != default_output_data_contract():
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            "invalid_output_data_contract"
        )
    if packet["memory_layout_plan"] != default_memory_layout_plan():
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            "invalid_memory_layout_plan"
        )
    if packet["benchmark_plan"] != default_benchmark_plan():
        raise NormGeometryCpuBaselineImplementationPlanValidationError("invalid_benchmark_plan")
    if packet["future_acceleration_seams"] != default_future_acceleration_seams():
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            "invalid_future_acceleration_seams"
        )
    if packet["implementation_constraints"] != default_implementation_constraints():
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            "invalid_implementation_constraints"
        )
    if packet["validation_plan"] != default_validation_plan():
        raise NormGeometryCpuBaselineImplementationPlanValidationError("invalid_validation_plan")
    if packet["output_contract"] != default_output_contract():
        raise NormGeometryCpuBaselineImplementationPlanValidationError("invalid_output_contract")

    algorithm_plan = packet["algorithm_plan"]
    numerical_plan = packet["numerical_stability_plan"]
    if not algorithm_plan:
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            "algorithm_plan_must_be_non_empty"
        )
    if not numerical_plan:
        raise NormGeometryCpuBaselineImplementationPlanValidationError(
            "numerical_stability_plan_must_be_non_empty"
        )

    seen_step_ids: set[str] = set()
    for step in algorithm_plan:
        step_id = step.get("step_id")
        if step_id in seen_step_ids:
            raise NormGeometryCpuBaselineImplementationPlanValidationError("duplicate_step_id")
        seen_step_ids.add(step_id)
        if step.get("step_type") not in ALLOWED_STEP_TYPE:
            raise NormGeometryCpuBaselineImplementationPlanValidationError("unknown_step_type")
        if step.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
            raise NormGeometryCpuBaselineImplementationPlanValidationError(
                "unknown_implementation_status"
            )

    seen_stability_ids: set[str] = set()
    for stability in numerical_plan:
        stability_id = stability.get("stability_id")
        if stability_id in seen_stability_ids:
            raise NormGeometryCpuBaselineImplementationPlanValidationError(
                "duplicate_stability_id"
            )
        seen_stability_ids.add(stability_id)
        if stability.get("stability_type") not in ALLOWED_STABILITY_TYPE:
            raise NormGeometryCpuBaselineImplementationPlanValidationError(
                "unknown_stability_type"
            )
        if stability.get("risk_level") not in ALLOWED_RISK_LEVEL:
            raise NormGeometryCpuBaselineImplementationPlanValidationError("unknown_risk_level")
        if stability.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
            raise NormGeometryCpuBaselineImplementationPlanValidationError(
                "unknown_implementation_status"
            )

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise NormGeometryCpuBaselineImplementationPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_norm_geometry_cpu_baseline_implementation_plan_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_norm_geometry_cpu_baseline_implementation_plan(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_norm_geometry_cpu_baseline_implementation_plan(
    payload: dict[str, Any],
) -> dict[str, Any]:
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
        "input_data_contract": payload.get(
            "input_data_contract", default_input_data_contract()
        ),
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
    base["canonical_hash"] = compute_norm_geometry_cpu_baseline_implementation_plan_hash(base)
    validate_norm_geometry_cpu_baseline_implementation_plan(base)
    return _finalize(base)
