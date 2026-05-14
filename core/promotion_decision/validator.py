from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import PromotionDecisionInputRef, PromotionDecisionEvidenceLineage, PromotionDecisionPosture, PromotionDecisionOperatorRequirement, PromotionDecisionRiskSummary, AuthorityRef, PromotionDecisionPacket, PromotionDecisionValidationFinding, PromotionDecisionValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_packet(x: PromotionDecisionPacket | Mapping[str, Any]) -> PromotionDecisionPacket:
    if isinstance(x, PromotionDecisionPacket):
        return x
    d = dict(x)
    return PromotionDecisionPacket(
        d["schema_version"], d["decision_packet_id"], d["proposal_id"], d["proposal_hash"], d["evaluation_id"], d["evaluation_hash"], tuple(PromotionDecisionInputRef(**r) for r in d["input_refs"]), PromotionDecisionEvidenceLineage(**d["evidence_lineage"]), PromotionDecisionPosture(**d["decision_posture"]), PromotionDecisionOperatorRequirement(**d["operator_requirement"]), PromotionDecisionRiskSummary(**d["risk_summary"]), d["packet_status"], d["created_by_lane"], AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None, d["promotion_execution_allowed"], d["rollback_execution_allowed"], d["mutation_allowed"], d["packet_hash"]
    )


def validate_promotion_decision_packet(packet: PromotionDecisionPacket | Mapping[str, Any]) -> PromotionDecisionValidationReport:
    p = _to_packet(packet)
    findings=[]
    status="PASS"
    if p.schema_version != "PromotionDecisionPacket.v1":
        findings.append(PromotionDecisionValidationFinding("SCHEMA_VERSION_INVALID","not_computable","schema_version must be PromotionDecisionPacket.v1."))
        status="NOT_COMPUTABLE"
    if not p.proposal_id or not p.proposal_hash or not p.evaluation_id or not p.evaluation_hash:
        findings.append(PromotionDecisionValidationFinding("REFS_REQUIRED","not_computable","Missing proposal/evaluation refs."))
        status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if p.promotion_execution_allowed:
        findings.append(PromotionDecisionValidationFinding("PROMOTION_EXEC_FORBIDDEN","error","promotion_execution_allowed must be false."))
        status="BLOCKED"
    if p.rollback_execution_allowed:
        findings.append(PromotionDecisionValidationFinding("ROLLBACK_EXEC_FORBIDDEN","error","rollback_execution_allowed must be false."))
        status="BLOCKED"
    if p.mutation_allowed:
        findings.append(PromotionDecisionValidationFinding("MUTATION_FORBIDDEN","error","mutation_allowed must be false."))
        status="BLOCKED"
    op = p.operator_requirement
    if not op.operator_review_required:
        findings.append(PromotionDecisionValidationFinding("OP_REVIEW_REQUIRED","error","operator_review_required must be true."))
        status="BLOCKED"
    if not op.operator_receipt_required:
        findings.append(PromotionDecisionValidationFinding("OP_RECEIPT_REQUIRED","error","operator_receipt_required must be true."))
        status="BLOCKED"
    if not op.execution_requires_separate_packet:
        findings.append(PromotionDecisionValidationFinding("SEPARATE_EXEC_PACKET_REQUIRED","error","execution_requires_separate_packet must be true."))
        status="BLOCKED"
    if p.packet_status == "READY_FOR_OPERATOR_DECISION" and (not p.input_refs or not p.evidence_lineage.lineage_id):
        findings.append(PromotionDecisionValidationFinding("READY_CONTENT_REQUIRED","not_computable","READY_FOR_OPERATOR_DECISION requires refs and evidence lineage."))
        status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if p.decision_posture.posture == "PROMOTION_RECOMMENDED" and not p.risk_summary.rollback_available:
        findings.append(PromotionDecisionValidationFinding("PROMOTION_REQUIRES_ROLLBACK_AVAILABLE","error","PROMOTION_RECOMMENDED requires rollback_available=true."))
        status="BLOCKED"
    if p.decision_posture.posture == "ROLLBACK_RECOMMENDED" and not (p.risk_summary.guardrail_breach_present or p.evidence_lineage.operator_receipt_ref_ids):
        findings.append(PromotionDecisionValidationFinding("ROLLBACK_REQUIRES_BREACH_OR_EVIDENCE","error","ROLLBACK_RECOMMENDED requires guardrail breach or rollback evidence ref."))
        status="BLOCKED"
    if p.created_by_lane=="SHADOW" and p.packet_status in {"READY_FOR_OPERATOR_DECISION","OPERATOR_APPROVED_FOR_FUTURE_EXECUTION"}:
        findings.append(PromotionDecisionValidationFinding("SHADOW_FINALIZE_BLOCKED","error","SHADOW may draft but cannot mark ready/approved."))
        status="BLOCKED"
    if p.created_by_lane=="FORECAST" and p.packet_status=="OPERATOR_APPROVED_FOR_FUTURE_EXECUTION":
        findings.append(PromotionDecisionValidationFinding("FORECAST_APPROVAL_BLOCKED","error","FORECAST may submit ready packets but cannot approve."))
        status="BLOCKED"
    if p.created_by_lane=="PROJECTION" and p.authority_ref is not None:
        findings.append(PromotionDecisionValidationFinding("PROJECTION_AUTHORITY_BLOCKED","error","PROJECTION cannot create decision authority."))
        status="BLOCKED"
    if p.created_by_lane=="CANON" and p.packet_status in {"READY_FOR_OPERATOR_DECISION","OPERATOR_APPROVED_FOR_FUTURE_EXECUTION","OPERATOR_DENIED","HELD"}:
        findings.append(PromotionDecisionValidationFinding("CANON_FINALIZE_BLOCKED","error","CANON may define schema/contracts only."))
        status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"decision_packet_id":p.decision_packet_id}))
    return PromotionDecisionValidationReport(status, tuple(findings), receipt_hash)
