from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.wasserstein_cpu_baseline_actual_pr_gate_review import (
    LOCKED_FALSE_FLAGS,
    WassersteinCpuBaselineActualPrGateReviewValidationError,
    build_wasserstein_cpu_baseline_actual_pr_gate_review,
    default_gate_conditions,
    default_output_contract,
    serialize_wasserstein_cpu_baseline_actual_pr_gate_review,
)


def _payload() -> dict:
    return {
        "review_id": "wasserstein-cpu-baseline-actual-pr-gate-review-test-001",
        "review_status": "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
        "plans_reviewed": [
            "WassersteinCpuBaselineImplementationPlan.v1:plan-001",
            "WassersteinCpuBaselineValidationPlan.v1:validation-plan-001",
        ],
        "gate_conditions": default_gate_conditions(),
        "implementation_recommendation": "ADVISORY_REVIEW_ONLY",
        "required_operator_decision": True,
        "stop_boundary_reason": "advisory only; operator decision required",
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_ACTUAL_PR_GATE_REVIEW_TEST",
            "evidence_refs": [
                "WassersteinCpuBaselineImplementationPlan.v1:plan-001"
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_cpu_baseline_actual_pr_gate_review.v1.schema.json"
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_hash_deterministic() -> None:
    a = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    b = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_version_fixed() -> None:
    p = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    assert p["schema_version"] == "WassersteinCpuBaselineActualPrGateReview.v1"


def test_review_type_fixed() -> None:
    p = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    assert p["review_type"] == "WASSERSTEIN_CPU_BASELINE_ACTUAL_PR_GATE_REVIEW"


def test_operator_id_fixed() -> None:
    p = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    assert p["operator_id"] == "WASSERSTEIN"


def test_required_operator_decision_always_true() -> None:
    p = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    assert p["required_operator_decision"] is True


def test_implementation_recommendation_not_authorized_or_advisory() -> None:
    p = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    assert p["implementation_recommendation"] in (
        "ADVISORY_REVIEW_ONLY",
        "NOT_AUTHORIZED",
        "BLOCKED",
    )
    assert p["implementation_recommendation"] != "AUTHORIZED"


def test_default_gate_conditions_non_empty() -> None:
    conds = default_gate_conditions()
    assert len(conds) >= 1


def test_default_gate_conditions_operator_decision_not_met() -> None:
    conds = default_gate_conditions()
    operator_conds = [c for c in conds if "operator" in c["condition_description"].lower()]
    assert operator_conds, "operator decision gate condition must exist"
    assert any(not c["condition_met"] for c in operator_conds), (
        "at least one operator decision condition must be unmet"
    )


def test_gate_conditions_sorted_by_condition_id() -> None:
    p = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    ids = [c["condition_id"] for c in p["gate_conditions"]]
    assert ids == sorted(ids)


def test_gate_conditions_no_duplicate_ids() -> None:
    conds = default_gate_conditions()
    ids = [c["condition_id"] for c in conds]
    assert len(ids) == len(set(ids))


def test_output_contract_no_metric_emission() -> None:
    c = default_output_contract()
    assert c["emits_metric_values"] is False
    assert c["emits_scores"] is False
    assert c["emits_forecast_inputs"] is False
    assert c["emits_authority_tokens"] is False
    assert c["emits_runtime_controls"] is False
    assert c["emits_gate_review"] is True


def test_all_governance_flags_false() -> None:
    p = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert p["governance_flags"][flag] is False, f"flag {flag} must be false"


def test_canonical_hash_64_hex() -> None:
    p = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    h = p["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_hash_changes_on_review_id_change() -> None:
    p1 = _payload()
    p2 = _payload()
    p2["review_id"] = "different-review-id"
    a = build_wasserstein_cpu_baseline_actual_pr_gate_review(p1)
    b = build_wasserstein_cpu_baseline_actual_pr_gate_review(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_plans_reviewed_sorted() -> None:
    payload = _payload()
    payload["plans_reviewed"] = [
        "ZZZ:plan-z",
        "AAA:plan-a",
    ]
    p = build_wasserstein_cpu_baseline_actual_pr_gate_review(payload)
    assert p["plans_reviewed"] == sorted(p["plans_reviewed"])


def test_serialize_is_valid_json() -> None:
    p = build_wasserstein_cpu_baseline_actual_pr_gate_review(_payload())
    raw = serialize_wasserstein_cpu_baseline_actual_pr_gate_review(p)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "WassersteinCpuBaselineActualPrGateReview.v1"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["governance_flags"].__setitem__("execution_authority", True),
            "authority_lock_must_be_false:execution_authority",
        ),
        (
            lambda p: p["governance_flags"].__setitem__("forecast_influence", True),
            "authority_lock_must_be_false:forecast_influence",
        ),
        (
            lambda p: p.__setitem__("review_status", "BAD_STATUS"),
            "unknown_review_status",
        ),
        (
            lambda p: p.__setitem__("implementation_recommendation", "AUTHORIZED"),
            "unknown_implementation_recommendation",
        ),
        (
            lambda p: p.__setitem__("plans_reviewed", []),
            "plans_reviewed_must_be_non_empty",
        ),
        (
            lambda p: p.__setitem__("gate_conditions", []),
            "gate_conditions_must_be_non_empty",
        ),
        (
            lambda p: p["gate_conditions"].append(dict(p["gate_conditions"][0])),
            "duplicate_condition_id",
        ),
        (
            lambda p: p["provenance"].__setitem__(
                "generated_by", "bad-wasserstein-distance-ref"
            ),
            "forbidden_provenance_reference_detected",
        ),
    ],
)
def test_validation_rejects_invalid(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(WassersteinCpuBaselineActualPrGateReviewValidationError, match=err):
        build_wasserstein_cpu_baseline_actual_pr_gate_review(payload)


def test_committed_artifact_parseable() -> None:
    path = Path(
        "out/metric_operator/"
        "wasserstein_cpu_baseline_actual_pr_gate_review_001.latest.json"
    )
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "WassersteinCpuBaselineActualPrGateReview.v1"
    assert data["operator_id"] == "WASSERSTEIN"
    assert len(data["canonical_hash"]) == 64
