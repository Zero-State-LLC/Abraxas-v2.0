from __future__ import annotations

import pytest

from core.wasserstein_expected_values_gate import (
    INVALID_FIXTURE_IDS,
    NC_FIXTURE_IDS,
    SHADOW_TRANSPORT_VALUES,
    SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    WassersteinExpectedValuesGateError,
    build_expected_value_authorization_scope,
    build_forecast_influence_block,
    build_metric_emission_block,
    build_p43_surface_lane_block,
    build_rejected_input_exclusion_scope,
    build_valid_fixture_result_review,
    build_wasserstein_expected_values_gate,
    compute_wasserstein_expected_values_gate_hash,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_expected_values_gate,
)


def _payload() -> dict:
    return {
        "gate_id": "wasserstein_expected_values_gate_001",
        "intended_lane": "SHADOW",
        "gate_stage": "EXPECTED_VALUES_GATE_ONLY",
        "valid_fixture_result_review": build_valid_fixture_result_review(),
        "expected_value_authorization_scope": build_expected_value_authorization_scope(),
        "rejected_input_exclusion_scope": build_rejected_input_exclusion_scope(),
        "metric_emission_block": build_metric_emission_block(),
        "forecast_influence_block": build_forecast_influence_block(),
        "p43_surface_lane_block": build_p43_surface_lane_block(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_EXPECTED_VALUES_ADDITION",
        "provenance": {
            "source": "P59_WASSERSTEIN_EXPECTED_VALUES_GATE",
            "evidence_refs": [
                "WassersteinTestVectorComputationCompleteReview.v1:"
                "wasserstein_test_vector_computation_complete_review_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_expected_values_gate.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Source constants
# ---------------------------------------------------------------------------


def test_source_hashes_correct() -> None:
    assert (
        SOURCE_COMPUTATION_RECEIPT_HASH
        == "010da2fdf344cfc32d2e9accc0ef19e96644fdd69974928ca047f87e4daf6188"
    )
    assert (
        SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH
        == "8d37688fb2f4c0337cdfb2cf2ab3fb491138cbd7c1f66eca87b476bd45a60079"
    )


def test_shadow_transport_values_present() -> None:
    assert len(SHADOW_TRANSPORT_VALUES) == 5
    assert abs(SHADOW_TRANSPORT_VALUES["valid-001"] - 0.4) < 1e-9
    assert abs(SHADOW_TRANSPORT_VALUES["valid-002"] - 0.4) < 1e-9
    assert abs(SHADOW_TRANSPORT_VALUES["valid-003"] - 0.866025) < 1e-6
    assert abs(SHADOW_TRANSPORT_VALUES["valid-004"] - 0.2) < 1e-9
    assert abs(SHADOW_TRANSPORT_VALUES["valid-005"]) < 1e-9


def test_excluded_fixture_counts() -> None:
    assert len(INVALID_FIXTURE_IDS) == 5
    assert len(NC_FIXTURE_IDS) == 4


# ---------------------------------------------------------------------------
# build_valid_fixture_result_review
# ---------------------------------------------------------------------------


def test_valid_fixture_result_review_gate_status() -> None:
    r = build_valid_fixture_result_review()
    assert r["gate_status"] == "VALID_FIXTURES_AUTHORIZED_FOR_EXPECTED_VALUES"


def test_valid_fixture_result_review_total() -> None:
    r = build_valid_fixture_result_review()
    assert r["total_reviewed"] == 5


def test_valid_fixture_result_review_all_eligible() -> None:
    r = build_valid_fixture_result_review()
    assert r["all_eligible_for_expected_distance"] is True
    assert r["all_shadow_transport_values_verified"] is True


def test_valid_fixture_result_review_scope() -> None:
    r = build_valid_fixture_result_review()
    assert r["expected_distance_scope"] == "SHADOW_ONLY"


def test_valid_fixture_result_review_fixture_reviews() -> None:
    r = build_valid_fixture_result_review()
    assert len(r["fixture_reviews"]) == 5
    for fr in r["fixture_reviews"]:
        assert fr["gate_status"] == "AUTHORIZED"
        assert fr["eligible_for_expected_distance"] is True
        assert fr["expected_distance_scope"] == "SHADOW_ONLY"
        assert fr["shadow_transport_value_verified"] is True


def test_valid_fixture_result_review_all_shadow_values() -> None:
    r = build_valid_fixture_result_review()
    observed = {
        fr["fixture_id"]: fr["shadow_transport_value"]
        for fr in r["fixture_reviews"]
    }
    for fid, expected in SHADOW_TRANSPORT_VALUES.items():
        assert abs(observed[fid] - expected) < 1e-9


# ---------------------------------------------------------------------------
# build_expected_value_authorization_scope
# ---------------------------------------------------------------------------


def test_expected_value_authorization_scope_status() -> None:
    r = build_expected_value_authorization_scope()
    assert r["authorization_status"] == "EXPECTED_WASSERSTEIN_DISTANCES_AUTHORIZED"


def test_expected_value_authorization_scope_valid_only() -> None:
    r = build_expected_value_authorization_scope()
    assert r["scope"] == "VALID_FIXTURES_ONLY"
    assert r["fixture_count"] == 5
    assert len(r["authorized_fixture_ids"]) == 5


def test_expected_value_authorization_scope_shadow_only() -> None:
    r = build_expected_value_authorization_scope()
    assert r["shadow_only"] is True
    assert r["no_metric_emission"] is True
    assert r["no_forecast_influence"] is True
    assert r["no_p43_output"] is True
    assert r["no_runtime_binding"] is True


def test_expected_value_authorization_scope_action() -> None:
    r = build_expected_value_authorization_scope()
    assert r["authorized_action"] == "ADD_EXPECTED_WASSERSTEIN_DISTANCE"


# ---------------------------------------------------------------------------
# build_rejected_input_exclusion_scope
# ---------------------------------------------------------------------------


def test_rejected_input_exclusion_scope_status() -> None:
    r = build_rejected_input_exclusion_scope()
    assert r["exclusion_status"] == "REJECTED_INPUT_FIXTURES_EXCLUDED"


def test_rejected_input_exclusion_scope_counts() -> None:
    r = build_rejected_input_exclusion_scope()
    assert r["invalid_count"] == 5
    assert r["not_computable_count"] == 4
    assert len(r["invalid_fixture_ids"]) == 5
    assert len(r["nc_fixture_ids"]) == 4


def test_rejected_input_exclusion_scope_excluded() -> None:
    r = build_rejected_input_exclusion_scope()
    assert r["expected_distance_excluded"] is True


# ---------------------------------------------------------------------------
# Block sections
# ---------------------------------------------------------------------------


def test_metric_emission_block_blocked() -> None:
    r = build_metric_emission_block()
    assert r["block_status"] == "BLOCKED"
    assert r["emits_metric_values"] is False
    assert r["no_runtime_emission"] is True
    assert r["no_p43_surface_output"] is True


def test_forecast_influence_block_blocked() -> None:
    r = build_forecast_influence_block()
    assert r["block_status"] == "BLOCKED"
    assert r["forecast_influence"] is False
    assert r["no_forecast_binding"] is True


def test_p43_surface_lane_block_blocked() -> None:
    r = build_p43_surface_lane_block()
    assert r["block_status"] == "BLOCKED"
    assert r["p43_surface_lanes_authorized"] is False
    assert r["no_p43_lanes_opened"] is True


# ---------------------------------------------------------------------------
# Full build
# ---------------------------------------------------------------------------


def test_build_packet_schema_version() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    assert pkt["schema_version"] == "WassersteinExpectedValuesGate.v1"


def test_build_packet_gate_type() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    assert pkt["gate_type"] == "WASSERSTEIN_EXPECTED_VALUES_GATE"


def test_build_packet_constants() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    assert pkt["operator_id"] == "WASSERSTEIN"
    assert pkt["source_computation_receipt_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH
    assert (
        pkt["source_computation_complete_review_hash"]
        == SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH
    )
    assert pkt["intended_lane"] == "SHADOW"
    assert pkt["gate_stage"] == "EXPECTED_VALUES_GATE_ONLY"


def test_build_packet_authority_locks_expected_values_gate() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    assert pkt["authority_locks"]["expected_values_gate_only"] is True


def test_build_packet_expected_wasserstein_distances_authorized() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    assert pkt["authority_locks"]["expected_wasserstein_distances_authorized"] is True


def test_build_packet_emits_metric_values_false() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    assert pkt["authority_locks"]["emits_metric_values"] is False


def test_build_packet_execution_authority_false() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    assert pkt["authority_locks"]["execution_authority"] is False


def test_build_packet_blocked_scopes_all_false() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    for k, v in pkt["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_build_packet_has_canonical_hash() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    assert "canonical_hash" in pkt
    assert len(pkt["canonical_hash"]) == 64


def test_build_packet_recommended_next_step() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    assert pkt["recommended_next_step"] == "WASSERSTEIN_EXPECTED_VALUES_ADDITION"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash() -> None:
    a = build_wasserstein_expected_values_gate(_payload())
    b = build_wasserstein_expected_values_gate(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_deterministic_serialization() -> None:
    a = build_wasserstein_expected_values_gate(_payload())
    b = build_wasserstein_expected_values_gate(_payload())
    assert serialize_wasserstein_expected_values_gate(
        a
    ) == serialize_wasserstein_expected_values_gate(b)


def test_hash_excludes_itself() -> None:
    pkt = build_wasserstein_expected_values_gate(_payload())
    altered = dict(pkt)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_expected_values_gate_hash(pkt)
        == compute_wasserstein_expected_values_gate_hash(altered)
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_expected_values_gate(_payload())
    b = build_wasserstein_expected_values_gate(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


# ---------------------------------------------------------------------------
# Validation failures
# ---------------------------------------------------------------------------


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["gate_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_expected_values_gate(p)


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="emits_metric_values_must_be_false"):
        build_wasserstein_expected_values_gate(p)


def test_expected_values_gate_only_false_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["expected_values_gate_only"] = False
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="expected_values_gate_only_must_be_true"):
        build_wasserstein_expected_values_gate(p)


def test_expected_wasserstein_distances_authorized_false_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["expected_wasserstein_distances_authorized"] = False
    p["authority_locks"] = al
    with pytest.raises(
        ValueError, match="expected_wasserstein_distances_authorized_must_be_true"
    ):
        build_wasserstein_expected_values_gate(p)


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    bs = default_blocked_scopes()
    bs["forecast_influence"] = True
    p["blocked_scopes"] = bs
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_expected_values_gate(p)


def test_provenance_forbidden_reference_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring metric-value authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_expected_values_gate(p)


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("gate_stage", "ACTIVE", "unknown_gate_stage"),
    ],
)
def test_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_expected_values_gate(p)


def test_metric_emission_block_mutation_raises() -> None:
    p = _payload()
    meb = build_metric_emission_block()
    meb["emits_metric_values"] = True
    p["metric_emission_block"] = meb
    with pytest.raises(
        WassersteinExpectedValuesGateError,
        match="metric_emission_block_emits_metric_values_not_false",
    ):
        build_wasserstein_expected_values_gate(p)


def test_forecast_influence_block_mutation_raises() -> None:
    p = _payload()
    fib = build_forecast_influence_block()
    fib["forecast_influence"] = True
    p["forecast_influence_block"] = fib
    with pytest.raises(
        WassersteinExpectedValuesGateError,
        match="forecast_influence_block_forecast_influence_not_false",
    ):
        build_wasserstein_expected_values_gate(p)


def test_p43_surface_lane_block_mutation_raises() -> None:
    p = _payload()
    p43b = build_p43_surface_lane_block()
    p43b["p43_surface_lanes_authorized"] = True
    p["p43_surface_lane_block"] = p43b
    with pytest.raises(
        WassersteinExpectedValuesGateError,
        match="p43_surface_lane_block_not_false",
    ):
        build_wasserstein_expected_values_gate(p)
