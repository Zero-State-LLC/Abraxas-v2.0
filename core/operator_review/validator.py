from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import OperatorReviewSourceRef, OperatorDecisionReceipt, OperatorReviewItem, OperatorDecisionPolicy, AuthorityRef, OperatorReviewQueue, OperatorReviewValidationFinding, OperatorReviewValidationReport

FINAL_DECISIONS = {"APPROVED", "DENIED", "HELD", "VOID"}


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_queue(q: OperatorReviewQueue | Mapping[str, Any]) -> OperatorReviewQueue:
    if isinstance(q, OperatorReviewQueue):
        return q
    d = dict(q)
    items = []
    for item in d["items"]:
        receipt = OperatorDecisionReceipt(**item["decision_receipt"]) if item.get("decision_receipt") else None
        items.append(OperatorReviewItem(item["item_id"], OperatorReviewSourceRef(**item["source_ref"]), item["review_type"], item["priority"], item["summary"], item["recommended_action"], item["mutation_allowed"], item["decision_status"], receipt))
    return OperatorReviewQueue(d["schema_version"], d["queue_id"], tuple(items), d["queue_status"], OperatorDecisionPolicy(**d["decision_policy"]), d["created_by_lane"], AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None, d["mutation_allowed"], d["queue_hash"])


def validate_operator_review_queue(queue: OperatorReviewQueue | Mapping[str, Any]) -> OperatorReviewValidationReport:
    q = _to_queue(queue)
    findings: list[OperatorReviewValidationFinding] = []
    status = "PASS"
    if q.schema_version != "OperatorReviewQueue.v1":
        findings.append(OperatorReviewValidationFinding("SCHEMA_VERSION_INVALID", "not_computable", "schema_version must be OperatorReviewQueue.v1."))
        status = "NOT_COMPUTABLE"
    if q.mutation_allowed:
        findings.append(OperatorReviewValidationFinding("QUEUE_MUTATION_FORBIDDEN", "error", "queue mutation_allowed must be false."))
        status = "BLOCKED"
    if q.decision_policy.allow_autonomous_approval:
        findings.append(OperatorReviewValidationFinding("AUTONOMOUS_APPROVAL_FORBIDDEN", "error", "allow_autonomous_approval must be false."))
        status = "BLOCKED"
    if q.decision_policy.allow_mutation:
        findings.append(OperatorReviewValidationFinding("MUTATION_POLICY_FORBIDDEN", "error", "allow_mutation must be false."))
        status = "BLOCKED"
    if q.decision_policy.routing_policy != "NO_ROUTING_CHANGE":
        findings.append(OperatorReviewValidationFinding("ROUTING_POLICY_INVALID", "error", "routing_policy must be NO_ROUTING_CHANGE."))
        status = "BLOCKED"
    if q.queue_status == "READY_FOR_REVIEW" and not q.items:
        findings.append(OperatorReviewValidationFinding("QUEUE_ITEMS_REQUIRED", "not_computable", "READY_FOR_REVIEW requires at least one item."))
        status = "NOT_COMPUTABLE" if status != "BLOCKED" else status

    for item in q.items:
        if item.mutation_allowed:
            findings.append(OperatorReviewValidationFinding("ITEM_MUTATION_FORBIDDEN", "error", "item mutation_allowed must be false."))
            status = "BLOCKED"
        if item.decision_status in FINAL_DECISIONS and item.decision_receipt is None:
            findings.append(OperatorReviewValidationFinding("FINAL_DECISION_RECEIPT_REQUIRED", "error", "Final decision requires decision_receipt."))
            status = "BLOCKED"
        if item.decision_status == "PENDING" and item.decision_receipt and item.decision_receipt.decision_status in FINAL_DECISIONS:
            findings.append(OperatorReviewValidationFinding("PENDING_FINAL_RECEIPT_MISMATCH", "error", "PENDING item cannot include final receipt."))
            status = "BLOCKED"
        if item.decision_receipt:
            if item.decision_receipt.mutation_authorized:
                findings.append(OperatorReviewValidationFinding("RECEIPT_MUTATION_AUTH_FORBIDDEN", "error", "decision receipt mutation_authorized must be false."))
                status = "BLOCKED"
            if item.decision_status != item.decision_receipt.decision_status:
                findings.append(OperatorReviewValidationFinding("DECISION_STATUS_MISMATCH", "error", "item and receipt decision_status must match."))
                status = "BLOCKED"

    if q.created_by_lane == "SHADOW" and any(i.decision_status in FINAL_DECISIONS for i in q.items):
        findings.append(OperatorReviewValidationFinding("SHADOW_FINALIZE_BLOCKED", "error", "SHADOW may draft review items but cannot finalize decisions."))
        status = "BLOCKED"
    if q.created_by_lane == "FORECAST" and any(i.decision_status == "APPROVED" for i in q.items):
        findings.append(OperatorReviewValidationFinding("FORECAST_APPROVAL_BLOCKED", "error", "FORECAST may submit items but cannot approve decisions."))
        status = "BLOCKED"
    if q.created_by_lane == "PROJECTION" and q.authority_ref is not None:
        findings.append(OperatorReviewValidationFinding("PROJECTION_AUTHORITY_BLOCKED", "error", "PROJECTION may not create review authority."))
        status = "BLOCKED"
    if q.created_by_lane == "CANON" and q.queue_status in {"READY_FOR_REVIEW", "PARTIALLY_REVIEWED", "REVIEW_COMPLETE"}:
        findings.append(OperatorReviewValidationFinding("CANON_FINALIZE_BLOCKED", "error", "CANON may define schema/contracts only."))
        status = "BLOCKED"

    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "queue_id": q.queue_id}))
    return OperatorReviewValidationReport(status, tuple(findings), receipt_hash)
