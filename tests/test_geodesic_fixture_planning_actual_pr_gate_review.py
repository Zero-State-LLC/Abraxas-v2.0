from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.geodesic_fixture_planning_actual_pr_gate_review import (
    LOCKED_FALSE_FLAGS,
    GeodesicFixturePlanningActualPrGateReviewValidationError,
    build_geodesic_fixture_planning_actual_pr_gate_review,
    default_gate_conditions,
    default_output_contract,
    serialize_geodesic_fixture_planning_actual_pr_gate_review,
)


def _payload() -> dict:
    return {
        "review_id": "pr-gate-review-test-001",
        "authorization_reviews_referenced": [
            "GeodesicFixturePlanningAuthorizationReview.v1:auth-review-001"
        ],
        "gate_conditions": default_gate_conditions(),
        "review_status": "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
        "fixture_planning_recommendation": "ADVISORY_REVIEW_ONLY",
        "stop_boundary_reason": "Advisory only; gate-cond-005 unmet.",
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "GEODESIC_FIXTURE_PLANNING_ACTUAL_PR_GATE_REVIEW_TEST",
            "evidence_refs": [
                "GeodesicFixturePlanningAuthorizationReview.v1:auth-review-001"
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "geodesic_fixture_planning_actual_pr_gate_review.v1.schema.json"
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_hash_deterministic() -> None:
    a = build_geodesic_fixture_planning_actual_pr_gate_review(_payload())
    b = build_geodesic_fixture_planning_actual_pr_gate_review(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_version_fixed() -> None:
    p = build_geodesic_fixture_planning_actual_pr_gate_review(_payload())
    assert p["schema_version"] == "GeodesicFixturePlanningActualPrGateReview.v1"


def test_review_type_fixed() -> None:
    p = build_geodesic_fixture_planning_actual_pr_gate_review(_payload())
    assert p["review_type"] == "GEODESIC_FIXTURE_PLANNING_ACTUAL_PR_GATE_REVIEW"


def test_operator_id_fixed() -> None:
    p = build_geodesic_fixture_planning_actual_pr_gate_review(_payload())
    assert p["operator_id"] == "GEODESIC"


def test_required_operator_decision_always_true() -> None:
    p = build_geodesic_fixture_planning_actual_pr_gate_review(_payload())
    assert p["required_operator_decision"] is True


def test_gate_cond_005_present_and_unmet() -> None:
    conditions = default_gate_conditions()
    gate5 = next((c for c in conditions if c["condition_id"] == "gate-cond-005"), None)
    assert gate5 is not None
    assert gate5["condition_met"] is False
    assert "blocking_reason" in gate5


def test_all_other_gate_conditions_met() -> None:
    conditions = default_gate_conditions()
    for c in conditions:
        if c["condition_id"] != "gate-cond-005":
            assert c["condition_met"] is True, f"{c['condition_id']} should be met"


def test_five_gate_conditions_total() -> None:
    assert len(default_gate_conditions()) == 5


def test_authorization_reviews_referenced_sorted() -> None:
    payload = _payload()
    payload["authorization_reviews_referenced"] = ["Z:z", "A:a"]
    p = build_geodesic_fixture_planning_actual_pr_gate_review(payload)
    assert p["authorization_reviews_referenced"] == sorted(
        p["authorization_reviews_referenced"]
    )


def test_output_contract_no_fixture_emission() -> None:
    c = default_output_contract()
    assert c["emits_fixture_files"] is False
    assert c["emits_metric_values"] is False
    assert c["emits_authority_tokens"] is False
    assert c["emits_gate_review"] is True


def test_all_governance_flags_false() -> None:
    p = build_geodesic_fixture_planning_actual_pr_gate_review(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert p["governance_flags"][flag] is False


def test_canonical_hash_64_hex() -> None:
    p = build_geodesic_fixture_planning_actual_pr_gate_review(_payload())
    h = p["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_serialize_is_valid_json() -> None:
    p = build_geodesic_fixture_planning_actual_pr_gate_review(_payload())
    raw = serialize_geodesic_fixture_planning_actual_pr_gate_review(p)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "GeodesicFixturePlanningActualPrGateReview.v1"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p.__setitem__("authorization_reviews_referenced", []),
            "authorization_reviews_referenced_must_be_non_empty",
        ),
        (
            lambda p: p.__setitem__("gate_conditions", []),
            "gate_conditions_must_be_non_empty",
        ),
        (
            lambda p: p.__setitem__("stop_boundary_reason", ""),
            "stop_boundary_reason_must_be_non_empty",
        ),
        (
            lambda p: p.__setitem__("review_status", "UNKNOWN"),
            "unknown_review_status",
        ),
        (
            lambda p: p.__setitem__("fixture_planning_recommendation", "UNKNOWN"),
            "unknown_fixture_planning_recommendation",
        ),
        (
            lambda p: p["governance_flags"].__setitem__("forecast_influence", True),
            "authority_lock_must_be_false:forecast_influence",
        ),
        (
            lambda p: p.__setitem__(
                "gate_conditions",
                [c for c in default_gate_conditions() if c["condition_id"] != "gate-cond-005"],
            ),
            "gate_cond_005_missing",
        ),
        (
            lambda p: [
                c.__setitem__("condition_met", True)
                for c in p["gate_conditions"]
                if c["condition_id"] == "gate-cond-005"
            ],
            "gate_cond_005_must_be_unmet",
        ),
        (
            lambda p: p["provenance"].__setitem__(
                "generated_by", "bad-geodesic-distance-ref"
            ),
            "forbidden_provenance_reference_detected",
        ),
    ],
)
def test_validation_rejects_invalid(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(
        GeodesicFixturePlanningActualPrGateReviewValidationError, match=err
    ):
        build_geodesic_fixture_planning_actual_pr_gate_review(payload)


def test_committed_artifact_parseable() -> None:
    path = Path(
        "out/metric_operator/"
        "geodesic_fixture_planning_actual_pr_gate_review_001.latest.json"
    )
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "GeodesicFixturePlanningActualPrGateReview.v1"
    assert data["operator_id"] == "GEODESIC"
    assert data["fixture_planning_recommendation"] == "ADVISORY_REVIEW_ONLY"
    assert len(data["canonical_hash"]) == 64
