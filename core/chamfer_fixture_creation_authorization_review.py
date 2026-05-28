from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash
from core.chamfer_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS

SCHEMA_VERSION = "ChamferFixtureCreationAuthorizationReview.v1"
REVIEW_TYPE = "CHAMFER_FIXTURE_CREATION_AUTHORIZATION_REVIEW"
OPERATOR_ID = "CHAMFER_DISTANCE"
ALLOWED_FAMILY = (
    "FIXTURE_CREATION_AUTHORIZATION_REVIEW",
    "EXPECTED_DISTANCE_POLICY_REVIEW",
    "VALID_INVALID_NOT_COMPUTABLE_GATE_REVIEW",
    "MIXED_CREATION_AUTHORIZATION_REVIEW",
)
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("AUTHORIZATION_REVIEW_ONLY", "AUTHORIZATION_HELD", "BLOCKED_PENDING_OPERATOR_REVIEW")
ALLOWED_FINDING_TYPE = (
    "FIXTURE_READINESS_REVIEW_FINDING", "EXPECTED_DISTANCE_POLICY_FINDING", "VALID_FIXTURE_PLAN_FINDING",
    "INVALID_FIXTURE_PLAN_FINDING", "NOT_COMPUTABLE_PLAN_FINDING", "GOVERNANCE_LOCK_FINDING", "NOT_COMPUTABLE_FINDING",
)
ALLOWED_FINDING_STATUS = ("REVIEWED", "ACTIVE_BLOCKER", "HELD_FOR_REVIEW", "NOT_COMPUTABLE")
ALLOWED_IMPL_STATUS = ("REVIEWED_METADATA_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW", "HELD_FOR_OPERATOR")
ALLOWED_BLOCKER_TYPE = (
    "FIXTURE_CREATION_NOT_AUTHORIZED", "EXPECTED_DISTANCES_NOT_ADDED", "TOLERANCE_VALUES_NOT_ADDED", "CHAMFER_MATH_NOT_IMPLEMENTED",
    "NO_RUNTIME_AUTHORITY", "NO_FORECAST_AUTHORITY", "OPERATOR_REVIEW_REQUIRED", "NOT_COMPUTABLE_BLOCKER",
)
ALLOWED_BLOCKER_STATUS = ("ACTIVE", "HELD", "NOT_COMPUTABLE")
FORBIDDEN = (
    "runtime", "scheduler", "cache", "forecast", "scoring", "metric-value", "chamfer-distance", "expected-distance",
    "tolerance-value", "fixture-file", "manifest-file", "schema-file", "gpu-kernel", "authority-flag", "authorization-granted",
    "fixture-creation-authorized",
)


class ChamferFixtureCreationAuthorizationReviewValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_authorization_findings() -> list[dict[str, Any]]:
    return [{
        "finding_id": "finding-001",
        "finding_type": "FIXTURE_READINESS_REVIEW_FINDING",
        "description": "Fixture readiness review exists and remains implementation-held.",
        "evidence_refs": ["ChamferFixtureImplementationReadinessReview.v1:review-001"],
        "finding_status": "HELD_FOR_REVIEW",
        "implementation_status": "HELD_FOR_OPERATOR",
    }]


def default_blocker_findings() -> list[dict[str, Any]]:
    return [{
        "blocker_id": "blocker-001",
        "blocker_type": "FIXTURE_CREATION_NOT_AUTHORIZED",
        "description": "Fixture creation remains held at authorization review boundary.",
        "required_resolution": "Operator review and separate fixture-creation PR planning boundary.",
        "evidence_refs": ["ChamferExpectedDistancePolicyPlan.v1:policy-001"],
        "blocker_status": "HELD",
    }]


def default_authorization_decision() -> dict[str, bool | str]:
    return {
        "decision_status": "AUTHORIZATION_HELD",
        "fixture_creation_authorized": False,
        "expected_values_authorized": False,
        "tolerance_values_authorized": False,
        "requires_new_fixture_creation_pr": True,
        "requires_operator_review": True,
        "requires_no_authority_scan": True,
        "requires_expected_distance_policy": True,
    }


def default_creation_constraints() -> dict[str, bool]:
    return {
        "fixture_files_added": False,
        "expected_distances_added": False,
        "tolerance_values_added": False,
        "metric_values_added": False,
        "chamfer_math_added": False,
        "scoring_added": False,
        "runtime_binding_added": False,
        "forecast_influence_added": False,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_fixture_files": False,
        "emits_expected_distances": False,
        "emits_tolerance_values": False,
        "emits_metric_values": False,
        "emits_chamfer_outputs": False,
        "emits_scores": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_authorization_review": True,
        "emits_blocker_summary": True,
        "emits_next_boundary_options": True,
    }


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ChamferFixtureCreationAuthorizationReviewValidationError("forbidden_provenance_reference_detected")


