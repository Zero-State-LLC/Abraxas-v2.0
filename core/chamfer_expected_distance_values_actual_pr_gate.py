from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash
from core.chamfer_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS

SCHEMA_VERSION = "ChamferExpectedDistanceValuesActualPRGate.v1"
GATE_TYPE = "CHAMFER_EXPECTED_DISTANCE_VALUES_ACTUAL_PR_GATE"
OPERATOR_ID = "CHAMFER_DISTANCE"
ALLOWED_GATE_FAMILY = (
    "EXPECTED_DISTANCE_VALUE_ACTUAL_PR_GATE",
    "VALUE_ELIGIBILITY_REVIEW_GATE",
    "FIXTURE_VALUE_MAPPING_GATE",
)
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("GATE_ONLY", "VALUES_HELD", "BLOCKED_PENDING_OPERATOR_REVIEW")
ALLOWED_ELIGIBILITY = ("ELIGIBLE_FOR_FUTURE_VALUE", "HELD_PENDING_OPERATOR_REVIEW")
ALLOWED_EXPECTED = ("NOT_ADDED", "PLANNED_ONLY", "HELD_PENDING_VALUE_PR")
ALLOWED_TOLERANCE = ("NOT_ADDED", "PLANNED_ONLY", "HELD_PENDING_POLICY")
ALLOWED_IMPL = ("GATE_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
ALLOWED_NULL_REASON = (
    "INVALID_INPUT",
    "NOT_COMPUTABLE_INPUT",
    "MISSING_POLICY",
    "AMBIGUOUS_INTERPRETATION",
    "INPUT_CONTRACT_VIOLATION",
)
ALLOWED_NULL_EXPECTED = (
    "MUST_REMAIN_NULL",
    "NOT_COMPUTABLE_NULL",
    "INVALID_INPUT_NULL",
)
FORBIDDEN_PROVENANCE = (
    "runtime execution",
    "scheduler mutation",
    "forecast influence",
    "metric output",
    "expected distance value added",
    "tolerance value added",
    "chamfer math enabled",
    "authority granted",
    "activation approved",
)
VALID_FIXTURE_IDS = {
    "identical_point_sets",
    "offset_point_sets",
    "partial_overlap_point_sets",
    "duplicate_points",
    "multidimensional_points",
}
NULL_LOCKED_REQUIRED = {
    "dimension_mismatch": "INVALID_INPUT",
    "empty_point_set": "INVALID_INPUT",
    "malformed_coordinates": "INVALID_INPUT",
    "missing_point_set": "INPUT_CONTRACT_VIOLATION",
    "non_numeric_coordinate": "INVALID_INPUT",
    "missing_numerical_policy": "NOT_COMPUTABLE_INPUT",
    "undeclared_dimensionality": "NOT_COMPUTABLE_INPUT",
    "unknown_coordinate_space": "NOT_COMPUTABLE_INPUT",
}


class ChamferExpectedDistanceValuesActualPRGateValidationError(ValueError): ...


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_expected_value_authorization_state() -> dict[str, bool]:
    return {
        "expected_values_authorized": False,
        "expected_distances_added": False,
        "expected_values_require_separate_pr": True,
        "operator_review_required": True,
        "value_formula_required": True,
        "fixture_hash_verification_required": True,
    }


def default_tolerance_authorization_state() -> dict[str, bool]:
    return {
        "tolerance_values_authorized": False,
        "tolerance_values_added": False,
        "tolerance_policy_required": True,
        "tolerance_values_require_separate_pr": True,
    }


def default_value_creation_constraints() -> dict[str, bool]:
    return {
        "expected_distances_added": False,
        "tolerance_values_added": False,
        "chamfer_math_added": False,
        "metric_values_emitted": False,
        "runtime_loading_enabled": False,
        "forecast_influence_added": False,
    }


def default_validation_plan() -> dict[str, bool]:
    return {
        "requires_fixture_manifest": True,
        "requires_fixture_hash_verification": True,
        "requires_expected_distance_value_plan": True,
        "requires_expected_distance_value_plan_archive": True,
        "requires_no_existing_expected_values_scan": True,
        "requires_no_tolerance_values_scan": True,
        "requires_no_chamfer_math_scan": True,
        "requires_no_metric_value_scan": True,
        "requires_no_runtime_loading_scan": True,
        "requires_no_authority_scan": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_expected_distances": False,
        "emits_tolerance_values": False,
        "emits_chamfer_outputs": False,
        "emits_metric_values": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_gate_metadata": True,
        "emits_eligible_fixture_refs": True,
        "emits_null_locked_fixture_refs": True,
    }


def default_eligible_value_fixture_refs() -> list[dict[str, str]]:
    return [
        {
            "fixture_id": fid,
            "fixture_path": f"input/fixtures/chamfer/valid/{fid}.v1.json",
            "eligibility_status": "ELIGIBLE_FOR_FUTURE_VALUE",
            "expected_distance_status": "HELD_PENDING_VALUE_PR",
            "tolerance_status": "HELD_PENDING_POLICY",
            "implementation_status": "GATE_ONLY",
        }
        for fid in sorted(VALID_FIXTURE_IDS)
    ]


def default_null_locked_fixture_refs() -> list[dict[str, str]]:
    entries = []
    for fid, reason in sorted(NULL_LOCKED_REQUIRED.items()):
        status = (
            "INVALID_INPUT_NULL"
            if reason in {"INVALID_INPUT", "INPUT_CONTRACT_VIOLATION"}
            else "NOT_COMPUTABLE_NULL"
        )
        kind = (
            "invalid"
            if fid
            in {
                "dimension_mismatch",
                "empty_point_set",
                "malformed_coordinates",
                "missing_point_set",
                "non_numeric_coordinate",
            }
            else "not_computable"
        )
        entries.append(
            {
                "fixture_id": fid,
                "fixture_path": f"input/fixtures/chamfer/{kind}/{fid}.v1.json",
                "null_lock_reason": reason,
                "expected_distance_status": status,
                "implementation_status": "BLOCKED_PENDING_REVIEW",
            }
        )
    return entries


def default_blocker_findings() -> list[dict[str, str]]:
    return [
        {
            "finding_id": "blocker-001",
            "finding": "Expected-distance and tolerance value insertion requires separate operator-reviewed PR with formula and hash verification.",
        }
    ]


def _assert_provenance_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_provenance_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_provenance_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN_PROVENANCE):
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "forbidden_provenance_tokens_detected"
        )


