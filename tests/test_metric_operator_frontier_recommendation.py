from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_frontier_recommendation import (
    MetricOperatorFrontierRecommendationError,
    build_metric_operator_frontier_recommendation,
    default_governance_flags,
    default_output_contract,
    default_ranked_options,
    serialize_metric_operator_frontier_recommendation,
)

_ARTIFACT_PATH = Path(
    "out/metric_operator/metric_operator_frontier_recommendation_001.latest.json"
)


def _payload() -> dict:
    return {
        "recommendation_id": "metric_operator_frontier_recommendation_001",
        "recommendation_status": "ADVISORY_ONLY",
        "ranked_options": default_ranked_options(),
        "recommended_next_step": "G_SEALED_PAUSE",
        "required_operator_decision": True,
        "stop_boundary_reason": "Test stop boundary reason.",
        "output_contract": default_output_contract(),
        "governance_flags": default_governance_flags(),
        "provenance": {
            "source": "TEST",
            "advisory_only": True,
            "generated_by": "TEST_ONLY",
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_deterministic_hash() -> None:
    first = build_metric_operator_frontier_recommendation(_payload())
    second = build_metric_operator_frontier_recommendation(_payload())
    assert first["canonical_hash"] == second["canonical_hash"]


def test_serialize_deterministic() -> None:
    a = build_metric_operator_frontier_recommendation(_payload())
    b = build_metric_operator_frontier_recommendation(_payload())
    assert serialize_metric_operator_frontier_recommendation(a) == serialize_metric_operator_frontier_recommendation(b)


def test_default_ranked_options_count() -> None:
    options = default_ranked_options()
    assert len(options) == 7


def test_default_ranks_unique_and_sequential() -> None:
    options = default_ranked_options()
    ranks = sorted(o["rank"] for o in options)
    assert ranks == list(range(1, 8))


def test_default_option_ids_unique() -> None:
    options = default_ranked_options()
    ids = [o["option_id"] for o in options]
    assert len(ids) == len(set(ids))


def test_rank_1_is_sealed_pause() -> None:
    options = {o["rank"]: o for o in default_ranked_options()}
    assert options[1]["option_id"] == "G_SEALED_PAUSE"


def test_blocked_options_have_blocked_posture() -> None:
    options = {o["option_id"]: o for o in default_ranked_options()}
    assert options["C_METRIC_EMISSION_AUTHORIZATION_REVIEW"]["authority_posture"] == "BLOCKED"
    assert options["E_P43_SURFACE_LANE_READINESS"]["authority_posture"] == "BLOCKED"


def test_advisory_options_have_advisory_posture() -> None:
    options = {o["option_id"]: o for o in default_ranked_options()}
    for oid in ("G_SEALED_PAUSE", "F_REGISTRY_STABILIZATION", "A_CROSS_OPERATOR_PARITY_REVIEW",
                "D_CPU_REFERENCE_IMPLEMENTATION_PLANNING", "B_THIRD_OPERATOR_SELECTION"):
        assert options[oid]["authority_posture"] == "ADVISORY_ONLY"


def test_authority_locks_all_false() -> None:
    record = build_metric_operator_frontier_recommendation(_payload())
    for v in record["governance_flags"].values():
        assert v is False


def test_output_contract_correct() -> None:
    record = build_metric_operator_frontier_recommendation(_payload())
    assert record["output_contract"]["emits_metric_values"] is False
    assert record["output_contract"]["emits_recommendation"] is True


def test_invalid_recommendation_status_raises() -> None:
    p = _payload()
    p["recommendation_status"] = "EXECUTE_NOW"
    with pytest.raises(MetricOperatorFrontierRecommendationError, match="invalid_recommendation_status"):
        build_metric_operator_frontier_recommendation(p)


def test_duplicate_rank_raises() -> None:
    p = _payload()
    dup = dict(p["ranked_options"][0])
    p["ranked_options"].append(dup)
    with pytest.raises(MetricOperatorFrontierRecommendationError, match="duplicate_rank"):
        build_metric_operator_frontier_recommendation(p)


def test_duplicate_option_id_raises() -> None:
    p = _payload()
    dup = dict(p["ranked_options"][0])
    dup["rank"] = 99
    p["ranked_options"].append(dup)
    with pytest.raises(MetricOperatorFrontierRecommendationError, match="duplicate_option_id"):
        build_metric_operator_frontier_recommendation(p)


def test_invalid_authority_posture_raises() -> None:
    p = _payload()
    p["ranked_options"][0]["authority_posture"] = "EXECUTE"
    with pytest.raises(MetricOperatorFrontierRecommendationError, match="invalid_authority_posture"):
        build_metric_operator_frontier_recommendation(p)


def test_authority_flag_true_raises() -> None:
    p = _payload()
    p["governance_flags"]["production_activation"] = True
    with pytest.raises(MetricOperatorFrontierRecommendationError, match="authority_lock_must_be_false"):
        build_metric_operator_frontier_recommendation(p)


def test_forbidden_provenance_token_raises() -> None:
    p = _payload()
    p["provenance"]["generated_by"] = "callable-system"
    with pytest.raises(MetricOperatorFrontierRecommendationError, match="forbidden_provenance_reference_detected"):
        build_metric_operator_frontier_recommendation(p)


def test_schema_version_set_correctly() -> None:
    record = build_metric_operator_frontier_recommendation(_payload())
    assert record["schema_version"] == "MetricOperatorFrontierRecommendation.v1"


def test_canonical_hash_64_hex() -> None:
    record = build_metric_operator_frontier_recommendation(_payload())
    h = record["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_required_operator_decision_true() -> None:
    record = build_metric_operator_frontier_recommendation(_payload())
    assert record["required_operator_decision"] is True


def test_committed_artifact_exists_and_valid() -> None:
    if not _ARTIFACT_PATH.exists():
        pytest.skip("artifact not yet emitted")
    on_disk = json.loads(_ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert on_disk["schema_version"] == "MetricOperatorFrontierRecommendation.v1"
    assert on_disk["recommendation_status"] == "ADVISORY_ONLY"
    h = on_disk["canonical_hash"]
    assert len(h) == 64


def test_committed_artifact_governance_flags_all_false() -> None:
    if not _ARTIFACT_PATH.exists():
        pytest.skip("artifact not yet emitted")
    on_disk = json.loads(_ARTIFACT_PATH.read_text(encoding="utf-8"))
    for v in on_disk["governance_flags"].values():
        assert v is False
