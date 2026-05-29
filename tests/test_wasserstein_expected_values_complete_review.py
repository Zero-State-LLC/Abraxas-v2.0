from __future__ import annotations

import pytest

from core.wasserstein_expected_values_complete_review import (
    EXPECTED_WASSERSTEIN_DISTANCES,
    INVALID_FIXTURE_FILES,
    NC_FIXTURE_FILES,
    SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH,
    SOURCE_EXPECTED_VALUES_GATE_HASH,
    VALID_FIXTURE_FILES,
    WassersteinExpectedValuesCompleteReviewError,
    build_authority_lock_review,
    build_expected_value_addition_review,
    build_invalid_fixture_exclusion_review,
    build_no_forecast_influence_review,
    build_no_metric_emission_review,
    build_no_p43_surface_lane_review,
    build_not_computable_fixture_exclusion_review,
    build_review_summary,
    build_valid_fixture_review,
    build_wasserstein_expected_values_complete_review,
    compute_wasserstein_expected_values_complete_review_hash,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_expected_values_complete_review,
)


def _payload() -> dict:
    return {
        "review_id": "wasserstein_expected_values_complete_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "EXPECTED_VALUES_COMPLETE_REVIEW_ONLY",
        "expected_value_addition_review": build_expected_value_addition_review(),
        "valid_fixture_review": build_valid_fixture_review(),
        "invalid_fixture_exclusion_review": build_invalid_fixture_exclusion_review(),
        "not_computable_fixture_exclusion_review": (
            build_not_computable_fixture_exclusion_review()
        ),
        "no_metric_emission_review": build_no_metric_emission_review(),
        "no_forecast_influence_review": build_no_forecast_influence_review(),
        "no_p43_surface_lane_review": build_no_p43_surface_lane_review(),
        "authority_lock_review": build_authority_lock_review(),
        "review_summary": build_review_summary(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_EXPECTED_VALUES_PHASE_COMPLETE",
        "provenance": {
            "source": "P61_WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW",
            "evidence_refs": [
                "WassersteinExpectedValuesAdditionReceipt.v1:"
                "wasserstein_expected_values_addition_receipt_001",
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


def test_source_addition_receipt_hash_correct() -> None:
    assert (
        SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH
        == "5c09ec19953914d2e5072b5abe2ae51c1482cd8d1a671874cbc7f7bb110db131"
    )


def test_source_gate_hash_correct() -> None:
    assert (
        SOURCE_EXPECTED_VALUES_GATE_HASH
        == "21baf9d688ba3ec0590e14355e26d043b48693ac71ecdb0d69da0afcf3b09bb2"
    )


def test_fixture_file_counts() -> None:
    assert len(VALID_FIXTURE_FILES) == 5
    assert len(INVALID_FIXTURE_FILES) == 5
    assert len(NC_FIXTURE_FILES) == 4


# ---------------------------------------------------------------------------
# build_expected_value_addition_review
# ---------------------------------------------------------------------------


def test_expected_value_addition_review_verified() -> None:
    r = build_expected_value_addition_review()
    assert r["addition_review_status"] == "EXPECTED_VALUE_ADDITION_VERIFIED"


def test_expected_value_addition_review_all_added() -> None:
    r = build_expected_value_addition_review()
    assert r["all_expected_values_added"] is True
    assert r["expected_values_match_receipt_manifest"] is True
    assert r["total_valid_fixtures"] == 5


def test_expected_value_addition_review_fixture_checks() -> None:
    r = build_expected_value_addition_review()
    assert len(r["fixture_checks"]) == 5
    for fc in r["fixture_checks"]:
        assert fc["check_status"] == "VERIFIED"
        assert fc["expected_wasserstein_distance_included"] is True
        assert fc["expected_wasserstein_distance_value_verified"] is True
        assert fc["source_expected_values_gate_hash_verified"] is True


@pytest.mark.parametrize("fixture_id", sorted(EXPECTED_WASSERSTEIN_DISTANCES))
def test_expected_value_addition_review_per_fixture(fixture_id: str) -> None:
    r = build_expected_value_addition_review()
    fc = next(x for x in r["fixture_checks"] if x["fixture_id"] == fixture_id)
    assert fc["check_status"] == "VERIFIED"


# ---------------------------------------------------------------------------
# build_valid_fixture_review
# ---------------------------------------------------------------------------


def test_valid_fixture_review_status() -> None:
    r = build_valid_fixture_review()
    assert r["review_status"] == "VALID_FIXTURES_REVIEW_VERIFIED"
    assert r["total_reviewed"] == 5
    assert r["all_verified"] is True


def test_valid_fixture_review_entries() -> None:
    r = build_valid_fixture_review()
    assert len(r["fixture_entries"]) == 5
    for entry in r["fixture_entries"]:
        assert entry["review_status"] == "VERIFIED"
        assert entry["metric_value_emitted_verified"] is True
        assert entry["intended_lane_verified"] is True
        assert entry["fixture_type_verified"] is True


# ---------------------------------------------------------------------------
# build_invalid_fixture_exclusion_review
# ---------------------------------------------------------------------------


def test_invalid_fixture_exclusion_review_status() -> None:
    r = build_invalid_fixture_exclusion_review()
    assert r["exclusion_review_status"] == "INVALID_FIXTURES_EXCLUDED_VERIFIED"
    assert r["invalid_count"] == 5
    assert r["all_excluded_unchanged"] is True


def test_invalid_fixture_exclusion_review_no_expected_distance() -> None:
    r = build_invalid_fixture_exclusion_review()
    for entry in r["fixture_entries"]:
        assert entry["expected_wasserstein_distance_present"] is False
        assert entry["fixture_unchanged"] is True
        assert entry["check_status"] == "EXCLUDED_VERIFIED"


# ---------------------------------------------------------------------------
# build_not_computable_fixture_exclusion_review
# ---------------------------------------------------------------------------


def test_not_computable_fixture_exclusion_review_status() -> None:
    r = build_not_computable_fixture_exclusion_review()
    assert (
        r["exclusion_review_status"] == "NOT_COMPUTABLE_FIXTURES_EXCLUDED_VERIFIED"
    )
    assert r["not_computable_count"] == 4
    assert r["all_excluded_unchanged"] is True


def test_not_computable_fixture_exclusion_review_no_expected_distance() -> None:
    r = build_not_computable_fixture_exclusion_review()
    for entry in r["fixture_entries"]:
        assert entry["expected_wasserstein_distance_present"] is False
        assert entry["fixture_unchanged"] is True
        assert entry["check_status"] == "EXCLUDED_VERIFIED"


# ---------------------------------------------------------------------------
# Review sections
# ---------------------------------------------------------------------------


def test_no_metric_emission_review_verified() -> None:
    r = build_no_metric_emission_review()
    assert r["review_status"] == "NO_METRIC_EMISSION_VERIFIED"
    assert r["emits_metric_values"] is False
    assert r["no_runtime_emission"] is True
    assert r["no_p43_surface_output"] is True


def test_no_forecast_influence_review_verified() -> None:
    r = build_no_forecast_influence_review()
    assert r["review_status"] == "NO_FORECAST_INFLUENCE_VERIFIED"
    assert r["forecast_influence"] is False
    assert r["no_forecast_binding"] is True
    assert r["no_p43_output"] is True


def test_no_p43_surface_lane_review_verified() -> None:
    r = build_no_p43_surface_lane_review()
    assert r["review_status"] == "NO_P43_SURFACE_LANE_VERIFIED"
    assert r["p43_surface_lanes_authorized"] is False
    assert r["no_p43_lanes_opened"] is True
    assert r["no_runtime_binding"] is True


def test_authority_lock_review_verified() -> None:
    r = build_authority_lock_review()
    assert r["review_status"] == "AUTHORITY_LOCKS_VERIFIED"
    assert r["advisory_only_verified"] is True
    assert r["shadow_lane_only_verified"] is True
    assert r["expected_values_complete_review_only_verified"] is True
    assert r["expected_wasserstein_distances_authorized_verified"] is True
    assert r["emits_metric_values_false_verified"] is True
    assert r["execution_authority_false_verified"] is True


def test_review_summary_all_sections_verified() -> None:
    r = build_review_summary()
    assert r["overall_status"] == "WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW_VERIFIED"
    assert r["sections_verified"] == 8
    assert r["total_review_sections"] == 8


# ---------------------------------------------------------------------------
# Full build
# ---------------------------------------------------------------------------


def test_build_packet_schema_version() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    assert pkt["schema_version"] == "WassersteinExpectedValuesCompleteReview.v1"


def test_build_packet_review_type() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    assert pkt["review_type"] == "WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW"


def test_build_packet_constants() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    assert pkt["operator_id"] == "WASSERSTEIN"
    assert (
        pkt["source_expected_values_addition_receipt_hash"]
        == SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH
    )
    assert (
        pkt["source_expected_values_gate_hash"] == SOURCE_EXPECTED_VALUES_GATE_HASH
    )
    assert pkt["intended_lane"] == "SHADOW"
    assert pkt["review_stage"] == "EXPECTED_VALUES_COMPLETE_REVIEW_ONLY"


def test_build_packet_authority_locks_complete_review_only() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    assert pkt["authority_locks"]["expected_values_complete_review_only"] is True


def test_build_packet_expected_wasserstein_distances_authorized() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    assert pkt["authority_locks"]["expected_wasserstein_distances_authorized"] is True


def test_build_packet_emits_metric_values_false() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    assert pkt["authority_locks"]["emits_metric_values"] is False


def test_build_packet_execution_authority_false() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    assert pkt["authority_locks"]["execution_authority"] is False


def test_build_packet_blocked_scopes_all_false() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    for k, v in pkt["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_build_packet_has_canonical_hash() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    assert "canonical_hash" in pkt
    assert len(pkt["canonical_hash"]) == 64


def test_build_packet_recommended_next_step() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    assert pkt["recommended_next_step"] == "WASSERSTEIN_EXPECTED_VALUES_PHASE_COMPLETE"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash() -> None:
    a = build_wasserstein_expected_values_complete_review(_payload())
    b = build_wasserstein_expected_values_complete_review(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_deterministic_serialization() -> None:
    a = build_wasserstein_expected_values_complete_review(_payload())
    b = build_wasserstein_expected_values_complete_review(_payload())
    assert serialize_wasserstein_expected_values_complete_review(
        a
    ) == serialize_wasserstein_expected_values_complete_review(b)


def test_hash_excludes_itself() -> None:
    pkt = build_wasserstein_expected_values_complete_review(_payload())
    altered = dict(pkt)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_expected_values_complete_review_hash(pkt)
        == compute_wasserstein_expected_values_complete_review_hash(altered)
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_expected_values_complete_review(_payload())
    b = build_wasserstein_expected_values_complete_review(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


# ---------------------------------------------------------------------------
# Validation failures
# ---------------------------------------------------------------------------


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["review_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_expected_values_complete_review(p)


def test_authority_locks_emits_metric_values_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="emits_metric_values_must_be_false"):
        build_wasserstein_expected_values_complete_review(p)


def test_expected_values_complete_review_only_false_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["expected_values_complete_review_only"] = False
    p["authority_locks"] = al
    with pytest.raises(
        ValueError, match="expected_values_complete_review_only_must_be_true"
    ):
        build_wasserstein_expected_values_complete_review(p)


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    bs = default_blocked_scopes()
    bs["canon_promotion"] = True
    p["blocked_scopes"] = bs
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_expected_values_complete_review(p)


def test_provenance_forbidden_reference_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring metric-value authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_expected_values_complete_review(p)


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("review_stage", "ACTIVE", "unknown_review_stage"),
    ],
)
def test_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_expected_values_complete_review(p)


def test_no_metric_emission_review_mutation_raises() -> None:
    p = _payload()
    nmer = build_no_metric_emission_review()
    nmer["emits_metric_values"] = True
    p["no_metric_emission_review"] = nmer
    with pytest.raises(
        WassersteinExpectedValuesCompleteReviewError,
        match="no_metric_emission_review_emits_metric_values_not_false",
    ):
        build_wasserstein_expected_values_complete_review(p)


def test_no_forecast_influence_review_mutation_raises() -> None:
    p = _payload()
    nfir = build_no_forecast_influence_review()
    nfir["forecast_influence"] = True
    p["no_forecast_influence_review"] = nfir
    with pytest.raises(
        WassersteinExpectedValuesCompleteReviewError,
        match="no_forecast_influence_review_forecast_influence_not_false",
    ):
        build_wasserstein_expected_values_complete_review(p)


def test_no_p43_surface_lane_review_mutation_raises() -> None:
    p = _payload()
    np43r = build_no_p43_surface_lane_review()
    np43r["p43_surface_lanes_authorized"] = True
    p["no_p43_surface_lane_review"] = np43r
    with pytest.raises(
        WassersteinExpectedValuesCompleteReviewError,
        match="no_p43_surface_lane_review_p43_lanes_not_false",
    ):
        build_wasserstein_expected_values_complete_review(p)
