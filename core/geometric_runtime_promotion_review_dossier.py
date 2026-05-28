from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeometricRuntimePromotionReviewDossier.v1"
DOSSIER_TYPE = "GEOMETRIC_RUNTIME_PROMOTION_REVIEW_DOSSIER"

ALLOWED_REVIEWED_RUNTIMES = ("GEOMETRIC_INTELLIGENCE_RUNTIME_v0_1",)
ALLOWED_REVIEW_STAGES = (
    "PROMOTION_REVIEW_ONLY",
    "READINESS_ASSESSMENT_ONLY",
    "BLOCKER_ASSESSMENT_ONLY",
    "HELD_FOR_OPERATOR_REVIEW",
)
ALLOWED_INTENDED_LANES = ("SHADOW", "REVIEW", "OBSERVATION_ONLY")
ALLOWED_FINDING_TYPES = (
    "SCAFFOLD_COMPLETION_FINDING",
    "TEST_VECTOR_FINDING",
    "REPLAY_RECEIPT_FINDING",
    "STABILIZATION_WINDOW_FINDING",
    "RENDERER_PLANNING_FINDING",
    "METRIC_SELECTION_FINDING",
    "GOVERNANCE_LOCK_FINDING",
    "NOT_COMPUTABLE_FINDING",
)
ALLOWED_READINESS_STATUS = (
    "READY_FOR_REVIEW",
    "NEEDS_STABILIZATION_EVIDENCE",
    "NEEDS_IMPLEMENTATION_PLAN",
    "NEEDS_OPERATOR_REVIEW",
    "BLOCKED_BY_GOVERNANCE",
    "NOT_COMPUTABLE",
)
ALLOWED_IMPLEMENTATION_STATUS = (
    "REVIEWED_METADATA_ONLY",
    "NOT_IMPLEMENTED",
    "BLOCKED_PENDING_REVIEW",
    "HELD_FOR_OPERATOR",
)
ALLOWED_BLOCKER_TYPES = (
    "NO_RUNTIME_AUTHORITY",
    "NO_CANON_PROMOTION_AUTHORITY",
    "NO_FORECAST_AUTHORITY",
    "NO_METRIC_IMPLEMENTATION",
    "NO_RENDERER_IMPLEMENTATION",
    "STABILIZATION_NOT_EXECUTED",
    "OPERATOR_REVIEW_REQUIRED",
    "NOT_COMPUTABLE_BLOCKER",
)
ALLOWED_BLOCKER_STATUS = ("ACTIVE", "HELD", "NOT_COMPUTABLE")
LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
    "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
)
FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast", "scoring", "promotion", "activation", "authorization", "canon-mutation",
)


class GeometricRuntimePromotionReviewDossierValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_readiness_findings() -> list[dict[str, Any]]:
    return [
        {
            "finding_id": "finding-001-governance-lock",
            "finding_type": "GOVERNANCE_LOCK_FINDING",
            "description": "All reviewed planning and stabilization surfaces remain advisory-only and non-authoritative.",
            "evidence_refs": ["REPO_FINAL_ARCHIVE_RECEIPT_GEOMETRIC_INTELLIGENCE_RUNTIME_v0_1"],
            "readiness_status": "NEEDS_OPERATOR_REVIEW",
            "implementation_status": "REVIEWED_METADATA_ONLY",
        }
    ]


def default_blocker_findings() -> list[dict[str, Any]]:
    return [
        {
            "blocker_id": "blocker-001-no-promotion-authority",
            "blocker_type": "NO_CANON_PROMOTION_AUTHORITY",
            "description": "Promotion remains blocked in this dossier lane.",
            "required_resolution": "operator_selected_new_planning_boundary_required",
            "evidence_refs": ["P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HOLD"],
            "blocker_status": "ACTIVE",
        }
    ]


def default_promotion_constraints() -> dict[str, bool]:
    return {
        "promotion_granted": False,
        "canon_promotion": False,
        "runtime_authority_granted": False,
        "execution_authority_granted": False,
        "activation_authorized": False,
        "forecast_influence_allowed": False,
        "scheduler_mutation_allowed": False,
        "oracle_mutation_allowed": False,
        "yggdrasil_route_mutation_allowed": False,
        "aal_viz_runtime_mutation_allowed": False,
        "p131_created": False,
    }


def default_review_decision() -> dict[str, Any]:
    return {
        "decision_status": "REVIEW_HELD",
        "promotion_allowed": False,
        "requires_new_planning_boundary": True,
        "requires_operator_review": True,
        "requires_stabilization_evidence": True,
        "requires_no_authority_scan": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_promotion": False,
        "emits_activation": False,
        "emits_runtime_controls": False,
        "emits_forecast_inputs": False,
        "emits_authority_tokens": False,
        "emits_review_metadata": True,
        "emits_blocker_summary": True,
        "emits_next_boundary_options": True,
    }


