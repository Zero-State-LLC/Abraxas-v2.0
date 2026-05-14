import hashlib
import json
from dataclasses import asdict, replace

from core.promotion_decision.models import AuthorityRef
from core.promotion_decision.packet import canonical_promotion_decision_packet_json, derive_promotion_decision_packet_from_evaluation, promotion_decision_packet_hash, write_promotion_decision_packet_contract_audit
from core.promotion_decision.validator import validate_promotion_decision_packet


def _eval(decision="PASS", rec="RECOMMEND_PROMOTION_PROPOSAL"):
    return {"evaluation_id": "eval-1", "evaluation_hash": "eval-h1", "proposal_id": "proposal-1", "proposal_hash": "proposal-h1", "decision": {"decision": decision}, "recommendations": [{"recommendation_type": rec}]}


def test_derivation_paths_and_execution_flags():
    p = derive_promotion_decision_packet_from_evaluation(_eval("PASS", "RECOMMEND_PROMOTION_PROPOSAL"))
    assert p.decision_posture.posture == "PROMOTION_RECOMMENDED" and p.packet_status == "READY_FOR_OPERATOR_DECISION" and (not p.promotion_execution_allowed)
    r = derive_promotion_decision_packet_from_evaluation(_eval("GUARDRAIL_BREACH", "RECOMMEND_ROLLBACK_PROPOSAL"))
    assert r.decision_posture.posture == "ROLLBACK_RECOMMENDED" and (not r.rollback_execution_allowed)
    h = derive_promotion_decision_packet_from_evaluation(_eval("INSUFFICIENT_EVIDENCE", "RECOMMEND_HOLD"))
    assert h.decision_posture.posture == "HOLD_RECOMMENDED"


def test_validation_flag_and_requirement_blocks():
    p = derive_promotion_decision_packet_from_evaluation(_eval())
    assert validate_promotion_decision_packet(replace(p, proposal_id="")).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_promotion_decision_packet(replace(p, promotion_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_promotion_decision_packet(replace(p, rollback_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_promotion_decision_packet(replace(p, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_promotion_decision_packet(replace(p, operator_requirement=replace(p.operator_requirement, operator_review_required=False))).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_promotion_decision_packet(replace(p, operator_requirement=replace(p.operator_requirement, execution_requires_separate_packet=False))).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_posture_and_lane_constraints():
    p = derive_promotion_decision_packet_from_evaluation(_eval())
    approved = replace(p, packet_status="OPERATOR_APPROVED_FOR_FUTURE_EXECUTION", created_by_lane="OPERATOR", authority_ref=AuthorityRef("MANUAL_RECEIPT", "id", "label"))
    assert (not approved.promotion_execution_allowed) and (not approved.rollback_execution_allowed)
    no_rb = replace(p, risk_summary=replace(p.risk_summary, rollback_available=False))
    assert validate_promotion_decision_packet(no_rb).status in {"BLOCKED", "NOT_COMPUTABLE"}
    sh = replace(p, created_by_lane="SHADOW")
    assert validate_promotion_decision_packet(sh).status in {"BLOCKED", "NOT_COMPUTABLE"}
    fc = replace(p, packet_status="OPERATOR_APPROVED_FOR_FUTURE_EXECUTION", created_by_lane="FORECAST")
    assert validate_promotion_decision_packet(fc).status in {"BLOCKED", "NOT_COMPUTABLE"}
    proj = replace(p, created_by_lane="PROJECTION", authority_ref=AuthorityRef("MANUAL_RECEIPT", "id", "label"))
    assert validate_promotion_decision_packet(proj).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_hash_schema_and_audit(tmp_path):
    p = derive_promotion_decision_packet_from_evaluation(_eval())
    alt = dict(asdict(p))
    alt["packet_hash"] = "other"
    assert promotion_decision_packet_hash(p) == promotion_decision_packet_hash(alt)
    assert canonical_promotion_decision_packet_json(p) == canonical_promotion_decision_packet_json(p)

    schema = json.loads(open("contracts/promotion_decision/promotion_decision_packet.v1.schema.json", encoding="utf-8").read())
    req = set(schema["required"])
    obj = asdict(p)
    assert req.issubset(set(obj.keys()))
    bad = dict(obj)
    bad.pop("decision_packet_id")
    assert not req.issubset(set(bad.keys()))

    h = write_promotion_decision_packet_contract_audit(tmp_path)
    fp = tmp_path / "out/audit/promotion_decision_packet_contract.latest.json"
    text = fp.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert h == hashlib.sha256(text.encode("utf-8")).hexdigest()
