from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash
from core.chamfer_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS

SCHEMA_VERSION = "ChamferFixtureCreationPRPlan.v1"
PLAN_TYPE = "CHAMFER_FIXTURE_CREATION_PR_PLAN"
OPERATOR_ID = "CHAMFER_DISTANCE"
ALLOWED_FAMILY = (
    "FIXTURE_CREATION_PR_PLANNING_ONLY",
    "NO_FIXTURE_FILES",
    "NO_EXPECTED_VALUES",
    "NO_METRIC_VALUES",
)
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("PR_PLAN_ONLY", "AUTHORIZATION_HELD", "BLOCKED_PENDING_OPERATOR_REVIEW")


class ChamferFixtureCreationPRPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_phase_statuses() -> list[dict[str, Any]]:
    return [
        {"phase_id": "phase-001", "phase_name": "Repo inventory", "phase_status": "PLANNED"},
        {"phase_id": "phase-002", "phase_name": "Contract design", "phase_status": "PLANNED"},
        {"phase_id": "phase-003", "phase_name": "Core builder behavior", "phase_status": "PLANNED"},
        {"phase_id": "phase-004", "phase_name": "Tests", "phase_status": "PLANNED"},
        {"phase_id": "phase-005", "phase_name": "Audit receipt", "phase_status": "PLANNED"},
        {"phase_id": "phase-006", "phase_name": "Fast-CI update", "phase_status": "PLANNED"},
        {"phase_id": "phase-007", "phase_name": "Validation", "phase_status": "PLANNED"},
        {"phase_id": "phase-008", "phase_name": "Output report", "phase_status": "PLANNED"},
    ]


def default_source_authorization_review_refs() -> list[str]:
    return ["ChamferFixtureCreationAuthorizationReview.v1:auth-review-001"]


def default_source_expected_distance_policy_plan_refs() -> list[str]:
    return ["ChamferExpectedDistancePolicyPlan.v1:policy-001"]


def default_planned_pr_surfaces() -> list[dict[str, str]]:
    return [
        {"surface_id": "surface-001", "surface_name": "core/chamfer_fixture_creation_pr_plan.py", "surface_kind": "CORE_BUILDER"},
        {"surface_id": "surface-002", "surface_name": "contracts/canon/chamfer_fixture_creation_pr_plan.v1.schema.json", "surface_kind": "SCHEMA_CONTRACT"},
        {"surface_id": "surface-003", "surface_name": "tests/test_chamfer_fixture_creation_pr_plan.py", "surface_kind": "TARGETED_TEST"},
        {"surface_id": "surface-004", "surface_name": "scripts/run_fast_ci.py", "surface_kind": "FAST_CI_SCOPE"},
        {"surface_id": "surface-005", "surface_name": "core/chamfer_fixture_creation_authorization_review.py", "surface_kind": "UPSTREAM_REVIEW_LINK"},
        {"surface_id": "surface-006", "surface_name": "core/chamfer_expected_distance_policy_plan.py", "surface_kind": "UPSTREAM_POLICY_LINK"},
        {"surface_id": "surface-007", "surface_name": "tests/test_run_fast_ci.py", "surface_kind": "VALIDATION_COVERAGE"},
    ]


def default_planned_fixture_groups() -> list[dict[str, str]]:
    return [
        {"group_id": "group-001", "group_name": "VALID_FIXTURES", "group_status": "PLANNED_NO_CREATION"},
        {"group_id": "group-002", "group_name": "INVALID_FIXTURES", "group_status": "PLANNED_NO_CREATION"},
        {"group_id": "group-003", "group_name": "NOT_COMPUTABLE_FIXTURES", "group_status": "PLANNED_NO_CREATION"},
    ]


def default_constraints() -> dict[str, bool]:
    return {
        "fixture_creation_authorized": False,
        "fixture_files_added": False,
        "manifest_file_added": False,
        "expected_distances_added": False,
        "tolerance_values_added": False,
        "chamfer_math_added": False,
        "metric_values_emitted": False,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_fixture_files": False,
        "emits_manifest_file": False,
        "emits_expected_distances": False,
        "emits_tolerance_values": False,
        "emits_chamfer_math": False,
        "emits_metric_values": False,
        "emits_authority_tokens": False,
        "emits_pr_plan_metadata": True,
    }


def validate_chamfer_fixture_creation_pr_plan(packet: dict[str, Any]) -> None:
    required = {
        "schema_version", "plan_id", "plan_type", "operator_id", "source_authorization_review_refs",
        "source_expected_distance_policy_plan_refs", "planning_scope", "phase_statuses", "planned_pr_surfaces",
        "planned_fixture_groups", "constraints",
        "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise ChamferFixtureCreationPRPlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferFixtureCreationPRPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise ChamferFixtureCreationPRPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferFixtureCreationPRPlanValidationError("unknown_operator_id")

    scope = packet["planning_scope"]
    if scope.get("plan_family") not in ALLOWED_FAMILY:
        raise ChamferFixtureCreationPRPlanValidationError("unknown_plan_family")
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferFixtureCreationPRPlanValidationError("unknown_intended_lane")
    if scope.get("plan_stage") not in ALLOWED_STAGE:
        raise ChamferFixtureCreationPRPlanValidationError("unknown_plan_stage")

    if not packet["source_authorization_review_refs"]:
        raise ChamferFixtureCreationPRPlanValidationError("source_authorization_review_refs_must_be_non_empty")
    if not packet["source_expected_distance_policy_plan_refs"]:
        raise ChamferFixtureCreationPRPlanValidationError("source_expected_distance_policy_plan_refs_must_be_non_empty")

    if packet["phase_statuses"] != default_phase_statuses():
        raise ChamferFixtureCreationPRPlanValidationError("invalid_phase_statuses")
    if packet["planned_pr_surfaces"] != default_planned_pr_surfaces():
        raise ChamferFixtureCreationPRPlanValidationError("invalid_planned_pr_surfaces")
    if packet["planned_fixture_groups"] != default_planned_fixture_groups():
        raise ChamferFixtureCreationPRPlanValidationError("invalid_planned_fixture_groups")
    if packet["constraints"] != default_constraints():
        raise ChamferFixtureCreationPRPlanValidationError("invalid_constraints")
    if packet["output_contract"] != default_output_contract():
        raise ChamferFixtureCreationPRPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferFixtureCreationPRPlanValidationError(f"authority_lock_must_be_false:{flag}")


def compute_chamfer_fixture_creation_pr_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_fixture_creation_pr_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_fixture_creation_pr_plan(payload: dict[str, Any]) -> dict[str, Any]:
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_authorization_review_refs": sorted(payload.get("source_authorization_review_refs", default_source_authorization_review_refs())),
        "source_expected_distance_policy_plan_refs": sorted(payload.get("source_expected_distance_policy_plan_refs", default_source_expected_distance_policy_plan_refs())),
        "phase_statuses": payload.get("phase_statuses", default_phase_statuses()),
        "planned_pr_surfaces": payload.get("planned_pr_surfaces", default_planned_pr_surfaces()),
        "planned_fixture_groups": payload.get("planned_fixture_groups", default_planned_fixture_groups()),
        "constraints": payload.get("constraints", default_constraints()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_fixture_creation_pr_plan_hash(base)
    validate_chamfer_fixture_creation_pr_plan(base)
    return _finalize(base)