def _assert_provenance_safe(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            _assert_provenance_safe(nested, (*path, str(key)))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_provenance_safe(nested, (*path, str(index)))
    elif isinstance(value, str):
        path_keys = set(path)
        # Allow identifier references to contain domain nouns such as
        # "runtime", "promotion", "activation", and "authorization".
        # These values are IDs, not executable authority instructions.
        if "evidence_refs" in path_keys or "upstream_schema_refs" in path_keys:
            return
        lowered = value.lower()
        if any(token in lowered for token in FORBIDDEN_PROVENANCE_TOKENS):
            raise GeometricRuntimePromotionReviewDossierValidationError("forbidden_provenance_reference_detected")


def validate_geometric_runtime_promotion_review_dossier(packet: dict[str, Any]) -> None:
    required = {
        "schema_version", "dossier_id", "dossier_type", "source_archive_receipt_refs", "source_renderer_plan_refs",
        "source_metric_selection_plan_refs", "source_oracle_stabilization_window_refs", "source_yggdrasil_stabilization_window_refs",
        "review_scope", "readiness_findings", "blocker_findings", "promotion_constraints", "review_decision", "output_contract",
        "governance_flags", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise GeometricRuntimePromotionReviewDossierValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise GeometricRuntimePromotionReviewDossierValidationError("invalid_schema_version")
    if packet["dossier_type"] != DOSSIER_TYPE:
        raise GeometricRuntimePromotionReviewDossierValidationError("invalid_dossier_type")

    scope = packet["review_scope"]
    if scope.get("reviewed_runtime") not in ALLOWED_REVIEWED_RUNTIMES:
        raise GeometricRuntimePromotionReviewDossierValidationError("unknown_reviewed_runtime")
    if scope.get("review_stage") not in ALLOWED_REVIEW_STAGES:
        raise GeometricRuntimePromotionReviewDossierValidationError("unknown_review_stage")
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANES:
        raise GeometricRuntimePromotionReviewDossierValidationError("unknown_intended_lane")

    findings = packet["readiness_findings"]
    if not findings:
        raise GeometricRuntimePromotionReviewDossierValidationError("readiness_findings_must_be_non_empty")
    seen_finding: set[str] = set()
    for finding in sorted(findings, key=lambda x: x["finding_id"]):
        fid = finding["finding_id"]
        if fid in seen_finding:
            raise GeometricRuntimePromotionReviewDossierValidationError("duplicate_finding_id")
        seen_finding.add(fid)
        if finding["finding_type"] not in ALLOWED_FINDING_TYPES:
            raise GeometricRuntimePromotionReviewDossierValidationError("unknown_finding_type")
        if finding["readiness_status"] not in ALLOWED_READINESS_STATUS:
            raise GeometricRuntimePromotionReviewDossierValidationError("unknown_readiness_status")
        if finding["implementation_status"] not in ALLOWED_IMPLEMENTATION_STATUS:
            raise GeometricRuntimePromotionReviewDossierValidationError("unknown_implementation_status")

    blockers = packet["blocker_findings"]
    if not blockers:
        raise GeometricRuntimePromotionReviewDossierValidationError("blocker_findings_must_be_non_empty")
    seen_blocker: set[str] = set()
    for blocker in sorted(blockers, key=lambda x: x["blocker_id"]):
        bid = blocker["blocker_id"]
        if bid in seen_blocker:
            raise GeometricRuntimePromotionReviewDossierValidationError("duplicate_blocker_id")
        seen_blocker.add(bid)
        if blocker["blocker_type"] not in ALLOWED_BLOCKER_TYPES:
            raise GeometricRuntimePromotionReviewDossierValidationError("unknown_blocker_type")
        if blocker["blocker_status"] not in ALLOWED_BLOCKER_STATUS:
            raise GeometricRuntimePromotionReviewDossierValidationError("unknown_blocker_status")

    if packet["promotion_constraints"] != default_promotion_constraints():
        raise GeometricRuntimePromotionReviewDossierValidationError("invalid_promotion_constraints")
    if packet["review_decision"] != default_review_decision():
        raise GeometricRuntimePromotionReviewDossierValidationError("invalid_review_decision")
    if packet["output_contract"] != default_output_contract():
        raise GeometricRuntimePromotionReviewDossierValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise GeometricRuntimePromotionReviewDossierValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(packet["provenance"])


def compute_geometric_runtime_promotion_review_dossier_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_geometric_runtime_promotion_review_dossier(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_geometric_runtime_promotion_review_dossier(payload: dict[str, Any]) -> dict[str, Any]:
    findings = sorted(payload.get("readiness_findings", default_readiness_findings()), key=lambda x: x["finding_id"])
    blockers = sorted(payload.get("blocker_findings", default_blocker_findings()), key=lambda x: x["blocker_id"])
    for finding in findings:
        finding["evidence_refs"] = sorted(finding.get("evidence_refs", []))
    for blocker in blockers:
        blocker["evidence_refs"] = sorted(blocker.get("evidence_refs", []))

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "dossier_type": DOSSIER_TYPE,
        "source_archive_receipt_refs": sorted(payload.get("source_archive_receipt_refs", [])),
        "source_renderer_plan_refs": sorted(payload.get("source_renderer_plan_refs", [])),
        "source_metric_selection_plan_refs": sorted(payload.get("source_metric_selection_plan_refs", [])),
        "source_oracle_stabilization_window_refs": sorted(payload.get("source_oracle_stabilization_window_refs", [])),
        "source_yggdrasil_stabilization_window_refs": sorted(payload.get("source_yggdrasil_stabilization_window_refs", [])),
        "readiness_findings": findings,
        "blocker_findings": blockers,
        "promotion_constraints": payload.get("promotion_constraints", default_promotion_constraints()),
        "review_decision": payload.get("review_decision", default_review_decision()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_geometric_runtime_promotion_review_dossier_hash(base)
    validate_geometric_runtime_promotion_review_dossier(base)
    return _finalize(base)
