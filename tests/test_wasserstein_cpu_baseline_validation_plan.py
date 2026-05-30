from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.wasserstein_cpu_baseline_validation_plan import (
    LOCKED_FALSE_FLAGS,
    WassersteinCpuBaselineValidationPlanValidationError,
    build_wasserstein_cpu_baseline_validation_plan,
    default_fixture_validation_scope,
    default_invalid_fixture_rejection_scope,
    default_no_forecast_scan,
    default_no_p43_scan,
    default_no_runtime_scan,
    default_output_contract,
    default_tolerance_policy,
    serialize_wasserstein_cpu_baseline_validation_plan,
)


def _payload() -> dict:
    return {
        "plan_id": "wasserstein-cpu-baseline-validation-plan-test-001",
        "source_implementation_plan_refs": [
            "WassersteinCpuBaselineImplementationPlan.v1:plan-001"
        ],
        "fixture_validation_scope": default_fixture_validation_scope(),
        "tolerance_policy": default_tolerance_policy(),
        "invalid_fixture_rejection_scope": default_invalid_fixture_rejection_scope(),
        "no_runtime_scan": default_no_runtime_scan(),
        "no_forecast_scan": default_no_forecast_scan(),
        "no_p43_scan": default_no_p43_scan(),
        "execution_authorized": False,
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_VALIDATION_PLAN_TEST",
            "evidence_refs": [
                "WassersteinCpuBaselineImplementationPlan.v1:plan-001"
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_cpu_baseline_validation_plan.v1.schema.json"
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_hash_deterministic() -> None:
    a = build_wasserstein_cpu_baseline_validation_plan(_payload())
    b = build_wasserstein_cpu_baseline_validation_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_version_fixed() -> None:
    p = build_wasserstein_cpu_baseline_validation_plan(_payload())
    assert p["schema_version"] == "WassersteinCpuBaselineValidationPlan.v1"


def test_plan_type_fixed() -> None:
    p = build_wasserstein_cpu_baseline_validation_plan(_payload())
    assert p["plan_type"] == "WASSERSTEIN_CPU_BASELINE_VALIDATION_PLAN"


def test_operator_id_fixed() -> None:
    p = build_wasserstein_cpu_baseline_validation_plan(_payload())
    assert p["operator_id"] == "WASSERSTEIN"


def test_execution_authorized_always_false() -> None:
    payload = _payload()
    payload["execution_authorized"] = True
    p = build_wasserstein_cpu_baseline_validation_plan(payload)
    assert p["execution_authorized"] is False


def test_fixture_validation_scope_defaults() -> None:
    fvs = default_fixture_validation_scope()
    assert fvs["valid_fixture_count"] == 5
    assert fvs["fixture_ids_declared"] is True
    assert fvs["execution_enabled"] is False
    assert fvs["determinism_required"] is True


def test_tolerance_policy_defaults() -> None:
    tp = default_tolerance_policy()
    assert tp["float64_required"] is True
    assert tp["zero_tolerance_for_1d_declared"] is True
    assert tp["tolerance_execution_enabled"] is False


def test_invalid_fixture_rejection_scope_defaults() -> None:
    s = default_invalid_fixture_rejection_scope()
    assert s["invalid_fixture_count"] == 2
    assert s["not_computable_fixture_count"] == 3
    assert s["rejection_policy_declared"] is True
    assert s["execution_enabled"] is False


def test_no_runtime_scan_defaults() -> None:
    s = default_no_runtime_scan()
    assert s["scan_declared"] is True
    assert s["runtime_mutation_blocked"] is True
    assert s["runtime_binding_blocked"] is True


def test_no_forecast_scan_defaults() -> None:
    s = default_no_forecast_scan()
    assert s["scan_declared"] is True
    assert s["forecast_influence_blocked"] is True


def test_no_p43_scan_defaults() -> None:
    s = default_no_p43_scan()
    assert s["scan_declared"] is True
    assert s["p43_surface_lanes_blocked"] is True


def test_output_contract_no_metric_emission() -> None:
    c = default_output_contract()
    assert c["emits_metric_values"] is False
    assert c["emits_scores"] is False
    assert c["emits_forecast_inputs"] is False
    assert c["emits_authority_tokens"] is False
    assert c["emits_validation_plan"] is True


def test_all_governance_flags_false() -> None:
    p = build_wasserstein_cpu_baseline_validation_plan(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert p["governance_flags"][flag] is False, f"flag {flag} must be false"


def test_canonical_hash_64_hex() -> None:
    p = build_wasserstein_cpu_baseline_validation_plan(_payload())
    h = p["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_hash_changes_on_plan_id_change() -> None:
    p1 = _payload()
    p2 = _payload()
    p2["plan_id"] = "different-plan-id"
    a = build_wasserstein_cpu_baseline_validation_plan(p1)
    b = build_wasserstein_cpu_baseline_validation_plan(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_serialize_is_valid_json() -> None:
    p = build_wasserstein_cpu_baseline_validation_plan(_payload())
    raw = serialize_wasserstein_cpu_baseline_validation_plan(p)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "WassersteinCpuBaselineValidationPlan.v1"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["governance_flags"].__setitem__("execution_authority", True),
            "authority_lock_must_be_false:execution_authority",
        ),
        (
            lambda p: p["governance_flags"].__setitem__("runtime_mutation", True),
            "authority_lock_must_be_false:runtime_mutation",
        ),
        (
            lambda p: p["fixture_validation_scope"].__setitem__("execution_enabled", True),
            "fixture_validation_execution_must_be_false",
        ),
        (
            lambda p: p["tolerance_policy"].__setitem__("tolerance_execution_enabled", True),
            "tolerance_execution_must_be_false",
        ),
        (
            lambda p: p["invalid_fixture_rejection_scope"].__setitem__("execution_enabled", True),
            "rejection_execution_must_be_false",
        ),
        (
            lambda p: p["provenance"].__setitem__("generated_by", "bad-wasserstein-distance-ref"),
            "forbidden_provenance_reference_detected",
        ),
    ],
)
def test_validation_rejects_invalid(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(WassersteinCpuBaselineValidationPlanValidationError, match=err):
        build_wasserstein_cpu_baseline_validation_plan(payload)


def test_committed_artifact_parseable() -> None:
    path = Path("out/metric_operator/wasserstein_cpu_baseline_validation_plan_001.latest.json")
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "WassersteinCpuBaselineValidationPlan.v1"
    assert data["operator_id"] == "WASSERSTEIN"
    assert len(data["canonical_hash"]) == 64
