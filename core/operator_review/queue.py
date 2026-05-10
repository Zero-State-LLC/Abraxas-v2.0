from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import (
    AuthorityRef,
    OperatorDecisionPolicy,
    OperatorDecisionReceipt,
    OperatorReviewItem,
    OperatorReviewQueue,
    OperatorReviewSourceRef,
)

SCHEMA_VERSION = "OperatorReviewQueue.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _default_policy() -> OperatorDecisionPolicy:
    return OperatorDecisionPolicy(
        policy_id="operator-review-policy-v1",
        allow_autonomous_approval=False,
        allow_mutation=False,
        require_receipt_for_final_decision=True,
        routing_policy="NO_ROUTING_CHANGE",
    )


def canonical_operator_review_queue_json(queue: OperatorReviewQueue | Mapping[str, Any]) -> str:
    payload = asdict(queue) if isinstance(queue, OperatorReviewQueue) else dict(queue)
    payload.pop("queue_hash", None)
    return _canonical_json(payload)


def operator_review_queue_hash(queue: OperatorReviewQueue | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_operator_review_queue_json(queue))


def operator_decision_receipt_hash(receipt: OperatorDecisionReceipt | Mapping[str, Any]) -> str:
    payload = asdict(receipt) if isinstance(receipt, OperatorDecisionReceipt) else dict(receipt)
    payload.pop("receipt_hash", None)
    return _sha256_text(_canonical_json(payload))


def build_operator_decision_receipt(receipt_id: str, decision_status: str, operator_id_policy: str, decision_reason: str, decision_scope: str) -> OperatorDecisionReceipt:
    draft = OperatorDecisionReceipt(receipt_id, decision_status, operator_id_policy, decision_reason, decision_scope, False, "PENDING")
    return replace(draft, receipt_hash=operator_decision_receipt_hash(draft))


def build_operator_review_item(item_id: str, source_ref: OperatorReviewSourceRef, review_type: str, priority: str, summary: str, recommended_action: str, decision_status: str = "PENDING", decision_receipt: OperatorDecisionReceipt | None = None) -> OperatorReviewItem:
    return OperatorReviewItem(item_id, source_ref, review_type, priority, summary, recommended_action, False, decision_status, decision_receipt)


def build_operator_review_queue(queue_id: str, items: tuple[OperatorReviewItem, ...], queue_status: str, created_by_lane: str, authority_ref: AuthorityRef | None, decision_policy: OperatorDecisionPolicy | None = None) -> OperatorReviewQueue:
    draft = OperatorReviewQueue(SCHEMA_VERSION, queue_id, items, queue_status, decision_policy or _default_policy(), created_by_lane, authority_ref, False, "PENDING")
    return replace(draft, queue_hash=operator_review_queue_hash(draft))


def write_operator_review_queue_contract_audit(base_dir: Path | str = ".") -> str:
    item = build_operator_review_item(
        item_id="item-1",
        source_ref=OperatorReviewSourceRef("SOURCE_RELIABILITY_ADVISORY", "advisory:1", "hash:1"),
        review_type="RELIABILITY_REVIEW",
        priority="HIGH",
        summary="Reliability posture requires operator review.",
        recommended_action="Hold for operator decision.",
    )
    queue = build_operator_review_queue(
        queue_id="operator-review-queue-v1",
        items=(item,),
        queue_status="READY_FOR_REVIEW",
        created_by_lane="FORECAST",
        authority_ref=None,
    )
    from .validator import validate_operator_review_queue

    report = validate_operator_review_queue(queue)
    payload = {
        "status": report.status,
        "queue_hash": queue.queue_hash,
        "receipt_hash": report.receipt_hash,
        "findings": [asdict(f) for f in report.findings],
        "schema_version": queue.schema_version,
    }
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/operator_review_queue_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
