from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import *

SCHEMA_VERSION = "PromotionDecisionPacket.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_promotion_decision_packet_json(packet: PromotionDecisionPacket | Mapping[str, Any]) -> str:
    payload = asdict(packet) if isinstance(packet, PromotionDecisionPacket) else dict(packet)
    payload.pop("packet_hash", None)
    return _canonical_json(payload)


def promotion_decision_packet_hash(packet: PromotionDecisionPacket | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_promotion_decision_packet_json(packet))


def build_promotion_decision_packet(
    decision_packet_id: str,
    proposal_id: str,
    proposal_hash: str,
    evaluation_id: str,
    evaluation_hash: str,
    input_refs: tuple[PromotionDecisionInputRef, ...],
    evidence_lineage: PromotionDecisionEvidenceLineage,
    decision_posture: PromotionDecisionPosture,
    operator_requirement: PromotionDecisionOperatorRequirement,
    risk_summary: PromotionDecisionRiskSummary,
    packet_status: str,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
) -> PromotionDecisionPacket:
    draft = PromotionDecisionPacket(
        SCHEMA_VERSION,
        decision_packet_id,
        proposal_id,
        proposal_hash,
        evaluation_id,
        evaluation_hash,
        input_refs,
        evidence_lineage,
        decision_posture,
        operator_requirement,
        risk_summary,
        packet_status,
        created_by_lane,
        authority_ref,
        False,
        False,
        False,
        "PENDING",
    )
    return replace(draft, packet_hash=promotion_decision_packet_hash(draft))


def derive_promotion_decision_packet_from_evaluation(evaluation: Mapping[str, Any], proposal: Mapping[str, Any] | None = None) -> PromotionDecisionPacket:
    e = dict(evaluation)
    p = dict(proposal or {})
    eval_decision = str(e.get("decision", {}).get("decision", "NOT_COMPUTABLE"))
    rec_types = {x.get("recommendation_type") for x in e.get("recommendations", [])}

    posture, packet_status, risk_posture, breach = "NOT_COMPUTABLE", "NOT_COMPUTABLE", "NOT_COMPUTABLE", False
    if e.get("evaluation_hash") and (p.get("proposal_hash") or e.get("proposal_hash")):
        if eval_decision == "PASS" and "RECOMMEND_PROMOTION_PROPOSAL" in rec_types:
            posture, packet_status, risk_posture = "PROMOTION_RECOMMENDED", "READY_FOR_OPERATOR_DECISION", "LOW"
        elif eval_decision == "GUARDRAIL_BREACH" or "RECOMMEND_ROLLBACK_PROPOSAL" in rec_types:
            posture, packet_status, risk_posture, breach = "ROLLBACK_RECOMMENDED", "READY_FOR_OPERATOR_DECISION", "HIGH", True
        elif eval_decision in {"INSUFFICIENT_EVIDENCE", "REVIEW_REQUIRED"}:
            posture, packet_status, risk_posture = "HOLD_RECOMMENDED", "READY_FOR_OPERATOR_DECISION", "MEDIUM"

    operator_req = PromotionDecisionOperatorRequirement(True, True, ("APPROVED", "DENIED", "HELD"), True)
    return build_promotion_decision_packet(
        decision_packet_id=f"promotion-decision:{e.get('evaluation_id', 'unknown')}",
        proposal_id=str(p.get("proposal_id", e.get("proposal_id", ""))),
        proposal_hash=str(p.get("proposal_hash", e.get("proposal_hash", ""))),
        evaluation_id=str(e.get("evaluation_id", "")),
        evaluation_hash=str(e.get("evaluation_hash", "")),
        input_refs=(PromotionDecisionInputRef("CANARY_EVALUATION", str(e.get("evaluation_id", "")), str(e.get("evaluation_hash", ""))),),
        evidence_lineage=PromotionDecisionEvidenceLineage("lineage-1", ("forecast:1",), ("brier:1",), ("cal:1",), ("rel:1",), ("canary:1",), tuple(), True),
        decision_posture=PromotionDecisionPosture(posture, f"Derived from evaluation decision={eval_decision}."),
        operator_requirement=operator_req,
        risk_summary=PromotionDecisionRiskSummary("risk-1", risk_posture, True, breach, "UNCERTAINTY_POLICY_V1"),
        packet_status=packet_status,
        created_by_lane="FORECAST",
        authority_ref=None,
    )


def write_promotion_decision_packet_contract_audit(base_dir: Path | str = ".") -> str:
    evaluation = {
        "evaluation_id": "eval-1",
        "evaluation_hash": "eval-h1",
        "proposal_id": "proposal-1",
        "proposal_hash": "proposal-h1",
        "decision": {"decision": "PASS"},
        "recommendations": [{"recommendation_type": "RECOMMEND_PROMOTION_PROPOSAL"}],
    }
    packet = derive_promotion_decision_packet_from_evaluation(evaluation)
    from .validator import validate_promotion_decision_packet

    report = validate_promotion_decision_packet(packet)
    payload = {"status": report.status, "packet_hash": packet.packet_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": packet.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/promotion_decision_packet_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
