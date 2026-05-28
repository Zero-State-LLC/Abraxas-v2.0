from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_fixture_creation_authorization_review import (
    ChamferFixtureCreationAuthorizationReviewValidationError,
    build_chamfer_fixture_creation_authorization_review,
    compute_chamfer_fixture_creation_authorization_review_hash,
    default_authorization_decision,
    default_authorization_findings,
    default_blocker_findings,
    default_creation_constraints,
    default_output_contract,
    serialize_chamfer_fixture_creation_authorization_review,
    validate_chamfer_fixture_creation_authorization_review,
)


def _payload() -> dict:
    return {
        "review_id": "auth-review-001",
        "source_fixture_readiness_review_refs": ["ChamferFixtureImplementationReadinessReview.v1:review-001"],
        "source_expected_distance_policy_plan_refs": ["ChamferExpectedDistancePolicyPlan.v1:policy-001"],
        "source_fixture_consolidation_receipt_refs": ["ChamferFixturePlanConsolidationReceipt.v1:receipt-001"],
        "source_valid_fixture_plan_refs": ["ChamferValidFixtureImplementationPlan.v1:plan-valid-001"],
        "source_invalid_fixture_plan_refs": ["ChamferInvalidFixtureImplementationPlan.v1:plan-invalid-001"],
        "source_not_computable_fixture_plan_refs": ["ChamferNotComputableFixtureImplementationPlan.v1:plan-nc-001"],
        "source_schema_plan_refs": ["ChamferTestVectorSchemaPlan.v1:plan-schema-001"],
        "source_baseline_implementation_plan_refs": ["ChamferBaselineImplementationPlan.v1:plan-001"],
        "authorization_scope": {
            "authorization_family": "FIXTURE_CREATION_AUTHORIZATION_REVIEW",
            "intended_lane": "SHADOW",
            "authorization_stage": "AUTHORIZATION_REVIEW_ONLY",
        },
        "provenance": {
            "source": "CHAMFER_FIXTURE_CREATION_AUTHORIZATION_REVIEW_V1",
            "evidence_refs": ["evidence-001"],
            "generated_by": "agent",
            "upstream_schema_refs": ["contracts/canon/chamfer_fixture_creation_authorization_review.v1.schema.json"],
        },
        "created_at_utc": "2026-05-28T00:00:00Z",
        "governance_flags": {k: False for k in (
            "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
            "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved",
            "authorization_granted"
        )},
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_chamfer_fixture_creation_authorization_review(_payload())
    b = build_chamfer_fixture_creation_authorization_review(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_fixture_creation_authorization_review(a) == serialize_chamfer_fixture_creation_authorization_review(b)


def test_default_findings_and_blockers_deterministic() -> None:
    assert default_authorization_findings() == default_authorization_findings()
    assert default_blocker_findings() == default_blocker_findings()


def test_operator_id_mismatch_fails() -> None:
    p = build_chamfer_fixture_creation_authorization_review(_payload())
    p["operator_id"] = "NOT_CHAMFER"
    with pytest.raises(ChamferFixtureCreationAuthorizationReviewValidationError, match="unknown_operator_id"):
        validate_chamfer_fixture_creation_authorization_review(p)


@pytest.mark.parametrize(("path", "val", "err"), [
    (("authorization_scope", "authorization_family"), "BAD", "unknown_authorization_family"),
    (("authorization_scope", "intended_lane"), "BAD", "unknown_intended_lane"),
    (("authorization_scope", "authorization_stage"), "BAD", "unknown_authorization_stage"),
    (("authorization_findings", 0, "finding_type"), "BAD", "unknown_finding_type"),
    (("authorization_findings", 0, "finding_status"), "BAD", "unknown_finding_status"),
    (("authorization_findings", 0, "implementation_status"), "BAD", "unknown_implementation_status"),
    (("blocker_findings", 0, "blocker_type"), "BAD", "unknown_blocker_type"),
    (("blocker_findings", 0, "blocker_status"), "BAD", "unknown_blocker_status"),
])
def test_enum_failures(path: tuple, val: str, err: str) -> None:
    p = _payload()
    p["authorization_findings"] = default_authorization_findings()
    p["blocker_findings"] = default_blocker_findings()
    t = p
    for key in path[:-1]:
        t = t[key]
    t[path[-1]] = val
    with pytest.raises(ChamferFixtureCreationAuthorizationReviewValidationError, match=err):
        build_chamfer_fixture_creation_authorization_review(p)


def test_duplicate_ids_fail() -> None:
    p = _payload()
    f = default_authorization_findings()[0]
    p["authorization_findings"] = [f, dict(f)]
    with pytest.raises(ChamferFixtureCreationAuthorizationReviewValidationError, match="duplicate_finding_id"):
        build_chamfer_fixture_creation_authorization_review(p)

    p = _payload()
    b = default_blocker_findings()[0]
    p["blocker_findings"] = [b, dict(b)]
    with pytest.raises(ChamferFixtureCreationAuthorizationReviewValidationError, match="duplicate_blocker_id"):
        build_chamfer_fixture_creation_authorization_review(p)


def test_locked_maps_governance_and_provenance() -> None:
    p = _payload()
    p["authorization_decision"] = dict(default_authorization_decision(), fixture_creation_authorized=True)
    with pytest.raises(ChamferFixtureCreationAuthorizationReviewValidationError, match="invalid_authorization_decision"):
        build_chamfer_fixture_creation_authorization_review(p)
    p = _payload()
    p["creation_constraints"] = dict(default_creation_constraints(), expected_distances_added=True)
    with pytest.raises(ChamferFixtureCreationAuthorizationReviewValidationError, match="invalid_creation_constraints"):
        build_chamfer_fixture_creation_authorization_review(p)
    p = _payload()
    p["output_contract"] = dict(default_output_contract(), emits_authority_tokens=True)
    with pytest.raises(ChamferFixtureCreationAuthorizationReviewValidationError, match="invalid_output_contract"):
        build_chamfer_fixture_creation_authorization_review(p)
    p = _payload()
    p["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ChamferFixtureCreationAuthorizationReviewValidationError, match="authority_lock_must_be_false"):
        build_chamfer_fixture_creation_authorization_review(p)
    p = _payload()
    p["provenance"]["source"] = "authorization-granted"
    with pytest.raises(ChamferFixtureCreationAuthorizationReviewValidationError, match="forbidden_provenance_reference_detected"):
        build_chamfer_fixture_creation_authorization_review(p)


def test_hash_exclusion_and_hash_change() -> None:
    packet = build_chamfer_fixture_creation_authorization_review(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_fixture_creation_authorization_review_hash(packet) == compute_chamfer_fixture_creation_authorization_review_hash(altered)
    p2 = _payload()
    p2["authorization_findings"] = [{**default_authorization_findings()[0], "description": "changed"}]
    changed = build_chamfer_fixture_creation_authorization_review(p2)
    assert packet["canonical_hash"] != changed["canonical_hash"]


def test_schema_and_id_refs() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_fixture_creation_authorization_review.v1.schema.json").read_text(encoding="utf-8"))
    packet = build_chamfer_fixture_creation_authorization_review(_payload())
    jsonschema.validate(packet, schema)
    assert all(isinstance(x, str) and ":" in x for x in packet["source_fixture_readiness_review_refs"])
