import hashlib
import json
from dataclasses import asdict, replace

from core.canary_evaluation import *


def _acc(status="EVIDENCE_READY", guardrails_clear=True):
    return {
        "activation_id": "act-1", "activation_hash": "act-h1", "accumulation_id": "acc-1", "accumulation_hash": "acc-h1",
        "accumulation_status": status,
        "readiness_summary": {"minimum_evidence_count": 3, "observed_evidence_count": 3 if status=="EVIDENCE_READY" else 1, "guardrails_clear": guardrails_clear},
        "guardrail_observations": [{"breach_detected": True}] if status=="GUARDRAIL_BREACH" else []
    }


def test_derivation_paths_and_non_authorization():
    p = derive_canary_evaluation_from_accumulation(_acc("EVIDENCE_READY", True))
    assert p.evaluation_status == "PASSED" and p.decision.decision == "PASS" and (not p.promotion_allowed)
    b = derive_canary_evaluation_from_accumulation(_acc("GUARDRAIL_BREACH", False))
    assert b.evaluation_status in {"FAILED", "REVIEW_REQUIRED"} and (not b.rollback_allowed)
    i = derive_canary_evaluation_from_accumulation(_acc("INSUFFICIENT_EVIDENCE", False))
    assert i.evaluation_status == "REVIEW_REQUIRED"


def test_missing_refs_and_flags_blocked_or_not_computable():
    e = derive_canary_evaluation_from_accumulation(_acc())
    missing = replace(e, activation_id="")
    assert validate_canary_evaluation(missing).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_canary_evaluation(replace(e, promotion_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_canary_evaluation(replace(e, rollback_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_canary_evaluation(replace(e, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_canary_evaluation(replace(e, review_summary=replace(e.review_summary, execution_allowed=True))).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_recommendations_do_not_authorize_and_lane_constraints():
    e = derive_canary_evaluation_from_accumulation(_acc("EVIDENCE_READY", True))
    assert any(r.recommendation_type == "RECOMMEND_PROMOTION_PROPOSAL" for r in e.recommendations) and (not e.promotion_allowed)
    b = derive_canary_evaluation_from_accumulation(_acc("GUARDRAIL_BREACH", False))
    assert any(r.recommendation_type == "RECOMMEND_ROLLBACK_PROPOSAL" for r in b.recommendations) and (not b.rollback_allowed)
    assert validate_canary_evaluation(replace(e, created_by_lane="SHADOW")).status in {"BLOCKED", "NOT_COMPUTABLE"}
    proj = replace(e, created_by_lane="PROJECTION", authority_ref=AuthorityRef("MANUAL_RECEIPT", "id", "label"))
    assert validate_canary_evaluation(proj).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_hash_schema_and_audit(tmp_path):
    e = derive_canary_evaluation_from_accumulation(_acc("EVIDENCE_READY", True))
    alt = dict(asdict(e)); alt["evaluation_hash"] = "other"
    assert canary_evaluation_hash(e) == canary_evaluation_hash(alt)
    assert canonical_canary_evaluation_json(e) == canonical_canary_evaluation_json(e)

    schema = json.loads(open("contracts/canary_evaluation/canary_evaluation.v1.schema.json", encoding="utf-8").read())
    req = set(schema["required"])
    obj = asdict(e)
    assert req.issubset(set(obj.keys()))
    bad = dict(obj); bad.pop("evaluation_id")
    assert not req.issubset(set(bad.keys()))

    h = write_canary_evaluation_contract_audit(tmp_path)
    p = tmp_path / "out/audit/canary_evaluation_contract.latest.json"
    text = p.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert h == hashlib.sha256(text.encode("utf-8")).hexdigest()
