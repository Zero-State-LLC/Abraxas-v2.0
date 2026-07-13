"""Tests for core/norm_geometry_baseline_promotion_review.py (candidate fada517b6edcda0d)"""

from core.norm_geometry_baseline_promotion_review import (
    SCHEMA_VERSION,
    REVIEW_ID,
    REVIEW_STATUS,
    REVIEW_STAGE,
    OPERATOR_ID,
    FORBIDDEN,
    GATE_PATH,
    DECISION_PATH,
    CLOSURE_PATH,
)

def test_schema_and_ids():
    assert SCHEMA_VERSION == "NormGeometryBaselinePromotionReview.v1"
    assert REVIEW_ID == "norm_geometry_baseline_promotion_review_001"
    assert REVIEW_STATUS == "NORM_GEOMETRY_BASELINE_PROMOTION_REVIEW_COMPLETE"
    assert REVIEW_STAGE == "BASELINE_PROMOTION_REVIEW_ONLY"
    assert OPERATOR_ID == "NORM_GEOMETRY"

def test_forbidden_items():
    assert "executable" in FORBIDDEN
    assert "geodesic-distance" in FORBIDDEN
    assert "dijkstra-execution" in FORBIDDEN
    assert len(FORBIDDEN) > 10

def test_paths_defined():
    assert str(GATE_PATH).endswith("norm_geometry_baseline_promotion_gate_001.latest.json")
    assert str(DECISION_PATH).endswith("norm_geometry_baseline_promotion_operator_decision.json")
    assert str(CLOSURE_PATH).endswith("norm_geometry_computation_operator_closure_001.latest.json")
