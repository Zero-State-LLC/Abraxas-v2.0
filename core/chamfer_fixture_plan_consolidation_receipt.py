from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash
from core.chamfer_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS

SCHEMA_VERSION = "ChamferFixturePlanConsolidationReceipt.v1"
RECEIPT_TYPE = "CHAMFER_FIXTURE_PLAN_CONSOLIDATION_RECEIPT"
OPERATOR_ID = "CHAMFER_DISTANCE"
ALLOWED_FAMILY = (
    "VALID_INVALID_NOT_COMPUTABLE_TRIAD",
    "FIXTURE_PLAN_CHAIN",
    "TEST_VECTOR_FIXTURE_PLANNING",
    "MIXED_FIXTURE_CONSOLIDATION",
)
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("CONSOLIDATION_RECEIPT_ONLY", "READINESS_SUMMARY_ONLY", "BLOCKED_PENDING_OPERATOR_REVIEW")
ALLOWED_SURFACE_TYPE = (
    "VALID_FIXTURE_IMPLEMENTATION_PLAN",
    "INVALID_FIXTURE_IMPLEMENTATION_PLAN",
    "NOT_COMPUTABLE_FIXTURE_IMPLEMENTATION_PLAN",
    "TEST_VECTOR_SCHEMA_PLAN",
    "BASELINE_IMPLEMENTATION_PLAN",
)
ALLOWED_CONSOLIDATION_STATUS = (
    "PRESENT_AND_VALIDATED",
    "PRESENT_METADATA_ONLY",
    "MISSING_OR_NOT_COMPUTABLE",
    "BLOCKED_PENDING_REVIEW",
)
ALLOWED_IMPL_STATUS = ("REVIEWED_METADATA_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
ALLOWED_FINDING_TYPE = (
    "VALID_FIXTURE_PLAN_FINDING",
    "INVALID_FIXTURE_PLAN_FINDING",
    "NOT_COMPUTABLE_PLAN_FINDING",
    "SCHEMA_PLAN_FINDING",
    "BASELINE_PLAN_FINDING",
    "GOVERNANCE_LOCK_FINDING",
    "NOT_COMPUTABLE_FINDING",
)
ALLOWED_FINDING_STATUS = ("SATISFIED", "ACTIVE_BLOCKER", "HELD_FOR_REVIEW", "NOT_COMPUTABLE")
FORBIDDEN = (
    "runtime", "scheduler", "cache", "forecast", "scoring", "metric-value", "chamfer-distance", "expected-distance",
    "fixture-file", "manifest-file", "schema-file", "gpu-kernel", "authority-flag"
)


class ChamferFixturePlanConsolidationReceiptValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_consolidated_surfaces() -> list[dict[str, Any]]:
    return [
        {
            "surface_id": "surface-001",
            "surface_type": "VALID_FIXTURE_IMPLEMENTATION_PLAN",
            "description": "Valid fixture planning surface observed.",
            "source_refs": ["ChamferValidFixtureImplementationPlan.v1:plan-001"],
            "consolidation_status": "PRESENT_AND_VALIDATED",
            "implementation_status": "REVIEWED_METADATA_ONLY",
        }
    ]


def default_consolidation_findings() -> list[dict[str, Any]]:
    return [
        {
            "finding_id": "finding-001",
            "finding_type": "GOVERNANCE_LOCK_FINDING",
            "description": "Authority and output locks remain metadata-only.",
            "evidence_refs": ["ChamferInvalidFixtureImplementationPlan.v1:plan-001"],
            "finding_status": "SATISFIED",
            "implementation_status": "REVIEWED_METADATA_ONLY",
        }
    ]


def default_readiness_constraints() -> dict[str, bool]:
    return {
        "valid_fixture_plan_present": True,
        "invalid_fixture_plan_present": True,
        "not_computable_fixture_plan_present": True,
        "schema_plan_present": True,
        "baseline_plan_present": True,
        "fixture_files_required_before_implementation": True,
        "expected_distances_required_before_metric_execution": True,
        "operator_review_required": True,
        "implementation_allowed": False,
    }


def default_fixture_constraints() -> dict[str, bool]:
    return {
        "fixture_files_added": False,
        "expected_distances_added": False,
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
        "emits_metric_values": False,
        "emits_chamfer_outputs": False,
        "emits_scores": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_consolidation_receipt": True,
        "emits_readiness_summary": True,
        "emits_blocker_summary": True,
    }


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ChamferFixturePlanConsolidationReceiptValidationError("forbidden_provenance_reference_detected")


def validate_chamfer_fixture_plan_consolidation_receipt(packet: dict[str, Any]) -> None:
    required = {
        "schema_version", "receipt_id", "receipt_type", "operator_id", "source_valid_fixture_plan_refs",
        "source_invalid_fixture_plan_refs", "source_not_computable_fixture_plan_refs", "source_schema_plan_refs",
        "source_baseline_implementation_plan_refs", "consolidation_scope", "consolidated_surfaces", "consolidation_findings",
        "readiness_constraints", "fixture_constraints", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash"
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise ChamferFixturePlanConsolidationReceiptValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferFixturePlanConsolidationReceiptValidationError("invalid_schema_version")
    if packet["receipt_type"] != RECEIPT_TYPE:
        raise ChamferFixturePlanConsolidationReceiptValidationError("invalid_receipt_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise ChamferFixturePlanConsolidationReceiptValidationError("unknown_operator_id")

    scope = packet["consolidation_scope"]
    if scope.get("consolidation_family") not in ALLOWED_FAMILY:
        raise ChamferFixturePlanConsolidationReceiptValidationError("unknown_consolidation_family")
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferFixturePlanConsolidationReceiptValidationError("unknown_intended_lane")
    if scope.get("consolidation_stage") not in ALLOWED_STAGE:
        raise ChamferFixturePlanConsolidationReceiptValidationError("unknown_consolidation_stage")

    surfaces = packet["consolidated_surfaces"]
    if not surfaces:
        raise ChamferFixturePlanConsolidationReceiptValidationError("consolidated_surfaces_must_be_non_empty")
    seen_surface: set[str] = set()
    for s in surfaces:
        sid = s.get("surface_id")
        if sid in seen_surface:
            raise ChamferFixturePlanConsolidationReceiptValidationError("duplicate_surface_id")
        seen_surface.add(sid)
        if s.get("surface_type") not in ALLOWED_SURFACE_TYPE:
            raise ChamferFixturePlanConsolidationReceiptValidationError("unknown_surface_type")
        if s.get("consolidation_status") not in ALLOWED_CONSOLIDATION_STATUS:
            raise ChamferFixturePlanConsolidationReceiptValidationError("unknown_consolidation_status")
        if s.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise ChamferFixturePlanConsolidationReceiptValidationError("unknown_implementation_status")

    findings = packet["consolidation_findings"]
    if not findings:
        raise ChamferFixturePlanConsolidationReceiptValidationError("consolidation_findings_must_be_non_empty")
    seen_finding: set[str] = set()
    for f in findings:
        fid = f.get("finding_id")
        if fid in seen_finding:
            raise ChamferFixturePlanConsolidationReceiptValidationError("duplicate_finding_id")
        seen_finding.add(fid)
        if f.get("finding_type") not in ALLOWED_FINDING_TYPE:
            raise ChamferFixturePlanConsolidationReceiptValidationError("unknown_finding_type")
        if f.get("finding_status") not in ALLOWED_FINDING_STATUS:
            raise ChamferFixturePlanConsolidationReceiptValidationError("unknown_finding_status")
        if f.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise ChamferFixturePlanConsolidationReceiptValidationError("unknown_implementation_status")

    if packet["readiness_constraints"] != default_readiness_constraints():
        raise ChamferFixturePlanConsolidationReceiptValidationError("invalid_readiness_constraints")
    if packet["fixture_constraints"] != default_fixture_constraints():
        raise ChamferFixturePlanConsolidationReceiptValidationError("invalid_fixture_constraints")
    if packet["output_contract"] != default_output_contract():
        raise ChamferFixturePlanConsolidationReceiptValidationError("invalid_output_contract")
    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferFixturePlanConsolidationReceiptValidationError(f"authority_lock_must_be_false:{flag}")
    _assert_safe(packet["provenance"])


def compute_chamfer_fixture_plan_consolidation_receipt_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_fixture_plan_consolidation_receipt(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_fixture_plan_consolidation_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    surfaces = sorted(payload.get("consolidated_surfaces", default_consolidated_surfaces()), key=lambda x: x["surface_id"])
    for surface in surfaces:
        surface["source_refs"] = sorted(surface.get("source_refs", []))
    findings = sorted(payload.get("consolidation_findings", default_consolidation_findings()), key=lambda x: x["finding_id"])
    for finding in findings:
        finding["evidence_refs"] = sorted(finding.get("evidence_refs", []))

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "operator_id": OPERATOR_ID,
        "source_valid_fixture_plan_refs": sorted(payload.get("source_valid_fixture_plan_refs", [])),
        "source_invalid_fixture_plan_refs": sorted(payload.get("source_invalid_fixture_plan_refs", [])),
        "source_not_computable_fixture_plan_refs": sorted(payload.get("source_not_computable_fixture_plan_refs", [])),
        "source_schema_plan_refs": sorted(payload.get("source_schema_plan_refs", [])),
        "source_baseline_implementation_plan_refs": sorted(payload.get("source_baseline_implementation_plan_refs", [])),
        "consolidated_surfaces": surfaces,
        "consolidation_findings": findings,
        "readiness_constraints": payload.get("readiness_constraints", default_readiness_constraints()),
        "fixture_constraints": payload.get("fixture_constraints", default_fixture_constraints()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_fixture_plan_consolidation_receipt_hash(base)
    validate_chamfer_fixture_plan_consolidation_receipt(base)
    return _finalize(base)
