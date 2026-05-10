import hashlib
import json
from dataclasses import asdict, replace

from core.promotion import *


def _proposal(status="READY_FOR_REVIEW", lane="FORECAST", receipt_ref="receipt://operator/review/1"):
    return build_promotion_proposal(
        proposal_id="proposal-1",
        proposal_type="PROMOTION",
        scope=PromotionProposalScope("SUBSYSTEM", "forecast-runtime"),
        evidence_refs=(PromotionEvidenceRef("SOURCE_RELIABILITY_ADVISORY", "a1", "h1", "reliability trend"),),
        change_set=PromotionChangeSet("cs1", "canary-only proposal", ("runtime/forecast",), "PROPOSAL_ONLY", "operator-reviewed canary", False),
        canary_policy=PromotionCanaryPolicy("cp1", True, "subsystem:forecast", "stable error", "spike in error", False),
        rollback_plan=PromotionRollbackPlan("rb1", True, "restore baseline", ("runtime/forecast",), False),
        review_requirement=PromotionReviewRequirement(True, "PROMOTION_PROPOSAL_REVIEW", True, receipt_ref),
        proposal_status=status,
        created_by_lane=lane,
        authority_ref=None,
    )


def test_deterministic_ready_for_review_passes():
    p1 = _proposal()
    p2 = _proposal()
    assert p1.proposal_hash == p2.proposal_hash
    assert validate_promotion_proposal(p1).status == "PASS"


def test_ready_for_review_without_evidence_blocked_or_not_computable():
    p = _proposal()
    p_bad = replace(p, evidence_refs=tuple())
    assert validate_promotion_proposal(p_bad).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_flag_constraints_blocked_or_not_computable():
    p = _proposal()
    assert validate_promotion_proposal(replace(p, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_promotion_proposal(replace(p, execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_promotion_proposal(replace(p, change_set=replace(p.change_set, applies_automatically=True))).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_promotion_proposal(replace(p, canary_policy=replace(p.canary_policy, auto_promote=True))).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_promotion_proposal(replace(p, rollback_plan=replace(p.rollback_plan, auto_rollback=True))).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_approved_for_canary_requires_receipt_ref_and_execution_stays_false():
    p = _proposal(status="APPROVED_FOR_CANARY", lane="OPERATOR", receipt_ref="")
    assert validate_promotion_proposal(p).status in {"BLOCKED", "NOT_COMPUTABLE"}
    p2 = _proposal(status="APPROVED_FOR_CANARY", lane="OPERATOR")
    assert not p2.execution_allowed


def test_mutation_like_requires_rollback_available():
    p = _proposal()
    p_bad = replace(p, rollback_plan=replace(p.rollback_plan, rollback_available=False))
    assert validate_promotion_proposal(p_bad).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_lane_constraints():
    sh = _proposal(status="READY_FOR_REVIEW", lane="SHADOW")
    assert validate_promotion_proposal(sh).status in {"BLOCKED", "NOT_COMPUTABLE"}
    fc = _proposal(status="APPROVED_FOR_CANARY", lane="FORECAST")
    assert validate_promotion_proposal(fc).status in {"BLOCKED", "NOT_COMPUTABLE"}
    proj = replace(_proposal(), created_by_lane="PROJECTION", authority_ref=AuthorityRef("MANUAL_RECEIPT", "id", "label"))
    assert validate_promotion_proposal(proj).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_hash_and_canonical_stability():
    p = _proposal()
    alt = dict(asdict(p)); alt["proposal_hash"] = "other"
    assert promotion_proposal_hash(p) == promotion_proposal_hash(alt)
    assert canonical_promotion_proposal_json(p) == canonical_promotion_proposal_json(p)


def test_schema_required_and_audit_artifact_hash(tmp_path):
    schema = json.loads(open("contracts/promotion/promotion_proposal.v1.schema.json", encoding="utf-8").read())
    obj = asdict(_proposal())
    req = set(schema["required"])
    assert req.issubset(set(obj.keys()))
    bad = dict(obj); bad.pop("proposal_id")
    assert not req.issubset(set(bad.keys()))

    h = write_promotion_proposal_contract_audit(tmp_path)
    p = tmp_path / "out/audit/promotion_proposal_contract.latest.json"
    text = p.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert h == hashlib.sha256(text.encode("utf-8")).hexdigest()
