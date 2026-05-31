"""Tests: ChamferBaselinePromotionReview.v1 artifact."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_baseline_promotion_review import (
    REVIEW_ID,
    REVIEW_STATUS,
    SCHEMA_VERSION,
    SOURCE_AUDIT_HASH,
    SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
    SOURCE_EV_ADDITION_RECEIPT_HASH,
    SOURCE_PACK_HASH,
    ChamferBaselinePromotionReviewError,
    build_chamfer_baseline_promotion_review,
    validate_chamfer_baseline_promotion_review,
)
from core.canonical.json import canonical_hash

OUT_PATH = Path(
    "out/metric_operator/chamfer_baseline_promotion_review_001.latest.json"
)


@pytest.fixture(scope="module")
def review() -> dict:
    return build_chamfer_baseline_promotion_review()


def test_review_status(review: dict) -> None:
    assert review["review_status"] == REVIEW_STATUS


def test_review_id(review: dict) -> None:
    assert review["review_id"] == REVIEW_ID


def test_schema_version(review: dict) -> None:
    assert review["schema_version"] == SCHEMA_VERSION


def test_operator_id(review: dict) -> None:
    assert review["operator_id"] == "CHAMFER_DISTANCE"


def test_intended_lane(review: dict) -> None:
    assert review["intended_lane"] == "SHADOW"


def test_canonical_hash_present_and_valid(review: dict) -> None:
    h = review.get("canonical_hash", "")
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_recomputes(review: dict) -> None:
    preimage = {k: v for k, v in review.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == review["canonical_hash"]


def test_source_hashes(review: dict) -> None:
    assert review["source_audit_hash"] == SOURCE_AUDIT_HASH
    assert (
        review["source_computation_complete_review_hash"]
        == SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH
    )
    assert review["source_expected_values_receipt_hash"] == SOURCE_EV_ADDITION_RECEIPT_HASH
    assert review["source_pack_hash"] == SOURCE_PACK_HASH


def test_authority_locks(review: dict) -> None:
    al = review["authority_locks"]
    assert al["advisory_only"] is True
    assert al["shadow_lane_only"] is True
    assert al["baseline_promotion_review_only"] is True
    assert al["chamfer_already_promoted_in_pack"] is True
    assert al["pack_repromotion_required"] is False
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False


def test_all_reviews_passed(review: dict) -> None:
    assert review["all_reviews_passed"] is True


def test_recommended_next_step(review: dict) -> None:
    assert review["recommended_next_step"] == "CHAMFER_BASELINE_PROMOTION_COMPLETE"


def test_audit_binding_review(review: dict) -> None:
    abr = review["audit_binding_review"]
    assert abr["audit_hash_confirmed"] is True
    assert abr["audit_recommended_next_step_matches"] is True
    assert abr["audit_computation_chain_closed"] is True
    assert abr["audit_pack_promoted"] is True
    assert abr["review_passed"] is True


def test_computation_complete_review_binding(review: dict) -> None:
    ccr = review["computation_complete_review_binding"]
    assert ccr["hash_confirmed"] is True
    assert ccr["chamfer_computation_authorized"] is True
    assert ccr["advisory_only"] is True
    assert ccr["canon_promotion"] is False
    assert ccr["review_passed"] is True


def test_expected_values_receipt_binding(review: dict) -> None:
    evr = review["expected_values_receipt_binding"]
    assert evr["hash_confirmed"] is True
    assert evr["all_5_shadow_distances_verified"] is True
    assert evr["all_values_match_static_fixtures"] is True
    assert evr["review_passed"] is True


def test_current_pack_state_review(review: dict) -> None:
    psr = review["current_pack_state_review"]
    assert psr["chamfer_already_promoted_in_pack"] is True
    assert psr["current_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert psr["current_computation_status"] == "SHADOW_STUB_ONLY"
    assert psr["shadow_stub_only_confirmed"] is True
    assert psr["pack_hash_confirmed"] is True
    assert psr["runtime_mutated"] is False
    assert psr["pack_vector_modified"] is False
    assert psr["review_passed"] is True


def test_target_state_review(review: dict) -> None:
    tsr = review["target_state_review"]
    assert tsr["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert tsr["target_computation_status"] == "SHADOW_STUB_ONLY"
    assert tsr["target_matches_current"] is True
    assert tsr["no_state_change_required_in_pack"] is True
    assert tsr["review_passed"] is True


def test_no_pack_repromotion_review(review: dict) -> None:
    npr = review["no_pack_repromotion_review"]
    assert npr["pack_repromotion_required"] is False
    assert npr["pack_vector_unchanged"] is True
    assert npr["pack_hash_before"] == SOURCE_PACK_HASH
    assert npr["pack_hash_after"] == SOURCE_PACK_HASH
    assert npr["review_passed"] is True


def test_projection_wiring_gap_review(review: dict) -> None:
    pwr = review["projection_wiring_gap_review"]
    assert pwr["promotion_key"] is None
    assert pwr["baseline_promotion_complete_key"] is None
    assert pwr["projection_cap_pct"] == 95
    assert pwr["wiring_gap_confirmed"] is True
    assert pwr["review_passed"] is True


def test_promotion_scope_review(review: dict) -> None:
    psr = review["promotion_scope_review"]
    assert psr["pack_repromotion"] is False
    assert psr["fixture_mutation"] is False
    assert psr["computation_rerun"] is False
    assert psr["runtime_mutation"] is False
    assert psr["canon_promotion"] is False
    assert psr["metric_emission"] is False
    assert psr["review_passed"] is True


def test_blocked_scope_review(review: dict) -> None:
    bs = review["blocked_scope_review"]
    assert bs["all_scopes_remain_blocked"] is True
    assert bs["metric_emission"] == "BLOCKED"
    assert bs["forecast_influence"] == "BLOCKED"
    assert bs["p43_lanes"] == "BLOCKED"
    assert bs["research_canary_guardrail"] == "ACTIVE"
    assert bs["review_passed"] is True


def test_blocked_scopes(review: dict) -> None:
    bs = review["blocked_scopes"]
    assert bs["metric_emission"] == "BLOCKED"
    assert bs["canon_promotion"] == "BLOCKED"
    assert bs["execution_authority"] == "BLOCKED"


def test_validate_passes(review: dict) -> None:
    validate_chamfer_baseline_promotion_review(review)


def test_validate_wrong_status_raises(review: dict) -> None:
    bad = {**review, "review_status": "WRONG"}
    with pytest.raises(ChamferBaselinePromotionReviewError):
        validate_chamfer_baseline_promotion_review(bad)


def test_validate_wrong_hash_raises(review: dict) -> None:
    bad = {**review, "canonical_hash": "a" * 64}
    with pytest.raises(ChamferBaselinePromotionReviewError):
        validate_chamfer_baseline_promotion_review(bad)


def test_validate_all_reviews_not_passed_raises(review: dict) -> None:
    bad = {**review, "all_reviews_passed": False}
    with pytest.raises(ChamferBaselinePromotionReviewError):
        validate_chamfer_baseline_promotion_review(bad)


def test_on_disk_artifact_matches_build(review: dict) -> None:
    if not OUT_PATH.exists():
        pytest.skip("on-disk artifact not yet generated; run the runner script first")
    on_disk = json.loads(OUT_PATH.read_text())
    assert on_disk["canonical_hash"] == review["canonical_hash"]
    assert on_disk["review_status"] == REVIEW_STATUS
