import hashlib
import json
from dataclasses import asdict, replace

from core.operator_review.models import AuthorityRef, OperatorReviewSourceRef
from core.operator_review.queue import build_operator_decision_receipt, build_operator_review_item, build_operator_review_queue, canonical_operator_review_queue_json, operator_decision_receipt_hash, operator_review_queue_hash, write_operator_review_queue_contract_audit
from core.operator_review.validator import validate_operator_review_queue


def _sample_item(status="PENDING", receipt=None):
    return build_operator_review_item(
        item_id="item-1",
        source_ref=OperatorReviewSourceRef("SOURCE_RELIABILITY_ADVISORY", "advisory:1", "hash:1"),
        review_type="RELIABILITY_REVIEW",
        priority="HIGH",
        summary="Review reliability advisory.",
        recommended_action="Hold for operator.",
        decision_status=status,
        decision_receipt=receipt,
    )


def _queue(items, lane="FORECAST"):
    return build_operator_review_queue("q-1", tuple(items), "READY_FOR_REVIEW", lane, None)


def test_deterministic_queue_hash_stable():
    q1 = _queue([_sample_item()])
    q2 = _queue([_sample_item()])
    assert q1.queue_hash == q2.queue_hash


def test_ready_for_review_requires_items():
    q = build_operator_review_queue("q-empty", tuple(), "READY_FOR_REVIEW", "FORECAST", None)
    assert validate_operator_review_queue(q).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_mutation_flags_blocked():
    q = _queue([_sample_item()])
    assert validate_operator_review_queue(replace(q, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    item = replace(q.items[0], mutation_allowed=True)
    assert validate_operator_review_queue(replace(q, items=(item,))).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_policy_and_receipt_mutation_blocked():
    q = _queue([_sample_item()])
    r = build_operator_decision_receipt("r1", "PENDING", "OPERATOR_HANDLE", "waiting", "ITEM")
    bad_item = replace(q.items[0], decision_receipt=replace(r, mutation_authorized=True))
    assert validate_operator_review_queue(replace(q, items=(bad_item,))).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_operator_review_queue(replace(q, decision_policy=replace(q.decision_policy, allow_autonomous_approval=True))).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_operator_review_queue(replace(q, decision_policy=replace(q.decision_policy, routing_policy="DYNAMIC"))).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_final_decisions_require_receipt_and_no_mutation_auth():
    q = _queue([_sample_item(status="APPROVED")], lane="OPERATOR")
    assert validate_operator_review_queue(q).status in {"BLOCKED", "NOT_COMPUTABLE"}
    r = build_operator_decision_receipt("r2", "APPROVED", "OPERATOR_HANDLE", "approved", "ITEM")
    q2 = _queue([_sample_item(status="APPROVED", receipt=r)], lane="OPERATOR")
    assert q2.items[0].decision_receipt and (not q2.items[0].decision_receipt.mutation_authorized)


def test_lane_constraints():
    r = build_operator_decision_receipt("r3", "APPROVED", "OPERATOR_HANDLE", "approved", "ITEM")
    sh = _queue([_sample_item(status="APPROVED", receipt=r)], lane="SHADOW")
    assert validate_operator_review_queue(sh).status in {"BLOCKED", "NOT_COMPUTABLE"}
    fc = _queue([_sample_item(status="APPROVED", receipt=r)], lane="FORECAST")
    assert validate_operator_review_queue(fc).status in {"BLOCKED", "NOT_COMPUTABLE"}
    proj = build_operator_review_queue("q-proj", (_sample_item(),), "READY_FOR_REVIEW", "PROJECTION", AuthorityRef("MANUAL_RECEIPT", "a", "b"))
    assert validate_operator_review_queue(proj).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_hash_and_canonical_stability():
    q = _queue([_sample_item()])
    alt = dict(asdict(q))
    alt["queue_hash"] = "other"
    assert operator_review_queue_hash(q) == operator_review_queue_hash(alt)
    rec = build_operator_decision_receipt("r4", "PENDING", "OPERATOR_HANDLE", "pending", "ITEM")
    alt_r = dict(asdict(rec))
    alt_r["receipt_hash"] = "other"
    assert operator_decision_receipt_hash(rec) == operator_decision_receipt_hash(alt_r)
    assert canonical_operator_review_queue_json(q) == canonical_operator_review_queue_json(q)


def test_schema_required_and_audit_hash_newline(tmp_path):
    schema = json.loads(open("contracts/operator_review/operator_review_queue.v1.schema.json", encoding="utf-8").read())
    obj = asdict(_queue([_sample_item()]))
    req = set(schema["required"])
    assert req.issubset(set(obj.keys()))
    bad = dict(obj)
    bad.pop("queue_id")
    assert not req.issubset(set(bad.keys()))

    h = write_operator_review_queue_contract_audit(tmp_path)
    p = tmp_path / "out/audit/operator_review_queue_contract.latest.json"
    text = p.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert h == hashlib.sha256(text.encode("utf-8")).hexdigest()
