from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferBaselineImplementationPlan.v1"
PLAN_TYPE = "CHAMFER_BASELINE_IMPLEMENTATION_PLAN"
OPERATOR_ID = "CHAMFER_DISTANCE"
ALLOWED_IMPLEMENTATION_MODE = (
    "CPU_REFERENCE_PLAN",
    "PURE_PYTHON_PLAN",
    "NUMPY_CANDIDATE_PLAN",
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
    "PAIRWISE_DISTANCE_TOPOLOGY_STEP",
    "NEAREST_NEIGHBOR_TOPOLOGY_STEP",
    "BIDIRECTIONAL_AGGREGATION_TOPOLOGY_STEP",
    "NOT_COMPUTABLE_BRANCH_STEP",
    "ERROR_STATE_STEP",
    "BASELINE_COMPARATOR_STEP",
)
ALLOWED_IMPLEMENTATION_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
ALLOWED_STABILITY_TYPE = (
    "FLOAT_PRECISION_POLICY",
    "EMPTY_INPUT_POLICY",
    "DIMENSION_MISMATCH_POLICY",
    "LARGE_POINT_SET_POLICY",
    "DUPLICATE_POINT_POLICY",
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
    "chamfer-distance",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class ChamferBaselineImplementationPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_algorithm_plan() -> list[dict[str, Any]]:
    return [{"step_id": "step-001", "step_type": "INPUT_VALIDATION_STEP", "description": "Validate inputs and contract metadata only.", "planned_inputs": ["point_set_a", "point_set_b"], "planned_outputs": ["validated_input_metadata"], "blocked_operations": ["distance_computation"], "implementation_status": "PLANNED_ONLY"}]


def default_numerical_stability_plan() -> list[dict[str, Any]]:
    return [{"stability_id": "stability-001", "stability_type": "FLOAT_PRECISION_POLICY", "description": "Define precision policy without executing kernels.", "risk_level": "MEDIUM", "planned_guardrail": "Require deterministic tolerance policy docs.", "implementation_status": "PLANNED_ONLY"}]


def default_input_data_contract() -> dict[str, bool]:
    return {"point_set_a_required": True, "point_set_b_required": True, "coordinate_dimensions_declared": True, "coordinate_type_declared": True, "empty_input_policy_declared": True, "dimension_mismatch_policy_declared": True, "non_numeric_policy_declared": True, "runtime_binding_enabled": False}


def default_output_data_contract() -> dict[str, bool]:
    return {"emits_distance_value": False, "emits_directional_distance": False, "emits_alignment_metadata": True, "emits_not_computable_state": True, "emits_error_metadata": True, "runtime_output_binding_enabled": False}


def default_memory_layout_plan() -> dict[str, bool]:
    return {"layout_declared": True, "point_set_representation_declared": True, "dimensionality_handling_declared": True, "allocation_strategy_declared": True, "streaming_mode_enabled": False, "gpu_memory_enabled": False, "runtime_buffer_binding_enabled": False}


def default_benchmark_plan() -> dict[str, bool]:
    return {"benchmark_declared": True, "fixture_scale_classes_declared": True, "deterministic_replay_required": True, "performance_thresholds_declared": False, "benchmark_execution_enabled": False}


def default_future_acceleration_seams() -> dict[str, bool]:
    return {"simd_candidate_declared": True, "gpu_candidate_declared": True, "streaming_candidate_declared": True, "acceleration_implemented": False, "acceleration_runtime_enabled": False}


def default_implementation_constraints() -> dict[str, bool]:
    return {"chamfer_math_added": False, "metric_values_emitted": False, "scoring_added": False, "runtime_binding_added": False, "oracle_integration_added": False, "yggdrasil_integration_added": False, "aal_viz_runtime_integration_added": False, "forecast_influence_added": False, "scheduler_integration_added": False, "renderer_integration_added": False}


def default_validation_plan() -> dict[str, bool]:
    return {"requires_algorithm_topology_tests": True, "requires_input_contract_tests": True, "requires_output_contract_tests": True, "requires_not_computable_tests": True, "requires_numerical_guardrail_tests": True, "requires_no_metric_value_scan": True, "requires_no_authority_scan": True, "requires_no_runtime_mutation_scan": True}


def default_output_contract() -> dict[str, bool]:
    return {"emits_metric_code": False, "emits_metric_values": False, "emits_scores": False, "emits_forecast_inputs": False, "emits_runtime_controls": False, "emits_authority_tokens": False, "emits_baseline_plan": True, "emits_algorithm_topology": True, "emits_validation_requirements": True}


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ChamferBaselineImplementationPlanValidationError("forbidden_provenance_reference_detected")


def validate_chamfer_baseline_implementation_plan(packet: dict[str, Any]) -> None:
    req = {"schema_version", "plan_id", "plan_type", "operator_id", "source_readiness_dossier_refs", "source_metric_registry_refs", "source_test_vector_pack_refs", "implementation_topology", "input_data_contract", "output_data_contract", "algorithm_plan", "numerical_stability_plan", "memory_layout_plan", "benchmark_plan", "future_acceleration_seams", "implementation_constraints", "validation_plan", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash"}
    missing = sorted(req - packet.keys())
    if missing:
        raise ChamferBaselineImplementationPlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferBaselineImplementationPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise ChamferBaselineImplementationPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferBaselineImplementationPlanValidationError("unknown_operator_id")
    topo = packet["implementation_topology"]
    if topo.get("implementation_mode") not in ALLOWED_IMPLEMENTATION_MODE:
        raise ChamferBaselineImplementationPlanValidationError("unknown_implementation_mode")
    if topo.get("intended_lane") not in ALLOWED_INTENDED_LANE:
        raise ChamferBaselineImplementationPlanValidationError("unknown_intended_lane")
    if topo.get("topology_stage") not in ALLOWED_TOPOLOGY_STAGE:
        raise ChamferBaselineImplementationPlanValidationError("unknown_topology_stage")

    if packet["input_data_contract"] != default_input_data_contract():
        raise ChamferBaselineImplementationPlanValidationError("invalid_input_data_contract")
    if packet["output_data_contract"] != default_output_data_contract():
        raise ChamferBaselineImplementationPlanValidationError("invalid_output_data_contract")
    if packet["memory_layout_plan"] != default_memory_layout_plan():
        raise ChamferBaselineImplementationPlanValidationError("invalid_memory_layout_plan")
    if packet["benchmark_plan"] != default_benchmark_plan():
        raise ChamferBaselineImplementationPlanValidationError("invalid_benchmark_plan")
    if packet["future_acceleration_seams"] != default_future_acceleration_seams():
        raise ChamferBaselineImplementationPlanValidationError("invalid_future_acceleration_seams")
    if packet["implementation_constraints"] != default_implementation_constraints():
        raise ChamferBaselineImplementationPlanValidationError("invalid_implementation_constraints")
    if packet["validation_plan"] != default_validation_plan():
        raise ChamferBaselineImplementationPlanValidationError("invalid_validation_plan")
    if packet["output_contract"] != default_output_contract():
        raise ChamferBaselineImplementationPlanValidationError("invalid_output_contract")

    algorithm_plan = packet["algorithm_plan"]
    numerical_plan = packet["numerical_stability_plan"]
    if not algorithm_plan:
        raise ChamferBaselineImplementationPlanValidationError("algorithm_plan_must_be_non_empty")
    if not numerical_plan:
        raise ChamferBaselineImplementationPlanValidationError("numerical_stability_plan_must_be_non_empty")

    seen_step_ids: set[str] = set()
    for step in algorithm_plan:
        step_id = step.get("step_id")
        if step_id in seen_step_ids:
            raise ChamferBaselineImplementationPlanValidationError("duplicate_step_id")
        seen_step_ids.add(step_id)
        if step.get("step_type") not in ALLOWED_STEP_TYPE:
            raise ChamferBaselineImplementationPlanValidationError("unknown_step_type")
        if step.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
            raise ChamferBaselineImplementationPlanValidationError("unknown_implementation_status")

    seen_stability_ids: set[str] = set()
    for stability in numerical_plan:
        stability_id = stability.get("stability_id")
        if stability_id in seen_stability_ids:
            raise ChamferBaselineImplementationPlanValidationError("duplicate_stability_id")
        seen_stability_ids.add(stability_id)
        if stability.get("stability_type") not in ALLOWED_STABILITY_TYPE:
            raise ChamferBaselineImplementationPlanValidationError("unknown_stability_type")
        if stability.get("risk_level") not in ALLOWED_RISK_LEVEL:
            raise ChamferBaselineImplementationPlanValidationError("unknown_risk_level")
        if stability.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
            raise ChamferBaselineImplementationPlanValidationError("unknown_implementation_status")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferBaselineImplementationPlanValidationError(f"authority_lock_must_be_false:{flag}")
    _prov_safe(packet["provenance"])


def compute_chamfer_baseline_implementation_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_baseline_implementation_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_baseline_implementation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    algorithm_plan = sorted(payload.get("algorithm_plan", default_algorithm_plan()), key=lambda x: x["step_id"])
    numerical_plan = sorted(payload.get("numerical_stability_plan", default_numerical_stability_plan()), key=lambda x: x["stability_id"])
    for step in algorithm_plan:
        step["planned_inputs"] = sorted(step.get("planned_inputs", []))
        step["planned_outputs"] = sorted(step.get("planned_outputs", []))
        step["blocked_operations"] = sorted(step.get("blocked_operations", []))

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_readiness_dossier_refs": sorted(payload.get("source_readiness_dossier_refs", [])),
        "source_metric_registry_refs": sorted(payload.get("source_metric_registry_refs", [])),
        "source_test_vector_pack_refs": sorted(payload.get("source_test_vector_pack_refs", [])),
        "algorithm_plan": algorithm_plan,
        "numerical_stability_plan": numerical_plan,
        "input_data_contract": payload.get("input_data_contract", default_input_data_contract()),
        "output_data_contract": payload.get("output_data_contract", default_output_data_contract()),
        "memory_layout_plan": payload.get("memory_layout_plan", default_memory_layout_plan()),
        "benchmark_plan": payload.get("benchmark_plan", default_benchmark_plan()),
        "future_acceleration_seams": payload.get("future_acceleration_seams", default_future_acceleration_seams()),
        "implementation_constraints": payload.get("implementation_constraints", default_implementation_constraints()),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_baseline_implementation_plan_hash(base)
    validate_chamfer_baseline_implementation_plan(base)
    return _finalize(base)
