from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import *

SCHEMA_VERSION = "PromotionProposal.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_promotion_proposal_json(proposal: PromotionProposal | Mapping[str, Any]) -> str:
    payload = asdict(proposal) if isinstance(proposal, PromotionProposal) else dict(proposal)
    payload.pop("proposal_hash", None)
    return _canonical_json(payload)


def promotion_proposal_hash(proposal: PromotionProposal | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_promotion_proposal_json(proposal))


def build_promotion_proposal(
    proposal_id: str,
    proposal_type: str,
    scope: PromotionProposalScope,
    evidence_refs: tuple[PromotionEvidenceRef, ...],
    change_set: PromotionChangeSet,
    canary_policy: PromotionCanaryPolicy,
    rollback_plan: PromotionRollbackPlan,
    review_requirement: PromotionReviewRequirement,
    proposal_status: str,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
) -> PromotionProposal:
    draft = PromotionProposal(
        SCHEMA_VERSION,
        proposal_id,
        proposal_type,
        scope,
        evidence_refs,
        change_set,
        canary_policy,
        rollback_plan,
        review_requirement,
        proposal_status,
        created_by_lane,
        authority_ref,
        False,
        False,
        "PENDING",
    )
    return replace(draft, proposal_hash=promotion_proposal_hash(draft))


def write_promotion_proposal_contract_audit(base_dir: Path | str = ".") -> str:
    proposal = build_promotion_proposal(
        proposal_id="promotion-proposal-v1",
        proposal_type="PROMOTION",
        scope=PromotionProposalScope("SUBSYSTEM", "forecast-runtime"),
        evidence_refs=(PromotionEvidenceRef("SOURCE_RELIABILITY_ADVISORY", "advisory:1", "hash:1", "Observed reliability trend."),),
        change_set=PromotionChangeSet("changeset:1", "Proposal-only canary path.", ("runtime/forecast",), "PROPOSAL_ONLY", "Operator-reviewed canary staging only.", False),
        canary_policy=PromotionCanaryPolicy("canary:1", True, "subsystem:forecast", "No elevated error during canary window.", "Error threshold exceeded.", False),
        rollback_plan=PromotionRollbackPlan("rollback:1", True, "Revert to pre-proposal manifest.", ("runtime/forecast",), False),
        review_requirement=PromotionReviewRequirement(True, "PROMOTION_PROPOSAL_REVIEW", True, "receipt://operator/review/1"),
        proposal_status="READY_FOR_REVIEW",
        created_by_lane="FORECAST",
        authority_ref=None,
    )
    from .validator import validate_promotion_proposal

    report = validate_promotion_proposal(proposal)
    payload = {
        "status": report.status,
        "proposal_hash": proposal.proposal_hash,
        "receipt_hash": report.receipt_hash,
        "findings": [asdict(f) for f in report.findings],
        "schema_version": proposal.schema_version,
    }
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/promotion_proposal_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
