from __future__ import annotations

import json
import pathlib

import pytest

from core.wasserstein_test_vector_computation_complete_review import (
    SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    WassersteinComputationCompleteReviewError,
    build_authority_lock_review,
    build_computation_completion_summary,
    build_no_forecast_influence_review,
    build_no_metric_value_emission_review,
    build_no_p43_surface_lane_review,
    build_rejected_input_result_review,
    build_shadow_transport_value_review,
    build_valid_fixture_result_review,
    build_wasserstein_test_vector_computation_complete_review,
    compute_wasserstein_test_vector_computation_complete_review_hash,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_test_vector_computation_complete_review,
)

# ---------------------------------------------------------------------------
# Test data derived from the committed computation receipt
# ---------------------------------------------------------------------------

_RECEIPT_PATH = (
    "out/projections/wasserstein_test_vector_computation_receipt_001.latest.json"
)


def _load_receipt() -> dict:
    return json.loads(pathlib.Path(_RECEIPT_PATH).read_text(encoding="utf-8"))


_RECEIPT = _load_receipt()
_VALID_RESULTS = _RECEIPT["valid_fixture_results"]
_INVALID_RESULTS = _RECEIPT["invalid_fixture_results"]
_NC_RESULTS = _RECEIPT["not_computable_fixture_results"]


