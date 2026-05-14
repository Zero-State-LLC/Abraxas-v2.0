from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import TemporalContinuityIndex, TemporalContinuityValidationFinding, TemporalContinuityValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_temporal_continuity_index(index: TemporalContinuityIndex | Mapping[str, Any]) -> TemporalContinuityValidationReport:
    i = index if isinstance(index, TemporalContinuityIndex) else TemporalContinuityIndex(**dict(index))
    findings = []
    status = "PASS"
    if i.history_rewrite_allowed or i.ledger_mutation_allowed or i.timeline_collapse_allowed or i.canonical_selection_allowed or i.live_execution_allowed or i.routing_change_allowed:
        findings.append(TemporalContinuityValidationFinding("FLAGS_FORBIDDEN", "error", "rewrite/mutation/collapse/selection/execution/routing must be false."))
        status = "BLOCKED"
    if any(c.mutation_allowed for c in i.component_scores):
        findings.append(TemporalContinuityValidationFinding("COMPONENT_MUTATION_FORBIDDEN", "error", "component_scores[*].mutation_allowed must be false."))
        status = "BLOCKED"
    if any(f.normalization_allowed for f in i.findings):
        findings.append(TemporalContinuityValidationFinding("FINDING_NORMALIZATION_FORBIDDEN", "error", "findings[*].normalization_allowed must be false."))
        status = "BLOCKED"
    if any(r.history_rewrite_allowed or r.ledger_mutation_allowed or r.timeline_collapse_allowed or r.canonical_selection_allowed for r in i.recommendations):
        findings.append(TemporalContinuityValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN", "error", "recommendation mutation/collapse/selection flags must be false."))
        status = "BLOCKED"
    if i.index_status == "CONTINUITY_STABLE" and not (i.continuity_posture == "STABLE" and i.continuity_score >= 0.85):
        findings.append(TemporalContinuityValidationFinding("STABLE_CONSTRAINT", "error", "CONTINUITY_STABLE requires STABLE posture and score >= 0.85."))
        status = "BLOCKED"
    if i.index_status == "CONTINUITY_MIXED" and not (i.continuity_posture == "MIXED" and 0.55 <= i.continuity_score < 0.85):
        findings.append(TemporalContinuityValidationFinding("MIXED_CONSTRAINT", "error", "CONTINUITY_MIXED requires MIXED posture and 0.55 <= score < 0.85."))
        status = "BLOCKED"
    if i.index_status == "CONTINUITY_UNSTABLE" and not (i.continuity_posture == "UNSTABLE" or any(f.finding_type in {"BLOCKED_HISTORY_PRESSURE", "NONDETERMINISM_PRESSURE"} for f in i.findings)):
        findings.append(TemporalContinuityValidationFinding("UNSTABLE_CONSTRAINT", "error", "CONTINUITY_UNSTABLE requires UNSTABLE posture or blocked/nondeterminism finding."))
        status = "BLOCKED"
    if i.index_status == "INSUFFICIENT_HISTORY" and not (len(i.input_refs) < 2 or any(f.finding_type == "INSUFFICIENT_HISTORY" for f in i.findings)):
        findings.append(TemporalContinuityValidationFinding("INSUFFICIENT_HISTORY_CONSTRAINT", "error", "INSUFFICIENT_HISTORY requires finding or fewer than 2 inputs."))
        status = "BLOCKED"
    if i.index_status == "OPERATOR_REVIEW_REQUIRED" and not any(r.operator_review_required for r in i.recommendations):
        findings.append(TemporalContinuityValidationFinding("REVIEW_REQUIRED_MISSING", "error", "OPERATOR_REVIEW_REQUIRED requires operator_review_required recommendation."))
        status = "BLOCKED"
    if i.created_by_lane == "SHADOW" and i.index_status == "CONTINUITY_STABLE" and i.authority_ref is not None:
        findings.append(TemporalContinuityValidationFinding("SHADOW_STABLE_AUTH_BLOCKED", "error", "SHADOW cannot mark CONTINUITY_STABLE authoritative."))
        status = "BLOCKED"
    if i.created_by_lane == "FORECAST" and i.index_status == "CONTINUITY_STABLE" and i.authority_ref is not None:
        findings.append(TemporalContinuityValidationFinding("FORECAST_STABLE_AUTH_BLOCKED", "error", "FORECAST cannot mark STABLE authoritative."))
        status = "BLOCKED"
    if i.created_by_lane == "PROJECTION" and i.authority_ref is not None:
        findings.append(TemporalContinuityValidationFinding("PROJECTION_AUTH_BLOCKED", "error", "PROJECTION cannot create continuity authority."))
        status = "BLOCKED"
    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "index_id": i.index_id}))
    return TemporalContinuityValidationReport(status, tuple(findings), receipt_hash)
