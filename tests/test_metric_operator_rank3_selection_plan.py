from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_rank3_selection_plan import (
    LOCKED_FALSE_FLAGS,
    MetricOperatorRank3SelectionPlanValidationError,
    build_metric_operator_rank3_selection_plan,
    default_implementation_gates,
    default_output_contract,
    serialize_metric_operator_rank3_selection_plan,
)


def _payload() -> dict:
    return {
        "plan_id": "rank3-selection-plan-test-001",
        "selection_scope": {
            "intended_lane": "SHADOW",
            "selection_family": "RANK3_OPERATOR_SELECTION",
            "selection_stage": "SELECTION_PLAN_ONLY",
        },
        "source_audit_refs": [
            "MetricOperatorRank3CandidateAudit.v1:audit-001"
        ],
        "source_registry_stabilization_refs": [
            "MetricOperatorRegistryStabilization.v1:stabilization-001"
        ],
        "source_frontier_recommendation_refs": [
            "MetricOperatorFrontierRecommendation.v1:recommendation-001"
        ],
        "implementation_gates": default_implementation_gates(),
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "METRIC_OPERATOR_RANK3_SELECTION_PLAN_TEST",
            "evidence_refs": ["MetricOperatorRank3CandidateAudit.v1:audit-001"],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_rank3_selection_plan.v1.schema.json"
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_hash_deterministic() -> None:
    a = build_metric_operator_rank3_selection_plan(_payload())
    b = build_metric_operator_rank3_selection_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_version_fixed() -> None:
    p = build_metric_operator_rank3_selection_plan(_payload())
    assert p["schema_version"] == "MetricOperatorRank3SelectionPlan.v1"


def test_plan_type_fixed() -> None:
    p = build_metric_operator_rank3_selection_plan(_payload())
    assert p["plan_type"] == "METRIC_OPERATOR_RANK3_SELECTION_PLAN"


def test_selected_operator_id_always_geodesic() -> None:
    p = build_metric_operator_rank3_selection_plan(_payload())
    assert p["selected_operator_id"] == "GEODESIC"


def test_implementation_gates_all_blocking() -> None:
    gates = default_implementation_gates()
    assert gates["implementation_blocked"] is True
    assert gates["fixture_creation_blocked"] is True
    assert gates["planning_only"] is True
    assert gates["requires_dedicated_tests"] is True
    assert gates["requires_new_operator_plan"] is True


def test_output_contract_no_metric_emission() -> None:
    c = default_output_contract()
    assert c["emits_metric_values"] is False
    assert c["emits_scores"] is False
    assert c["emits_forecast_inputs"] is False
    assert c["emits_authority_tokens"] is False
    assert c["emits_selection_metadata"] is True


def test_all_governance_flags_false() -> None:
    p = build_metric_operator_rank3_selection_plan(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert p["governance_flags"][flag] is False


def test_canonical_hash_64_hex() -> None:
    p = build_metric_operator_rank3_selection_plan(_payload())
    h = p["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_source_audit_refs_sorted() -> None:
    payload = _payload()
    payload["source_audit_refs"] = ["Z:z", "A:a"]
    p = build_metric_operator_rank3_selection_plan(payload)
    assert p["source_audit_refs"] == sorted(p["source_audit_refs"])


def test_serialize_is_valid_json() -> None:
    p = build_metric_operator_rank3_selection_plan(_payload())
    raw = serialize_metric_operator_rank3_selection_plan(p)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "MetricOperatorRank3SelectionPlan.v1"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["selection_scope"].__setitem__("intended_lane", "BAD"),
            "unknown_intended_lane",
        ),
        (
            lambda p: p["selection_scope"].__setitem__("selection_family", "BAD"),
            "unknown_selection_family",
        ),
        (
            lambda p: p["selection_scope"].__setitem__("selection_stage", "BAD"),
            "unknown_selection_stage",
        ),
        (
            lambda p: p.__setitem__("source_audit_refs", []),
            "source_audit_refs_must_be_non_empty",
        ),
        (
            lambda p: p["governance_flags"].__setitem__("forecast_influence", True),
            "authority_lock_must_be_false:forecast_influence",
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
    with pytest.raises(MetricOperatorRank3SelectionPlanValidationError, match=err):
        build_metric_operator_rank3_selection_plan(payload)


def test_committed_artifact_parseable() -> None:
    path = Path("out/metric_operator/metric_operator_rank3_selection_plan_001.latest.json")
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "MetricOperatorRank3SelectionPlan.v1"
    assert data["selected_operator_id"] == "GEODESIC"
    assert len(data["canonical_hash"]) == 64
