from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.geodesic_baseline_promotion_review import (
    REVIEW_ID,
    REVIEW_STATUS,
    REVIEW_STAGE,
    SCHEMA_VERSION,
    SOURCE_BASELINE_PROMOTION_DECISION_HASH,
    SOURCE_GEODESIC_CLOSURE_HASH,
    GeodesicBaselinePromotionReviewError,
    build_geodesic_baseline_promotion_review,
    validate_geodesic_baseline_promotion_review,
)
from core.canonical.json import canonical_hash


def _build() -> dict:
    return build_geodesic_baseline_promotion_review()


def test_builds_without_error() -> None:
    review = _build()
    assert review["review_status"] == REVIEW_STATUS


def test_schema_version() -> None:
    review = _build()
    assert review["schema_version"] == SCHEMA_VERSION


def test_review_id() -> None:
    review = _build()
    assert review["review_id"] == REVIEW_ID


def test_review_stage() -> None:
    review = _build()
    assert review["review_stage"] == REVIEW_STAGE


def test_intended_lane_shadow() -> None:
    review = _build()
    assert review["intended_lane"] == "SHADOW"


def test_source_hashes_present() -> None:
    review = _build()
    assert review["source_baseline_promotion_decision_hash"] == SOURCE_BASELINE_PROMOTION_DECISION_HASH
    assert review["source_geodesic_closure_hash"] == SOURCE_GEODESIC_CLOSURE_HASH


def test_deterministic() -> None:
    a = _build()
    b = _build()
    assert a["canonical_hash"] == b["canonical_hash"]


def test_canonical_hash_valid() -> None:
    review = _build()
    h = review["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in review.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_validate_passes() -> None:
    review = _build()
    validate_geodesic_baseline_promotion_review(review)


def test_decision_review_passed() -> None:
    review = _build()
    assert review["decision_review"]["decision_review_passed"] is True


def test_decision_review_baseline_promotion_authorized() -> None:
    review = _build()
    assert review["decision_review"]["baseline_promotion_authorized"] is True


def test_decision_review_target_vector_type() -> None:
    review = _build()
    assert review["decision_review"]["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"


def test_decision_review_target_computation_status() -> None:
    review = _build()
    assert review["decision_review"]["target_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_closure_review_passed() -> None:
    review = _build()
    assert review["closure_review"]["closure_review_passed"] is True


def test_closure_review_all_closure_passed() -> None:
    review = _build()
    assert review["closure_review"]["all_closure_passed"] is True


def test_baseline_pack_update_review_passed() -> None:
    review = _build()
    assert review["baseline_pack_update_review"]["pack_update_review_passed"] is True


def test_baseline_pack_update_previous_vector_type() -> None:
    review = _build()
    pu = review["baseline_pack_update_review"]
    assert pu["previous_vector_type"] == "VALID_METADATA_VECTOR"
    assert pu["previous_expected_computation_status"] == "NOT_IMPLEMENTED"


def test_baseline_pack_update_new_vector_type() -> None:
    review = _build()
    pu = review["baseline_pack_update_review"]
    assert pu["new_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert pu["new_expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_operator_state_geodesic_shadow() -> None:
    review = _build()
    geo = review["operator_state_after_update"]["GEODESIC"]
    assert geo["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert geo["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_operator_state_wasserstein_unchanged() -> None:
    review = _build()
    ws = review["operator_state_after_update"]["WASSERSTEIN"]
    assert ws["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert ws["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_operator_state_chamfer_unchanged() -> None:
    review = _build()
    ch = review["operator_state_after_update"]["CHAMFER_DISTANCE"]
    assert ch["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert ch["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_parity_review_passed() -> None:
    review = _build()
    pr = review["parity_review"]
    assert pr["parity_review_passed"] is True
    assert pr["geodesic_at_shadow_stub_after_promotion"] is True
    assert pr["wasserstein_at_shadow_stub"] is True
    assert pr["chamfer_distance_at_shadow_stub"] is True
    assert pr["parity_achieved"] is True


def test_parity_shadow_stub_operators() -> None:
    review = _build()
    shadow_ops = review["parity_review"]["shadow_stub_operators_after_update"]
    assert set(shadow_ops) == {"WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC"}


def test_no_metric_emission_review_passed() -> None:
    review = _build()
    assert review["no_metric_emission_review"]["no_metric_emission_review_passed"] is True
    assert review["no_metric_emission_review"]["emits_metric_values"] is False


def test_no_forecast_influence_review_passed() -> None:
    review = _build()
    assert review["no_forecast_influence_review"]["no_forecast_influence_review_passed"] is True
    assert review["no_forecast_influence_review"]["forecast_influence"] is False


def test_no_p43_surface_lane_review_passed() -> None:
    review = _build()
    assert review["no_p43_surface_lane_review"]["no_p43_surface_lane_review_passed"] is True
    assert review["no_p43_surface_lane_review"]["p43_surface_lanes_authorized"] is False


def test_authority_locks_true_flags() -> None:
    review = _build()
    locks = review["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["baseline_promotion_review_only"] is True
    assert locks["baseline_promotion_authorized"] is True


def test_authority_locks_false_flags() -> None:
    review = _build()
    locks = review["authority_locks"]
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        assert locks[flag] is False, f"authority_locks.{flag} must be False"


def test_blocked_scopes_all_false() -> None:
    review = _build()
    bs = review["blocked_scopes"]
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        assert bs[flag] is False, f"blocked_scopes.{flag} must be False"


def test_recommended_next_step() -> None:
    review = _build()
    assert review["recommended_next_step"] == "GEODESIC_BASELINE_PROMOTION_COMPLETE"


def test_validate_wrong_schema_version() -> None:
    review = _build()
    review = dict(review)
    review["schema_version"] = "WRONG"
    with pytest.raises(GeodesicBaselinePromotionReviewError, match="schema_version"):
        validate_geodesic_baseline_promotion_review(review)


def test_validate_wrong_review_status() -> None:
    review = _build()
    review = dict(review)
    review["review_status"] = "WRONG"
    with pytest.raises(GeodesicBaselinePromotionReviewError, match="review_status"):
        validate_geodesic_baseline_promotion_review(review)


def test_validate_wrong_intended_lane() -> None:
    review = _build()
    review = dict(review)
    review["intended_lane"] = "PRODUCTION"
    with pytest.raises(GeodesicBaselinePromotionReviewError, match="intended_lane"):
        validate_geodesic_baseline_promotion_review(review)


def test_validate_authority_lock_flip() -> None:
    review = _build()
    locks = dict(review["authority_locks"])
    locks["execution_authority"] = True
    review = dict(review)
    review["authority_locks"] = locks
    with pytest.raises(GeodesicBaselinePromotionReviewError, match="authority_locks.execution_authority"):
        validate_geodesic_baseline_promotion_review(review)


def test_validate_parity_flag_false() -> None:
    review = _build()
    pr = dict(review["parity_review"])
    pr["geodesic_at_shadow_stub_after_promotion"] = False
    review = dict(review)
    review["parity_review"] = pr
    with pytest.raises(GeodesicBaselinePromotionReviewError, match="geodesic_at_shadow_stub_after_promotion"):
        validate_geodesic_baseline_promotion_review(review)


def test_artifact_file_written_by_runner() -> None:
    path = Path("out/metric_operator/geodesic_baseline_promotion_review_001.latest.json")
    if not path.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(path.read_text())
    assert data["review_status"] == REVIEW_STATUS
    assert data["schema_version"] == SCHEMA_VERSION
    assert isinstance(data["canonical_hash"], str) and len(data["canonical_hash"]) == 64
