from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import TemporalClimateOperatorReviewProjectionQueue, TemporalOperatorReviewValidationFinding, TemporalOperatorReviewValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_temporal_operator_review_projection_queue(queue: TemporalClimateOperatorReviewProjectionQueue | Mapping[str, Any]) -> TemporalOperatorReviewValidationReport:
    q = queue if isinstance(queue, TemporalClimateOperatorReviewProjectionQueue) else TemporalClimateOperatorReviewProjectionQueue(**dict(queue))
    findings = []
    status = "PASS"
    if (not q.projection_only) or q.queue_authoritative or q.action_authorization_allowed or q.execution_allowed or q.mutation_allowed or q.rollback_allowed or q.promotion_allowed or q.timeline_collapse_allowed or q.canonical_selection_allowed or q.routing_change_allowed or q.auto_transition_allowed:
        findings.append(TemporalOperatorReviewValidationFinding("FLAGS_FORBIDDEN", "error", "queue must remain projection-only and zero-authority/action/execution/mutation/rollback/promotion/collapse/selection/routing/auto-transition."))
        status = "BLOCKED"
    if any((not i.projection_only) or i.action_authorization_allowed for i in q.queue_items):
        findings.append(TemporalOperatorReviewValidationFinding("ITEM_FLAGS_FORBIDDEN", "error", "queue_items must be projection_only with no action authorization."))
        status = "BLOCKED"
    if any((not s.projection_only) or s.action_authorization_allowed for s in q.risk_surfaces):
        findings.append(TemporalOperatorReviewValidationFinding("SURFACE_FLAGS_FORBIDDEN", "error", "risk_surfaces must be projection_only with no action authorization."))
        status = "BLOCKED"
    if any(r.action_authorization_allowed or r.execution_allowed or r.routing_change_allowed for r in q.recommendations):
        findings.append(TemporalOperatorReviewValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN", "error", "recommendations cannot authorize/execute/route."))
        status = "BLOCKED"
    if q.queue_status == "REVIEW_STABLE" and any(s.severity == "BLOCKED" for s in q.risk_surfaces):
        findings.append(TemporalOperatorReviewValidationFinding("REVIEW_STABLE_CONSTRAINT", "error", "REVIEW_STABLE requires no BLOCKED risk surfaces."))
        status = "BLOCKED"
    if q.queue_status == "REVIEW_PRESSURE" and not any(i.item_type == "PRESSURE_SPIKE" for i in q.queue_items) and not any(s.surface_type == "PRESSURE_ESCALATION" for s in q.risk_surfaces):
        findings.append(TemporalOperatorReviewValidationFinding("REVIEW_PRESSURE_CONSTRAINT", "error", "REVIEW_PRESSURE requires pressure item or risk surface."))
        status = "BLOCKED"
    if q.queue_status == "REVIEW_REGIME_RISK" and not any(i.item_type == "REGIME_SHIFT" for i in q.queue_items) and not any(s.surface_type == "REGIME_INSTABILITY" for s in q.risk_surfaces):
        findings.append(TemporalOperatorReviewValidationFinding("REVIEW_REGIME_RISK_CONSTRAINT", "error", "REVIEW_REGIME_RISK requires regime-risk item or risk surface."))
        status = "BLOCKED"
    if q.queue_status == "REVIEW_FRACTURE_RISK" and not any(i.item_type == "FRACTURE_CLUSTER" for i in q.queue_items) and not any(s.surface_type == "TOPOLOGY_FRACTURE" for s in q.risk_surfaces):
        findings.append(TemporalOperatorReviewValidationFinding("REVIEW_FRACTURE_RISK_CONSTRAINT", "error", "REVIEW_FRACTURE_RISK requires fracture item or risk surface."))
        status = "BLOCKED"
    if q.queue_status == "REVIEW_UNSTABLE" and not any(s.severity in {"WARN", "BLOCKED"} for s in q.risk_surfaces):
        findings.append(TemporalOperatorReviewValidationFinding("REVIEW_UNSTABLE_CONSTRAINT", "error", "REVIEW_UNSTABLE requires WARN/BLOCKED risk surface."))
        status = "BLOCKED"
    if q.queue_status == "OPERATOR_REVIEW_REQUIRED" and not any(r.operator_review_required for r in q.recommendations):
        findings.append(TemporalOperatorReviewValidationFinding("REVIEW_REQUIRED_MISSING", "error", "OPERATOR_REVIEW_REQUIRED requires operator_review_required recommendation."))
        status = "BLOCKED"
    if q.created_by_lane == "PROJECTION" and ((not q.projection_only) or q.queue_authoritative):
        findings.append(TemporalOperatorReviewValidationFinding("PROJECTION_AUTH_BLOCKED", "error", "PROJECTION queues must remain projection_only and non-authoritative."))
        status = "BLOCKED"
    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "queue_id": q.queue_id}))
    return TemporalOperatorReviewValidationReport(status, tuple(findings), receipt_hash)
