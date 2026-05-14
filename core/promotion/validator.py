from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import PromotionProposalScope, PromotionEvidenceRef, PromotionChangeSet, PromotionCanaryPolicy, PromotionRollbackPlan, PromotionReviewRequirement, AuthorityRef, PromotionProposal, PromotionValidationFinding, PromotionValidationReport

MUTATION_LIKE_TYPES = {"PROMOTION", "ADAPTATION", "ROUTING_CHANGE", "SOURCE_WEIGHT_CHANGE", "CALIBRATION_POLICY_CHANGE"}


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_proposal(proposal: PromotionProposal | Mapping[str, Any]) -> PromotionProposal:
    if isinstance(proposal, PromotionProposal):
        return proposal
    d = dict(proposal)
    return PromotionProposal(
        d["schema_version"],
        d["proposal_id"],
        d["proposal_type"],
        PromotionProposalScope(**d["scope"]),
        tuple(PromotionEvidenceRef(**x) for x in d["evidence_refs"]),
        PromotionChangeSet(**d["change_set"]),
        PromotionCanaryPolicy(**d["canary_policy"]),
        PromotionRollbackPlan(**d["rollback_plan"]),
        PromotionReviewRequirement(**d["review_requirement"]),
        d["proposal_status"],
        d["created_by_lane"],
        AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None,
        d["mutation_allowed"],
        d["execution_allowed"],
        d["proposal_hash"],
    )


def validate_promotion_proposal(proposal: PromotionProposal | Mapping[str, Any]) -> PromotionValidationReport:
    p = _to_proposal(proposal)
    findings: list[PromotionValidationFinding] = []
    status = "PASS"
    if p.schema_version != "PromotionProposal.v1":
        findings.append(PromotionValidationFinding("SCHEMA_VERSION_INVALID", "not_computable", "schema_version must be PromotionProposal.v1."))
        status = "NOT_COMPUTABLE"
    if p.mutation_allowed:
        findings.append(PromotionValidationFinding("MUTATION_FORBIDDEN", "error", "mutation_allowed must be false."))
        status = "BLOCKED"
    if p.execution_allowed:
        findings.append(PromotionValidationFinding("EXECUTION_FORBIDDEN", "error", "execution_allowed must be false."))
        status = "BLOCKED"
    if p.change_set.applies_automatically:
        findings.append(PromotionValidationFinding("AUTOMATIC_APPLY_FORBIDDEN", "error", "change_set.applies_automatically must be false."))
        status = "BLOCKED"
    if p.canary_policy.auto_promote:
        findings.append(PromotionValidationFinding("AUTO_PROMOTE_FORBIDDEN", "error", "canary_policy.auto_promote must be false."))
        status = "BLOCKED"
    if p.rollback_plan.auto_rollback:
        findings.append(PromotionValidationFinding("AUTO_ROLLBACK_FORBIDDEN", "error", "rollback_plan.auto_rollback must be false."))
        status = "BLOCKED"
    if not p.review_requirement.review_required:
        findings.append(PromotionValidationFinding("REVIEW_REQUIRED", "error", "review_requirement.review_required must be true."))
        status = "BLOCKED"
    if not p.review_requirement.required_operator_receipt:
        findings.append(PromotionValidationFinding("OPERATOR_RECEIPT_REQUIRED", "error", "review_requirement.required_operator_receipt must be true."))
        status = "BLOCKED"
    if p.proposal_status == "READY_FOR_REVIEW" and len(p.evidence_refs) < 1:
        findings.append(PromotionValidationFinding("EVIDENCE_REQUIRED", "not_computable", "READY_FOR_REVIEW requires at least one evidence_ref."))
        status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if p.proposal_status == "APPROVED_FOR_CANARY" and not p.review_requirement.operator_receipt_ref:
        findings.append(PromotionValidationFinding("APPROVAL_RECEIPT_REF_REQUIRED", "not_computable", "APPROVED_FOR_CANARY requires operator_receipt_ref."))
        status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if p.proposal_type in MUTATION_LIKE_TYPES and not p.rollback_plan.rollback_available:
        findings.append(PromotionValidationFinding("ROLLBACK_REQUIRED", "error", "Mutation-like proposal types require rollback_available=true."))
        status = "BLOCKED"
    if p.created_by_lane == "SHADOW" and p.proposal_status in {"READY_FOR_REVIEW", "APPROVED_FOR_CANARY"}:
        findings.append(PromotionValidationFinding("SHADOW_FINALIZE_BLOCKED", "error", "SHADOW may draft but cannot mark READY_FOR_REVIEW or APPROVED_FOR_CANARY."))
        status = "BLOCKED"
    if p.created_by_lane == "FORECAST" and p.proposal_status == "APPROVED_FOR_CANARY":
        findings.append(PromotionValidationFinding("FORECAST_APPROVAL_BLOCKED", "error", "FORECAST may submit READY_FOR_REVIEW but cannot approve."))
        status = "BLOCKED"
    if p.created_by_lane == "PROJECTION" and p.authority_ref is not None:
        findings.append(PromotionValidationFinding("PROJECTION_AUTHORITY_BLOCKED", "error", "PROJECTION cannot create promotion authority."))
        status = "BLOCKED"
    if p.created_by_lane == "CANON" and p.proposal_status in {"READY_FOR_REVIEW", "APPROVED_FOR_CANARY"}:
        findings.append(PromotionValidationFinding("CANON_FINALIZE_BLOCKED", "error", "CANON may define schema/contracts only."))
        status = "BLOCKED"

    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "proposal_id": p.proposal_id}))
    return PromotionValidationReport(status, tuple(findings), receipt_hash)
