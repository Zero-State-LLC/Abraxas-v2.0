from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.geodesic_computation import (
    COMPUTATION_STAGE,
    COMPUTATION_STATUS,
    OPERATOR_ID,
    RECEIPT_ID,
    SCHEMA_VERSION,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    SOURCE_IMPLEMENTATION_PLAN_HASH,
    GeodesicComputationError,
    _directed_shortest_path,
    build_computation_receipt,
    validate_computation_receipt,
)


# ── algorithm unit tests ───────────────────────────────────────────────────────


def test_simple_shortest_path():
    nodes = ["A", "B", "C"]
    edges = [
        {"from": "A", "to": "B", "weight": 1.0},
        {"from": "B", "to": "C", "weight": 2.0},
        {"from": "A", "to": "C", "weight": 5.0},
    ]
    assert _directed_shortest_path(nodes, edges, "A", "C") == 3.0


def test_self_loop_returns_zero():
    nodes = ["A", "B"]
    edges = [{"from": "A", "to": "B", "weight": 1.0}]
    assert _directed_shortest_path(nodes, edges, "A", "A") == 0.0


def test_multi_hop():
    nodes = ["A", "B", "C", "D"]
    edges = [
        {"from": "A", "to": "B", "weight": 1.0},
        {"from": "B", "to": "C", "weight": 1.0},
        {"from": "C", "to": "D", "weight": 1.0},
        {"from": "A", "to": "D", "weight": 10.0},
        {"from": "B", "to": "D", "weight": 5.0},
    ]
    assert _directed_shortest_path(nodes, edges, "A", "D") == 3.0


def test_no_path_raises():
    nodes = ["A", "B", "C", "D"]
    edges = [
        {"from": "A", "to": "B", "weight": 1.0},
        {"from": "C", "to": "D", "weight": 1.0},
    ]
    with pytest.raises(GeodesicComputationError, match="NO_PATH"):
        _directed_shortest_path(nodes, edges, "A", "D")


def test_direct_edge():
    nodes = ["A", "B", "C", "D", "E"]
    edges = [
        {"from": "A", "to": "B", "weight": 2.0},
        {"from": "A", "to": "E", "weight": 1.5},
        {"from": "B", "to": "E", "weight": 2.0},
    ]
    assert _directed_shortest_path(nodes, edges, "A", "E") == 1.5


# ── build round-trip ───────────────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_computation_receipt(), dict)


def test_schema_version():
    assert build_computation_receipt()["schema_version"] == SCHEMA_VERSION


def test_receipt_id():
    assert build_computation_receipt()["receipt_id"] == RECEIPT_ID


def test_operator_id():
    assert build_computation_receipt()["operator_id"] == OPERATOR_ID


def test_computation_status():
    assert build_computation_receipt()["computation_status"] == COMPUTATION_STATUS


def test_computation_stage():
    assert build_computation_receipt()["computation_stage"] == COMPUTATION_STAGE


def test_intended_lane():
    assert build_computation_receipt()["intended_lane"] == "SHADOW"


def test_source_gate_hash():
    assert (
        build_computation_receipt()["source_implementation_gate_hash"]
        == SOURCE_IMPLEMENTATION_GATE_HASH
    )


def test_source_plan_hash():
    assert (
        build_computation_receipt()["source_implementation_plan_hash"]
        == SOURCE_IMPLEMENTATION_PLAN_HASH
    )


