from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_baseline_implementation_plan import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_baseline_implementation_plan,
    compute_chamfer_baseline_implementation_plan_hash,
    default_algorithm_plan,
    default_benchmark_plan,
    default_future_acceleration_seams,
    default_implementation_constraints,
    default_input_data_contract,
    default_memory_layout_plan,
    default_numerical_stability_plan,
    default_output_contract,
    default_output_data_contract,
    default_validation_plan,
    serialize_chamfer_baseline_implementation_plan,
)


def _payload() -> dict[str, object]:
    return {
        "plan_id": "chamfer-baseline-implementation-plan-001",
        "source_readiness_dossier_refs": ["ChamferDistanceImplementationReadinessDossier.v1:dossier-001"],
        "source_metric_registry_refs": ["MetricOperatorRegistry.v1:registry-001"],
        "source_test_vector_pack_refs": ["MetricOperatorBaselineTestVectorPack.v1:pack-001"],
        "implementation_topology": {
            "implementation_mode": "CPU_REFERENCE_PLAN",
            "intended_lane": "SHADOW",
            "topology_stage": "BASELINE_PLAN_ONLY",
        },
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "CHAMFER_BASELINE_IMPLEMENTATION_PLAN_v0.1",
            "evidence_refs": ["MetricOperatorImplementationSelectionPlan.v1:plan-001"],
            "generated_by": "unit-test",
            "upstream_schema_refs": ["contracts/canon/chamfer_distance_implementation_readiness_dossier.v1.schema.json"],
        },
        "created_at_utc": "2026-05-28T00:00:00Z",
    }


def test_hash_and_serialize_deterministic() -> None:
    a = build_chamfer_baseline_implementation_plan(_payload())
    b = build_chamfer_baseline_implementation_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_baseline_implementation_plan(a) == serialize_chamfer_baseline_implementation_plan(b)


def test_default_plans_non_empty_deterministic() -> None:
    assert default_algorithm_plan() and default_numerical_stability_plan()
    assert default_algorithm_plan() == default_algorithm_plan()
    assert default_numerical_stability_plan() == default_numerical_stability_plan()


def test_operator_must_be_chamfer_distance() -> None:
    payload = _payload()
    payload["operator_id"] = "BAD"
    packet = build_chamfer_baseline_implementation_plan(payload)
    assert packet["operator_id"] == "CHAMFER_DISTANCE"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["implementation_topology"].__setitem__("implementation_mode", "BAD"), "unknown_implementation_mode"),
        (lambda p: p["implementation_topology"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["implementation_topology"].__setitem__("topology_stage", "BAD"), "unknown_topology_stage"),
        (lambda p: p["algorithm_plan"].append(dict(p["algorithm_plan"][0])), "duplicate_step_id"),
        (lambda p: p["algorithm_plan"][0].__setitem__("step_type", "BAD"), "unknown_step_type"),
        (lambda p: p["algorithm_plan"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
        (lambda p: p["numerical_stability_plan"].append(dict(p["numerical_stability_plan"][0])), "duplicate_stability_id"),
        (lambda p: p["numerical_stability_plan"][0].__setitem__("stability_type", "BAD"), "unknown_stability_type"),
        (lambda p: p["numerical_stability_plan"][0].__setitem__("risk_level", "BAD"), "unknown_risk_level"),
    ],
)
def test_failures(mutator, err: str) -> None:
    payload = _payload()
    payload["algorithm_plan"] = default_algorithm_plan()
    payload["numerical_stability_plan"] = default_numerical_stability_plan()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_chamfer_baseline_implementation_plan(payload)


def test_locked_maps() -> None:
    payload = _payload()
    payload["input_data_contract"] = default_input_data_contract()
    payload["input_data_contract"]["runtime_binding_enabled"] = True
    with pytest.raises(ValueError, match="invalid_input_data_contract"):
        build_chamfer_baseline_implementation_plan(payload)

    payload = _payload()
    payload["output_data_contract"] = default_output_data_contract()
    payload["output_data_contract"]["emits_distance_value"] = True
    with pytest.raises(ValueError, match="invalid_output_data_contract"):
        build_chamfer_baseline_implementation_plan(payload)

    payload = _payload()
    payload["memory_layout_plan"] = default_memory_layout_plan()
    payload["memory_layout_plan"]["gpu_memory_enabled"] = True
    with pytest.raises(ValueError, match="invalid_memory_layout_plan"):
        build_chamfer_baseline_implementation_plan(payload)

    payload = _payload()
    payload["benchmark_plan"] = default_benchmark_plan()
    payload["benchmark_plan"]["benchmark_execution_enabled"] = True
    with pytest.raises(ValueError, match="invalid_benchmark_plan"):
        build_chamfer_baseline_implementation_plan(payload)

    payload = _payload()
    payload["future_acceleration_seams"] = default_future_acceleration_seams()
    payload["future_acceleration_seams"]["acceleration_implemented"] = True
    with pytest.raises(ValueError, match="invalid_future_acceleration_seams"):
        build_chamfer_baseline_implementation_plan(payload)

    payload = _payload()
    payload["implementation_constraints"] = default_implementation_constraints()
    payload["implementation_constraints"]["metric_values_emitted"] = True
    with pytest.raises(ValueError, match="invalid_implementation_constraints"):
        build_chamfer_baseline_implementation_plan(payload)

    payload = _payload()
    payload["validation_plan"] = default_validation_plan()
    payload["validation_plan"]["requires_no_authority_scan"] = False
    with pytest.raises(ValueError, match="invalid_validation_plan"):
        build_chamfer_baseline_implementation_plan(payload)

    payload = _payload()
    payload["output_contract"] = default_output_contract()
    payload["output_contract"]["emits_metric_values"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_chamfer_baseline_implementation_plan(payload)

    payload = _payload()
    payload["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_chamfer_baseline_implementation_plan(payload)


def test_provenance_hash_schema_refs() -> None:
    payload = _payload()
    payload["provenance"]["source"] = "numpy scipy metric-value runtime"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_chamfer_baseline_implementation_plan(payload)

    packet = build_chamfer_baseline_implementation_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_baseline_implementation_plan_hash(packet) == compute_chamfer_baseline_implementation_plan_hash(altered)

    changed_payload = _payload()
    changed_payload["implementation_topology"]["topology_stage"] = "DATA_LAYOUT_ONLY"
    changed = build_chamfer_baseline_implementation_plan(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_baseline_implementation_plan.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(packet, schema)
    assert packet["source_readiness_dossier_refs"]
    assert packet["source_metric_registry_refs"]
    assert packet["source_test_vector_pack_refs"]
