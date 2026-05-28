from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_fixture_creation_pr_plan import (
    ChamferFixtureCreationPRPlanValidationError,
    build_chamfer_fixture_creation_pr_plan,
    compute_chamfer_fixture_creation_pr_plan_hash,
    default_constraints,
    default_output_contract,
    default_phase_statuses,
    default_planned_fixture_groups,
    default_planned_pr_surfaces,
    default_source_authorization_review_refs,
    default_source_expected_distance_policy_plan_refs,
    serialize_chamfer_fixture_creation_pr_plan,
    validate_chamfer_fixture_creation_pr_plan,
)


def _payload() -> dict:
    return {
        "plan_id": "chamfer-fixture-creation-pr-plan-001",
        "source_authorization_review_refs": ["ChamferFixtureCreationAuthorizationReview.v1:auth-review-001"],
        "source_expected_distance_policy_plan_refs": ["ChamferExpectedDistancePolicyPlan.v1:policy-001"],
        "planning_scope": {
            "plan_family": "FIXTURE_CREATION_PR_PLANNING_ONLY",
            "intended_lane": "SHADOW",
            "plan_stage": "PR_PLAN_ONLY",
        },
        "provenance": {
            "source": "CHAMFER_FIXTURE_CREATION_PR_PLAN_V1",
            "evidence_refs": ["evidence-001"],
            "generated_by": "agent",
            "upstream_schema_refs": ["contracts/canon/chamfer_fixture_creation_pr_plan.v1.schema.json"],
        },
        "created_at_utc": "2026-05-28T00:00:00Z",
        "governance_flags": {k: False for k in (
            "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
            "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved",
            "authorization_granted"
        )},
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_chamfer_fixture_creation_pr_plan(_payload())
    b = build_chamfer_fixture_creation_pr_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_fixture_creation_pr_plan(a) == serialize_chamfer_fixture_creation_pr_plan(b)


def test_locked_defaults() -> None:
    p = build_chamfer_fixture_creation_pr_plan(_payload())
    assert p["source_authorization_review_refs"] == default_source_authorization_review_refs()
    assert p["source_expected_distance_policy_plan_refs"] == default_source_expected_distance_policy_plan_refs()
    assert p["phase_statuses"] == default_phase_statuses()
    assert p["planned_pr_surfaces"] == default_planned_pr_surfaces()
    assert p["planned_fixture_groups"] == default_planned_fixture_groups()
    assert len(p["planned_pr_surfaces"]) >= 7
    assert len(p["planned_fixture_groups"]) >= 3
    assert p["constraints"] == default_constraints()
    assert p["output_contract"] == default_output_contract()


def test_enum_and_lock_failures() -> None:
    p = _payload()
    p["planning_scope"]["plan_family"] = "BAD"
    with pytest.raises(ChamferFixtureCreationPRPlanValidationError, match="unknown_plan_family"):
        build_chamfer_fixture_creation_pr_plan(p)

    p = _payload()
    p["source_authorization_review_refs"] = []
    with pytest.raises(ChamferFixtureCreationPRPlanValidationError, match="source_authorization_review_refs_must_be_non_empty"):
        build_chamfer_fixture_creation_pr_plan(p)

    p = _payload()
    p["constraints"] = dict(default_constraints(), fixture_files_added=True)
    with pytest.raises(ChamferFixtureCreationPRPlanValidationError, match="invalid_constraints"):
        build_chamfer_fixture_creation_pr_plan(p)

    p = _payload()
    p["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ChamferFixtureCreationPRPlanValidationError, match="authority_lock_must_be_false"):
        build_chamfer_fixture_creation_pr_plan(p)


def test_hash_exclusion_and_schema() -> None:
    packet = build_chamfer_fixture_creation_pr_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_fixture_creation_pr_plan_hash(packet) == compute_chamfer_fixture_creation_pr_plan_hash(altered)

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_fixture_creation_pr_plan.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(packet, schema)
    validate_chamfer_fixture_creation_pr_plan(packet)
