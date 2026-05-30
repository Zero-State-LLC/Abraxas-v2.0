from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.wasserstein_cpu_baseline_implementation_plan import (
    LOCKED_FALSE_FLAGS,
    WassersteinCpuBaselineImplementationPlanValidationError,
    build_wasserstein_cpu_baseline_implementation_plan,
    default_algorithm_plan,
    default_benchmark_plan,
    default_future_acceleration_seams,
    default_implementation_constraints,
    default_input_data_contract,
    default_memory_layout_plan,
    default_numerical_stability_plan,
    default_output_contract,
    default_output_data_contract,
    serialize_wasserstein_cpu_baseline_implementation_plan,
)


def _payload() -> dict:
    return {
        "plan_id": "wasserstein-cpu-baseline-plan-test-001",
        "source_readiness_dossier_refs": [
            "WassersteinDistanceImplementationReadinessDossier.v1:dossier-001"
        ],
        "source_metric_registry_refs": ["MetricOperatorRegistry.v1:registry-001"],
        "source_test_vector_pack_refs": [
            "MetricOperatorBaselineTestVectorPack.v1:pack-001"
        ],
        "implementation_topology": {
            "implementation_mode": "CPU_REFERENCE_PLAN",
            "intended_lane": "SHADOW",
            "topology_stage": "BASELINE_PLAN_ONLY",
        },
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_PLAN_TEST",
            "evidence_refs": ["WassersteinDistanceImplementationReadinessDossier.v1:dossier-001"],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_cpu_baseline_implementation_plan.v1.schema.json"
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_hash_deterministic() -> None:
    a = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    b = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_serialize_deterministic() -> None:
    a = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    b = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    assert serialize_wasserstein_cpu_baseline_implementation_plan(a) == (
        serialize_wasserstein_cpu_baseline_implementation_plan(b)
    )


def test_schema_version_fixed() -> None:
    p = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    assert p["schema_version"] == "WassersteinCpuBaselineImplementationPlan.v1"


def test_plan_type_fixed() -> None:
    p = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    assert p["plan_type"] == "WASSERSTEIN_CPU_BASELINE_IMPLEMENTATION_PLAN"


def test_operator_id_fixed() -> None:
    p = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    assert p["operator_id"] == "WASSERSTEIN"


def test_default_algorithm_plan_non_empty_and_deterministic() -> None:
    plan = default_algorithm_plan()
    assert len(plan) >= 1
    assert default_algorithm_plan() == plan


def test_default_algorithm_plan_has_expected_steps() -> None:
    step_types = {s["step_type"] for s in default_algorithm_plan()}
    assert "INPUT_VALIDATION_STEP" in step_types
    assert "OPTIMAL_TRANSPORT_TOPOLOGY_STEP" in step_types
    assert "BASELINE_COMPARATOR_STEP" in step_types
    assert "NOT_COMPUTABLE_BRANCH_STEP" in step_types


def test_default_numerical_stability_plan_non_empty_and_deterministic() -> None:
    plan = default_numerical_stability_plan()
    assert len(plan) >= 1
    assert default_numerical_stability_plan() == plan


def test_default_numerical_stability_plan_has_expected_types() -> None:
    types = {s["stability_type"] for s in default_numerical_stability_plan()}
    assert "FLOAT_PRECISION_POLICY" in types
    assert "DEGENERATE_DISTRIBUTION_POLICY" in types
    assert "NOT_COMPUTABLE_POLICY" in types


def test_implementation_constraints_wasserstein_key() -> None:
    c = default_implementation_constraints()
    assert "wasserstein_math_added" in c
    assert c["wasserstein_math_added"] is False
    assert "chamfer_math_added" not in c


def test_all_governance_flags_false() -> None:
    p = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert p["governance_flags"][flag] is False, f"flag {flag} must be false"


def test_output_contract_no_metric_emission() -> None:
    c = default_output_contract()
    assert c["emits_metric_values"] is False
    assert c["emits_metric_code"] is False
    assert c["emits_forecast_inputs"] is False
    assert c["emits_authority_tokens"] is False


def test_input_data_contract_no_runtime_binding() -> None:
    c = default_input_data_contract()
    assert c["runtime_binding_enabled"] is False


def test_output_data_contract_no_distance_emission() -> None:
    c = default_output_data_contract()
    assert c["emits_distance_value"] is False
    assert c["emits_transport_plan"] is False
    assert c["runtime_output_binding_enabled"] is False


def test_memory_layout_no_runtime_binding() -> None:
    m = default_memory_layout_plan()
    assert m["streaming_mode_enabled"] is False
    assert m["gpu_memory_enabled"] is False
    assert m["runtime_buffer_binding_enabled"] is False


def test_benchmark_plan_no_execution() -> None:
    b = default_benchmark_plan()
    assert b["benchmark_execution_enabled"] is False
    assert b["deterministic_replay_required"] is True


def test_future_acceleration_seams_no_runtime() -> None:
    f = default_future_acceleration_seams()
    assert f["acceleration_implemented"] is False
    assert f["acceleration_runtime_enabled"] is False
    assert f["approximation_candidate_declared"] is True


def test_canonical_hash_64_hex() -> None:
    p = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    h = p["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_hash_changes_on_plan_id_change() -> None:
    p1 = _payload()
    p2 = _payload()
    p2["plan_id"] = "different-id"
    a = build_wasserstein_cpu_baseline_implementation_plan(p1)
    b = build_wasserstein_cpu_baseline_implementation_plan(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_algorithm_steps_sorted_by_step_id() -> None:
    p = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    ids = [s["step_id"] for s in p["algorithm_plan"]]
    assert ids == sorted(ids)


def test_stability_entries_sorted_by_stability_id() -> None:
    p = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    ids = [s["stability_id"] for s in p["numerical_stability_plan"]]
    assert ids == sorted(ids)


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["implementation_topology"].__setitem__("implementation_mode", "BAD"),
            "unknown_implementation_mode",
        ),
        (
            lambda p: p["implementation_topology"].__setitem__("intended_lane", "BAD"),
            "unknown_intended_lane",
        ),
        (
            lambda p: p["implementation_topology"].__setitem__("topology_stage", "BAD"),
            "unknown_topology_stage",
        ),
        (
            lambda p: p["algorithm_plan"].append(dict(p["algorithm_plan"][0])),
            "duplicate_step_id",
        ),
        (
            lambda p: p["algorithm_plan"][0].__setitem__("step_type", "BAD"),
            "unknown_step_type",
        ),
        (
            lambda p: p["algorithm_plan"][0].__setitem__("implementation_status", "BAD"),
            "unknown_implementation_status",
        ),
        (
            lambda p: p["numerical_stability_plan"].append(
                dict(p["numerical_stability_plan"][0])
            ),
            "duplicate_stability_id",
        ),
        (
            lambda p: p["numerical_stability_plan"][0].__setitem__("stability_type", "BAD"),
            "unknown_stability_type",
        ),
        (
            lambda p: p["numerical_stability_plan"][0].__setitem__("risk_level", "BAD"),
            "unknown_risk_level",
        ),
        (
            lambda p: p["governance_flags"].__setitem__("execution_authority", True),
            "authority_lock_must_be_false:execution_authority",
        ),
        (
            lambda p: p["governance_flags"].__setitem__("forecast_influence", True),
            "authority_lock_must_be_false:forecast_influence",
        ),
        (
            lambda p: p["provenance"].__setitem__("generated_by", "bad-wasserstein-distance-ref"),
            "forbidden_provenance_reference_detected",
        ),
    ],
)
def test_validation_rejects_invalid(mutator, err: str) -> None:
    payload = _payload()
    payload["algorithm_plan"] = default_algorithm_plan()
    payload["numerical_stability_plan"] = default_numerical_stability_plan()
    mutator(payload)
    with pytest.raises(WassersteinCpuBaselineImplementationPlanValidationError, match=err):
        build_wasserstein_cpu_baseline_implementation_plan(payload)


def test_serialize_is_valid_json() -> None:
    p = build_wasserstein_cpu_baseline_implementation_plan(_payload())
    raw = serialize_wasserstein_cpu_baseline_implementation_plan(p)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "WassersteinCpuBaselineImplementationPlan.v1"


def test_committed_artifact_parseable() -> None:
    path = Path(
        "out/metric_operator/wasserstein_cpu_baseline_implementation_plan_001.latest.json"
    )
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "WassersteinCpuBaselineImplementationPlan.v1"
    assert data["operator_id"] == "WASSERSTEIN"
    assert len(data["canonical_hash"]) == 64
