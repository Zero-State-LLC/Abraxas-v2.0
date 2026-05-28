from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash
from core.chamfer_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS

SCHEMA_VERSION = "ChamferFixtureCreationActualPRGate.v1"
GATE_TYPE = "CHAMFER_FIXTURE_CREATION_ACTUAL_PR_GATE"
OPERATOR_ID = "CHAMFER_DISTANCE"
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("ACTUAL_PR_GATE_ONLY", "OPERATOR_REVIEW_HELD", "BLOCKED_PENDING_OPERATOR_REVIEW")
FORBIDDEN = (
    "runtime", "scheduler", "cache", "forecast", "scoring", "metric-value", "chamfer-distance", "expected-distance",
    "tolerance-value", "fixture-file-created", "manifest-file-created", "gpu-kernel", "authority-flag", "authorization-granted",
)


class ChamferFixtureCreationActualPRGateValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_source_refs() -> dict[str, list[str]]:
    return {
        "source_pr_plan_refs": ["ChamferFixtureCreationPRPlan.v1:chamfer-fixture-creation-pr-plan-001"],
        "source_archive_receipt_refs": ["REPO_ARCHIVE_RECEIPT_CHAMFER_FIXTURE_CREATION_PR_PLAN_v0_1"],
    }


def default_proposed_fixture_directories() -> list[str]:
    return ["fixtures/chamfer/valid", "fixtures/chamfer/invalid", "fixtures/chamfer/not_computable"]


def default_fixture_batches() -> dict[str, list[str]]:
    return {
        "valid_fixture_batches": ["valid_batch_core_v1"],
        "invalid_fixture_batches": ["invalid_batch_core_v1"],
        "not_computable_fixture_batches": ["not_computable_batch_core_v1"],
    }


def default_blockers() -> list[dict[str, str]]:
    return [{
        "blocker_id": "blocker-001",
        "blocker_type": "OPERATOR_APPROVAL_REQUIRED",
        "description": "Fixture creation remains unauthorized until operator approval is explicitly recorded.",
    }]


def default_validation_requirements() -> list[str]:
    return [
        "run_fast_ci_pass_required",
        "governance_true_scan_must_be_empty_for_new_surfaces",
        "fixture_value_math_non_emission_scan_must_be_empty_for_new_surfaces",
    ]


def default_gate_constraints() -> dict[str, bool]:
    return {
        "fixture_creation_authorized": False,
        "fixture_files_added": False,
        "manifest_file_added": False,
        "expected_distances_added": False,
        "tolerance_values_added": False,
        "chamfer_math_added": False,
        "metric_values_emitted": False,
        "runtime_binding_added": False,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_fixture_files": False,
        "emits_manifest_file": False,
        "emits_expected_distances": False,
        "emits_tolerance_values": False,
        "emits_metric_values": False,
        "emits_chamfer_math": False,
        "emits_runtime_binding": False,
        "emits_gate_metadata_only": True,
    }


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ChamferFixtureCreationActualPRGateValidationError("forbidden_provenance_reference_detected")


def validate_chamfer_fixture_creation_actual_pr_gate(packet: dict[str, Any]) -> None:
    required = {
        "schema_version", "gate_id", "gate_type", "operator_id", "source_pr_plan_refs", "source_archive_receipt_refs",
        "gate_scope", "proposed_fixture_directories", "proposed_manifest_path", "required_future_pr_name",
        "required_operator_approval_state", "proposed_fixture_batches", "validation_requirements", "blockers",
        "gate_constraints", "output_contract", "stop_rule", "governance_flags", "authority_state", "provenance",
        "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise ChamferFixtureCreationActualPRGateValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferFixtureCreationActualPRGateValidationError("invalid_schema_version")
    if packet["gate_type"] != GATE_TYPE:
        raise ChamferFixtureCreationActualPRGateValidationError("invalid_gate_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferFixtureCreationActualPRGateValidationError("unknown_operator_id")
    if packet["authority_state"] != "ADVISORY_ONLY":
        raise ChamferFixtureCreationActualPRGateValidationError("invalid_authority_state")

    scope = packet["gate_scope"]
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferFixtureCreationActualPRGateValidationError("unknown_intended_lane")
    if scope.get("gate_stage") not in ALLOWED_STAGE:
        raise ChamferFixtureCreationActualPRGateValidationError("unknown_gate_stage")

    for key in ("source_pr_plan_refs", "source_archive_receipt_refs", "proposed_fixture_directories", "validation_requirements"):
        if not packet[key]:
            raise ChamferFixtureCreationActualPRGateValidationError(f"{key}_must_be_non_empty")

    batches = packet["proposed_fixture_batches"]
    for key in ("valid_fixture_batches", "invalid_fixture_batches", "not_computable_fixture_batches"):
        if not batches.get(key):
            raise ChamferFixtureCreationActualPRGateValidationError(f"{key}_must_be_non_empty")

    blockers = packet["blockers"]
    if not blockers:
        raise ChamferFixtureCreationActualPRGateValidationError("blockers_must_be_non_empty")
    seen: set[str] = set()
    for blocker in blockers:
        bid = blocker.get("blocker_id")
        if bid in seen:
            raise ChamferFixtureCreationActualPRGateValidationError("duplicate_blocker_id")
        seen.add(bid)

    if packet["gate_constraints"] != default_gate_constraints():
        raise ChamferFixtureCreationActualPRGateValidationError("invalid_gate_constraints")
    if packet["output_contract"] != default_output_contract():
        raise ChamferFixtureCreationActualPRGateValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferFixtureCreationActualPRGateValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_safe(packet["provenance"])


def compute_chamfer_fixture_creation_actual_pr_gate_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_fixture_creation_actual_pr_gate(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_fixture_creation_actual_pr_gate(payload: dict[str, Any]) -> dict[str, Any]:
    refs = default_source_refs()
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "gate_type": GATE_TYPE,
        "operator_id": OPERATOR_ID,
        "source_pr_plan_refs": sorted(payload.get("source_pr_plan_refs", refs["source_pr_plan_refs"])),
        "source_archive_receipt_refs": sorted(payload.get("source_archive_receipt_refs", refs["source_archive_receipt_refs"])),
        "proposed_fixture_directories": sorted(payload.get("proposed_fixture_directories", default_proposed_fixture_directories())),
        "proposed_fixture_batches": payload.get("proposed_fixture_batches", default_fixture_batches()),
        "validation_requirements": sorted(payload.get("validation_requirements", default_validation_requirements())),
        "blockers": sorted(payload.get("blockers", default_blockers()), key=lambda x: x["blocker_id"]),
        "gate_constraints": payload.get("gate_constraints", default_gate_constraints()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_fixture_creation_actual_pr_gate_hash(base)
    validate_chamfer_fixture_creation_actual_pr_gate(base)
    return _finalize(base)
