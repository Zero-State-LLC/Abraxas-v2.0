from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import *


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_replay_consensus_review(review: ReplayConsensusReview | Mapping[str, Any]) -> ReplayConsensusValidationReport:
    r = review if isinstance(review, ReplayConsensusReview) else ReplayConsensusReview(**dict(review))
    findings = []
    status = "PASS"
    if r.history_rewrite_allowed or r.ledger_mutation_allowed or r.timeline_collapse_allowed or r.live_execution_allowed or r.routing_change_allowed:
        findings.append(ReplayConsensusValidationFinding("FLAGS_FORBIDDEN", "error", "rewrite/mutation/collapse/execution/routing must be false.")); status = "BLOCKED"
    if any((not c.lineages_preserved) or c.normalization_allowed for c in r.consensus_clusters):
        findings.append(ReplayConsensusValidationFinding("CLUSTER_PRESERVATION_REQUIRED", "error", "clusters must preserve lineages and disallow normalization.")); status = "BLOCKED"
    if any(f.normalization_allowed for f in r.consensus_findings):
        findings.append(ReplayConsensusValidationFinding("FINDING_NORMALIZATION_FORBIDDEN", "error", "findings normalization_allowed must be false.")); status = "BLOCKED"
    if r.consensus_posture.canonical_selection_allowed or r.consensus_posture.auto_promotion_allowed:
        findings.append(ReplayConsensusValidationFinding("POSTURE_SELECTION_FORBIDDEN", "error", "canonical_selection_allowed/auto_promotion_allowed must be false.")); status = "BLOCKED"
    if any(rc.history_rewrite_allowed or rc.ledger_mutation_allowed or rc.timeline_collapse_allowed for rc in r.recommendations):
        findings.append(ReplayConsensusValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN", "error", "recommendations cannot permit rewrite/mutation/collapse.")); status = "BLOCKED"
    if r.review_status == "CONSENSUS_PRESENT" and (r.consensus_posture.consensus_state != "STRONG_CONSENSUS" or any(f.severity in {"BLOCKED", "NOT_COMPUTABLE"} for f in r.consensus_findings)):
        findings.append(ReplayConsensusValidationFinding("CONSENSUS_PRESENT_INVALID", "error", "CONSENSUS_PRESENT requires STRONG_CONSENSUS and no BLOCKED/NOT_COMPUTABLE findings.")); status = "BLOCKED"
    if r.review_status == "PARTIAL_CONSENSUS" and r.consensus_posture.consensus_state != "PARTIAL_CONSENSUS":
        findings.append(ReplayConsensusValidationFinding("PARTIAL_STATE_REQUIRED", "error", "PARTIAL_CONSENSUS requires PARTIAL_CONSENSUS consensus_state.")); status = "BLOCKED"
    if r.review_status == "CONSENSUS_CONFLICT" and (r.consensus_posture.consensus_state != "CONFLICTED" or not any(f.finding_type == "CONFLICT_SIGNAL" for f in r.consensus_findings)):
        findings.append(ReplayConsensusValidationFinding("CONFLICT_STATE_REQUIRED", "error", "CONSENSUS_CONFLICT requires CONFLICTED posture and CONFLICT_SIGNAL finding.")); status = "BLOCKED"
    if r.review_status == "INSUFFICIENT_ARBITRATION_HISTORY" and r.consensus_posture.arbitration_count >= 2:
        findings.append(ReplayConsensusValidationFinding("INSUFFICIENT_COUNT_INVALID", "error", "INSUFFICIENT_ARBITRATION_HISTORY requires arbitration_count < 2.")); status = "BLOCKED"
    if r.review_status == "OPERATOR_REVIEW_REQUIRED" and not any(rec.operator_review_required for rec in r.recommendations):
        findings.append(ReplayConsensusValidationFinding("REVIEW_REQUIRED_MISSING", "error", "OPERATOR_REVIEW_REQUIRED requires operator_review_required recommendation.")); status = "BLOCKED"
    if r.created_by_lane == "SHADOW" and r.review_status == "CONSENSUS_PRESENT":
        findings.append(ReplayConsensusValidationFinding("SHADOW_CONSENSUS_BLOCKED", "error", "SHADOW cannot mark CONSENSUS_PRESENT as authoritative.")); status = "BLOCKED"
    if r.created_by_lane == "FORECAST" and r.consensus_posture.consensus_state == "STRONG_CONSENSUS":
        findings.append(ReplayConsensusValidationFinding("FORECAST_STRONG_BLOCKED", "error", "FORECAST cannot mark STRONG_CONSENSUS authoritative.")); status = "BLOCKED"
    if r.created_by_lane == "PROJECTION" and r.authority_ref is not None:
        findings.append(ReplayConsensusValidationFinding("PROJECTION_AUTH_BLOCKED", "error", "PROJECTION cannot create consensus authority.")); status = "BLOCKED"
    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "review_id": r.review_id}))
    return ReplayConsensusValidationReport(status, tuple(findings), receipt_hash)
