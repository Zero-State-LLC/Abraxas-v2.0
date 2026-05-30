from __future__ import annotations

import pytest

from core.chamfer_distance_computation_authorization_review import (
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH,
    SOURCE_FIXTURE_CREATION_GATE_HASH,
    ChamferDistanceComputationAuthorizationReviewError,
    build_chamfer_distance_computation_authorization_review,
    compute_chamfer_distance_computation_authorization_review_hash,
    default_authority_lock_review,
    default_authority_locks,
    default_blocked_scopes,
    default_computation_receipt_review,
    default_computation_scope_review,
    default_fixture_corpus_readiness_review,
    serialize_chamfer_distance_computation_authorization_review,
)


def _payload() -> dict:
    return {
        "authorization_review_id": "chamfer_distance_computation_authorization_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "COMPUTATION_AUTHORIZATION_REVIEW_ONLY",
        "fixture_corpus_readiness_review": default_fixture_corpus_readiness_review(),
        "computation_receipt_review": default_computation_receipt_review(),
        "computation_scope_review": default_computation_scope_review(),
        "authority_lock_review": default_authority_lock_review(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "CHAMFER_DISTANCE_COMPUTATION_ACTUAL_PR_GATE",
        "provenance": {
            "source": "CHAMFER_DISTANCE_COMPUTATION_AUTHORIZATION_REVIEW",
            "evidence_refs": [
                f"ChamferDistanceComputationReceipt.v1:{SOURCE_COMPUTATION_RECEIPT_HASH}",
            ],
            "generated_by": "PATCH_CHAMFER_DISTANCE_COMPUTATION_AUTHORIZATION_REVIEW_001",
            "upstream_schema_refs": [],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_build_valid_packet() -> None:
    packet = build_chamfer_distance_computation_authorization_review(_payload())
    assert packet["schema_version"] == "ChamferDistanceComputationAuthorizationReview.v1"
    assert packet["review_type"] == "CHAMFER_DISTANCE_COMPUTATION_AUTHORIZATION_REVIEW"
    assert packet["operator_id"] == "CHAMFER_DISTANCE"
    assert "canonical_hash" in packet


def test_hash_deterministic() -> None:
    p1 = build_chamfer_distance_computation_authorization_review(_payload())
    p2 = build_chamfer_distance_computation_authorization_review(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_hash_function() -> None:
    packet = build_chamfer_distance_computation_authorization_review(_payload())
    h = compute_chamfer_distance_computation_authorization_review_hash(packet)
    assert h == packet["canonical_hash"]


def test_serialize_produces_string() -> None:
    packet = build_chamfer_distance_computation_authorization_review(_payload())
    s = serialize_chamfer_distance_computation_authorization_review(packet)
    assert isinstance(s, str)
    assert "CHAMFER_DISTANCE_COMPUTATION_AUTHORIZATION_REVIEW" in s


def test_invalid_lane_raises() -> None:
    p = _payload()
    p["intended_lane"] = "PRODUCTION"
    with pytest.raises(ChamferDistanceComputationAuthorizationReviewError):
        build_chamfer_distance_computation_authorization_review(p)


def test_invalid_review_stage_raises() -> None:
    p = _payload()
    p["review_stage"] = "INVALID_STAGE"
    with pytest.raises(ChamferDistanceComputationAuthorizationReviewError):
        build_chamfer_distance_computation_authorization_review(p)


def test_authority_lock_violation_raises() -> None:
    p = _payload()
    al = dict(default_authority_locks())
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ChamferDistanceComputationAuthorizationReviewError):
        build_chamfer_distance_computation_authorization_review(p)


def test_forbidden_token_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime_source"
    with pytest.raises(ChamferDistanceComputationAuthorizationReviewError, match="forbidden"):
        build_chamfer_distance_computation_authorization_review(p)


def test_source_hashes_present() -> None:
    assert len(SOURCE_COMPUTATION_RECEIPT_HASH) == 64
    assert len(SOURCE_FIXTURE_CREATION_GATE_HASH) == 64
    assert len(SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH) == 64


def test_fixture_corpus_readiness_totals() -> None:
    r = default_fixture_corpus_readiness_review()
    assert r["total_fixtures_verified"] == 13
    assert r["valid_fixtures"] == 5
    assert r["invalid_fixtures"] == 5
    assert r["not_computable_fixtures"] == 3
    assert r["corpus_readiness_status"] == "READY"


def test_computation_scope_eligible() -> None:
    cs = default_computation_scope_review()
    assert cs["computation_scope_status"] == "ELIGIBLE_FOR_BOUNDED_AUTHORIZATION"


def test_authority_locks_defaults() -> None:
    al = default_authority_locks()
    assert al["emits_metric_values"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False


def test_blocked_scopes_all_false() -> None:
    assert all(v is False for v in default_blocked_scopes().values())