def validate_chamfer_fixture_creation_authorization_review(packet: dict[str, Any]) -> None:
    required = {
        "schema_version", "review_id", "review_type", "operator_id", "source_fixture_readiness_review_refs",
        "source_expected_distance_policy_plan_refs", "source_fixture_consolidation_receipt_refs", "source_valid_fixture_plan_refs",
        "source_invalid_fixture_plan_refs", "source_not_computable_fixture_plan_refs", "source_schema_plan_refs",
        "source_baseline_implementation_plan_refs", "authorization_scope", "authorization_findings", "blocker_findings",
        "authorization_decision", "creation_constraints", "output_contract", "governance_flags", "provenance", "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise ChamferFixtureCreationAuthorizationReviewValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferFixtureCreationAuthorizationReviewValidationError("invalid_schema_version")
    if packet["review_type"] != REVIEW_TYPE:
        raise ChamferFixtureCreationAuthorizationReviewValidationError("invalid_review_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferFixtureCreationAuthorizationReviewValidationError("unknown_operator_id")

    scope = packet["authorization_scope"]
    if scope.get("authorization_family") not in ALLOWED_FAMILY:
        raise ChamferFixtureCreationAuthorizationReviewValidationError("unknown_authorization_family")
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferFixtureCreationAuthorizationReviewValidationError("unknown_intended_lane")
    if scope.get("authorization_stage") not in ALLOWED_STAGE:
        raise ChamferFixtureCreationAuthorizationReviewValidationError("unknown_authorization_stage")

    findings = packet["authorization_findings"]
    if not findings:
        raise ChamferFixtureCreationAuthorizationReviewValidationError("authorization_findings_must_be_non_empty")
    seen_f: set[str] = set()
    for finding in findings:
        fid = finding.get("finding_id")
        if fid in seen_f:
            raise ChamferFixtureCreationAuthorizationReviewValidationError("duplicate_finding_id")
        seen_f.add(fid)
        if finding.get("finding_type") not in ALLOWED_FINDING_TYPE:
            raise ChamferFixtureCreationAuthorizationReviewValidationError("unknown_finding_type")
        if finding.get("finding_status") not in ALLOWED_FINDING_STATUS:
            raise ChamferFixtureCreationAuthorizationReviewValidationError("unknown_finding_status")
        if finding.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise ChamferFixtureCreationAuthorizationReviewValidationError("unknown_implementation_status")

    blockers = packet["blocker_findings"]
    if not blockers:
        raise ChamferFixtureCreationAuthorizationReviewValidationError("blocker_findings_must_be_non_empty")
    seen_b: set[str] = set()
    for blocker in blockers:
        bid = blocker.get("blocker_id")
        if bid in seen_b:
            raise ChamferFixtureCreationAuthorizationReviewValidationError("duplicate_blocker_id")
        seen_b.add(bid)
        if blocker.get("blocker_type") not in ALLOWED_BLOCKER_TYPE:
            raise ChamferFixtureCreationAuthorizationReviewValidationError("unknown_blocker_type")
        if blocker.get("blocker_status") not in ALLOWED_BLOCKER_STATUS:
            raise ChamferFixtureCreationAuthorizationReviewValidationError("unknown_blocker_status")

    if packet["authorization_decision"] != default_authorization_decision():
        raise ChamferFixtureCreationAuthorizationReviewValidationError("invalid_authorization_decision")
    if packet["creation_constraints"] != default_creation_constraints():
        raise ChamferFixtureCreationAuthorizationReviewValidationError("invalid_creation_constraints")
    if packet["output_contract"] != default_output_contract():
        raise ChamferFixtureCreationAuthorizationReviewValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferFixtureCreationAuthorizationReviewValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_safe(packet["provenance"])


def compute_chamfer_fixture_creation_authorization_review_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_fixture_creation_authorization_review(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_fixture_creation_authorization_review(payload: dict[str, Any]) -> dict[str, Any]:
    findings = sorted(payload.get("authorization_findings", default_authorization_findings()), key=lambda x: x["finding_id"])
    for f in findings:
        f["evidence_refs"] = sorted(f.get("evidence_refs", []))
    blockers = sorted(payload.get("blocker_findings", default_blocker_findings()), key=lambda x: x["blocker_id"])
    for b in blockers:
        b["evidence_refs"] = sorted(b.get("evidence_refs", []))

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "source_fixture_readiness_review_refs": sorted(payload.get("source_fixture_readiness_review_refs", [])),
        "source_expected_distance_policy_plan_refs": sorted(payload.get("source_expected_distance_policy_plan_refs", [])),
        "source_fixture_consolidation_receipt_refs": sorted(payload.get("source_fixture_consolidation_receipt_refs", [])),
        "source_valid_fixture_plan_refs": sorted(payload.get("source_valid_fixture_plan_refs", [])),
        "source_invalid_fixture_plan_refs": sorted(payload.get("source_invalid_fixture_plan_refs", [])),
        "source_not_computable_fixture_plan_refs": sorted(payload.get("source_not_computable_fixture_plan_refs", [])),
        "source_schema_plan_refs": sorted(payload.get("source_schema_plan_refs", [])),
        "source_baseline_implementation_plan_refs": sorted(payload.get("source_baseline_implementation_plan_refs", [])),
        "authorization_findings": findings,
        "blocker_findings": blockers,
        "authorization_decision": payload.get("authorization_decision", default_authorization_decision()),
        "creation_constraints": payload.get("creation_constraints", default_creation_constraints()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_fixture_creation_authorization_review_hash(base)
    validate_chamfer_fixture_creation_authorization_review(base)
    return _finalize(base)