def validate_chamfer_expected_distance_values_actual_pr_gate(
    packet: dict[str, Any],
) -> None:
    req = {
        "schema_version",
        "gate_id",
        "gate_type",
        "operator_id",
        "source_fixture_manifest_refs",
        "source_fixture_archive_receipt_refs",
        "source_expected_distance_value_plan_refs",
        "source_expected_distance_value_plan_archive_refs",
        "source_fixture_file_refs",
        "gate_scope",
        "eligible_value_fixture_refs",
        "null_locked_fixture_refs",
        "expected_value_authorization_state",
        "tolerance_authorization_state",
        "value_creation_constraints",
        "validation_plan",
        "blocker_findings",
        "output_contract",
        "governance_flags",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    miss = sorted(req - packet.keys())
    if miss:
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            f"missing_required_fields:{miss}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "invalid_schema_version"
        )
    if packet["gate_type"] != GATE_TYPE:
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "invalid_gate_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "unknown_operator_id"
        )
    for k in (
        "source_fixture_manifest_refs",
        "source_fixture_archive_receipt_refs",
        "source_expected_distance_value_plan_refs",
        "source_expected_distance_value_plan_archive_refs",
        "source_fixture_file_refs",
        "eligible_value_fixture_refs",
        "null_locked_fixture_refs",
        "blocker_findings",
    ):
        if not packet[k]:
            raise ChamferExpectedDistanceValuesActualPRGateValidationError(
                f"{k}_must_be_non_empty"
            )
    scope = packet["gate_scope"]
    if scope.get("gate_family") not in ALLOWED_GATE_FAMILY:
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "unknown_gate_family"
        )
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "unknown_intended_lane"
        )
    if scope.get("gate_stage") not in ALLOWED_STAGE:
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "unknown_gate_stage"
        )

    seen = set()
    for e in packet["eligible_value_fixture_refs"]:
        fid = e.get("fixture_id")
        if fid in seen:
            raise ChamferExpectedDistanceValuesActualPRGateValidationError(
                "duplicate_eligible_fixture_id"
            )
        seen.add(fid)
        if fid not in VALID_FIXTURE_IDS:
            raise ChamferExpectedDistanceValuesActualPRGateValidationError(
                "invalid_eligible_fixture_id"
            )
        if (
            e.get("eligibility_status") not in ALLOWED_ELIGIBILITY
            or e.get("expected_distance_status") not in ALLOWED_EXPECTED
            or e.get("tolerance_status") not in ALLOWED_TOLERANCE
            or e.get("implementation_status") not in ALLOWED_IMPL
        ):
            raise ChamferExpectedDistanceValuesActualPRGateValidationError(
                "unknown_eligible_fixture_enum"
            )

    seen = set()
    for e in packet["null_locked_fixture_refs"]:
        fid = e.get("fixture_id")
        if fid in seen:
            raise ChamferExpectedDistanceValuesActualPRGateValidationError(
                "duplicate_null_locked_fixture_id"
            )
        seen.add(fid)
        if (
            fid in VALID_FIXTURE_IDS
            and e.get("null_lock_reason") != "AMBIGUOUS_INTERPRETATION"
        ):
            raise ChamferExpectedDistanceValuesActualPRGateValidationError(
                "valid_fixture_improperly_null_locked"
            )
        if fid in VALID_FIXTURE_IDS and fid in seen:
            pass
        if fid in VALID_FIXTURE_IDS:
            continue
        if fid not in NULL_LOCKED_REQUIRED:
            raise ChamferExpectedDistanceValuesActualPRGateValidationError(
                "invalid_null_locked_fixture_id"
            )
        if (
            e.get("null_lock_reason") not in ALLOWED_NULL_REASON
            or e.get("expected_distance_status") not in ALLOWED_NULL_EXPECTED
            or e.get("implementation_status") not in ALLOWED_IMPL
        ):
            raise ChamferExpectedDistanceValuesActualPRGateValidationError(
                "unknown_null_locked_fixture_enum"
            )

    if not set(NULL_LOCKED_REQUIRED).issubset(
        {x.get("fixture_id") for x in packet["null_locked_fixture_refs"]}
    ):
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "missing_required_null_locked_fixture_ids"
        )

    if (
        packet["expected_value_authorization_state"]
        != default_expected_value_authorization_state()
    ):
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "invalid_expected_value_authorization_state"
        )
    if (
        packet["tolerance_authorization_state"]
        != default_tolerance_authorization_state()
    ):
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "invalid_tolerance_authorization_state"
        )
    if packet["value_creation_constraints"] != default_value_creation_constraints():
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "invalid_value_creation_constraints"
        )
    if packet["validation_plan"] != default_validation_plan():
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "invalid_validation_plan"
        )
    if packet["output_contract"] != default_output_contract():
        raise ChamferExpectedDistanceValuesActualPRGateValidationError(
            "invalid_output_contract"
        )
    for f in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(f) is not False:
            raise ChamferExpectedDistanceValuesActualPRGateValidationError(
                f"authority_lock_must_be_false:{f}"
            )
    _assert_provenance_safe(packet["provenance"])