def _payload(receipt: dict | None = None) -> dict:
    r = receipt if receipt is not None else _RECEIPT
    vfr = build_valid_fixture_result_review(r["valid_fixture_results"])
    rir = build_rejected_input_result_review(
        r["invalid_fixture_results"], r["not_computable_fixture_results"]
    )
    stvr = build_shadow_transport_value_review(r["valid_fixture_results"])
    nmver = build_no_metric_value_emission_review(r)
    nfir = build_no_forecast_influence_review(r)
    np43r = build_no_p43_surface_lane_review(r)
    alr = build_authority_lock_review(r)
    ccs = build_computation_completion_summary(r)
    return {
        "review_id": "wasserstein_test_vector_computation_complete_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW_ONLY",
        "valid_fixture_result_review": vfr,
        "rejected_input_result_review": rir,
        "shadow_transport_value_review": stvr,
        "no_metric_value_emission_review": nmver,
        "no_forecast_influence_review": nfir,
        "no_p43_surface_lane_review": np43r,
        "authority_lock_review": alr,
        "computation_completion_summary": ccs,
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_EXPECTED_VALUES_GATE",
        "provenance": {
            "source": "P58_WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW",
            "evidence_refs": [
                "WassersteinTestVectorComputationReceipt.v1:"
                "wasserstein_test_vector_computation_receipt_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_computation_complete_review.v1.schema.json",
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
        SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH
        == "3ac3aeccdb5521db58f0fbadac8fa6e3641d1f8fb8daec8fe98d1fcafe575d65"
    )


# ---------------------------------------------------------------------------
# build_valid_fixture_result_review
# ---------------------------------------------------------------------------


def test_valid_fixture_result_review_status() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["review_status"] == "VALID_FIXTURE_RESULTS_VERIFIED"


def test_valid_fixture_result_review_total() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["total_reviewed"] == 5


def test_valid_fixture_result_review_all_shadow_transport_value() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["all_have_shadow_transport_value"] is True


def test_valid_fixture_result_review_all_shadow_lane() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["all_shadow_lane"] is True


def test_valid_fixture_result_review_no_metric_values() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["no_metric_values_emitted"] is True


def test_valid_fixture_result_review_fixture_reviews_count() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert len(r["fixture_reviews"]) == 5
    for fr in r["fixture_reviews"]:
        assert fr["review_status"] == "PASS"
        assert fr["shadow_transport_value_present"] is True
        assert fr["metric_value_emitted"] is False


# ---------------------------------------------------------------------------
# build_rejected_input_result_review
# ---------------------------------------------------------------------------


def test_rejected_input_result_review_status() -> None:
    r = build_rejected_input_result_review(_INVALID_RESULTS, _NC_RESULTS)
    assert r["review_status"] == "REJECTED_INPUT_RESULTS_VERIFIED"


def test_rejected_input_result_review_total() -> None:
    r = build_rejected_input_result_review(_INVALID_RESULTS, _NC_RESULTS)
    assert r["total_reviewed"] == 9
    assert r["invalid_reviewed"] == 5
    assert r["not_computable_reviewed"] == 4


def test_rejected_input_result_review_no_metric_values() -> None:
    r = build_rejected_input_result_review(_INVALID_RESULTS, _NC_RESULTS)
    assert r["no_metric_values_emitted"] is True


def test_rejected_input_result_review_all_pass() -> None:
    r = build_rejected_input_result_review(_INVALID_RESULTS, _NC_RESULTS)
    assert len(r["fixture_reviews"]) == 9
    for fr in r["fixture_reviews"]:
        assert fr["review_status"] == "PASS"


# ---------------------------------------------------------------------------
# build_shadow_transport_value_review
# ---------------------------------------------------------------------------


def test_shadow_transport_value_review_status() -> None:
    r = build_shadow_transport_value_review(_VALID_RESULTS)
    assert r["review_status"] == "SHADOW_TRANSPORT_VALUES_VERIFIED"


def test_shadow_transport_value_review_all_within_tolerance() -> None:
    r = build_shadow_transport_value_review(_VALID_RESULTS)
    assert r["all_within_tolerance"] is True


def test_shadow_transport_value_review_fixture_reviews() -> None:
    r = build_shadow_transport_value_review(_VALID_RESULTS)
    assert len(r["fixture_reviews"]) == 5
    for fr in r["fixture_reviews"]:
        assert fr["review_status"] == "PASS"
        assert fr["within_tolerance"] is True


def test_shadow_transport_value_review_valid_001() -> None:
    r = build_shadow_transport_value_review(_VALID_RESULTS)
    fr = next(x for x in r["fixture_reviews"] if x["fixture_id"] == "valid-001")
    assert abs(fr["shadow_transport_value_observed"] - 0.4) < 1e-9


def test_shadow_transport_value_review_valid_002() -> None:
    r = build_shadow_transport_value_review(_VALID_RESULTS)
    fr = next(x for x in r["fixture_reviews"] if x["fixture_id"] == "valid-002")
    assert abs(fr["shadow_transport_value_observed"] - 0.4) < 1e-9


def test_shadow_transport_value_review_valid_003() -> None:
    r = build_shadow_transport_value_review(_VALID_RESULTS)
    fr = next(x for x in r["fixture_reviews"] if x["fixture_id"] == "valid-003")
    assert abs(fr["shadow_transport_value_observed"] - 0.866025) < 1e-6


def test_shadow_transport_value_review_valid_004() -> None:
    r = build_shadow_transport_value_review(_VALID_RESULTS)
    fr = next(x for x in r["fixture_reviews"] if x["fixture_id"] == "valid-004")
    assert abs(fr["shadow_transport_value_observed"] - 0.2) < 1e-9


def test_shadow_transport_value_review_valid_005() -> None:
    r = build_shadow_transport_value_review(_VALID_RESULTS)
    fr = next(x for x in r["fixture_reviews"] if x["fixture_id"] == "valid-005")
    assert abs(fr["shadow_transport_value_observed"]) < 1e-9


def test_shadow_transport_value_no_metric_value_emitted() -> None:
    r = build_shadow_transport_value_review(_VALID_RESULTS)
    assert r["no_metric_value_emitted"] is True
    assert r["no_expected_distance_added"] is True


# ---------------------------------------------------------------------------
# build_no_metric_value_emission_review
# ---------------------------------------------------------------------------


def test_no_metric_value_emission_review_status() -> None:
    r = build_no_metric_value_emission_review(_RECEIPT)
    assert r["review_status"] == "NO_METRIC_VALUES_EMITTED_VERIFIED"


def test_no_metric_value_emission_review_source_false() -> None:
    r = build_no_metric_value_emission_review(_RECEIPT)
    assert r["source_emits_metric_values"] is False
    assert r["source_fcr_no_metric_values_emitted"] is True


# ---------------------------------------------------------------------------
# build_no_forecast_influence_review
# ---------------------------------------------------------------------------


def test_no_forecast_influence_review_status() -> None:
    r = build_no_forecast_influence_review(_RECEIPT)
    assert r["review_status"] == "NO_FORECAST_INFLUENCE_VERIFIED"


def test_no_forecast_influence_review_clean() -> None:
    r = build_no_forecast_influence_review(_RECEIPT)
    assert r["source_scan_status"] == "CLEAN"
    assert r["source_scan_violations"] == []
    assert r["no_forecast_binding"] is True


# ---------------------------------------------------------------------------
# build_no_p43_surface_lane_review
# ---------------------------------------------------------------------------


def test_no_p43_surface_lane_review_status() -> None:
    r = build_no_p43_surface_lane_review(_RECEIPT)
    assert r["review_status"] == "NO_P43_SURFACE_LANES_VERIFIED"


def test_no_p43_surface_lane_review_clean() -> None:
    r = build_no_p43_surface_lane_review(_RECEIPT)
    assert r["source_scan_status"] == "CLEAN"
    assert r["source_scan_violations"] == []
    assert r["no_p43_lanes_opened"] is True


# ---------------------------------------------------------------------------
# build_authority_lock_review
# ---------------------------------------------------------------------------


def test_authority_lock_review_status() -> None:
    r = build_authority_lock_review(_RECEIPT)
    assert r["review_status"] == "AUTHORITY_LOCKS_VERIFIED"


def test_authority_lock_review_all_locks_intact() -> None:
    r = build_authority_lock_review(_RECEIPT)
    assert r["all_locks_intact"] is True


def test_authority_lock_review_source_values() -> None:
    r = build_authority_lock_review(_RECEIPT)
    assert r["source_advisory_only"] is True
    assert r["source_shadow_lane_only"] is True
    assert r["source_test_vector_computation_only"] is True
    assert r["source_wasserstein_computation_authorized"] is True
    assert r["source_emits_metric_values"] is False
    assert r["source_forecast_influence"] is False
    assert r["source_p43_surface_lanes_authorized"] is False
    assert r["source_execution_authority"] is False


# ---------------------------------------------------------------------------
# build_computation_completion_summary
# ---------------------------------------------------------------------------


def test_computation_completion_summary_status() -> None:
    r = build_computation_completion_summary(_RECEIPT)
    assert r["review_completion_status"] == "COMPUTATION_COMPLETION_VERIFIED"


def test_computation_completion_summary_counts() -> None:
    r = build_computation_completion_summary(_RECEIPT)
    assert r["computation_status"] == "WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE"
    assert r["total_fixtures"] == 14
    assert r["valid_computed"] == 5
    assert r["invalid_rejected"] == 5
    assert r["not_computable_rejected"] == 4
    assert r["all_shadow_lane"] is True
    assert r["no_metric_values_emitted"] is True
    assert r["determinism_status"] == "PASS"


# ---------------------------------------------------------------------------
# Full build_wasserstein_test_vector_computation_complete_review
# ---------------------------------------------------------------------------


def test_build_packet_schema_version() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert (
        pkt["schema_version"] == "WassersteinTestVectorComputationCompleteReview.v1"
    )


def test_build_packet_review_type() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert (
        pkt["review_type"]
        == "WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW"
    )


def test_build_packet_constants() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert pkt["operator_id"] == "WASSERSTEIN"
    assert pkt["source_computation_receipt_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH
    assert (
        pkt["source_computation_actual_pr_gate_hash"]
        == SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH
    )
    assert pkt["intended_lane"] == "SHADOW"
    assert pkt["review_stage"] == "TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW_ONLY"


def test_build_packet_authority_locks_complete_review_only() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert (
        pkt["authority_locks"]["test_vector_computation_complete_review_only"] is True
    )


def test_build_packet_wasserstein_computation_authorized() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert pkt["authority_locks"]["wasserstein_computation_authorized"] is True


def test_build_packet_emits_metric_values_false() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert pkt["authority_locks"]["emits_metric_values"] is False


def test_build_packet_execution_authority_false() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert pkt["authority_locks"]["execution_authority"] is False


def test_build_packet_all_review_sections_verified() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert (
        pkt["valid_fixture_result_review"]["review_status"]
        == "VALID_FIXTURE_RESULTS_VERIFIED"
    )
    assert (
        pkt["rejected_input_result_review"]["review_status"]
        == "REJECTED_INPUT_RESULTS_VERIFIED"
    )
    assert (
        pkt["shadow_transport_value_review"]["review_status"]
        == "SHADOW_TRANSPORT_VALUES_VERIFIED"
    )
    assert (
        pkt["no_metric_value_emission_review"]["review_status"]
        == "NO_METRIC_VALUES_EMITTED_VERIFIED"
    )
    assert (
        pkt["no_forecast_influence_review"]["review_status"]
        == "NO_FORECAST_INFLUENCE_VERIFIED"
    )
    assert (
        pkt["no_p43_surface_lane_review"]["review_status"]
        == "NO_P43_SURFACE_LANES_VERIFIED"
    )
    assert (
        pkt["authority_lock_review"]["review_status"] == "AUTHORITY_LOCKS_VERIFIED"
    )
    assert (
        pkt["computation_completion_summary"]["review_completion_status"]
        == "COMPUTATION_COMPLETION_VERIFIED"
    )


def test_build_packet_blocked_scopes_all_false() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    for k, v in pkt["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_build_packet_has_canonical_hash() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert "canonical_hash" in pkt
    assert len(pkt["canonical_hash"]) == 64


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash() -> None:
    a = build_wasserstein_test_vector_computation_complete_review(_payload())
    b = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_deterministic_serialization() -> None:
    a = build_wasserstein_test_vector_computation_complete_review(_payload())
    b = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert serialize_wasserstein_test_vector_computation_complete_review(
        a
    ) == serialize_wasserstein_test_vector_computation_complete_review(b)


# ---------------------------------------------------------------------------
# Hash excludes itself
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    altered = dict(pkt)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_test_vector_computation_complete_review_hash(pkt)
        == compute_wasserstein_test_vector_computation_complete_review_hash(altered)
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_computation_complete_review(_payload())
    b = build_wasserstein_test_vector_computation_complete_review(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


# ---------------------------------------------------------------------------
# Validation failures
# ---------------------------------------------------------------------------


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["review_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_computation_complete_review(p)


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="emits_metric_values_must_be_false"):
        build_wasserstein_test_vector_computation_complete_review(p)


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    bs = default_blocked_scopes()
    bs["forecast_influence"] = True
    p["blocked_scopes"] = bs
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_computation_complete_review(p)


def test_provenance_forbidden_reference_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring metric-value authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_computation_complete_review(p)


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
        build_wasserstein_test_vector_computation_complete_review(p)


def test_invalid_fixture_wrong_count_raises() -> None:
    with pytest.raises(WassersteinComputationCompleteReviewError):
        build_rejected_input_result_review(_INVALID_RESULTS[:3], _NC_RESULTS)


def test_nc_fixture_wrong_count_raises() -> None:
    with pytest.raises(WassersteinComputationCompleteReviewError):
        build_rejected_input_result_review(_INVALID_RESULTS, _NC_RESULTS[:2])


def test_recommended_next_step() -> None:
    pkt = build_wasserstein_test_vector_computation_complete_review(_payload())
    assert pkt["recommended_next_step"] == "WASSERSTEIN_EXPECTED_VALUES_GATE"