def test_canonical_hash_64_chars():
    h = build_computation_receipt()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    r = build_computation_receipt()
    pre = {k: v for k, v in r.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == r["canonical_hash"]


def test_validate_passes():
    validate_computation_receipt(build_computation_receipt())


def test_replay_stable():
    assert build_computation_receipt() == build_computation_receipt()


def test_recommended_next_step():
    assert (
        build_computation_receipt()["recommended_next_step"]
        == "GEODESIC_COMPUTATION_COMPLETE_REVIEW"
    )


# ── valid fixture results ──────────────────────────────────────────────────────


def test_valid_fixture_count():
    assert len(build_computation_receipt()["valid_fixture_results"]) == 5


def test_all_valid_match():
    vr = build_computation_receipt()["valid_fixture_results"]
    for r in vr:
        assert r["comparison_outcome"] == "MATCH", (
            f"{r['fixture_id']} expected MATCH, got {r['comparison_outcome']}"
        )


def test_valid_001_distance():
    vr = build_computation_receipt()["valid_fixture_results"]
    r = next(x for x in vr if "valid_001" in x["fixture_id"])
    assert r["computed_geodesic_distance"] == 3.0
    assert r["expected_geodesic_distance"] == 3.0


def test_valid_002_distance():
    vr = build_computation_receipt()["valid_fixture_results"]
    r = next(x for x in vr if "valid_002" in x["fixture_id"])
    assert r["computed_geodesic_distance"] == 3.0
    assert r["expected_geodesic_distance"] == 3.0


def test_valid_003_self_loop_distance():
    vr = build_computation_receipt()["valid_fixture_results"]
    r = next(x for x in vr if "valid_003" in x["fixture_id"])
    assert r["computed_geodesic_distance"] == 0.0
    assert r["expected_geodesic_distance"] == 0.0


def test_valid_004_distance():
    vr = build_computation_receipt()["valid_fixture_results"]
    r = next(x for x in vr if "valid_004" in x["fixture_id"])
    assert r["computed_geodesic_distance"] == 3.0
    assert r["expected_geodesic_distance"] == 3.0


def test_valid_005_distance():
    vr = build_computation_receipt()["valid_fixture_results"]
    r = next(x for x in vr if "valid_005" in x["fixture_id"])
    assert r["computed_geodesic_distance"] == 1.5
    assert r["expected_geodesic_distance"] == 1.5


def test_valid_no_metric_emitted():
    for r in build_computation_receipt()["valid_fixture_results"]:
        assert r["metric_emitted"] is False


def test_valid_no_forecast_influenced():
    for r in build_computation_receipt()["valid_fixture_results"]:
        assert r["forecast_influenced"] is False


def test_valid_outcome_computed():
    for r in build_computation_receipt()["valid_fixture_results"]:
        assert r["computation_outcome"] == "COMPUTED"


def test_valid_fixture_hashes_present():
    for r in build_computation_receipt()["valid_fixture_results"]:
        h = r.get("fixture_canonical_hash", "")
        assert isinstance(h, str) and len(h) == 64


# ── invalid fixture results ────────────────────────────────────────────────────


def test_invalid_fixture_count():
    assert len(build_computation_receipt()["invalid_fixture_results"]) == 4


def test_invalid_all_rejection_outcome():
    for r in build_computation_receipt()["invalid_fixture_results"]:
        assert r["rejection_outcome"] == "INVALID_INPUT"


def test_invalid_computation_not_attempted():
    for r in build_computation_receipt()["invalid_fixture_results"]:
        assert r["computation_attempted"] is False


def test_invalid_no_metric_emitted():
    for r in build_computation_receipt()["invalid_fixture_results"]:
        assert r["metric_emitted"] is False


def test_invalid_001_reason():
    ir = build_computation_receipt()["invalid_fixture_results"]
    r = next(x for x in ir if "invalid_001" in x["fixture_id"])
    assert "source_node" in r["rejection_reason"]


def test_invalid_002_reason():
    ir = build_computation_receipt()["invalid_fixture_results"]
    r = next(x for x in ir if "invalid_002" in x["fixture_id"])
    assert "target_node" in r["rejection_reason"]


def test_invalid_003_reason():
    ir = build_computation_receipt()["invalid_fixture_results"]
    r = next(x for x in ir if "invalid_003" in x["fixture_id"])
    assert "edge_list" in r["rejection_reason"]


def test_invalid_fixture_hashes_present():
    for r in build_computation_receipt()["invalid_fixture_results"]:
        h = r.get("fixture_canonical_hash", "")
        assert isinstance(h, str) and len(h) == 64


# ── not_computable fixture results ─────────────────────────────────────────────


def test_nc_fixture_count():
    assert len(build_computation_receipt()["not_computable_fixture_results"]) == 4


def test_nc_all_not_computable_outcome():
    for r in build_computation_receipt()["not_computable_fixture_results"]:
        assert r["not_computable_outcome"] == "NOT_COMPUTABLE"


def test_nc_computation_not_attempted():
    for r in build_computation_receipt()["not_computable_fixture_results"]:
        assert r["computation_attempted"] is False


def test_nc_no_metric_emitted():
    for r in build_computation_receipt()["not_computable_fixture_results"]:
        assert r["metric_emitted"] is False


def test_nc_001_empty_input():
    nc = build_computation_receipt()["not_computable_fixture_results"]
    r = next(x for x in nc if "nc_001" in x["fixture_id"])
    assert r["not_computable_reason"] == "EMPTY_INPUT"


def test_nc_002_disconnected():
    nc = build_computation_receipt()["not_computable_fixture_results"]
    r = next(x for x in nc if "nc_002" in x["fixture_id"])
    assert r["not_computable_reason"] == "DISCONNECTED_GRAPH"


def test_nc_003_source_not_in_graph():
    nc = build_computation_receipt()["not_computable_fixture_results"]
    r = next(x for x in nc if "nc_003" in x["fixture_id"])
    assert r["not_computable_reason"] == "SOURCE_NODE_NOT_IN_GRAPH"


def test_nc_004_target_not_in_graph():
    nc = build_computation_receipt()["not_computable_fixture_results"]
    r = next(x for x in nc if "nc_004" in x["fixture_id"])
    assert r["not_computable_reason"] == "TARGET_NODE_NOT_IN_GRAPH"


def test_nc_fixture_hashes_present():
    for r in build_computation_receipt()["not_computable_fixture_results"]:
        h = r.get("fixture_canonical_hash", "")
        assert isinstance(h, str) and len(h) == 64


# ── comparison summary ─────────────────────────────────────────────────────────


def test_comparison_summary_all_match():
    cs = build_computation_receipt()["comparison_summary"]
    assert cs["all_valid_match"] is True


def test_comparison_summary_match_count():
    cs = build_computation_receipt()["comparison_summary"]
    assert cs["match_count"] == 5


def test_comparison_summary_mismatch_zero():
    cs = build_computation_receipt()["comparison_summary"]
    assert cs["mismatch_count"] == 0


def test_comparison_summary_total():
    cs = build_computation_receipt()["comparison_summary"]
    assert cs["total_valid_fixtures"] == 5


# ── numerical policy ───────────────────────────────────────────────────────────


def test_numerical_policy_negative_weight():
    np_ = build_computation_receipt()["numerical_policy"]
    assert np_["negative_weight_policy"] == "REJECT_AS_INVALID_INPUT"


def test_numerical_policy_self_loop():
    np_ = build_computation_receipt()["numerical_policy"]
    assert np_["self_loop_policy"] == "ZERO_DISTANCE_IF_SOURCE_EQUALS_TARGET"


# ── block reviews ──────────────────────────────────────────────────────────────


def test_no_metric_emission_review_passed():
    b = build_computation_receipt()["no_metric_emission_review"]
    assert b["emits_metric_values"] is False
    assert b["review_passed"] is True


def test_no_forecast_influence_review_passed():
    b = build_computation_receipt()["no_forecast_influence_review"]
    assert b["forecast_influence"] is False
    assert b["review_passed"] is True


def test_no_p43_review_passed():
    b = build_computation_receipt()["no_p43_surface_lane_review"]
    assert b["p43_surface_lanes_authorized"] is False
    assert b["review_passed"] is True


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_computation_receipt()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False"


# ── authority locks ────────────────────────────────────────────────────────────


def test_lock_advisory_only():
    assert build_computation_receipt()["authority_locks"]["advisory_only"] is True


def test_lock_shadow_lane_only():
    assert build_computation_receipt()["authority_locks"]["shadow_lane_only"] is True


def test_lock_test_vector_computation_only():
    assert (
        build_computation_receipt()["authority_locks"]["test_vector_computation_only"] is True
    )


def test_lock_geodesic_computation_authorized():
    assert (
        build_computation_receipt()["authority_locks"][
            "geodesic_computation_implementation_authorized"
        ]
        is True
    )


def test_lock_emits_metric_values_false():
    assert build_computation_receipt()["authority_locks"]["emits_metric_values"] is False


def test_lock_execution_authority_false():
    assert build_computation_receipt()["authority_locks"]["execution_authority"] is False


def test_lock_production_activation_false():
    assert build_computation_receipt()["authority_locks"]["production_activation"] is False


# ── validate rejects bad inputs ────────────────────────────────────────────────


def test_validate_rejects_wrong_schema():
    r = build_computation_receipt()
    r["schema_version"] = "Wrong.v1"
    with pytest.raises(GeodesicComputationError):
        validate_computation_receipt(r)


def test_validate_rejects_wrong_status():
    r = build_computation_receipt()
    r["computation_status"] = "WRONG"
    with pytest.raises(GeodesicComputationError):
        validate_computation_receipt(r)


def test_validate_rejects_hash_mismatch():
    r = build_computation_receipt()
    r["canonical_hash"] = "a" * 64
    with pytest.raises(GeodesicComputationError):
        validate_computation_receipt(r)


def test_validate_rejects_mismatch_count_nonzero():
    r = build_computation_receipt()
    r["comparison_summary"]["mismatch_count"] = 1
    r["comparison_summary"]["all_valid_match"] = False
    h = canonical_hash({k: v for k, v in r.items() if k != "canonical_hash"})
    r["canonical_hash"] = h
    with pytest.raises(GeodesicComputationError):
        validate_computation_receipt(r)


def test_validate_rejects_execution_authority_true():
    r = build_computation_receipt()
    r["authority_locks"]["execution_authority"] = True
    h = canonical_hash({k: v for k, v in r.items() if k != "canonical_hash"})
    r["canonical_hash"] = h
    with pytest.raises(GeodesicComputationError):
        validate_computation_receipt(r)