def compute_chamfer_expected_distance_values_actual_pr_gate_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_expected_distance_values_actual_pr_gate(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_expected_distance_values_actual_pr_gate(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "gate_type": GATE_TYPE,
        "operator_id": OPERATOR_ID,
        "source_fixture_manifest_refs": sorted(
            payload.get("source_fixture_manifest_refs", ["chamfer.fixture.manifest.v1"])
        ),
        "source_fixture_archive_receipt_refs": sorted(
            payload.get(
                "source_fixture_archive_receipt_refs",
                ["REPO_ARCHIVE_RECEIPT_CHAMFER_FIXTURE_FILES_ACTUAL_PR_v0_1"],
            )
        ),
        "source_expected_distance_value_plan_refs": sorted(
            payload.get(
                "source_expected_distance_value_plan_refs",
                ["chamfer.expected_distance.value.plan.v1"],
            )
        ),
        "source_expected_distance_value_plan_archive_refs": sorted(
            payload.get(
                "source_expected_distance_value_plan_archive_refs",
                ["REPO_ARCHIVE_RECEIPT_CHAMFER_EXPECTED_DISTANCE_VALUE_PLAN_v0_1"],
            )
        ),
        "source_fixture_file_refs": sorted(
            payload.get(
                "source_fixture_file_refs",
                [f"chamfer.valid.{x}.v1" for x in sorted(VALID_FIXTURE_IDS)]
                + [
                    f"chamfer.invalid.{x}.v1"
                    for x in [
                        "dimension_mismatch",
                        "empty_point_set",
                        "malformed_coordinates",
                        "missing_point_set",
                        "non_numeric_coordinate",
                    ]
                ]
                + [
                    f"chamfer.not_computable.{x}.v1"
                    for x in [
                        "missing_numerical_policy",
                        "undeclared_dimensionality",
                        "unknown_coordinate_space",
                    ]
                ],
            )
        ),
        "eligible_value_fixture_refs": sorted(
            payload.get(
                "eligible_value_fixture_refs", default_eligible_value_fixture_refs()
            ),
            key=lambda x: x["fixture_id"],
        ),
        "null_locked_fixture_refs": sorted(
            payload.get("null_locked_fixture_refs", default_null_locked_fixture_refs()),
            key=lambda x: x["fixture_id"],
        ),
        "expected_value_authorization_state": payload.get(
            "expected_value_authorization_state",
            default_expected_value_authorization_state(),
        ),
        "tolerance_authorization_state": payload.get(
            "tolerance_authorization_state", default_tolerance_authorization_state()
        ),
        "value_creation_constraints": payload.get(
            "value_creation_constraints", default_value_creation_constraints()
        ),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "blocker_findings": sorted(
            payload.get("blocker_findings", default_blocker_findings()),
            key=lambda x: x["finding_id"],
        ),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = (
        compute_chamfer_expected_distance_values_actual_pr_gate_hash(base)
    )
    validate_chamfer_expected_distance_values_actual_pr_gate(base)
    return _finalize(base)
