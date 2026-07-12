"""Tests for core/norm_geometry_cpu_baseline_actual_pr_gate_review.py (HARDENING candidate 1418bfd1fba75e8d)

Covers constants, validate, build, hash, serialize.
"""

from core.norm_geometry_cpu_baseline_actual_pr_gate_review import (
    SCHEMA_VERSION,
    REVIEW_TYPE,
    ALLOWED_REVIEW_STATUS,
    ALLOWED_IMPLEMENTATION_RECOMMENDATION,
    LOCKED_FALSE_FLAGS,
    FORBIDDEN,
    validate_norm_geometry_cpu_baseline_actual_pr_gate_review,
    build_norm_geometry_cpu_baseline_actual_pr_gate_review,
    compute_norm_geometry_cpu_baseline_actual_pr_gate_review_hash,
    serialize_norm_geometry_cpu_baseline_actual_pr_gate_review,
    default_gate_conditions,
    default_output_contract,
)


def test_constants():
    assert SCHEMA_VERSION.startswith("NormGeometryCpuBaselineActualPrGateReview")
    assert REVIEW_TYPE == "NORM_GEOMETRY_CPU_BASELINE_ACTUAL_PR_GATE_REVIEW"
    assert "PLANS_COMPLETE_PENDING_OPERATOR_DECISION" in ALLOWED_REVIEW_STATUS
    assert "ADVISORY_REVIEW_ONLY" in ALLOWED_IMPLEMENTATION_RECOMMENDATION
    assert "production_activation" in LOCKED_FALSE_FLAGS
    assert "executable" in FORBIDDEN


def test_build_and_validate_minimal():
    payload = {
        "review_id": "test-001",
        "created_at_utc": "2026-07-11T00:00:00Z",
        "review_status": "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
        "implementation_recommendation": "ADVISORY_REVIEW_ONLY",
        "plans_reviewed": ["plan-001"],
        "governance_flags": {flag: False for flag in LOCKED_FALSE_FLAGS},
        "stop_boundary_reason": "none",
        "provenance": {},
        "gate_conditions": default_gate_conditions(),
        "output_contract": default_output_contract(),
        "required_operator_decision": True,
    }
    review = build_norm_geometry_cpu_baseline_actual_pr_gate_review(payload)
    assert review["schema_version"] == SCHEMA_VERSION
    assert review["review_type"] == REVIEW_TYPE


def test_hash_and_serialize():
    payload = {
        "review_id": "test-002",
        "created_at_utc": "2026-07-11T00:00:00Z",
        "review_status": "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
        "implementation_recommendation": "ADVISORY_REVIEW_ONLY",
        "plans_reviewed": ["plan-001"],
        "governance_flags": {flag: False for flag in LOCKED_FALSE_FLAGS},
        "stop_boundary_reason": "none",
        "provenance": {},
        "gate_conditions": default_gate_conditions(),
        "output_contract": default_output_contract(),
        "required_operator_decision": True,
    }
    review = build_norm_geometry_cpu_baseline_actual_pr_gate_review(payload)
    h = compute_norm_geometry_cpu_baseline_actual_pr_gate_review_hash(review)
    assert isinstance(h, str) and len(h) > 10
    s = serialize_norm_geometry_cpu_baseline_actual_pr_gate_review(review)
    assert isinstance(s, str)
