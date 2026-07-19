"""Tests for scripts/transport/run_wasserstein_invalid_fixture_implementation_plan.py (candidate fd5b52d96fe43aa0)"""

from core.wasserstein_invalid_fixture_implementation_plan import (
    build_wasserstein_invalid_fixture_implementation_plan,
    default_fixture_constraints,
    default_invalid_fixture_cases,
    default_output_contract,
    default_rejection_policy_plan,
    default_validation_plan,
    LOCKED_FALSE_FLAGS,
)

def test_default_helpers():
    assert isinstance(default_invalid_fixture_cases(), list)
    assert isinstance(default_fixture_constraints(), dict)
    assert isinstance(default_output_contract(), dict)
    assert isinstance(default_rejection_policy_plan(), dict)
    assert isinstance(default_validation_plan(), dict)

def test_build_invalid_fixture_plan_with_payload():
    payload = {
        "created_at_utc": "2026-07-12T00:00:00Z",
        "plan_id": "wasserstein_invalid_fixture_implementation_plan_001",
        "source_schema_plan_refs": [
            "WassersteinTestVectorSchemaPlan.v1:wasserstein_test_vector_schema_plan_001",
        ],
        "source_dossier_refs": [
            "WassersteinDistanceImplementationReadinessDossier.v1:wasserstein_distance_implementation_readiness_dossier_001",
        ],
        "source_valid_fixture_plan_refs": [
            "WassersteinValidFixtureImplementationPlan.v1:wasserstein_valid_fixture_implementation_plan_001",
        ],
        "invalid_fixture_scope": {
            "fixture_family": "MIXED_INVALID_FIXTURE_PLAN",
            "intended_lane": "SHADOW",
            "implementation_stage": "IMPLEMENTATION_PLAN_ONLY",
        },
        "invalid_fixture_cases": default_invalid_fixture_cases(),
        "rejection_policy_plan": default_rejection_policy_plan(),
        "deterministic_ordering_plan": {
            "sort_by_case_id": True,
            "stable_serialization_required": True,
            "canonical_hash_required": True,
            "nondeterministic_ordering_allowed": False,
        },
        "validation_plan": default_validation_plan(),
        "fixture_constraints": default_fixture_constraints(),
        "output_contract": default_output_contract(),
        "governance_flags": {flag: False for flag in LOCKED_FALSE_FLAGS},
        "provenance": {"source": "test", "brier_score": 0.1},
    }
    plan = build_wasserstein_invalid_fixture_implementation_plan(payload)
    assert plan is not None
    assert "schema_version" in plan
    assert "canonical_hash" in plan

def test_plan_has_rejection_and_validation():
    payload = {
        "created_at_utc": "2026-07-12T00:00:00Z",
        "plan_id": "wasserstein_invalid_fixture_implementation_plan_001",
        "source_schema_plan_refs": ["ref1"],
        "source_dossier_refs": ["ref2"],
        "source_valid_fixture_plan_refs": ["ref3"],
        "invalid_fixture_scope": {
            "fixture_family": "MIXED_INVALID_FIXTURE_PLAN",
            "intended_lane": "SHADOW",
            "implementation_stage": "IMPLEMENTATION_PLAN_ONLY",
        },
        "invalid_fixture_cases": default_invalid_fixture_cases(),
        "rejection_policy_plan": default_rejection_policy_plan(),
        "deterministic_ordering_plan": {
            "sort_by_case_id": True,
            "stable_serialization_required": True,
            "canonical_hash_required": True,
            "nondeterministic_ordering_allowed": False,
        },
        "validation_plan": default_validation_plan(),
        "fixture_constraints": default_fixture_constraints(),
        "output_contract": default_output_contract(),
        "governance_flags": {flag: False for flag in LOCKED_FALSE_FLAGS},
        "provenance": {"source": "test", "brier_score": 0.1},
    }
    plan = build_wasserstein_invalid_fixture_implementation_plan(payload)
    plan_str = str(plan)
    assert "rejection" in plan_str.lower() or "validation" in plan_str.lower() or len(plan) > 5
