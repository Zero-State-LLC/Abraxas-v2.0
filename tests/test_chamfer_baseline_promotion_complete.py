"""Tests: ChamferBaselinePromotionComplete.v1 artifact."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_baseline_promotion_complete import (
    COMPLETE_STATUS,
    COMPLETION_ID,
    SCHEMA_VERSION,
    SOURCE_AUDIT_HASH,
    SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
    SOURCE_EV_ADDITION_RECEIPT_HASH,
    SOURCE_PACK_HASH,
    SOURCE_REVIEW_HASH,
    ChamferBaselinePromotionCompleteError,
    build_chamfer_baseline_promotion_complete,
    validate_chamfer_baseline_promotion_complete,
)
from core.canonical.json import canonical_hash

OUT_PATH = Path(
    "out/metric_operator/chamfer_baseline_promotion_complete_001.latest.json"
)


@pytest.fixture(scope="module")
def completion() -> dict:
    return build_chamfer_baseline_promotion_complete()


def test_complete_status(completion: dict) -> None:
    assert completion["complete_status"] == COMPLETE_STATUS


def test_completion_id(completion: dict) -> None:
    assert completion["completion_id"] == COMPLETION_ID


def test_schema_version(completion: dict) -> None:
    assert completion["schema_version"] == SCHEMA_VERSION


def test_operator_id(completion: dict) -> None:
    assert completion["operator_id"] == "CHAMFER_DISTANCE"


def test_intended_lane(completion: dict) -> None:
    assert completion["intended_lane"] == "SHADOW"


def test_canonical_hash_present_and_valid(completion: dict) -> None:
    h = completion.get("canonical_hash", "")
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_recomputes(completion: dict) -> None:
    preimage = {k: v for k, v in completion.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == completion["canonical_hash"]


def test_source_hashes(completion: dict) -> None:
    assert completion["source_review_hash"] == SOURCE_REVIEW_HASH
    assert completion["source_audit_hash"] == SOURCE_AUDIT_HASH
    assert (
        completion["source_computation_complete_review_hash"]
        == SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH
    )
    assert completion["source_expected_values_receipt_hash"] == SOURCE_EV_ADDITION_RECEIPT_HASH
    assert completion["source_pack_hash"] == SOURCE_PACK_HASH


def test_authority_locks(completion: dict) -> None:
    al = completion["authority_locks"]
    assert al["advisory_only"] is True
    assert al["shadow_lane_only"] is True
    assert al["baseline_promotion_complete_only"] is True
    assert al["chamfer_already_promoted_in_pack"] is True
    assert al["pack_repromotion_required"] is False
    assert al["projection_wiring_pending"] is True
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False


def test_all_completions_confirmed(completion: dict) -> None:
    assert completion["all_completions_confirmed"] is True


def test_recommended_next_step(completion: dict) -> None:
    assert completion["recommended_next_step"] == "CHAMFER_PROJECTION_WIRING_ADAPTER"


def test_review_binding(completion: dict) -> None:
    rb = completion["review_binding"]
    assert rb["review_hash_confirmed"] is True
    assert rb["all_reviews_passed"] is True
    assert rb["review_recommended_matches"] is True
    assert rb["review_advisory_only"] is True
    assert rb["review_pack_repromotion_required"] is False
    assert rb["review_projection_wiring_gap_confirmed"] is True
    assert rb["confirmed"] is True


def test_audit_binding(completion: dict) -> None:
    ab = completion["audit_binding"]
    assert ab["audit_hash_confirmed"] is True
    assert ab["audit_computation_chain_closed"] is True
    assert ab["audit_pack_promoted"] is True
    assert ab["audit_advisory_only"] is True
    assert ab["confirmed"] is True


def test_computation_complete_review_binding(completion: dict) -> None:
    crb = completion["computation_complete_review_binding"]
    assert crb["hash_confirmed"] is True
    assert crb["chamfer_computation_authorized"] is True
    assert crb["advisory_only"] is True
    assert crb["canon_promotion"] is False
    assert crb["confirmed"] is True


def test_expected_values_receipt_binding(completion: dict) -> None:
    evb = completion["expected_values_receipt_binding"]
    assert evb["hash_confirmed"] is True
    assert evb["all_5_shadow_distances_verified"] is True
    assert evb["all_values_match_static_fixtures"] is True
    assert evb["operator_approval_on_record"] is True
    assert evb["confirmed"] is True


def test_baseline_state_completion(completion: dict) -> None:
    bsc = completion["baseline_state_completion"]
    assert bsc["chamfer_already_promoted_in_pack"] is True
    assert bsc["current_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert bsc["current_computation_status"] == "SHADOW_STUB_ONLY"
    assert bsc["shadow_stub_only_confirmed"] is True
    assert bsc["pack_hash_confirmed"] is True
    assert bsc["runtime_mutated"] is False
    assert bsc["pack_vector_modified"] is False
    assert bsc["governance_closure_complete"] is True
    assert bsc["confirmed"] is True


def test_no_pack_repromotion_completion(completion: dict) -> None:
    npr = completion["no_pack_repromotion_completion"]
    assert npr["pack_repromotion_required"] is False
    assert npr["pack_repromotion_performed"] is False
    assert npr["pack_vector_unchanged"] is True
    assert npr["pack_hash_before"] == SOURCE_PACK_HASH
    assert npr["pack_hash_after"] == SOURCE_PACK_HASH
    assert npr["confirmed"] is True


def test_projection_wiring_pending_record(completion: dict) -> None:
    pwr = completion["projection_wiring_pending_record"]
    assert pwr["promotion_key_in_this_phase"] is None
    assert pwr["baseline_promotion_complete_key_in_this_phase"] is None
    assert pwr["projection_cap_pct"] == 95
    assert pwr["projection_wiring_pending"] is True
    assert pwr["wiring_phase"] == "CHAMFER_PROJECTION_WIRING_ADAPTER"
    assert pwr["confirmed"] is True


def test_blocked_scope_completion(completion: dict) -> None:
    bs = completion["blocked_scope_completion"]
    assert bs["all_scopes_remain_blocked"] is True
    assert bs["metric_emission"] == "BLOCKED"
    assert bs["forecast_influence"] == "BLOCKED"
    assert bs["p43_lanes"] == "BLOCKED"
    assert bs["research_canary_guardrail"] == "ACTIVE"
    assert bs["confirmed"] is True


def test_blocked_scopes(completion: dict) -> None:
    bs = completion["blocked_scopes"]
    assert bs["metric_emission"] == "BLOCKED"
    assert bs["canon_promotion"] == "BLOCKED"
    assert bs["execution_authority"] == "BLOCKED"


def test_validate_passes(completion: dict) -> None:
    validate_chamfer_baseline_promotion_complete(completion)


def test_validate_wrong_status_raises(completion: dict) -> None:
    bad = {**completion, "complete_status": "WRONG"}
    with pytest.raises(ChamferBaselinePromotionCompleteError):
        validate_chamfer_baseline_promotion_complete(bad)


def test_validate_wrong_hash_raises(completion: dict) -> None:
    bad = {**completion, "canonical_hash": "a" * 64}
    with pytest.raises(ChamferBaselinePromotionCompleteError):
        validate_chamfer_baseline_promotion_complete(bad)


def test_validate_not_all_confirmed_raises(completion: dict) -> None:
    bad = {**completion, "all_completions_confirmed": False}
    with pytest.raises(ChamferBaselinePromotionCompleteError):
        validate_chamfer_baseline_promotion_complete(bad)


def test_validate_wrong_next_step_raises(completion: dict) -> None:
    bad = {**completion, "recommended_next_step": "WRONG"}
    with pytest.raises(ChamferBaselinePromotionCompleteError):
        validate_chamfer_baseline_promotion_complete(bad)


def test_on_disk_artifact_matches_build(completion: dict) -> None:
    if not OUT_PATH.exists():
        pytest.skip("on-disk artifact not yet generated; run the runner script first")
    on_disk = json.loads(OUT_PATH.read_text())
    assert on_disk["canonical_hash"] == completion["canonical_hash"]
    assert on_disk["complete_status"] == COMPLETE_STATUS
